import os
import time
import json
import traceback
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# --- 설정 ---
BASE_URL = "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52005M.do?page=1&orderBy=date&tabId=1&sidoCd=1100000000&period=%EC%9E%84%EC%8B%A0%20%C2%B7%20%EC%B6%9C%EC%82%B0,%EC%98%81%EC%9C%A0%EC%95%84,%EC%95%84%EB%8F%99"

# 프로젝트 루트 경로 찾기 (backend/services/bokjiro_scraper -> 루트)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, 'data', 'pdfs', 'bokjiro')
LOG_DIR = os.path.join(PROJECT_ROOT, 'data', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'download_log.json')
DEBUG_LOG_FILE = os.path.join(LOG_DIR, 'debug_log.txt')
CHECKPOINT_FILE = os.path.join(LOG_DIR, 'checkpoint.json')

# Debug levels
DEBUG_LEVELS = {
    'ERROR': 0,
    'WARNING': 1,
    'INFO': 2,
    'DEBUG': 3,
    'VERBOSE': 4
}

CURRENT_DEBUG_LEVEL = DEBUG_LEVELS['VERBOSE']  # Set to maximum debugging

def time_operation(operation_name):
    """Decorator to time operations and log them"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            debug_log(f"Starting {operation_name}...", 'DEBUG')
            try:
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                debug_log(f"Completed {operation_name} in {elapsed_time:.2f}s", 'INFO')
                return result
            except Exception as e:
                elapsed_time = time.time() - start_time
                debug_log(f"Failed {operation_name} after {elapsed_time:.2f}s", 'ERROR', e)
                raise
        return wrapper
    return decorator

def log_timing_info(operation, start_time, additional_info=""):
    """Log timing information for operations"""
    elapsed = time.time() - start_time
    message = f"{operation} completed in {elapsed:.2f}s"
    if additional_info:
        message += f" | {additional_info}"
    debug_log(message, 'INFO')

def debug_log(message, level='INFO', error=None):
    """Enhanced logging with timestamps and debug levels"""
    if DEBUG_LEVELS.get(level, 2) > CURRENT_DEBUG_LEVEL:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"

    if error:
        log_message += f" | ERROR: {str(error)}"
        if hasattr(error, '__traceback__'):
            log_message += f"\nTRACEBACK: {traceback.format_exc()}"

    print(log_message)

    # Also write to debug log file
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(DEBUG_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception:
        pass  # Don't fail on logging errors

def save_checkpoint(data):
    """Save checkpoint data for resumption"""
    try:
        with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        debug_log(f"Checkpoint saved: {data}", 'DEBUG')
    except Exception as e:
        debug_log(f"Failed to save checkpoint", 'ERROR', e)

def load_checkpoint():
    """Load checkpoint data"""
    try:
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            debug_log(f"Checkpoint loaded: {data}", 'DEBUG')
            return data
    except Exception as e:
        debug_log(f"Failed to load checkpoint", 'ERROR', e)
    return None

def wait_for_page_stable(driver, timeout=30, stable_time=2):
    """Wait for page to be stable (no DOM changes for specified time)"""
    debug_log(f"Waiting for page to stabilize (timeout: {timeout}s, stable time: {stable_time}s)", 'DEBUG')

    start_time = time.time()
    last_dom_size = 0
    stable_count = 0

    while time.time() - start_time < timeout:
        try:
            # Check if page is still loading
            ready_state = driver.execute_script("return document.readyState")
            if ready_state != "complete":
                debug_log("Page still loading...", 'VERBOSE')
                time.sleep(0.5)
                continue

            # Check DOM stability
            current_dom_size = driver.execute_script("return document.getElementsByTagName('*').length")

            if current_dom_size == last_dom_size:
                stable_count += 1
                if stable_count >= stable_time:
                    debug_log(f"Page stabilized after {time.time() - start_time:.1f}s", 'DEBUG')
                    return True
            else:
                stable_count = 0
                last_dom_size = current_dom_size
                debug_log(f"DOM still changing (elements: {current_dom_size})", 'VERBOSE')

            time.sleep(0.5)

        except Exception as e:
            debug_log(f"Error checking page stability: {e}", 'WARNING')
            time.sleep(0.5)

    debug_log(f"Page stabilization timeout after {timeout}s", 'WARNING')
    return False

def wait_for_element_stable(driver, by, value, timeout=20):
    """Wait for element to be present and stable"""
    debug_log(f"Waiting for element to be stable: {by}={value}", 'DEBUG')

    wait = WebDriverWait(driver, timeout)
    try:
        # First wait for element to be present
        element = wait.until(EC.presence_of_element_located((by, value)))

        # Then wait for it to be clickable
        element = wait.until(EC.element_to_be_clickable((by, value)))

        # Additional stability check
        time.sleep(0.5)
        debug_log(f"Element is stable and ready: {by}={value}", 'DEBUG')
        return element

    except TimeoutException:
        debug_log(f"Element not found or not stable within {timeout}s: {by}={value}", 'WARNING')
        return None

def extract_policy_title(element, policy_index):
    """Extract policy title using multiple fallback methods"""
    debug_log(f"Extracting title for policy {policy_index}", 'DEBUG')

    title_methods = [
        # Method 1: title attribute
        lambda e: e.get_attribute('title'),
        # Method 2: aria-label attribute
        lambda e: e.get_attribute('aria-label'),
        # Method 3: text content
        lambda e: e.text,
        # Method 4: Look for nested text elements
        lambda e: extract_nested_text(e),
        # Method 5: Look for specific text patterns
        lambda e: extract_from_onclick_or_href(e)
    ]

    for method_num, method in enumerate(title_methods, 1):
        try:
            raw_title = method(element)
            debug_log(f"Method {method_num} raw result: '{raw_title}'", 'VERBOSE')

            if raw_title and raw_title.strip():
                # Clean up the title
                clean_title = clean_policy_title(raw_title)
                if clean_title and len(clean_title.strip()) > 2:  # Minimum meaningful length
                    debug_log(f"Successfully extracted title with method {method_num}: '{clean_title}'", 'DEBUG')
                    return clean_title

        except Exception as e:
            debug_log(f"Title extraction method {method_num} failed: {e}", 'VERBOSE')
            continue

    # Final fallback: generate a descriptive name
    fallback_title = f"정책_{policy_index}번"
    debug_log(f"All methods failed, using fallback: '{fallback_title}'", 'WARNING')
    return fallback_title

def extract_nested_text(element):
    """Extract text from nested elements"""
    try:
        # Look for common text containers
        text_selectors = [
            '.policy-title',
            '.title',
            'span',
            'div',
            'p'
        ]

        for selector in text_selectors:
            try:
                nested_element = element.find_element(By.CSS_SELECTOR, selector)
                text = nested_element.text.strip()
                if text and len(text) > 2:
                    return text
            except:
                continue

        return None
    except Exception:
        return None

def extract_from_onclick_or_href(element):
    """Extract title from onclick or href attributes"""
    try:
        # Check onclick attribute for title information
        onclick = element.get_attribute('onclick')
        if onclick:
            # Look for patterns that might contain title
            import re
            matches = re.findall(r"'([^']{10,})'", onclick)
            for match in matches:
                if '정책' in match or '지원' in match or '사업' in match:
                    return match

        # Check href attribute
        href = element.get_attribute('href')
        if href:
            # Extract meaningful part from URL
            import urllib.parse
            parsed = urllib.parse.urlparse(href)
            query_params = urllib.parse.parse_qs(parsed.query)
            # Look for title-like parameters
            for key, values in query_params.items():
                if 'title' in key.lower() or 'name' in key.lower():
                    if values and values[0]:
                        return urllib.parse.unquote(values[0])

        return None
    except Exception:
        return None

def clean_policy_title(raw_title):
    """Clean and normalize policy title"""
    if not raw_title:
        return None

    # Remove common suffixes and prefixes
    title = raw_title.strip()

    # Remove "자세히 보기" and variations
    cleanup_patterns = [
        " 자세히 보기",
        "자세히 보기",
        " 자세히보기",
        "자세히보기",
        " 보기",
        "보기",
        " 상세보기",
        "상세보기",
        " 상세정보",
        "상세정보"
    ]

    for pattern in cleanup_patterns:
        title = title.replace(pattern, "")

    # Clean up extra whitespace
    title = " ".join(title.split())

    return title.strip() if title.strip() else None

def debug_found_elements(driver, policy_elements, policy_selectors):
    """Debug information about found policy elements"""
    if not debug_log or DEBUG_LEVELS.get('DEBUG', 3) > CURRENT_DEBUG_LEVEL:
        return

    debug_log(f"Found {len(policy_elements)} total policy elements", 'DEBUG')

    # Test each selector individually to see which ones work
    for i, selector in enumerate(policy_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            debug_log(f"Selector {i+1} '{selector}': {len(elements)} elements", 'DEBUG')

            # Sample first element details
            if elements:
                element = elements[0]
                try:
                    sample_info = {
                        'tag': element.tag_name,
                        'title': element.get_attribute('title'),
                        'aria-label': element.get_attribute('aria-label'),
                        'class': element.get_attribute('class'),
                        'text': element.text[:50] + '...' if len(element.text) > 50 else element.text,
                        'href': element.get_attribute('href')
                    }
                    debug_log(f"Sample element info: {sample_info}", 'VERBOSE')
                except Exception as e:
                    debug_log(f"Error getting sample element info: {e}", 'WARNING')
        except Exception as e:
            debug_log(f"Selector {i+1} failed: {e}", 'DEBUG')

    # Analyze first few policy elements for title extraction
    for i, element in enumerate(policy_elements[:3]):  # Check first 3 elements
        try:
            title_attempts = {
                'title_attr': element.get_attribute('title'),
                'aria_label': element.get_attribute('aria-label'),
                'text_content': element.text,
                'inner_html': element.get_attribute('innerHTML')[:100] if element.get_attribute('innerHTML') else None
            }
            debug_log(f"Element {i+1} title attempts: {title_attempts}", 'VERBOSE')
        except Exception as e:
            debug_log(f"Error analyzing element {i+1}: {e}", 'WARNING')

def analyze_page_structure(driver):
    """Analyze page structure when no policy elements are found"""
    debug_log("Analyzing page structure to find alternative selectors", 'INFO')

    try:
        # Look for common link patterns
        all_links = driver.find_elements(By.TAG_NAME, "a")
        debug_log(f"Found {len(all_links)} total links on page", 'DEBUG')

        # Analyze links that might be policy links
        potential_policy_links = []
        for link in all_links[:20]:  # Check first 20 links
            try:
                text = link.text.strip()
                title = link.get_attribute('title')
                href = link.get_attribute('href')
                onclick = link.get_attribute('onclick')

                # Look for patterns that indicate policy links
                if any(keyword in str(text).lower() + str(title).lower() + str(href).lower() + str(onclick).lower()
                       for keyword in ['정책', '사업', '지원', '복지', 'detail', 'view', '보기']):
                    potential_policy_links.append({
                        'text': text[:50],
                        'title': title,
                        'href': href[:100] if href else None,
                        'class': link.get_attribute('class'),
                        'id': link.get_attribute('id')
                    })
            except Exception as e:
                continue

        if potential_policy_links:
            debug_log(f"Found {len(potential_policy_links)} potential policy links:", 'INFO')
            for i, link_info in enumerate(potential_policy_links[:5]):  # Show first 5
                debug_log(f"Potential link {i+1}: {link_info}", 'INFO')
        else:
            debug_log("No potential policy links found with common keywords", 'WARNING')

        # Look for common container patterns
        container_selectors = [
            '.policy-list', '.list-container', '.content-list',
            '[class*="list"]', '[class*="item"]', '[class*="policy"]',
            '.cl-text-wrapper', '.cl-text', '.text-wrapper'
        ]

        for selector in container_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    debug_log(f"Found {len(elements)} elements with selector '{selector}'", 'DEBUG')
                    # Analyze first element
                    if elements:
                        first_elem = elements[0]
                        debug_log(f"Sample {selector} element: tag={first_elem.tag_name}, "
                                f"text='{first_elem.text[:50]}', class='{first_elem.get_attribute('class')}'", 'VERBOSE')
            except Exception as e:
                continue

    except Exception as e:
        debug_log(f"Error analyzing page structure: {e}", 'ERROR')

def is_safe_policy_element(element):
    """Safety check to ensure we're only clicking legitimate policy elements"""
    try:
        # Get element attributes
        href = element.get_attribute('href') or ''
        title = element.get_attribute('title') or ''
        text = element.text or ''
        onclick = element.get_attribute('onclick') or ''
        class_name = element.get_attribute('class') or ''

        # SAFETY BLACKLIST - Never click these
        dangerous_patterns = [
            'certificate', '인증서', '공동인증서',
            'login', '로그인', 'auth', 'sign',
            'export', '내보내기', '다운로드',
            'install', '설치', 'setup'
        ]

        # Check all text content for dangerous patterns
        all_text = (href + title + text + onclick + class_name).lower()

        for pattern in dangerous_patterns:
            if pattern in all_text:
                debug_log(f"SAFETY: Dangerous pattern '{pattern}' found in element: {all_text[:100]}", 'ERROR')
                return False

        # SAFETY WHITELIST - Only click these patterns
        safe_patterns = [
            '자세히 보기', 'detail', 'TWAT52005M',
            '상세보기', '정책', '사업', '지원'
        ]

        has_safe_pattern = any(pattern in all_text for pattern in safe_patterns)

        if not has_safe_pattern:
            debug_log(f"SAFETY: No safe patterns found in element: {all_text[:100]}", 'WARNING')
            return False

        # Additional safety: Must be a link (a tag)
        if element.tag_name.lower() != 'a':
            debug_log(f"SAFETY: Element is not a link: {element.tag_name}", 'WARNING')
            return False

        debug_log(f"SAFETY: Element passed all safety checks", 'DEBUG')
        return True

    except Exception as e:
        debug_log(f"SAFETY: Error checking element safety: {e}", 'ERROR')
        return False


def is_safe_tab_element(element, expected_tab_name):
    """Safety check for tab elements"""
    try:
        # Get element attributes
        text = element.text or ''
        title = element.get_attribute('title') or ''
        class_name = element.get_attribute('class') or ''

        # Combine all text for analysis
        all_text = (text + title + class_name).lower()
        expected_name_lower = expected_tab_name.lower()

        # MUST contain the expected tab name
        if expected_name_lower not in all_text:
            debug_log(f"TAB SAFETY: Expected tab name '{expected_tab_name}' not found: {all_text[:100]}", 'WARNING')
            return False

        # BLACKLIST - Never click these tab-like elements
        forbidden_patterns = [
            'certificate', '인증서', '공동인증서',
            'login', '로그인', 'logout', '로그아웃',
            'install', '설치', 'download', '내보내기'
        ]

        for pattern in forbidden_patterns:
            if pattern in all_text:
                debug_log(f"TAB SAFETY: Forbidden pattern '{pattern}' found: {all_text[:100]}", 'ERROR')
                return False

        debug_log(f"TAB SAFETY: Tab element is safe", 'DEBUG')
        return True

    except Exception as e:
        debug_log(f"TAB SAFETY: Error checking tab safety: {e}", 'ERROR')
        return False

def monitor_browser_state(driver, context=""):
    """Monitor and log browser state for debugging"""
    try:
        current_url = driver.current_url
        page_title = driver.title[:100] + '...' if len(driver.title) > 100 else driver.title
        window_count = len(driver.window_handles)

        debug_log(f"Browser State {context}: URL={current_url}, Title='{page_title}', Windows={window_count}", 'VERBOSE')

        # Check if page has critical elements
        try:
            policies_found = len(driver.find_elements(By.CSS_SELECTOR, "a.cl-text-wrapper[title*='자세히 보기']"))
            pagination_found = len(driver.find_elements(By.XPATH, "//div[contains(@class, 'pageindexer')]" ))
            debug_log(f"Page Elements {context}: Policies={policies_found}, Pagination={pagination_found}", 'VERBOSE')
        except Exception as e:
            debug_log(f"Failed to check page elements {context}", 'WARNING', e)

        return True
    except Exception as e:
        debug_log(f"Browser state monitoring failed {context}", 'ERROR', e)
        return False

def restart_browser_if_needed(driver, wait, processed_count):
    """Restart browser if needed for resource management"""
    RESTART_THRESHOLD = 30  # Restart every 30 processed items (reduced for 101 total items)

    if processed_count > 0 and processed_count % RESTART_THRESHOLD == 0:
        debug_log(f"Browser restart triggered after {processed_count} processed items", 'INFO')
        try:
            driver.quit()
            time.sleep(2)
            new_driver = setup_driver()
            new_wait = WebDriverWait(new_driver, 20)
            debug_log("Browser restarted successfully", 'INFO')
            return new_driver, new_wait
        except Exception as e:
            debug_log("Browser restart failed", 'ERROR', e)
            raise

    return driver, wait

def setup_driver():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": os.path.abspath(DOWNLOAD_DIR),
        "plugins.always_open_pdf_externally": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def load_processed_log():
    """Load processing log with backward compatibility"""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle new format with metadata
                if isinstance(data, dict) and "policies" in data:
                    return data["policies"]
                # Handle old format (direct policy dict)
                elif isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"로그 파일 읽기 오류: {e}")
    return {}

def save_processed_log(log_data):
    """Save processing log with timestamp"""
    # Add metadata to log
    log_with_metadata = {
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_processed": len(log_data),
        "policies": log_data
    }

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_with_metadata, f, ensure_ascii=False, indent=4)

def is_valid_pdf_filename(filename):
    """Validate if the filename represents a PDF file"""
    if not filename:
        return False
    filename_lower = filename.lower().strip()
    return filename_lower.endswith('.pdf') and len(filename_lower) > 4

def find_pdf_elements(driver):
    """Find PDF-related elements using multiple selector strategies"""
    pdf_selectors = [
        # Primary selector - exact match
        "//div[@class='cl-text' and contains(text(), '.pdf')]",
        # Fallback selectors
        "//div[contains(@class, 'cl-text') and contains(text(), '.pdf')]",
        "//span[contains(text(), '.pdf')]",
        "//a[contains(@href, '.pdf')]",
        "//div[contains(text(), '.PDF')]",  # Uppercase extension
        # Alternative patterns
        "//*[contains(text(), '.pdf') or contains(text(), '.PDF')]"
    ]

    download_selectors = [
        # Primary download button selector
        "//div[@class='cl-text' and text()='다운로드']",
        # Fallback selectors
        "//div[contains(@class, 'cl-text') and contains(text(), '다운로드')]",
        "//button[contains(text(), '다운로드')]",
        "//a[contains(text(), '다운로드')]",
        "//input[@type='button' and contains(@value, '다운로드')]"
    ]

    # Try to find PDF filename element
    pdf_element = None
    pdf_filename = None

    for selector in pdf_selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                text = element.text.strip()
                if is_valid_pdf_filename(text):
                    pdf_element = element
                    pdf_filename = text
                    break
            if pdf_element:
                break
        except Exception as e:
            print(f"PDF selector '{selector}' 실패: {e}")
            continue

    # Try to find download button
    download_element = None
    for selector in download_selectors:
        try:
            download_element = driver.find_element(By.XPATH, selector)
            break
        except Exception as e:
            print(f"다운로드 버튼 selector '{selector}' 실패: {e}")
            continue

    return pdf_element, pdf_filename, download_element

def wait_for_download_completion(download_dir, expected_filename=None, timeout=30):
    """Wait for file download to complete and verify it's a valid PDF"""
    import glob

    start_time = time.time()
    initial_files = set(os.listdir(download_dir))

    while time.time() - start_time < timeout:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files

        # Check for completed downloads (no .crdownload or .tmp files)
        completed_downloads = [f for f in new_files if not f.endswith(('.crdownload', '.tmp', '.part'))]

        if completed_downloads:
            latest_file = max(completed_downloads, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
            file_path = os.path.join(download_dir, latest_file)

            # Verify file size and basic PDF structure
            if os.path.getsize(file_path) > 100:  # Minimum size check
                try:
                    with open(file_path, 'rb') as f:
                        header = f.read(4)
                        if header == b'%PDF':
                            return {"status": "success", "filename": latest_file, "filepath": file_path}
                except Exception as e:
                    print(f"PDF 검증 실패: {e}")

        time.sleep(1)

    return {"status": "download_timeout", "message": "다운로드 시간 초과"}

def process_detail_page(driver, wait):
    """Enhanced PDF detection and download with robust error handling"""
    try:
        # Step 1: Navigate to additional info tab
        print("추가정보 탭 클릭 시도...")
        additional_info_selectors = [
            "//a[.//div[text()='추가정보']]",
            "//a[contains(text(), '추가정보')]",
            "//div[contains(@class, 'tab') and contains(text(), '추가정보')]"
        ]

        additional_info_clicked = False
        for selector in additional_info_selectors:
            try:
                element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))

                # SAFETY CHECK: Verify this is actually an "additional info" tab
                if not is_safe_tab_element(element, "추가정보"):
                    debug_log(f"SAFETY: Tab element failed safety check", 'WARNING')
                    continue

                element.click()
                additional_info_clicked = True
                print("추가정보 탭 클릭 성공")
                time.sleep(0.5)  # Initial wait
                wait_for_page_stable(driver, timeout=15)  # Wait for tab content to stabilize
                break
            except (TimeoutException, NoSuchElementException) as e:
                print(f"추가정보 탭 selector '{selector}' 실패: {e}")
                continue

        if not additional_info_clicked:
            return {"status": "nav_error", "message": "추가정보 탭을 찾을 수 없음"}

        # Step 2: Enhanced PDF detection
        print("PDF 파일 검색 중...")
        pdf_element, pdf_filename, download_element = find_pdf_elements(driver)

        if not pdf_element or not pdf_filename:
            # Additional check - look for any downloadable files
            try:
                file_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '첨부') or contains(text(), '파일') or contains(text(), '다운로드')]" )
                if file_elements:
                    print("PDF가 아닌 다른 파일들이 발견됨")
                    return {"status": "no_pdf", "message": "PDF 파일 없음 (다른 파일 형식 존재 가능)"}
                else:
                    return {"status": "no_pdf", "message": "다운로드 가능한 파일 없음"}
            except Exception:
                return {"status": "no_pdf", "message": "PDF 파일 없음"}

        if not download_element:
            return {"status": "download_error", "message": "다운로드 버튼을 찾을 수 없음"}

        print(f"PDF 파일 발견: {pdf_filename}")

        # Step 3: Attempt download with verification
        print("다운로드 시작...")
        try:
            download_element.click()

            # Wait for download completion with verification
            download_result = wait_for_download_completion(DOWNLOAD_DIR, pdf_filename)

            if download_result["status"] == "success":
                print(f"다운로드 완료: {download_result['filename']}")
                return {
                    "status": "success",
                    "filename": download_result["filename"],
                    "original_filename": pdf_filename,
                    "filepath": download_result["filepath"]
                }
            else:
                return download_result

        except Exception as e:
            return {"status": "download_error", "message": f"다운로드 실패: {str(e)}"}

    except Exception as e:
        print(f"PDF 처리 중 예상치 못한 오류: {e}")
        return {"status": "error", "message": f"처리 오류: {str(e)}"}


def get_total_count(driver):
    """Extract the total number of policies from the page"""
    try:
        # Look for the total count element - it should be a number in a cl-text div
        total_count_elements = driver.find_elements(By.XPATH,
            "//div[@class='cl-text' and contains(@style, 'display: table-cell')]")

        # Filter for elements that contain only digits and are reasonable policy counts (50-2000)
        potential_counts = []
        for elem in total_count_elements:
            text = elem.text.strip()
            if text.isdigit():
                count = int(text)
                if 50 <= count <= 2000:  # Reasonable range for policy counts
                    potential_counts.append(count)

        if potential_counts:
            # Take the most reasonable count (usually the smallest reasonable number)
            total_count = min(potential_counts)
            print(f"[총계] 발견된 전체 정책 수: {total_count}")
            return total_count
        else:
            print("[경고] 전체 정책 수를 찾을 수 없습니다.")
            return None

    except Exception as e:
        print(f"[오류] 전체 정책 수 확인 중 오류: {e}")
        return None

def detect_last_page(driver, current_page, strict=False):
    """
    Detect if current page is the last page using multiple indicators
    strict=True: More thorough checking for edge cases
    """
    indicators = []

    try:
        # Indicator 1: Check if next button is disabled
        next_button_disabled = driver.find_elements(By.XPATH,
            "//div[contains(@class, 'cl-pageindexer-next') and contains(@class, 'cl-disabled')]")

        if next_button_disabled:
            indicators.append("next_button_disabled")
            debug_log("Last page indicator: Next button is disabled", 'DEBUG')

        # Indicator 2: Check if we're at page 12 and no higher pages exist
        if current_page >= 12:
            higher_pages = driver.find_elements(By.XPATH,
                f"//div[@class='cl-pageindexer-index' and @data-index > '{current_page}']")
            if not higher_pages:
                indicators.append("no_higher_pages")
                debug_log(f"Last page indicator: No pages higher than {current_page}", 'DEBUG')

        # Indicator 3: Check if current page button is the last in visible range
        all_page_buttons = driver.find_elements(By.XPATH,
            "//div[@class='cl-pageindexer-index']")

        if all_page_buttons:
            max_visible_page = 0
            for button in all_page_buttons:
                try:
                    page_num = int(button.get_attribute('data-index'))
                    max_visible_page = max(max_visible_page, page_num)
                except (ValueError, TypeError):
                    continue

            if current_page == max_visible_page and current_page >= 12:
                indicators.append("highest_visible_page")
                debug_log(f"Last page indicator: Current page {current_page} is highest visible", 'DEBUG')

        # Indicator 4: Check if policies on page are fewer than expected (strict mode)
        if strict:
            try:
                policy_elements = driver.find_elements(By.CSS_SELECTOR,
                    "a[title*=\"자세히 보기\"], a[aria-label*=\"자세히 보기\"], a[href*=\"TWAT52005M\"]")
                policy_count = len(policy_elements)

                if policy_count < 6 and current_page >= 12:  # Fewer policies suggests last page
                    indicators.append("fewer_policies")
                    debug_log(f"Last page indicator: Only {policy_count} policies on page {current_page}", 'DEBUG')
            except Exception as e:
                debug_log(f"Error counting policies for last page detection: {e}", 'WARNING')

        # Decision logic
        if strict:
            # Strict mode: need at least 2 indicators
            is_last = len(indicators) >= 2
        else:
            # Normal mode: next button disabled is strong indicator
            is_last = "next_button_disabled" in indicators or len(indicators) >= 2

        debug_log(f"Last page detection for page {current_page}: indicators={indicators}, is_last={is_last}", 'INFO')
        return is_last

    except Exception as e:
        debug_log(f"Error in last page detection: {e}", 'ERROR')
        # Fallback: if page >= 12, assume it's the last
        return current_page >= 12

def check_pagination_available(driver, current_page):
    """Check if pagination to next page is available with enhanced detection"""
    try:
        next_page = current_page + 1
        debug_log(f"Checking pagination availability: {current_page} → {next_page}", 'DEBUG')

        # Wait for pagination elements to be stable
        time.sleep(1)

        # Get all available page numbers in current view first
        all_page_buttons = driver.find_elements(By.XPATH,
            "//div[@class='cl-pageindexer-index']")

        available_pages = []
        for button in all_page_buttons:
            try:
                page_num = int(button.get_attribute('data-index'))
                available_pages.append(page_num)
            except (ValueError, TypeError):
                continue

        available_pages.sort()
        max_available_page = max(available_pages) if available_pages else current_page
        min_available_page = min(available_pages) if available_pages else current_page

        debug_log(f"Available pages in current range: {available_pages}, range: {min_available_page}-{max_available_page}", 'VERBOSE')

        # First, try to find the specific page number button for next page
        page_button = driver.find_elements(By.XPATH,
            f"//div[@class='cl-pageindexer-index' and @data-index='{next_page}']")

        if page_button and page_button[0].is_enabled():
            debug_log(f"Found direct page number button for {next_page}", 'DEBUG')
            return {'available': True, 'method': 'page_number', 'target': next_page}

        # Special handling for range transitions (when next_page is not in current visible range)
        if next_page > max_available_page:
            debug_log(f"Need to transition to next range. Current max: {max_available_page}, trying for: {next_page}", 'INFO')

            # Try clicking the next button to load the next range
            next_button = driver.find_elements(By.XPATH,
                "//div[contains(@class, 'cl-pageindexer-next')]" )

            if next_button:
                debug_log(f"Found next button for range transition. Classes: {next_button[0].get_attribute('class')}", 'DEBUG')

                try:
                    # Click the next button (even if it appears disabled)
                    driver.execute_script("arguments[0].click();", next_button[0])
                    time.sleep(2)  # Wait for new range to load
                    debug_log("Clicked next button for range transition", 'DEBUG')

                    # Re-scan for available pages in the new range
                    new_page_buttons = driver.find_elements(By.XPATH,
                        "//div[@class='cl-pageindexer-index']")

                    new_available_pages = []
                    for button in new_page_buttons:
                        try:
                            page_num = int(button.get_attribute('data-index'))
                            new_available_pages.append(page_num)
                        except (ValueError, TypeError):
                            continue

                    new_available_pages.sort()
                    debug_log(f"After range transition, new available pages: {new_available_pages}", 'DEBUG')

                    if new_available_pages:
                        # Find the first available page in the new range
                        # This could be page 6, 7, or whatever is actually available
                        first_new_page = min(new_available_pages)

                        # Check if our original target (next_page) is available
                        if next_page in new_available_pages:
                            target_page = next_page
                            debug_log(f"Original target page {next_page} is available in new range", 'DEBUG')
                        else:
                            # Use the first available page in the new range
                            target_page = first_new_page
                            debug_log(f"Original target page {next_page} not found, using first available: {target_page}", 'DEBUG')

                        return {'available': True, 'method': 'page_number', 'target': target_page}
                    else:
                        debug_log("No pages found after range transition", 'WARNING')

                except Exception as e:
                    debug_log(f"Failed to click next button for range transition: {e}", 'WARNING')

        # Check for enabled next button (>) for standard page-by-page transitions
        next_button_enabled = driver.find_elements(By.XPATH,
            "//div[contains(@class, 'cl-pageindexer-next') and not(contains(@class, 'cl-disabled'))]")

        if next_button_enabled and next_button_enabled[0].is_enabled():
            debug_log(f"Found enabled next button for standard transition to {next_page}", 'DEBUG')
            return {'available': True, 'method': 'next_button', 'target': next_page}

        # Enhanced final page detection - check multiple indicators
        is_last_page = detect_last_page(driver, current_page)
        if is_last_page:
            debug_log(f"FINAL PAGE DETECTED at page {current_page}. Stopping pagination.", 'INFO')
            return {'available': False, 'method': None, 'target': None}

        # If we can't find a way forward but haven't reached the theoretical end,
        # check if we're stuck in a loop
        if current_page >= 12:
            debug_log(f"Reached page 12 limit but pagination may be looping. Final check...", 'WARNING')
            # Double-check if this is really the last page
            if detect_last_page(driver, current_page, strict=True):
                return {'available': False, 'method': None, 'target': None}
            else:
                debug_log(f"Page 12+ but not confirmed as last page, allowing one more attempt", 'WARNING')
                return {'available': False, 'method': 'range_transition_needed', 'target': next_page}

        debug_log(f"No more pages available. Current: {current_page}, Max available: {max_available_page}", 'INFO')
        return {'available': False, 'method': None, 'target': None}

    except Exception as e:
        debug_log(f"Pagination check failed for {current_page} → {next_page}", 'ERROR', e)
        return {'available': False, 'method': None, 'target': None}

def run_scraper():
    print("="*60)
    print("📋 BOKJIRO PDF SCRAPER - SAFE MODE")
    print("="*60)
    print("✅ 안전 기능 활성화:")
    print("   - 정책 링크만 클릭 (인증서/로그인 링크 차단)")
    print("   - PDF 파일 자유롭게 다운로드")
    print("   - 추가정보 탭만 접근 (기타 탭 차단)")
    print("   - 정책 클릭 전 안전성 검증")
    print("="*60)

    driver = setup_driver()
    wait = WebDriverWait(driver, 20)
    processed_log = load_processed_log()

    # Track overall progress
    session_start_time = time.time()
    total_processed_count = len(processed_log)
    expected_total = 101  # Known total from user
    expected_pages = 12   # Known total pages from user

    debug_log(f"Starting SAFE scraper session. Already processed: {total_processed_count}/{expected_total}", 'INFO')

    current_page = 1
    total_count = None
    visited_pages = []  # Track visited pages to detect loops
    max_consecutive_failures = 3  # Stop after 3 consecutive page failures

    while True:
        # Detect infinite loops
        if current_page in visited_pages:
            visited_count = visited_pages.count(current_page)
            if visited_count >= 2:
                print(f"\n⚠️ 무한 루프 감지! 페이지 {current_page}를 {visited_count}번 방문했습니다.")
                print("스크래핑을 안전하게 종료합니다.")
                break

        visited_pages.append(current_page)

        # Keep only recent pages to avoid memory issues
        if len(visited_pages) > 20:
            visited_pages = visited_pages[-15:]
        page_load_success = False

        page_url = BASE_URL.replace("page=1", f"page={current_page}")
        print(f"\n--- {current_page} 페이지 스크래핑 시작 ---")
        print(f"[URL] {page_url}")
        
        try:
            page_load_start = time.time()
            debug_log(f"Loading page {current_page}: {page_url}", 'INFO')
            driver.get(page_url)
            time.sleep(0.5)  # Initial wait
            wait_for_page_stable(driver, timeout=20)  # Wait for page to stabilize
            log_timing_info(f"Page {current_page} load", page_load_start)
        except WebDriverException as e:
            print(f"브라우저 get URL 실패: {e}. 브라우저를 재시작하고 같은 페이지부터 다시 시도합니다.")
            driver.quit()
            driver = setup_driver()
            wait = WebDriverWait(driver, 20)
            continue

        if current_page == 1 and total_count is None:
            total_count = get_total_count(driver)
            if total_count:
                print(f"[목표] 전체 {total_count}개 정책 처리 예정")

        # SAFE policy element selectors - only specific, verified patterns
        policy_selectors = [
            "a[title*=\"자세히 보기\"]",  # Primary: title contains "자세히 보기"
            "a[aria-label*=\"자세히 보기\"]",  # Aria label contains "자세히 보기"
            "a[href*=\"TWAT52005M\"]"  # URL pattern for policy details - SAFE
        ]
        # REMOVED DANGEROUS SELECTORS:
        # - "a[onclick*=\"detail\"]" - TOO BROAD, can match certificate links
        # - ".cl-text-wrapper" - TOO GENERAL, can match any wrapper
        # - "a.cl-text-wrapper" - TOO GENERAL
        # - ".policy-item a" - GENERIC, may not exist

        details_button_selector = ", ".join(policy_selectors)
        debug_log(f"Using policy selector: {details_button_selector}", 'DEBUG')
        
        try:
            print("페이지의 정책을 찾는 중...")
            try:
                # Wait for at least 1 policy, but allow for variable number per page
                WebDriverWait(driver, 20).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, details_button_selector)) >= 1
                )
                time.sleep(1)  # Additional wait for all policies to load

                policy_elements = driver.find_elements(By.CSS_SELECTOR, details_button_selector)
                num_policies_on_page = len(policy_elements)
                print(f"현재 페이지에서 {num_policies_on_page}개의 정책을 발견했습니다.")

                # Debug: analyze found elements
                debug_found_elements(driver, policy_elements, policy_selectors)

                # If no elements found, try to analyze page structure
                if num_policies_on_page == 0:
                    analyze_page_structure(driver)

                if num_policies_on_page == 0:
                    print("정책을 찾을 수 없습니다. 다음 페이지로 이동합니다.")
                    page_load_success = True
                    continue

            except TimeoutException:
                print("페이지에서 정책을 찾을 수 없습니다. 스크래핑을 중단합니다.")
                break

            for i in range(num_policies_on_page):
                print(f"\n정책 {i+1}/{num_policies_on_page} 처리 중...")

                # Re-navigate to the page only if needed (not every time)
                current_url = driver.current_url
                if f"page={current_page}" not in current_url:
                    print("페이지가 변경되어 다시 로드합니다.")
                    driver.get(page_url)
                    wait_for_page_stable(driver, timeout=15)

                # Wait for all policy elements to be stable and visible
                try:
                    policy_elements = WebDriverWait(driver, 15).until(
                        lambda d: d.find_elements(By.CSS_SELECTOR, details_button_selector)
                    )

                    if len(policy_elements) <= i:
                        print(f"정책 요소 {i+1}이 없습니다. 페이지를 다시 로드합니다.")
                        driver.get(page_url)
                        wait_for_page_stable(driver, timeout=15)
                        policy_elements = driver.find_elements(By.CSS_SELECTOR, details_button_selector)

                    if len(policy_elements) <= i:
                        print(f"정책 요소 {i+1}을 찾을 수 없습니다. 건너뜁니다.")
                        continue

                except TimeoutException:
                    print(f"정책 요소를 찾을 수 없습니다. 건너뜁니다.")
                    continue

                element_to_click = policy_elements[i]

                # Extract policy title with multiple fallback methods
                policy_title = extract_policy_title(element_to_click, i+1)
                print(f"\n- '{policy_title}' 처리 중...")

                # Skip if we couldn't extract a meaningful title
                if not policy_title or policy_title.strip() == '' or policy_title.startswith('정책_'):
                    print(f"정책 제목을 추출할 수 없습니다 (제목: '{policy_title}'). 요소 상세 분석 후 건너뜁니다.")
                    # Additional debug for problematic elements
                    try:
                        debug_log(f"Problematic element - tag: {element_to_click.tag_name}, "
                                f"class: {element_to_click.get_attribute('class')}, "
                                f"id: {element_to_click.get_attribute('id')}, "
                                f"href: {element_to_click.get_attribute('href')}", 'WARNING')
                    except Exception as e:
                        debug_log(f"Error analyzing problematic element: {e}", 'ERROR')
                    continue

                if policy_title in processed_log:
                    status = processed_log[policy_title].get('status', 'unknown')
                    print(f"이미 처리한 항목입니다 (상태: {status}). 건너뜁니다.")
                    print(f"{current_page}페이지의 ({i + 1}/{num_policies_on_page}) 완료.")
                    continue

                policy_start_time = time.time()
                debug_log(f"Processing policy: {policy_title}", 'INFO')

                click_success = False
                click_attempts = [
                    lambda: element_to_click.click(),
                    lambda: driver.execute_script("arguments[0].click();", element_to_click),
                    lambda: driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", element_to_click),
                ]

                for attempt_num, click_method in enumerate(click_attempts, 1):
                    try:
                        # SAFETY CHECK: Verify this is actually a policy element before clicking
                        if not is_safe_policy_element(element_to_click):
                            debug_log(f"SAFETY: Element failed safety check, skipping", 'ERROR')
                            break

                        # Re-check if element is still valid before clicking
                        if element_to_click.is_enabled() and element_to_click.is_displayed():
                            click_method()
                            click_success = True
                            debug_log(f"Successfully clicked policy {i+1} with method {attempt_num}", 'DEBUG')
                            break
                        else:
                            debug_log(f"Element became invalid, refreshing policy elements", 'WARNING')
                            policy_elements = driver.find_elements(By.CSS_SELECTOR, details_button_selector)
                            if len(policy_elements) > i:
                                element_to_click = policy_elements[i]
                            else:
                                raise Exception("Policy element disappeared")
                    except Exception as e:
                        debug_log(f"Click attempt {attempt_num} failed: {e}", 'WARNING')
                        if attempt_num == len(click_attempts):
                            print(f"모든 클릭 시도가 실패했습니다: {e}")
                            break  # Break from click attempts, but continue to next iteration of policy loop

                if not click_success:
                    print(f"{current_page}페이지의 ({i + 1}/{num_policies_on_page}) 건너뜀 (클릭 실패).")
                    continue

                result = process_detail_page(driver, wait)
                result['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
                result['policy_title'] = policy_title
                processed_log[policy_title] = result
                save_processed_log(processed_log)

                log_timing_info(f"Policy processing: {policy_title}", policy_start_time, f"Status: {result.get('status', 'unknown')}")

                status = result.get('status', 'unknown')
                if status == 'success':
                    print(f"[성공] PDF 다운로드 성공: {result.get('filename', 'unknown')}")
                elif status == 'no_pdf':
                    print(f"[없음] PDF 없음: {result.get('message', 'PDF 파일을 찾을 수 없음')}")
                else:
                    print(f"[오류] 오류 발생: {result.get('message', '알 수 없는 오류')}")

                print(f"{current_page}페이지의 ({i + 1}/{num_policies_on_page}) 완료.")

            page_load_success = True

            # Update and display overall progress
            current_processed_log = load_processed_log()
            total_processed_count = len(current_processed_log)
            progress_percentage = (total_processed_count / expected_total) * 100
            print(f"\n[전체 진행률] {total_processed_count}/{expected_total} ({progress_percentage:.1f}%) | 페이지 {current_page}/{expected_pages}")
            debug_log(f"Page {current_page} completed. Total progress: {total_processed_count}/{expected_total}", 'INFO')

            # Restart browser periodically for stability
            driver, wait = restart_browser_if_needed(driver, wait, total_processed_count)

        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(f"페이지 {current_page} 처리 중 심각한 오류 발생: {e}")
            page_load_success = False
        
        if not page_load_success:
            print(f"페이지 {current_page} 처리에 실패했습니다. 브라우저를 재시작하고 같은 페이지부터 다시 시도합니다.")
            try:
                driver.quit()
            except:
                pass
            driver = setup_driver()
            wait = WebDriverWait(driver, 20)
            continue

        try:
            print(f"\n{current_page} 페이지 완료. 다음 페이지 확인 중...")
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pageindexer')]" )))
            except TimeoutException:
                raise Exception("페이지네이션 컨트롤을 찾을 수 없습니다. 페이지가 비정상적으로 로드되었습니다.")

            pagination_info = check_pagination_available(driver, current_page)

            if not pagination_info['available']:
                print(f"\n{'='*60}")
                print(f"🎉 마지막 페이지 도달! 페이지 {current_page}에서 스크래핑을 완료합니다.")
                print(f"{'='*60}")

                # Final progress update
                final_processed_log = load_processed_log()
                final_count = len(final_processed_log)
                final_percentage = (final_count / expected_total) * 100

                print(f"✅ 최종 진행률: {final_count}/{expected_total} ({final_percentage:.1f}%)")
                print(f"📊 총 처리 페이지: {current_page}/{expected_pages}")

                break

            next_page = pagination_info['target']
            method = pagination_info['method']

            if next_page != current_page + 1:
                print(f"[전략] 다음 페이지로 이동: {current_page} → {next_page} (방법: {method}) [범위 전환]")
            else:
                print(f"[전략] 다음 페이지로 이동: {current_page} → {next_page} (방법: {method})")

            navigation_success = False
            actual_target_page = pagination_info['target']

            if method == 'page_number':
                try:
                    page_button = wait.until(EC.presence_of_element_located(
                        (By.XPATH, f"//div[@class='cl-pageindexer-index' and @data-index='{actual_target_page}']")
                    ))
                    driver.execute_script("arguments[0].click();", page_button)
                    navigation_success = True
                except Exception as e:
                    print(f"[실패] 페이지 번호 버튼 클릭 실패: {e}")
                    raise

            elif method == 'next_button':
                try:
                    next_button = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='cl-pageindexer-next' and not(contains(@class, 'cl-disabled'))]")
                    ))
                    driver.execute_script("arguments[0].click();", next_button)
                    navigation_success = True
                except Exception as e:
                    print(f"[실패] 다음 버튼 클릭 실패: {e}")
                    raise

            if not navigation_success:
                 raise Exception("페이지 네비게이션 클릭에 실패했습니다.")

            current_page = actual_target_page
            time.sleep(1)  # Initial wait
            wait_for_page_stable(driver, timeout=20)  # Wait for page to stabilize

        except Exception as e:
            print(f"페이지 네비게이션 중 예상치 못한 오류: {e}. 브라우저를 재시작하고 현재 페이지부터 다시 시도합니다.")
            try:
                driver.quit()
            except:
                pass
            driver = setup_driver()
            wait = WebDriverWait(driver, 20)
            continue

    driver.quit()

    final_log = load_processed_log()
    session_elapsed_time = time.time() - session_start_time

    print(f"\n{'='*80}")
    print(f"📈 BOKJIRO 스크래핑 완료 보고서")
    print(f"{'='*80}")
    print(f"⏱️ 전체 세션 소요 시간: {session_elapsed_time/60:.1f}분")
    print(f"📄 처리된 총 페이지: {current_page}/{expected_pages}")

    generate_summary_report(final_log, expected_total)
    print(f"\n{'='*80}")
    print("🎊 모든 작업이 성공적으로 완료되었습니다!")
    print(f"{'='*80}")


def generate_summary_report(processed_log, total_count=None):
    """Generate a comprehensive summary report of the scraping session"""
    print("\n" + "="*60)
    print("스크래핑 세션 요약 보고서")
    print("="*60)

    if not processed_log:
        print("처리된 항목이 없습니다.")
        return

    status_counts = {}
    for policy_title, result in processed_log.items():
        status = result.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    total_processed = len(processed_log)
    no_pdf_count = status_counts.get('no_pdf', 0)
    
    print(f"\n[최종 요약]")
    if total_count:
        print(f"총 {total_count}개의 정책 중 {total_processed}개를 확인했습니다.")
    else:
        print(f"총 {total_processed}개의 정책을 확인했습니다.")
        
    print(f"그 중 {no_pdf_count}개는 PDF 파일이 아니었습니다.")
    
    print("\n" + "="*60)


# ============================================
# 데이터 통계 및 관리 함수
# ============================================

def get_data_stats():
    """
    현재 데이터 통계 조회

    Returns:
        dict: 데이터 통계
    """
    stats = {
        'pdf_count': 0,
        'log_size': 0,
        'has_checkpoint': False
    }

    try:
        # PDF 개수
        pdf_dir = os.path.join(os.getcwd(), 'data', 'pdfs', 'bokjiro')
        if os.path.exists(pdf_dir):
            stats['pdf_count'] = len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])

        # 로그 크기
        if os.path.exists(DEBUG_LOG_FILE):
            stats['log_size'] = os.path.getsize(DEBUG_LOG_FILE) / 1024  # KB

        # 체크포인트 여부
        stats['has_checkpoint'] = os.path.exists(CHECKPOINT_FILE)

        return stats

    except Exception as e:
        debug_log("통계 조회 중 오류", 'WARNING', e)
        return stats


def reset_all_data(keep_downloads=False):
    """
    모든 데이터 초기화

    Args:
        keep_downloads: True면 다운로드 파일 유지

    Returns:
        dict: 삭제 통계
    """
    stats = {
        'pdf_files': 0,
        'log_files': 0,
        'checkpoint': False
    }

    try:
        # PDF 파일 삭제
        if not keep_downloads:
            pdf_dir = os.path.join(os.getcwd(), 'data', 'pdfs', 'bokjiro')
            if os.path.exists(pdf_dir):
                pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
                for f in pdf_files:
                    try:
                        os.remove(os.path.join(pdf_dir, f))
                        stats['pdf_files'] += 1
                    except:
                        pass

        # 로그 파일 삭제
        log_files = [LOG_FILE, DEBUG_LOG_FILE]
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    os.remove(log_file)
                    stats['log_files'] += 1
                except:
                    pass

        # 체크포인트 삭제
        if os.path.exists(CHECKPOINT_FILE):
            try:
                os.remove(CHECKPOINT_FILE)
                stats['checkpoint'] = True
            except:
                pass

        return stats

    except Exception as e:
        debug_log("데이터 초기화 중 오류", 'ERROR', e)
        return stats


# ============================================
# 메인 함수
# ============================================

def main():
    """메인 함수 - auto_scraper와 동일한 옵션 제공"""
    global DOWNLOAD_DIR  # global 선언을 함수 맨 위로 이동

    print(f"\n{'='*70}")
    print(f"복지로(Bokjiro) PDF 자동 스크래퍼 v2.0")
    print(f"{'='*70}")
    print(f"✅ 안전 기능 활성화:")
    print(f"   - 정책 링크만 클릭 (인증서/로그인 링크 차단)")
    print(f"   - PDF 파일 자유롭게 다운로드")
    print(f"   - 추가정보 탭만 접근 (기타 탭 차단)")
    print(f"{'='*70}\n")

    # 데이터 통계 표시
    data_stats = get_data_stats()

    print(f"📊 현재 데이터 현황:")
    print(f"   📄 다운로드된 PDF: {data_stats['pdf_count']}개")
    print(f"   📝 로그 크기: {data_stats['log_size']:.1f} KB")
    if data_stats['has_checkpoint']:
        print(f"   💾 체크포인트: 있음")
    print()

    # 초기화 옵션
    if data_stats['pdf_count'] > 0:
        print(f"🔄 초기화 옵션:")
        print(f"   1. 데이터 초기화 (로그만 삭제, PDF 유지)")
        print(f"   2. 완전 초기화 (PDF + 로그 모두 삭제)")
        print(f"   3. 초기화 안 함 (기존 데이터 사용)")
        print()

        reset_option = input("선택 [1/2/3]: ").strip()

        if reset_option == '1':
            # 로그만 초기화
            reset_stats = reset_all_data(keep_downloads=True)
            print(f"\n   ✅ 로그 초기화 완료!")
            print(f"   📄 PDF 파일 {data_stats['pdf_count']}개는 유지됩니다.")
            print(f"   📝 로그 파일: {reset_stats['log_files']}개 삭제")
            print(f"   💾 체크포인트: {'삭제됨' if reset_stats['checkpoint'] else '없음'}\n")

        elif reset_option == '2':
            # 완전 초기화
            confirm = input("⚠️  PDF 파일과 모든 로그가 삭제됩니다. 계속하시겠습니까? [y/n]: ")
            if confirm.lower() == 'y':
                reset_stats = reset_all_data(keep_downloads=False)
                print(f"\n   ✅ 완전 초기화 완료!")
                print(f"   📄 PDF 파일: {reset_stats['pdf_files']}개 삭제")
                print(f"   📝 로그 파일: {reset_stats['log_files']}개 삭제")
                print(f"   💾 체크포인트: {'삭제됨' if reset_stats['checkpoint'] else '없음'}")
                print(f"   ℹ️  완전히 처음 상태로 돌아갑니다.\n")
            else:
                print(f"\n   ℹ️  취소되었습니다. 기존 데이터를 사용합니다.\n")

        else:
            # 초기화 안 함
            print(f"\n   ℹ️  기존 데이터를 사용합니다.\n")
    else:
        print(f"📚 데이터 없음 (새로 시작합니다)\n")

    # 체크포인트 확인
    checkpoint = load_checkpoint()

    if checkpoint:
        print(f"💾 이전 작업을 발견했습니다:")
        print(f"   마지막 페이지: {checkpoint.get('last_page', 'N/A')}")
        print(f"   마지막 정책: {checkpoint.get('last_policy_index', 'N/A')}번째")
        print(f"   타임스탬프: {checkpoint.get('timestamp', 'N/A')}\n")

        resume = input("🔄 이어서 진행하시겠습니까? [y/n]: ")

        if resume.lower() == 'y':
            print(f"\n✅ 재개합니다.\n")
            print(f"{'='*60}\n")
            # 체크포인트 기반 재개는 run_scraper 내부에서 처리
        else:
            print("\n새로 시작합니다.\n")
            # 체크포인트 삭제
            try:
                if os.path.exists(CHECKPOINT_FILE):
                    os.remove(CHECKPOINT_FILE)
            except:
                pass

    # 다운로드 디렉토리 설정
    default_dir = DOWNLOAD_DIR
    print(f"📂 다운로드 폴더 경로")
    print(f"   기본값: {default_dir}")
    download_dir_input = input("   다른 경로 입력 (엔터키: 기본값 사용): ").strip()

    if download_dir_input:
        download_dir = download_dir_input
        # 전역 변수 업데이트
        DOWNLOAD_DIR = download_dir
    else:
        download_dir = default_dir

    # 폴더 생성
    os.makedirs(download_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"✅ 설정 완료")
    print(f"{'='*60}")
    print(f"📍 URL: {BASE_URL}")
    print(f"📂 다운로드 폴더: {download_dir}")
    print(f"{'='*60}\n")

    # Auto-start for automated execution
    # input("엔터키를 누르면 스크래핑을 시작합니다...")
    print(f"🚀 스크래핑을 자동으로 시작합니다...\n")

    # 스크래퍼 실행
    run_scraper()

    print("\n👋 프로그램을 종료합니다.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.\n")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}\n")
        debug_log("프로그램 실행 중 치명적 오류", 'ERROR', e)
