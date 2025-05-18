# 식품 영양성분 데이터베이스 RESTful API 설계 문서

## 1. RESTful API 설계 접근 방식

### 1.1 Richardson 성숙도 모델(Richardson Maturity Model)

본 API는 Leonard Richardson이 제안한 REST 성숙도 모델을 기반으로 설계되었습니다. 이 모델은 REST API 설계의 발전 단계를 네 단계로 정의합니다:

- **Level 0: HTTP 터널링** - HTTP를 단순 전송 프로토콜로만 사용
- **Level 1: 자원(Resources)** - 개별 리소스에 대한 URI 구조 도입
- **Level 2: HTTP 동사(HTTP Verbs)** - HTTP 메서드와 상태 코드 적절히 활용
- **Level 3: 하이퍼미디어 컨트롤(HATEOAS)** - 응답에 다음 가능한 작업에 대한 링크 포함

본 API는 **Level 2**를 구현하여 명확한 리소스 구조와 HTTP 메서드의 의미론적 사용을 통해 REST 원칙을 충실히 따르고 있습니다.

### 1.2 채택한 RESTful 원칙

1. **리소스 기반 설계** - 모든 데이터를 리소스로 모델링
2. **URI를 통한 리소스 식별** - 각 리소스는 고유한 URI로 식별
3. **HTTP 메서드의 의미론적 사용** - 메서드의 본래 의미에 맞게 사용
   - GET: 리소스 조회 (안전한 작업)
   - POST: 새 리소스 생성
   - PUT: 리소스 업데이트
   - DELETE: 리소스 삭제
4. **적절한 HTTP 상태 코드 사용** - 작업 결과를 표준 HTTP 상태 코드로 전달
5. **무상태(Stateless) 통신** - 각 요청은 독립적으로 처리

## 2. API 엔드포인트 설계

### 2.1 기본 URL 구조

```
http://localhost:8000/api/v1
```

### 2.2 리소스 계층 구조

```
/foods                # 식품 컬렉션
/foods/{food_id}      # 특정 식품 리소스
```

### 2.3 HTTP 메서드 사용 가이드

| HTTP 메서드 | 엔드포인트 | 설명 | 상태 코드 |
|------------|-----------|-----|--------|
| GET | /foods | 식품 목록 조회 (검색 및 페이지네이션 지원) | 200 OK |
| GET | /foods/{food_id} | 특정 식품 조회 | 200 OK, 404 Not Found |
| POST | /foods | 새 식품 생성 | 201 Created, 400 Bad Request |
| PUT | /foods/{food_id} | 식품 정보 업데이트 | 200 OK, 404 Not Found |
| DELETE | /foods/{food_id} | 식품 삭제 | 204 No Content, 404 Not Found |

## 3. 요청 및 응답 형식

### 3.1 데이터 형식

요청과 응답 모두 JSON 형식을 사용합니다:

```
Content-Type: application/json
```

### 3.2 페이지네이션 및 필터링

컬렉션 API는 페이지네이션과 필터링을 쿼리 파라미터로 지원합니다:

```
/foods?skip=0&limit=100&food_name=쌀
```

주요 쿼리 파라미터:
- `skip`: 건너뛸 항목 수 (기본값: 0)
- `limit`: 반환할 최대 항목 수 (기본값: 100)
- `food_name`: 식품명 필터 (부분 일치)
- `research_year`: 조사 연도 필터
- `maker_name`: 제조사 필터 (부분 일치)
- `food_code`: 식품 코드 필터 (정확 일치)

### 3.3 상태 코드 사용

본 API는 다음과 같은 HTTP 상태 코드를 사용합니다:

| 상태 코드 | 설명 |
|---------|------|
| 200 OK | 요청 성공 |
| 201 Created | 리소스 생성 성공 |
| 204 No Content | 리소스 삭제 성공 |
| 400 Bad Request | 잘못된 요청 형식 |
| 404 Not Found | 요청한 리소스가 존재하지 않음 |
| 422 Unprocessable Entity | 데이터 유효성 검사 실패 |
| 500 Internal Server Error | 서버 내부 오류 |

## 4. API 사용 예시

### 4.1 식품 목록 조회

**요청:**
```bash
curl --get \
  --data-urlencode "food_name=쌀" \
  --data-urlencode "limit=5" \
  -H "accept: application/json" \
  http://localhost:8000/api/v1/foods/
```

**응답:**
```json
{
  "items": [
    {
      "id": 1,
      "food_cd": "D000001",
      "food_name": "쌀밥",
      "group_name": "곡류",
      "research_year": "2023",
      "maker_name": "식약처",
      "ref_name": "식품영양성분DB",
      "serving_size": 210.0,
      "calorie": 310.0,
      "carbohydrate": 68.9,
      "protein": 5.6,
      "province": 0.5,
      "sugars": 0.0,
      "salt": 2.0,
      "cholesterol": 0.0,
      "saturated_fatty_acids": 0.1,
      "trans_fat": 0.0
    },
    // ... 추가 항목
  ],
  "total": 150,
  "skip": 0,
  "limit": 5
}
```

### 4.2 특정 식품 조회

**요청:**
```bash
curl -X GET "http://localhost:8000/api/v1/foods/1" -H "accept: application/json"
```

**응답:**
```json
{
  "id": 1,
  "food_cd": "D000001",
  "food_name": "쌀밥",
  "group_name": "곡류",
  "research_year": "2023",
  "maker_name": "식약처",
  "ref_name": "식품영양성분DB",
  "serving_size": 210.0,
  "calorie": 310.0,
  "carbohydrate": 68.9,
  "protein": 5.6,
  "province": 0.5,
  "sugars": 0.0,
  "salt": 2.0,
  "cholesterol": 0.0,
  "saturated_fatty_acids": 0.1,
  "trans_fat": 0.0
}
```

### 4.3 새 식품 생성

**요청:**
```bash
curl -X POST "http://localhost:8000/api/v1/foods/" \
  -H "Content-Type: application/json" \
  -d '{
    "food_cd": "D000099",
    "food_name": "새로운 식품",
    "group_name": "가공식품",
    "research_year": "2025",
    "maker_name": "테스트 회사",
    "ref_name": "사용자 입력",
    "serving_size": 100.0,
    "calorie": 250.0,
    "carbohydrate": 30.0,
    "protein": 10.0,
    "province": 5.0,
    "sugars": 2.0,
    "salt": 300.0,
    "cholesterol": 15.0,
    "saturated_fatty_acids": 1.5,
    "trans_fat": 0.0
  }'
```

**응답: (201 Created)**
```json
{
  "id": 7684,
  "food_cd": "D000099",
  "food_name": "새로운 식품",
  "group_name": "가공식품",
  "research_year": "2025",
  "maker_name": "테스트 회사",
  "ref_name": "사용자 입력",
  "serving_size": 100.0,
  "calorie": 250.0,
  "carbohydrate": 30.0,
  "protein": 10.0,
  "province": 5.0,
  "sugars": 2.0,
  "salt": 300.0,
  "cholesterol": 15.0,
  "saturated_fatty_acids": 1.5,
  "trans_fat": 0.0
}
```

### 4.4 식품 정보 업데이트

**요청:**
```bash
curl -X PUT "http://localhost:8000/api/v1/foods/1" \
  -H "Content-Type: application/json" \
  -d '{
    "food_name": "업데이트된 식품명",
    "calorie": 280.0,
    "carbohydrate": 35.0
  }'
```

**응답: (200 OK)**
```json
{
  "id": 1,
  "food_cd": "D000001",
  "food_name": "업데이트된 식품명",
  "group_name": "곡류",
  "research_year": "2023",
  "maker_name": "식약처",
  "ref_name": "식품영양성분DB",
  "serving_size": 210.0,
  "calorie": 280.0,
  "carbohydrate": 35.0,
  "protein": 5.6,
  "province": 0.5,
  "sugars": 0.0,
  "salt": 2.0,
  "cholesterol": 0.0,
  "saturated_fatty_acids": 0.1,
  "trans_fat": 0.0
}
```

### 4.5 식품 삭제

**요청:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/foods/1" -H "accept: application/json"
```

**응답: (204 No Content)**
*응답 본문 없음*

## 5. 향후 발전 방향: Level 3 - HATEOAS 구현

향후 API를 Richardson 성숙도 모델의 Level 3로 발전시키기 위해 다음과 같은 HATEOAS(Hypermedia As The Engine Of Application State) 구현을 고려할 수 있습니다:

```json
{
  "id": 1,
  "food_name": "쌀밥",
  "links": [
    { "rel": "self", "href": "/api/v1/foods/1", "method": "GET" },
    { "rel": "update", "href": "/api/v1/foods/1", "method": "PUT" },
    { "rel": "delete", "href": "/api/v1/foods/1", "method": "DELETE" },
    { "rel": "collection", "href": "/api/v1/foods", "method": "GET" }
  ],
  // ... 기타 속성
}
```

컬렉션 응답에서는 다음과 같이 페이지네이션 링크를 포함할 수 있습니다:

```json
{
  "items": [ ... ],
  "links": [
    { "rel": "self", "href": "/api/v1/foods?skip=0&limit=100", "method": "GET" },
    { "rel": "next", "href": "/api/v1/foods?skip=100&limit=100", "method": "GET" },
    { "rel": "create", "href": "/api/v1/foods", "method": "POST" }
  ],
  "total": 150
}
```

HATEOAS 구현의 이점:
- API가 진화해도 클라이언트 코드 변경 최소화
- 클라이언트가 API를 보다 쉽게 탐색 가능
- 새로운 기능이나 관계를 쉽게 추가 가능

## 6. 참고 문헌

1. Richardson, L., & Ruby, S. (2007). RESTful Web Services. O'Reilly Media.
2. Fowler, M. "Richardson Maturity Model" https://martinfowler.com/articles/richardsonMaturityModel.html
3. "REST in Practice: Hypermedia and Systems Architecture" by Jim Webber, Savas Parastatidis, Ian Robinson
