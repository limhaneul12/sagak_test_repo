from typing import TypeAlias, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, func
from sqlalchemy.future import select

from app.models import food as models
from app.schemas import food as schemas

# 타입 엘리어스 정의
FoodList: TypeAlias = Sequence[models.Food]
FoodSearchResult: TypeAlias = tuple[FoodList, int]


class FoodService:
    """식품 영양성분 데이터를 관리하는 서비스 클래스
    
    데이터베이스 연산을 추상화하여 식품 정보에 대한 CRUD 작업 및 검색 기능 제공
    """
    def __init__(self, db: AsyncSession) -> None:
        """서비스 초기화 생성자
        
        Args:
            db: SQLAlchemy 비동기 데이터베이스 세션
        """
        self.db = db

    async def get_food(self, food_id: int) -> models.Food | None:
        """아이디로 식품 정보 조회
        
        Args:
            food_id: 조회할 식품의 고유 ID
            
        Returns:
            조회된 식품 객체 또는 찾지 못한 경우 None
        """
        stmt = select(models.Food).where(models.Food.id == food_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_food_by_code(self, food_cd: str) -> models.Food | None:
        """식품코드로 식품 정보 조회
        
        Args:
            food_cd: 조회할 식품의 코드 (예: D000006)
            
        Returns:
            조회된 식품 객체 또는 찾지 못한 경우 None
        """
        stmt = select(models.Food).where(models.Food.food_cd == food_cd)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_food(self, food: schemas.FoodCreate) -> models.Food:
        """새로운 식품 정보 생성
        
        Args:
            food: 생성할 식품 정보 스키마
            
        Returns:
            생성된 식품 정보 객체 (ID 값 포함)
        """
        db_food = models.Food(**food.model_dump())
        self.db.add(db_food)
        await self.db.commit()
        await self.db.refresh(db_food)
        return db_food

    async def update_food(self, food_id: int, food_update: schemas.FoodUpdate) -> models.Food | None:
        """기존 식품 정보 업데이트
        
        제공된 필드만 선택적으로 업데이트합니다.
        
        Args:
            food_id: 업데이트할 식품의 ID
            food_update: 갱신할 정보가 포함된 스키마 (선택적 필드)
            
        Returns:
            업데이트된 식품 정보 객체 또는 찾지 못한 경우 None
        """
        db_food = await self.get_food(food_id)
        if not db_food:
            return None

        update_data = food_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_food, key, value)

        await self.db.commit()
        await self.db.refresh(db_food)
        return db_food

    async def delete_food(self, food_id: int) -> bool:
        """식품 정보 삭제
        
        Args:
            food_id: 삭제할 식품의 ID
            
        Returns:
            삭제 성공 여부 (True: 성공, False: 해당 ID의 식품 없음)
        """
        db_food = await self.get_food(food_id)
        if not db_food:
            return False

        await self.db.delete(db_food)
        await self.db.commit()
        return True

    async def search_foods(
        self, search_params: schemas.FoodSearchRequest, skip: int = 0, limit: int = 100
    ) -> FoodSearchResult:
        """식품 정보 검색
        
        여러 기준으로 식품 정보를 검색하고 결과를 페이지네이션하여 반환합니다.
        검색 조건이 없는 경우 모든 식품 정보를 반환합니다.
        
        Args:
            search_params: 검색 조건이 포함된 요청 객체
                - food_name: 식품명 (부분 일치 검색)
                - research_year: 연도 (정확한 일치 검색)
                - maker_name: 제조사/지역 (부분 일치 검색)
                - food_code: 식품코드 (정확한 일치 검색)
            skip: 건너뛰는 개수 (페이지네이션)
            limit: 반환할 최대 개수 (페이지네이션)
            
        Returns:
            두 값의 튜플:
              - items: 검색된 식품 정보 목록
              - total: 전체 검색 결과 개수
        """
        stmt = select(models.Food)

        # 제공된 필터 조건 적용
        filters = []
        if search_params.food_name:
            filters.append(models.Food.food_name.like(f"%{search_params.food_name}%"))
        if search_params.research_year:
            filters.append(models.Food.research_year == search_params.research_year)
        if search_params.maker_name:
            filters.append(models.Food.maker_name.like(f"%{search_params.maker_name}%"))
        if search_params.food_code:
            filters.append(models.Food.food_cd == search_params.food_code)

        if filters:
            stmt = stmt.where(or_(*filters))
            
        # 총 개수 검색
        total_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.db.execute(total_stmt)
        total = result.scalar_one()
        
        # 실제 데이터 검색 (offset, limit 적용)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        items = result.scalars().all()

        return items, total
    
