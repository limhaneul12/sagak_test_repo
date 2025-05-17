# 식품 영양 성분 데이터베이스 API

본 프로젝트는 식품 영양 성분 DB를 FastAPI를 사용하여 RESTful API로 제공합니다. 국민이 자주 섭취하는 음식과 유통되는 가공 식품 등에 대한 영양 성분 정보를 검색할 수 있습니다.

## 기능

- 식품 영양 성분 데이터 검색 API
- 식품 데이터 CRUD API
- Excel 데이터를 DB로 가져오는 도구
- Docker를 통한 배포

## 기술 스택

- Python 3.12.10
- FastAPI
- SQLAlchemy
- SQLite
- Pandas (데이터 처리)
- Docker & Docker Compose

## 프로젝트 구조

```
.
├── app/                    # 메인 애플리케이션 폴더
│   ├── api/                # API 엔드포인트 정의
│   │   └── endpoints/      # 각 리소스별 엔드포인트
│   ├── core/               # 설정 및 유틸리티
│   ├── db/                 # 데이터베이스 설정
│   ├── models/             # SQLAlchemy 모델
│   ├── schemas/            # Pydantic 모델
│   ├── services/           # 비즈니스 로직
│   └── main.py             # FastAPI 애플리케이션 인스턴스
├── import_data.py          # 데이터 가져오기 스크립트
├── requirements.txt        # 의존성
├── Dockerfile              # Docker 이미지 정의
└── docker-compose.yml      # Docker Compose 설정
```

## 설치 및 실행

### 로컬 개발 환경

1. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

2. 데이터베이스 초기화 및 데이터 가져오기
   ```bash
   python import_data.py
   ```

3. API 서버 실행
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker로 실행

```bash
# 애플리케이션 빌드 및 실행
docker-compose up -d
```

## API 문서

서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 검색 API

```
GET /api/v1/foods/
```

**요청 인자:**

- `food_name`: 식품이름 (선택)
- `research_year`: 연도(YYYY) (선택)
- `maker_name`: 지역/제조사 (선택)
- `food_code`: 식품코드 (선택)
- `skip`: 건너뛸 결과 수 (기본값: 0)
- `limit`: 최대 결과 수 (기본값: 100)

### CRUD API

```
POST /api/v1/foods/           # 식품 생성
GET /api/v1/foods/{food_id}   # 식품 조회
PUT /api/v1/foods/{food_id}   # 식품 수정
DELETE /api/v1/foods/{food_id} # 식품 삭제
```