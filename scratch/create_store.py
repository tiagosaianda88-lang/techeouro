with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace title
content = content.replace('<title>Tech &amp; Ouro — O Diário dos Mercados, Economia e Desporto</title>', '<title>Loja Oficial | Merchandise — Tech &amp; Ouro</title>')

# Remove hero and manifesto
import re
content = re.sub(r'<!-- Hero Section -->.*?</section>', '', content, flags=re.DOTALL)

# Add store hero and grid
store_html = """
  <!-- Store Hero -->
  <header class="page-header" style="position: relative; overflow: hidden; padding-top: 100px;">
    <div class="hero-glow-bg"></div>
    <div class="hero-brand-container lion-propulsion-container" style="margin-bottom: 20px;">
      <img src="JPN.png" alt="Tech & Ouro Golden Lion" style="width: 120px; border-radius: 50%; opacity: 0.9; box-shadow: var(--shadow-gold);">
    </div>
    <p style="font-size: 0.75rem; letter-spacing: 0.2em; color: var(--gold); text-transform: uppercase; margin-bottom: 8px; font-weight: 600;">
      <span lang="pt">Merchandising</span>
      <span lang="en">Official Merch</span>
    </p>
    <h1 class="page-title">
      <span lang="pt">Loja <em>Oficial</em></span>
      <span lang="en">Official <em>Store</em></span>
    </h1>
  </header>
  <div class="gold-line"></div>

  <!-- Store Grid -->
  <section class="cards-3" style="margin-top: 60px;">
    
    <!-- T-Shirts -->
    <div class="card" style="cursor: default;">
      <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 4rem; margin-bottom: 15px;">👕</div>
        <p class="card-cat"><span lang="pt">VESTUÁRIO</span><span lang="en">APPAREL</span></p>
        <h2 class="card-title"><span lang="pt">T-shirts Premium</span><span lang="en">Premium T-shirts</span></h2>
        <p class="card-desc">
          <span lang="pt">Qualidade premium com o Leão Dourado impresso a ouro.</span>
          <span lang="en">Premium quality with the Golden Lion printed in gold.</span>
        </p>
      </div>
      <div class="card-meta" style="justify-content: center;">
        <span style="color: var(--gold); font-weight: bold;"><span lang="pt">EM BREVE</span><span lang="en">COMING SOON</span></span>
      </div>
    </div>

    <!-- Caps -->
    <div class="card" style="cursor: default;">
      <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 4rem; margin-bottom: 15px;">🧢</div>
        <p class="card-cat"><span lang="pt">ACESSÓRIOS</span><span lang="en">ACCESSORIES</span></p>
        <h2 class="card-title"><span lang="pt">Bonés Tech & Ouro</span><span lang="en">Tech & Ouro Caps</span></h2>
        <p class="card-desc">
          <span lang="pt">Design discreto e profissional para investidores e criadores.</span>
          <span lang="en">Discreet and professional design for investors and creators.</span>
        </p>
      </div>
      <div class="card-meta" style="justify-content: center;">
        <span style="color: var(--gold); font-weight: bold;"><span lang="pt">EM BREVE</span><span lang="en">COMING SOON</span></span>
      </div>
    </div>

    <!-- Mugs -->
    <div class="card" style="cursor: default;">
      <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 4rem; margin-bottom: 15px;">☕</div>
        <p class="card-cat"><span lang="pt">COLEÇÃO</span><span lang="en">COLLECTION</span></p>
        <h2 class="card-title"><span lang="pt">Canecas de Mercado</span><span lang="en">Market Mugs</span></h2>
        <p class="card-desc">
          <span lang="pt">Comece o dia a analisar gráficos com a nossa caneca oficial.</span>
          <span lang="en">Start the day analyzing charts with our official mug.</span>
        </p>
      </div>
      <div class="card-meta" style="justify-content: center;">
        <span style="color: var(--gold); font-weight: bold;"><span lang="pt">EM BREVE</span><span lang="en">COMING SOON</span></span>
      </div>
    </div>

  </section>
"""

# Insert the store HTML after the nav
idx = content.find('</nav>')
if idx != -1:
    content = content[:idx+6] + '\n' + store_html + '\n' + content[idx+6:]

with open('loja.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
