import sys
from pathlib import Path

# Add parent directory to path to import detector
sys.path.insert(0, str(Path(__file__).parent.parent))

from detector import get_page_hash

urls = [
    "https://suit.cibil.com/",
    "https://affidavit.eci.gov.in/"
]

for url in urls:
    print(f"\nTesting: {url}")
    try:
        hash_value = get_page_hash(url)
        print(f"✓ Success! Hash: {hash_value[:16]}...")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
