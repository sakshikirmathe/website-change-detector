import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, SSLError
import ssl

# Test URLs
urls = [
    "https://suit.cibil.com/",
    "https://affidavit.eci.gov.in/"
]

for url in urls:
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"{'='*60}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (WebsiteChangeDetector/1.0)"
        }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Content Length: {len(response.text)} bytes")
        print(f"✓ Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
        print(f"✓ Success! URL is accessible")
        
    except Timeout:
        print(f"✗ TIMEOUT ERROR: Server took too long to respond (>10 seconds)")
        
    except ConnectionError as e:
        print(f"✗ CONNECTION ERROR: {str(e)}")
        
    except SSLError as e:
        print(f"✗ SSL/CERTIFICATE ERROR: {str(e)}")
        print(f"  This means the website's SSL certificate has issues")
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP ERROR: {str(e)}")
        
    except Exception as e:
        print(f"✗ UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")

# Try with additional options for stubborn sites
print(f"\n\n{'='*60}")
print("Testing with SSL verification disabled (less secure)...")
print(f"{'='*60}")

for url in urls:
    print(f"\nTesting: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(
            url, 
            headers=headers, 
            timeout=15, 
            allow_redirects=True,
            verify=False  # Disable SSL verification
        )
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Size: {len(response.text)} bytes")
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
