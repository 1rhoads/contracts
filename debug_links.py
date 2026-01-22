import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.dms.myflorida.com/business_operations/state_purchasing/state_contracts_and_agreements/state_term_contract/digital_security_solutions/price_sheets_-_pricing"

try:
    response = requests.get(BASE_URL, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = soup.find_all('a', href=True)
    
    targets = ["Presidio", "ARGO"]
    
    print(f"Scanning for targets: {targets}")
    
    for link in links:
        text = link.get_text(strip=True)
        href = link['href']
        full_url = urljoin(BASE_URL, href)
        
        for t in targets:
            if t.lower() in text.lower():
                print(f"MATCH FOUND: {t}")
                print(f"Text: {text}")
                print(f"Href: {href}")
                print(f"Full: {full_url}")
                
                # Check headers to see content type
                try:
                    head = requests.head(full_url, allow_redirects=True, timeout=10)
                    print(f"Content-Type: {head.headers.get('Content-Type')}")
                except Exception as e:
                    print(f"Head request failed: {e}")
                print("-" * 20)
                
except Exception as e:
    print(f"Error: {e}")
