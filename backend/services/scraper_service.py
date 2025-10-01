import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from supabase import Client

from .. import crud
from . import rag_service

# --- Settings ---
BASE_URL = "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52005M.do?page=1&orderBy=date&tabId=1&sidoCd=1100000000&period=%EC%9E%84%EC%8B%A0%20%C2%B7%20%EC%B6%9C%EC%82%B0,%EC%98%81%EC%9C%A0%EC%95%84,%EC%95%84%EB%8F%99"
DOWNLOAD_DIR = os.path.join(os.getcwd(), 'data', 'pdfs', 'bokjiro')

def setup_driver():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": os.path.abspath(DOWNLOAD_DIR),
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def clean_policy_title(raw_title):
    """Clean and normalize policy title"""
    if not raw_title:
        return None

    title = raw_title.strip()
    cleanup_patterns = [" 자세히 보기", "자세히 보기", " 보기", "보기"]

    for pattern in cleanup_patterns:
        title = title.replace(pattern, "")

    return " ".join(title.split()).strip() if title.strip() else None

def wait_for_download_completion(download_dir, expected_filename=None, timeout=30):
    """Wait for file download to complete and verify it's a valid PDF"""
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


def find_pdf_elements(driver):
    """Find PDF-related elements using multiple selector strategies"""
    pdf_selectors = [
        "//div[@class='cl-text' and contains(text(), '.pdf')]",
        "//div[contains(@class, 'cl-text') and contains(text(), '.pdf')]",
        "//span[contains(text(), '.pdf')]",
        "//a[contains(@href, '.pdf')]",
        "//div[contains(text(), '.PDF')]",
        "//*[contains(text(), '.pdf') or contains(text(), '.PDF')]"
    ]

    download_selectors = [
        "//div[@class='cl-text' and text()='다운로드']",
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
                if text and text.lower().endswith('.pdf') and len(text) > 4:
                    pdf_element = element
                    pdf_filename = text
                    break
            if pdf_element:
                break
        except Exception:
            continue

    # Try to find download button
    download_element = None
    for selector in download_selectors:
        try:
            download_element = driver.find_element(By.XPATH, selector)
            break
        except Exception:
            continue

    return pdf_element, pdf_filename, download_element


def process_detail_page(driver, wait):
    """Navigate to additional info tab, find PDF, and download it"""
    try:
        # Step 1: Navigate to additional info tab
        print("  → Clicking 추가정보 tab...")
        additional_info_selectors = [
            "//a[.//div[text()='추가정보']]",
            "//a[contains(text(), '추가정보')]",
            "//div[contains(@class, 'tab') and contains(text(), '추가정보')]"
        ]

        additional_info_clicked = False
        for selector in additional_info_selectors:
            try:
                element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                element.click()
                additional_info_clicked = True
                print("  ✓ 추가정보 tab clicked")
                time.sleep(2)
                break
            except (TimeoutException, NoSuchElementException):
                continue

        if not additional_info_clicked:
            return {"status": "nav_error", "message": "추가정보 탭을 찾을 수 없음"}

        # Step 2: Find PDF elements
        print("  → Searching for PDF file...")
        pdf_element, pdf_filename, download_element = find_pdf_elements(driver)

        if not pdf_element or not pdf_filename:
            return {"status": "no_pdf", "message": "PDF 파일 없음"}

        if not download_element:
            return {"status": "download_error", "message": "다운로드 버튼을 찾을 수 없음"}

        print(f"  ✓ PDF found: {pdf_filename}")

        # Step 3: Check if file already exists
        expected_filepath = os.path.join(DOWNLOAD_DIR, pdf_filename)
        if os.path.exists(expected_filepath):
            print(f"  ✓ File already exists: {pdf_filename}")
            return {
                "status": "success",
                "filename": pdf_filename,
                "original_filename": pdf_filename,
                "filepath": expected_filepath,
                "already_existed": True
            }

        # Step 4: Download PDF
        print("  → Starting download...")
        download_element.click()

        # Wait for download completion
        download_result = wait_for_download_completion(DOWNLOAD_DIR, pdf_filename)

        if download_result["status"] == "success":
            print(f"  ✓ Download complete: {download_result['filename']}")
            return {
                "status": "success",
                "filename": download_result["filename"],
                "original_filename": pdf_filename,
                "filepath": download_result["filepath"]
            }
        else:
            return download_result

    except Exception as e:
        print(f"  ✗ Error processing detail page: {e}")
        return {"status": "error", "message": f"처리 오류: {str(e)}"}


def run_scraping(supabase: Client, max_policies: int = 5, skip_rag: bool = True):
    """Main function to run the scraper and download PDFs (without RAG processing)"""
    driver = setup_driver()
    wait = WebDriverWait(driver, 20)

    scraped_policies = []
    processed_count = 0

    # Get list of existing downloaded PDFs to skip duplicates
    existing_pdfs = set()
    if os.path.exists(DOWNLOAD_DIR):
        existing_pdfs = {f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.pdf')}
        print(f"📊 Found {len(existing_pdfs)} existing PDF files in download directory")

    # Get list of existing policies from database
    existing_policies = set()
    try:
        response = supabase.table("policies").select("title").execute()
        existing_policies = {policy["title"] for policy in response.data}
        print(f"📊 Found {len(existing_policies)} existing policies in database")
    except Exception as e:
        print(f"⚠️  Could not fetch existing policies: {e}")

    try:
        print(f"🌐 Navigating to Bokjiro...")
        driver.get(BASE_URL)
        time.sleep(5)

        # Try multiple selectors to find policy links
        policy_selectors = [
            "a[title*='자세히 보기']",
            "a[aria-label*='자세히 보기']",
            "a[href*='TWAT52005M']"
        ]

        policy_links = None
        for selector in policy_selectors:
            try:
                policy_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if policy_links and len(policy_links) > 0:
                    print(f"✅ Found {len(policy_links)} policies using selector: {selector}")
                    break
            except:
                continue

        if not policy_links:
            return {"status": "error", "message": "No policy links found"}

        # Limit to max_policies
        policies_to_process = min(len(policy_links), max_policies)

        for i in range(policies_to_process):
            try:
                # Re-fetch links to avoid stale elements
                for selector in policy_selectors:
                    try:
                        policy_links = driver.find_elements(By.CSS_SELECTOR, selector)
                        if policy_links:
                            break
                    except:
                        continue

                if i >= len(policy_links):
                    break

                link = policy_links[i]

                # Extract title
                raw_title = link.get_attribute('title') or link.text
                policy_title = clean_policy_title(raw_title)

                if not policy_title or len(policy_title) < 3:
                    policy_title = f"정책_{i+1}"

                policy_id = f"bokjiro_{int(time.time())}_{i}"

                print(f"\n📋 [{i+1}/{policies_to_process}] Processing: {policy_title}")

                # Click to detail page
                driver.execute_script("arguments[0].click();", link)
                time.sleep(3)

                # Process detail page to download PDF
                result = process_detail_page(driver, wait)

                if result["status"] == "success":
                    # PDF downloaded successfully
                    pdf_path = result["filepath"]
                    pdf_filename = result["filename"]

                    if result.get("already_existed"):
                        print(f"  ✓ PDF already downloaded, skipping")
                    else:
                        print(f"  ✓ PDF downloaded successfully")

                    scraped_policies.append({
                        "id": policy_id,
                        "title": policy_title,
                        "status": "success",
                        "pdf_filename": pdf_filename,
                        "pdf_path": pdf_path
                    })
                    processed_count += 1

                elif result["status"] == "no_pdf":
                    print(f"  ⚠ No PDF found for this policy")
                    scraped_policies.append({
                        "id": policy_id,
                        "title": policy_title,
                        "status": "no_pdf"
                    })
                else:
                    print(f"  ✗ Failed to download PDF: {result.get('message', 'Unknown error')}")
                    scraped_policies.append({
                        "id": policy_id,
                        "title": policy_title,
                        "status": "download_error",
                        "message": result.get("message")
                    })

                # Go back to list page
                driver.back()
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error processing policy {i+1}: {e}")
                try:
                    driver.get(BASE_URL)
                    time.sleep(3)
                except:
                    pass
                continue

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        driver.quit()
        print(f"\n✅ Scraping completed: {processed_count} policies processed successfully")

    return {"status": "completed", "scraped_policies": scraped_policies, "total_processed": processed_count}
