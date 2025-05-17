// API 기본 URL 설정
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 전역 상태 관리
const state = {
    currentPage: 1,
    pageSize: 12,
    totalItems: 0,
    searchTerm: '',
    researchYear: '',
    makerName: '',
    years: []
};

// DOM 요소
const elements = {
    searchInput: document.getElementById('search-input'),
    searchButton: document.getElementById('search-button'),
    yearFilter: document.getElementById('year-filter'),
    makerFilter: document.getElementById('maker-filter'),
    resultsList: document.getElementById('results-list'),
    resultsCount: document.getElementById('results-count').querySelector('span'),
    pageInfo: document.getElementById('page-info'),
    prevPageBtn: document.getElementById('prev-page'),
    nextPageBtn: document.getElementById('next-page'),
    loading: document.getElementById('loading'),
    noResults: document.getElementById('no-results'),
    detailModal: document.getElementById('detail-modal'),
    closeModalBtn: document.querySelector('.close-button'),
    foodDetailTitle: document.getElementById('food-detail-title'),
    foodCode: document.getElementById('food-code'),
    foodYear: document.getElementById('food-year'),
    foodMaker: document.getElementById('food-maker'),
    foodServing: document.getElementById('food-serving'),
    nutritionData: document.getElementById('nutrition-data')
};

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', async () => {
    // 로딩 표시
    showLoading(true);
    
    try {
        // 초기 데이터 로드
        await loadYears();
        await searchFoods();
    } catch (error) {
        console.error('초기화 오류:', error);
        showError('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
        // 로딩 숨김
        showLoading(false);
    }
    
    // 이벤트 리스너 설정
    setupEventListeners();
});

// 이벤트 리스너 설정
function setupEventListeners() {
    // 검색 버튼 클릭
    elements.searchButton.addEventListener('click', handleSearch);
    
    // 검색 입력 필드에서 Enter 키 누름
    elements.searchInput.addEventListener('keyup', e => {
        if (e.key === 'Enter') handleSearch();
    });
    
    // 연도 필터 변경
    elements.yearFilter.addEventListener('change', handleSearch);
    
    // 제조사 필터 변경
    elements.makerFilter.addEventListener('change', handleSearch);
    
    // 페이지네이션 - 이전 페이지
    elements.prevPageBtn.addEventListener('click', () => {
        if (state.currentPage > 1) {
            state.currentPage--;
            searchFoods();
        }
    });
    
    // 페이지네이션 - 다음 페이지
    elements.nextPageBtn.addEventListener('click', () => {
        const maxPages = Math.ceil(state.totalItems / state.pageSize);
        if (state.currentPage < maxPages) {
            state.currentPage++;
            searchFoods();
        }
    });
    
    // 모달 닫기 버튼
    elements.closeModalBtn.addEventListener('click', () => {
        elements.detailModal.classList.add('hidden');
    });
    
    // 모달 바깥쪽 클릭하면 닫기
    elements.detailModal.addEventListener('click', e => {
        if (e.target === elements.detailModal) {
            elements.detailModal.classList.add('hidden');
        }
    });
}

// 검색 핸들러
async function handleSearch() {
    state.searchTerm = elements.searchInput.value.trim();
    state.researchYear = elements.yearFilter.value;
    state.makerName = elements.makerFilter.value.trim();
    state.currentPage = 1;
    
    await searchFoods();
}

// 연구 연도 옵션 로드
async function loadYears() {
    try {
        // 실제 API 연동 시 이 부분을 수정해야 할 수 있습니다.
        // 여기서는 임시 데이터로 사용합니다.
        const years = ['2020', '2021', '2022', '2023', '2024', '2025'];
        state.years = years;
        
        // 연도 필터에 옵션 추가
        const yearFilter = elements.yearFilter;
        years.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearFilter.appendChild(option);
        });
    } catch (error) {
        console.error('연도 로드 오류:', error);
        throw error;
    }
}

// 식품 검색 API 호출
async function searchFoods() {
    showLoading(true);
    elements.resultsList.innerHTML = '';
    elements.noResults.classList.add('hidden');
    
    try {
        // API 요청 파라미터 구성
        const params = new URLSearchParams({
            skip: (state.currentPage - 1) * state.pageSize,
            limit: state.pageSize
        });
        
        // 선택적 파라미터 추가
        if (state.searchTerm) params.append('food_name', state.searchTerm);
        if (state.researchYear) params.append('research_year', state.researchYear);
        if (state.makerName) params.append('maker_name', state.makerName);
        
        // API 호출
        const response = await fetch(`${API_BASE_URL}/foods?${params.toString()}`);
        
        if (!response.ok) {
            throw new Error(`API 오류: ${response.status}`);
        }
        
        const data = await response.json();
        state.totalItems = data.total;
        
        // 결과 표시
        updateResultsInfo();
        
        // 검색 결과가 없을 경우
        if (data.items.length === 0) {
            elements.noResults.classList.remove('hidden');
            return;
        }
        
        // 결과 렌더링
        renderFoodResults(data.items);
    } catch (error) {
        console.error('검색 오류:', error);
        showError('검색 중 오류가 발생했습니다.');
    } finally {
        showLoading(false);
    }
}

// 식품 검색 결과 렌더링
function renderFoodResults(foods) {
    const resultsList = elements.resultsList;
    
    foods.forEach(food => {
        const foodCard = document.createElement('div');
        foodCard.className = 'food-card';
        foodCard.addEventListener('click', () => showFoodDetails(food.id));
        
        foodCard.innerHTML = `
            <h3 class="food-name">${food.food_name}</h3>
            <p class="food-meta-item"><strong>제조사:</strong> ${food.maker_name || '-'}</p>
            <p class="food-meta-item"><strong>연구 연도:</strong> ${food.research_year || '-'}</p>
            <div class="food-nutrition-highlight">
                <div class="nutrition-item">
                    <span class="nutrition-name">칼로리:</span>
                    <span>${food.calorie || 0} kcal</span>
                </div>
                <div class="nutrition-item">
                    <span class="nutrition-name">탄수화물:</span>
                    <span>${food.carbohydrate || 0} g</span>
                </div>
                <div class="nutrition-item">
                    <span class="nutrition-name">단백질:</span>
                    <span>${food.protein || 0} g</span>
                </div>
            </div>
        `;
        
        resultsList.appendChild(foodCard);
    });
}

// 식품 상세 정보 표시
async function showFoodDetails(foodId) {
    showLoading(true);
    
    try {
        // API 호출로 상세 정보 가져오기
        const response = await fetch(`${API_BASE_URL}/foods/${foodId}`);
        
        if (!response.ok) {
            throw new Error(`API 오류: ${response.status}`);
        }
        
        const food = await response.json();
        
        // 모달에 데이터 채우기
        elements.foodDetailTitle.textContent = food.food_name;
        elements.foodCode.textContent = food.food_cd || '-';
        elements.foodYear.textContent = food.research_year || '-';
        elements.foodMaker.textContent = food.maker_name || '-';
        elements.foodServing.textContent = food.serving_size || 100;
        
        // 영양소 데이터 표시
        const nutritionHTML = `
            <tr>
                <td>열량</td>
                <td>${food.calorie || 0} kcal</td>
            </tr>
            <tr>
                <td>탄수화물</td>
                <td>${food.carbohydrate || 0} g</td>
            </tr>
            <tr>
                <td>단백질</td>
                <td>${food.protein || 0} g</td>
            </tr>
            <tr>
                <td>지방</td>
                <td>${food.province || 0} g</td>
            </tr>
            <tr>
                <td>당류</td>
                <td>${food.sugars || 0} g</td>
            </tr>
            <tr>
                <td>나트륨</td>
                <td>${food.salt || 0} mg</td>
            </tr>
            <tr>
                <td>콜레스테롤</td>
                <td>${food.cholesterol || 0} mg</td>
            </tr>
            <tr>
                <td>포화지방산</td>
                <td>${food.saturated_fatty_acids || 0} g</td>
            </tr>
            <tr>
                <td>트랜스지방산</td>
                <td>${food.trans_fat || 0} g</td>
            </tr>
        `;
        
        elements.nutritionData.innerHTML = nutritionHTML;
        
        // 모달 표시
        elements.detailModal.classList.remove('hidden');
    } catch (error) {
        console.error('상세 정보 로드 오류:', error);
        showError('상세 정보를 불러오는 중 오류가 발생했습니다.');
    } finally {
        showLoading(false);
    }
}

// 검색 결과 정보 업데이트 (페이지네이션, 결과 수 등)
function updateResultsInfo() {
    elements.resultsCount.textContent = state.totalItems;
    elements.pageInfo.textContent = `페이지: ${state.currentPage}`;
    
    // 페이지네이션 버튼 활성화/비활성화
    const maxPages = Math.ceil(state.totalItems / state.pageSize);
    elements.prevPageBtn.disabled = state.currentPage <= 1;
    elements.nextPageBtn.disabled = state.currentPage >= maxPages;
}

// 로딩 상태 표시
function showLoading(isLoading) {
    if (isLoading) {
        elements.loading.classList.remove('hidden');
    } else {
        elements.loading.classList.add('hidden');
    }
}

// 에러 메시지 표시
function showError(message) {
    alert(message);
}

// 디버깅 목적으로 더미 데이터 생성 함수 (실제 API 연동 시 삭제)
function generateDummyData(count = 10) {
    const dummyFoods = [];
    const foodNames = ['사과', '바나나', '귤', '오렌지', '복숭아', '딸기', '포도', '수박', '참외', '키위', '망고'];
    const makerNames = ['농심', '롯데', '해태', '오리온', 'CJ', '동원', '삼양', '풀무원', '곰표', '빙그레'];
    
    for (let i = 1; i <= count; i++) {
        const randomFood = foodNames[Math.floor(Math.random() * foodNames.length)];
        const randomMaker = makerNames[Math.floor(Math.random() * makerNames.length)];
        const randomYear = 2020 + Math.floor(Math.random() * 6); // 2020~2025
        
        dummyFoods.push({
            id: i,
            food_cd: `F${String(i).padStart(6, '0')}`,
            food_name: `${randomFood} ${i}`,
            maker_name: randomMaker,
            research_year: String(randomYear),
            serving_size: Math.floor(Math.random() * 150) + 50, // 50~200g
            calorie: Math.floor(Math.random() * 500) + 50, // 50~550 kcal
            carbohydrate: Math.floor(Math.random() * 80) + 5, // 5~85g
            protein: Math.floor(Math.random() * 30) + 1, // 1~31g
            province: Math.floor(Math.random() * 20) + 1, // 1~21g
            sugars: Math.floor(Math.random() * 30), // 0~30g
            salt: Math.floor(Math.random() * 1000) + 10, // 10~1010mg
            cholesterol: Math.floor(Math.random() * 100), // 0~100mg
            saturated_fatty_acids: Math.floor(Math.random() * 10), // 0~10g
            trans_fat: Math.random().toFixed(1) // 0.0~0.9g
        });
    }
    
    return dummyFoods;
}
