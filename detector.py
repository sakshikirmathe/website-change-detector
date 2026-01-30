import requests
import hashlib
import re


def normalize_content(content: str) -> str:
    """
    Normalize webpage content to reduce false positives.
    - Remove extra whitespace
    - Collapse multiple spaces
    """
    content = content.strip()
    content = re.sub(r"\s+", " ", content)
    return content


def get_page_hash(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (WebsiteChangeDetector/1.0)"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    normalized_content = normalize_content(response.text)
    return hashlib.sha256(
        normalized_content.encode("utf-8")
    ).hexdigest()
