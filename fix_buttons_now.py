import glob
import re

html_files = glob.glob('/Users/tmss1988/Desktop/netfily/*.html')
for html_file in html_files:
    with open(html_file, 'r') as f:
        html = f.read()
    
    # Fix LER TUDO button link to open the modal
    new_html = re.sub(
        r'<a href="[^"]*"( style="background: var\(--gold\); color: black; padding: )2px 8px([^"]*"><span lang="pt">LER TUDO)',
        r'<a href="javascript:void(0)" onclick="openArticle(this.closest(\'.card\'))"\1 15px 30px\2',
        html
    )
    
    # Fix WhatsApp button padding to match
    new_html = re.sub(
        r'(<a href="https://wa.me/[^"]*"[^>]*style="[^"]*padding:\s*)2px 8px',
        r'\1 15px 30px',
        new_html
    )
    
    if html != new_html:
        with open(html_file, 'w') as f:
            f.write(new_html)
        print(f"Fixed {html_file}")
