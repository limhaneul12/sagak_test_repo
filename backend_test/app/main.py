"""FastAPI 애플리케이션 엔트리 포인트"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.db.database import engine
from app.models import food as models
from app.core.config import settings

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION
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
    """루트 엔드포인트 - API 상태 확인
    
    Returns:
        API 실행 상태 메시지
    """
    return {"message": "Food Nutrition Database API is running"}
