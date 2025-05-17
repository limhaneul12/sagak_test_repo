import pandas as pd
from pathlib import Path
import numpy as np
import sqlite3
from typing import Optional


def process_food_data(file_path: Path, output_csv_path: Path | str = "processed_food_data.csv"):
    """
    Excel 파일의 식품 영양 성분 데이터를 읽어서 정제하고 CSV 파일로 저장합니다.
    
    Args:
        file_path: Excel 파일 경로 (Path 객체)
        output_csv_path: 출력할 CSV 파일 경로 (Path 객체 또는 문자열)
    """
    # 엑셀 파일 읽기
    print(f"Loading data from {file_path}...")
    try:
        df = pd.read_excel(file_path)
        print(f"Successfully loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
        print("First few column names:", df.columns.tolist()[:10])  # 컬럼명 확인용 출력
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
    
    # 십품 영양성분 데이터 분석 결과에 따른 열 이름 매핑
    column_mapping = {
        "NO": "id",
        "식품코드": "food_cd",
        "식품대분류": "group_name",
        "식품명": "food_name",
        "연도": "research_year",
        "지역 / 제조사": "maker_name",
        "성분표출처": "ref_name",
        "1회제공량": "serving_size",
        "에너지(㎉)": "calorie",
        "탄수화물(g)": "carbohydrate",
        "단백질(g)": "protein",
        "지방(g)": "province",
        "총당류(g)": "sugars",
        "나트륨(㎎)": "salt",
        "콜레스테롤(㎎)": "cholesterol",
        "총 포화 지방산(g)": "saturated_fatty_acids",
        "트랜스 지방산(g)": "trans_fat"
    }
    
    # 데이터 프레임 열 이름 변경 및 카피 생성 후 작업
    print("Mapping columns from original Excel file...")
    
    # 컬럼 매핑 전 원본 데이터 카피
    df_copy = df.copy()
    
    # 매핑된 컬럼 확인
    renamed_columns = {}
    for korean_name, english_name in column_mapping.items():
        if korean_name in df.columns:
            df_copy = df_copy.rename(columns={korean_name: english_name})
            renamed_columns[korean_name] = english_name
            print(f"  - Mapped: '{korean_name}' -> '{english_name}'")
    
    # 매핑된 컬럼 수 확인
    print(f"Successfully mapped {len(renamed_columns)} columns out of {len(column_mapping)} defined mappings")
    
    # 매핑되지 않은 필수 컬럼 확인
    required_columns = ['id', 'food_cd', 'group_name', 'food_name', 'research_year', 'maker_name', 'ref_name', 
                     'serving_size', 'calorie', 'carbohydrate', 'protein', 'province', 'sugars', 
                     'salt', 'cholesterol', 'saturated_fatty_acids', 'trans_fat']
    
    missing_columns = [col for col in required_columns if col not in df_copy.columns]
    if missing_columns:
        print(f"Missing {len(missing_columns)} required columns: {', '.join(missing_columns)}")
        for col in missing_columns:
            print(f"  - Adding empty column: {col}")
            df_copy[col] = np.nan
    
    # 데이터 정제 실행
    print("Cleaning and processing data...")
    
    # '-' 값 NaN으로 변환 (수수로 표시된 없음 값)
    for col in df_copy.columns:
        if df_copy[col].dtype == 'object':
            df_copy[col] = df_copy[col].replace('-', np.nan)
    
    # 데이터 타입 변환
    numeric_columns = ['serving_size', 'calorie', 'carbohydrate', 'protein', 'province', 
                     'sugars', 'salt', 'cholesterol', 'saturated_fatty_acids', 'trans_fat']
    
    string_columns = ['food_cd', 'group_name', 'food_name', 'maker_name', 'ref_name']
    
    # 연도는 문자열로 처리 (YYYY 형식 유지)
    if 'research_year' in df_copy.columns:
        df_copy['research_year'] = df_copy['research_year'].astype(str)
    
    # 수치형 컬럼 변환 및 결측치 0으로 처리
    for col in numeric_columns:
        if col in df_copy.columns:
            df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce').fillna(0)
    
    # 문자열 컬럼 결측치 빈 문자열로 처리
    for col in string_columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].fillna('')
    
    # 최종 데이터 프레임에 필요한 열만 선택 (요청인자.md의 출력 항목 순서에 맞게)
    final_columns = ['id', 'food_cd', 'group_name', 'food_name', 'research_year', 'maker_name', 'ref_name', 
                    'serving_size', 'calorie', 'carbohydrate', 'protein', 'province', 'sugars', 
                    'salt', 'cholesterol', 'saturated_fatty_acids', 'trans_fat']
    
    # 순서대로 컬럼 정렬
    for col in final_columns:
        if col not in df_copy.columns:
            print(f"Warning: Column '{col}' is missing from the final dataset and will contain empty values.")

    # 컬럼 선택 및 정렬
    final_df = pd.DataFrame()
    for col in final_columns:
        if col in df_copy.columns:
            final_df[col] = df_copy[col]
        else:
            # 없는 컬럼은 빈 값으로 추가
            final_df[col] = np.nan if col in numeric_columns else ""
    
    # ID 컬럼 처리 - 'id' 컬럼이 매핑되지 않은 경우 새로 생성
    if 'NO' not in renamed_columns.keys():
        print("Creating sequential ID column...")
        final_df['id'] = range(1, len(final_df) + 1)
    
    # CSV 파일로 저장
    print("Saving processed data to CSV file...")
    output_path = Path(output_csv_path)
    if output_path.parent.name:  # 부모 디렉토리가 있는지 확인
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    final_df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"✓ Data processed and saved to {output_csv_path}")
    print(f"✓ Total records: {len(final_df)}")
    
    # 데이터 요약 정보 출력
    print("\n=== Data Summary ===")
    print(f"Columns: {', '.join(final_columns)}")
    
    # 각 컬럼 데이터 타입 출력
    print("\nColumn Data Types:")
    for col in final_columns:
        print(f"  - {col}: {final_df[col].dtype}")
    
    print("\n=== Sample Data (first 5 rows) ===")
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', 120)  # 화면 너비 조정
    print(final_df.head().to_string())
    
    # SQL 삽입용 SQL 파일 생성
    print("\nGenerating SQL insert file...")
    create_sql_insert_file(final_df, output_path.parent / "insert_food_data.sql")
    
    return final_df


def create_sql_insert_file(df: pd.DataFrame, sql_file_path: Path):
    """
    DataFrame의 데이터로 SQL INSERT 문을 생성하여 파일로 저장합니다.
    SQL Injection을 방지하기 위해 적절히 이스케이프된 실제 값을 사용합니다.
    
    Args:
        df: 데이터프레임
        sql_file_path: SQL 파일 저장 경로
    """
    print(f"Creating SQL insert file at {sql_file_path}...")
    
    # 테이블 생성 SQL
    create_table_sql = """
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
        """
    
    # INSERT 문 생성 - SQL Injection 방지를 위한 적절한 이스케이프 처리
    with open(sql_file_path, 'w', encoding='utf-8') as f:
        f.write(create_table_sql)
        
        # 트랜잭션 시작
        f.write("BEGIN TRANSACTION;\n\n")
        
        # 컬럼 목록 한 번만 정의
        columns = ", ".join(df.columns)
        
        # 배치 단위로 처리 (SQLite의 기본 제한은 999개 변수)
        batch_size = 500  # 더 큰 배치 크기 사용
        total_rows = len(df)
        rows_processed = 0
        
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:min(i+batch_size, total_rows)]
            batch_count = len(batch_df)
            
            # 배치 정보 추가 (VALUES 키워드 전에)
            f.write(f"\n-- Batch {i//batch_size + 1}: Inserting {batch_count} records\n")
            
            # 각 배치의 첫 번째 레코드에만 INSERT 문 추가
            if i == 0:
                f.write(f"INSERT INTO foods ({columns}) VALUES\n")
            
            # 배치 내 각 행 처리
            for idx, (_, row) in enumerate(batch_df.iterrows()):
                # 각 값을 타입에 맞게 적절히 이스케이프 처리
                safe_values = []
                for col, val in zip(df.columns, row):
                    if pd.isna(val):  # NULL 처리
                        safe_values.append("NULL")
                    elif col in ['id', 'serving_size'] or col.endswith(('calorie', 'carbohydrate', 'protein', 'province', 
                                                                'sugars', 'salt', 'cholesterol', 
                                                                'saturated_fatty_acids', 'trans_fat')):
                        # 숫자형 데이터
                        safe_values.append(str(val))
                    else:
                        # 문자열 데이터 - 작은따옴표 이스케이프
                        escaped_val = str(val).replace("'", "''")
                        safe_values.append(f"'{escaped_val}'")
                
                # VALUES 부분만 작성
                values_str = ", ".join(safe_values)
                rows_processed += 1
                
                # 마지막 행이 아니면 콤마 추가, 마지막 행이면 세미콜론 추가
                if rows_processed < total_rows:
                    f.write(f"({values_str}),\n")
                else:
                    f.write(f"({values_str});\n")
                
            f.write("\n")  # 배치 끝나면 줄바꿈 추가
            
            f.write("\n")
        
        # 트랜잭션 커밋
        f.write("COMMIT;\n")
    
    print(f"SQL insert file created successfully at {sql_file_path}")


def save_to_sqlite(df: pd.DataFrame, db_path: Path | str) -> bool:
    """
    DataFrame의 데이터를 SQLite 데이터베이스에 저장합니다.
    SQL Injection 방지를 위해 파라미터화된 쿼리를 사용합니다.
    
    Args:
        df: 데이터프레임
        db_path: SQLite 데이터베이스 파일 경로
        
    Returns:
        bool: 저장 성공 여부
    """
    conn = None
    try:
        print(f"Saving data to SQLite database at {db_path}...")
        # SQLite 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 생성
        create_table_sql = """
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
        """
        cursor.execute(create_table_sql)
        
        # 기존 데이터 삭제 (옵션)
        cursor.execute("DELETE FROM foods")
        
        # 변경사항 먼저 저장
        conn.commit()
        
        # INSERT 쿼리 준비 및 실행
        columns = ", ".join(df.columns)
        placeholders = ", ".join(["?" for _ in range(len(df.columns))])
        insert_sql = f"INSERT INTO foods ({columns}) VALUES ({placeholders})"
        
        # 파라미터 바인딩을 사용한 데이터 삽입 (일괄 작업)
        batch_size = 500  # SQLite 권장 일괄 크기
        total_rows = len(df)
        
        for i in range(0, total_rows, batch_size):
            # 트랜잭션 시작
            conn.execute("BEGIN TRANSACTION")
            
            # 배치 처리
            batch_end = min(i + batch_size, total_rows)
            print(f"Processing records {i+1} to {batch_end}...")
            
            batch_data = [tuple(row) for row in df.iloc[i:batch_end].values]
            cursor.executemany(insert_sql, batch_data)
            
            # 트랜잭션 커밋
            conn.commit()
        
        # 연결 종료
        conn.close()
        conn = None
        
        print(f"✓ Successfully inserted {total_rows} records into SQLite database")
        return True
        
    except Exception as e:
        print(f"Error saving to SQLite database: {e}")
        # 연결이 있으면 롤백
        if conn:
            try:
                conn.rollback()
            except sqlite3.Error as rollback_error:
                print(f"Error during rollback: {rollback_error}")
            finally:
                conn.close()
        return False


def load_from_csv(csv_path: Path | str) -> pd.DataFrame | None:
    """
    CSV 파일에서 데이터를 읽어 DataFrame으로 반환합니다.
    
    Args:
        csv_path: CSV 파일 경로
        
    Returns:
        DataFrame 또는 None (오류 발생 시)
    """
    try:
        print(f"Loading data from CSV file {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"✓ Successfully loaded {len(df)} records from CSV")
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None


def main():
    # 파일 경로 설정
    data_dir = Path(__file__).parent / "data"
    import_path = data_dir / "통합 식품영양성분DB_음식_20230715.xlsx"
    csv_path = data_dir / "processed_food_data.csv"
    db_path = data_dir / "food_nutrition.db"
    sql_path = data_dir / "insert_food_data.sql"
    
    # 엑셀 파일 처리 및 CSV 생성
    if not csv_path.exists():
        print("Processing Excel file...")
        process_food_data(import_path, csv_path)
    
    # CSV 파일 로드
    df = load_from_csv(csv_path)
    if df is None:
        print("Failed to load CSV data. Exiting.")
        return
    
    # SQL 파일 생성
    create_sql_insert_file(df, sql_path)
    
    # SQLite DB에 저장
    save_to_sqlite(df, db_path)
    
    print("\n데이터 처리가 완료되었습니다.")
    print(f"1. CSV 파일: {csv_path}")
    print(f"2. SQL 파일: {sql_path}")
    print(f"3. SQLite DB: {db_path}")


if __name__ == "__main__":
    main()
