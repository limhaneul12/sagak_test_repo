"""FastAPI 애플리케이션 엔트리 포인트"""
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.db.database import async_engine, Base
from app.models import food as models
from app.core.config import settings

# ✅ lifespan 컨텍스트로 DB 테이블 생성 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 테스트 환경에서는 lifespan 로직 실행 안함
    is_test = 'pytest' in sys.modules
    
    if not is_test:
        try:
            # DB 테이블 생성
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"Database initialization error: {e}")
            
    yield  # 앱 실행 시작

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan  # ✅ lifespan 등록
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    """루트 엔드포인트 - API 상태 확인"""
    return {"message": "Food Nutrition Database API is running"}