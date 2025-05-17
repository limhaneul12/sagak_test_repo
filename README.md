# Food Nutrition Database API

## 프로젝트 개요

본 프로젝트는 식품영양성분 데이터베이스를 기반으로 한 RESTful API 구현입니다. 약 9만여 건의 식품영양성분 정보를 DB화하여 사용자가 쉽게 조회하고 관리할 수 있는 API를 제공합니다.

### 핵심 기능

- 식품 정보 CRUD 작업 (생성, 조회, 업데이트, 삭제)
- 다양한 조건을 통한 식품 검색 (이름, 제조사, 연도, 식품코드 등)
- 비동기 처리를 통한 고성능 API
- 종합적인 데이터 분석 및 통계 제공

### 기술 스택

- **언어**: Python 3.12+
- **웹 프레임워크**: FastAPI
- **ORM**: SQLAlchemy 2.0+
- **데이터베이스**: SQLite (data/food_nutrition.db)
- **테스트 프레임워크**: pytest
- **패키지 관리**: Poetry
- **도커라이즈**: Docker 및 docker-compose

## 구현 내용

### 코드 구조

프로젝트는 다음과 같은 계층 구조로 설계되었습니다:

```
app/
├── api/            # API 엔드포인트 정의
├── core/           # 핵심 설정 및 유틸리티
├── db/             # 데이터베이스 연결 및 설정
├── models/         # SQLAlchemy 데이터 모델
├── schemas/        # Pydantic 데이터 검증 스키마
├── services/       # 비즈니스 로직 서비스 레이어
└── tests/          # 자동화 테스트
```

### 주요 개선사항

1. **의존성 주입 패턴 적용**
   - `app/services/dependencies.py` 파일을 통해 FoodService의 의존성 주입
   - API 엔드포인트에서 서비스 레이어 직접 생성 대신 DI 사용

2. **SQLAlchemy 최신 스타일 적용**
   - `declarative_base()` 대신 `DeclarativeBase` 클래스 상속 방식 사용
   - SQLAlchemy 2.0 표준에 맞춘 비동기 세션 관리

3. **파이썬 3.12 타입 힌트 현대화**
   - 최신 Python 타입 힌트 문법 사용 (예: `list[str]` 대신 `List[str]`)
   - `TypeAlias`를 활용한 명확한 타입 정의
   - Union 타입에 파이프 연산자 사용 (예: `str | None`)

4. **비동기 프로그래밍 적용**
   - FastAPI와 SQLAlchemy 비동기 세션을 통한 효율적인 비동기 처리
   - 동시성 처리를 통한 API 성능 향상

## 테스트 결과

### 테스트 케이스 요약

총 9개의 테스트 케이스가 구현되어 있으며, 모두 성공적으로 통과했습니다:

1. **데이터베이스 테스트 (3개)**
   - 데이터베이스 연결 테스트
   - Food 모델 스키마 테스트
   - SQLite 직접 연결 테스트

2. **API 엔드포인트 테스트 (6개)**
   - 식품 생성 테스트 (POST)
   - 식품 조회 테스트 (GET)
   - 존재하지 않는 식품 조회 테스트
   - 식품 검색 테스트
   - 식품 정보 업데이트 테스트 (PUT)
   - 식품 삭제 테스트 (DELETE)

### 테스트 환경

- Python 버전: 3.12.10
- 운영체제: darwin (macOS)
- 데이터베이스: 실제 DB 사용 (data/food_nutrition.db)

## 실행 방법

### Poetry 기준 실행

1. **프로젝트 클론**

```bash
git clone <repository-url>
cd sagak_test_repo
```

2. **Poetry 환경 설정**

```bash
poetry install
poetry shell
```

3. **데이터베이스 초기화 및 데이터 삽입**

```bash
python import_data.py
```

이 명령어는 다음을 수행합니다:
- Excel 파일(통합 식품영양성분DB_음식_20230715.xlsx)에서 데이터 로드
- 데이터 정제 및 컬럼 매핑
- 처리된 데이터를 CSV 파일로 저장 (data/processed_food_data.csv)
- SQL 삽입 파일 생성 (data/insert_food_data.sql)
- SQLite 데이터베이스에 데이터 삽입 (data/food_nutrition.db)

4. **애플리케이션 실행**

```bash
python main.py
```

5. **테스트 실행**

```bash
python run_tests.py
```

### Docker 기준 실행

```bash
docker-compose up -d
```

## 저장소 파일 구조

```
sagak_test_repo/
├── app/               # 애플리케이션 코드
│   ├── api/          # API 엔드포인트 로직
│   ├── core/         # 핵심 설정 및 환경변수
│   ├── db/           # 데이터베이스 연결 및 세션
│   ├── models/       # SQLAlchemy 데이터 모델
│   ├── schemas/      # Pydantic 스키마
│   ├── services/     # 비즈니스 로직
│   └── tests/        # 테스트 코드
├── data/              # 데이터 관련 파일
│   ├── analysis_report/ # 데이터 분석 결과
│   ├── food_nutrition.db # SQLite 데이터베이스
│   ├── insert_food_data.sql # SQL 삽입 파일
│   └── processed_food_data.csv # 처리된 CSV 데이터
├── etc/               # 부가 문서
├── api_docs.md       # API 사용 가이드
├── import_data.py    # 데이터 삽입 스크립트
├── main.py           # 애플리케이션 엔트리포인트
├── test_docs.md      # 테스트 문서
├── pyproject.toml    # Poetry 설정 파일
├── pytest.ini        # pytest 설정
├── run_tests.py      # 테스트 실행 스크립트
├── Dockerfile        # Docker 이미지 설정
├── docker-compose.yml # Docker 구성 파일
└── README.md         # 프로젝트 설명
```

## 데이터 분석 결과

### 데이터 개요

- 총 7,683개의 식품 데이터 분석
- 100개의 컬럼을 17개의 핵심 필드로 매핑

### 주요 발견사항

- 식품 영양성분 데이터는 여러 출처에서 제공됨
- 식품 대분류 및 상세분류를 통한 체계적 구조화
- 다양한 영양 정보 제공 (열량, 단백질, 탄수화물, 지방 등)

### API 설계 접근법

- RESTful API 설계 원칙 준수
- 리차드슨 성숙도 모델 (Richardson Maturity Model) 적용
- 적절한 HTTP 상태 코드 사용
- 파라미터 검증 및 에러 처리

## API 문서

애플리케이션 실행 후 다음 URL에서 Swagger 문서 확인 가능:

```
http://localhost:8000/docs
```