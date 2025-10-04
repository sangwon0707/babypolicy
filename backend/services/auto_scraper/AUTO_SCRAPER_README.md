# Auto Scraper 사용 가이드

## 📁 폴더 구조

```
backend/services/
├── auto_scraper/              # 스크래퍼 메인 폴더
│   ├── auto_scraper.py        # 메인 실행 파일
│   ├── config.py              # 설정 파일
│   ├── database.py            # DB 관리
│   ├── pdf_detector.py        # PDF 탐지 로직
│   ├── utils.py               # 유틸리티 함수
│   ├── data/                  # 데이터 폴더
│   │   ├── downloads/         # PDF 다운로드 폴더
│   │   └── logs/              # 로그 폴더
│   ├── requirements.txt       # 필요한 패키지
│   └── README.md              # 원본 문서
├── run_auto_scraper.py        # 실행 래퍼 스크립트
└── run_scraper.bat            # Windows 배치 파일 (더블클릭으로 실행)
```

## 🚀 실행 방법

### 방법 1: 배치 파일 실행 (가장 간단)

```
backend/services/run_scraper.bat 파일을 더블클릭
```

### 방법 2: Python 스크립트 실행

```bash
cd backend/services
python run_auto_scraper.py
```

### 방법 3: 직접 실행

```bash
cd backend/services/auto_scraper
python auto_scraper.py
```

### 방법 4: 명령줄 인자로 URL 전달 (자동 모드)

```bash
python run_auto_scraper.py https://example.com/board
```

## 📦 필수 패키지 설치

```bash
cd backend/services/auto_scraper
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install selenium webdriver-manager requests
```

## ⚙️ 설정 변경

`auto_scraper/config.py` 파일에서 다양한 설정을 변경할 수 있습니다:

- `DOWNLOAD_DIR`: 다운로드 폴더 경로
- `HEADLESS_MODE`: GUI 없이 실행 (True/False)
- `TIMEOUT`: 페이지 로딩 및 대기 시간
- `DEBUG_LEVEL`: 로그 상세도 조정
- `USE_DATABASE`: SQLite DB 사용 여부

## 🔒 개인정보 보호 (ver1.4.1)

- 이메일 주소 자동 수집 차단
- 전화번호, 주민번호 등 개인정보 필터링
- PDF 파일만 다운로드 (다른 형식 차단)
- 로그에서 개인정보 자동 마스킹

## 📊 주요 기능

1. **자동 PDF 탐지 및 다운로드**
   - 다중 전략 기반 PDF 링크 탐지
   - JavaScript 링크 처리
   - 첨부파일, 다운로드 버튼 자동 인식

2. **페이지네이션 자동 처리**
   - 다음 페이지 자동 이동
   - Checkpoint 기능으로 중단 후 재개 가능

3. **전략 학습 시스템 (ver1.3+)**
   - 게시판별 성공 전략 자동 학습
   - 페이지별 빠른 모드 적용
   - 학습 데이터 저장/로드

4. **안정성 강화 (ver1.4)**
   - 연속 에러 복구
   - 브라우저 자동 재시작
   - Stale element 방지

## 🗂️ 데이터 위치

- **다운로드된 PDF**: `auto_scraper/data/downloads/`
- **로그 파일**: `auto_scraper/data/logs/`
- **학습 데이터**: `auto_scraper/data/logs/learned_strategies.json`
- **체크포인트**: `auto_scraper/data/logs/checkpoint.json`

## 🛠️ 문제 해결

### Chrome Driver 오류
```bash
pip install --upgrade webdriver-manager
```

### 인코딩 오류 (Windows)
- 배치 파일 사용 시 자동으로 UTF-8 설정됨
- 직접 실행 시 `chcp 65001` 명령 실행

### 경로 오류
- 반드시 `run_auto_scraper.py`를 통해 실행
- `auto_scraper.py`를 직접 실행할 경우 `auto_scraper` 폴더 내부에서 실행

## 📝 사용 예시

```bash
# 1. services 폴더로 이동
cd C:\Users\Jun\OneDrive\Desktop\MS\baby project\demo\babypolicy\backend\services

# 2. 스크래퍼 실행
python run_auto_scraper.py

# 또는 배치 파일 실행
run_scraper.bat

# 3. 프롬프트에 게시판 URL 입력
# 예) https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52005M.do

# 4. 다운로드 폴더 경로 입력 (또는 Enter로 기본값 사용)

# 5. 스크래핑 시작
```

## 🔄 재개 기능

이전 작업이 중단된 경우, 다시 실행하면 체크포인트를 감지하고 이어서 진행할 수 있습니다.

```
💾 이전 작업을 발견했습니다:
   페이지: 3
   진행: 5번째 게시글
   다운로드 완료: 42개

🔄 이어서 진행하시겠습니까? [y/n]:
```

## 📞 문의 및 버그 리포트

문제 발생 시 `auto_scraper/data/logs/debug_log.txt` 파일을 확인하세요.
