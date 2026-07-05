import os
import re

for filename in os.listdir('.'):
    if filename.endswith('.html'):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace <p class="card-desc"> with <div class="card-desc">
        content = re.sub(r'<p class="card-desc">', r'<div class="card-desc">', content)
        content = re.sub(r'</p>\s*</div>\s*<div class="card-meta"', r'</div>\n  </div>\n  <div class="card-meta"', content)
        # We need a safer regex.
        
        # Actually, let's just do simple string replacements where possible, but we need to close the div instead of p.
        # It's better to use regex to find <p class="card-desc">...</p> and replace the tags.
        content = re.sub(r'<p class="card-desc">(.*?)</p>', r'<div class="card-desc">\1</div>', content, flags=re.DOTALL)
        content = re.sub(r'<h2 class="card-title">(.*?)</h2>', r'<div class="card-title">\1</div>', content, flags=re.DOTALL)
        
        # Also in update_news.py
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

with open('scripts/update_news.py', 'r', encoding='utf-8') as f:
    py_content = f.read()
    py_content = re.sub(r'<p class="card-desc">', r'<div class="card-desc">', py_content)
    py_content = re.sub(r'</p>\s*</div>\s*<div class="card-meta"', r'</div>\n  </div>\n  <div class="card-meta"', py_content) # dangerous
    
    # safer:
    py_content = py_content.replace('<p class="card-desc">', '<div class="card-desc">')
    py_content = py_content.replace('</p>\n  </div>\n  <div class="card-meta"', '</div>\n  </div>\n  <div class="card-meta"')
    py_content = py_content.replace('<h2 class="card-title">', '<div class="card-title">')
    py_content = py_content.replace('</h2>\n    <div class="card-desc">', '</div>\n    <div class="card-desc">')
    py_content = py_content.replace('</h2>\n    <p class="card-desc">', '</div>\n    <p class="card-desc">')

with open('scripts/update_news.py', 'w', encoding='utf-8') as f:
    f.write(py_content)
print("Done")
