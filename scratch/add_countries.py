with open('paises.html', 'r', encoding='utf-8') as f:
    content = f.read()

# I need to add Canada, USA, Ireland, Switzerland to the countries grid
new_countries = """
    <!-- USA -->
    <div class="card" onclick="openArticle(this)">
      <div>
        <p class="card-cat"><span lang="pt">AMÉRICA DO NORTE</span><span lang="en">NORTH AMERICA</span></p>
        <h2 class="card-title">🇺🇸 <span lang="pt">Estados Unidos da América</span><span lang="en">United States</span></h2>
        <p class="card-desc">
          <span lang="pt">A maior economia mundial e o epicentro dos mercados financeiros e tecnologia.</span>
          <span lang="en">The world's largest economy and epicenter of financial markets and technology.</span>
        </p>
      </div>
      <div class="card-meta">
        <span><span lang="pt">NY, USA</span><span lang="en">NY, USA</span></span>
        <span class="up">ATIVO</span>
      </div>
    </div>

    <!-- Canada -->
    <div class="card" onclick="openArticle(this)">
      <div>
        <p class="card-cat"><span lang="pt">AMÉRICA DO NORTE</span><span lang="en">NORTH AMERICA</span></p>
        <h2 class="card-title">🇨🇦 <span lang="pt">Canadá</span><span lang="en">Canada</span></h2>
        <p class="card-desc">
          <span lang="pt">Um gigante de recursos naturais, forte no setor energético e metais preciosos.</span>
          <span lang="en">A natural resources giant, strong in the energy sector and precious metals.</span>
        </p>
      </div>
      <div class="card-meta">
        <span><span lang="pt">TOR, CAN</span><span lang="en">TOR, CAN</span></span>
        <span class="up">ATIVO</span>
      </div>
    </div>

    <!-- Switzerland -->
    <div class="card" onclick="openArticle(this)">
      <div>
        <p class="card-cat"><span lang="pt">EUROPA</span><span lang="en">EUROPE</span></p>
        <h2 class="card-title">🇨🇭 <span lang="pt">Suíça</span><span lang="en">Switzerland</span></h2>
        <p class="card-desc">
          <span lang="pt">O centro bancário global e um refúgio histórico de estabilidade para o ouro e capitais.</span>
          <span lang="en">The global banking center and a historical safe haven for gold and capital.</span>
        </p>
      </div>
      <div class="card-meta">
        <span><span lang="pt">ZUR, CHE</span><span lang="en">ZUR, CHE</span></span>
        <span class="up">ATIVO</span>
      </div>
    </div>

    <!-- Ireland -->
    <div class="card" onclick="openArticle(this)">
      <div>
        <p class="card-cat"><span lang="pt">EUROPA</span><span lang="en">EUROPE</span></p>
        <h2 class="card-title">🇮🇪 <span lang="pt">Irlanda</span><span lang="en">Ireland</span></h2>
        <p class="card-desc">
          <span lang="pt">Polo tecnológico europeu com forte presença de multinacionais e investimento estrangeiro.</span>
          <span lang="en">European tech hub with a strong presence of multinationals and foreign investment.</span>
        </p>
      </div>
      <div class="card-meta">
        <span><span lang="pt">DUB, IRL</span><span lang="en">DUB, IRL</span></span>
        <span class="up">ATIVO</span>
      </div>
    </div>
"""

# Let's see if Phase 2 is mentioned in the file
import re
if '<!-- Phase 2 Countries' in content:
    content = re.sub(r'<!-- Phase 2 Countries.*?-->', new_countries, content, flags=re.DOTALL)
else:
    # Just append before the closing </section> of cards-3
    idx = content.find('</section>')
    if idx != -1:
        content = content[:idx] + new_countries + '\n  ' + content[idx:]

with open('paises.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
