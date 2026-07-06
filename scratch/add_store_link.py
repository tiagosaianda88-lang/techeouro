import glob

html_files = glob.glob('*.html')
for file in html_files:
    if file == 'terminal.html':
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add to nav-links
    if '<li><a href="/loja"' not in content:
        content = content.replace("<li><a href='/sobre'><span lang=\"pt\">Sobre</span><span lang=\"en\">About</span></a></li>", 
                                  "<li><a href='/loja' style='color: var(--gold);'><span lang=\"pt\">Loja</span><span lang=\"en\">Store</span></a></li>\n      <li><a href='/sobre'><span lang=\"pt\">Sobre</span><span lang=\"en\">About</span></a></li>")
                                  
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
print("Done")
