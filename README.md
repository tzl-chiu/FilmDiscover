# 🎬 FilmDiscover - 電影探索與深度分析站

這是一個使用 **Flask** 開發的電影推薦應用，整合了 **TMDB API** 與 **Google Gemini AI**，不僅支援電影瀏覽與搜尋，更能為每一部電影提供 AI 生成的深度影評分析。

已部署至Render  [https://filmdiscover.onrender.com](https://filmdiscover.onrender.com)

![圖片](https://i.ibb.co/zTpyrJR0/2026-06-16-22-19-52.png)


## 🚀 功能特色

* **熱門電影瀏覽：** 快速獲取當前最受歡迎的電影清單。
* **智慧搜尋：** 支援關鍵字搜尋，內建 SQLite 資料庫快取機制，大幅提升查詢效能。
* **分類篩選：** 輕鬆篩選「今年上映」及「本月新片」。
* **AI 深度影評：** 一鍵喚起 Google Gemini AI，針對電影劇情與特色進行深度解析（支援 Markdown 渲染）。
* **高效快取：** 影評分析結果自動儲存至 SQLite，重複查詢無需耗費額外 API 額度。
* **現代介面：** 響應式設計，使用 Tailwind CSS 構建，具備骨架屏 (Skeleton) 優化等待體驗。

## 🛠 技術棧

* **後端：** Python, Flask, Flask-SQLAlchemy
* **前端：** HTML5, JavaScript (Async/Await), Tailwind CSS, Marked.js (Markdown 解析)
* **人工智慧：** Google Gemini API (`gemini-2.5-flash`)
* **第三方服務：** The Movie Database (TMDB) API
* **資料庫：** SQLite

## 📂 專案結構

```text
FilmDiscover/
├── app.py              # Flask 後端邏輯 (路由、API 串接、Gemini整合、資料庫操作)
├── requirements.txt    # 依賴清單
├── .env                # 環境變數 (存放 TMDB_KEY 與 genai_api_key)
├── static/             
│   ├── js/             # 前端邏輯 (movie_detail.js 處理非同步請求與渲染)
│   └── ...
└── templates/          
    ├── index.html      # 搜尋頁面
    └── movie_detail.html # 電影詳情與 AI 分析結果頁面

## 📦 安裝與執行

建立並啟動虛擬環境

Bash
python3 -m venv venv
source venv/bin/activate
安裝依賴套件

Bash
pip install -r requirements.txt

設定 API Key
在根目錄建立 .env 檔案，填入以下金鑰：
TMDB_KEY=你的TMDB_API_KEY
genai_api_key=你的Google_Gemini_API_KEY

啟動應用

Bash
python3 app.py
啟動後，開啟瀏覽器造訪 http://127.0.0.1:5000 即可使用。
