FROM python:3.12-slim-bookworm

# 필수 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 -

# 비루트 사용자 생성
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

# Poetry 설정 파일만 먼저 복사
COPY --chown=appuser:appuser pyproject.toml poetry.lock* ./

# Poetry로 의존성 설치 (개발 의존성 제외, 현재 프로젝트는 설치하지 않음)
RUN /root/.local/bin/poetry config virtualenvs.create false \
    && /root/.local/bin/poetry install --only main --no-root --no-interaction --no-ansi

# 애플리케이션 코드 복사
COPY --chown=appuser:appuser . .

# 권한 설정
RUN chown -R appuser:appuser /app

# 비루트 사용자로 전환
USER appuser

# 데이터베이스 초기화 및 서버 실행
CMD ["sh", "-c", "python import_data.py && uvicorn main:app --host 0.0.0.0 --port 8000"]