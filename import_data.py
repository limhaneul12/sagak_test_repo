import pandas as pd
import sqlite3
import hashlib
import logging
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
        self.data_dir.mkdir(exist_ok=True)
        
        # food_data 디렉토리 생성
        food_data_dir = self.data_dir / "food_data"
        food_data_dir.mkdir(exist_ok=True)
        
        self.excel_path = self.data_dir / "food_data/통합 식품영양성분DB_음식_20230715.xlsx"
        self.csv_path = self.data_dir / "food_data/processed_food_data.csv"
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
        
        # CSV 저장
        df.to_csv(self.csv_path, index=False, encoding='utf-8')
        logger.info(f"CSV 파일 저장 완료: {self.csv_path}")
        
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