import os
import re

HTML_FILES = [
    "desporto.html",
    "disclaimer.html",
    "economia.html",
    "geopolitica.html",
    "mercados.html",
    "noticias.html",
    "ouro.html",
    "paises.html",
    "sobre.html",
    "tech.html"
]

TICKER_HTML = """  <!-- Live Financial Ticker -->
  <div class="ticker-container">
    <div class="ticker-track">
      <div class="ticker-item">XAU/USD (Ouro) <span class="up">$3 327.40 (+0.62%)</span></div>
      <div class="ticker-item">BTC/USD <span class="up">$107 280.00 (+1.20%)</span></div>
      <div class="ticker-item">EUR/USD <span class="dn">1.1342 (-0.30%)</span></div>
      <div class="ticker-item">PSI 20 <span class="up">6 841.20 (+0.40%)</span></div>
      <div class="ticker-item">Prata <span class="up">$37.18 (+0.80%)</span></div>
      <div class="ticker-item">WTI Brent <span class="dn">$77.20 (-0.50%)</span></div>
      <div class="ticker-item">BRK.B <span class="up">$518.40 (+0.30%)</span></div>
      <!-- Duplicate for infinite scrolling -->
      <div class="ticker-item">XAU/USD (Ouro) <span class="up">$3 327.40 (+0.62%)</span></div>
      <div class="ticker-item">BTC/USD <span class="up">$107 280.00 (+1.20%)</span></div>
      <div class="ticker-item">EUR/USD <span class="dn">1.1342 (-0.30%)</span></div>
      <div class="ticker-item">PSI 20 <span class="up">6 841.20 (+0.40%)</span></div>
      <div class="ticker-item">Prata <span class="up">$37.18 (+0.80%)</span></div>
      <div class="ticker-item">WTI Brent <span class="dn">$77.20 (-0.50%)</span></div>
      <div class="ticker-item">BRK.B <span class="up">$518.40 (+0.30%)</span></div>
    </div>
  </div>"""

def enhance_file(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return
        
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Ticker if not present
    if "ticker-container" not in content:
        # Insert right after </nav>
        nav_pattern = re.compile(r"(</nav>)", re.IGNORECASE)
        content = nav_pattern.sub(r"</nav>\n\n" + TICKER_HTML, content, count=1)
        print(f"[{filename}] Added live financial ticker.")

    # 2. Add glow to page-header if not present
    if "hero-glow-bg" not in content:
        header_pattern = re.compile(r"(<header class=\"page-header\">)", re.IGNORECASE)
        replacement = '<header class="page-header" style="position: relative; overflow: hidden;">\n    <div class="hero-glow-bg"></div>'
        content = header_pattern.sub(replacement, content, count=1)
        print(f"[{filename}] Added hero-glow-bg inside page-header.")

    # 3. Add gold line after page-header if not present
    # We look for the closing </header> after page-header
    # Let's find the first page-header block
    header_block_match = re.search(r'(<header class="page-header"[^>]*>.*?</header>)', content, re.DOTALL | re.IGNORECASE)
    if header_block_match:
        header_block = header_block_match.group(1)
        end_idx = content.find(header_block) + len(header_block)
        if "gold-line" not in content[end_idx:end_idx+200]:
            content = content.replace(header_block, header_block + "\n  <div class=\"gold-line\"></div>", 1)
            print(f"[{filename}] Added gold-line separator.")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    for f in HTML_FILES:
        enhance_file(f)
    print("All section pages enhanced successfully!")
