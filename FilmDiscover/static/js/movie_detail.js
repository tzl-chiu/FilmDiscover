/**
 * 電影詳情頁的核心邏輯：負責資料載入與 AI 深度影評分析
 */

// 1. 從網址獲取電影 ID
const movieId = window.location.pathname.split('/').pop();

// 2. 初始化：載入電影基本資料
async function loadDetail() {
    try {
        const res = await fetch(`/api/movie/${movieId}`);
        const movie = await res.json();
        // 把標題存起來
        currentMovieTitle = movie.title; 
    
        document.getElementById('title').innerText = movie.title;
        document.getElementById('overview').innerText = movie.overview;
        document.getElementById('poster').src = `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
        document.getElementById('rating').innerText = `TMDB 評分: ${movie.vote_average}`;
    } catch (error) {
        console.error("載入電影詳情失敗:", error);
    }
}


// 3. 呼叫 Gemini 的分析功能 (包含骨架屏與載入狀態處理)
async function analyzeMovie() {
    const btn = document.getElementById('aiBtn');
    const resultArea = document.getElementById('aiReviewArea');
    const skeleton = document.getElementById('skeleton'); 
    const resultText = document.getElementById('aiResult');

    // 1. 強制顯示 UI 狀態
    btn.disabled = true;
    btn.innerText = "AI 正在深度解析中...";
    resultArea.classList.remove('hidden');
    skeleton.classList.remove('hidden');
    resultText.classList.add('hidden');
    resultText.innerText = "";

    // 2. [關鍵修正] 使用 setTimeout 讓出主執行緒，讓瀏覽器先渲染骨架屏
    await new Promise(resolve => setTimeout(resolve, 0));

    // 3. 開始請求
    try {
        const url = `/api/ai-review/${movieId}?title=${encodeURIComponent(currentMovieTitle)}`;
        const res = await fetch(url);
        const data = await res.json();
        
        // 4. 渲染結果
        skeleton.classList.add('hidden');
        resultText.classList.remove('hidden');
        // 【關鍵修改】：使用 marked.parse() 將 Markdown 轉為 HTML
        resultText.innerHTML = marked.parse(data.review);
    } catch (error) {
        skeleton.classList.add('hidden');
        resultText.classList.remove('hidden');
        resultText.innerText = "服務暫時無法連線，請稍後再試。";
    } finally {
        btn.disabled = false;
        btn.innerText = "✨ AI 深度影評分析";
    }
}

// 頁面載入時執行初始化
loadDetail();

//  綁定✨ AI 深度影評分析 的按鈕
document.addEventListener("DOMContentLoaded", function() {
    const aiBtn = document.getElementById('aiBtn');
    if (aiBtn) {
        aiBtn.addEventListener('click', analyzeMovie);
    }
});