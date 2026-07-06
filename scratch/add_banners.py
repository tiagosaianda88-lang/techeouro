import glob

html_files = glob.glob('*.html')

banner_html = """
  <!-- Espaco Promocional -->
  <div class="promo-box">
    <div class="promo-box-title">
      <span lang="pt">Espaço Publicitário</span>
      <span lang="en">Sponsored Link</span>
    </div>
    <div class="promo-box-subtitle">
      <span lang="pt">Anuncie aqui as suas soluções de investimento e trading. Contacte-nos.</span>
      <span lang="en">Advertise your investment and trading solutions here. Contact us.</span>
    </div>
  </div>
"""

for file in html_files:
    if file == 'terminal.html':
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '<div class="content-wrap"' in content and 'promo-box' not in content:
        # Insert just before the last content-wrap
        idx = content.rfind('<div class="content-wrap"')
        if idx != -1:
            content = content[:idx] + banner_html + '\n  ' + content[idx:]
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
print("Done")
