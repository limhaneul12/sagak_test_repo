from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import SessionLocal
from app.models import food as models
from app.schemas import food as schemas
from app.services.food import FoodService

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.Food, status_code=status.HTTP_201_CREATED)
async def create_food(
    food: schemas.FoodCreate, db: Annotated[Session, Depends(get_db)]
) -> schemas.Food:
    food_service = FoodService(db)
    return food_service.create_food(food)


@router.get("/{food_id}", response_model=schemas.Food)
async def get_food(food_id: int, db: Annotated[Session, Depends(get_db)]) -> schemas.Food:
    food_service = FoodService(db)
    food = food_service.get_food(food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food


@router.get("/", response_model=schemas.FoodSearchResponse)
async def search_foods(
    db: Annotated[Session, Depends(get_db)],
    food_name: str | None = None,
    research_year: str | None = None,
    maker_name: str | None = None,
    food_code: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> schemas.FoodSearchResponse:
    food_service = FoodService(db)
    search_params = schemas.FoodSearchRequest(
        food_name=food_name,
        research_year=research_year,
        maker_name=maker_name,
        food_code=food_code,
    )
    items, total = food_service.search_foods(search_params, skip, limit)
    return schemas.FoodSearchResponse(items=items, total=total)


@router.put("/{food_id}", response_model=schemas.Food)
async def update_food(
    food_id: int, food: schemas.FoodUpdate, db: Annotated[Session, Depends(get_db)]
) -> schemas.Food:
    food_service = FoodService(db)
    updated_food = food_service.update_food(food_id, food)
    if not updated_food:
        raise HTTPException(status_code=404, detail="Food not found")
    return updated_food


@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food(food_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    food_service = FoodService(db)
    if not food_service.delete_food(food_id):
        raise HTTPException(status_code=404, detail="Food not found")
