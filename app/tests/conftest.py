"""테스트를 위한 공통 설정 및 fixture 제공"""
import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status
from fastapi.testclient import TestClient
from typing import Generator

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 실제 프로젝트 구조에 맞춰 import 경로 수정
from app.db.database import Base
from app.models import food as models
from app.services.food import FoodService

# 테스트용 모의 서비스 가져오기
from app.schemas import food as schemas
from app.tests.mock_food_service import MockFoodService

# 루트 디렉토리의 main 모듈 가져오기
import main
from main import app
from app.api.endpoints.food import get_async_db


# 테스트용 데이터베이스 파일 경로 설정 (동기식 드라이버 사용)
DB_PATH = "/Users/imhaneul/Documents/sagak_test_repo/data/food_nutrition.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 동기식 테스트용 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 동기식 테스트용 세션 생성
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# 동기식 테스트 DB 의존성 오버라이드 함수
def override_get_async_db() -> Generator[Session, None, None]:
    """동기식 테스트용 DB 세션 생성"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 동기식 DB 의존성 오버라이드 적용
app.dependency_overrides[get_async_db] = override_get_async_db

# API 엔드포인트 모듈에서 함수 가져오기
from app.api.endpoints import food as food_endpoints
from app.services.food import FoodService

# 테스트용 FoodService 객체 생성 함수
def get_mock_food_service(db: Session = Depends(override_get_async_db)):
    return MockFoodService(db)

# 의존성 오버라이드 설정
# 중요: FoodService의 비동기 메소드 대신 MockFoodService의 동기 메소드가 사용되도록 함
app.dependency_overrides[FoodService] = get_mock_food_service


@pytest.fixture(scope="function")
def test_db():
    """동기식 테스트용 데이터베이스 설정"""
    # 기존 테이블 구조 유지
    yield


@pytest.fixture(scope="function")
def client(test_db):
    """테스트 클라이언트 생성"""
    with TestClient(app) as c:
        yield c
        
# 테스트 시작 시 API 엔드포인트 패치
@pytest.fixture(scope="session", autouse=True)
def patch_endpoints():
    # 동기식 MockFoodService와 비동기 함수를 연결하기 위한 패치
    # 이 기능은 이제 dependency_overrides에서 처리
    yield
    
    # 테스트 종료 후 클린업
    if FoodService in app.dependency_overrides:
        del app.dependency_overrides[FoodService]
