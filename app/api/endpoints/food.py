from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from app.schemas import food as schemas
from app.services.food import FoodService
from app.services.dependencies import get_food_service

router = APIRouter()


@router.post("/", response_model=schemas.Food, status_code=status.HTTP_201_CREATED)
async def create_food(
    food: schemas.FoodCreate, 
    food_service: Annotated[FoodService, Depends(get_food_service)]
) -> schemas.Food:
    """식품 데이터 생성 API - 새로운 식품 정보를 데이터베이스에 추가
    
    Args:
        food: 생성할 식품 데이터 (식품명, 코드, 영양성분 등 포함)
        food_service: 식품 서비스 계층(의존성 주입)
        
    Returns:
        생성된 식품 데이터 (데이터베이스 ID 포함)
    """
    return await food_service.create_food(food)


@router.get("/", response_model=schemas.FoodSearchResponse)
async def search_foods(
    food_service: Annotated[FoodService, Depends(get_food_service)],
    food_name: str | None = None,
    research_year: str | None = None,
    maker_name: str | None = None,
    food_code: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> schemas.FoodSearchResponse:
    """식품 검색 API - 다양한 조건으로 식품 데이터 검색 및 페이지네이션 제공
    
    Args:
        food_service: 식품 서비스 계층(의존성 주입)
        food_name: (선택) 검색할 식품 이름 - 부분 일치 검색
        research_year: (선택) 연구 연도 기준 필터링
        maker_name: (선택) 제조사 이름 기준 필터링
        food_code: (선택) 식품 코드 기준 필터링
        skip: 페이지네이션 - 건너뚰 레코드 수
        limit: 페이지네이션 - 한 번에 가져올 최대 레코드 수
        
    Returns:
        검색된 식품 목록과 총 개수가 포함된 응답 객체
    """
    search_params = schemas.FoodSearchRequest(
        food_name=food_name,
        research_year=research_year,
        maker_name=maker_name,
        food_code=food_code,
    )
    items, total = await food_service.search_foods(search_params, skip, limit)
    return schemas.FoodSearchResponse(items=items, total=total)


@router.get("/{food_id}", response_model=schemas.Food)
async def get_food(
    food_id: int, 
    food_service: Annotated[FoodService, Depends(get_food_service)]
) -> schemas.Food:
    """식품 상세 조회 API - 해당 ID의 식품 상세 정보 반환
    
    Args:
        food_id: 조회할 식품의 고유 식별자(ID)
        food_service: 식품 서비스 계층(의존성 주입)
        
    Returns:
        조회된 식품 상세 정보
        
    Raises:
        HTTPException: 해당 ID의 식품이 없을 경우 404 오류 발생
    """
    food = await food_service.get_food(food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food


@router.put("/{food_id}", response_model=schemas.Food)
async def update_food(
    food_id: int, 
    food: schemas.FoodUpdate, 
    food_service: Annotated[FoodService, Depends(get_food_service)]
) -> schemas.Food:
    """식품 업데이트 API - 해당 ID의 식품 정보 수정
    
    Args:
        food_id: 수정할 식품의 고유 식별자(ID)
        food: 수정할 내용이 포함된 식품 데이터 (변경할 필드만 포함)
        food_service: 식품 서비스 계층(의존성 주입)
        
    Returns:
        수정된 식품 정보
        
    Raises:
        HTTPException: 해당 ID의 식품이 없을 경우 404 오류 발생
    """
    updated_food = await food_service.update_food(food_id, food)
    if not updated_food:
        raise HTTPException(status_code=404, detail="Food not found")
    return updated_food


@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food(
    food_id: int, 
    food_service: Annotated[FoodService, Depends(get_food_service)]
) -> None:
    """식품 삭제 API - 해당 ID의 식품 데이터 삭제
    
    Args:
        food_id: 삭제할 식품의 고유 식별자(ID)
        food_service: 식품 서비스 계층(의존성 주입)
        
    Returns:
        None - 204 No Content 상태코드 반환
        
    Raises:
        HTTPException: 해당 ID의 식품이 없을 경우 404 오류 발생
    """
    if not await food_service.delete_food(food_id):
        raise HTTPException(status_code=404, detail="Food not found")
