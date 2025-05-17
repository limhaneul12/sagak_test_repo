from pydantic import BaseModel


class FoodBase(BaseModel):
    """식품 정보의 기본 데이터 모델
    
    모든 식품 관련 스키마의 기본이 되는 클래스로, 필수 필드들을 정의
    """
    food_cd: str                # 식품코드 - 고유 식별자
    group_name: str             # 식품군 - 식품의 분류 카테고리
    food_name: str              # 식품이름 - 식품의 명칭
    research_year: str          # 조사년도 - 데이터가 수집된 연도(YYYY)
    maker_name: str             # 지역/제조사 - 식품의 생산지 또는 제조회사
    ref_name: str               # 자료출처 - 데이터의 원천 정보
    serving_size: float         # 1회 제공량 - 일반적인 1회 섭취 기준량
    calorie: float              # 열량(kcal) - 1회 제공량당 열량
    carbohydrate: float         # 탄수화물(g) - 1회 제공량당 함유량
    protein: float              # 단백질(g) - 1회 제공량당 함유량
    province: float             # 지방(g) - 1회 제공량당 함유량
    sugars: float               # 총당류(g) - 1회 제공량당 함유량
    salt: float                 # 나트륨(mg) - 1회 제공량당 함유량
    cholesterol: float          # 콜레스테롤(mg) - 1회 제공량당 함유량
    saturated_fatty_acids: float # 포화지방산(g) - 1회 제공량당 함유량
    trans_fat: float            # 트랜스지방(g) - 1회 제공량당 함유량


class FoodCreate(FoodBase):
    """식품 생성을 위한 데이터 모델
    
    새로운 식품 정보를 생성할 때 사용됩니다.
    현재는 FoodBase와 동일하지만, 필요시 추가 필드나 검증 로직을 포함
    """
    pass


class FoodUpdate(BaseModel):
    """식품 정보 업데이트를 위한 데이터 모델
    
    기존 식품 정보를 업데이트할 때 사용됩니다.
    모든 필드가 선택적(optional)으로, 변경할 필드만 포함하여 요청
    """
    food_cd: str | None = None
    group_name: str | None = None
    food_name: str | None = None
    research_year: str | None = None
    maker_name: str | None = None
    ref_name: str | None = None
    serving_size: float | None = None
    calorie: float | None = None
    carbohydrate: float | None = None
    protein: float | None = None
    province: float | None = None
    sugars: float | None = None
    salt: float | None = None
    cholesterol: float | None = None
    saturated_fatty_acids: float | None = None
    trans_fat: float | None = None


class Food(FoodBase):
    """완전한 식품 정보 데이터 모델
    
    데이터베이스에서 조회된 전체 식품 정보를 표현
    FoodBase의 모든 필드에 추가로 데이터베이스 ID 포함
    """
    id: int  # 데이터베이스 ID - 시스템 내부에서 사용되는 고유 식별자

    class Config:
        from_attributes = True  # ORM 모델에서 데이터 가져올 수 있도록 설정


class FoodSearchRequest(BaseModel):
    """식품 검색 요청 데이터 모델
    
    식품 정보 검색할 때 사용 파라미터 정의
    모든 필드 선택적, 제공 필드에 따라 검색 조건 구성
    """
    food_name: str | None = None      # 식품이름 - 부분 일치 검색 가능
    research_year: str | None = None  # 조사년도 - 정확한 연도 일치 검색
    maker_name: str | None = None     # 지역/제조사 - 부분 일치 검색 가능
    food_code: str | None = None      # 식품코드 - 정확한 코드 일치 검색


class FoodSearchResponse(BaseModel):
    """식품 검색 응답 데이터 모델
    
    검색 결과 반환 구조 정의
    식품 목록과 총 결과 수 포함
    """
    items: list[Food]  # 검색된 식품 목록
    total: int         # 검색 결과의 총 개수 (페이지네이션 지원용)
