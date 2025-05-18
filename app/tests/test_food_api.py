"""식품 정보 API 엔드포인트 비동기 테스트"""
import os
import sys

# 프로젝트 루트 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 모든 모델 클래스를 명시적으로 임포트하여 Base에 매핑되도록 함
from main import app
from app.db.database import Base
from app.models.food import Food  # Food 모델을 명시적으로 임포트
from app.services.dependencies import get_async_db

# 테스트용 데이터베이스 설정
TEST_DB_FILE = "test_food_nutrition.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

# 비동기 엔진 생성
test_async_engine = create_async_engine(TEST_DB_URL, echo=False)
TestAsyncSessionLocal = sessionmaker(
    test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session", autouse=True)
def cleanup_db() -> Generator[None, None, None]:
    """테스트 세션 종료 후 데이터베이스 엔진 정리"""
    yield
    # 세션 종료 시 비동기 엔진 정리를 동기적으로 처리
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_async_engine.dispose())
    print("Test engine disposed at session end")
    
    # 테스트 DB 파일 정리
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
        print(f"Removed test database file: {TEST_DB_FILE}")



# 테스트용 데이터베이스 의존성 오버라이드
async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """테스트용 비동기 데이터베이스 세션 제공"""
    async_session = AsyncSession(bind=test_async_engine, expire_on_commit=False)
    try:
        yield async_session
    finally:
        await async_session.close()


# 의존성 오버라이드 설정
app.dependency_overrides[get_async_db] = override_get_async_db


@pytest_asyncio.fixture(scope="function")
async def create_test_tables() -> AsyncGenerator[None, None]:
    """테스트 테이블 생성 - 함수별로 새로운 테스트 DB 환경 제공"""
    print(f"Setting up test tables for test")
    
    # 테이블 삭제 후 재생성
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("Test tables created successfully")
    yield
    
    # 각 테스트 완료 후 테이블 데이터 정리
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("Test tables cleaned up")


@pytest_asyncio.fixture
async def db_session(create_test_tables) -> AsyncGenerator[AsyncSession, None]:
    """테스트용 데이터베이스 세션 제공"""
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture
async def async_client(create_test_tables) -> AsyncGenerator[AsyncClient, None]:
    """비동기 HTTP 테스트 클라이언트 제공"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        yield client


@pytest.fixture
def sample_food(request) -> dict[str, str | float]:
    """테스트용 샘플 식품 데이터 - 테스트 함수마다 고유한 food_cd 제공"""
    # 테스트 함수명을 기반으로 고유 식별자 생성
    test_name = request.node.name
    unique_id = abs(hash(test_name)) % 10000000
    food_cd = f"D{unique_id:07d}"
    
    return {
        "food_cd": food_cd,
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
    async def test_create_food(self, async_client: AsyncClient, sample_food: dict[str, str | float]):
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
    async def test_get_food(self, async_client: AsyncClient, sample_food: dict[str, str | float]):
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
    async def test_search_foods(self, async_client: AsyncClient, sample_food: dict[str, str | float]) -> None:
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
    async def test_update_food(self, async_client: AsyncClient, sample_food: dict[str, str | float]) -> None:
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
    async def test_delete_food(self, async_client: AsyncClient, sample_food: dict[str, str | float]) -> None:
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
