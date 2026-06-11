# 電影探索與推薦站 (Movie Discovery Site)

這是一個使用 **Flask** 開發的電影推薦應用，整合了 **TMDB API**，支援熱門電影瀏覽、關鍵字搜尋，以及按年度/月份篩選的功能。

## 🚀 功能特色
- **熱門電影瀏覽**：一鍵獲取當前最受歡迎的電影清單。
- **智慧搜尋**：支援關鍵字搜尋，並具備 SQLite 資料庫快取機制，大幅提升二次查詢速度。
- **分類篩選**：支援篩選「今年上映」及「本月新片」。
- **分頁瀏覽**：流暢的上下頁翻頁功能，方便探索更多電影。
- **響應式設計**：使用 Tailwind CSS 構建，手機與桌機皆有良好的閱讀體驗。

## 🛠 技術棧
- **後端**：Python, Flask, Flask-SQLAlchemy
- **前端**：HTML5, JavaScript (Async/Await), Tailwind CSS
- **第三方服務**：The Movie Database (TMDB) API
- **資料庫**：SQLite

```text
project/
├── app.py              # 核心：Flask 後端邏輯 (路由、API 串接、資料庫)
├── requirements.txt    # 依賴清單：專案執行所需的函式庫
├── static/             # 存放靜態檔案
│   ├── css/            # 網站樣式 (Tailwind CSS/自定義樣式)
│   ├── js/             # 前端邏輯 (API 請求、DOM 渲染)
│   └── images/         # 專案圖片資源
└── templates/          # HTML 樣板
    ├── index.html      # 主頁面：搜尋與電影清單呈現
    └── movie_detail.html # 電影詳情頁面

## 📦 安裝與執行

建立並啟動虛擬環境

Bash
python3 -m venv venv
source venv/bin/activate
安裝依賴套件

Bash
pip install -r requirements.txt
設定 API Key
在 app.py 中將 TMDB_KEY 替換為你自己的 TMDB API Key。

啟動應用

Bash
python3 app.py
啟動後，開啟瀏覽器造訪 http://127.0.0.1:5000 即可使用。
