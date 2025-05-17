"""식품 정보 API 엔드포인트 비동기 테스트"""
import pytest
from httpx import AsyncClient
from typing import Dict, Any

from app.schemas.food import Food


@pytest.fixture
def sample_food() -> Dict[str, Any]:
    """테스트용 샘플 식품 데이터"""
    return {
        "food_cd": "D000001",
        "food_name": "테스트 식품",
        "group_name": "과자",
        "research_year": "2023",
        "maker_name": "테스트 회사",
        "ref_name": "식품영양성분DB",
        "serving_size": 100.0,
        "calorie": 350.0,
        "carbohydrate": 50.0,
        "protein": 5.0,
        "province": 15.0,
        "sugars": 20.0,
        "salt": 1.0,
        "cholesterol": 0.0,
        "saturated_fatty_acids": 5.0,
        "trans_fat": 0.0
    }


class TestFoodAPI:
    """식품 API 비동기 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_create_food(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
        """POST /foods/ - 식품 생성 테스트"""
        response = await async_client.post("/foods/", json=sample_food)
        
        # 상태 코드 및 응답 검증
        assert response.status_code == 201
        data = response.json()
        assert data["food_cd"] == sample_food["food_cd"]
        assert data["food_name"] == sample_food["food_name"]
        assert "id" in data  # ID가 생성되었는지 확인
        
        return data  # 다른 테스트에서 참조할 수 있도록 반환

    @pytest.mark.asyncio
    async def test_get_food(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
        """GET /foods/{food_id} - 식품 조회 테스트"""
        # 먼저 식품 생성
        create_response = await async_client.post("/foods/", json=sample_food)
        created_food = create_response.json()
        food_id = created_food["id"]
        
        # 생성된 식품 조회
        response = await async_client.get(f"/foods/{food_id}")
        
        # 상태 코드 및 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == food_id
        assert data["food_name"] == sample_food["food_name"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_food(self, async_client: AsyncClient):
        """GET /foods/{food_id} - 존재하지 않는 식품 조회 테스트"""
        # 아주 큰 ID값을 사용하여 확실히 존재하지 않는 식품 조회
        response = await async_client.get("/foods/999999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_search_foods(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
        """GET /foods/ - 식품 검색 테스트"""
        # 먼저 식품 생성
        await async_client.post("/foods/", json=sample_food)
        
        # 이름으로 검색
        response = await async_client.get(f"/foods/?food_name={sample_food['food_name']}")
        
        # 상태 코드 및 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert any(item["food_name"] == sample_food["food_name"] for item in data["items"])

    @pytest.mark.asyncio
    async def test_update_food(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
        """PUT /foods/{food_id} - 식품 정보 업데이트 테스트"""
        # 먼저 식품 생성
        create_response = await async_client.post("/foods/", json=sample_food)
        created_food = create_response.json()
        food_id = created_food["id"]
        
        # 업데이트할 데이터
        update_data = {
            "food_name": "업데이트된 식품명",
            "calorie": 400.0
        }
        
        # 식품 정보 업데이트
        response = await async_client.put(f"/foods/{food_id}", json=update_data)
        
        # 상태 코드 및 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == food_id
        assert data["food_name"] == update_data["food_name"]
        assert data["calorie"] == update_data["calorie"]
        # 업데이트하지 않은 필드는 유지되어야 함
        assert data["food_cd"] == sample_food["food_cd"]

    @pytest.mark.asyncio
    async def test_delete_food(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
        """DELETE /foods/{food_id} - 식품 삭제 테스트"""
        # 먼저 식품 생성
        create_response = await async_client.post("/foods/", json=sample_food)
        created_food = create_response.json()
        food_id = created_food["id"]
        
        # 식품 삭제
        response = await async_client.delete(f"/foods/{food_id}")
        
        # 상태 코드 검증 (204 No Content)
        assert response.status_code == 204
        
        # 삭제 확인
        get_response = await async_client.get(f"/foods/{food_id}")
        assert get_response.status_code == 404
