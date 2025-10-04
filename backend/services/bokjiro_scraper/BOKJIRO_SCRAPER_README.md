# Bokjiro Scraper 사용 가이드 v2.0

## 🆕 v2.0 업데이트 내용

✨ **Auto Scraper와 동일한 옵션 제공**
- 데이터 통계 표시 (PDF 개수, 로그 크기 등)
- 3가지 초기화 옵션 (로그만 / 완전 초기화 / 초기화 안 함)
- 다운로드 디렉토리 선택 기능
- 체크포인트 재개 기능 강화
- fresh_start.py 통합 (별도 파일 불필요)

## 📁 폴더 구조

```
backend/services/
├── bokjiro_scraper/           # 복지로 스크래퍼 메인 폴더
│   ├── bokjiro_scraper.py     # 메인 실행 파일 ⭐
│   ├── requirements.txt       # 필요한 패키지
│   ├── README.md              # 원본 문서
│   └── data/                  # 데이터 폴더
│       ├── pdfs/              # PDF 다운로드 폴더
│       │   └── bokjiro/       # 복지로 PDF 저장 위치
│       └── logs/              # 로그 폴더
│           ├── download_log.json
│           ├── debug_log.txt
│           └── checkpoint.json
│
├── run_bokjiro_scraper.py     # 실행 래퍼 스크립트 ⭐
└── run_bokjiro.bat            # Windows 배치 파일 (더블클릭 실행) ⭐
```

## 🚀 실행 방법

### 방법 1: 배치 파일 실행 (가장 간단)

```
backend/services/run_bokjiro.bat 파일을 더블클릭
```

### 방법 2: Python 스크립트 실행

```bash
cd backend/services
python run_bokjiro_scraper.py
```

### 방법 3: 직접 실행

```bash
cd backend/services/bokjiro_scraper
python bokjiro_scraper.py
```

## 📦 필수 패키지 설치

```bash
cd backend/services/bokjiro_scraper
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install selenium webdriver-manager
```

## 🎯 주요 기능

### 1. **복지로(Bokjiro) PDF 자동 다운로드**
   - 복지로 사이트에서 정책 정보 자동 수집
   - PDF 파일 자동 다운로드
   - 중복 다운로드 방지

### 2. **체크포인트 기능**
   - 중단 시 현재 위치 저장
   - 재실행 시 이어서 진행 가능

### 3. **상세한 로깅**
   - 다운로드 로그 (`download_log.json`)
   - 디버그 로그 (`debug_log.txt`)
   - 실시간 진행 상황 표시

### 4. **데이터 관리 기능 (v2.0 신규)**
   - 📊 현재 데이터 통계 표시
   - 🔄 3가지 초기화 옵션:
     - 옵션 1: 로그만 삭제 (PDF 유지)
     - 옵션 2: 완전 초기화 (PDF + 로그 모두 삭제)
     - 옵션 3: 초기화 안 함
   - 📂 다운로드 디렉토리 사용자 지정

## 🗂️ 데이터 위치

- **다운로드된 PDF**: `bokjiro_scraper/data/pdfs/bokjiro/`
- **다운로드 로그**: `bokjiro_scraper/data/logs/download_log.json`
- **디버그 로그**: `bokjiro_scraper/data/logs/debug_log.txt`
- **체크포인트**: `bokjiro_scraper/data/logs/checkpoint.json`

## 🔄 실행 시 옵션 선택

### 1. 데이터 통계 확인
프로그램 시작 시 자동으로 표시:
```
📊 현재 데이터 현황:
   📄 다운로드된 PDF: 42개
   📝 로그 크기: 125.3 KB
   💾 체크포인트: 있음
```

### 2. 초기화 옵션 선택
```
🔄 초기화 옵션:
   1. 데이터 초기화 (로그만 삭제, PDF 유지)
   2. 완전 초기화 (PDF + 로그 모두 삭제)
   3. 초기화 안 함 (기존 데이터 사용)

선택 [1/2/3]:
```

### 3. 체크포인트 재개
이전 작업이 중단된 경우:
```
💾 이전 작업을 발견했습니다:
   마지막 페이지: 5
   마지막 정책: 3번째
   타임스탬프: 2025-10-02 16:30:00

🔄 이어서 진행하시겠습니까? [y/n]:
```

### 4. 다운로드 폴더 선택
```
📂 다운로드 폴더 경로
   기본값: C:\...\data\pdfs\bokjiro
   다른 경로 입력 (엔터키: 기본값 사용):
```

## ⚙️ 설정

`bokjiro_scraper.py` 파일 상단에서 설정 가능:

```python
# 복지로 기본 URL
BASE_URL = "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/..."

# 다운로드 폴더
DOWNLOAD_DIR = os.path.join(os.getcwd(), 'data', 'pdfs', 'bokjiro')

# 디버그 레벨
CURRENT_DEBUG_LEVEL = DEBUG_LEVELS['VERBOSE']  # ERROR, WARNING, INFO, DEBUG, VERBOSE
```

## 🛠️ 문제 해결

### Chrome Driver 오류
```bash
pip install --upgrade webdriver-manager
```

### 인코딩 오류 (한글 깨짐)
- 배치 파일(`run_bokjiro.bat`) 사용 권장
- 또는 명령 프롬프트에서 `chcp 65001` 실행 후 스크립트 실행

### 모듈 import 오류
- 반드시 `run_bokjiro_scraper.py`를 사용하여 실행
- 또는 `bokjiro_scraper` 폴더 내부에서 직접 실행

## 📝 사용 예시

```bash
# 1. services 폴더로 이동
cd C:\Users\Jun\OneDrive\Desktop\MS\baby project\demo\babypolicy\backend\services

# 2. 스크래퍼 실행
python run_bokjiro_scraper.py

# 또는 배치 파일 실행
run_bokjiro.bat

# 3. 옵션 선택
# - 초기화 옵션 선택 (1/2/3)
# - 체크포인트 재개 여부 (y/n)
# - 다운로드 폴더 경로 (엔터: 기본값)

# 4. 스크래핑 시작
# 엔터키를 누르면 자동으로 복지로 사이트 접속 및 PDF 다운로드 시작
```

## 💡 바탕화면 바로가기

`run_bokjiro.bat` 파일의 바로가기를 바탕화면에 만들면:
- **더블클릭만으로 즉시 실행**
- 별도의 명령 프롬프트 없이 사용 가능

바로가기 이름 예시: **"복지로 PDF 다운로더"**

## 🆚 v1.0과 v2.0 비교

| 기능 | v1.0 | v2.0 |
|------|------|------|
| **초기화** | fresh_start.py 별도 실행 | 메인 프로그램에 통합 ✅ |
| **통계 표시** | ❌ | PDF 개수, 로그 크기 표시 ✅ |
| **초기화 옵션** | 전체 삭제만 가능 | 3가지 옵션 제공 ✅ |
| **폴더 선택** | 고정 경로 | 사용자 지정 가능 ✅ |
| **체크포인트** | 기본 기능 | 상세 정보 표시 ✅ |
| **사용 편의성** | 보통 | 매우 편리 ✅ |

## 📞 추가 정보

- 원본 README: `bokjiro_scraper/README.md`
- ~~초기화 스크립트: `fresh_start.py`~~ (v2.0에서 통합됨)

---

**업그레이드 완료! 🎉**

이제 Auto Scraper와 동일한 편리한 옵션을 제공합니다!

문제가 발생하면 `bokjiro_scraper/data/logs/debug_log.txt` 파일을 확인하세요.
