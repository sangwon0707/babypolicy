"""
Bokjiro Scraper 실행 래퍼 스크립트
bokjiro_scraper 폴더의 기능을 backend/services에서 실행할 수 있도록 함

사용법 (프로젝트 루트에서):
  # Windows:
  backend\\venv\\Scripts\\python backend\\services\\run_bokjiro_scraper.py

  # Mac/Linux:
  backend/venv/bin/python backend/services/run_bokjiro_scraper.py
"""

import os
import sys

# bokjiro_scraper 모듈의 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
bokjiro_scraper_dir = os.path.join(current_dir, 'bokjiro_scraper')
sys.path.insert(0, bokjiro_scraper_dir)

# bokjiro_scraper 메인 모듈 임포트 및 실행
if __name__ == "__main__":
    # bokjiro_scraper.py의 main 함수 실행
    import bokjiro_scraper

    try:
        bokjiro_scraper.main()
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.\n")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}\n")
        import traceback
        traceback.print_exc()
