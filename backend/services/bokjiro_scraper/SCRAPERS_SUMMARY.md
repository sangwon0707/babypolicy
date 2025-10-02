# 스크래퍼 설치 및 사용 가이드

## ✅ 설치된 스크래퍼 목록

### 1. **Auto Scraper** (범용 PDF 스크래퍼 v1.4.1)
- 📁 위치: `services/auto_scraper/`
- ▶️ 실행: `run_scraper.bat` (더블클릭)
- 🎯 기능: 모든 게시판에서 PDF 자동 다운로드
- ✨ 특징: AI 학습 시스템, 개인정보 보호, 다중 전략

### 2. **Bokjiro Scraper** (복지로 전용 스크래퍼 v2.0) 🆕
- 📁 위치: `services/bokjiro_scraper/`
- ▶️ 실행: `run_bokjiro.bat` (더블클릭)
- 🎯 기능: 복지로 사이트 PDF 자동 다운로드
- ✨ **v2.0 업데이트**: Auto Scraper와 동일한 옵션 제공!

---

## 🎉 v2.0 업데이트 완료!

**Bokjiro Scraper가 Auto Scraper와 동일한 기능을 제공합니다:**

### ✅ 동일한 옵션
1. **데이터 통계 표시**
   - PDF 개수
   - 로그 크기
   - 체크포인트 상태

2. **3가지 초기화 옵션**
   - 옵션 1: 로그만 삭제 (PDF 유지)
   - 옵션 2: 완전 초기화 (PDF + 로그 모두 삭제)
   - 옵션 3: 초기화 안 함

3. **다운로드 디렉토리 선택**
   - 기본 경로 사용 또는
   - 사용자 지정 경로 입력

4. **체크포인트 재개**
   - 중단 지점부터 이어서 실행
   - 상세 정보 표시

5. **~~fresh_start.py 통합~~**
   - 별도 파일 불필요
   - 메인 프로그램에 모든 기능 통합

---

## 📁 최종 폴더 구조

```
backend/services/
│
├── auto_scraper/                    # 범용 PDF 스크래퍼
│   ├── auto_scraper.py              ⭐ 메인 실행 파일
│   ├── config.py
│   ├── database.py
│   ├── pdf_detector.py
│   ├── utils.py
│   └── data/
│       ├── downloads/
│       └── logs/
│
├── bokjiro_scraper/                 # 복지로 전용 스크래퍼
│   ├── bokjiro_scraper.py           ⭐ 메인 실행 파일 (v2.0)
│   ├── requirements.txt
│   └── data/
│       ├── pdfs/bokjiro/
│       └── logs/
│
├── run_auto_scraper.py              ⭐ Auto Scraper 실행 래퍼
├── run_scraper.bat                  ⭐ Auto Scraper 배치 파일
│
├── run_bokjiro_scraper.py           ⭐ Bokjiro Scraper 실행 래퍼
├── run_bokjiro.bat                  ⭐ Bokjiro Scraper 배치 파일
│
└── BOKJIRO_SCRAPER_README.md        📄 상세 가이드
```

---

## 🚀 실행 방법 (둘 다 동일)

### Auto Scraper
```
services/run_scraper.bat 더블클릭
```

### Bokjiro Scraper
```
services/run_bokjiro.bat 더블클릭
```

---

## 💡 바탕화면 바로가기 만들기

### 1. Auto Scraper
1. `run_scraper.bat` 우클릭
2. "바로 가기 만들기"
3. 바탕화면으로 이동
4. 이름: **"범용 PDF 스크래퍼"**

### 2. Bokjiro Scraper
1. `run_bokjiro.bat` 우클릭
2. "바로 가기 만들기"
3. 바탕화면으로 이동
4. 이름: **"복지로 PDF 다운로더"**

**이제 바탕화면에서 더블클릭으로 실행! 🎉**

---

## 📊 실행 시 옵션 선택 (둘 다 동일)

### 1단계: 데이터 통계 확인
```
📊 현재 데이터 현황:
   📄 다운로드된 PDF: 42개
   📝 로그 크기: 125.3 KB
   💾 체크포인트: 있음
```

### 2단계: 초기화 옵션
```
🔄 초기화 옵션:
   1. 데이터 초기화 (로그만 삭제, PDF 유지)
   2. 완전 초기화 (PDF + 로그 모두 삭제)
   3. 초기화 안 함 (기존 데이터 사용)

선택 [1/2/3]:
```

### 3단계: 체크포인트 재개
```
💾 이전 작업을 발견했습니다:
   마지막 페이지: 5
   마지막 정책: 3번째

🔄 이어서 진행하시겠습니까? [y/n]:
```

### 4단계: 다운로드 폴더 선택
```
📂 다운로드 폴더 경로
   기본값: C:\...\data\pdfs\...
   다른 경로 입력 (엔터키: 기본값 사용):
```

### 5단계: 실행 시작
```
엔터키를 누르면 스크래핑을 시작합니다...
```

---

## 🔍 스크래퍼 비교표

| 항목 | Auto Scraper | Bokjiro Scraper v2.0 |
|------|--------------|---------------------|
| **대상 사이트** | 모든 게시판 | 복지로 전용 |
| **데이터 통계** | ✅ | ✅ (v2.0) |
| **초기화 옵션** | ✅ 3가지 | ✅ 3가지 (v2.0) |
| **폴더 선택** | ✅ | ✅ (v2.0) |
| **체크포인트** | ✅ | ✅ (v2.0) |
| **학습 기능** | ✅ AI 학습 | ❌ |
| **개인정보 보호** | ✅ 강화 | ⚠️ 기본 |
| **사용 편의성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **별도 초기화 스크립트** | ❌ (통합됨) | ❌ (v2.0에서 통합) |

---

## 🎯 사용 시나리오

### Auto Scraper를 사용하세요:
- ✅ 다양한 게시판에서 PDF를 수집할 때
- ✅ 게시판 구조가 복잡하거나 JavaScript 링크가 많을 때
- ✅ 여러 사이트를 순회하며 수집할 때
- ✅ AI 학습 기능이 필요할 때
- ✅ 개인정보 보호가 중요할 때

### Bokjiro Scraper를 사용하세요:
- ✅ 복지로 사이트만 사용할 때
- ✅ 빠르고 간단하게 시작하고 싶을 때
- ✅ 복지로 사이트 구조에 최적화된 성능을 원할 때
- ✅ 안정적인 스크래핑이 필요할 때

---

## 📦 필수 패키지 설치

### Auto Scraper
```bash
cd auto_scraper
pip install -r requirements.txt
```

### Bokjiro Scraper
```bash
cd bokjiro_scraper
pip install -r requirements.txt
```

---

## 🛠️ 문제 해결

### Chrome Driver 오류
```bash
pip install --upgrade webdriver-manager selenium
```

### 한글 깨짐
- `.bat` 배치 파일 사용 (자동 UTF-8 설정)

### 모듈 import 오류
- `run_*.py` 래퍼 스크립트 사용

---

## 📚 상세 문서

- **Bokjiro Scraper v2.0**: `BOKJIRO_SCRAPER_README.md`
- **Auto Scraper**: `auto_scraper/README.md`

---

## 🎉 업데이트 완료!

두 스크래퍼 모두 **동일한 사용자 경험**을 제공합니다!

1. ✅ 데이터 통계 표시
2. ✅ 3가지 초기화 옵션
3. ✅ 다운로드 폴더 선택
4. ✅ 체크포인트 재개
5. ✅ 바탕화면 바로가기로 실행

**바탕화면 바로가기를 만들어서 더블클릭으로 사용하세요!** 🚀
