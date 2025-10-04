"""
범용 PDF 자동 스크래퍼 ver1.4.1 - 유틸리티 함수들

ver1.4.1 추가 기능:
- 개인정보 감지 및 필터링 (정보통신망법 준수)
- 이메일 주소 자동 감지 및 제거
- 전화번호, 주민번호 패턴 감지
- PDF 파일 확장자 엄격 검증

기존 기능:
- SHA256 해시 계산 (중복 방지)
- 파일명 정규화 (특수문자 처리)
- HTTP 헤더 기반 파일명 추출
"""

import os
import sys
import time
import json
import hashlib
import re
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import *


# ============================================
# ver1.4.1: 개인정보 보호 (정보통신망법 준수)
# ============================================

# 개인정보 정규식 패턴
PERSONAL_INFO_PATTERNS = {
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    'phone': re.compile(r'(\d{2,3}[-.\s]?\d{3,4}[-.\s]?\d{4})'),
    'mobile': re.compile(r'(01[0-9][-.\s]?\d{3,4}[-.\s]?\d{4})'),
    'rrn': re.compile(r'\d{6}[-\s]?[1-4]\d{6}'),  # 주민번호
}

def contains_personal_info(text):
    """
    텍스트에 개인정보가 포함되어 있는지 검사
    정보통신망법 제50조의2 위반 방지

    Args:
        text: 검사할 텍스트

    Returns:
        tuple: (bool, list) - (개인정보 포함 여부, 발견된 정보 유형 리스트)
    """
    if not text:
        return False, []

    found_types = []

    for info_type, pattern in PERSONAL_INFO_PATTERNS.items():
        if pattern.search(str(text)):
            found_types.append(info_type)
            debug_log(f"⚠️ 개인정보 감지: {info_type}", 'WARNING')

    return len(found_types) > 0, found_types


def remove_personal_info(text):
    """
    텍스트에서 개인정보 제거 (마스킹)

    Args:
        text: 원본 텍스트

    Returns:
        str: 개인정보가 제거된 텍스트
    """
    if not text:
        return text

    cleaned_text = str(text)

    # 이메일 제거
    cleaned_text = PERSONAL_INFO_PATTERNS['email'].sub('[이메일제거]', cleaned_text)

    # 전화번호 제거
    cleaned_text = PERSONAL_INFO_PATTERNS['phone'].sub('[전화번호제거]', cleaned_text)
    cleaned_text = PERSONAL_INFO_PATTERNS['mobile'].sub('[전화번호제거]', cleaned_text)

    # 주민번호 제거
    cleaned_text = PERSONAL_INFO_PATTERNS['rrn'].sub('[주민번호제거]', cleaned_text)

    return cleaned_text


def is_pdf_file_only(filename):
    """
    PDF 파일만 허용 (다른 파일 형식 차단)
    ver1.4.1 버그픽스: 확장자 추출 실패 시에도 .pdf 포함 파일명 허용

    Args:
        filename: 파일명

    Returns:
        bool: PDF 파일이면 True
    """
    if not filename:
        return False

    # 확장자 추출
    ext = os.path.splitext(filename.lower())[1]

    debug_log(f"PDF 검증: 파일명='{filename}', 확장자='{ext}'", 'DEBUG')

    # PDF 확장자 확인
    if ext == '.pdf':
        debug_log(f"✅ PDF 파일 확인: {filename}", 'DEBUG')
        return True

    # 차단된 파일 형식 확인
    blocked_extensions = ['.txt', '.csv', '.xlsx', '.xls', '.doc', '.docx',
                         '.hwp', '.zip', '.rar', '.exe', '.html', '.xml']

    if ext in blocked_extensions:
        debug_log(f"🔒 차단된 파일 형식: {ext} ({filename})", 'WARNING')
        return False

    # ⭐ 버그픽스: 확장자 없거나 추출 실패한 경우
    if not ext or ext == '':
        # 파일명에 .pdf가 포함되어 있으면 PDF로 간주
        if '.pdf' in filename.lower():
            debug_log(f"✅ PDF 패턴 감지 (확장자 없음): {filename}", 'DEBUG')
            return True
        # 그 외에는 차단
        debug_log(f"🔒 확장자 없음, 차단: {filename}", 'WARNING')
        return False

    # 알 수 없는 확장자는 보안을 위해 차단
    debug_log(f"🔒 알 수 없는 파일 형식: {ext} ({filename})", 'WARNING')
    return False


def sanitize_for_logging(text, max_length=200):
    """
    로깅용 텍스트 정제 (개인정보 제거 + 길이 제한)

    Args:
        text: 원본 텍스트
        max_length: 최대 길이

    Returns:
        str: 정제된 텍스트
    """
    if not text:
        return ""

    # 개인정보 제거
    cleaned = remove_personal_info(str(text))

    # 길이 제한
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + "..."

    return cleaned


# ============================================
# 로깅 시스템
# ============================================

def debug_log(message, level='INFO', error=None):
    """통합 로깅 시스템"""
    if DEBUG_LEVELS.get(level, 2) > CURRENT_DEBUG_LEVEL:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"

    if error:
        log_message += f" | ERROR: {str(error)}"
        if hasattr(error, '__traceback__'):
            log_message += f"\nTRACEBACK: {traceback.format_exc()}"

    print(log_message)

    # 파일에도 기록
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(DEBUG_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception:
        pass  # 로깅 실패는 무시


# ============================================
# Selenium 드라이버 설정
# ============================================

def setup_driver(download_dir=None):
    """
    Selenium WebDriver 설정 (안티봇 우회 포함)

    Args:
        download_dir: PDF 다운로드 폴더 경로

    Returns:
        WebDriver 객체
    """
    if download_dir is None:
        download_dir = DOWNLOAD_DIR

    os.makedirs(download_dir, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()

    # 다운로드 설정
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "plugins.always_open_pdf_externally": True,
        "safebrowsing.enabled": True,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # 안티봇 우회 설정
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument(f"user-agent={USER_AGENT}")

    # 성능 최적화
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Headless 모드 (필요시 주석 해제)
    # chrome_options.add_argument("--headless")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # WebDriver 감지 우회
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })

        debug_log("Selenium 드라이버 설정 완료", 'INFO')
        return driver

    except Exception as e:
        debug_log("드라이버 설정 실패", 'ERROR', e)
        raise


def restart_browser(old_driver, download_dir=None):
    """브라우저 재시작"""
    try:
        old_driver.quit()
        debug_log("브라우저 종료", 'INFO')
    except:
        pass

    time.sleep(2)
    new_driver = setup_driver(download_dir)
    debug_log("브라우저 재시작 완료", 'INFO')
    return new_driver


# ============================================
# 페이지 안정화 대기
# ============================================

def wait_for_page_stable(driver, timeout=None, stable_time=2):
    """
    페이지가 완전히 로드되고 안정화될 때까지 대기

    Args:
        driver: WebDriver 객체
        timeout: 최대 대기 시간 (초)
        stable_time: 안정화 판단 시간 (초)

    Returns:
        bool: 성공 여부
    """
    if timeout is None:
        timeout = TIMEOUT['page_stable']

    debug_log(f"페이지 안정화 대기 중 (timeout: {timeout}s)", 'DEBUG')

    start_time = time.time()
    last_dom_size = 0
    stable_count = 0

    while time.time() - start_time < timeout:
        try:
            # 페이지 로딩 상태 확인
            ready_state = driver.execute_script("return document.readyState")
            if ready_state != "complete":
                debug_log("페이지 로딩 중...", 'VERBOSE')
                time.sleep(0.5)
                continue

            # DOM 안정성 확인
            current_dom_size = driver.execute_script("return document.getElementsByTagName('*').length")

            if current_dom_size == last_dom_size:
                stable_count += 1
                if stable_count >= stable_time:
                    debug_log(f"페이지 안정화 완료 ({time.time() - start_time:.1f}s)", 'DEBUG')
                    return True
            else:
                stable_count = 0
                last_dom_size = current_dom_size
                debug_log(f"DOM 변경 감지 (요소: {current_dom_size}개)", 'VERBOSE')

            time.sleep(0.5)

        except Exception as e:
            debug_log(f"페이지 안정성 확인 오류", 'WARNING', e)
            time.sleep(0.5)

    debug_log(f"페이지 안정화 타임아웃 ({timeout}s)", 'WARNING')
    return False


# ============================================
# 다운로드 관리
# ============================================

def wait_for_download_completion(download_dir, expected_filename=None, timeout=None):
    """
    파일 다운로드 완료 대기 및 검증

    Args:
        download_dir: 다운로드 폴더
        expected_filename: 예상 파일명 (선택)
        timeout: 최대 대기 시간 (초)

    Returns:
        dict: {"status": "success/timeout", "filename": "...", "filepath": "..."}
    """
    if timeout is None:
        timeout = TIMEOUT['download_wait']

    start_time = time.time()
    initial_files = set(os.listdir(download_dir))

    debug_log("다운로드 완료 대기 중...", 'DEBUG')

    while time.time() - start_time < timeout:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files

        # 다운로드 중인 파일 제외 (.crdownload, .tmp, .part)
        completed_downloads = [f for f in new_files if not f.endswith(('.crdownload', '.tmp', '.part'))]

        if completed_downloads:
            latest_file = max(completed_downloads, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
            file_path = os.path.join(download_dir, latest_file)

            # 파일 크기 및 PDF 검증
            if os.path.getsize(file_path) > MIN_PDF_SIZE:
                try:
                    with open(file_path, 'rb') as f:
                        header = f.read(4)
                        if header == PDF_HEADER:
                            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                            debug_log(f"다운로드 완료: {latest_file} ({file_size_mb:.2f} MB)", 'INFO')
                            return {
                                "status": "success",
                                "filename": latest_file,
                                "filepath": file_path,
                                "size": f"{file_size_mb:.2f} MB"
                            }
                except Exception as e:
                    debug_log(f"PDF 검증 실패", 'WARNING', e)

        time.sleep(1)

    debug_log("다운로드 타임아웃", 'WARNING')
    return {"status": "timeout", "message": "다운로드 시간 초과"}


def is_already_downloaded(filename, download_dir=None):
    """
    파일이 이미 다운로드되었는지 확인

    Args:
        filename: 파일명
        download_dir: 다운로드 폴더

    Returns:
        bool: 이미 존재하면 True
    """
    if download_dir is None:
        download_dir = DOWNLOAD_DIR

    filepath = os.path.join(download_dir, filename)
    return os.path.exists(filepath)


def get_safe_filename(text, max_length=100):
    """
    안전한 파일명 생성 (특수문자 제거)

    Args:
        text: 원본 텍스트
        max_length: 최대 길이

    Returns:
        str: 안전한 파일명
    """
    # 파일명에 사용 불가능한 문자 제거
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')

    # 길이 제한
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


# ============================================
# 로그 파일 관리
# ============================================

def load_download_log():
    """다운로드 로그 불러오기"""
    if os.path.exists(DOWNLOAD_LOG_FILE):
        try:
            with open(DOWNLOAD_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            debug_log("다운로드 로그 읽기 오류", 'ERROR', e)

    return {
        "last_updated": None,
        "total_downloaded": 0,
        "downloads": []
    }


def save_download_log(log_data):
    """다운로드 로그 저장"""
    log_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(DOWNLOAD_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        debug_log("다운로드 로그 저장 실패", 'ERROR', e)


def add_download_record(title, filename, url, size, method):
    """다운로드 기록 추가"""
    log_data = load_download_log()

    log_data["downloads"].append({
        "title": title,
        "filename": filename,
        "url": url,
        "size": size,
        "method": method,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    log_data["total_downloaded"] = len(log_data["downloads"])
    save_download_log(log_data)


def load_failed_log():
    """실패 로그 불러오기"""
    if os.path.exists(FAILED_LOG_FILE):
        try:
            with open(FAILED_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            debug_log("실패 로그 읽기 오류", 'ERROR', e)

    return {
        "last_updated": None,
        "total_failed": 0,
        "failures": []
    }


def save_failed_log(log_data):
    """실패 로그 저장"""
    log_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(FAILED_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        debug_log("실패 로그 저장 실패", 'ERROR', e)


def add_failure_record(title, url, reason):
    """실패 기록 추가"""
    log_data = load_failed_log()

    log_data["failures"].append({
        "title": title,
        "url": url,
        "reason": reason,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    log_data["total_failed"] = len(log_data["failures"])
    save_failed_log(log_data)


# ============================================
# Checkpoint 관리
# ============================================

def load_checkpoint():
    """체크포인트 불러오기"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                debug_log(f"체크포인트 로드: 페이지 {data.get('current_page')}, 게시글 {data.get('current_article_index')}", 'INFO')
                return data
        except (json.JSONDecodeError, IOError) as e:
            debug_log("체크포인트 읽기 오류", 'ERROR', e)

    return None


def save_checkpoint(page, article_index, board_url, total_downloaded=0):
    """체크포인트 저장"""
    data = {
        "current_page": page,
        "current_article_index": article_index,
        "board_url": board_url,
        "total_downloaded": total_downloaded,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        debug_log(f"체크포인트 저장: 페이지 {page}, 게시글 {article_index}", 'DEBUG')
    except Exception as e:
        debug_log("체크포인트 저장 실패", 'ERROR', e)


def clear_checkpoint():
    """체크포인트 삭제"""
    try:
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
            debug_log("체크포인트 삭제 완료", 'INFO')
    except Exception as e:
        debug_log("체크포인트 삭제 실패", 'ERROR', e)


# ============================================
# 진행 상황 표시
# ============================================

def display_progress(current, total, prefix='진행'):
    """
    진행률 표시

    Args:
        current: 현재 진행
        total: 전체
        prefix: 접두사
    """
    if not SHOW_PROGRESS_BAR:
        return

    percentage = (current / total * 100) if total > 0 else 0
    filled_length = int(50 * current // total) if total > 0 else 0
    bar = '█' * filled_length + '-' * (50 - filled_length)

    print(f'\r{prefix}: |{bar}| {percentage:.1f}% ({current}/{total})', end='', flush=True)

    if current == total:
        print()  # 줄바꿈


def format_time(seconds):
    """초를 시:분:초 형식으로 변환"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}시간 {minutes}분 {secs}초"
    elif minutes > 0:
        return f"{minutes}분 {secs}초"
    else:
        return f"{secs}초"


# ============================================
# 파일 해시 및 중복 체크 (ver1.1 추가)
# ============================================

def calculate_file_hash(file_path):
    """
    파일의 SHA256 해시 계산

    Args:
        file_path: 파일 경로

    Returns:
        str: SHA256 해시 문자열 (소문자) 또는 None
    """
    try:
        sha256_hash = hashlib.sha256()

        with open(file_path, 'rb') as f:
            # 대용량 파일 대비 블록 단위로 읽기
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        hash_value = sha256_hash.hexdigest()
        debug_log(f"파일 해시 계산: {os.path.basename(file_path)} -> {hash_value[:16]}...", 'DEBUG')

        return hash_value

    except Exception as e:
        debug_log(f"해시 계산 실패: {file_path}", 'WARNING', e)
        return None


def normalize_filename(filename, max_length=100):
    """
    파일명 정규화 (특수문자 제거, 공백 처리)

    Args:
        filename: 원본 파일명
        max_length: 최대 길이

    Returns:
        str: 정규화된 파일명
    """
    # 확장자 분리
    name, ext = os.path.splitext(filename)

    # 파일명에 사용 불가능한 문자 제거
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')

    # 연속된 공백을 하나로
    name = re.sub(r'\s+', ' ', name)

    # 앞뒤 공백 제거
    name = name.strip()

    # 길이 제한 (확장자 포함)
    max_name_length = max_length - len(ext)
    if len(name) > max_name_length:
        name = name[:max_name_length]

    normalized = name + ext

    if normalized != filename:
        debug_log(f"파일명 정규화: '{filename}' -> '{normalized}'", 'DEBUG')

    return normalized


def extract_filename_from_url(url):
    """
    URL에서 파일명 추출

    Args:
        url: URL 문자열

    Returns:
        str or None: 파일명 또는 None
    """
    try:
        # URL에서 마지막 부분 추출
        # https://example.com/files/report.pdf?id=123 → report.pdf
        path = url.split('/')[-1]
        filename = path.split('?')[0]  # 쿼리 파라미터 제거
        filename = filename.split('#')[0]  # 앵커 제거

        if '.pdf' in filename.lower():
            return normalize_filename(filename)

        return None

    except Exception as e:
        debug_log(f"URL에서 파일명 추출 실패: {url}", 'WARNING', e)
        return None


def extract_filename_from_content_disposition(response_headers):
    """
    HTTP Content-Disposition 헤더에서 파일명 추출

    Args:
        response_headers: HTTP 응답 헤더 (dict)

    Returns:
        str or None: 파일명 또는 None
    """
    try:
        content_disposition = response_headers.get('Content-Disposition', '')

        if not content_disposition:
            return None

        # filename="report.pdf" 또는 filename*=UTF-8''report.pdf 패턴
        patterns = [
            r'filename\*=UTF-8\'\'(.+)',
            r'filename="(.+)"',
            r'filename=([^;\s]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, content_disposition, re.IGNORECASE)
            if match:
                filename = match.group(1).strip('"\'')

                # URL 디코딩 (필요시)
                import urllib.parse
                filename = urllib.parse.unquote(filename)

                if '.pdf' in filename.lower():
                    debug_log(f"Content-Disposition에서 파일명 추출: {filename}", 'DEBUG')
                    return normalize_filename(filename)

        return None

    except Exception as e:
        debug_log("Content-Disposition 파싱 실패", 'WARNING', e)
        return None


def generate_fallback_filename(article_title):
    """
    파일명 추출 실패 시 대체 파일명 생성

    Args:
        article_title: 게시글 제목

    Returns:
        str: 생성된 파일명
    """
    # 게시글 제목 정규화
    title = normalize_filename(article_title, max_length=50)

    # 타임스탬프 추가
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{title}_{timestamp}.pdf"

    debug_log(f"대체 파일명 생성: {filename}", 'DEBUG')

    return filename


# ============================================
# 안전성 검증
# ============================================

def is_safe_element(element):
    """
    요소가 클릭해도 안전한지 검증

    Args:
        element: WebElement

    Returns:
        bool: 안전하면 True
    """
    if not SAFE_MODE:
        return True

    try:
        # 요소 속성 가져오기
        href = element.get_attribute('href') or ''
        title = element.get_attribute('title') or ''
        text = element.text or ''
        onclick = element.get_attribute('onclick') or ''
        class_name = element.get_attribute('class') or ''

        # 모든 텍스트 결합
        all_text = (href + title + text + onclick + class_name).lower()

        # 위험한 패턴 확인
        for pattern in DANGEROUS_PATTERNS:
            if pattern in all_text:
                debug_log(f"위험한 패턴 감지: {pattern}", 'WARNING')
                return False

        return True

    except Exception as e:
        debug_log("안전성 검증 오류", 'WARNING', e)
        return False


# ============================================
# ver1.3.1: 데이터 초기화 기능
# ============================================

def reset_all_data(keep_downloads=False):
    """
    모든 데이터 완전 초기화 (테스트용)

    Args:
        keep_downloads: True면 PDF 파일 유지, False면 모두 삭제

    Returns:
        dict: 삭제된 항목 통계
    """
    stats = {
        'learning_data': False,
        'pdf_files': 0,
        'log_files': 0,
        'checkpoint': False,
        'database': False
    }

    try:
        # 1. 학습 데이터 삭제
        if os.path.exists(LEARNED_STRATEGIES_FILE):
            os.remove(LEARNED_STRATEGIES_FILE)
            stats['learning_data'] = True
            debug_log("학습 데이터 파일 삭제", 'INFO')

        # 2. PDF 파일 삭제 (옵션)
        if not keep_downloads and os.path.exists(DOWNLOAD_DIR):
            import shutil
            pdf_count = len([f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.pdf')])
            shutil.rmtree(DOWNLOAD_DIR)
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            stats['pdf_files'] = pdf_count
            debug_log(f"PDF 파일 {pdf_count}개 삭제", 'INFO')

        # 3. 로그 파일 삭제
        log_files = [
            DOWNLOAD_LOG_FILE,
            FAILED_LOG_FILE,
            DEBUG_LOG_FILE,
            STRATEGY_LEARN_FILE,
            BOARD_PATTERN_CACHE
        ]

        for log_file in log_files:
            if os.path.exists(log_file):
                os.remove(log_file)
                stats['log_files'] += 1

        debug_log(f"로그 파일 {stats['log_files']}개 삭제", 'INFO')

        # 4. 체크포인트 삭제
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
            stats['checkpoint'] = True
            debug_log("체크포인트 파일 삭제", 'INFO')

        # 5. DB 초기화 (있으면)
        if USE_DATABASE:
            db_file = os.path.join(LOG_DIR, 'downloads.db')
            if os.path.exists(db_file):
                os.remove(db_file)
                stats['database'] = True
                debug_log("데이터베이스 파일 삭제", 'INFO')

        return stats

    except Exception as e:
        debug_log("데이터 초기화 중 오류", 'ERROR', e)
        return stats


def get_data_stats():
    """
    현재 데이터 통계 조회

    Returns:
        dict: 데이터 통계
    """
    stats = {
        'pdf_count': 0,
        'learning_boards': 0,
        'log_size': 0,
        'has_checkpoint': False
    }

    try:
        # PDF 개수
        if os.path.exists(DOWNLOAD_DIR):
            stats['pdf_count'] = len([f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.pdf')])

        # 학습된 게시판 개수
        if os.path.exists(LEARNED_STRATEGIES_FILE):
            with open(LEARNED_STRATEGIES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats['learning_boards'] = len(data)

        # 로그 크기
        if os.path.exists(DEBUG_LOG_FILE):
            stats['log_size'] = os.path.getsize(DEBUG_LOG_FILE) / 1024  # KB

        # 체크포인트 여부
        stats['has_checkpoint'] = os.path.exists(CHECKPOINT_FILE)

        return stats

    except Exception as e:
        debug_log("통계 조회 중 오류", 'WARNING', e)
        return stats