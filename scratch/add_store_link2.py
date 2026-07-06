import glob

html_files = glob.glob('*.html')
for file in html_files:
    if file == 'terminal.html' or file == 'loja.html':
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to add Loja to the nav-links
    # Let's find: <li><a href='/sobre'>
    import re
    if '<li><a href="/loja"' not in content and "<li><a href='/loja'" not in content:
        content = re.sub(r'<li><a href=[\'"]/sobre[\'"]>', r'<li><a href="/loja" style="color: var(--gold); font-weight: bold;"><span lang="pt">Loja</span><span lang="en">Store</span></a></li>\n      <li><a href="/sobre">', content)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

print("Done")
