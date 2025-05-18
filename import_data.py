import pandas as pd
import sqlite3
import hashlib
import logging
import re
from pathlib import Path
from datetime import datetime


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataManager:
    """식품 영양성분 데이터 관리 클래스"""
    
    def __init__(self, base_dir: Path = None):
        if base_dir is None:
            base_dir = Path(__file__).parent
            
        # 경로 설정
        self.data_dir = base_dir / "data"
        
        self.excel_path = self.data_dir / "food_data" / "통합_식품영양성분DB_음식_20230715.xlsx"
        self.csv_path = self.data_dir / "food_data" / "processed_food_data.csv"
        self.db_path = self.data_dir / "food_nutrition.db"
        self.sql_schema_path = self.data_dir / "table_schema.sql"
    
    def get_csv_hash(self) -> str:
        try:
            with open(self.csv_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"CSV 해시값 계산 중 오류: {e}")
            return ""
    
    def process_excel_to_csv(self) -> bool:
        """Excel 파일 처리하여 CSV로 변환"""
        logger.info(f"Excel 파일 처리 시작: {self.excel_path}")
        
        # Excel 파일 읽기
        df = pd.read_excel(self.excel_path)
        logger.info(f"Excel 파일 로드: {len(df)} 행")
        
        # 컬럼 매핑 정의 (한글 -> 영문)
        # 요청인자.md에 명시된 매핑 정의
        column_mapping = {
            'NO': 'id',
            '식품코드': 'food_cd',
            '식품대분류': 'group_name',
            '식품명': 'food_name',
            '연도': 'research_year',
            '지역 / 제조사': 'maker_name',
            '성분표출처': 'ref_name',
            '1회제공량': 'serving_size',
            '에너지(㎉)': 'calorie',
            '탄수화물(g)': 'carbohydrate',
            '단백질(g)': 'protein',
            '지방(g)': 'province',
            '총당류(g)': 'sugars',
            '나트륨(㎎)': 'salt',
            '콜레스테롤(㎎)': 'cholesterol',
            '총 포화 지방산(g)': 'saturated_fatty_acids',
            '트랜스 지방산(g)': 'trans_fat',
        }
        
        # 디버깅을 위해 원본 컬럼 출력
        logger.info(f"원본 엑셀 파일 컬럼: {list(df.columns)}")
        
        # 컬럼명 변환 및 매핑 결과 확인
        # 매핑 적용 전 컬럼명 목록
        original_columns = df.columns.tolist()
        logger.info(f"매핑 전 컬럼 수: {len(original_columns)}")
        
        # 컬럼 이름 변경 (기존 매핑 방식)
        df = df.rename(columns=column_mapping)
        
        # 매핑 이후 실제 변환된 컬럼 목록 확인
        mapped_columns = [col for col in df.columns if col in column_mapping.values()]
        logger.info(f"성공적으로 매핑된 컬럼: {mapped_columns}")
        
        # 원하는 필수 컬럼 목록 (중복 제거)
        required_columns = ['id', 'food_cd', 'group_name', 'food_name', 'research_year', 'maker_name', 'ref_name', 
                        'serving_size', 'calorie', 'carbohydrate', 'protein', 'province', 'sugars', 
                        'salt', 'cholesterol', 'saturated_fatty_acids', 'trans_fat']
        
        # 매핑 후 누락된 필수 컬럼 확인
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"필수 컬럼 중 누락된 컬럼: {missing_columns}")
            # 없는 컬럼 추가 (사용자 요구사항에 따라 빈 값으로 초기화)
            for col in missing_columns:
                df[col] = ''
        
        # 데이터 전처리 
        # 단위 제거 및 숫자로 변환
        numeric_columns = ['serving_size', 'calorie', 'carbohydrate', 'protein', 'province', 
                          'sugars', 'salt', 'cholesterol', 'saturated_fatty_acids', 'trans_fat']
        
        # 숫자형 컬럼 처리
        for col in numeric_columns:
            if col in df.columns:
                logger.info(f"컬럼 '{col}' 전처리 중...")
                
                # 데이터 타입 확인 및 로깅
                logger.info(f"컬럼 '{col}' 데이터 타입: {df[col].dtype}")
                
                # '-' 값을 NaN으로 변환
                df[col] = df[col].replace('-', pd.NA)
                
                # 단위(g, mg, kcal 등) 제거 - 더 강화된 정규식 사용
                df[col] = df[col].apply(
                    lambda x: re.sub(r'[^0-9\.]', '', str(x).replace(',', '.')) 
                    if pd.notna(x) and str(x).strip() != '' else x
                )
                
                # 데이터 변환 결과 로깅 (처음 5개 항목 샘플)
                sample_values = df[col].head(5).tolist()
                logger.info(f"컬럼 '{col}' 샘플 데이터(단위 제거 후): {sample_values}")
                
                # 숫자로 변환 (coerce 옵션으로 변환 불가 값은 NaN으로)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 요구사항대로 NaN 값을 0으로 변환
                df[col] = df[col].fillna(0)
        
        # 문자열 컬럼 처리
        string_columns = ['food_cd', 'group_name', 'food_name', 'research_year', 'maker_name', 'ref_name']
        for col in string_columns:
            if col in df.columns:
                # 요구사항대로 NaN 값을 빈 문자열로 변환
                df[col] = df[col].fillna('')

        # 요청인자.md에 명시된 순서대로 컬럼 배치
        df = df[required_columns]
        
        # CSV 저장
        df.to_csv(self.csv_path, index=False, encoding='utf-8')
        logger.info(f"CSV 파일 저장 완료: {self.csv_path}, 컬럼: {list(df.columns)}")
        
        return True
    
    def check_db_status(self) -> tuple[bool, bool]:
        """DB 상태 및 CSV 변경 여부 확인"""
        db_initialized = False
        csv_changed = False
        
        # 파일 존재 확인
        if not self.csv_path.exists():
            logger.error(f"CSV 파일이 없습니다: {self.csv_path}")
            return db_initialized, csv_changed
        
        if not self.db_path.exists():
            logger.info(f"DB 파일이 없습니다: {self.db_path}")
            return db_initialized, csv_changed
        
        # 현재 CSV 해시값
        current_csv_hash = self.get_csv_hash()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 메타 테이블 확인
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # foods 테이블 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='foods'")
        if cursor.fetchone():
            # 데이터 존재 확인
            cursor.execute("SELECT COUNT(*) FROM foods")
            count = cursor.fetchone()[0]
            if count > 0:
                db_initialized = True
                logger.info(f"데이터베이스에 {count}개의 레코드가 있습니다.")
            
            # 저장된 해시값 확인
            cursor.execute("SELECT value FROM meta WHERE key='csv_hash'")
            row = cursor.fetchone()
            if row:
                stored_hash = row[0]
                if current_csv_hash and stored_hash != current_csv_hash:
                    csv_changed = True
                    logger.info("CSV 파일이 변경되었습니다. 데이터 갱신이 필요합니다.")
        
        conn.close()
        
        return db_initialized, csv_changed
    
    def update_database(self) -> bool:
        """CSV 데이터로 데이터베이스 갱신"""
        # CSV 파일 로드
        logger.info(f"CSV 파일 로드: {self.csv_path}")
        df = pd.read_csv(self.csv_path)
        logger.info(f"총 {len(df)} 개의 레코드 로드됨")
        
        # 테이블 스키마에 없는 컬럼 제거 (예: 'NO' 컬럼)
        if 'NO' in df.columns:
            logger.info("'NO' 컬럼 제거 - 테이블 스키마에 없음")
            df = df.drop(columns=['NO'])
        
        # DB 연결
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SQL 스키마 실행 (테이블 정의)
        logger.info(f"테이블 스키마 적용: {self.sql_schema_path}")
        with open(self.sql_schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)
        
        # 기존 데이터 삭제
        cursor.execute("DELETE FROM foods")
        logger.info("기존 데이터 삭제 완료")
        
        # CSV 데이터 삽입 (pandas to_sql 사용 - SQL Injection 방지)
        logger.info("CSV 데이터 DB에 삽입 시작")
        df.to_sql('foods', conn, if_exists='append', index=False)
        
        # 메타 정보 업데이트
        csv_hash = self.get_csv_hash()
        timestamp = datetime.now().isoformat()
        
        cursor.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", 
                     ('csv_hash', csv_hash))
        cursor.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", 
                     ('last_updated', timestamp))
        
        conn.commit()
        conn.close()
        
        logger.info(f"데이터베이스 갱신 완료: {len(df)} 레코드, 타임스탬프: {timestamp}")
        logger.info(f"CSV 해시: {csv_hash}")
        return True
    
    def run(self):
        """데이터 임포트 프로세스 실행"""
        # 1. CSV 파일이 없으면 Excel -> CSV 변환
        if not self.csv_path.exists():
            logger.info("CSV 파일이 없습니다. Excel 파일에서 변환합니다.")
            self.process_excel_to_csv()
        
        # 2. DB 상태 확인
        db_initialized, csv_changed = self.check_db_status()
        
        # 3. DB 초기화 또는 갱신 필요 여부 판단
        if not db_initialized or csv_changed:
            action = "초기화" if not db_initialized else "갱신"
            logger.info(f"데이터베이스 {action}가 필요합니다.")
            if self.update_database():
                logger.info(f"데이터베이스 {action}가 완료되었습니다.")
        else:
            logger.info("데이터베이스가 이미 초기화되어 있고 CSV도 변경되지 않았습니다. 아무 작업도 수행하지 않습니다.")


def main():
    """메인 함수"""
    manager = DataManager()
    manager.run()


if __name__ == "__main__":
    main()