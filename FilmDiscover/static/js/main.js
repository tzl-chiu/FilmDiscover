
// 搜尋功能
async function searchMovies() {
    const query = document.getElementById('searchInput').value;
    if (!query) return;
    // 直接請求後端搜尋 API
    const response = await fetch(`/api/movies/search?q=${query}`);
    const data = await response.json();
    
    // 直接使用渲染函式把結果丟進去
    renderMovies(data.results);
}

// 網頁啟動時自動載入
loadMovies();



/**
 * 電影篩選與顯示模組
 * 負責處理使用者點擊「分類按鈕」後的資料請求與頁面渲染
 */

// 定義全域變數來記住當前的狀態
let currentPage = 1;
let currentType = 'popular';

/**
 * 載入電影資料（包含分頁功能）
 * @param {string} type - 分類類型: 'popular', 'this_year', 'this_month'
 * @param {number} page - 要載入的頁碼
 */
async function loadMovies(type = 'popular', page = 1) {
    currentType = type; // 更新目前分類
    currentPage = page; // 更新目前頁碼
    
    let url = '';
    
    // 根據分類與頁碼建立 URL
    if (type === 'popular') {
        url = `/api/movies/popular?page=${page}`;
    } else if (type === 'this_year') {
        url = `/api/movies/discover?year=2026&page=${page}`;
    } else if (type === 'this_month') {
        url = `/api/movies/discover?year=2026&month=6&page=${page}`;
    }

    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.results) {
            renderMovies(data.results);
            // 更新頁面上的頁碼顯示 (假設你有一個 id="pageIndicator" 的元素)
            const indicator = document.getElementById('pageIndicator');
            if (indicator) indicator.innerText = `第 ${currentPage} 頁`;
            
            // 翻頁後捲動回頂部
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    } catch (error) {
        console.error('抓取電影失敗:', error);
    }
}

/**
 * 處理上一頁與下一頁的點擊事件
 * @param {number} direction - 傳入 -1 (上一頁) 或 1 (下一頁)
 */
function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage < 1) return; // 防止頁碼小於 1
    loadMovies(currentType, newPage);
}

/**
 * 將電影資料渲染至前端 grid 容器 (保持不變)
 */
function renderMovies(movies) {
    const grid = document.getElementById('movieGrid');
    grid.innerHTML = ''; 
    
    // 檢查是否有資料
    if (!movies || movies.length === 0) {
        grid.innerHTML = '<p class="text-center col-span-full">找不到相關電影</p>';
        return;
    }

    movies.forEach(movie => {
        // 直接呼叫 generateCard 並塞進 grid
        grid.innerHTML += generateCard(movie);
    });
            
        

}

// 在 main.js 生成電影卡片的地方 (假設你有一個 generateCard 函式)
function generateCard(movie) {
    const poster = movie.poster_path 
        ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` 
        : 'https://via.placeholder.com/500x750?text=無海報';

    return `
        <div class="bg-gray-800 p-4 rounded hover:scale-105 transition cursor-pointer" 
             onclick="window.location.href='/movie/${movie.id}'">
            <img src="${poster}" class="w-full h-64 object-cover rounded">
            <h2 class="mt-2 font-bold truncate">${movie.title}</h2>
            <p class="text-sm text-gray-400">${movie.release_date || '未知日期'}</p>
        </div>
    `;
}

// 確保這行有在最下面，且沒有被註解掉
document.addEventListener("DOMContentLoaded", function() {
    loadMovies('popular', 1);
});
