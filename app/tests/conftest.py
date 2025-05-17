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

# 테스트용 데이터베이스 파일 경로 설정
TEST_DB_PATH = "/Users/imhaneul/Documents/sagak_test_repo/data/food_nutrition.db"
TEST_ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

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

