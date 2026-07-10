// IsThereAnyHotdeal - JavaScript Application

// App State
let state = {
    platform: '',
    search: '',
    sortBy: 'discount'
};

// DOM Elements
const dealsTbody = document.getElementById('deals-tbody');
const searchInput = document.getElementById('search-input');
const clearSearchBtn = document.getElementById('clear-search-btn');
const sortSelect = document.getElementById('sort-select');
const syncBtn = document.getElementById('sync-btn');
const resultsCount = document.getElementById('results-count');
const toast = document.getElementById('toast');

// Stat Elements
const statTotal = document.getElementById('stat-total');
const statCoupang = document.getElementById('stat-coupang');
const statNaver = document.getElementById('stat-naver');
const statToss = document.getElementById('stat-toss');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    fetchDeals();
});

// Setup Events
function setupEventListeners() {
    // 1. Platform Filters
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Remove active classes
            filterBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class
            btn.classList.add('active');
            
            // Update state
            state.platform = btn.getAttribute('data-platform');
            fetchDeals();
        });
    });

    // 2. Search Box with Debounce
    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        state.search = val;
        
        // Show/hide clear button
        if (val.length > 0) {
            clearSearchBtn.style.display = 'block';
        } else {
            clearSearchBtn.style.display = 'none';
        }

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchDeals();
        }, 300);
    });

    // 3. Clear Search
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        state.search = '';
        clearSearchBtn.style.display = 'none';
        fetchDeals();
    });

    // 4. Sort Dropdown
    sortSelect.addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        fetchDeals();
    });

    // 5. Sync Button
    syncBtn.addEventListener('click', handleSync);
}

// Fetch Deals from API
async function fetchDeals() {
    renderLoading();
    
    // Build query URL
    const params = new URLSearchParams();
    if (state.platform) params.append('platform', state.platform);
    if (state.search) params.append('search', state.search);
    if (state.sortBy) params.append('sort_by', state.sortBy);
    
    try {
        const response = await fetch(`/api/deals?${params.toString()}`);
        if (!response.ok) throw new Error('데이터 로딩 오류');
        
        const deals = await response.json();
        renderDeals(deals);
        updateStatistics(deals);
    } catch (err) {
        renderError(err.message);
        showToast('서버로부터 데이터를 가져오지 못했습니다.', 'error');
    }
}

// Render Loading Spinner Row
function renderLoading() {
    dealsTbody.innerHTML = `
        <tr>
            <td colspan="7" class="loading-state">
                <div style="display: flex; justify-content: center; align-items: center; gap: 8px;">
                    <span class="spinner" style="border-top-color: #3b5bdb;"></span>
                    최신 정보를 조회하고 있습니다...
                </div>
            </td>
        </tr>
    `;
}

// Render Error Row
function renderError(msg) {
    dealsTbody.innerHTML = `
        <tr>
            <td colspan="7" class="empty-state" style="color: #e03131;">
                ⚠️ 에러: ${msg}
            </td>
        </tr>
    `;
}

// Format Currency Utility
function formatPrice(value) {
    return new Intl.NumberFormat('ko-KR').format(value) + '원';
}

// Render Table Rows
function renderDeals(deals) {
    if (!deals || deals.length === 0) {
        dealsTbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    검색 조건에 맞는 핫딜 목록이 없습니다.
                </td>
            </tr>
        `;
        resultsCount.textContent = '0개 상품 조회됨';
        return;
    }

    resultsCount.textContent = `${deals.length}개 상품 조회됨`;
    
    let html = '';
    deals.forEach(deal => {
        // Platform Badge
        let platformLabel = '';
        let platformClass = '';
        if (deal.platform === 'coupang') {
            platformLabel = '쿠팡';
            platformClass = 'badge-coupang';
        } else if (deal.platform === 'naver') {
            platformLabel = '네이버';
            platformClass = 'badge-naver';
        } else if (deal.platform === 'toss') {
            platformLabel = '토스';
            platformClass = 'badge-toss';
        }

        // Image
        const imgUrl = deal.image_url || 'https://via.placeholder.com/48?text=No+Img';

        // Price formatting with drop indicator
        let priceHtml = `<div class="price-current">${formatPrice(deal.price)}</div>`;
        if (deal.prev_price && deal.prev_price > deal.price) {
            const drop = deal.prev_price - deal.price;
            priceHtml = `
                <div>
                    <span class="price-previous">${formatPrice(deal.prev_price)}</span>
                    <span class="price-current">${formatPrice(deal.price)}</span>
                    <span class="price-drop-indicator">⬇️ ${formatPrice(drop)} 인하</span>
                </div>
            `;
        }

        // Discount Tag
        const discountRate = deal.discount_rate || 0;
        const discountHtml = discountRate > 0 
            ? `<span class="discount-tag">-${Math.round(discountRate)}%</span>` 
            : `<span class="discount-tag" style="background-color: #495057;">-</span>`;

        html += `
            <tr>
                <td style="text-align: center;">
                    <span class="badge ${platformClass}">${platformLabel}</span>
                </td>
                <td style="text-align: center;">
                    <img src="${imgUrl}" class="product-img" alt="${deal.title}">
                </td>
                <td>
                    <div class="product-cell">
                        <a href="${deal.original_url}" target="_blank" class="product-title" title="${deal.title}">
                            ${deal.title}
                        </a>
                        <span style="font-size: 11px; color: var(--text-secondary);">상품 ID: ${deal.product_id}</span>
                    </div>
                </td>
                <td style="text-align: right;">
                    ${priceHtml}
                </td>
                <td style="text-align: center;">
                    ${discountHtml}
                </td>
                <td style="text-align: center; font-size: 12px; color: var(--text-secondary);">
                    ${deal.observed_at}
                </td>
                <td style="text-align: center;">
                    <a href="${deal.original_url}" target="_blank" class="btn-buy">구매하기 🔗</a>
                </td>
            </tr>
        `;
    });
    
    dealsTbody.innerHTML = html;
}

// Update Stats Board
function updateStatistics(deals) {
    if (state.platform || state.search) {
        // 필터링된 상태에서는 통계 카드는 고정해 두거나, 현재 불러와진 목록에서 계산
        // 전체 통계를 반영하기 위해 별도 조회 없이 현재 응답 결과에 따라 유연하게 렌더링
    }
    
    // 비동기로 전체 통계 로직 (전체 개수 조회)
    fetch('/api/deals')
        .then(res => res.json())
        .then(allDeals => {
            statTotal.textContent = allDeals.length;
            statCoupang.textContent = allDeals.filter(d => d.platform === 'coupang').length;
            statNaver.textContent = allDeals.filter(d => d.platform === 'naver').length;
            statToss.textContent = allDeals.filter(d => d.platform === 'toss').length;
        })
        .catch(() => {});
}

// Trigger Manual Collector Sync
async function handleSync() {
    const btnText = syncBtn.querySelector('.btn-text');
    const spinner = syncBtn.querySelector('.spinner');
    
    // Disable UI
    syncBtn.disabled = true;
    btnText.style.opacity = '0.5';
    spinner.style.display = 'inline-block';
    
    showToast('각 쇼핑몰로부터 최신 가격 정보를 수집하는 중...', 'info');

    try {
        const response = await fetch('/api/collect');
        if (!response.ok) throw new Error('수집기 호출 실패');
        
        const data = await response.json();
        
        if (data.status === 'success' || data.status === 'partial_success') {
            let msg = `${data.collected_count}개 상품 업데이트 완료!`;
            if (data.errors && data.errors.length > 0) {
                msg += ` (일부 수집 실패: 쿠팡 API 점검)`;
                showToast(msg, 'info');
            } else {
                showToast(msg, 'success');
            }
            fetchDeals(); // Refresh
        } else {
            throw new Error(data.message || '수집기 작동 중 오류');
        }
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        // Restore UI
        syncBtn.disabled = false;
        btnText.style.opacity = '1';
        spinner.style.display = 'none';
    }
}

// Toast Notification Helper
function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = 'toast'; // reset
    
    if (type === 'error') {
        toast.classList.add('error');
    } else if (type === 'success') {
        toast.classList.add('success');
    }
    
    toast.classList.add('show');
    
    // Auto-hide after 3 seconds
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
