from flask import Flask, render_template, jsonify, request
import requests
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy import select
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_cache.db' # 建立一個本地的資料庫檔案
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 關閉不必要的警告
db = SQLAlchemy(app)

# 定義資料庫表格結構
class MovieCache(db.Model):
    query = db.Column(db.String(100), primary_key=True) # 關鍵字當作主鍵
    result = db.Column(db.Text, nullable=False)        # 儲存 API 回傳的 JSON 字串

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

# 2. 獲取熱門電影 (給前端 JS 呼叫)
@app.route('/api/movies/popular')
def popular():
    page = request.args.get('page', 1)
    url = f"{BASE_URL}/movie/popular?api_key={TMDB_KEY}&language=zh-TW&page={page}"
    return jsonify(requests.get(url).json())

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


if __name__ == '__main__':
    app.run(debug=True)