"""
식품영양 API에 대한 부하 테스트를 위한 Locust 테스트 파일
"""
import random
import json
from locust import HttpUser, task, between


class FoodApiUser(HttpUser):
    """
    식품영양 API에 대한 부하 테스트를 수행하는 가상 사용자 클래스
    """
    # 사용자당 작업 사이의 대기 시간 (초)
    wait_time = between(1, 5)
    
    # 검색에 사용할 임의의 식품명 목록
    food_names = ["사과", "바나나", "귤", "오렌지", "복숭아", "딸기", "포도", 
                  "수박", "참외", "키위", "망고", "쌀", "빵", "우유", "치즈",
                  "요구르트", "고기", "소고기", "돼지고기", "닭고기", "김치",
                  "된장", "고추장", "간장", "소금", "설탕", "꿀", "식초"]
    
    # 연도 목록
    years = ["2020", "2021", "2022", "2023", "2024", "2025"]
    
    # 제조사 목록
    makers = ["농심", "롯데", "해태", "오리온", "CJ", "동원", 
              "삼양", "풀무원", "곰표", "빙그레", "매일"]
              
    # 식품군 목록
    food_groups = ["곡류", "과일류", "계란류", "고기류", "채소류", 
                 "유제품", "유지류", "조리식품", "함과류", "음료류"]
                 
    # 자료출처 목록
    ref_sources = ["국내 식품영양데이터베이스", "산업식품발전협회", 
                 "식품의약청", "영양표시기준", "자체연구데이터"]
    
    def on_start(self):
        """
        테스트 시작 시 초기화 작업
        """
        self.api_prefix = "/api/v1"
        self.client.headers = {"Content-Type": "application/json"}
    
    @task(10)  # 가중치 10
    def search_foods(self):
        """
        검색 API 테스트 - 가장 높은 빈도로 호출
        """
        # 파라미터 랜덤 생성
        params = {}
        
        # 임의로 검색 조건 추가 (50% 확률)
        if random.random() > 0.5:
            params["food_name"] = random.choice(self.food_names)
        
        # 20% 확률로 연도 필터 추가
        if random.random() > 0.8:
            params["research_year"] = random.choice(self.years)
        
        # 10% 확률로 제조사 필터 추가
        if random.random() > 0.9:
            params["maker_name"] = random.choice(self.makers)
        
        # 페이지네이션 파라미터 추가
        params["skip"] = random.randint(0, 50) * 10
        params["limit"] = random.choice([10, 20, 50, 100])
        
        # API 호출
        self.client.get(f"{self.api_prefix}/foods", params=params, name="/api/v1/foods (검색)")
    
    @task(3)  # 가중치 3
    def get_food_details(self):
        """
        상세 정보 조회 API 테스트
        """
        # 1~100 사이의 임의의 ID로 상세 정보 요청
        food_id = random.randint(1, 100)
        self.client.get(f"{self.api_prefix}/foods/{food_id}", name="/api/v1/foods/{id} (상세)")
    
    @task(1)  # 가중치 1 (가장 낮은 빈도)
    def create_random_food(self):
        """
        식품 생성 API 테스트 (로드가 낮은 테스트)
        """
        # 랜덤 식품 데이터 생성
        food_data = {
            # 필수 필드
            "food_name": f"테스트_{random.choice(self.food_names)}_{random.randint(1000, 9999)}",
            "food_cd": f"T{random.randint(10000, 99999)}",
            "research_year": random.choice(self.years),
            "maker_name": random.choice(self.makers),
            # 누락되었던 필수 필드
            "group_name": random.choice(self.food_groups),  # 식품군 추가
            "ref_name": random.choice(self.ref_sources),    # 자료출처 추가
            # 영양 성분 필드
            "serving_size": random.randint(50, 300),
            "calorie": random.randint(50, 600),
            "carbohydrate": random.randint(0, 100),
            "protein": random.randint(0, 50),
            "province": random.randint(0, 30),
            "sugars": random.randint(0, 40),
            "salt": random.randint(0, 2000),
            "cholesterol": random.randint(0, 150),
            "saturated_fatty_acids": random.randint(0, 20),
            "trans_fat": round(random.uniform(0, 5), 1)
        }
        
        # API 호출 (실제 데이터가 생성되므로 주의)
        self.client.post(
            f"{self.api_prefix}/foods", 
            json=food_data,
            name="/api/v1/foods (생성)"
        )
