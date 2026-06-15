from flask import Flask, render_template, jsonify, request
import requests
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy import select
from google import genai
import os
from dotenv import load_dotenv
from datetime import datetime, timezone , timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_cache.db' # 建立一個本地的資料庫檔案
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 關閉不必要的警告
db = SQLAlchemy(app)

# 定義資料庫表格結構
class MovieCache(db.Model):
    # 用 movie_id 作為唯一的識別碼 (這對於電影詳情頁非常重要)
    id = db.Column(db.Integer, primary_key=True)
    # 搜尋用的關鍵字 (例如 "瑪利歐")，可以設為索引方便搜尋，但不一定要當主鍵
    key = db.Column(db.String(255), unique=True, nullable=False)
    # API 原始結果 (JSON)
    result = db.Column(db.Text, nullable=True) 
    # AI 分析結果
    ai_review = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    

# 初始化資料庫 (確保在啟動時有這張表)
with app.app_context():
    db.create_all()
    
# 載入 .env 檔案中的環境變數
load_dotenv()

# 安全地取得 API Key    
TMDB_KEY =  os.getenv("TMDB_KEY")    
BASE_URL = "https://api.themoviedb.org/3"


# 1. 首頁：渲染 HTML 模板
@app.route('/')
def index():
    return render_template('index.html')

#檢查快取的時間戳記，是否超過24小時
def is_expired(created_at):
    # 設定過期時間為 24 小時
    expiration_time = timedelta(hours=24)
    # 比較現在時間與資料建立時間
    return datetime.now(timezone.utc) - created_at.replace(tzinfo=timezone.utc) > expiration_time

# 2. 獲取熱門電影 (給前端 JS 呼叫)  優化「首頁熱門電影」的 API 一天只更新一次
@app.route('/api/movies/popular')
def popular():
    page = request.args.get('page', 1)
    cache_key = f"popular_page_{page}"
    
    cached = db.session.execute(select(MovieCache).filter_by(key=cache_key)).scalar()
    
    # 如果有快取，且沒有過期，才回傳
    if cached and not is_expired(cached.created_at):
        print("從資料庫讀取有效快取...")
        return jsonify(json.loads(cached.result))
    
    # 呼叫 API
    url = f"{BASE_URL}/movie/popular?api_key={TMDB_KEY}&language=zh-TW&page={page}"
    response_data = requests.get(url).json()
    
    # 確認快取時間，存入資料庫
    if cached:
        # 更新現有記錄 (這樣才不會一直新增重複的 key)
        cached.result = json.dumps(response_data)
        cached.created_at = datetime.now(timezone.utc)
    else:
        # 新增記錄
        new_cache = MovieCache(key=cache_key, result=json.dumps(response_data))
        db.session.add(new_cache)
    
    return jsonify(response_data)


# 3. 根據關鍵字搜尋 (這會讓你的網站更有實用性)
@app.route('/api/movies/search')
def search():
    query = request.args.get('q')
    
    # 1. 先去資料庫找有沒有快取過
    cached_data = db.session.execute(select(MovieCache).filter_by(query=query)).scalar()
    if cached_data:
        print("從資料庫讀取快取...")
        return jsonify(json.loads(cached_data.result))
    
    # 2. 如果沒有，才去呼叫 TMDB API
    print("發送 API 請求...")
    url = f"{BASE_URL}/search/movie?api_key={TMDB_KEY}&query={query}&language=zh-TW"
    response = requests.get(url).json()
    
    # 3. 將結果存入資料庫，下次就不用再查了
    new_cache = MovieCache(query=query, result=json.dumps(response))
    db.session.add(new_cache)
    db.session.commit()
    
    return jsonify(response)

# 4. 獲取年份，若沒輸入則預設為今年
# 推薦將年份與月份邏輯整合進 API
    
@app.route('/api/movies/discover')
def discover():
    page = request.args.get('page', 1)
    # 接收前端傳來的參數，預設值設為 None
    year = request.args.get('year')
    month = request.args.get('month')
    
    params = {
        "api_key": TMDB_KEY, 
        "language": "zh-TW", 
        "sort_by": "release_date.desc",
        "page": page
    }
    
    # 動態加入篩選條件
    if year:
        params["primary_release_year"] = year
    if month:
        # 假設篩選當月 1號到 30號
        params["primary_release_date.gte"] = f"{year}-{month}-01"
        params["primary_release_date.lte"] = f"{year}-{month}-30"
        
    url = f"{BASE_URL}/discover/movie"
    response = requests.get(url, params=params)
    return jsonify(response.json()) # 直接用剛剛拿到的 response 即可

# 5.增加一個新的網址路徑，用來顯示電影細節。
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    # 這裡你需要用 movie_id 去 TMDB 抓詳細資料
    # 接著把資料傳給一個新的 HTML 檔案 (movie_detail.html)
    return render_template('movie_detail.html', movie_id=movie_id)


# 這是開發者保護機制
DEBUG_MODE = True 

@app.route('/api/movie/<int:movie_id>')
def get_movie_detail(movie_id):
    # 1. 定義資料夾路徑與檔案名稱
    basedir = os.path.abspath(os.path.dirname(__file__))
    mock_dir = os.path.join(basedir, 'mock_data') # 設定一個叫 mock_data 的資料夾
    
    # 2. 自動建立資料夾 (如果不存在的話)
    if not os.path.exists(mock_dir):
        os.makedirs(mock_dir)
        
    filename = f'movie_{movie_id}.json'
    file_path = os.path.join(mock_dir, filename)

    if DEBUG_MODE:
        if os.path.exists(file_path):
            print(f"DEBUG: 讀取本地 Mock Data: {mock_dir}/{filename}")
            with open(file_path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        
        # 檔案不存在，從 TMDB 抓取並存入 mock_data 資料夾
        print(f"DEBUG: 正在下載並儲存至 {mock_dir}/{filename} ...")
        url = f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_KEY}&language=zh-TW"
        response = requests.get(url)
        data = response.json()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return jsonify(data)
    else:
        # 正式模式：維持原樣，呼叫 TMDB API
        url = f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_KEY}&language=zh-TW"
        response = requests.get(url)
        return jsonify(response.json())

@app.route('/api/ai-review/<int:movie_id>')
def ai_review(movie_id):
    # 1. 接收前端參數
    movie_title = request.args.get('title')
    
    # 2. 安全性檢查
    if not movie_title or movie_title == 'undefined':
        return jsonify({"review": "錯誤：無法取得電影名稱，請重新整理頁面。"})

    # 3. 資料庫快取檢查：使用 movie_id 進行查詢
    # 使用 .get() 方法直接根據主鍵 (Primary Key) 查詢
    # 新寫法
    cached = db.session.get(MovieCache, movie_id)
    
    if cached and cached.ai_review:
        print(f"DEBUG: 從資料庫讀取快取 - {movie_title}")
        return jsonify({"review": cached.ai_review})

    # 4. 如果沒有快取，則呼叫 Gemini
    try:
        print(f"DEBUG: 呼叫 Gemini 分析 - {movie_title}")
        client = genai.Client(api_key=os.getenv("genai_api_key"))
        #prompt = f"請針對電影《{movie_title}》進行深度分析，包括劇情亮點與推薦原因。"
        # 修改 prompt，加入具體的要求與字數限制
        prompt = f"""
        請針對電影《{movie_title}》提供一份精簡的影評，字數控制在 600 字以內，包含以下重點：
        
        1. 值得推薦嗎？（用一句話總結是否值得進戲院或串流觀看）
        2. 爛番茄評分：(如果不知道確切評分，請根據電影口碑給出大致評價指標)
        3. 演員演技表現：(簡評主演的演技是否到位)
        4. 觀影推薦原因：(簡單說明推薦或不推薦的理由)
        
        請以客觀且精煉的語氣回答。
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        analysis_text = response.text
        
        # 5. 將結果存入資料庫
        if not cached:
            # 新增一筆記錄
            new_cache = MovieCache(movie_id=movie_id, ai_review=analysis_text)
            db.session.add(new_cache)
        else:
            # 更新現有記錄
            cached.ai_review = analysis_text
            
        db.session.commit()
        
        return jsonify({"review": analysis_text})
        
    except Exception as e:
        print(f"DEBUG: AI 呼叫錯誤: {str(e)}")
        return jsonify({"review": "目前 API 額度已達上限或連線失敗，請稍後再試。"})



if __name__ == '__main__':
    app.run(debug=True)