"""식품 정보 API 엔드포인트 테스트"""
import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.models import food as models
from app.schemas import food as schemas


@pytest.fixture
def sample_food():
    """테스트용 샘플 식품 데이터"""
    return {
        "food_cd": "D000001",
        "food_name": "테스트 식품",
        "group_name": "과자",  # food_group → group_name으로 수정
        "research_year": "2023",
        "maker_name": "테스트 회사",
        "ref_name": "식품영양성분DB",
        "serving_size": 100.0,
        "calorie": 350.0,
        "carbohydrate": 50.0,
        "protein": 5.0,
        "province": 15.0,  # fat → province로 수정
        "sugars": 20.0,    # sugar → sugars로 수정
        "salt": 1.0,
        "cholesterol": 0.0,  # 누락된 필수 필드 추가
        "saturated_fatty_acids": 5.0,  # 누락된 필수 필드 추가
        "trans_fat": 0.0  # 누락된 필수 필드 추가
    }


class TestFoodAPI:
    """식품 API 테스트 클래스"""
    
    def test_create_food(self, client: TestClient, sample_food: dict):
        """POST /foods/ - 식품 생성 테스트"""
        response = client.post("/api/v1/foods/", json=sample_food)
        
        # 상태 코드 및 응답 검증
        assert response.status_code == 201
        data = response.json()
        assert data["food_cd"] == sample_food["food_cd"]
        assert data["food_name"] == sample_food["food_name"]
        assert "id" in data  # ID가 생성되었는지 확인
    
    def test_get_food(self, client: TestClient, sample_food: dict):
        """GET /foods/{food_id} - 식품 조회 테스트"""
        # 먼저 식품 생성
        create_response = client.post("/api/v1/foods/", json=sample_food)
        created_food = create_response.json()
        food_id = created_food["id"]
        
        # 생성된 식품 조회
        response = client.get(f"/api/v1/foods/{food_id}")
        
        # 상태 코드 및 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == food_id
        assert data["food_name"] == sample_food["food_name"]
    
    def test_get_nonexistent_food(self, client: TestClient):
        """GET /foods/{food_id} - 존재하지 않는 식품 조회 테스트"""
        # 아주 큰 ID값을 사용하여 확실히 존재하지 않는 식품 조회
        response = client.get("/api/v1/foods/999999999")
        assert response.status_code == 404
    
    def test_search_foods(self, client: TestClient, sample_food: dict):
        """GET /foods/ - 식품 검색 테스트"""
        # 먼저 식품 생성
        client.post("/api/v1/foods/", json=sample_food)
        
        # 이름으로 검색
        response = client.get(f"/api/v1/foods/?food_name={sample_food['food_name']}")
        
        # 상태 코드 및 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["items"][0]["food_name"] == sample_food["food_name"]
    
    def test_update_food(self, client: TestClient, sample_food: dict):
        """PUT /foods/{food_id} - 식품 정보 업데이트 테스트"""
        # 먼저 식품 생성
        create_response = client.post("/api/v1/foods/", json=sample_food)
        created_food = create_response.json()
        food_id = created_food["id"]
        
        # 업데이트할 데이터
        update_data = {
            "food_name": "업데이트된 식품명",
            "calorie": 400.0
        }
        
        # 식품 정보 업데이트
        response = client.put(f"/api/v1/foods/{food_id}", json=update_data)
        
        # 상태 코드 및 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == food_id
        assert data["food_name"] == update_data["food_name"]
        assert data["calorie"] == update_data["calorie"]
        # 업데이트하지 않은 필드는 유지되어야 함
        assert data["food_cd"] == sample_food["food_cd"]
    
    def test_delete_food(self, client: TestClient, sample_food: dict):
        """DELETE /foods/{food_id} - 식품 삭제 테스트"""
        # 먼저 식품 생성
        create_response = client.post("/api/v1/foods/", json=sample_food)
        created_food = create_response.json()
        food_id = created_food["id"]
        
        # 식품 삭제
        response = client.delete(f"/api/v1/foods/{food_id}")
        
        # 상태 코드 검증 (204 No Content)
        assert response.status_code == 204
        
        # 삭제 확인
        get_response = client.get(f"/api/v1/foods/{food_id}")
        assert get_response.status_code == 404
