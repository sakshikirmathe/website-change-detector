import sys
from pathlib import Path
import time

# Add parent directory to path to import detector
sys.path.insert(0, str(Path(__file__).parent.parent))

from detector import get_page_hash

urls = [
    "https://suit.cibil.com/",
    "https://affidavit.eci.gov.in/",
    "https://www.google.com",  # Control test - should be fast with requests
]

for url in urls:
    print(f"\nTesting: {url}")
    try:
        start = time.time()
        hash_value = get_page_hash(url)
        elapsed = time.time() - start
        print(f"✓ Success! Hash: {hash_value[:16]}...")
        print(f"  Time taken: {elapsed:.2f}s")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
