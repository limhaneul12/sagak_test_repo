from fastapi import APIRouter
from app.api.endpoints import food

api_router = APIRouter()
api_router.include_router(food.router, prefix="/foods", tags=["foods"])
