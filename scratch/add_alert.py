import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

alert_html = """
  <!-- Breaking News Alert -->
  <div style="background: linear-gradient(90deg, #ff0000, #990000); color: white; text-align: center; padding: 10px; font-weight: bold; letter-spacing: 1px; margin-top: 60px;">
    🚨 <span lang="pt">ALERTA EXCLUSIVO: Movimentações chocantes no mercado identificadas. Leia a nossa análise urgente abaixo.</span>
    <span lang="en">EXCLUSIVE ALERT: Shocking market movements identified. Read our urgent analysis below.</span> 🚨
  </div>
"""

# Insert right after the nav
if '<!-- Breaking News Alert -->' not in content:
    content = content.replace('</nav>', '</nav>\n' + alert_html, 1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

print("Alert added to index.html")
