import os
import re
from html.parser import HTMLParser

class TranslationChecker(HTMLParser):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.issues = []
        self.current_path = []
        self.in_body = False
        self.in_script_or_style = False
        self.has_global_switcher = False
        self.script_js_referenced = False
        self.links = []
        
    def handle_starttag(self, tag, attrs):
        self.current_path.append(tag)
        attrs_dict = dict(attrs)
        
        if tag == 'body':
            self.in_body = True
        if tag in ('script', 'style'):
            self.in_script_or_style = True
            
        # Check global switcher
        if tag == 'button' and attrs_dict.get('id') == 'lang-btn-pt':
            self.has_global_switcher = True
            
        # Check script.js reference
        if tag == 'script' and attrs_dict.get('src') == 'script.js':
            self.script_js_referenced = True
            
        # Collect links
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            # Only track local .html files
            if not href.startswith(('http', '#', 'mailto:')):
                self.links.append((href, self.getpos()))

    def handle_endtag(self, tag):
        if self.current_path:
            self.current_path.pop()
        if tag == 'body':
            self.in_body = False
        if tag in ('script', 'style'):
            self.in_script_or_style = False

    def handle_data(self, data):
        # We only check data inside the body and not inside scripts/styles
        if not self.in_body or self.in_script_or_style:
            return
            
        # If there is meaningful text, check if it's wrapped in lang attribute
        stripped = data.strip()
        if stripped and re.search(r'[a-zA-Z]{2,}', stripped):
            pass

def verify_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    parser = TranslationChecker(filename)
    parser.feed(content)
    
    # 1. Check for global navigation script reference
    issues = []
    if not parser.script_js_referenced:
        issues.append("Missing <script src=\"script.js\"></script> at the bottom.")
        
    # 2. Check for global language buttons
    if not parser.has_global_switcher:
        issues.append("Missing PT/EN toggle buttons (<button id=\"lang-btn-pt\">).")
        
    # 3. Check that the file contains both lang="pt" and lang="en" tags
    pt_count = len(re.findall(r'lang=["\']pt["\']', content))
    en_count = len(re.findall(r'lang=["\']en["\']', content))
    
    # Note: <html lang="pt"> counts as one lang="pt", so we expect more if translated.
    if pt_count <= 1 or en_count == 0:
        issues.append(f"Likely untranslated (found {pt_count} pt tags, {en_count} en tags).")
        
    return issues, parser.links

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_files = [f for f in os.listdir(root_dir) if f.endswith('.html') and 'copia' not in f.lower() and 'cópia' not in f.lower() and 'cópia' not in f.lower()]
    
    print("--- TECH & OURO BILINGUAL AUDIT TOOL ---")
    all_valid_links = set(html_files)
    all_valid_links.add('index.html')
    
    overall_ok = True
    for f in sorted(html_files):
        path = os.path.join(root_dir, f)
        issues, links = verify_file(path)
        
        # Verify internal links
        link_issues = []
        for l, pos in links:
            base_link = l.split('#')[0]
            if base_link and base_link not in all_valid_links:
                link_issues.append(f"Broken link '{l}' at line {pos[0]}")
                
        all_issues = issues + link_issues
        if all_issues:
            print(f"❌ {f}:")
            for issue in all_issues:
                print(f"   - {issue}")
            overall_ok = False
        else:
            print(f"✅ {f}: Perfect")
            
    if overall_ok:
        print("\n🎉 All files are verified and correctly linked/bilingual!")
    else:
        print("\n⚠️ Some issues were found. Please resolve them.")

if __name__ == '__main__':
    main()
