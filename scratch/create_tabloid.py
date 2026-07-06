import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace title
content = content.replace('<title>Tech & Ouro · A Gazeta do Ouro</title>', '<title>Tabloides & Exclusivos — Tech & Ouro</title>')
content = content.replace('<title>Tech &amp; Ouro · A Gazeta do Ouro</title>', '<title>Tabloides & Exclusivos — Tech & Ouro</title>')

# Remove hero section entirely
content = re.sub(r'<!-- Hero Section -->.*?</section>', '', content, flags=re.DOTALL)

# Add Tabloid hero and cards
tabloid_html = """
  <!-- Tabloid Hero -->
  <header class="page-header" style="position: relative; overflow: hidden; padding-top: 100px;">
    <div class="hero-glow-bg" style="background: radial-gradient(circle at 50% -50%, rgba(201, 20, 20, 0.4), transparent 70%);"></div>
    <div class="hero-brand-container" style="margin-bottom: 20px;">
      <h1 class="page-title" style="color: #ff3333; font-size: 3rem; text-transform: uppercase; font-weight: 900; letter-spacing: -1px;">
        <span lang="pt">EXCLUSIVO</span>
        <span lang="en">EXCLUSIVE</span>
      </h1>
    </div>
    <p style="font-size: 0.9rem; letter-spacing: 0.2em; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 8px; font-weight: 600;">
      <span lang="pt">A Verdade dos Mercados</span>
      <span lang="en">The Truth Behind the Markets</span>
    </p>
  </header>
  <div class="gold-line" style="background: linear-gradient(90deg, transparent, #ff3333, transparent);"></div>

  <!-- Tabloid Grid -->
  <section class="cards-3" style="margin-top: 60px;">
    
    <!-- Scandal -->
    <div class="card" onclick="openArticle(this)">
      <div>
        <p class="card-cat" style="color: #ff3333;"><span lang="pt">ESCÂNDALO</span><span lang="en">SCANDAL</span></p>
        <h2 class="card-title"><span lang="pt">O Colapso Secreto do Fundo Suíço que Abanou Londres</span><span lang="en">The Secret Swiss Fund Collapse That Shook London</span></h2>
        <p class="card-desc">
          <span lang="pt">Documentos revelam manobras arriscadas na compra de Ouro e Prata que custaram mil milhões.</span>
          <span lang="en">Documents reveal risky maneuvers in Gold and Silver purchases that cost billions.</span>
        </p>
      </div>
      <div class="card-meta">
        <span><span lang="pt">LONDRES</span><span lang="en">LONDON</span></span>
        <span class="up">LEIA MAIS</span>
      </div>
    </div>

    <!-- Crypto Millionaire -->
    <div class="card" onclick="openArticle(this)">
      <div>
        <p class="card-cat" style="color: #ff3333;"><span lang="pt">FORTUNAS</span><span lang="en">FORTUNES</span></p>
        <h2 class="card-title"><span lang="pt">Jovem de 24 Anos Faz Fortuna de 10M€ em Bitcoin</span><span lang="en">24-Year-Old Makes €10M Fortune in Bitcoin</span></h2>
        <p class="card-desc">
          <span lang="pt">Como um estudante em Dublin previu a subida épica da criptomoeda.</span>
          <span lang="en">How a student in Dublin predicted the epic rise of the cryptocurrency.</span>
        </p>
      </div>
      <div class="card-meta">
        <span><span lang="pt">DUBLIN</span><span lang="en">DUBLIN</span></span>
        <span class="up">LEIA MAIS</span>
      </div>
    </div>

    <!-- Sports Transfer -->
    <div class="card" onclick="openArticle(this)">
      <div>
        <p class="card-cat" style="color: #ff3333;"><span lang="pt">FUTEBOL</span><span lang="en">FOOTBALL</span></p>
        <h2 class="card-title"><span lang="pt">Transferência Relâmpago: 150 Milhões na Premier League</span><span lang="en">Lightning Transfer: 150 Million in the Premier League</span></h2>
        <p class="card-desc">
          <span lang="pt">Negócio fechado à porta fechada na calada da noite. Os valores chocaram o mercado.</span>
          <span lang="en">Deal closed behind closed doors in the dead of night. The figures shocked the market.</span>
        </p>
      </div>
      <div class="card-meta">
        <span><span lang="pt">MANCHESTER</span><span lang="en">MANCHESTER</span></span>
        <span class="up">LEIA MAIS</span>
      </div>
    </div>

  </section>
"""

# Insert the tabloid HTML after the nav
idx = content.find('</nav>')
if idx != -1:
    content = content[:idx+6] + '\n' + tabloid_html + '\n' + content[idx+6:]

with open('tabloides.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
