import sys
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

TARGET_URL = "https://www.techeouro.net"

class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "img" and "src" in attrs_dict:
            self.assets.append(attrs_dict["src"])
        elif tag == "link" and "rel" in attrs_dict and "stylesheet" in attrs_dict["rel"] and "href" in attrs_dict:
            self.assets.append(attrs_dict["href"])
        elif tag == "script" and "src" in attrs_dict:
            self.assets.append(attrs_dict["src"])

def check_url(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status
    except Exception as e:
        print(f"Error checking {url}: {e}")
        return None

def main():
    print(f"Starting health check for {TARGET_URL}...")
    
    # 1. Check main page
    try:
        req = urllib.request.Request(
            TARGET_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.status
            html_content = response.read().decode('utf-8')
    except Exception as e:
        print(f"CRITICAL: Failed to load target URL {TARGET_URL}: {e}")
        sys.exit(1)
        
    if status != 200:
        print(f"CRITICAL: Target URL returned status {status}")
        sys.exit(1)
        
    print("Main page is loaded successfully (200 OK).")

    # 2. Parse assets (images, stylesheets, scripts)
    parser = AssetParser()
    parser.feed(html_content)
    
    # Remove duplicates and query parameters for clean check
    unique_assets = list(set(parser.assets))
    failed_assets = []
    
    print(f"Found {len(unique_assets)} unique assets to verify...")
    
    for asset in unique_assets:
        # Ignore external links or empty links
        if asset.startswith("http://") or asset.startswith("https://"):
            asset_url = asset
        elif asset.startswith("//"):
            asset_url = "https:" + asset
        else:
            # Resolve relative link
            # Clean query parameters like ?v=3 for checking raw file
            clean_asset = asset.split('?')[0]
            asset_url = urljoin(TARGET_URL, clean_asset)
            
        print(f"Verifying asset: {asset_url}")
        asset_status = check_url(asset_url)
        
        if asset_status != 200:
            print(f"WARNING: Asset {asset} failed check (Status: {asset_status})")
            failed_assets.append(asset)
            
    if failed_assets:
        print("\nCRITICAL: The following assets are missing or failed to load:")
        for fa in failed_assets:
            print(f" - {fa}")
        sys.exit(1)
        
    print("\nSUCCESS: Website health check passed. All pages and assets are fully online!")
    sys.exit(0)

if __name__ == "__main__":
    main()
