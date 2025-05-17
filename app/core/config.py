"""환경 변수 및 .env 파일에서 설정을 로드하는 모듈"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 관리 클래스"""
    
    # .env 파일에서 로드하는 설정
    APP_TITLE: str
    APP_VERSION: str
    DATABASE_URL: str
    CORS_ORIGINS: list[str]
    API_PREFIX: str
    
    # SQLite 관련 추가 설정
    DATABASE_CONNECT_ARGS: dict[str, bool] = {"check_same_thread": False}
    SQLALCHEMY_AUTOCOMMIT: bool = False
    SQLALCHEMY_AUTOFLUSH: bool = False
    
    # CORS 추가 설정
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 전역 설정 인스턴스 생성
settings = Settings()
