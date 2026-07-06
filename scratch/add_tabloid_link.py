import glob
import re

html_files = glob.glob('*.html')
for file in html_files:
    if file == 'terminal.html' or file == 'tabloides.html':
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '<li><a href="/tabloides"' not in content:
        content = re.sub(r'<li><a href=[\'"]desporto.html[\'"]>', r'<li><a href="/tabloides" style="color: #ff3333; font-weight: bold;"><span lang="pt">Exclusivos</span><span lang="en">Tabloids</span></a></li>\n      <li><a href="desporto.html">', content)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

print("Nav updated")
