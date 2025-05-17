"""비동기 테스트를 위한 공통 설정 및 fixture 제공"""
import os
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Any
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.database import Base, get_async_db
from main import app

# 테스트용 데이터베이스 파일 경로 설정 (app/tests 디렉토리에 파일 생성)
import os

# 현재 파일의 디렉토리 경로 가져오기
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 테스트 DB 파일 경로 설정
TEST_DB_FILE = os.path.join(CURRENT_DIR, "test_food_nutrition.db")

# 테스트 실행 전 기존 DB 파일이 있다면 삭제
if os.path.exists(TEST_DB_FILE):
    os.remove(TEST_DB_FILE)

# SQLite 연결 문자열 생성
TEST_ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

# 테스트용 비동기 엔진 생성
test_async_engine = create_async_engine(
    TEST_ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
    future=True
)


# 테스트용 비동기 DB 세션 제공 함수
async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """테스트용 비동기 데이터베이스 세션 제공"""
    async_session = AsyncSession(bind=test_async_engine, expire_on_commit=False)
    try:
        yield async_session
    finally:
        await async_session.close()


# 의존성 오버라이드 설정
app.dependency_overrides[get_async_db] = override_get_async_db



@pytest_asyncio.fixture(scope="session")
async def create_test_tables():
    """테스트 전용 데이터베이스 테이블 생성"""
    # 테스트 실행용 데이터베이스 파일에 테이블 생성
    print(f"Creating tables in test database: {TEST_DB_FILE}")
    async with test_async_engine.begin() as conn:
        # 테이블 생성
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully")
    yield
    # 테스트 완료 후 데이터베이스 연결 종료 처리
    await test_async_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def reset_test_data(create_test_tables):
    """테스트 실행 전 테이블의 데이터 초기화"""
    # 테이블 생성 후 각 테스트마다 테이블 데이터 클리어
    print("Clearing test data before test")
    tables = Base.metadata.sorted_tables
    async with test_async_engine.begin() as conn:
        for table in tables:
            await conn.execute(table.delete())
    yield
    # 테스트 후 데이터 초기화 상태 가능


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """비동기 테스트 클라이언트 생성

    FastAPI 애플리케이션에 대한 비동기 HTTP 요청을 수행할 수 있는 클라이언트 제공
    
    Yields:
        비동기 HTTP 클라이언트 인스턴스
    """
    from httpx import ASGITransport
    
    # HTTPX AsyncClient에서는 app 파라미터 대신 transport를 사용
    transport = ASGITransport(app=app)
    
    # base_url을 'http://test'에서 'http://test/api/v1'로 변경하여 API_PREFIX를 포함
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """비동기 테스트 데이터베이스 세션 제공
    
    Yields:
        비동기 SQLAlchemy 세션 인스턴스
    """
    async with AsyncSession(bind=test_async_engine) as session:
        yield session

