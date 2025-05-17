import pandas as pd
import numpy as np
from pathlib import Path

def analyze_excel_data(excel_path):
    """엑셀 파일을 분석하고 데이터 구조 및 결측치 정보를 반환합니다."""
    print(f"Loading file: {excel_path}")
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        print(f"Successfully loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None
    
    # 기본 정보 수집
    analysis = {
        "file_path": str(excel_path),
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": df.columns.tolist(),
        "sample_data": df.head(5).to_dict('records'),
        "missing_data": {}
    }
    
    # 결측치 분석
    missing_stats = df.isnull().sum()
    missing_percent = (df.isnull().sum() / len(df)) * 100
    
    for column in df.columns:
        missing_count = missing_stats[column]
        missing_pct = missing_percent[column]
        analysis["missing_data"][column] = {
            "count": int(missing_count),
            "percent": float(missing_pct),
            "has_missing": missing_count > 0
        }
    
    # 데이터 타입 분석
    analysis["data_types"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    # 수치형 컬럼 통계 (결측치 제외)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    analysis["numeric_stats"] = {}
    for col in numeric_cols:
        analysis["numeric_stats"][col] = {
            "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
            "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
            "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
            "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
        }
    
    # 중복 데이터 확인
    analysis["duplicate_rows"] = int(df.duplicated().sum())
    
    return analysis

def write_analysis_to_txt(analysis, output_path):
    """분석 결과를 텍스트 파일로 저장합니다."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("===== 식품 영양성분 데이터 분석 결과 =====\n\n")
        
        # 기본 정보
        f.write(f"파일 경로: {analysis['file_path']}\n")
        f.write(f"총 행 수: {analysis['row_count']}\n")
        f.write(f"총 열 수: {analysis['column_count']}\n\n")
        
        # 컬럼 목록
        f.write("===== 컬럼 목록 =====\n")
        for i, col in enumerate(analysis['columns']):
            f.write(f"{i+1}. {col} (타입: {analysis['data_types'][col]})\n")
        f.write("\n")
        
        # 결측치 분석
        f.write("===== 결측치 분석 =====\n")
        missing_cols = [col for col in analysis['missing_data'] if analysis['missing_data'][col]['has_missing']]
        if missing_cols:
            for col in missing_cols:
                info = analysis['missing_data'][col]
                f.write(f"{col}: {info['count']}개 결측 ({info['percent']:.2f}%)\n")
        else:
            f.write("결측치가 없는 완전한 데이터셋입니다.\n")
        f.write("\n")
        
        # 수치형 데이터 통계
        if analysis.get("numeric_stats"):
            f.write("===== 수치형 데이터 통계 =====\n")
            for col, stats in analysis["numeric_stats"].items():
                f.write(f"{col}:\n")
                f.write(f"  - 최소값: {stats['min']}\n")
                f.write(f"  - 최대값: {stats['max']}\n")
                f.write(f"  - 평균값: {stats['mean']}\n")
                f.write(f"  - 중앙값: {stats['median']}\n")
            f.write("\n")
        
        # 중복 데이터
        f.write(f"중복 행 수: {analysis['duplicate_rows']}\n\n")
        
        # 샘플 데이터
        f.write("===== 샘플 데이터 (처음 5행) =====\n")
        for i, row in enumerate(analysis['sample_data']):
            f.write(f"행 {i+1}:\n")
            for col, val in row.items():
                f.write(f"  - {col}: {val}\n")
            f.write("\n")
        
        # 식품 데이터베이스 구성 방안
        f.write("\n===== 데이터 처리 및 변환 방안 =====\n")
        f.write("1. 요청인자.md 기반 필요 컬럼 매핑:\n")
        required_columns = [
            "id", "food_cd", "group_name", "food_name", "research_year", 
            "maker_name", "ref_name", "serving_size", "calorie", "carbohydrate", 
            "protein", "province", "sugars", "salt", "cholesterol", 
            "saturated_fatty_acids", "trans_fat"
        ]
        
        existing_columns = set(analysis['columns'])
        
        for col in required_columns:
            status = "존재" if col in existing_columns else "생성 필요"
            f.write(f"  - {col}: {status}\n")
        
        f.write("\n2. 컬럼 매핑 방안:\n")
        f.write("  - 원본 컬럼명과 목표 컬럼명의 매핑 테이블 작성\n")
        f.write("  - 대소문자 및 공백 무시하고 유사한 컬럼명 매핑\n")
        f.write("  - 존재하지 않는 컬럼은 기본값으로 생성\n\n")
        
        f.write("3. 데이터 정제 방안:\n")
        f.write("  - 결측치: 수치형 데이터는 0으로, 문자열은 빈 문자열로 대체\n")
        f.write("  - 데이터 타입 변환: 각 컬럼에 적합한 데이터 타입으로 변환\n")
        f.write("  - 중복 데이터 제거: 필요시 중복 행 제거\n\n")
        
        f.write("4. 컬럼 데이터 타입:\n")
        f.write("  - 문자열 컬럼: food_cd, group_name, food_name, research_year, maker_name, ref_name\n")
        f.write("  - 숫자형 컬럼: serving_size, calorie, carbohydrate, protein, province, sugars, salt, cholesterol, saturated_fatty_acids, trans_fat\n")

if __name__ == "__main__":
    # 파일 경로
    current_dir = Path(__file__).resolve().parent
    excel_path = current_dir / "통합 식품영양성분DB_음식_20230715.xlsx"
    output_path = current_dir / "식품영양성분_데이터분석결과.txt"
    
    # 분석 실행
    analysis = analyze_excel_data(excel_path)
    
    if analysis:
        write_analysis_to_txt(analysis, output_path)
        print(f"분석 결과가 {output_path}에 저장되었습니다.")
    else:
        print("분석을 완료할 수 없습니다. 파일을 확인해주세요.")
