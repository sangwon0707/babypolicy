# 범용 PDF 자동 스크래퍼 ver1.4.1-final

공공기관 게시판에서 PDF 파일을 자동으로 탐지하고 다운로드하는 Python 프로그램

lh 사이트 = https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancList.do?mi=1026
sh 사이트 = https://www.i-sh.co.kr/app/lay2/program/S48T561C563/www/brd/m_247/list.do?multi_itm_seq=2

## 주요 특징

- ✅ **SH, LH 공공기관 사이트 완벽 지원**
- ✅ **AI 전략 학습 시스템** - 게시판별로 학습하여 2번째부터 5배 빠름
- ✅ **7가지 PDF 탐지 전략** - 다양한 게시판 구조 대응
- ✅ **자동 페이지네이션** - 여러 페이지 자동 처리
- ✅ **중단 후 재개** - 체크포인트 기능으로 언제든 재시작
- ✅ **중복 방지** - SHA256 해시 기반 중복 체크

---

## 설치

### 1. 필수 라이브러리 설치

```bash
pip install selenium webdriver-manager
```

### 2. Chrome 브라우저 설치

프로그램이 자동으로 ChromeDriver를 설치합니다.

---

## 사용 방법

### 기본 실행

```bash
python auto_scraper.py
```

### 자동 모드 (커맨드라인 인자)

```bash
python auto_scraper.py "https://apply.lh.or.kr/lhapply/..."
```

### 실행 흐름

1. **초기화 옵션 선택** (기존 데이터가 있는 경우)
   - `1`: 학습 데이터만 초기화 (PDF 파일 유지)
   - `2`: 완전 초기화 (모든 데이터 삭제)
   - `3`: 초기화 안 함 (기존 데이터 사용)

2. **게시판 URL 입력**
   ```
   예시:
   SH: https://www.i-sh.co.kr/main/notice/noticeList.do
   LH: https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancList.do?mi=1026
   복지로: https://www.bokjiro.go.kr/...
   ```

3. **다운로드 폴더 경로 지정** (선택)
   - 기본값: `data/downloads/`
   - 엔터키: 기본값 사용

4. **자동 실행**
   - 게시글 링크 추출
   - PDF 탐지 및 다운로드
   - 다음 페이지로 자동 이동

---

## 지원 사이트

| 사이트 | URL 예시 | 지원 여부 |
|--------|---------|----------|
| **SH (서울주택도시공사)** | `i-sh.co.kr` | ✅ |
| **LH (한국토지주택공사)** | `apply.lh.or.kr` | ✅ |
| **복지로** | `bokjiro.go.kr` | ✅ |
| **일반 게시판** | - | ✅ |

### 동작 메커니즘

#### SH 사이트
```html
<a href="download.php?id=123">공고문.pdf</a>
```
→ 텍스트에서 "공고문.pdf" 추출 ✅

#### LH 사이트
```html
<a href="javascript:" class="wrtancInfoBtn">입주자모집공고.pdf</a>
```
→ `.wrtancInfoBtn` 클래스 특별 처리 ✅

---

## 주요 기능

### 1. 전략 학습 시스템

게시판별로 성공한 PDF 탐지 전략을 자동 학습하여 성능을 최적화합니다.

```
게시물 1: 모든 전략 시도 (6초) → 학습
게시물 2-100: 학습된 전략만 시도 (1초) → 5배 빠름!
```

**학습 데이터 위치:** `data/logs/learned_strategies.json`

### 2. 7가지 PDF 탐지 전략

1. **파일명 직접 링크** - 링크 텍스트에 `.pdf` 포함
2. **직접 PDF 링크** - `<a href="*.pdf">`
3. **임베디드 PDF** - `<iframe>`, `<embed>` 태그
4. **첨부파일 섹션** - "첨부파일" 섹션 내 PDF
5. **다운로드 버튼** - "다운로드" 버튼 클릭
6. **JavaScript 핸들러** - onclick 이벤트
7. **미리보기-다운로드 쌍** - 미리보기 버튼과 연결

### 3. 자동 페이지네이션

- 페이지 번호 버튼 자동 감지
- "다음" 버튼 자동 클릭
- 마지막 페이지까지 자동 처리

### 4. 체크포인트 기능

프로그램 중단 시 자동 저장:
- 현재 페이지 번호
- 현재 게시글 인덱스
- 다운로드 개수

재실행 시 이어서 진행 가능합니다.

### 5. 중복 방지

- **파일명 기반** - 같은 파일명은 다운로드 안 함
- **SHA256 해시 기반** - 파일 내용이 같으면 다운로드 안 함
- **이력 관리** - `data/logs/download_log.json`에 기록

---

## 설정 (config.py)

### 주요 설정

```python
# 전략 학습 시스템
USE_STRATEGY_LEARNING = True          # 학습 활성화

# 다운로드 설정
DOWNLOAD_ALL_PDFS = True               # 게시물당 모든 PDF 다운로드
MAX_PDFS_PER_ARTICLE = 10              # 게시물당 최대 PDF 개수

# 타임아웃 설정 (초)
TIMEOUT = {
    'page_load': 20,                   # 페이지 로딩 대기
    'element_wait': 10,                # 요소 대기
    'download_wait': 30,               # 다운로드 대기
    'page_stable': 5                   # 페이지 안정화 대기
}

# 브라우저 설정
HEADLESS_MODE = False                  # GUI 없이 실행
BLOCK_IMAGES = True                    # 이미지 로딩 차단 (메모리 절약)
BROWSER_RESTART_INTERVAL = 50          # N개 게시글마다 브라우저 재시작

# 디버그 레벨
CURRENT_DEBUG_LEVEL = DEBUG_LEVELS['INFO']  # ERROR, WARNING, INFO, DEBUG, VERBOSE
```

---

## 폴더 구조

```
auto_scraper-ver1.4.1-final/
├── auto_scraper.py           # 메인 프로그램
├── pdf_detector.py           # PDF 탐지 엔진
├── utils.py                  # 유틸리티 함수
├── config.py                 # 설정 파일
├── database.py               # 데이터베이스 (선택)
├── README.md                 # 이 파일
├── HISTORY.md                # 개발 히스토리
└── data/
    ├── downloads/            # PDF 다운로드 폴더
    └── logs/                 # 로그 및 학습 데이터
        ├── learned_strategies.json  # 전략 학습 데이터
        ├── download_log.json        # 다운로드 이력
        ├── failed_log.json          # 실패 이력
        ├── checkpoint.json          # 체크포인트
        └── debug_log.txt            # 디버그 로그
```

---

## 문제 해결

### Q1. "PDF 파일 없음"이라고 나와요

**A:** 다음을 확인하세요:
1. 게시글에 실제 PDF가 있는지 확인
2. `config.py`의 `CURRENT_DEBUG_LEVEL`을 `DEBUG`로 변경
3. `debug_log.txt` 파일에서 상세 로그 확인

### Q2. 브라우저가 자동으로 닫혀요

**A:** 이는 정상입니다. 50개 게시글마다 메모리 절약을 위해 브라우저를 재시작합니다.
- `config.py`의 `BROWSER_RESTART_INTERVAL` 값을 조정할 수 있습니다.

### Q3. 특정 사이트에서 작동하지 않아요

**A:**
1. 해당 사이트의 게시판 구조가 특이한 경우일 수 있습니다.
2. 디버그 로그를 확인하여 어느 단계에서 실패하는지 파악하세요.
3. 이슈를 제보해주시면 지원을 추가하겠습니다.

### Q4. 속도가 느려요

**A:**
1. 첫 게시글은 학습을 위해 느립니다 (정상)
2. 2번째부터는 빨라집니다
3. `config.py`의 `BLOCK_IMAGES = True`인지 확인 (메모리 절약)

### Q5. 학습 데이터를 초기화하고 싶어요

**A:** 프로그램 실행 시 초기화 옵션에서 선택하거나, 직접 삭제:
```bash
rm data/logs/learned_strategies.json
```

---

## 고급 기능

### 1. 데이터 관리

프로그램 실행 시 데이터 현황 대시보드가 표시됩니다:
```
📊 현재 데이터 현황:
   📚 학습된 게시판: 3개
   📄 다운로드된 PDF: 50개
   📝 로그 크기: 42.9 KB
   💾 체크포인트: 있음
```

### 2. 로그 레벨

```python
# config.py
DEBUG_LEVELS = {
    'ERROR': 0,      # 오류만
    'WARNING': 1,    # 경고 이상
    'INFO': 2,       # 정보 이상 (기본값)
    'DEBUG': 3,      # 디버그 이상
    'VERBOSE': 4     # 모든 로그
}

CURRENT_DEBUG_LEVEL = DEBUG_LEVELS['INFO']
```

### 3. 자동 모드 활용

```bash
# 여러 사이트를 순차적으로 실행
python auto_scraper.py "https://site1.com/board"
python auto_scraper.py "https://site2.com/board"
python auto_scraper.py "https://site3.com/board"
```

---

## 성능

| 항목 | 값 |
|------|-----|
| **평균 처리 시간** | 1초/게시물 (2번째부터) |
| **메모리 사용** | 낮음 (이미지 차단) |
| **학습 효과** | 5배 속도 향상 |
| **성공률** | 90%+ (지원 사이트) |

---

## 개발 정보

- **버전**: 1.4.1-final
- **날짜**: 2025-10-02
- **Python**: 3.7+
- **라이브러리**: Selenium, webdriver-manager

### 버전 히스토리

상세한 개발 히스토리는 `HISTORY.md`를 참고하세요.

---

## 라이선스

이 프로그램은 교육 및 연구 목적으로 제공됩니다.

---

## 기여

버그 리포트나 기능 제안은 환영합니다!

---

**마지막 업데이트: 2025-10-02**
