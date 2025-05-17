from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import AsyncGenerator

from app.core.config import settings

# SQLite URL을 비동기 호환 형식으로 변환
async_database_url = settings.DATABASE_URL

# 비동기 SQLAlchemy 엔진 초기화
async_engine = create_async_engine(
    async_database_url, 
    connect_args=settings.DATABASE_CONNECT_ARGS,
    future=True
)

# 비동기 데이터베이스 세션 설정
AsyncSessionLocal = sessionmaker(
    autocommit=settings.SQLALCHEMY_AUTOCOMMIT,
    autoflush=settings.SQLALCHEMY_AUTOFLUSH,
    bind=async_engine,
    class_=AsyncSession
)

# SQLAlchemy 2.0 스타일 - 모델 기본 클래스
class Base(DeclarativeBase):
    """모든 모델의 기본 클래스"""
    pass


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """비동기 데이터베이스 세션 디펜던시"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
