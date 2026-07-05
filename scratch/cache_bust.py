import os

html_files = [
    "artigo-2.html",
    "desporto.html",
    "disclaimer.html",
    "economia.html",
    "geopolitica.html",
    "index.html",
    "mercados.html",
    "noticias.html",
    "ouro.html",
    "paises.html",
    "sobre.html",
    "tech.html",
    "terminal.html"
]

for filename in html_files:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace style.css link with cache-busting version
        updated_content = content.replace('href="style.css"', 'href="style.css?v=2"')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Updated {filename}")
    else:
        print(f"File not found: {filename}")
