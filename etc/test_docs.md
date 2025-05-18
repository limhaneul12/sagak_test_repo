# Food Nutrition Database API 테스트 문서

## 테스트 개요

이 문서는 Food Nutrition Database API에 대한 테스트 환경 구성, 테스트 케이스 설명, 그리고 테스트 결과를 상세히 기술합니다. 모든 테스트는 pytest 프레임워크를 사용하여 비동기 테스트 환경에서 수행되었습니다.

## 테스트 환경

- **Python 버전**: 3.12.10
- **운영체제**: macOS (darwin)
- **테스트 프레임워크**: pytest 8.3.5, pytest-asyncio 0.26.0
- **데이터베이스**: SQLite (data/food_nutrition.db)
- **테스트 설정**: 
  - asyncio_mode = strict
  - asyncio_default_fixture_loop_scope = function

## 테스트 구조

테스트는 크게 두 부분으로 나뉩니다:
1. **데이터베이스 테스트**: 데이터베이스 연결 및 스키마 검증
2. **API 엔드포인트 테스트**: REST API 기능 검증

### 테스트 파일 구조

```
app/tests/
├── __init__.py
├── conftest.py            # 테스트 공통 설정 및 픽스처
├── test_db.py             # 데이터베이스 테스트
└── test_food_api.py       # API 엔드포인트 테스트
```

## 테스트 픽스처

테스트에 사용된 주요 픽스처는 다음과 같습니다:

### 1. async_client

비동기 HTTP 테스트 클라이언트를 제공하는 픽스처입니다. FastAPI 애플리케이션에 대한 요청을 시뮬레이션하는 데 사용됩니다.

```python
@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """비동기 테스트 클라이언트 생성"""
    from httpx import ASGITransport
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        yield client
```

### 2. db_session

비동기 테스트 데이터베이스 세션을 제공하는 픽스처입니다.

```python
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """비동기 테스트 데이터베이스 세션 제공"""
    async with AsyncSession(bind=test_async_engine) as session:
        yield session
```

### 3. sample_food

테스트에 사용할 샘플 식품 데이터를 제공하는 픽스처입니다.

```python
@pytest.fixture
def sample_food() -> Dict[str, Any]:
    """테스트용 샘플 식품 데이터"""
    return {
        "food_cd": "D000001",
        "food_name": "테스트 식품",
        "group_name": "과자",
        # ... 다른 필드들 ...
    }
```

## 데이터베이스 테스트 케이스

### 1. test_database_connection

데이터베이스 연결이 정상적으로 작동하는지 테스트합니다.

```python
@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """데이터베이스 연결 테스트"""
    # 간단한 쿼리 실행
    result = await db_session.execute(select(1))
    assert result.scalar_one() == 1
```

### 2. test_food_schema

Food 모델 스키마가 올바르게 정의되어 있는지 테스트합니다.

```python
@pytest.mark.asyncio
async def test_food_schema(db_session: AsyncSession):
    """Food 모델 스키마 테스트"""
    # Food 모델을 사용한 쿼리 실행
    result = await db_session.execute(select(Food).limit(1))
    _ = result.scalar_one_or_none()
```

### 3. test_sqlite_direct_connection

SQLite 직접 연결 및 테이블 구조를 테스트합니다.

```python
def test_sqlite_direct_connection():
    """SQLite 직접 연결 테스트"""
    # 직접 SQLite 연결 테스트
    conn = sqlite3.connect("sagak_test_repo/data/food_nutrition.db")
    try:
        # 테이블 구조 확인
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(foods)")
        columns = cursor.fetchall()
        
        # 필수 컬럼 존재 여부 확인
        column_names = [col[1] for col in columns]
        required_columns = ["id", "food_cd", "food_name", "group_name"]
        
        for col in required_columns:
            assert col in column_names
            
    finally:
        conn.close()
```

## API 엔드포인트 테스트 케이스

### 1. test_create_food

식품 생성 API 엔드포인트를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_create_food(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
    """POST /foods/ - 식품 생성 테스트"""
    response = await async_client.post("/foods/", json=sample_food)
    
    # 상태 코드 및 응답 검증
    assert response.status_code == 201
    data = response.json()
    assert data["food_cd"] == sample_food["food_cd"]
    assert data["food_name"] == sample_food["food_name"]
    assert "id" in data  # ID가 생성되었는지 확인
```

### 2. test_get_food

식품 조회 API 엔드포인트를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_get_food(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
    """GET /foods/{food_id} - 식품 조회 테스트"""
    # 먼저 식품 생성
    create_response = await async_client.post("/foods/", json=sample_food)
    created_food = create_response.json()
    food_id = created_food["id"]
    
    # 생성된 식품 조회
    response = await async_client.get(f"/foods/{food_id}")
    
    # 상태 코드 및 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == food_id
    assert data["food_name"] == sample_food["food_name"]
```

### 3. test_get_nonexistent_food

존재하지 않는 식품 ID에 대한 요청을 테스트합니다.

```python
@pytest.mark.asyncio
async def test_get_nonexistent_food(self, async_client: AsyncClient):
    """GET /foods/{food_id} - 존재하지 않는 식품 조회 테스트"""
    # 아주 큰 ID값을 사용하여 확실히 존재하지 않는 식품 조회
    response = await async_client.get("/foods/999999999")
    assert response.status_code == 404
```

### 4. test_search_foods

식품 검색 API 엔드포인트를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_search_foods(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
    """GET /foods/ - 식품 검색 테스트"""
    # 먼저 식품 생성
    await async_client.post("/foods/", json=sample_food)
    
    # 이름으로 검색
    response = await async_client.get(f"/foods/?food_name={sample_food['food_name']}")
    
    # 상태 코드 및 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert any(item["food_name"] == sample_food["food_name"] for item in data["items"])
```

### 5. test_update_food

식품 정보 업데이트 API 엔드포인트를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_update_food(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
    """PUT /foods/{food_id} - 식품 정보 업데이트 테스트"""
    # 먼저 식품 생성
    create_response = await async_client.post("/foods/", json=sample_food)
    created_food = create_response.json()
    food_id = created_food["id"]
    
    # 업데이트할 데이터
    update_data = {
        "food_name": "업데이트된 식품명",
        "calorie": 400.0
    }
    
    # 식품 정보 업데이트
    response = await async_client.put(f"/foods/{food_id}", json=update_data)
    
    # 상태 코드 및 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == food_id
    assert data["food_name"] == update_data["food_name"]
    assert data["calorie"] == update_data["calorie"]
    # 업데이트하지 않은 필드는 유지되어야 함
    assert data["food_cd"] == sample_food["food_cd"]
```

### 6. test_delete_food

식품 삭제 API 엔드포인트를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_delete_food(self, async_client: AsyncClient, sample_food: Dict[str, Any]):
    """DELETE /foods/{food_id} - 식품 삭제 테스트"""
    # 먼저 식품 생성
    create_response = await async_client.post("/foods/", json=sample_food)
    created_food = create_response.json()
    food_id = created_food["id"]
    
    # 식품 삭제
    response = await async_client.delete(f"/foods/{food_id}")
    
    # 상태 코드 검증 (204 No Content)
    assert response.status_code == 204
    
    # 삭제 확인
    get_response = await async_client.get(f"/foods/{food_id}")
    assert get_response.status_code == 404
```

## 테스트 실행 방법

### 1. 가상환경에서 직접 실행

```bash
# 가상환경 활성화
source .venv/bin/activate

# pytest 직접 실행
pytest app/tests/
```

### 2. run_tests.py 스크립트 사용

```bash
# run_tests.py 스크립트 실행
python run_tests.py
```

이 스크립트는 테스트를 실행하고 결과를 test_result.txt 파일에 저장합니다.

## 테스트 결과

### 테스트 실행 결과 요약

```
============================= test session starts ==============================
platform darwin -- Python 3.12.10, pytest-8.3.5, pluggy-1.6.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=function
collecting ... collected 9 items

app/tests/test_db.py::TestDatabase::test_database_connection PASSED      [ 11%]
app/tests/test_db.py::TestDatabase::test_food_schema PASSED              [ 22%]
app/tests/test_db.py::TestDatabase::test_sqlite_direct_connection PASSED [ 33%]
app/tests/test_food_api.py::TestFoodAPI::test_create_food PASSED         [ 44%]
app/tests/test_food_api.py::TestFoodAPI::test_get_food PASSED            [ 55%]
app/tests/test_food_api.py::TestFoodAPI::test_get_nonexistent_food PASSED [ 66%]
app/tests/test_food_api.py::TestFoodAPI::test_search_foods PASSED        [ 77%]
app/tests/test_food_api.py::TestFoodAPI::test_update_food PASSED         [ 88%]
app/tests/test_food_api.py::TestFoodAPI::test_delete_food PASSED         [100%]

======================== 9 passed, 3 warnings in 0.05s =========================
```

### 테스트 커버리지

현재 테스트는 다음 영역을 포괄적으로 커버합니다:

1. **데이터베이스 테스트**:
   - 데이터베이스 연결 및 세션 관리
   - 스키마 정의 및 테이블 구조

2. **API 엔드포인트 테스트**:
   - 모든 CRUD 작업 (생성, 조회, 업데이트, 삭제)
   - 검색 기능

### 경고 및 개선사항

테스트 실행 중 다음과 같은 경고가 발생했으며, 이에 대한 개선이 이루어졌습니다:

1. **Pydantic 관련 경고**:
   - 원인: `class Config` 사용이 Pydantic V2에서 더 이상 권장되지 않음
   - 해결: `model_config` 딕셔너리로 대체하여 최신 Pydantic 스타일 적용

2. **pytest-asyncio 관련 경고**:
   - 원인: `event_loop` 픽스처 재정의가 더 이상 권장되지 않음
   - 해결: `loop_scope` 파라미터를 사용하도록 코드 업데이트

