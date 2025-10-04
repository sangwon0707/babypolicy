"""
범용 PDF 자동 스크래퍼 ver1.4 - PDF 탐지 전략 엔진 (빠른 모드 + 안정성 강화)

ver1.4 핵심 개선사항:
🎯 빠른 모드 추가:
  - auto_detect_and_download_fast(): 학습된 전략만 시도
  - 실패 시 전체 탐지로 자동 폴백
  - 페이지 단위 학습으로 속도 최적화

⚡ 안정성 강화:
  - 게시판 URL 추출 로직 간소화 (쿼리 파라미터만 제거)
  - 중복 제거: URL + 텍스트 해시 조합으로 개선
  - 전략 식별자 생성 함수 추가 (get_strategy_identifier)

ver1.3 기능 유지:
- 전략 패턴 학습 시스템
- 게시판별 전략 성공률 추적
- 다중 PDF 다운로드 지원
- 해시 기반 중복 체크
"""

import re
import os
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import *
from utils import (
    debug_log, wait_for_page_stable, wait_for_download_completion, is_safe_element,
    calculate_file_hash, normalize_filename, extract_filename_from_url,
    generate_fallback_filename, is_already_downloaded
)

# ver1.4: 빠른 모드 함수 export
__all__ = ['auto_detect_and_download_all', 'auto_detect_and_download_fast',
           'save_learned_strategies', 'reset_learned_strategies',
           'get_learned_strategies_stats', 'analyze_page_structure']

# ver1.1: DB 사용 여부에 따라 import
if USE_DATABASE:
    try:
        from database import (
            is_duplicate_by_filename, is_duplicate_by_hash,
            is_duplicate_by_url_filename, add_download_record as db_add_download_record
        )
    except ImportError:
        debug_log("database.py를 찾을 수 없습니다. 파일 기반 중복 체크만 사용됩니다.", 'WARNING')
        USE_DATABASE = False


# ============================================
# ver1.3: 전략 학습 시스템 (메모리 + JSON)
# ============================================

# 메모리 캐시: 빠른 조회용
_learned_strategies = {}
# {
#     "https://bokjiro.go.kr/board/list": {
#         "filename_link": {"success": 15, "fail": 1, "score": 0.94},
#         "direct_link": {"success": 3, "fail": 2, "score": 0.60},
#         ...
#     }
# }

def load_learned_strategies():
    """JSON 파일에서 학습된 전략 로드"""
    global _learned_strategies

    try:
        if os.path.exists(LEARNED_STRATEGIES_FILE):
            with open(LEARNED_STRATEGIES_FILE, 'r', encoding='utf-8') as f:
                _learned_strategies = json.load(f)
            debug_log(f"학습된 전략 로드 완료: {len(_learned_strategies)}개 게시판", 'INFO')
        else:
            _learned_strategies = {}
            debug_log("학습 데이터 없음, 새로 시작", 'DEBUG')
    except Exception as e:
        debug_log("학습 데이터 로드 실패, 새로 시작", 'WARNING', e)
        _learned_strategies = {}


def save_learned_strategies():
    """학습된 전략을 JSON 파일에 저장"""
    try:
        os.makedirs(os.path.dirname(LEARNED_STRATEGIES_FILE), exist_ok=True)
        with open(LEARNED_STRATEGIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(_learned_strategies, f, ensure_ascii=False, indent=2)
        debug_log(f"학습 데이터 저장 완료: {len(_learned_strategies)}개 게시판", 'DEBUG')
    except Exception as e:
        debug_log("학습 데이터 저장 실패", 'WARNING', e)


def reset_learned_strategies():
    """
    학습된 전략 데이터 초기화 (테스트용)

    - 메모리 캐시 초기화
    - JSON 파일 삭제
    """
    global _learned_strategies

    try:
        # 1. 메모리 캐시 초기화
        _learned_strategies = {}
        debug_log("메모리 학습 데이터 초기화 완료", 'INFO')

        # 2. JSON 파일 삭제
        if os.path.exists(LEARNED_STRATEGIES_FILE):
            os.remove(LEARNED_STRATEGIES_FILE)
            debug_log(f"학습 파일 삭제: {LEARNED_STRATEGIES_FILE}", 'INFO')

        return True
    except Exception as e:
        debug_log("학습 데이터 초기화 실패", 'ERROR', e)
        return False


def get_learned_strategies_stats():
    """
    학습 데이터 통계 조회

    Returns:
        dict: 게시판별 학습 통계
    """
    stats = {
        'total_boards': len(_learned_strategies),
        'boards': []
    }

    for board_url, strategies in _learned_strategies.items():
        board_stat = {
            'url': board_url,
            'strategies': len(strategies),
            'top_strategy': None,
            'top_score': 0
        }

        # 최고 점수 전략 찾기
        for strategy_type, data in strategies.items():
            if data['score'] > board_stat['top_score']:
                board_stat['top_strategy'] = strategy_type
                board_stat['top_score'] = data['score']

        stats['boards'].append(board_stat)

    return stats


def calculate_strategy_score(success_count, fail_count):
    """
    전략 신뢰도 점수 계산

    방식: 성공률 + 연속 성공 보너스
    - 기본 점수: success / (success + fail)
    - 연속 3회 성공 시 +0.1 보너스

    Args:
        success_count: 성공 횟수
        fail_count: 실패 횟수

    Returns:
        float: 0.0 ~ 1.0 사이 점수
    """
    total = success_count + fail_count
    if total == 0:
        return 0.5  # 초기 중립 점수

    base_score = success_count / total

    # 연속 성공 보너스
    if success_count >= 3 and fail_count == 0:
        base_score = min(1.0, base_score + 0.1)

    return round(base_score, 2)


def update_strategy_stats(board_url, strategy_type, success):
    """
    전략 통계 업데이트 (성공/실패 기록)

    Args:
        board_url: 게시판 URL
        strategy_type: 전략 타입 (예: "filename_link")
        success: 성공 여부 (True/False)
    """
    global _learned_strategies

    # 게시판 초기화
    if board_url not in _learned_strategies:
        _learned_strategies[board_url] = {}

    # 전략 초기화
    if strategy_type not in _learned_strategies[board_url]:
        _learned_strategies[board_url][strategy_type] = {
            "success": 0,
            "fail": 0,
            "score": 0.5
        }

    # 통계 업데이트
    stats = _learned_strategies[board_url][strategy_type]
    if success:
        stats["success"] += 1
    else:
        stats["fail"] += 1

    # 점수 재계산
    stats["score"] = calculate_strategy_score(stats["success"], stats["fail"])

    debug_log(f"전략 업데이트 [{strategy_type}]: {stats} (게시판: {board_url[:50]})", 'DEBUG')


def get_sorted_strategies(board_url, all_strategy_types):
    """
    게시판별 학습된 전략을 점수 순으로 정렬

    Args:
        board_url: 게시판 URL
        all_strategy_types: 모든 전략 타입 리스트

    Returns:
        list: [{"type": "...", "score": 0.94}, ...] 점수 높은 순
    """
    if board_url not in _learned_strategies:
        # 학습 데이터 없음 → 기본 순서 (모두 동일 점수)
        return [{"type": t, "score": 0.5} for t in all_strategy_types]

    board_stats = _learned_strategies[board_url]
    strategy_list = []

    for strategy_type in all_strategy_types:
        if strategy_type in board_stats:
            score = board_stats[strategy_type]["score"]
        else:
            score = 0.5  # 시도 안 한 전략은 중립 점수

        strategy_list.append({"type": strategy_type, "score": score})

    # 점수 높은 순으로 정렬
    strategy_list.sort(key=lambda x: x["score"], reverse=True)

    return strategy_list


def should_skip_strategy(board_url, strategy_type):
    """
    전략을 스킵해야 하는지 판단 (연속 5회 실패 시)

    Args:
        board_url: 게시판 URL
        strategy_type: 전략 타입

    Returns:
        bool: True이면 스킵
    """
    if board_url not in _learned_strategies:
        return False

    if strategy_type not in _learned_strategies[board_url]:
        return False

    stats = _learned_strategies[board_url][strategy_type]

    # 연속 5회 실패 기준: success=0, fail>=5
    if stats["success"] == 0 and stats["fail"] >= 5:
        debug_log(f"전략 스킵 [{strategy_type}]: 연속 {stats['fail']}회 실패", 'DEBUG')
        return True

    return False


def get_strategy_learned_score(board_url, strategy_type):
    """
    전략의 학습된 점수 조회

    Args:
        board_url: 게시판 URL
        strategy_type: 전략 타입

    Returns:
        float: 학습된 점수 (0.0~1.0), 없으면 0.5 (중립)
    """
    if board_url not in _learned_strategies:
        return 0.5

    if strategy_type not in _learned_strategies[board_url]:
        return 0.5

    return _learned_strategies[board_url][strategy_type]['score']


def sort_strategies_by_learning(strategies, board_url):
    """
    학습된 데이터를 기반으로 전략 우선순위 정렬

    핵심: 항상 모든 전략을 탐지하되, 학습된 점수로 우선순위만 조정!

    Args:
        strategies: 탐지된 전략 리스트
        board_url: 게시판 URL

    Returns:
        list: 우선순위 정렬된 전략 리스트
    """
    if board_url not in _learned_strategies or not strategies:
        # 학습 데이터 없으면 기본 confidence로 정렬
        return sorted(strategies, key=lambda x: x['confidence'], reverse=True)

    def get_priority_score(strategy):
        strategy_type = strategy['type']
        base_confidence = strategy['confidence']

        # 학습된 점수 가져오기
        learned_score = get_strategy_learned_score(board_url, strategy_type)

        # 최종 우선순위 = 학습 점수 70% + 기본 confidence 30%
        priority = learned_score * 0.7 + base_confidence * 0.3

        return priority

    sorted_list = sorted(strategies, key=get_priority_score, reverse=True)

    debug_log(f"전략 우선순위 정렬 완료 (학습 기반)", 'DEBUG')
    for i, s in enumerate(sorted_list[:3], 1):
        learned_score = get_strategy_learned_score(board_url, s['type'])
        debug_log(f"  {i}. {s['type']}: 학습={learned_score:.2f}, confidence={s['confidence']:.2f}", 'DEBUG')

    return sorted_list


# 초기화: 프로그램 시작 시 학습 데이터 로드
load_learned_strategies()


def extract_board_url(article_url):
    """
    게시물 URL에서 게시판 기본 URL 추출 (ver1.4 개선)

    핵심: 간단하고 안정적인 방식으로 게시판 URL 추출

    예시:
    - https://bokjiro.go.kr/board/view?id=123 → https://bokjiro.go.kr/board/view
    - https://example.com/notice/detail/456 → https://example.com/notice/detail
    - https://site.com/bbs/read.php?no=789 → https://site.com/bbs

    Args:
        article_url: 게시물 URL

    Returns:
        str: 게시판 기본 URL
    """
    if not article_url or article_url == "unknown":
        return "unknown"

    try:
        from urllib.parse import urlparse, urljoin

        parsed = urlparse(article_url)

        # 방법 1: 쿼리 파라미터만 제거 (가장 안전)
        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # 방법 2: 마지막 경로 세그먼트가 숫자면 제거
        if parsed.path.split('/')[-1].isdigit():
            base = urljoin(base, '.')

        debug_log(f"게시판 URL 추출: {article_url[:60]} → {base[:60]}", 'DEBUG')
        return base

    except Exception as e:
        debug_log(f"게시판 URL 추출 실패, 원본 사용: {e}", 'WARNING')
        return article_url


# ============================================
# 전략 1: 직접 PDF 링크 탐지
# ============================================

def find_direct_pdf_links(driver):
    """
    <a href="*.pdf"> 형태의 직접 PDF 링크 찾기

    Args:
        driver: WebDriver 객체

    Returns:
        list: 탐지된 전략 리스트
    """
    strategies = []

    try:
        # CSS Selector로 PDF 링크 찾기
        pdf_links = driver.find_elements(By.CSS_SELECTOR, 'a[href$=".pdf"], a[href$=".PDF"]')

        debug_log(f"직접 PDF 링크 {len(pdf_links)}개 발견", 'DEBUG')

        for link in pdf_links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()

                if href and is_safe_element(link):
                    strategies.append({
                        'type': 'direct_link',
                        'element': link,
                        'url': href,
                        'text': text or '제목없음',
                        'confidence': 0.95,
                        'method': 'click'
                    })
            except Exception as e:
                debug_log(f"직접 링크 분석 오류", 'WARNING', e)
                continue

    except Exception as e:
        debug_log("직접 PDF 링크 탐지 오류", 'WARNING', e)

    return strategies


# ============================================
# 전략 2: 다운로드 버튼 탐지
# ============================================

def find_download_buttons(driver):
    """
    "다운로드", "Download" 등의 키워드를 가진 버튼 찾기

    Args:
        driver: WebDriver 객체

    Returns:
        list: 탐지된 전략 리스트
    """
    strategies = []

    try:
        # 모든 다운로드 키워드 결합
        all_keywords = []
        for lang_keywords in DOWNLOAD_KEYWORDS.values():
            all_keywords.extend(lang_keywords)

        # 클릭 가능한 요소들 찾기
        clickable_elements = driver.find_elements(By.XPATH,
            "//button | //a | //div[@onclick] | //span[@onclick] | //input[@type='button']")

        debug_log(f"클릭 가능한 요소 {len(clickable_elements)}개 검사 중", 'DEBUG')

        for element in clickable_elements:
            try:
                text = (element.text or '').lower()
                title = (element.get_attribute('title') or '').lower()
                aria_label = (element.get_attribute('aria-label') or '').lower()
                value = (element.get_attribute('value') or '').lower()

                all_text = f"{text} {title} {aria_label} {value}"

                # 키워드 매칭
                matched_keywords = [kw for kw in all_keywords if kw in all_text]

                if matched_keywords and is_safe_element(element):
                    # Confidence 계산
                    confidence = 0.7

                    # .pdf가 근처에 있으면 confidence 증가
                    if '.pdf' in all_text:
                        confidence = 0.9

                    # "다운로드" 키워드가 정확히 일치하면 confidence 증가
                    if any(kw == text.strip() for kw in ['다운로드', 'download']):
                        confidence = 0.85

                    strategies.append({
                        'type': 'download_button',
                        'element': element,
                        'text': element.text or title or '버튼',
                        'keywords': matched_keywords,
                        'confidence': confidence,
                        'method': 'click'
                    })

            except Exception as e:
                continue

        debug_log(f"다운로드 버튼 {len(strategies)}개 발견", 'DEBUG')

    except Exception as e:
        debug_log("다운로드 버튼 탐지 오류", 'WARNING', e)

    return strategies


# ============================================
# 전략 3: 첨부파일 섹션 탐지
# ============================================

def find_attachment_sections(driver):
    """
    "첨부파일", "Attachment" 섹션에서 PDF 찾기

    Args:
        driver: WebDriver 객체

    Returns:
        list: 탐지된 전략 리스트
    """
    strategies = []

    try:
        # 첨부파일 키워드
        all_keywords = []
        for lang_keywords in ATTACHMENT_KEYWORDS.values():
            all_keywords.extend(lang_keywords)

        # 첨부파일 섹션 찾기
        for keyword in all_keywords:
            try:
                # 키워드가 포함된 섹션 찾기
                sections = driver.find_elements(By.XPATH,
                    f"//*[contains(text(), '{keyword}')]/ancestor::div[1] | "
                    f"//*[contains(text(), '{keyword}')]/following-sibling::div[1] | "
                    f"//*[contains(@class, 'attach')] | "
                    f"//*[contains(@class, 'file')]"
                )

                for section in sections:
                    # 섹션 안의 PDF 링크 찾기 (href 또는 text에 .pdf 포함)
                    # ver1.3.2: text에 .pdf가 있는 링크도 탐지 (download.php?id=123 같은 경우 대응)
                    pdf_links = section.find_elements(By.XPATH,
                        ".//a[contains(@href, '.pdf') or contains(@href, '.PDF') or "
                        "contains(text(), '.pdf') or contains(text(), '.PDF')]")

                    for link in pdf_links:
                        if is_safe_element(link):
                            link_text = link.text or '첨부파일'
                            link_href = link.get_attribute('href') or ''

                            # ver1.3.2: 비PDF 파일 필터링 (.xlsx, .xls, .doc, .docx, .hwp 등)
                            non_pdf_extensions = ['.xlsx', '.xls', '.xlsm', '.doc', '.docx', '.hwp', '.zip', '.egg']
                            is_non_pdf = any(ext in link_text.lower() or ext in link_href.lower()
                                           for ext in non_pdf_extensions)

                            if is_non_pdf:
                                debug_log(f"비PDF 파일 스킵: {link_text[:50]}", 'DEBUG')
                                continue

                            strategies.append({
                                'type': 'attachment_section',
                                'element': link,
                                'text': link_text,
                                'url': link_href,
                                'confidence': 0.90,
                                'method': 'click'
                            })

                    # 섹션 안의 다운로드 버튼 찾기
                    download_buttons = section.find_elements(By.XPATH,
                        ".//button | .//a | .//*[@onclick]")

                    for button in download_buttons:
                        button_text = (button.text or '').lower()
                        if any(kw in button_text for kw in ['다운로드', 'download']) and is_safe_element(button):
                            strategies.append({
                                'type': 'attachment_button',
                                'element': button,
                                'text': button.text or '다운로드',
                                'confidence': 0.85,
                                'method': 'click'
                            })

            except Exception as e:
                continue

        debug_log(f"첨부파일 섹션에서 {len(strategies)}개 발견", 'DEBUG')

    except Exception as e:
        debug_log("첨부파일 섹션 탐지 오류", 'WARNING', e)

    return strategies


# ============================================
# 전략 4: iframe/embed 탐지
# ============================================

def find_embedded_pdfs(driver):
    """
    <iframe src="*.pdf"> 또는 <embed> 태그 찾기

    Args:
        driver: WebDriver 객체

    Returns:
        list: 탐지된 전략 리스트
    """
    strategies = []

    try:
        # iframe 검색
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            try:
                src = iframe.get_attribute('src') or ''
                if '.pdf' in src.lower():
                    strategies.append({
                        'type': 'iframe',
                        'element': iframe,
                        'url': src,
                        'text': 'iframe PDF',
                        'confidence': 0.90,
                        'method': 'download_url'
                    })
            except:
                continue

        # embed 검색
        embeds = driver.find_elements(By.TAG_NAME, 'embed')
        for embed in embeds:
            try:
                src = embed.get_attribute('src') or ''
                if '.pdf' in src.lower():
                    strategies.append({
                        'type': 'embed',
                        'element': embed,
                        'url': src,
                        'text': 'embed PDF',
                        'confidence': 0.90,
                        'method': 'download_url'
                    })
            except:
                continue

        # object 검색
        objects = driver.find_elements(By.TAG_NAME, 'object')
        for obj in objects:
            try:
                data = obj.get_attribute('data') or ''
                if '.pdf' in data.lower():
                    strategies.append({
                        'type': 'object',
                        'element': obj,
                        'url': data,
                        'text': 'object PDF',
                        'confidence': 0.90,
                        'method': 'download_url'
                    })
            except:
                continue

        debug_log(f"임베디드 PDF {len(strategies)}개 발견", 'DEBUG')

    except Exception as e:
        debug_log("임베디드 PDF 탐지 오류", 'WARNING', e)

    return strategies


# ============================================
# 전략 5: 미리보기-다운로드 쌍 탐지
# ============================================

def find_preview_download_pairs(driver):
    """
    미리보기 버튼 근처의 다운로드 버튼 찾기
    ver1.1: SKIP_PREVIEW_BUTTONS 옵션으로 건너뛰기 가능

    Args:
        driver: WebDriver 객체

    Returns:
        list: 탐지된 전략 리스트
    """
    strategies = []

    # ver1.1: 미리보기 버튼 건너뛰기 옵션
    if SKIP_PREVIEW_BUTTONS:
        debug_log("미리보기-다운로드 쌍 탐지 건너뜀 (SKIP_PREVIEW_BUTTONS=True)", 'DEBUG')
        return strategies

    try:
        # 미리보기 키워드
        preview_keywords = []
        for lang_keywords in PREVIEW_KEYWORDS.values():
            preview_keywords.extend(lang_keywords)

        # 미리보기 요소 찾기
        preview_elements = driver.find_elements(By.XPATH,
            "//button | //a | //div[@onclick] | //span[@onclick]")

        for preview_elem in preview_elements:
            try:
                text = (preview_elem.text or '').lower()

                # 미리보기 키워드 확인
                if any(kw in text for kw in preview_keywords):
                    # 같은 부모 안의 다운로드 버튼 찾기
                    parent = preview_elem.find_element(By.XPATH, "..")
                    download_buttons = parent.find_elements(By.XPATH,
                        ".//*[contains(text(), '다운로드') or contains(text(), 'download') or contains(text(), 'Download')]")

                    for btn in download_buttons:
                        if is_safe_element(btn):
                            strategies.append({
                                'type': 'preview_download_pair',
                                'element': btn,
                                'text': btn.text or '다운로드',
                                'confidence': 0.60,  # ver1.1: 낮은 우선순위 (0.80 → 0.60)
                                'method': 'click'
                            })

            except:
                continue

        debug_log(f"미리보기-다운로드 쌍 {len(strategies)}개 발견", 'DEBUG')

    except Exception as e:
        debug_log("미리보기-다운로드 쌍 탐지 오류", 'WARNING', e)

    return strategies


# ============================================
# 전략 6: JavaScript 핸들러 분석
# ============================================

def find_javascript_handlers(driver):
    """
    onclick="downloadPDF('file.pdf')" 같은 패턴 찾기

    Args:
        driver: WebDriver 객체

    Returns:
        list: 탐지된 전략 리스트
    """
    strategies = []

    try:
        # onclick 속성이 있는 요소들
        elements_with_onclick = driver.find_elements(By.XPATH, "//*[@onclick]")

        debug_log(f"onclick 속성 요소 {len(elements_with_onclick)}개 검사 중", 'DEBUG')

        for element in elements_with_onclick:
            try:
                onclick = element.get_attribute('onclick') or ''

                # onclick 안에 .pdf가 있는지 확인
                if '.pdf' in onclick.lower() and is_safe_element(element):
                    # PDF URL 추출 시도
                    pdf_matches = re.findall(r'["\']([^"\']*\.pdf)["\']', onclick, re.IGNORECASE)

                    strategies.append({
                        'type': 'javascript_handler',
                        'element': element,
                        'onclick': onclick,
                        'pdf_urls': pdf_matches,
                        'text': element.text or 'JS 핸들러',
                        'confidence': 0.75,
                        'method': 'click'
                    })

            except:
                continue

        debug_log(f"JavaScript 핸들러 {len(strategies)}개 발견", 'DEBUG')

    except Exception as e:
        debug_log("JavaScript 핸들러 탐지 오류", 'WARNING', e)

    return strategies


# ============================================
# 전략 7: 파일명 직접 링크 탐지 (i-sh.co.kr 등)
# ============================================

def find_filename_links(driver):
    """
    파일명 텍스트 자체가 클릭 가능한 링크인 경우 탐지

    사용 사례:
    - <a onclick="downloadFile('file.pdf')">공고문.pdf</a>
    - <span onclick="download(123)">입찰명세서.pdf</span>

    Args:
        driver: WebDriver 객체

    Returns:
        list: 탐지된 전략 리스트
    """
    strategies = []

    try:
        # .pdf를 포함한 텍스트를 가진 클릭 가능한 요소 찾기
        # 단, "미리보기" 키워드는 제외
        xpath_parts = []

        # .pdf 또는 .PDF 텍스트 포함
        xpath_parts.append("contains(text(), '.pdf') or contains(text(), '.PDF')")

        # 미리보기 키워드 제외
        if SKIP_PREVIEW_BUTTONS:
            for kw in PREVIEW_KEYWORDS_FILTER:
                xpath_parts.append(f"not(contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{kw.lower()}'))")

        # onclick 또는 href 속성 필요
        xpath_parts.append("(@onclick or @href)")

        xpath_query = f"//*[{' and '.join(xpath_parts)}]"

        debug_log(f"파일명 직접 링크 검색 중...", 'DEBUG')

        elements = driver.find_elements(By.XPATH, xpath_query)

        for elem in elements:
            try:
                text = elem.text.strip()

                # 파일명처럼 생긴 텍스트인지 확인
                if '.pdf' in text.lower() and 3 < len(text) < 200:

                    # onclick 또는 href 확인
                    onclick = elem.get_attribute('onclick') or ''
                    href = elem.get_attribute('href') or ''

                    # 안전성 체크
                    if is_safe_element(elem):
                        strategies.append({
                            'type': 'filename_link',
                            'element': elem,
                            'text': text,
                            'onclick': onclick,
                            'url': href if href != '#' else None,
                            'confidence': 0.95,  # 높은 신뢰도 (파일명 직접 클릭)
                            'method': 'click'
                        })

                        debug_log(f"파일명 링크 발견: {text[:50]}", 'VERBOSE')

            except Exception as e:
                debug_log(f"파일명 링크 분석 오류", 'VERBOSE', e)
                continue

        debug_log(f"파일명 직접 링크 {len(strategies)}개 발견", 'DEBUG')

    except Exception as e:
        debug_log("파일명 직접 링크 탐지 오류", 'WARNING', e)

    return strategies


# ============================================
# 파일명 추출 (ver1.1 강화)
# ============================================

def extract_filename_from_strategy(strategy, article_title=''):
    """
    전략에서 PDF 파일명 추출 (ver1.4 복원 - SH 검증됨)

    Args:
        strategy: PDF 탐지 전략 dict
        article_title: 게시글 제목 (fallback용)

    Returns:
        str or None: 파일명 (예: "report.pdf") 또는 None
    """
    try:
        strategy_type = strategy.get('type', '')

        # 비PDF 파일 확장자 필터링
        non_pdf_extensions = ['.xlsx', '.xls', '.xlsm', '.doc', '.docx', '.hwp', '.zip', '.egg', '.txt', '.ppt', '.pptx']

        # 방법 1: URL에서 추출 (직접 링크, iframe, embed)
        if 'url' in strategy and strategy['url']:
            url_lower = strategy['url'].lower()

            # URL에 비PDF 확장자가 있으면 None 반환
            if any(ext in url_lower for ext in non_pdf_extensions):
                debug_log(f"비PDF URL 스킵: {strategy['url'][:50]}", 'DEBUG')
                return None

            filename = extract_filename_from_url(strategy['url'])
            if filename:
                debug_log(f"URL에서 파일명 추출: {filename}", 'DEBUG')
                return normalize_filename(filename) if NORMALIZE_FILENAMES else filename

        # 방법 2: 텍스트에서 추출 (다운로드 버튼, 첨부파일) - 정규식 강화
        if 'text' in strategy and strategy['text']:
            text = strategy['text']

            # 텍스트에 비PDF 확장자가 있으면 None 반환
            text_lower = text.lower()
            if any(ext in text_lower for ext in non_pdf_extensions):
                debug_log(f"비PDF 텍스트 스킵: {text[:50]}", 'DEBUG')
                return None

            # 한글, 영문, 숫자, 특수문자 포함 PDF 파일명 패턴
            patterns = [
                r'([\w가-힣\s\-_\.\(\)\[\]]+\.pdf)',  # 일반 패턴
                r'([^\s]+\.pdf)',  # 공백 없는 패턴
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    filename = match.group(1).strip()
                    debug_log(f"텍스트에서 파일명 추출: {filename}", 'DEBUG')
                    return normalize_filename(filename) if NORMALIZE_FILENAMES else filename

        # 방법 3: onclick에서 추출 (JavaScript 핸들러)
        if 'onclick' in strategy and strategy['onclick']:
            onclick = strategy['onclick']

            match = re.search(r'["\']([^"\']*\.pdf)["\']', onclick, re.IGNORECASE)

            if match:
                filename = match.group(1).split('/')[-1]  # 경로 제거
                debug_log(f"onclick에서 파일명 추출: {filename}", 'DEBUG')
                return normalize_filename(filename) if NORMALIZE_FILENAMES else filename

        # 방법 4: Fallback - 게시글 제목 + 타임스탬프
        if article_title:
            filename = generate_fallback_filename(article_title)
            debug_log(f"Fallback 파일명 생성: {filename}", 'DEBUG')
            return filename

        debug_log(f"파일명 추출 실패: {strategy_type}", 'DEBUG')
        return None

    except Exception as e:
        debug_log(f"파일명 추출 중 오류", 'WARNING', e)
        return None


# ============================================
# ver1.1: 다중 PDF 다운로드 지원
# ============================================

def check_duplicate(filename, file_path, article_url):
    """
    중복 체크 (파일명 + 해시)

    Args:
        filename: 파일명
        file_path: 파일 경로 (다운로드 후)
        article_url: 게시글 URL

    Returns:
        dict: {"is_duplicate": bool, "reason": str, "duplicate_info": dict}
    """
    # 1. 파일명 기반 체크
    if USE_FILENAME_CHECK:
        if USE_DATABASE and is_duplicate_by_filename(filename):
            debug_log(f"DB 파일명 중복: {filename}", 'INFO')
            return {
                'is_duplicate': True,
                'reason': 'filename_in_db',
                'duplicate_info': {'filename': filename}
            }

        # 파일 시스템 체크
        download_path = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.exists(download_path):
            debug_log(f"파일 시스템 중복: {filename}", 'INFO')
            return {
                'is_duplicate': True,
                'reason': 'filename_exists',
                'duplicate_info': {'filename': filename}
            }

    # 2. 해시 기반 체크 (다운로드 후)
    if USE_HASH_CHECK and file_path and os.path.exists(file_path):
        file_hash = calculate_file_hash(file_path)

        if file_hash and USE_DATABASE:
            dup_info = is_duplicate_by_hash(file_hash)
            if dup_info:
                debug_log(f"해시 중복 발견: {dup_info['filename']}", 'INFO')

                # 중복 파일 삭제 (옵션)
                if REMOVE_DUPLICATE_AFTER_DOWNLOAD:
                    try:
                        os.remove(file_path)
                        debug_log(f"중복 파일 삭제: {filename}", 'INFO')
                    except:
                        pass

                return {
                    'is_duplicate': True,
                    'reason': 'hash_duplicate',
                    'duplicate_info': dup_info
                }

    return {
        'is_duplicate': False,
        'reason': None,
        'duplicate_info': None
    }


def execute_download_strategy(driver, strategy, download_dir):
    """
    전략 실행 및 다운로드
    ver1.1: 새 창 자동 감지 및 닫기 기능 추가

    Args:
        driver: WebDriver
        strategy: 다운로드 전략 dict
        download_dir: 다운로드 폴더

    Returns:
        dict: 다운로드 결과
    """
    try:
        before_files = set(os.listdir(download_dir))

        # 현재 창 개수 저장 (새 창 감지용)
        initial_windows = len(driver.window_handles)
        current_window = driver.current_window_handle

        # 전략 실행
        if strategy['method'] == 'click':
            element = strategy['element']

            if not element.is_displayed() or not element.is_enabled():
                return {'status': 'failed', 'reason': 'element_not_valid'}

            try:
                element.click()
            except:
                driver.execute_script("arguments[0].click();", element)

            debug_log("요소 클릭 완료", 'DEBUG')

            # 새 창 감지 및 처리 (CLOSE_NEW_WINDOWS 옵션)
            if CLOSE_NEW_WINDOWS:
                time.sleep(1)  # 새 창이 열릴 시간 대기

                current_windows = len(driver.window_handles)

                if current_windows > initial_windows:
                    # 새 창이 열렸음
                    debug_log(f"새 창 감지됨 ({current_windows - initial_windows}개), 닫고 복귀", 'INFO')

                    # 모든 새 창 닫기
                    for handle in driver.window_handles:
                        if handle != current_window:
                            try:
                                driver.switch_to.window(handle)
                                driver.close()
                                debug_log(f"새 창 닫음", 'DEBUG')
                            except:
                                pass

                    # 원래 창으로 복귀
                    driver.switch_to.window(current_window)
                    debug_log("원래 창으로 복귀", 'DEBUG')

                    # 새 창이 열렸다는 것은 미리보기 버튼일 가능성 → 실패 처리
                    return {'status': 'failed', 'reason': 'new_window_opened'}

        elif strategy['method'] == 'download_url':
            url = strategy['url']
            driver.execute_script(f"window.open('{url}', '_blank');")
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[0])

        # 다운로드 대기
        result = wait_for_download_completion(download_dir, timeout=TIMEOUT['download_wait'])

        return result

    except Exception as e:
        debug_log(f"전략 실행 오류: {e}", 'WARNING')
        return {'status': 'failed', 'reason': str(e)}


def auto_detect_and_download_fast(driver, wait, download_dir, known_strategy, article_title='', article_url=''):
    """
    이미 학습된 전략만 시도 (빠른 모드) - ver1.4

    Args:
        driver: WebDriver 객체
        wait: WebDriverWait 객체
        download_dir: 다운로드 폴더
        known_strategy: 학습된 전략 타입 (예: "filename_link")
        article_title: 게시글 제목
        article_url: 게시글 URL

    Returns:
        dict: 다운로드 결과
    """
    debug_log(f"⚡ 빠른 모드: {known_strategy} 전략만 시도", 'INFO')

    # 해당 전략만 실행
    strategies = []
    if known_strategy == 'filename_link':
        strategies = find_filename_links(driver)
    elif known_strategy == 'direct_link':
        strategies = find_direct_pdf_links(driver)
    elif known_strategy == 'attachment_section':
        strategies = find_attachment_sections(driver)
    elif known_strategy == 'download_button':
        strategies = find_download_buttons(driver)
    elif known_strategy == 'iframe':
        strategies = find_embedded_pdfs(driver)
    elif known_strategy == 'javascript_handler':
        strategies = find_javascript_handlers(driver)
    elif known_strategy == 'preview_download_pair':
        strategies = find_preview_download_pairs(driver)

    if not strategies:
        debug_log("⚠️ 학습된 전략 실패, 전체 탐지로 전환", 'WARNING')
        return auto_detect_and_download_all(driver, wait, download_dir, article_title, article_url)

    # 첫 번째 전략만 시도
    strategy = strategies[0]
    result = execute_download_strategy(driver, strategy, download_dir)

    if result['status'] == 'success':
        # 파일명 추출
        expected_filename = extract_filename_from_strategy(strategy, article_title)
        actual_filename = result.get('filename', expected_filename)
        file_hash = calculate_file_hash(result.get('filepath', '')) if USE_HASH_CHECK else None

        return {
            'status': 'success',
            'downloads': [{
                'filename': actual_filename,
                'size': result.get('size', 'unknown'),
                'method': known_strategy,
                'confidence': strategy.get('confidence', 0.8),
                'filepath': result.get('filepath', ''),
                'hash': file_hash
            }],
            'skipped': [],
            'successful_strategy': known_strategy
        }
    else:
        # 실패 시 전체 탐지로 폴백
        debug_log("⚠️ 빠른 모드 실패, 전체 탐지로 전환", 'WARNING')
        return auto_detect_and_download_all(driver, wait, download_dir, article_title, article_url)


def auto_detect_and_download_all(driver, wait, download_dir, article_title='', article_url='', board_domain=None):
    """
    ver1.4: 모든 PDF 탐지 및 다운로드 (전략 학습 + 동적 우선순위 + 빠른 모드)

    Args:
        driver: WebDriver 객체
        wait: WebDriverWait 객체
        download_dir: 다운로드 폴더
        article_title: 게시글 제목
        article_url: 게시글 URL
        board_domain: 게시판 도메인 (사용 안 함, 하위 호환)

    Returns:
        dict: {"status": "success/no_pdf/partial", "downloads": [...], "skipped": [...], "successful_strategy": "..."}
    """
    debug_log("🔍 PDF 자동 탐지 시작 (ver1.4 - 전략 학습 + 빠른 모드)", 'INFO')

    # ver1.3 FIX: 게시물 URL → 게시판 URL 추출 (학습 키로 사용)
    # 예: https://bokjiro.go.kr/board/view?id=123 → https://bokjiro.go.kr/board
    board_url = extract_board_url(article_url) if article_url else "unknown"

    # 학습된 전략이 있는지 확인
    has_learned = board_url in _learned_strategies and len(_learned_strategies[board_url]) > 0

    if has_learned:
        debug_log(f"📚 학습된 패턴 발견! 우선순위 전략 사용 (게시판: {board_url[:60]})", 'INFO')
    else:
        debug_log(f"🆕 새 게시판: 모든 전략 시도하여 학습 (게시판: {board_url[:60]})", 'INFO')

    try:
        # 1. 항상 모든 전략으로 후보 탐지! (학습 여부와 관계없이)
        # 핵심: PDF를 놓치지 않기 위해 모든 전략 실행
        all_strategies = []

        debug_log("모든 전략으로 PDF 후보 탐지 시작...", 'DEBUG')

        # ⭐ 최우선: 파일명 직접 링크 (i-sh.co.kr 등)
        if PREFER_FILENAME_LINKS:
            all_strategies.extend(find_filename_links(driver))

        # 우선순위 높은 전략들
        all_strategies.extend(find_direct_pdf_links(driver))
        all_strategies.extend(find_embedded_pdfs(driver))
        all_strategies.extend(find_attachment_sections(driver))
        all_strategies.extend(find_download_buttons(driver))

        # JavaScript 핸들러
        all_strategies.extend(find_javascript_handlers(driver))

        # ⚠️ 낮은 우선순위: 미리보기-다운로드 쌍 (마지막 또는 건너뜀)
        all_strategies.extend(find_preview_download_pairs(driver))

        debug_log(f"총 {len(all_strategies)}개 PDF 후보 탐지 완료", 'INFO')

        # 2. 학습 데이터로 우선순위 정렬
        # 학습된 전략을 앞으로, 실패한 전략을 뒤로
        if USE_STRATEGY_LEARNING and has_learned:
            debug_log("학습된 데이터로 전략 우선순위 조정...", 'DEBUG')
            all_strategies = sort_strategies_by_learning(all_strategies, board_url)
        else:
            # 학습 없으면 기본 confidence로 정렬
            all_strategies.sort(key=lambda x: x['confidence'], reverse=True)
            debug_log("기본 confidence로 전략 정렬", 'DEBUG')

        if not all_strategies:
            debug_log("⚠️ PDF 탐지 실패: 후보 없음", 'INFO')
            return {
                'status': 'no_pdf',
                'message': 'PDF를 찾을 수 없음',
                'downloads': [],
                'skipped': []
            }

        debug_log(f"📊 총 {len(all_strategies)}개 다운로드 후보 발견", 'INFO')

        # 3. DOWNLOAD_ALL_PDFS 설정에 따라 처리
        if not DOWNLOAD_ALL_PDFS:
            # 기존 방식: 첫 번째만 다운로드
            all_strategies = all_strategies[:1]
            debug_log("단일 PDF 모드: 첫 번째 후보만 시도", 'INFO')

        # MAX_PDFS_PER_ARTICLE 제한
        all_strategies = all_strategies[:MAX_PDFS_PER_ARTICLE]

        # 4. 중복 제거 (같은 URL, 같은 파일명) - ver1.4 개선
        unique_strategies = []
        seen = set()

        def get_strategy_identifier(strategy):
            """더 안정적인 식별자 생성 (ver1.4)"""
            import hashlib

            # 1순위: URL + 텍스트 조합 (가장 안전)
            url = strategy.get('url', '')
            text = strategy.get('text', '').strip()

            if url and text:
                return hashlib.md5(f"{url}:{text}".encode()).hexdigest()
            elif text:
                return f"text:{text}"
            elif url:
                return f"url:{url}"
            else:
                return f"element:{id(strategy['element'])}"

        for strategy in all_strategies:
            identifier = get_strategy_identifier(strategy)

            if identifier not in seen:
                unique_strategies.append(strategy)
                seen.add(identifier)
                debug_log(f"고유 전략 추가: {identifier[:60]}", 'DEBUG')
            else:
                debug_log(f"중복 전략 스킵: {identifier[:60]}", 'DEBUG')

        debug_log(f"중복 제거: {len(all_strategies)}개 → {len(unique_strategies)}개 전략", 'INFO')

        # 5. 각 전략 순차 시도
        downloads = []
        skipped = []
        failed_count = 0

        for i, strategy in enumerate(unique_strategies, 1):
            try:
                debug_log(f"▶ 전략 {i}/{len(unique_strategies)} 시도: {strategy['type']}", 'INFO')

                # 파일명 추출
                expected_filename = extract_filename_from_strategy(strategy, article_title)

                if not expected_filename:
                    # ver1.3.2: 파일명 추출 실패는 학습에 기록하지 않음 (비PDF 파일일 가능성)
                    debug_log("파일명 추출 실패 (비PDF 또는 추출 불가), 다음 전략 시도", 'DEBUG')
                    # 비PDF 파일은 전략 실패가 아니므로 학습에 영향 없음
                    continue

                # 중복 체크 (다운로드 전)
                dup_check = check_duplicate(expected_filename, None, article_url)

                if dup_check['is_duplicate']:
                    debug_log(f"건너뜀: {expected_filename} ({dup_check['reason']})", 'INFO')
                    print(f"    ⏭️ 건너뜀: {expected_filename} (이미 다운로드됨)")

                    skipped.append({
                        'filename': expected_filename,
                        'reason': dup_check['reason'],
                        'strategy': strategy['type']
                    })
                    continue

                # 다운로드 실행
                download_result = execute_download_strategy(driver, strategy, download_dir)

                if download_result['status'] == 'success':
                    filepath = download_result['filepath']
                    actual_filename = download_result['filename']

                    # 해시 기반 중복 체크
                    dup_check_after = check_duplicate(actual_filename, filepath, article_url)

                    if dup_check_after['is_duplicate']:
                        skipped.append({
                            'filename': actual_filename,
                            'reason': dup_check_after['reason'],
                            'strategy': strategy['type']
                        })
                        # ver1.3: 중복도 실패로 학습 (같은 파일 또 다운로드 시도하지 않도록)
                        if USE_STRATEGY_LEARNING:
                            update_strategy_stats(board_url, strategy['type'], success=False)
                        continue

                    # 성공 기록
                    file_hash = calculate_file_hash(filepath) if USE_HASH_CHECK else None

                    downloads.append({
                        'filename': actual_filename,
                        'size': download_result.get('size', 'unknown'),
                        'method': strategy['type'],
                        'confidence': strategy['confidence'],
                        'filepath': filepath,
                        'hash': file_hash
                    })

                    # DB 기록
                    if USE_DATABASE:
                        db_add_download_record(
                            article_title=article_title,
                            article_url=article_url,
                            filename=actual_filename,
                            file_hash=file_hash,
                            file_size=download_result.get('size'),
                            method=strategy['type']
                        )

                    # ver1.3: 성공한 전략 학습!
                    if USE_STRATEGY_LEARNING:
                        update_strategy_stats(board_url, strategy['type'], success=True)
                        debug_log(f"📚 전략 학습: [{strategy['type']}] 성공 기록", 'DEBUG')

                    debug_log(f"✅ 다운로드 성공 [{i}/{len(unique_strategies)}]: {actual_filename}", 'INFO')

                else:
                    # ver1.3: 실패한 전략 학습
                    if USE_STRATEGY_LEARNING:
                        update_strategy_stats(board_url, strategy['type'], success=False)
                    failed_count += 1

            except Exception as e:
                debug_log(f"전략 {i} 실행 중 오류: {e}", 'WARNING')
                # ver1.3 FIX: 예외 발생도 학습 (실패로 기록)
                if USE_STRATEGY_LEARNING and 'strategy' in locals():
                    update_strategy_stats(board_url, strategy['type'], success=False)
                failed_count += 1
                continue

        # 6. 결과 반환
        # ver1.2: 성공한 전략 타입 기록 (패턴 학습용)
        successful_strategy = None
        if downloads:
            # 첫 번째 성공한 전략의 타입 저장
            successful_strategy = downloads[0].get('method')

        if downloads:
            status = 'success' if failed_count == 0 else 'partial'
            debug_log(f"✅ 다운로드 완료: {len(downloads)}개 성공, {len(skipped)}개 건너뜀, {failed_count}개 실패", 'INFO')

            return {
                'status': status,
                'downloads': downloads,
                'skipped': skipped,
                'failed_count': failed_count,
                'successful_strategy': successful_strategy
            }

        elif skipped:
            debug_log(f"⏭️ 모두 건너뜀: {len(skipped)}개", 'INFO')
            return {
                'status': 'all_skipped',
                'downloads': [],
                'skipped': skipped,
                'failed_count': failed_count,
                'successful_strategy': None
            }

        else:
            debug_log(f"❌ 모든 전략 실패", 'WARNING')
            return {
                'status': 'no_pdf',
                'message': f'{len(unique_strategies)}개 전략 시도했으나 실패',
                'downloads': [],
                'skipped': [],
                'successful_strategy': None
            }

    except Exception as e:
        debug_log("PDF 탐지 중 오류 발생", 'ERROR', e)
        return {
            'status': 'error',
            'message': f'탐지 오류: {str(e)}',
            'downloads': [],
            'skipped': []
        }


# ============================================
# 하위 호환성: 단일 PDF 다운로드 (기존 함수)
# ============================================

def auto_detect_and_download(driver, wait, download_dir):
    """
    모든 전략을 시도해서 PDF 자동 탐지 및 다운로드

    Args:
        driver: WebDriver 객체
        wait: WebDriverWait 객체
        download_dir: 다운로드 폴더

    Returns:
        dict: {"status": "success/no_pdf/error", "method": "...", "filename": "..."}
    """
    debug_log("🔍 PDF 자동 탐지 시작", 'INFO')

    try:
        # 1. 모든 전략으로 후보 찾기
        all_strategies = []

        all_strategies.extend(find_direct_pdf_links(driver))
        all_strategies.extend(find_embedded_pdfs(driver))
        all_strategies.extend(find_attachment_sections(driver))
        all_strategies.extend(find_download_buttons(driver))
        all_strategies.extend(find_preview_download_pairs(driver))
        all_strategies.extend(find_javascript_handlers(driver))

        if not all_strategies:
            debug_log("⚠️ PDF 탐지 실패: 후보 없음", 'INFO')
            return {
                'status': 'no_pdf',
                'message': 'PDF를 찾을 수 없음'
            }

        debug_log(f"📊 총 {len(all_strategies)}개 다운로드 후보 발견", 'INFO')

        # 2. Confidence 순으로 정렬
        all_strategies.sort(key=lambda x: x['confidence'], reverse=True)

        # 3. 상위 전략들 출력
        debug_log("상위 다운로드 전략:", 'INFO')
        for i, strategy in enumerate(all_strategies[:5], 1):
            debug_log(f"  {i}. [{strategy['type']}] "
                     f"Confidence: {strategy['confidence']:.0%} "
                     f"- {strategy.get('text', 'N/A')[:30]}", 'INFO')

        # 4. 각 전략 순차적으로 시도
        for i, strategy in enumerate(all_strategies, 1):
            try:
                debug_log(f"▶ 전략 {i}/{len(all_strategies)} 시도: {strategy['type']}", 'INFO')

                # ✅ 파일명 추출 및 중복 체크
                expected_filename = extract_filename_from_strategy(strategy)

                if expected_filename:
                    # 파일이 이미 존재하는지 확인
                    if is_already_downloaded(expected_filename, download_dir):
                        debug_log(f"파일 존재, 건너뜀: {expected_filename}", 'INFO')
                        print(f"    ⏭️ 건너뜀: {expected_filename} (이미 다운로드됨)")

                        return {
                            'status': 'skipped',
                            'message': '이미 다운로드됨',
                            'filename': expected_filename,
                            'method': strategy['type'],
                            'confidence': strategy['confidence']
                        }

                # 다운로드 시작 전 파일 목록 저장
                before_files = set(os.listdir(download_dir))

                # 전략 실행
                if strategy['method'] == 'click':
                    # 요소 클릭
                    element = strategy['element']

                    # 요소가 여전히 유효한지 확인
                    if not element.is_displayed() or not element.is_enabled():
                        debug_log("요소가 유효하지 않음, 다음 전략 시도", 'WARNING')
                        continue

                    # 클릭 시도
                    try:
                        element.click()
                    except:
                        # JavaScript 클릭 시도
                        driver.execute_script("arguments[0].click();", element)

                    debug_log("요소 클릭 완료", 'DEBUG')

                elif strategy['method'] == 'download_url':
                    # URL에서 직접 다운로드 (iframe/embed)
                    url = strategy['url']
                    debug_log(f"URL에서 직접 다운로드: {url}", 'DEBUG')

                    # 새 탭에서 열어서 다운로드 트리거
                    driver.execute_script(f"window.open('{url}', '_blank');")
                    time.sleep(2)

                    # 원래 탭으로 복귀
                    driver.switch_to.window(driver.window_handles[0])

                # 다운로드 대기
                result = wait_for_download_completion(download_dir, timeout=TIMEOUT['download_wait'])

                if result['status'] == 'success':
                    debug_log(f"✅ 다운로드 성공: {strategy['type']}", 'INFO')

                    return {
                        'status': 'success',
                        'method': strategy['type'],
                        'confidence': strategy['confidence'],
                        'filename': result['filename'],
                        'size': result.get('size', 'unknown'),
                        'filepath': result['filepath']
                    }

            except Exception as e:
                debug_log(f"❌ 전략 {i} 실패: {e}", 'WARNING')
                continue

        # 5. 모든 전략 실패
        debug_log(f"⚠️ 모든 전략 실패 ({len(all_strategies)}개 시도)", 'WARNING')
        return {
            'status': 'no_pdf',
            'message': f'{len(all_strategies)}개 전략 시도했으나 실패',
            'attempted_strategies': [s['type'] for s in all_strategies]
        }

    except Exception as e:
        debug_log("PDF 탐지 중 오류 발생", 'ERROR', e)
        return {
            'status': 'error',
            'message': f'탐지 오류: {str(e)}'
        }


# ============================================
# 페이지 구조 분석 (디버깅용)
# ============================================

def analyze_page_structure(driver):
    """
    페이지 구조를 분석해서 PDF 관련 요소 출력 (디버깅용)

    Args:
        driver: WebDriver 객체
    """
    debug_log("\n" + "="*60, 'INFO')
    debug_log("📊 페이지 구조 분석", 'INFO')
    debug_log("="*60, 'INFO')

    try:
        # 모든 링크 분석
        all_links = driver.find_elements(By.TAG_NAME, "a")
        debug_log(f"\n총 링크 수: {len(all_links)}", 'INFO')

        # PDF 관련 링크
        pdf_links = [link for link in all_links if '.pdf' in (link.get_attribute('href') or '').lower()]
        debug_log(f"PDF 링크 수: {len(pdf_links)}", 'INFO')

        # 다운로드 관련 요소
        download_elements = driver.find_elements(By.XPATH,
            "//*[contains(text(), '다운로드') or contains(text(), 'download') or contains(text(), 'Download')]")
        debug_log(f"다운로드 관련 요소 수: {len(download_elements)}", 'INFO')

        # 첨부파일 관련 요소
        attachment_elements = driver.find_elements(By.XPATH,
            "//*[contains(text(), '첨부') or contains(text(), 'attachment') or contains(text(), 'Attachment')]")
        debug_log(f"첨부파일 관련 요소 수: {len(attachment_elements)}", 'INFO')

        # iframe/embed
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        embeds = driver.find_elements(By.TAG_NAME, 'embed')
        debug_log(f"iframe 수: {len(iframes)}, embed 수: {len(embeds)}", 'INFO')

        debug_log("="*60 + "\n", 'INFO')

    except Exception as e:
        debug_log("페이지 구조 분석 오류", 'ERROR', e)