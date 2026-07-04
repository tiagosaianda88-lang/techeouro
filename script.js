// Tech & Ouro · Global Language Switcher System
function setLanguage(lang) {
  if (lang === 'en') {
    document.body.classList.add('lang-en');
    const btnEn = document.getElementById('lang-btn-en');
    const btnPt = document.getElementById('lang-btn-pt');
    if (btnEn) btnEn.classList.add('active');
    if (btnPt) btnPt.classList.remove('active');
  } else {
    document.body.classList.remove('lang-en');
    const btnEn = document.getElementById('lang-btn-en');
    const btnPt = document.getElementById('lang-btn-pt');
    if (btnPt) btnPt.classList.add('active');
    if (btnEn) btnEn.classList.remove('active');
  }
  localStorage.setItem('site-lang', lang);
}

// Automatically update the hero date to today's date in PT/EN
function updateHeroDate() {
  const dateElement = document.querySelector('.hero-date');
  if (!dateElement) return;

  const now = new Date();
  
  // Format in Portuguese (e.g. Quinta-feira, 2 de Julho de 2026)
  const optionsPt = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
  let datePt = now.toLocaleDateString('pt-PT', optionsPt);
  datePt = datePt.charAt(0).toUpperCase() + datePt.slice(1);
  
  // Format in English (e.g. Thursday, July 2, 2026)
  const optionsEn = { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' };
  const dateEn = now.toLocaleDateString('en-US', optionsEn);
  
  dateElement.innerHTML = `
    <span lang="pt">${datePt} · Algarve, Portugal</span>
    <span lang="en">${dateEn} · Algarve, Portugal</span>
  `;
}

// Automatically load the user's preferred language when the page loads
function updateDynamicDates() {
  const dateElements = document.querySelectorAll('.dynamic-date');
  if (dateElements.length === 0) return;

  const ptMonths = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'];
  const enMonths = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

  dateElements.forEach(el => {
    const offset = parseInt(el.getAttribute('data-offset') || '0', 10);
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() - offset);

    const day = targetDate.getDate();
    const monthIdx = targetDate.getMonth();
    const year = targetDate.getFullYear();

    const ptFormatted = `${day} ${ptMonths[monthIdx]} ${year}`;
    const enFormatted = `${day} ${enMonths[monthIdx]} ${year}`;

    el.innerHTML = `
      <span lang="pt">${ptFormatted}</span>
      <span lang="en">${enFormatted}</span>
    `;
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const savedLang = localStorage.getItem('site-lang') || 'pt';
  setLanguage(savedLang);
  updateHeroDate();
  updateDynamicDates();
  updateHeaderPrices();
  setInterval(updateHeaderPrices, 90000);
});

// Toggle Mobile Menu for responsive navigation
function toggleMobileMenu() {
  const navLinks = document.querySelector('.nav-links');
  const menuBtn = document.querySelector('.mobile-menu-btn');
  if (navLinks) navLinks.classList.toggle('active');
  if (menuBtn) menuBtn.classList.toggle('active');
}

// Interactive Premium Article Modal Viewer
function openArticle(cardEl) {
  const catPtEl = cardEl.querySelector('.card-cat [lang="pt"]');
  const catEnEl = cardEl.querySelector('.card-cat [lang="en"]');
  const titlePtEl = cardEl.querySelector('.card-title [lang="pt"]');
  const titleEnEl = cardEl.querySelector('.card-title [lang="en"]');
  const descPtEl = cardEl.querySelector('.card-desc [lang="pt"]');
  const descEnEl = cardEl.querySelector('.card-desc [lang="en"]');
  const dateEl = cardEl.querySelector('.dynamic-date') || cardEl.querySelector('.card-meta span:first-child');

  const catPt = catPtEl ? catPtEl.innerText : (cardEl.querySelector('.card-cat') ? cardEl.querySelector('.card-cat').innerText : 'Geral');
  const catEn = catEnEl ? catEnEl.innerText : catPt;
  const titlePt = titlePtEl ? titlePtEl.innerText : (cardEl.querySelector('.card-title') ? cardEl.querySelector('.card-title').innerText : '');
  const titleEn = titleEnEl ? titleEnEl.innerText : titlePt;
  const descPt = descPtEl ? descPtEl.innerText : (cardEl.querySelector('.card-desc') ? cardEl.querySelector('.card-desc').innerText : '');
  const descEn = descEnEl ? descEnEl.innerText : descPt;
  const dateHtml = dateEl ? dateEl.innerHTML : 'HOJE / TODAY';

  let modal = document.getElementById('article-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'article-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(4, 6, 8, 0.95);
      backdrop-filter: blur(10px);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
      padding: 20px;
    `;
    document.body.appendChild(modal);
  }

  modal.innerHTML = `
    <div style="
      background: #0d1117;
      border: 1px solid rgba(201, 162, 39, 0.3);
      border-radius: 8px;
      max-width: 800px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      padding: 40px;
      position: relative;
      color: #e8f0e4;
      font-family: sans-serif;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    ">
      <button onclick="closeArticleModal()" style="
        position: absolute;
        top: 20px;
        right: 20px;
        background: none;
        border: 1px solid rgba(201,162,39,0.3);
        color: #d4af37;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 5px 12px;
        border-radius: 4px;
        transition: all 0.2s;
      " onmouseover="this.style.background='rgba(201,162,39,0.1)'" onmouseout="this.style.background='none'">✕</button>
      
      <div style="margin-bottom: 20px; display: flex; align-items: center; gap: 15px;">
        <span style="
          font-size: 0.7rem;
          font-weight: 700;
          letter-spacing: 0.1em;
          color: #d4af37;
          border: 1px solid rgba(201,162,39,0.4);
          padding: 3px 8px;
          border-radius: 3px;
          text-transform: uppercase;
        ">
          <span lang="pt">${catPt}</span>
          <span lang="en">${catEn}</span>
        </span>
        <span style="font-size: 0.8rem; color: #8a9e8a;">${dateHtml}</span>
      </div>

      <h1 style="font-size: 2rem; margin-bottom: 20px; color: #e8f0e4; line-height: 1.2;">
        <span lang="pt">${titlePt}</span>
        <span lang="en">${titleEn}</span>
      </h1>

      <div style="font-size: 1.1rem; line-height: 1.6; color: #c8d4c4; margin-bottom: 30px; border-left: 3px solid #d4af37; padding-left: 15px; font-style: italic;">
        <span lang="pt">${descPt}</span>
        <span lang="en">${descEn}</span>
      </div>

      <div style="font-size: 1rem; line-height: 1.7; color: #a0b0a0; display: flex; flex-direction: column; gap: 15px;">
        <p>
          <span lang="pt">A nossa equipa editorial está a acompanhar de perto o desenvolvimento desta situação. Mais detalhes técnicos, dados de mercado e gráficos comparativos serão adicionados nas próximas atualizações do portal.</span>
          <span lang="en">Our editorial team is closely monitoring the development of this situation. Additional technical details, market data, and comparative charts will be added in upcoming portal updates.</span>
        </p>
        <p>
          <span lang="pt">Este conteúdo destina-se a fins puramente informativos e de análise de longo prazo. Nenhuma parte deste artigo deve ser interpretada como aconselhamento financeiro ou recomendação profissional.</span>
          <span lang="en">This content is intended purely for informational and long-term analysis purposes. No part of this article should be construed as financial advice or professional recommendation.</span>
        </p>
      </div>
    </div>
  `;

  modal.style.opacity = '1';
  modal.style.pointerEvents = 'all';
  
  const activeLang = localStorage.getItem('site-lang') || 'pt';
  setLanguage(activeLang);
}

function closeArticleModal() {
  const modal = document.getElementById('article-modal');
  if (modal) {
    modal.style.opacity = '0';
    modal.style.pointerEvents = 'none';
  }
}

// Dynamic Header Ticker Price Updater (BTC & EUR/USD)
function updateHeaderPrices() {
  // Update EUR/USD from Frankfurter API
  fetch('https://api.frankfurter.app/latest?from=EUR&to=USD')
    .then(r => r.json())
    .then(d => {
      if (d.rates && d.rates.USD) {
        const rate = d.rates.USD.toFixed(4);
        const tickerItems = document.querySelectorAll('.ticker-item');
        tickerItems.forEach(item => {
          if (item.innerHTML.includes('EUR/USD')) {
            item.innerHTML = `EUR/USD <span class="dn">${rate}</span>`;
          }
        });
      }
    }).catch(() => {});

  // Update BTC/USD from CoinGecko
  fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true')
    .then(r => r.json())
    .then(d => {
      if (d.bitcoin) {
        const price = Math.round(d.bitcoin.usd).toLocaleString('en-US');
        const chg = d.bitcoin.usd_24h_change.toFixed(2);
        const sign = chg >= 0 ? '+' : '';
        const cls = chg >= 0 ? 'up' : 'dn';
        
        // Update top tickers
        const tickerItems = document.querySelectorAll('.ticker-item');
        tickerItems.forEach(item => {
          if (item.innerHTML.includes('BTC/USD')) {
            item.innerHTML = `BTC/USD <span class="${cls}">$${price} (${sign}${chg}%)</span>`;
          }
        });
        
        // Update prices inside ouro.html page if present
        const btcPagePrice = document.querySelector('.btc-spot-price');
        if (btcPagePrice) {
          btcPagePrice.innerHTML = `$${price} <span style="font-size: 0.9rem; margin-left: 10px; color: ${chg >= 0 ? 'var(--up-color, #00ff8c)' : 'var(--down-color, #ff4466)'};">${sign}${chg}% (24h)</span>`;
        }
      }
    }).catch(() => {});
}



