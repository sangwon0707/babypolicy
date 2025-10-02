"""
Bokjiro Scraper 실행 래퍼 스크립트
bokjiro_scraper 폴더의 기능을 backend/services에서 실행할 수 있도록 함
"""

import os
import sys

# bokjiro_scraper 모듈의 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
bokjiro_scraper_dir = os.path.join(current_dir, 'bokjiro_scraper')
sys.path.insert(0, bokjiro_scraper_dir)

# bokjiro_scraper 메인 모듈 임포트 및 실행
if __name__ == "__main__":
    # 작업 디렉토리를 bokjiro_scraper 폴더로 변경 (상대 경로 문제 해결)
    os.chdir(bokjiro_scraper_dir)

    # bokjiro_scraper.py의 main 함수 실행
    import bokjiro_scraper

    try:
        # bokjiro_scraper.py에 main() 함수가 있으면 실행
        if hasattr(bokjiro_scraper, 'main'):
            bokjiro_scraper.main()
        else:
            # main() 함수가 없으면 모듈 직접 실행
            print("복지로(Bokjiro) PDF 스크래퍼를 시작합니다...")
            print("스크래퍼 모듈이 로드되었습니다.")
            print("\n프로그램을 시작하려면 bokjiro_scraper.py를 직접 확인하세요.")
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.\n")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}\n")
        import traceback
        traceback.print_exc()
