import requests
import hashlib
import re
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from requests.exceptions import HTTPError, SSLError


def normalize_content(content: str) -> str:
    """
    Normalize webpage content to reduce false positives.
    - Remove extra whitespace
    - Collapse multiple spaces
    """
    content = content.strip()
    content = re.sub(r"\s+", " ", content)
    return content


def get_page_hash_with_selenium(url: str) -> str:
    """
    Fallback method using Selenium for websites that block requests library.
    This uses a real Chrome browser to fetch the page.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Get page content
        page_content = driver.page_source
        
        normalized_content = normalize_content(page_content)
        return hashlib.sha256(
            normalized_content.encode("utf-8")
        ).hexdigest()
    finally:
        if driver:
            driver.quit()


def get_page_hash(url: str) -> str:
    """
    Get page hash using requests first, fallback to Selenium for blocked sites.
    """
    # Try with requests first (faster)
    try:
        return get_page_hash_with_requests(url)
    except HTTPError as e:
        # If we get a 403 (Forbidden), try with Selenium
        if "403" in str(e):
            try:
                return get_page_hash_with_selenium(url)
            except Exception as selenium_error:
                # If Selenium also fails, raise the original error
                raise e from selenium_error
        else:
            raise
    except SSLError as e:
        # For SSL errors, try Selenium as fallback
        try:
            return get_page_hash_with_selenium(url)
        except Exception as selenium_error:
            raise e from selenium_error


def get_page_hash_with_requests(url: str) -> str:
    """
    Primary method using requests library (fast).
    """
    # Use a realistic browser User-Agent to bypass bot detection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Referer": url,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none"
    }

    # Add a small delay to look like human behavior
    time.sleep(0.5)

    # Create a session to maintain cookies and connection
    session = requests.Session()
    session.headers.update(headers)

    # Retry logic for better reliability
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = session.get(
                url, 
                timeout=15, 
                allow_redirects=True,
                verify=True  # SSL verification enabled by default
            )
            response.raise_for_status()
            
            normalized_content = normalize_content(response.text)
            return hashlib.sha256(
                normalized_content.encode("utf-8")
            ).hexdigest()
            
        except SSLError as e:
            # If SSL error, retry with verification disabled
            if attempt == 0:
                try:
                    response = session.get(
                        url,
                        timeout=15,
                        allow_redirects=True,
                        verify=False  # Disable SSL verification as fallback
                    )
                    response.raise_for_status()
                    
                    normalized_content = normalize_content(response.text)
                    return hashlib.sha256(
                        normalized_content.encode("utf-8")
                    ).hexdigest()
                except Exception:
                    raise e  # Re-raise original SSL error
            else:
                raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)  # Wait before retrying
