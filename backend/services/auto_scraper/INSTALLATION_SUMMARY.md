# Auto Scraper 설치 완료 요약

## ✅ 완료된 작업

### 1. 폴더 이동 및 구조 설정

원본 위치:
```
C:\Users\Jun\OneDrive\Desktop\MS\baby project\bokjiro_scraper\auto_scraper-ver1.4.1-final
```

새 위치:
```
C:\Users\Jun\OneDrive\Desktop\MS\baby project\demo\babypolicy\backend\services\auto_scraper
```

### 2. 최종 폴더 구조

```
backend/services/
├── auto_scraper/                    # 스크래퍼 메인 폴더
│   ├── auto_scraper.py              # 메인 실행 파일 ⭐
│   ├── config.py                    # 설정 파일
│   ├── database.py                  # DB 관리
│   ├── pdf_detector.py              # PDF 탐지 로직
│   ├── utils.py                     # 유틸리티 함수
│   ├── requirements.txt             # 필요한 패키지 목록
│   ├── README.md                    # 원본 문서
│   ├── HISTORY.md                   # 버전 히스토리
│   └── data/                        # 데이터 폴더
│       ├── downloads/               # PDF 다운로드 저장 위치
│       └── logs/                    # 로그 파일 저장 위치
│
├── run_auto_scraper.py              # 실행 래퍼 스크립트 ⭐
├── run_scraper.bat                  # Windows 배치 파일 (더블클릭 실행) ⭐
├── AUTO_SCRAPER_README.md           # 사용 가이드
└── INSTALLATION_SUMMARY.md          # 이 파일

기타 서비스 파일들:
├── scraper_service.py               # 기존 복지로 스크래퍼
├── rag_service.py                   # RAG 서비스
├── babypolicy_chat_ingest.py        # 채팅 데이터 처리
└── babypolicy_chat/                 # 채팅 관련 폴더
```

### 3. 생성된 파일들

#### a) `run_auto_scraper.py` - Python 실행 래퍼
- `auto_scraper` 폴더의 경로를 자동으로 설정
- 작업 디렉토리를 자동으로 변경
- 상대 경로 문제 해결

#### b) `run_scraper.bat` - Windows 배치 파일
- 더블클릭으로 간편하게 실행
- UTF-8 인코딩 자동 설정
- 한글 출력 문제 해결

#### c) `requirements.txt` - 필요한 패키지 목록
```
selenium>=4.0.0
webdriver-manager>=3.8.0
requests>=2.28.0
```

#### d) `AUTO_SCRAPER_README.md` - 상세 사용 가이드
- 실행 방법 4가지 제공
- 설정 변경 가이드
- 문제 해결 방법
- 사용 예시

## 🚀 실행 방법

### 🟢 추천: 배치 파일 실행 (가장 간단)
```
services/run_scraper.bat 파일을 더블클릭
```

### Python 스크립트 실행
```bash
cd backend/services
python run_auto_scraper.py
```

### 직접 실행 (auto_scraper 폴더 내부)
```bash
cd backend/services/auto_scraper
python auto_scraper.py
```

### 자동 모드 (URL 직접 전달)
```bash
python run_auto_scraper.py https://example.com/board
```

## 📦 설치 확인

### 1. 필요한 패키지 설치
```bash
cd backend/services/auto_scraper
pip install -r requirements.txt
```

### 2. 테스트 실행
```bash
cd backend/services
python run_auto_scraper.py
```

프롬프트가 나타나면 성공적으로 설치된 것입니다!

## ⚙️ 주요 설정 (config.py)

스크래퍼 동작을 커스터마이징하려면 `auto_scraper/config.py` 파일을 수정하세요:

```python
# 다운로드 폴더
DOWNLOAD_DIR = os.path.join(DATA_DIR, 'downloads')

# 헤드리스 모드 (GUI 없이 실행)
HEADLESS_MODE = False  # True로 변경하면 브라우저 창이 보이지 않음

# 타임아웃 설정
TIMEOUT = {
    'page_load': 20,      # 페이지 로딩 대기 시간
    'element_wait': 10,   # 요소 대기 시간
    'download_wait': 30,  # 다운로드 대기 시간
    'page_stable': 5      # 페이지 안정화 대기 시간
}

# 디버그 레벨
CURRENT_DEBUG_LEVEL = DEBUG_LEVELS['VERBOSE']  # ERROR, WARNING, INFO, DEBUG, VERBOSE

# 데이터베이스 사용
USE_DATABASE = True  # SQLite DB로 다운로드 이력 관리

# 전략 학습 시스템
USE_STRATEGY_LEARNING = True  # 게시판별 성공 전략 자동 학습
```

## 🔒 개인정보 보호 기능 (ver1.4.1)

자동으로 활성화된 보호 기능:
- ✅ 이메일 주소 자동 수집 차단
- ✅ 전화번호, 주민번호 필터링
- ✅ PDF 파일만 다운로드 (다른 형식 차단)
- ✅ 로그에서 개인정보 자동 마스킹

## 📊 특징 및 기능

### 1. 범용 PDF 자동 스크래퍼
- 다양한 게시판 구조에 자동 적응
- JavaScript 동적 링크 처리
- 첨부파일, 다운로드 버튼 자동 인식

### 2. 페이지네이션 자동 처리
- 다음 페이지 자동 이동
- 무한 스크롤 지원

### 3. Checkpoint 기능
- 중단 시 현재 위치 저장
- 재실행 시 이어서 진행 가능

### 4. 전략 학습 시스템 (ver1.3+)
- 게시판별 성공 전략 자동 학습
- 페이지 단위 빠른 모드 적용
- 학습 데이터 영구 저장

### 5. 안정성 강화 (ver1.4)
- 연속 에러 복구
- 브라우저 자동 재시작
- Stale element 방지

## 🗂️ 데이터 저장 위치

- **다운로드된 PDF**: `auto_scraper/data/downloads/`
- **디버그 로그**: `auto_scraper/data/logs/debug_log.txt`
- **다운로드 로그**: `auto_scraper/data/logs/download_log.json`
- **실패 로그**: `auto_scraper/data/logs/failed_log.json`
- **학습 데이터**: `auto_scraper/data/logs/learned_strategies.json`
- **체크포인트**: `auto_scraper/data/logs/checkpoint.json`
- **데이터베이스**: `auto_scraper/data/logs/processed_articles.db` (SQLite)

## 🛠️ 문제 해결

### Chrome Driver 오류
```bash
pip install --upgrade webdriver-manager
```

### 인코딩 오류 (한글 깨짐)
- 배치 파일(`run_scraper.bat`) 사용 권장
- 또는 명령 프롬프트에서 `chcp 65001` 실행 후 스크립트 실행

### 모듈 import 오류
- 반드시 `run_auto_scraper.py`를 사용하여 실행
- 또는 `auto_scraper` 폴더 내부에서 직접 실행

### Selenium 관련 오류
```bash
pip install --upgrade selenium
```

## 📞 추가 정보

- 원본 README: `auto_scraper/README.md`
- 버전 히스토리: `auto_scraper/HISTORY.md`
- 사용 가이드: `AUTO_SCRAPER_README.md`

## ✨ 다음 단계

1. **필수 패키지 설치**
   ```bash
   cd auto_scraper
   pip install -r requirements.txt
   ```

2. **테스트 실행**
   ```bash
   cd ..
   python run_auto_scraper.py
   ```

3. **설정 커스터마이징** (선택사항)
   - `auto_scraper/config.py` 파일 편집

4. **실제 스크래핑 시작**
   - 게시판 URL 입력
   - 자동으로 PDF 다운로드 시작!

---

**설치 완료! 🎉**

문제가 발생하면 `auto_scraper/data/logs/debug_log.txt` 파일을 확인하세요.
