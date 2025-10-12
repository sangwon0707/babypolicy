"""
범용 PDF 자동 스크래퍼 ver1.4.1 - 메인 프로그램

ver1.4.1 핵심 개선사항:
🔒 개인정보 보호 (정보통신망법 준수):
    - 이메일 주소 자동 수집 금지
    - 전화번호, 주민번호 등 개인정보 필터링
    - PDF 파일만 다운로드 (다른 파일 형식 차단)
    - 로그에 개인정보 자동 제거

🎯 탭/네비게이션 필터링:
    - 탭 메뉴(공고문, 임대가이드 등) 자동 필터링
    - 페이징/네비게이션 요소 제외
    - 게시글 품질 검증 강화 (URL 패턴, 텍스트 길이, 테이블 구조)
    - 필터링 통계 로깅 추가

ver1.4 핵심 개선사항:
🎯 안정성 강화:
    - 게시판 URL 추출 로직 개선 (간단하고 안정적)
    - 중복 제거 로직 수정 (URL + 텍스트 해시 조합)
    - 연속 에러 복구 강화 (5회 실패 시 사용자 확인)
    - 타임아웃 최적화 (불필요한 대기 시간 단축)

⚡ 성능 개선:
    - 페이지 단위 학습 로직 (첫 게시글에서 학습 → 나머지 빠른 모드)
    - 빠른 모드: 학습된 전략만 시도 → 실패 시 전체 탐지로 폴백
    - 실시간 진행 로그 (타임스탬프 포함)

ver1.3 기능 유지:
    - 전략 패턴 학습 시스템
    - 게시판 URL별 전략 성공률 추적
    - 이미지 차단 메모리 절약

사용법:
    python auto_scraper.py
"""

import os
import sys
import io
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Windows 콘솔 UTF-8 인코딩 설정 (이모지 출력 지원)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from config import *
from utils import *
from pdf_detector import (
    auto_detect_and_download_all,
    auto_detect_and_download_fast,  # ver1.4: 빠른 모드
    analyze_page_structure,
    save_learned_strategies,  # ver1.3: 학습 데이터 저장
    reset_learned_strategies,  # ver1.3.1: 학습 데이터 초기화
    get_learned_strategies_stats  # ver1.3.1: 학습 통계 조회
)

# ver1.2: DB 사용
if USE_DATABASE:
    try:
        from database import (
            get_download_stats, migrate_from_json,
            is_article_processed, mark_article_processed,
            cleanup_old_processed_articles, save_board_pattern,
            get_board_pattern
        )
    except ImportError:
        debug_log("database.py를 찾을 수 없습니다.", 'WARNING')
        USE_DATABASE = False


# ============================================
# 게시판 링크 추출 (ver1.1 안정적 방식)
# ============================================

def is_navigation_or_tab_element(element):
    """
    ver1.4.1: 탭 메뉴나 네비게이션 요소 필터링

    Args:
        element: WebElement 객체

    Returns:
        bool: True면 탭/네비게이션 요소 (제외), False면 게시글 링크
    """
    try:
        # 1. 클래스명 체크
        class_name = element.get_attribute('class') or ''
        class_lower = class_name.lower()

        # 탭/네비게이션 클래스 패턴
        nav_class_patterns = [
            'tab', 'nav', 'menu', 'header', 'gnb', 'lnb',
            'breadcrumb', 'pagination', 'paging', 'pageindexer'
        ]

        if any(pattern in class_lower for pattern in nav_class_patterns):
            debug_log(f"탭/네비게이션 제외 (클래스): {class_name}", 'VERBOSE')
            return True

        # 2. 텍스트 패턴 체크
        text = element.text.strip()

        # 탭 메뉴 텍스트 패턴 (한글/영문)
        tab_text_patterns = [
            '공고문', '임대가이드', '청약연습', '가이드', '연습',
            'tab', 'guide', 'practice', 'manual', 'tutorial',
            '이전', '다음', '처음', '마지막',  # 페이징
            'prev', 'next', 'first', 'last'
        ]

        text_lower = text.lower()
        if any(pattern in text_lower for pattern in tab_text_patterns):
            debug_log(f"탭 메뉴 제외 (텍스트): {text}", 'VERBOSE')
            return True

        # 3. 부모 요소 체크 (탭 컨테이너 안에 있는지)
        try:
            parent = element.find_element(By.XPATH, '..')
            parent_class = (parent.get_attribute('class') or '').lower()

            if any(pattern in parent_class for pattern in nav_class_patterns):
                debug_log(f"탭 컨테이너 내부 요소 제외: {text}", 'VERBOSE')
                return True
        except:
            pass

        # 4. 위치 기반 필터 (상단 고정 영역)
        try:
            # Y 좌표가 200px 이하이고 텍스트가 짧으면 상단 메뉴일 가능성
            location = element.location
            if location['y'] < 200 and len(text) < 15:
                # 추가 검증: href가 게시판 패턴이 아니면 탭으로 간주
                href = element.get_attribute('href') or ''
                is_board_pattern = any(pattern in href.lower() for pattern in BOARD_LINK_PATTERNS)

                if not is_board_pattern:
                    debug_log(f"상단 영역 제외: {text} (y={location['y']})", 'VERBOSE')
                    return True
        except:
            pass

        return False

    except Exception as e:
        debug_log(f"탭 필터링 오류", 'WARNING', e)
        return False  # 오류 시 게시글로 간주


def is_valid_article_link(element, text):
    """
    ver1.4.1: 게시글 링크 품질 검증
    ver1.4.2: LH 사이트 대응 추가

    Args:
        element: WebElement 객체
        text: 링크 텍스트

    Returns:
        bool: True면 유효한 게시글 링크
    """
    try:
        # 🆕 LH 사이트 전용: .wrtancInfoBtn 클래스는 무조건 통과
        element_class = (element.get_attribute('class') or '').lower()
        if 'wrtancinfobtn' in element_class:
            debug_log(f"LH 게시글 링크 감지: {text[:50]}", 'VERBOSE')
            return True

        # 1. 텍스트 길이 검증 (너무 짧으면 탭명일 가능성)
        if len(text) < 8:  # 최소 8자 이상
            debug_log(f"텍스트 너무 짧음 제외: {text}", 'VERBOSE')
            return False

        # 2. URL 패턴 검증
        href = element.get_attribute('href') or ''

        # 게시글 ID 파라미터 체크 (board_id, no, idx, seq 등)
        article_id_patterns = ['no=', 'idx=', 'seq=', 'id=', 'num=', 'board_id=', 'article']
        has_article_id = any(pattern in href.lower() for pattern in article_id_patterns)

        # onclick도 체크
        onclick = element.get_attribute('onclick') or ''
        has_onclick_article = any(pattern in onclick.lower() for pattern in ['view', 'detail', 'show'])

        if not (has_article_id or has_onclick_article):
            # href와 onclick 둘 다 게시글 패턴이 없으면 의심
            if href and href != '#':
                debug_log(f"게시글 패턴 없음 제외: {text[:30]}", 'VERBOSE')
                return False

        # 3. 게시글 특성 요소 확인 (날짜, 조회수 등이 포함된 행)
        try:
            # 부모 <tr>에서 <td> 개수 확인
            parent_tr = element.find_element(By.XPATH, './ancestor::tr[1]')
            tds = parent_tr.find_elements(By.TAG_NAME, 'td')

            # 일반적으로 게시판은 3개 이상의 td (번호, 제목, 날짜 등)
            if len(tds) >= 3:
                debug_log(f"게시판 행 구조 확인: {text[:30]} (td={len(tds)})", 'VERBOSE')
                return True
        except:
            pass

        # 4. 모든 검증 통과
        return True

    except Exception as e:
        debug_log(f"게시글 검증 오류", 'WARNING', e)
        return True  # 오류 시 게시글로 간주


def extract_board_links(driver):
    """
    게시판 페이지에서 게시글 링크 자동 추출
    ver1.4.1: 탭/네비게이션 필터링 강화

    Args:
        driver: WebDriver 객체

    Returns:
        list: [{"url": "...", "title": "...", "element": WebElement}, ...]
    """
    debug_log("게시글 링크 추출 시작 (ver1.4.1 - 탭 필터링 강화)", 'INFO')

    # ✅ 1. <a> 태그 검색
    all_links = driver.find_elements(By.TAG_NAME, "a")
    debug_log(f"<a> 태그 수: {len(all_links)}", 'DEBUG')

    # ✅ 2. onclick 속성이 있는 모든 요소 검색 (tr, div, span 등)
    all_onclick_elements = driver.find_elements(By.XPATH, "//*[@onclick]")
    debug_log(f"onclick 요소 수: {len(all_onclick_elements)}", 'DEBUG')

    # 합치기
    all_elements = all_links + all_onclick_elements
    debug_log(f"총 검사 대상: {len(all_elements)}개", 'DEBUG')

    article_links = []
    filtered_count = {'tab': 0, 'invalid': 0, 'safe': 0, 'text_length': 0, 'exclude_pattern': 0}

    for element in all_elements:
        try:
            href = element.get_attribute('href')
            onclick = element.get_attribute('onclick')
            tag_name = element.tag_name.lower()

            # ✅ 텍스트 추출 (요소 타입에 따라 다르게)
            if tag_name == 'tr':
                # <tr> 태그인 경우: td들에서 제목 찾기
                try:
                    tds = element.find_elements(By.TAG_NAME, 'td')
                    if len(tds) >= 2:
                        text = tds[1].text.strip()
                    else:
                        text = element.text.strip()
                except:
                    text = element.text.strip()
            else:
                text = element.text.strip()

            # 텍스트가 없으면 건너뛰기
            if not text:
                continue

            # 1. 안전성 검증
            if not is_safe_element(element):
                filtered_count['safe'] += 1
                continue

            # 2. ver1.4.1: 탭/네비게이션 필터링
            if is_navigation_or_tab_element(element):
                filtered_count['tab'] += 1
                continue

            # 3. ver1.4.1: 개인정보 보호 - 이메일 주소 포함 여부 체크
            if ENABLE_PRIVACY_PROTECTION and BLOCK_EMAIL_COLLECTION:
                has_personal, info_types = contains_personal_info(text)
                if has_personal:
                    debug_log(f"🔒 개인정보 포함 링크 제외: {sanitize_for_logging(text)}", 'WARNING')
                    filtered_count['exclude_pattern'] += 1
                    continue

            # 4. 텍스트 길이 필터
            if len(text) < MIN_LINK_TEXT_LENGTH or len(text) > MAX_LINK_TEXT_LENGTH:
                filtered_count['text_length'] += 1
                continue

            # 5. 제외 패턴 확인
            if any(exclude_text in text.lower() for exclude_text in EXCLUDE_LINK_TEXTS):
                filtered_count['exclude_pattern'] += 1
                continue

            # 6. ver1.4.1: 게시글 링크 품질 검증
            if not is_valid_article_link(element, text):
                filtered_count['invalid'] += 1
                continue

            # 🆕 LH 사이트 전용: .wrtancInfoBtn 클래스 처리
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

            # ✅ 6. JavaScript 링크 체크 (onclick 속성)
            if onclick:
                onclick_lower = onclick.lower()
                js_patterns = ['view', 'detail', 'show', 'read', 'open', 'go', 'move']

                if any(pattern in onclick_lower for pattern in js_patterns):
                    article_links.append({
                        'url': None,
                        'title': text,
                        'element': element,
                        'is_javascript': True
                    })
                    debug_log(f"JavaScript 링크 발견 ({tag_name}): {text[:50]} (onclick={onclick[:50]})", 'VERBOSE')
                    continue

            # 7. 일반 URL 링크 체크
            if href and href != '#':
                href_lower = href.lower()
                is_board_link = any(pattern in href_lower for pattern in BOARD_LINK_PATTERNS)

                if is_board_link:
                    article_links.append({
                        'url': href,
                        'title': text,
                        'element': element,
                        'is_javascript': False
                    })
                    debug_log(f"일반 링크 발견: {text[:50]}", 'VERBOSE')

        except Exception as e:
            debug_log(f"링크 분석 오류", 'WARNING', e)
            continue

    # 중복 제거
    unique_links = []
    seen_identifiers = set()

    for link in article_links:
        if link.get('is_javascript'):
            identifier = link['title']
        else:
            identifier = link['url']

        if identifier not in seen_identifiers:
            unique_links.append(link)
            seen_identifiers.add(identifier)

    # 통계 출력
    js_count = sum(1 for link in unique_links if link.get('is_javascript', False))
    url_count = len(unique_links) - js_count

    debug_log(f"🚫 필터링 통계: 탭={filtered_count['tab']}, 품질불량={filtered_count['invalid']}, "
              f"안전성={filtered_count['safe']}, 길이={filtered_count['text_length']}, "
              f"제외패턴={filtered_count['exclude_pattern']}", 'INFO')
    debug_log(f"✅ 총 {len(unique_links)}개 게시글 링크 추출 완료 (JavaScript: {js_count}개, 일반: {url_count}개)", 'INFO')

    return unique_links


# ============================================
# 게시글 처리
# ============================================

def process_article(driver, wait, link_info, download_dir):
    """
    게시글 상세 페이지 처리 (PDF 탐지 및 다운로드)

    Args:
        driver: WebDriver 객체
        wait: WebDriverWait 객체
        link_info: 게시글 정보 dict
        download_dir: 다운로드 폴더

    Returns:
        dict: {"status": "success/no_pdf/error", "downloads": [...], ...}
    """
    try:
        article_title = link_info.get('title', '제목없음')
        is_javascript = link_info.get('is_javascript', False)
        article_url = link_info.get('url')

        # ✅ JavaScript 링크 처리
        if is_javascript:
            element = link_info['element']
            debug_log(f"JavaScript 링크 클릭: {article_title[:50]}", 'DEBUG')

            try:
                element.click()
                debug_log("일반 클릭 성공", 'DEBUG')
            except Exception as click_error:
                debug_log(f"일반 클릭 실패, JavaScript 클릭 시도", 'DEBUG', click_error)
                driver.execute_script("arguments[0].click();", element)
                debug_log("JavaScript 클릭 성공", 'DEBUG')

            wait_for_page_stable(driver, timeout=TIMEOUT['page_load'])
            article_url = driver.current_url

        else:
            # ✅ 일반 URL 링크 처리
            if not article_url:
                raise Exception("게시글 URL이 없습니다")

            debug_log(f"게시글 URL 이동: {article_url}", 'DEBUG')
            driver.get(article_url)
            wait_for_page_stable(driver, timeout=TIMEOUT['page_load'])

        # 다중 PDF 탐지 및 다운로드
        result = auto_detect_and_download_all(
            driver=driver,
            wait=wait,
            download_dir=download_dir,
            article_title=article_title,
            article_url=article_url
        )

        # 결과에 게시글 정보 추가
        result['article_title'] = article_title
        result['article_url'] = article_url

        return result

    except Exception as e:
        debug_log(f"게시글 처리 오류", 'ERROR', e)
        return {
            'status': 'error',
            'message': str(e),
            'article_title': link_info.get('title', '제목없음'),
            'article_url': link_info.get('url', 'N/A'),
            'downloads': [],
            'skipped': []
        }


# ============================================
# 페이지네이션
# ============================================

def find_next_page_button(driver, current_page):
    """다음 페이지 버튼 찾기"""
    debug_log(f"다음 페이지 버튼 검색 중 (현재: {current_page})", 'DEBUG')

    try:
        next_page = current_page + 1

        # 방법 1: 페이지 번호 버튼 찾기 (1, 2, 3, ...)
        page_number_selectors = [
            f"//a[text()='{next_page}']",
            f"//a[contains(@href, 'page={next_page}')]",
            f"//a[@data-page='{next_page}']",
            f"//button[text()='{next_page}']",
            f"//div[text()='{next_page}' and (@onclick or @data-page)]"
        ]

        for selector in page_number_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element.is_displayed() and element.is_enabled():
                    debug_log(f"✅ 페이지 번호 버튼 발견: {next_page}", 'DEBUG')
                    return {
                        'available': True,
                        'element': element,
                        'method': 'page_number',
                        'page': next_page
                    }
            except NoSuchElementException:
                continue

        # 방법 2: "다음", "Next", ">" 버튼 찾기
        next_button_keywords = []
        for lang_keywords in NEXT_PAGE_KEYWORDS.values():
            next_button_keywords.extend(lang_keywords)
        next_button_keywords.extend(['>', '›', '»', 'next'])

        for keyword in next_button_keywords:
            try:
                elements = driver.find_elements(By.XPATH,
                    f"//a[contains(text(), '{keyword}')] | "
                    f"//button[contains(text(), '{keyword}')] | "
                    f"//span[contains(text(), '{keyword}')]/parent::a | "
                    f"//span[contains(text(), '{keyword}')]/parent::button"
                )

                for element in elements:
                    class_name = element.get_attribute('class') or ''
                    if 'disabled' in class_name.lower() or 'inactive' in class_name.lower():
                        continue

                    if element.is_displayed() and element.is_enabled():
                        debug_log(f"✅ 다음 버튼 발견: '{keyword}'", 'DEBUG')
                        return {
                            'available': True,
                            'element': element,
                            'method': 'next_button',
                            'page': next_page
                        }

            except:
                continue

        # 마지막 페이지
        debug_log("⚠️ 다음 페이지 버튼을 찾을 수 없음 (마지막 페이지)", 'INFO')
        return {
            'available': False,
            'element': None,
            'method': None,
            'page': current_page
        }

    except Exception as e:
        debug_log("다음 페이지 버튼 검색 오류", 'ERROR', e)
        return {
            'available': False,
            'element': None,
            'method': None,
            'page': current_page
        }


def navigate_to_next_page(driver, current_page):
    """다음 페이지로 이동"""
    try:
        next_info = find_next_page_button(driver, current_page)

        if not next_info['available']:
            return {'success': False, 'page': current_page}

        element = next_info['element']

        try:
            element.click()
        except:
            driver.execute_script("arguments[0].click();", element)

        debug_log(f"다음 페이지로 이동 중... (방법: {next_info['method']})", 'INFO')

        # 페이지 로딩 대기
        time.sleep(2)
        wait_for_page_stable(driver, timeout=TIMEOUT['page_load'])

        debug_log(f"✅ 페이지 {next_info['page']} 이동 완료", 'INFO')

        return {'success': True, 'page': next_info['page']}

    except Exception as e:
        debug_log("페이지 이동 오류", 'ERROR', e)
        return {'success': False, 'page': current_page}


# ============================================
# 통계 출력 및 로깅 (ver1.4 개선)
# ============================================

def log_progress(page, article_idx, total, status):
    """간결한 진행 로그 (ver1.4)"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] P{page} {article_idx}/{total} | {status}")


def display_page_summary(page, success_count, skipped_count, no_pdf_count, error_count):
    """페이지별 통계 출력"""
    print(f"\n{'='*60}")
    print(f"📊 페이지 {page} 완료")
    print(f"   ✅ 성공: {success_count}개 | ⏭️ 건너뜀: {skipped_count}개 | ⚠️ PDF없음: {no_pdf_count}개 | ❌ 실패: {error_count}개")

    # 전체 진행 상황
    download_log = load_download_log()
    total_downloaded = download_log['total_downloaded']
    print(f"💾 전체 진행: {total_downloaded}개 다운로드 완료")
    print(f"{'='*60}\n")


def display_final_summary(start_time, total_pages, success_count, skipped_count, no_pdf_count, error_count):
    """최종 통계 출력"""
    elapsed_time = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"🏁 스크래핑 완료")
    print(f"{'='*60}")
    print(f"📄 처리한 페이지: {total_pages}개")
    print(f"✅ 다운로드 성공: {success_count}개")
    print(f"⏭️ 건너뜀: {skipped_count}개 (이미 다운로드됨)")
    print(f"⚠️ PDF 없음: {no_pdf_count}개")
    print(f"❌ 실패: {error_count}개")
    print(f"⏱️ 소요 시간: {format_time(elapsed_time)}")
    print(f"{'='*60}\n")


# ============================================
# 메인 스크래퍼
# ============================================

def run_scraper(board_url, download_dir, resume_from=None):
    """
    메인 스크래퍼 실행
    """
    # 드라이버 설정
    driver = setup_driver(download_dir)
    wait = WebDriverWait(driver, TIMEOUT['element_wait'])

    # 시작 정보
    if resume_from:
        current_page = resume_from['current_page']
        resume_article_index = resume_from['current_article_index'] + 1
        board_url = resume_from.get('board_url', board_url)
        print(f"🔄 페이지 {current_page}, {resume_article_index + 1}번째 게시글부터 재개합니다.\n")
    else:
        current_page = 1
        resume_article_index = 0

    # 통계
    start_time = time.time()
    total_pages_processed = 0
    total_success = 0
    total_skipped = 0
    total_no_pdf = 0
    total_error = 0

    processed_count = 0

    try:
        while True:  # Ctrl+C까지 무한 실행
            try:
                # 현재 페이지 URL 생성
                if '?' in board_url:
                    current_url = f"{board_url}&page={current_page}"
                else:
                    # 페이지 파라미터가 이미 URL에 있을 수 있음
                    current_url = board_url

                print(f"\n{'='*60}")
                print(f"📄 페이지 {current_page} 처리 중...")
                print(f"{'='*60}")
                print(f"🔗 URL: {current_url}\n")

                # 페이지 접속
                driver.get(current_url)
                wait_for_page_stable(driver, timeout=TIMEOUT['page_load'])

                # 게시글 개수 파악 (첫 추출)
                article_links = extract_board_links(driver)

                if not article_links:
                    print("⚠️ 게시글을 찾을 수 없습니다.")
                    print("페이지 구조를 분석합니다...\n")
                    analyze_page_structure(driver)

                    response = input("\n계속 진행하시겠습니까? [y/n]: ")
                    if response.lower() != 'y':
                        break

                    nav_result = navigate_to_next_page(driver, current_page)
                    if nav_result['success']:
                        current_page = nav_result['page']
                        continue
                    else:
                        print("다음 페이지를 찾을 수 없습니다. 종료합니다.")
                        break

                total_articles = len(article_links)
                print(f"📝 게시글 {total_articles}개 발견\n")

                # 페이지별 통계
                page_success = 0
                page_skipped = 0
                page_no_pdf = 0
                page_error = 0

                # ver1.4: 연속 에러 카운터
                MAX_CONSECUTIVE_ERRORS = 5
                error_count = 0

                # ver1.4: 페이지별 학습 전략 (초기화)
                page_learned_strategy = None

                # 각 게시글 처리 (인덱스 기반)
                for idx in range(total_articles):
                    # 재시작 시 건너뛰기
                    if current_page == (resume_from or {}).get('current_page', 0) and idx < resume_article_index:
                        print(f"  ⏭️ [{idx + 1}/{total_articles}] 건너뜀 (이미 처리됨)")
                        continue

                    # ✅ 매번 게시판 링크 다시 추출 (stale element 방지)
                    article_links = extract_board_links(driver)

                    if idx >= len(article_links):
                        debug_log(f"게시글 {idx + 1}번을 찾을 수 없음 (총 {len(article_links)}개)", 'WARNING')
                        break

                    link_info = article_links[idx]
                    article_title = link_info['title']

                    # ver1.4: 진행 로그 출력
                    log_progress(current_page, idx + 1, total_articles, f"처리 중: {article_title[:30]}")

                    # ver1.4: 페이지 단위 학습 로직
                    try:
                        if idx == 0:
                            # 첫 게시글: 전체 탐지 + 학습
                            print(f"  [{idx + 1}/{total_articles}] 학습 모드 (모든 전략 시도)")
                            result = process_article(driver, wait, link_info, download_dir)

                            # 성공한 전략 저장
                            if result['status'] in ['success', 'partial']:
                                page_learned_strategy = result.get('successful_strategy')
                                if page_learned_strategy:
                                    print(f"    ✓ 학습 완료: {page_learned_strategy}")
                        else:
                            # 나머지: 빠른 모드
                            if page_learned_strategy:
                                print(f"  [{idx + 1}/{total_articles}] 빠른 모드 ({page_learned_strategy})")
                                # 빠른 모드로 처리 - process_article 대신 직접 호출
                                article_url_temp = driver.current_url
                                result_fast = auto_detect_and_download_fast(
                                    driver, wait, download_dir,
                                    page_learned_strategy,
                                    article_title, article_url_temp
                                )
                                result = {
                                    **result_fast,
                                    'article_title': article_title,
                                    'article_url': article_url_temp
                                }
                            else:
                                # 학습 실패 시 전체 탐지
                                print(f"  [{idx + 1}/{total_articles}] 학습 없음 (전체 탐지)")
                                result = process_article(driver, wait, link_info, download_dir)

                        error_count = 0  # 성공 시 리셋
                    except Exception as e:
                        error_count += 1
                        debug_log(f"게시글 처리 중 오류 발생", 'ERROR', e)

                        if error_count >= MAX_CONSECUTIVE_ERRORS:
                            print(f"\n⚠️ 연속 {MAX_CONSECUTIVE_ERRORS}회 실패. 게시판 구조 변경 가능성")
                            user_response = input("계속 진행하시겠습니까? [y/n]: ")
                            if user_response.lower() != 'y':
                                print("사용자가 중단을 선택했습니다.")
                                break
                            error_count = 0  # 계속하면 리셋

                        # 에러 결과 생성
                        result = {
                            'status': 'error',
                            'message': str(e),
                            'article_title': article_title,
                            'article_url': 'N/A',
                            'downloads': [],
                            'skipped': []
                        }

                    # 결과에서 정보 추출
                    article_url = result.get('article_url', 'N/A')

                    # 다중 PDF 결과 처리
                    downloads = result.get('downloads', [])
                    skipped = result.get('skipped', [])

                    if result['status'] in ['success', 'partial']:
                        # 다운로드 성공
                        for dl in downloads:
                            filename = dl.get('filename', 'unknown')
                            size = dl.get('size', 'unknown')
                            print(f"    ✅ 성공: {filename} ({size})")

                            add_download_record(
                                title=article_title,
                                filename=filename,
                                url=article_url,
                                size=size,
                                method=dl.get('method', 'unknown')
                            )

                        page_success += len(downloads)
                        total_success += len(downloads)

                        # 건너뛴 파일들
                        page_skipped += len(skipped)
                        total_skipped += len(skipped)

                        if result['status'] == 'partial':
                            print(f"    ⚠️ 일부 PDF 다운로드 실패")

                    elif result['status'] == 'all_skipped':
                        # 모두 건너뜀
                        for sk in skipped:
                            print(f"    ⏭️ 건너뜀: {sk.get('filename', 'unknown')}")

                        page_skipped += len(skipped)
                        total_skipped += len(skipped)

                    elif result['status'] == 'no_pdf':
                        print(f"    ⚠️ PDF 없음")
                        if USE_DATABASE:
                            from database import add_failure_record as db_add_failure
                            db_add_failure(article_title, article_url, 'no_pdf')
                        else:
                            add_failure_record(article_title, article_url, 'no_pdf')

                        page_no_pdf += 1
                        total_no_pdf += 1

                    else:  # error
                        message = result.get('message', 'unknown')
                        print(f"    ❌ 실패: {message}")

                        if USE_DATABASE:
                            from database import add_failure_record as db_add_failure
                            db_add_failure(article_title, article_url, message)
                        else:
                            add_failure_record(article_title, article_url, message)

                        page_error += 1
                        total_error += 1

                    # Checkpoint 저장
                    download_log = load_download_log()
                    save_checkpoint(
                        page=current_page,
                        article_index=idx,
                        board_url=current_url,
                        total_downloaded=download_log['total_downloaded']
                    )

                    # ✅ 게시판 목록으로 복귀 (안정성 강화)
                    try:
                        debug_log(f"게시판 복귀: {current_url}", 'DEBUG')
                        driver.get(current_url)
                        wait_for_page_stable(driver, timeout=TIMEOUT['page_load'])
                        time.sleep(1)

                        # 게시판 페이지가 맞는지 확인
                        if "list" not in driver.current_url.lower() and "board" not in driver.current_url.lower():
                            debug_log("게시판 복귀 확인 실패, 재시도", 'WARNING')
                            driver.get(current_url)
                            wait_for_page_stable(driver, timeout=TIMEOUT['page_load'])

                    except Exception as e:
                        debug_log("게시판 복귀 중 오류, 재시도", 'WARNING', e)
                        driver.get(current_url)
                        wait_for_page_stable(driver, timeout=TIMEOUT['page_load'])
                        time.sleep(1)

                    # 브라우저 주기적 재시작
                    processed_count += 1
                    if processed_count % BROWSER_RESTART_INTERVAL == 0:
                        print(f"\n  🔄 브라우저 재시작 중... ({processed_count}개 처리 완료)")
                        driver = restart_browser(driver, download_dir)
                        wait = WebDriverWait(driver, TIMEOUT['element_wait'])
                        driver.get(current_url)
                        wait_for_page_stable(driver, timeout=TIMEOUT['page_load'])

                # 페이지 통계 출력
                display_page_summary(current_page, page_success, page_skipped, page_no_pdf, page_error)
                total_pages_processed += 1

                # ver1.3: 페이지 종료 시 학습 데이터 저장 (메모리 → JSON)
                if USE_STRATEGY_LEARNING:
                    save_learned_strategies()
                    debug_log(f"📚 페이지 {current_page} 종료: 학습 데이터 저장 완료", 'DEBUG')

                # 다음 페이지로 이동
                print(f"📄 다음 페이지 확인 중...")
                nav_result = navigate_to_next_page(driver, current_page)

                if not nav_result['success']:
                    print(f"\n{'='*60}")
                    print(f"🎉 마지막 페이지 도달! 스크래핑 완료")
                    print(f"{'='*60}\n")
                    break

                current_page = nav_result['page']
                resume_article_index = 0  # 새 페이지는 처음부터

            except KeyboardInterrupt:
                print(f"\n\n{'='*60}")
                print(f"🛑 사용자가 중단했습니다 (Ctrl+C)")
                print(f"{'='*60}\n")
                break

            except Exception as e:
                debug_log(f"페이지 {current_page} 처리 중 오류 발생", 'ERROR', e)
                print(f"\n❌ 오류 발생: {e}")
                print("브라우저를 재시작하고 계속합니다...\n")

                # 브라우저 재시작
                driver = restart_browser(driver, download_dir)
                wait = WebDriverWait(driver, TIMEOUT['element_wait'])
                continue

    finally:
        # 드라이버 종료
        try:
            driver.quit()
        except:
            pass

        # ver1.3: 프로그램 종료 시 최종 학습 데이터 저장
        if USE_STRATEGY_LEARNING:
            save_learned_strategies()
            print("📚 학습 데이터 저장 완료\n")

        # 최종 통계
        display_final_summary(start_time, total_pages_processed, total_success, total_skipped, total_no_pdf, total_error)


# ============================================
# 메인 함수
# ============================================

def main():
    """메인 함수"""
    # 커맨드라인 인자 확인
    auto_mode = len(sys.argv) > 1
    auto_url = sys.argv[1] if auto_mode else None

    print(f"\n{'='*70}")
    print(f"범용 PDF 자동 스크래퍼 ver1.4.1")
    print(f"{'='*70}")
    print(f"개인정보 보호: 정보통신망법 준수 (이메일/전화번호 수집 차단)")
    print(f"ver1.4.1: 탭/네비게이션 필터링 강화로 학습 정확도 향상!")
    print(f"PDF 전용: PDF 파일만 다운로드 (다른 형식 자동 차단)")
    print(f"로그 보안: 개인정보 자동 마스킹")
    print(f"{'='*70}\n")

    # ver1.3.1: 데이터 관리 옵션
    data_stats = get_data_stats()

    if USE_STRATEGY_LEARNING:
        # 현재 데이터 현황 표시
        print(f"📊 현재 데이터 현황:")
        print(f"   📚 학습된 게시판: {data_stats['learning_boards']}개")
        print(f"   📄 다운로드된 PDF: {data_stats['pdf_count']}개")
        print(f"   📝 로그 크기: {data_stats['log_size']:.1f} KB")
        if data_stats['has_checkpoint']:
            print(f"   💾 체크포인트: 있음")
        print()

        if data_stats['learning_boards'] > 0 or data_stats['pdf_count'] > 0:
            # 초기화 옵션 선택
            if auto_mode:
                # 자동 모드: 초기화 안 함
                reset_option = '3'
                print(f"🔄 자동 모드: 기존 데이터 사용\n")
            else:
                print(f"🔄 초기화 옵션:")
                print(f"   1. 학습 데이터만 초기화 (PDF 파일 유지)")
                print(f"   2. 완전 초기화 (학습 데이터 + PDF + 로그 모두 삭제)")
                print(f"   3. 초기화 안 함 (기존 데이터 사용)")
                print()

                reset_option = input("선택 [1/2/3]: ").strip()

            if reset_option == '1':
                # 학습 데이터만 초기화
                if reset_learned_strategies():
                    print(f"\n   ✅ 학습 데이터 초기화 완료!")
                    print(f"   📄 PDF 파일 {data_stats['pdf_count']}개는 유지됩니다.")
                    print(f"   ℹ️  모든 게시판을 새로 학습합니다.\n")
                else:
                    print(f"\n   ❌ 초기화 실패\n")

            elif reset_option == '2':
                # 완전 초기화
                confirm = input("⚠️  PDF 파일과 모든 로그가 삭제됩니다. 계속하시겠습니까? [y/n]: ")
                if confirm.lower() == 'y':
                    reset_stats = reset_all_data(keep_downloads=False)
                    print(f"\n   ✅ 완전 초기화 완료!")
                    print(f"   📚 학습 데이터: {'삭제됨' if reset_stats['learning_data'] else '없음'}")
                    print(f"   📄 PDF 파일: {reset_stats['pdf_files']}개 삭제")
                    print(f"   📝 로그 파일: {reset_stats['log_files']}개 삭제")
                    print(f"   💾 체크포인트: {'삭제됨' if reset_stats['checkpoint'] else '없음'}")
                    print(f"   🗄️  데이터베이스: {'삭제됨' if reset_stats['database'] else '없음'}")
                    print(f"   ℹ️  완전히 처음 상태로 돌아갑니다.\n")
                else:
                    print(f"\n   ℹ️  취소되었습니다. 기존 데이터를 사용합니다.\n")

            else:
                # 초기화 안 함
                print(f"\n   ℹ️  기존 데이터를 사용합니다.\n")
        else:
            print(f"📚 데이터 없음 (새로 시작합니다)\n")

    # ver1.2: JSON → DB 마이그레이션
    if USE_DATABASE:
        json_log = DOWNLOAD_LOG_FILE
        if os.path.exists(json_log):
            print(f"💾 기존 JSON 로그를 DB로 마이그레이션 중...")
            count = migrate_from_json(json_log)
            if count > 0:
                print(f"   ✅ {count}개 레코드 마이그레이션 완료\n")
            else:
                print(f"   ℹ️  마이그레이션할 데이터가 없습니다\n")

    # Checkpoint 확인
    checkpoint = load_checkpoint()

    if checkpoint and not auto_mode:
        print(f"💾 이전 작업을 발견했습니다:")
        print(f"   페이지: {checkpoint['current_page']}")
        print(f"   진행: {checkpoint['current_article_index'] + 1}번째 게시글")
        print(f"   URL: {checkpoint['board_url']}")
        print(f"   마지막 실행: {checkpoint['last_updated']}")
        print(f"   다운로드 완료: {checkpoint['total_downloaded']}개\n")

        resume = input("🔄 이어서 진행하시겠습니까? [y/n]: ")

        if resume.lower() == 'y':
            board_url = checkpoint['board_url']
            download_dir = DOWNLOAD_DIR

            print(f"\n✅ 재개합니다.\n")
            print(f"{'='*60}\n")

            run_scraper(board_url, download_dir, resume_from=checkpoint)
            return

        else:
            print("\n새로 시작합니다.\n")
            clear_checkpoint()

    # 새로 시작
    if auto_mode:
        # 자동 모드: 커맨드라인 인자로 URL 받음
        board_url = auto_url
        download_dir = DOWNLOAD_DIR
        print(f"📍 URL: {board_url}")
        print(f"📂 폴더: {download_dir}\n")
    else:
        # 대화형 모드
        board_url = input("📍 게시판 URL을 입력하세요:\n   예) https://example.com/board\n\n> ")

        if not board_url.strip():
            print("❌ URL을 입력해주세요.")
            return

        download_dir_input = input(f"\n📂 다운로드 폴더 경로 (기본값: {DOWNLOAD_DIR}):\n   엔터키를 누르면 기본값 사용\n\n> ")

        download_dir = download_dir_input.strip() if download_dir_input.strip() else DOWNLOAD_DIR

        print(f"\n{'='*60}")
        print(f"✅ 설정 완료")
        print(f"{'='*60}")
        print(f"📍 URL: {board_url}")
        print(f"📂 폴더: {download_dir}")
        print(f"{'='*60}\n")

        input("엔터키를 누르면 스크래핑을 시작합니다...")

    # 폴더 생성
    os.makedirs(download_dir, exist_ok=True)

    print(f"\n🚀 스크래핑 시작...\n")

    # 스크래퍼 실행
    run_scraper(board_url, download_dir)

    print("\n👋 프로그램을 종료합니다.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.\n")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}\n")
        debug_log("프로그램 실행 중 치명적 오류", 'ERROR', e)
