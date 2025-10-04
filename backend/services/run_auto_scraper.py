"""
Auto Scraper 실행 래퍼 스크립트
auto_scraper-ver1.4.1-final의 기능을 backend/services에서 실행할 수 있도록 함

사용법 (프로젝트 루트에서):
  # Windows:
  backend\\venv\\Scripts\\python backend\\services\\run_auto_scraper.py
  backend\\venv\\Scripts\\python backend\\services\\run_auto_scraper.py "https://apply.lh.or.kr/..."

  # Mac/Linux:
  backend/venv/bin/python backend/services/run_auto_scraper.py
  backend/venv/bin/python backend/services/run_auto_scraper.py "https://apply.lh.or.kr/..."
"""

import os
import sys

# auto_scraper 모듈의 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
auto_scraper_dir = os.path.join(current_dir, 'auto_scraper')
sys.path.insert(0, auto_scraper_dir)

# auto_scraper 메인 모듈 임포트 및 실행
if __name__ == "__main__":
    # 작업 디렉토리를 auto_scraper 폴더로 변경 (상대 경로 문제 해결)
    os.chdir(auto_scraper_dir)

    # auto_scraper.py의 main 함수 실행
    from auto_scraper import main

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.\n")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}\n")
