"""서비스 레이어 의존성 제공"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.services.food import FoodService


async def get_food_service(db: AsyncSession = Depends(get_async_db)) -> FoodService:
    """식품 서비스 의존성 제공
    
    Args:
        db: 비동기 데이터베이스 세션
        
    Returns:
        초기화된 FoodService 인스턴스
    """
    return FoodService(db)
