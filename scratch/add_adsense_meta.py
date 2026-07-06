import glob
import re

html_files = glob.glob('*.html')
meta_tag = '<meta name="google-adsense-account" content="ca-pub-2757348402596933">'

for file in html_files:
    if file == 'terminal.html':
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if meta_tag not in content and '</head>' in content:
        content = content.replace('</head>', f'  {meta_tag}\n</head>', 1)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

print("Meta tags added.")
