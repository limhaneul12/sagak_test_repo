from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLAlchemy 엔진 초기화
engine = create_engine(
    settings.DATABASE_URL, connect_args=settings.DATABASE_CONNECT_ARGS
)

# 데이터베이스 세션 설정
SessionLocal = sessionmaker(
    autocommit=settings.SQLALCHEMY_AUTOCOMMIT,
    autoflush=settings.SQLALCHEMY_AUTOFLUSH,
    bind=engine
)

# SQLAlchemy 모델 기본 클래스
Base = declarative_base()
