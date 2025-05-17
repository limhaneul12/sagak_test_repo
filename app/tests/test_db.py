"""데이터베이스 연결 및 스키마 테스트"""
import pytest
import sqlite3
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food import Food


class TestDatabase:
    """데이터베이스 연결 및 스키마 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self, db_session: AsyncSession):
        """데이터베이스 연결 테스트"""
        # 간단한 쿼리 실행
        result = await db_session.execute(select(1))
        assert result.scalar_one() == 1
    
    @pytest.mark.asyncio
    async def test_food_schema(self, db_session: AsyncSession):
        """Food 모델 스키마 테스트"""
        # Food 모델을 사용한 쿼리 실행
        result = await db_session.execute(select(Food).limit(1))
        
        # 결과가 없어도 쿼리가 성공적으로 실행되면 스키마는 정상
        # 실제 결과가 있는지는 중요하지 않음 (테스트 데이터베이스에 따라 다를 수 있음)
        _ = result.scalar_one_or_none()

    def test_sqlite_direct_connection(self):
        """SQLite 직접 연결 테스트"""
        # 직접 SQLite 연결 테스트
        conn = sqlite3.connect("/Users/imhaneul/Documents/sagak_test_repo/data/food_nutrition.db")
        try:
            # 기본 쿼리 실행
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(foods)")
            columns = cursor.fetchall()
            
            # 테이블 구조 확인
            column_names = [col[1] for col in columns]
            required_columns = ["id", "food_cd", "food_name", "group_name"]
            
            # 필수 컬럼 존재 여부 확인
            for col in required_columns:
                assert col in column_names, f"컬럼 {col}이 foods 테이블에 존재하지 않습니다."
            
        finally:
            conn.close()
