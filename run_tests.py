#!/usr/bin/env python
"""테스트 실행 및 결과 보고서 생성 스크립트"""
import os
import sys
import subprocess
from datetime import datetime

# 프로젝트 루트 경로 추가
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_tests_and_generate_report():
    """테스트 실행 및 결과 보고서 생성"""
    report_file = "test_result.txt"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 테스트 실행 환경에 경로 추가
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH', '')}"
    
    print("테스트 실행 중...")
    try:
        # pytest 실행
        result = subprocess.run(
            ["pytest", "-v", "app/tests"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # 결과 보고서 작성
        with open(report_file, "w") as f:
            f.write(f"# Food Nutrition Database API 테스트 보고서\n\n")
            f.write(f"## 실행 시간: {current_time}\n\n")
            
            # 결과 표시
            success = result.returncode == 0
            f.write(f"## 테스트 결과: {'\u2705 성공' if success else '\u274c 실패'}\n\n")
            
            # stdout 출력
            f.write("## 상세 테스트 결과\n\n```\n")
            f.write(result.stdout)
            f.write("```\n\n")
            
            # stderr 출력 (있는 경우)
            if result.stderr:
                f.write("## 오류 메시지\n\n```\n")
                f.write(result.stderr)
                f.write("```\n\n")
            
            # 테스트 환경 정보
            f.write("## 환경 정보\n\n")
            f.write(f"- Python 버전: {sys.version.split()[0]}\n")
            f.write(f"- 운영체제: {sys.platform}\n")
            f.write(f"- 데이터베이스: data/food_nutrition.db (실제 DB 사용)\n")
        
        print(f"테스트 완료! 결과: {report_file}")
        return success
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = run_tests_and_generate_report()
    sys.exit(0 if success else 1)
