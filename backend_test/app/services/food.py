from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import food as models
from app.schemas import food as schemas


class FoodService:
    def __init__(self, db: Session):
        self.db = db

    def get_food(self, food_id: int) -> models.Food | None:
        return self.db.query(models.Food).filter(models.Food.id == food_id).first()

    def get_food_by_code(self, food_cd: str) -> models.Food | None:
        return self.db.query(models.Food).filter(models.Food.food_cd == food_cd).first()

    def create_food(self, food: schemas.FoodCreate) -> models.Food:
        db_food = models.Food(**food.model_dump())
        self.db.add(db_food)
        self.db.commit()
        self.db.refresh(db_food)
        return db_food

    def update_food(self, food_id: int, food_update: schemas.FoodUpdate) -> models.Food | None:
        db_food = self.get_food(food_id)
        if not db_food:
            return None

        update_data = food_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_food, key, value)

        self.db.commit()
        self.db.refresh(db_food)
        return db_food

    def delete_food(self, food_id: int) -> bool:
        db_food = self.get_food(food_id)
        if not db_food:
            return False

        self.db.delete(db_food)
        self.db.commit()
        return True

    def search_foods(
        self, search_params: schemas.FoodSearchRequest, skip: int = 0, limit: int = 100
    ) -> tuple[list[models.Food], int]:
        query = self.db.query(models.Food)

        # Apply filters if provided
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
            query = query.filter(or_(*filters))

        total = query.count()
        items = query.offset(skip).limit(limit).all()

        return items, total
