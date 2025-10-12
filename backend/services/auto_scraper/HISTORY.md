# 📜 개발 히스토리

## 타임라인 요약

```
ver1.1 (초기) → ver1.2 (안정화) → ver1.3 (학습 시스템) → ver1.3.1 (학습 버그 수정)
→ ver1.3.2 (비PDF 필터링) → ver1.4 (성능 최적화) → ver1.4.1 (탭 필터링)
→ ver1.4.2 (동적 스크립트) → **ver1.4.1-final (LH 사이트 대응 완성)**
```

---

## 📅 2025-10-02: ver1.4.1-final 🎯

### 🎉 최종 완성 버전

**목표:** SH와 LH 두 공공기관 사이트 모두 완벽 지원

### 핵심 수정사항

#### 1. LH 사이트 게시글 추출 문제 해결
**문제:**
- LH 사이트의 `.wrtancInfoBtn` 클래스 링크가 추출 안됨
- 50개 링크 감지 → 1개만 추출되는 버그
- onclick 없고 `href="javascript:"` 형태라 기존 로직으로 스킵됨

**해결:**
```python
# auto_scraper.py:297-307
# LH 전용 게시글 링크 수집 로직 추가
element_class = (element.get_attribute('class') or '').lower()
if 'wrtancinfobtn' in element_class:
    article_links.append({
        'url': None,
        'title': text,
        'element': element,
        'is_javascript': True
    })
    debug_log(f"LH JavaScript 링크 추가: {text[:50]}", 'VERBOSE')
    continue
```

#### 2. ver1.4 PDF 추출 로직 복원
**문제:**
- ver1.4.1의 복잡한 검증 로직이 SH 사이트 PDF 인식 실패
- `is_pdf_file_only()`, `contains_personal_info()` 등 불필요한 검증

**해결:**
- ver1.4의 단순하고 안정적인 `extract_filename_from_strategy()` 로직 복원
- 순서: URL → 텍스트 → onclick → Fallback
- 비PDF 확장자만 간단히 필터링

#### 3. 자동 모드 지원
**추가:**
- 커맨드라인 인자로 URL 전달 가능
- 백그라운드 실행 지원
- 사용자 입력 없이 자동 실행

```bash
# 사용 예시
python auto_scraper.py "https://apply.lh.or.kr/..."
```

#### 4. UTF-8 인코딩 설정
**추가:**
```python
# Windows 콘솔 이모지 출력 지원
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

### 테스트 결과
- ✅ **SH 사이트**: PDF 정상 인식 및 다운로드
- ✅ **LH 사이트**: 게시글 50+ 추출, PDF 정상 인식
- ✅ **기존 사이트**: 모두 정상 작동

### 수정 파일
- `auto_scraper.py`: LH 링크 수집 + 자동 모드 + UTF-8
- `pdf_detector.py`: ver1.4 로직 복원
- `config.py`: 디버그 레벨 VERBOSE

---

## 🔍 SH vs LH 사이트 구조 차이 및 해결 과정

### HTML 구조 비교

| 구분 | SH 사이트 | LH 사이트 |
|------|----------|----------|
| **URL** | `i-sh.co.kr` | `apply.lh.or.kr` |
| **게시글 링크** | 일반 `<a>` 태그 | `<a class="wrtancInfoBtn">` |
| **href 속성** | `href="view.do?id=123"` | `href="javascript:"` |
| **onclick 속성** | ❌ 없음 | ❌ 없음 |
| **PDF 링크** | `<a href="download.php?id=123">공고문.pdf</a>` | `<a href="lhFile.do?id=xxx">입주자모집.pdf</a>` |
| **PDF URL 확장자** | `.php` (동적 스크립트) | `.do` (동적 스크립트) |

### 문제점 분석

#### 문제 1: LH 게시글 추출 실패

| 단계 | 기존 로직 | LH 링크 | 결과 |
|------|----------|---------|------|
| **1. onclick 체크** | `if onclick and 'view' in onclick:` | onclick 없음 | ❌ 스킵 |
| **2. URL 체크** | `if 'view' in href or 'no=' in href:` | `href="javascript:"` | ❌ 스킵 |
| **결과** | - | - | **❌ 게시글 미추출** |

**왜 안 됐나:**
- LH 링크는 onclick도 없고, href도 `javascript:`라서 두 조건 모두 만족 못함
- 50개 감지되지만 검증 통과 못해서 1개만 추출

#### 문제 2: SH PDF 인식 실패

| 단계 | ver1.4 로직 | ver1.4.1 로직 | SH PDF | 결과 |
|------|------------|--------------|--------|------|
| **1. URL 확인** | URL에서 파일명 추출 시도 | `is_pdf_file_only()` 검증 | `download.php` | ver1.4: ✅ 스킵, ver1.4.1: ❌ 차단 |
| **2. 텍스트 확인** | 텍스트에서 PDF 패턴 검색 | 복잡한 개인정보 필터링 | `공고문.pdf` | ver1.4: ✅ 성공, ver1.4.1: ❌ 도달 못함 |
| **결과** | **✅ PDF 인식** | **❌ PDF 없음** | - | ver1.4 승리 |

**왜 안 됐나:**
- ver1.4.1은 URL부터 확인하는데, `download.php`를 차단 대상으로 판단
- 텍스트 확인 로직까지 도달하지 못함
- 복잡한 검증 로직이 오히려 방해

### 해결 방법 비교

#### 해결 1: LH 게시글 추출

**Before (ver1.4.1):**
```python
# 링크 검증 로직
if onclick and 'view' in onclick:
    article_links.append(...)  # onclick 있는 것만
elif href and 'view' in href:
    article_links.append(...)  # URL 패턴 맞는 것만

# LH 링크: onclick도 없고 href도 javascript: → 둘 다 스킵!
```

**After (ver1.4.1-final):**
```python
# 링크 검증 로직
if is_valid_article_link(element, text):  # 검증 통과 ✅

    # 🆕 LH 전용 처리 (onclick/href 체크 전에 먼저!)
    element_class = (element.get_attribute('class') or '').lower()
    if 'wrtancinfobtn' in element_class:
        article_links.append({...})  # ✅ 추가!
        continue

    # 기존 onclick/href 체크
    if onclick and 'view' in onclick:
        article_links.append(...)
    elif href and 'view' in href:
        article_links.append(...)
```

**핵심:**
- `.wrtancInfoBtn` 클래스를 직접 감지
- onclick/href 체크 **전에** 먼저 처리
- 50개 모두 정상 추출!

#### 해결 2: SH PDF 인식

**Before (ver1.4.1):**
```python
def extract_filename_from_strategy(strategy):
    # 1. URL 확인
    if 'url' in strategy:
        if is_pdf_file_only(url):  # download.php → ❌ 차단!
            return filename
        else:
            return None  # 여기서 종료! 텍스트 확인 안 함!

    # 2. 텍스트 확인 (도달 못함!)
    if 'text' in strategy:
        return extract_from_text(text)
```

**After (ver1.4.1-final - ver1.4 복원):**
```python
def extract_filename_from_strategy(strategy):
    non_pdf_extensions = ['.xlsx', '.xls', '.doc', ...]

    # 1. URL 확인 (단순 필터링만)
    if 'url' in strategy:
        if any(ext in url for ext in non_pdf_extensions):
            return None  # 확실한 비PDF만 차단
        filename = extract_filename_from_url(url)
        if filename:
            return filename  # ✅ 성공하면 반환
        # ✅ 실패해도 계속 진행!

    # 2. 텍스트 확인 (URL 실패해도 시도!)
    if 'text' in strategy:
        patterns = [r'([\w가-힣\s\-_\.]+\.pdf)', ...]
        match = re.search(pattern, text)
        if match:
            return match.group(1)  # ✅ "공고문.pdf" 성공!
```

**핵심:**
- 복잡한 검증 제거, 단순하게!
- URL 실패해도 텍스트 계속 확인
- `download.php` 스킵하고 텍스트에서 `공고문.pdf` 찾음!

### 최종 비교표

| 사이트 | ver1.4 | ver1.4.1 | ver1.4.1-final | 해결 방법 |
|--------|--------|----------|----------------|----------|
| **SH** | ✅ 성공 | ❌ 실패 (PDF 미인식) | ✅ 성공 | ver1.4 로직 복원 |
| **LH** | ❌ 실패 (게시글 미추출) | ❌ 실패 (게시글 미추출) | ✅ 성공 | `.wrtancInfoBtn` 특별 처리 |
| **복지로** | ✅ 성공 | ✅ 성공 | ✅ 성공 | - |

### 핵심 교훈

1. **단순함이 승리한다**
   - ver1.4.1의 복잡한 검증 로직이 오히려 SH 사이트를 망침
   - ver1.4의 단순한 로직이 더 안정적

2. **사이트별 특성 파악이 중요하다**
   - LH는 `.wrtancInfoBtn`이라는 특별한 클래스 사용
   - 이를 직접 감지하는 로직 추가로 해결

3. **Fallback이 중요하다**
   - URL 실패해도 텍스트, onclick 계속 시도
   - 한 방법이 안 되면 다음 방법으로

4. **성급한 최적화는 독이다**
   - ver1.4.1의 "개인정보 보호" 검증이 오히려 정상 PDF 차단
   - 필요한 것만 검증하고, 나머지는 단순하게

---

## 📅 2025-10-02: ver1.4.2 (계획)

### 동적 스크립트 대응 (미적용)

**목표:** `.php`, `.do`, `.asp` 등 동적 스크립트 URL 처리

**기술적 개선:**
- 파일명 추출 우선순위 변경: 텍스트 → onclick → URL
- 동적 스크립트 확장자 목록 추가
- 3단계 Fallback 시스템

**Note:** ver1.4.1-final에서는 ver1.4 로직 복원으로 해결되어 이 변경사항 미적용

---

## 📅 2025-10-02: ver1.4.1

### 🎯 탭/네비게이션 필터링 강화

**문제:**
- LH 사이트의 탭 메뉴(공고문, 임대가이드, 청약연습하기)가 게시글로 잘못 인식
- 불필요한 클릭으로 시간 낭비 및 학습 오류

**해결:**

#### 1. 탭/네비게이션 자동 감지
```python
def is_navigation_or_tab_element(element):
    # 클래스명 체크
    if 'tab' in class_attr or 'nav' in class_attr:
        return True
    # 텍스트 패턴 체크
    if any(pattern in text for pattern in ['공고문', '임대가이드', '청약연습']):
        return True
    # 부모 요소 체크
    # Y좌표 위치 기반 필터
```

#### 2. 게시글 링크 품질 검증
```python
def is_valid_article_link(element, text):
    # 텍스트 길이: 최소 8자
    # URL 패턴: no=, idx=, seq=, id= 등
    # onclick 패턴: view, detail, show 등
    # 테이블 구조: <tr> 내 3개 이상 <td>
```

#### 3. 필터링 통계 로깅
```python
filtered_count = {
    'tab': 0,
    'invalid': 0,
    'safe': 0,
    'text_length': 0,
    'exclude_pattern': 0
}
```

### 기대 효과
- ✅ 학습 정확도 향상 (실제 게시글만 학습)
- ✅ 성능 개선 (불필요한 클릭 제거)
- ✅ 안정성 향상 (페이징/네비 오인식 차단)

---

## 📅 2025-10-01: ver1.3.2

### 🎯 비PDF 파일 필터링 강화 (SH 사이트 성공!)

**문제:**
- 첨부파일 섹션에 엑셀(`.xlsx`), 워드(`.doc`) 등이 섞여 있을 때
- 중간에 비PDF 파일 때문에 실패가 누적
- 5번째 PDF부터 다운로드 안됨

**해결:**

#### 1. 첨부파일 탐지 강화
```python
# href 또는 text에 .pdf 포함된 링크 모두 탐지
pdf_links = section.find_elements(By.XPATH,
    ".//a[contains(@href, '.pdf') or contains(text(), '.pdf')]")

# 비PDF 확장자 자동 필터링
non_pdf_extensions = ['.xlsx', '.xls', '.doc', '.docx', '.hwp', '.zip', ...]
```

#### 2. 중복 제거 로직 개선 (핵심!)
**Before:**
```python
# URL을 우선 식별자로 사용 → 같은 URL이면 중복 스킵 → 다중 PDF 누락!
if 'url' in strategy:
    identifier = strategy['url']
elif 'text' in strategy:
    identifier = strategy['text']
```

**After:**
```python
# 파일명(text)을 우선 식별자로 사용 → 파일명 다르면 별도 파일로 인식
if 'text' in strategy and strategy['text']:
    identifier = strategy['text'].strip()  # 파일명 우선! ✅
elif 'url' in strategy:
    identifier = strategy['url']
```

#### 3. 학습 시스템 개선
- 비PDF 파일은 전략 실패로 기록하지 않음
- 엑셀/워드 때문에 전략이 스킵되는 문제 해결

### 효과
- ✅ 엑셀, 워드가 섞여도 PDF 정상 다운로드
- ✅ 같은 섹션에 여러 PDF 모두 다운로드
- ✅ **SH 사이트 완벽 작동!**

---

## 📅 2025-01-XX: ver1.3.1

### 🐛 학습 시스템 버그 수정 (치명적!)

**문제 1: 학습이 안 됨**

**증상:**
```
게시물 1: 6초 (느림)
게시물 2: 6초 (여전히 느림!) ❌
게시물 3: 6초 (계속 느림...) ❌
```

**원인:**
```python
# 잘못된 코드
board_url = article_url  # 게시물 URL을 그대로 사용

# 예시:
게시물 1: "https://bokjiro.go.kr/board/view?id=123"
게시물 2: "https://bokjiro.go.kr/board/view?id=124"  # 다른 키!
게시물 3: "https://bokjiro.go.kr/board/view?id=125"  # 또 다른 키!
```
→ 매번 다른 URL → 매번 새 게시판 인식 → 학습 안 됨!

**해결:**
```python
def extract_board_url(article_url):
    """게시물 URL → 게시판 기본 URL 추출"""
    # 쿼리 파라미터 제거 (id=, no=)
    # 게시물 상세 경로 제거 (view, detail)
    # 숫자 경로 제거 (게시물 ID)

# 수정된 코드
board_url = extract_board_url(article_url)  # ✅

# 예시:
게시물 1: "https://bokjiro.go.kr/board"
게시물 2: "https://bokjiro.go.kr/board"  # 같은 키! ✅
게시물 3: "https://bokjiro.go.kr/board"  # 계속 같은 키! ✅
```

**문제 2: 2번째 게시물부터 "PDF 없음"**

**원인:**
```python
# 잘못된 로직
if has_learned:
    # 학습된 전략만 실행 → PDF 후보 탐지 단계에서 필터링
    for strategy_type in learned_strategies:
        strategies = detector_func(driver)
```
→ 다른 전략의 PDF 후보가 탐지 안됨!

**해결:**
```python
# 항상 모든 전략으로 PDF 후보 탐지
all_strategies.extend(find_filename_links(driver))
all_strategies.extend(find_direct_pdf_links(driver))
# ... (모든 전략)

# 학습된 우선순위로 정렬
if has_learned:
    all_strategies = sort_strategies_by_learning(all_strategies, board_url)
```

**문제 3: 실패한 전략을 계속 재시도**

**해결:**
- 성공/실패 모두 기록
- 연속 5회 실패 시 자동 스킵

### 효과
- ✅ 게시물 2부터 **75% 빠름** (6초 → 1초)
- ✅ 올바른 학습 누적
- ✅ 2번째 게시물부터 정상 작동

### 새 기능
- 3단계 초기화 옵션
- 데이터 현황 대시보드
- 학습 통계 조회

---

## 📅 2025-01-XX: ver1.3

### 🎯 전략 학습 시스템 구현

**핵심 신기능:**
- 게시판 URL별로 성공한 PDF 탐지 전략 자동 학습
- 신뢰도 점수 기반 동적 우선순위 조정
- 연속 5회 실패 전략 자동 스킵

**성능:**
```
게시물 1: 모든 전략 시도 (5-7초) → 학습
게시물 2-100: 학습된 전략만 시도 (1초) → 5배 빠름!
```

**학습 데이터:**
```json
{
  "https://bokjiro.go.kr/board": {
    "filename_link": {"success": 10, "fail": 0, "score": 1.0},
    "direct_link": {"success": 0, "fail": 5, "score": 0.0}
  }
}
```

**새 파일:**
- `data/logs/learned_strategies.json`

**새 함수:**
- `load_learned_strategies()`
- `save_learned_strategies()`
- `calculate_strategy_score()`
- `update_strategy_stats()`

---

## 📅 2025-01-XX: ver1.2

### 🛡️ 안정화 버전

**목표:** ver1.1의 불안정 요소 제거

**변경사항:**
- ❌ `CACHE_BOARD_LINKS = False` (페이지 점프 문제)
- ❌ `TRACK_PROCESSED_ARTICLES = False` (DB 부하)
- ❌ `USE_BOARD_PATTERN_CACHE = False` (실효성 낮음)
- ✅ `BLOCK_IMAGES = True` (메모리 40-60% 절약)

**버그 수정:**
- 페이지 점프 문제 해결 (1→11 대신 1→2→3)
- 메모리 사용량 증가 문제 해결

---

## 📅 2025-01-XX: ver1.1

### ✨ 초기 버전

**7가지 PDF 탐지 전략:**
1. 파일명 직접 링크
2. 직접 PDF 링크 (`<a href="*.pdf">`)
3. 임베디드 PDF (iframe/embed)
4. 첨부파일 섹션
5. 다운로드 버튼
6. JavaScript 핸들러
7. 미리보기-다운로드 쌍

**기본 기능:**
- 다중 PDF 다운로드
- SHA256 해시 기반 중복 체크
- SQLite DB 이력 관리
- 자동 페이지네이션
- 체크포인트 (중단 후 재개)
- 브라우저 주기적 재시작

**특징:**
- 안정성 높음 (검증된 기본 로직)
- 속도 느림 (모든 전략 매번 시도)
- 메모리 많이 사용 (이미지 로딩)

---

## 🎯 주요 버그 수정 요약

| 버전 | 버그 | 해결 |
|------|------|------|
| ver1.3.1 | 학습 안 됨 | 게시판 URL 추출 |
| ver1.3.1 | 2번째부터 PDF 없음 | 전략 필터링 로직 수정 |
| ver1.3.2 | 다중 PDF 누락 | 중복 제거 로직 개선 |
| ver1.4.1 | LH 탭 오인식 | 탭/네비 필터링 |
| ver1.4.1-final | LH 게시글 미추출 | `.wrtancInfoBtn` 특별 처리 |
| ver1.4.1-final | SH PDF 미인식 | ver1.4 로직 복원 |

---

## 🚀 성능 변화

| 버전 | 평균 처리 시간 | 메모리 사용 | 학습 기능 |
|------|---------------|-----------|----------|
| ver1.1 | 6초/게시물 | 높음 | ❌ |
| ver1.2 | 6초/게시물 | 중간 (40-60% ↓) | ❌ |
| ver1.3 | 1초/게시물 (2번째부터) | 중간 | ✅ (버그) |
| ver1.3.1 | 1초/게시물 (2번째부터) | 중간 | ✅ (수정) |
| ver1.3.2 | 1초/게시물 | 중간 | ✅ |
| ver1.4 | 1초/게시물 | 낮음 | ✅ |
| ver1.4.1 | 1초/게시물 | 낮음 | ✅ |
| **ver1.4.1-final** | **1초/게시물** | **낮음** | **✅** |

---

## 📊 지원 사이트 변화

| 버전 | SH | LH | 복지로 | 일반 웹 |
|------|----|----|--------|---------|
| ver1.1-1.4 | ❌ | ❌ | ✅ | ✅ |
| ver1.4.1 | ❌ | ❌ | ✅ | ✅ |
| **ver1.4.1-final** | **✅** | **✅** | **✅** | **✅** |

---

**마지막 업데이트: 2025-10-02**
**최종 버전: ver1.4.1-final**
**상태: ✅ 안정 & 완성**
