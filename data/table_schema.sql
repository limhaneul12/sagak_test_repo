-- 테이블 스키마 정의
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY,
    food_cd TEXT,
    group_name TEXT,
    food_name TEXT,
    research_year TEXT,
    maker_name TEXT,
    ref_name TEXT,
    serving_size REAL,
    calorie REAL,
    carbohydrate REAL,
    protein REAL,
    province REAL, 
    sugars REAL,
    salt REAL,
    cholesterol REAL,
    saturated_fatty_acids REAL,
    trans_fat REAL
);

-- 메타 데이터 테이블
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);