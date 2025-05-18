# Food Nutrition Database API 테스트 문서

## 테스트 개요

이 문서는 Food Nutrition Database API에 대한 테스트 환경 구성, 테스트 케이스 설명, 그리고 테스트 결과를 상세히 기술합니다. 모든 테스트는 pytest 프레임워크를 사용하여 비동기 테스트 환경에서 수행되었습니다.

## 테스트 환경

- **Python 버전**: 3.12.10
- **운영체제**: macOS (darwin)
- **테스트 프레임워크**: pytest 8.3.5, pytest-asyncio 0.26.0
- **데이터베이스**: SQLite (in-memory, 테스트용)
- **테스트 설정**: 
  - asyncio_mode = strict
  - 각 테스트 함수마다 독립적인 데이터베이스 환경 제공

## 테스트 구조

테스트는 API 엔드포인트에 중점을 둔 종합적인 테스트로 구성되어 있으며, 각 테스트 케이스는 데이터베이스 스키마 검증과 API 기능 검증을 동시에 수행합니다.

### 테스트 파일 구조

```
app/tests/
├── test_docs.md           # 테스트 문서
└── test_food_api.py       # API 엔드포인트 통합 테스트
```

## 테스트 픽스처

테스트에 사용된 주요 픽스처는 다음과 같습니다:

### 1. create_test_tables

각 테스트 함수마다 새로운 테스트 테이블 환경을 제공하는 픽스처입니다.

```python
@pytest_asyncio.fixture(scope="function")
async def create_test_tables() -> AsyncGenerator[None, None]:
    """테스트 테이블 생성 - 함수별로 새로운 테스트 DB 환경 제공"""
    # 테이블 삭제 후 재생성
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # 각 테스트 완료 후 테이블 데이터 정리
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

### 2. db_session

비동기 테스트 데이터베이스 세션을 제공하는 픽스처입니다.

```python
@pytest_asyncio.fixture
async def db_session(create_test_tables) -> AsyncGenerator[AsyncSession, None]:
    """테스트용 데이터베이스 세션 제공"""
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()
```

### 3. async_client

비동기 HTTP 테스트 클라이언트를 제공하는 픽스처입니다. FastAPI 애플리케이션에 대한 요청을 시뮤레이션하는 데 사용됩니다.

```python
@pytest_asyncio.fixture
async def async_client(create_test_tables) -> AsyncGenerator[AsyncClient, None]:
    """비동기 HTTP 테스트 클라이언트 제공"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        yield client
```

### 4. sample_food

테스트에 사용할 샘플 식품 데이터를 제공하는 픽스처입니다. 테스트 함수마다 고유한 food_cd를 생성합니다.

```python
@pytest.fixture
def sample_food(request) -> dict[str, str | float]:
    """테스트용 샘플 식품 데이터 - 테스트 함수마다 고유한 food_cd 제공"""
    # 테스트 함수명을 기반으로 고유 식별자 생성
    test_name = request.node.name
    unique_id = abs(hash(test_name)) % 10000000
    food_cd = f"D{unique_id:07d}"
    
    return {
        "food_cd": food_cd,
        "food_name": "테스트 식품",
        "group_name": "과자",
        "research_year": "2023",
        "maker_name": "테스트 회사",
        "ref_name": "테스트 DB",
        "serving_size": 100.0,
        "calorie": 300.0,
        "carbohydrate": 50.0,
        "protein": 5.0,
        "province": 10.0,
        "sugars": 20.0,
        "salt": 100.0,
        "cholesterol": 0.0,
        "saturated_fatty_acids": 1.0,
        "trans_fat": 0.0
    }
```

## API 테스트 케이스

`test_food_api.py` 파일에는 다음과 같은 테스트 케이스가 구현되어 있습니다. 각 테스트는 실제 API 엔드포인트를 호출하여 기능과 응답을 검증합니다.

### TestFoodAPI 클래스

API 엔드포인트에 대한 종합적인 테스트를 포함한 클래스입니다. 각 테스트 함수는 테스트 실행 전에 새로운 데이터베이스 환경을 구성합니다.

## API 엔드포인트 테스트 케이스

`TestFoodAPI` 클래스에는 다음 테스트 메서드들이 있습니다. 각 테스트는 독립적인 데이터베이스 환경에서 실행됩니다.

### 1. test_create_food

식품 생성 API 엔드포인트(POST /foods/)를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_create_food(self, async_client: AsyncClient, sample_food: dict[str, str | float]):
    """POST /foods/ - 식품 생성 테스트"""
    response = await async_client.post("/foods/", json=sample_food)
    
    # 상태 코드 및 응답 검증
    assert response.status_code == 201
    data = response.json()
    assert data["food_cd"] == sample_food["food_cd"]
    assert data["food_name"] == sample_food["food_name"]
    assert "id" in data  # ID가 생성되었는지 확인
    
    return data  # 다른 테스트에서 참조할 수 있도록 반환
```

### 2. test_get_food

식품 조회 API 엔드포인트(GET /foods/{food_id})를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_get_food(self, async_client: AsyncClient, sample_food: dict[str, str | float]):
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

존재하지 않는 식품 ID에 대한 요청(GET /foods/999999999)을 테스트합니다.

```python
@pytest.mark.asyncio
async def test_get_nonexistent_food(self, async_client: AsyncClient):
    """GET /foods/{food_id} - 존재하지 않는 식품 조회 테스트"""
    # 아주 큰 ID값을 사용하여 확실히 존재하지 않는 식품 조회
    response = await async_client.get("/foods/999999999")
    assert response.status_code == 404
```

### 4. test_search_foods

식품 검색 API 엔드포인트(GET /foods/?food_name=...)를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_search_foods(
    self,
    async_client: AsyncClient,
    sample_food: dict[str, str | float]
) -> None:
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

식품 정보 업데이트 API 엔드포인트(PUT /foods/{food_id})를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_update_food(
    self,
    async_client: AsyncClient,
    sample_food: dict[str, str | float]
) -> None:
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

식품 삭제 API 엔드포인트(DELETE /foods/{food_id})를 테스트합니다.

```python
@pytest.mark.asyncio
async def test_delete_food(
    self,
    async_client: AsyncClient,
    sample_food: dict[str, str | float]
) -> None:
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

테스트를 실행하는 데는 두 가지 방법이 있습니다.

### 1. pytest 링을 통한 직접 실행

```bash
# 가상환경 활성화
source .venv/bin/activate

# pytest 직접 실행
pytest app/tests/test_food_api.py -v
```

### 2. run_tests.py 스크립트 사용

```bash
# run_tests.py 스크립트 실행
python run_tests.py
```

이 스크립트는 테스트를 실행하고 결과를 `etc/test_result.txt` 파일에 저장합니다.

## 테스트 결과

### 테스트 실행 결과 예시

```
============================= test session starts ==============================
platform darwin -- Python 3.12.10, pytest-8.3.5, pluggy-1.6.0 -- /usr/local/bin/python3.12.10
asyncio: mode=Mode.STRICT
collecting ... collected 6 items

app/tests/test_food_api.py::TestFoodAPI::test_create_food PASSED         [ 16%]
app/tests/test_food_api.py::TestFoodAPI::test_get_food PASSED            [ 33%]
app/tests/test_food_api.py::TestFoodAPI::test_get_nonexistent_food PASSED [ 50%]
app/tests/test_food_api.py::TestFoodAPI::test_search_foods PASSED        [ 66%]
app/tests/test_food_api.py::TestFoodAPI::test_update_food PASSED         [ 83%]
app/tests/test_food_api.py::TestFoodAPI::test_delete_food PASSED         [100%]

======================== 6 passed in 1.82s =========================
```

### 테스트 커버리지

현재 테스트는 다음 영역을 포괄적으로 커버합니다:

1. **API 엔드포인트 기능테스트**
   - 모든 CRUD 작업(생성, 조회, 업데이트, 삭제)
   - 검색 기능 및 필터링
   - 오류 상황(404 Not Found 등)

2. **간접적 데이터베이스 테스트**
   - 픽스처 레벨에서 데이터베이스 테이블 생성/삭제 처리
   - 독립적인 테스트 환경 제공

### 개선사항

현재 시스템은 다음과 같은 개선사항을 적용하였습니다:

1. **테스트 데이터베이스 고립**
   - 실제 데이터베이스가 아닌 바로 생성된 테스트 용 DB 사용
   - 테스트 함수마다 문제 없이 새로운 환경에서 테스트 실행

2. **테스트 데이터 동적 생성**
   - 해시 기반의 고유 food_cd 사용으로 테스트 간 충돌 방지
   - 테스트 안정성 향상

3. **최신 Python 기능 사용**
   - Python 3.12 타입 어노테이션 활용 (Union 대신 | 기호 사용 등)
   - 클린한 비동기 테스트 코드 구성

