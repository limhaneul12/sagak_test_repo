# Food Nutrition Database API 사용 가이드

## API 개요

이 문서는 식품영양성분 데이터베이스 API의 사용법과 각 엔드포인트에 대한 상세 설명을 제공합니다. 이 API는 RESTful 원칙을 준수하며 비동기 처리를 통한 고성능 응답을 제공합니다.

## 기본 URL

```
http://localhost:8000/api/v1
```

## 인증

현재 버전에서는 별도의 인증이 필요하지 않습니다.

## 엔드포인트 목록

### 1. 식품 목록 조회

**요청**
```http
GET /foods/
```

**쿼리 파라미터**
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| skip | integer | 아니오 | 건너뛸 레코드 수 (기본값: 0) |
| limit | integer | 아니오 | 반환할 최대 레코드 수 (기본값: 100) |
| food_name | string | 아니오 | 식품 이름으로 필터링 (부분일치) |
| research_year | string | 아니오 | 조사 연도로 필터링 (YYYY) |
| maker_name | string | 아니오 | 제조사/지역으로 필터링 (부분일치) |
| food_cd | string | 아니오 | 식품 코드로 필터링 (정확일치) |

**응답**
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
    // ... 추가 아이템
  ],
  "total": 150,
  "skip": 0,
  "limit": 100
}
```

**상태 코드**
- `200 OK`: 성공
- `400 Bad Request`: 잘못된 요청 파라미터

### 2. 특정 식품 조회

**요청**
```http
GET /foods/{food_id}
```

**URL 파라미터**
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| food_id | integer | 식품 ID |

**응답**
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

**상태 코드**
- `200 OK`: 성공
- `404 Not Found`: 해당 ID의 식품을 찾을 수 없음

### 3. 식품 생성

**요청**
```http
POST /foods/
```

**요청 본문**
```json
{
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

**응답**
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

**상태 코드**
- `201 Created`: 식품 생성 성공
- `400 Bad Request`: 잘못된 요청 데이터
- `409 Conflict`: 이미 존재하는 식품 코드

### 4. 식품 정보 업데이트

**요청**
```http
PUT /foods/{food_id}
```

**URL 파라미터**
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| food_id | integer | 식품 ID |

**요청 본문**
```json
{
  "food_name": "업데이트된 식품명",
  "calorie": 280.0,
  "carbohydrate": 35.0
}
```

**응답**
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

**상태 코드**
- `200 OK`: 업데이트 성공
- `400 Bad Request`: 잘못된 요청 데이터
- `404 Not Found`: 해당 ID의 식품을 찾을 수 없음

### 5. 식품 삭제

**요청**
```http
DELETE /foods/{food_id}
```

**URL 파라미터**
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| food_id | integer | 식품 ID |

**응답**
본문 없음

**상태 코드**
- `204 No Content`: 삭제 성공
- `404 Not Found`: 해당 ID의 식품을 찾을 수 없음

## 데이터 스키마

### Food 스키마

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | integer | 자동생성 | 식품 ID (기본키) |
| food_cd | string | 예 | 식품 코드 |
| food_name | string | 예 | 식품 이름 |
| group_name | string | 예 | 식품군 |
| research_year | string | 예 | 조사 연도 |
| maker_name | string | 예 | 제조사/지역 |
| ref_name | string | 예 | 자료 출처 |
| serving_size | float | 예 | 1회 제공량 (g) |
| calorie | float | 예 | 열량 (kcal) |
| carbohydrate | float | 예 | 탄수화물 함량 (g) |
| protein | float | 예 | 단백질 함량 (g) |
| province | float | 예 | 지방 함량 (g) |
| sugars | float | 아니오 | 총당류 함량 (g) |
| salt | float | 아니오 | 나트륨 함량 (mg) |
| cholesterol | float | 아니오 | 콜레스테롤 함량 (mg) |
| saturated_fatty_acids | float | 아니오 | 포화지방산 함량 (g) |
| trans_fat | float | 아니오 | 트랜스지방 함량 (g) |

## 에러 처리

API는 다음과 같은 형식의 에러 응답을 반환합니다:

```json
{
  "detail": "에러 메시지"
}
```

**공통 에러 코드**
- `400 Bad Request`: 잘못된 요청 데이터
- `404 Not Found`: 요청한 리소스를 찾을 수 없음
- `422 Unprocessable Entity`: 데이터 검증 오류
- `500 Internal Server Error`: 서버 내부 오류

## 사용 예시

### cURL을 이용한 식품 목록 조회
```bash
curl --get \
  --data-urlencode "food_name=쌀" \
  --data-urlencode "limit=5" \
  -H "accept: application/json" \
  http://localhost:8000/api/v1/foods/
```

### Python requests 라이브러리를 이용한 식품 생성
```python
import requests
import json

url = "http://localhost:8000/api/v1/foods/"
payload = {
  "food_cd": "D000100",
  "food_name": "테스트 식품",
  "group_name": "테스트",
  "research_year": "2025",
  "maker_name": "API 테스트",
  "ref_name": "API 예제",
  "serving_size": 100.0,
  "calorie": 200.0,
  "carbohydrate": 25.0,
  "protein": 10.0,
  "province": 5.0,
  "sugars": 2.0,
  "salt": 300.0,
  "cholesterol": 15.0,
  "saturated_fatty_acids": 1.5,
  "trans_fat": 0.0
}
headers = {
  'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.status_code)
print(response.json())
```

## 성능 고려사항

- **페이지네이션**: 대량의 데이터 요청 시 `skip`과 `limit` 파라미터를 활용하여 페이지네이션 구현
- **필터링**: 필요한 데이터만 효율적으로 검색하기 위해 쿼리 파라미터 활용
- **비동기 처리**: API는 비동기 방식으로 구현되어 동시에 많은 요청을 처리할 수 있음

## 테스트 결과

### 테스트 요약

```
✅ 테스트 상태: 성공
📊 테스트 개수: 6개 테스트 전체 통과
⏱️ 실행 시간: 0.32초
```

### 테스트 항목

| 테스트 | 설명 | 결과 |
|--------|------|------|
| test_create_food | 식품 생성 API 테스트 | ✅ 통과 |
| test_get_food | 특정 식품 조회 API 테스트 | ✅ 통과 |
| test_get_nonexistent_food | 존재하지 않는 식품 조회 테스트 | ✅ 통과 |
| test_search_foods | 식품 검색 API 테스트 | ✅ 통과 |
| test_update_food | 식품 정보 업데이트 API 테스트 | ✅ 통과 |
| test_delete_food | 식품 삭제 API 테스트 | ✅ 통과 |
