// Tech & Ouro · Global Language Switcher System
function setLanguage(lang) {
  const activeLang = lang === 'en' ? 'en' : 'pt';
  const isEnglish = activeLang === 'en';
  const btnEn = document.getElementById('lang-btn-en');
  const btnPt = document.getElementById('lang-btn-pt');

  document.documentElement.lang = activeLang;
  document.body.classList.toggle('lang-en', isEnglish);

  if (btnEn) {
    btnEn.classList.toggle('active', isEnglish);
    btnEn.setAttribute('aria-pressed', String(isEnglish));
  }
  if (btnPt) {
    btnPt.classList.toggle('active', !isEnglish);
    btnPt.setAttribute('aria-pressed', String(!isEnglish));
  }

  localStorage.setItem('site-lang', activeLang);
  document.dispatchEvent(new CustomEvent('site-language-change', {
    detail: { lang: activeLang }
  }));
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
  initMobileMenuAccessibility();
  normalizeSourceLinks();
  applyBalancedCardGrids();
  initArticleInteractions();
  initAdSenseSlots();
  updateHeaderPrices();
  updateCryptoList();
  setInterval(updateHeaderPrices, 90000);
  setInterval(updateCryptoList, 120000);
});

// Toggle Mobile Menu for responsive navigation
function toggleMobileMenu() {
  const navLinks = document.querySelector('.nav-links');
  const menuBtn = document.querySelector('.mobile-menu-btn');
  if (!navLinks || !menuBtn) return;
  const isOpen = navLinks.classList.toggle('active');
  menuBtn.classList.toggle('active', isOpen);
  menuBtn.setAttribute('aria-expanded', String(isOpen));
}

function initMobileMenuAccessibility() {
  const navLinks = document.querySelector('.nav-links');
  const menuBtn = document.querySelector('.mobile-menu-btn');
  if (!navLinks || !menuBtn) return;
  if (!navLinks.id) navLinks.id = 'primary-navigation';
  menuBtn.setAttribute('aria-controls', navLinks.id);
  menuBtn.setAttribute('aria-expanded', String(navLinks.classList.contains('active')));
  menuBtn.setAttribute('aria-label', 'Menu');
}

function applyBalancedCardGrids() {
  const grids = document.querySelectorAll('.cards-2, .cards-3');
  grids.forEach(grid => {
    const cards = [...grid.querySelectorAll(':scope > .card:not(.in-feed-ad)')];
    cards.forEach(card => {
      card.classList.remove('index-final-row', 'balanced-extra-hidden', 'balanced-last-card');
    });

    if (document.body.classList.contains('home')) {
      cards.slice(-2).forEach(card => card.classList.add('index-final-row'));
      if (cards.length % 2 === 1) cards[cards.length - 1].classList.add('balanced-last-card');
    }
  });
}

function escapeModalHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[char]);
}

function safeModalUrl(value) {
  if (!value) return '';
  try {
    const url = new URL(value, window.location.href);
    return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
  } catch {
    return '';
  }
}

function safeExternalStoryUrl(value) {
  const url = safeModalUrl(value);
  if (!url) return '';

  try {
    const parsed = new URL(url);
    const current = new URL(window.location.href);
    if (parsed.origin === current.origin) return '';
    return url;
  } catch {
    return '';
  }
}

function safeSpecificSourceUrl(value) {
  const url = safeExternalStoryUrl(value);
  if (!url) return '';

  try {
    const parsed = new URL(url);
    const host = parsed.hostname.toLowerCase().replace(/^www\./, '');
    const path = parsed.pathname.replace(/\/+$/, '');
    const parts = path.split('/').filter(Boolean);

    if (host === 'news.google.com') {
      return /\/(?:rss\/)?articles\//.test(path) ? url : '';
    }
    if (host.endsWith('reuters.com') && parts.length <= 2) return '';
    if ((host.includes('bbc.co.uk') || host.includes('bbc.com')) && (
      parts.length <= 2 || ['uk', 'science-environment'].includes(parts[parts.length - 1])
    )) return '';
    if (host.endsWith('infomoney.com.br') && parts.length <= 1) return '';
    if (parts.length < 2) return '';
    return url;
  } catch {
    return '';
  }
}

function normalizeSourceLinks() {
  document.querySelectorAll('.source-attribution a').forEach(link => {
    const wrapper = link.closest('.source-attribution');
    if (!wrapper) return;
    wrapper.dataset.sourceName = link.textContent.trim();
    wrapper.dataset.sourceUrl = link.href;

    if (safeSpecificSourceUrl(link.href)) {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      return;
    }

    const sourceName = document.createElement('span');
    sourceName.className = 'source-name';
    sourceName.textContent = link.textContent;
    link.replaceWith(sourceName);
  });
}

function initArticleInteractions() {
  if (document.body.dataset.articleInteractionsReady === 'true') return;
  document.body.dataset.articleInteractionsReady = 'true';

  document.addEventListener('click', event => {
    const trigger = event.target.closest('.read-full-link, [data-open-article="true"]');
    if (!trigger) return;

    const card = trigger.closest('.card');
    if (!card) return;

    event.preventDefault();
    event.stopPropagation();
    openArticle(card);
  }, true);
}

function initAdSenseSlots() {
  const slots = document.querySelectorAll('ins.adsbygoogle');
  if (slots.length === 0) return;

  window.adsbygoogle = window.adsbygoogle || [];

  const markSlotEmpty = slot => {
    const holder = slot.closest('.in-feed-ad, .promo-box');
    if (!holder || holder.classList.contains('ad-slot-filled')) return;
    holder.classList.add('ad-slot-empty');
  };

  const syncSlotState = slot => {
    const holder = slot.closest('.in-feed-ad, .promo-box');
    if (!holder) return;

    const status = slot.getAttribute('data-ad-status');
    const isFilled = status === 'filled';

    holder.classList.toggle('ad-slot-filled', isFilled);
    holder.classList.toggle('ad-slot-empty', status === 'unfilled');
  };

  const requestSlot = slot => {
    if (['true', 'error', 'unavailable'].includes(slot.dataset.adsenseRequested)) {
      return true;
    }

    const holder = slot.closest('.in-feed-ad, .promo-box');
    const availableWidth = Math.max(
      slot.getBoundingClientRect().width,
      holder ? holder.getBoundingClientRect().width : 0
    );
    const availableHeight = Math.max(
      slot.getBoundingClientRect().height,
      holder ? holder.getBoundingClientRect().height : 0
    );

    if (availableWidth < 250 || availableHeight < 50) return false;

    slot.dataset.adsenseRequested = 'true';
    try {
      window.adsbygoogle.push({});
    } catch {
      slot.dataset.adsenseRequested = 'error';
      markSlotEmpty(slot);
    }
    return true;
  };

  slots.forEach(slot => {
    syncSlotState(slot);

    const observer = new MutationObserver(() => syncSlotState(slot));
    observer.observe(slot, {
      attributes: true,
      attributeFilter: ['data-ad-status'],
      childList: true,
      subtree: true
    });

    if (slot.dataset.adsenseRequested === 'true') return;

    const holder = slot.closest('.in-feed-ad, .promo-box');
    let sizeObserver = null;
    const requestWhenReady = () => {
      if (!requestSlot(slot)) return;
      if (sizeObserver) sizeObserver.disconnect();
    };

    if (holder && 'ResizeObserver' in window) {
      sizeObserver = new ResizeObserver(requestWhenReady);
      sizeObserver.observe(holder);
    }

    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(requestWhenReady);
    });

    window.setTimeout(() => {
      if (slot.dataset.adsenseRequested === 'true') return;
      if (sizeObserver) sizeObserver.disconnect();
      slot.dataset.adsenseRequested = 'unavailable';
      markSlotEmpty(slot);
    }, 10000);
  });

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
  const sourceAttributionEl = cardEl.querySelector('.source-attribution');
  const sourceLinkEl = cardEl.querySelector('.source-attribution a');
  const editorialPtEl = cardEl.querySelector('.editorial-attribution [lang="pt"]');
  const editorialEnEl = cardEl.querySelector('.editorial-attribution [lang="en"]');

  const catPt = catPtEl ? catPtEl.innerText : (cardEl.querySelector('.card-cat') ? cardEl.querySelector('.card-cat').innerText : 'Geral');
  const catEn = catEnEl ? catEnEl.innerText : catPt;
  const titlePt = titlePtEl ? titlePtEl.innerText : (cardEl.querySelector('.card-title') ? cardEl.querySelector('.card-title').innerText : '');
  const titleEn = titleEnEl ? titleEnEl.innerText : titlePt;
  const descPt = descPtEl ? descPtEl.innerText : (cardEl.querySelector('.card-desc') ? cardEl.querySelector('.card-desc').innerText : '');
  const descEn = descEnEl ? descEnEl.innerText : descPt;
  const sourceName = sourceAttributionEl?.dataset.sourceName || (sourceLinkEl ? sourceLinkEl.innerText : '');
  const sourceUrl = sourceAttributionEl?.dataset.sourceUrl || (sourceLinkEl ? sourceLinkEl.href : '');
  const editorialPt = editorialPtEl ? editorialPtEl.innerText : 'Resumo editorial Tech & Ouro';
  const editorialEn = editorialEnEl ? editorialEnEl.innerText : 'Editorial summary by Tech & Ouro';
  const dateText = dateEl ? dateEl.innerText : 'HOJE / TODAY';
  const specificSourceUrl = safeSpecificSourceUrl(sourceUrl);

  let modal = document.getElementById('article-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'article-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'article-modal-title');
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
    modal.addEventListener('click', event => {
      if (event.target === modal) closeArticleModal();
    });
  }

  modal.innerHTML = `
    <div style="
      background: #0d1117;
      border: 1px solid rgba(201, 162, 39, 0.3);
      border-radius: 8px;
      max-width: 680px;
      width: 100%;
      max-height: 82vh;
      overflow-y: auto;
      padding: 34px;
      position: relative;
      color: #e8f0e4;
      font-family: sans-serif;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    ">
      <button id="article-modal-close" onclick="closeArticleModal()" aria-label="Fechar / Close" style="
        position: absolute;
        top: 16px;
        right: 16px;
        background: none;
        border: 1px solid rgba(201,162,39,0.3);
        color: #d4af37;
        font-size: 1.2rem;
        cursor: pointer;
        width: 40px;
        height: 40px;
        border-radius: 4px;
      ">✕</button>
      
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
          <span lang="pt">${escapeModalHtml(catPt)}</span>
          <span lang="en">${escapeModalHtml(catEn)}</span>
        </span>
        <span style="font-size: 0.8rem; color: #8a9e8a;">${escapeModalHtml(dateText)}</span>
      </div>

      <h1 id="article-modal-title" style="font-size: clamp(1.45rem, 4vw, 2rem); margin-bottom: 20px; color: #e8f0e4; line-height: 1.2; padding-right: 34px;">
        <span lang="pt">${escapeModalHtml(titlePt)}</span>
        <span lang="en">${escapeModalHtml(titleEn)}</span>
      </h1>

      <div style="font-size: 1.03rem; line-height: 1.65; color: #c8d4c4; margin-bottom: 24px; border-left: 3px solid #d4af37; padding-left: 15px;">
        <span lang="pt">${escapeModalHtml(descPt)}</span>
        <span lang="en">${escapeModalHtml(descEn)}</span>
      </div>

      <div style="
        margin: 0 0 20px;
        padding: 14px 16px;
        border-left: 3px solid rgba(212,175,55,0.5);
        background: rgba(212,175,55,0.04);
        color: #d8cfaa;
        display: grid;
        gap: 6px;
        font-size: 0.82rem;
        line-height: 1.45;
      ">
        <div><span lang="pt">${escapeModalHtml(editorialPt)}</span><span lang="en">${escapeModalHtml(editorialEn)}</span></div>
      </div>
      ${sourceName ? `
      <div style="
        margin-top: 16px;
        padding-top: 14px;
        border-top: 1px solid rgba(201,162,39,0.12);
        font-size: 0.78rem;
        color: #8a9e8a;
        line-height: 1.45;
      ">
        <strong style="color:#d4af37;"><span lang="pt">Fonte:</span><span lang="en">Source:</span></strong>
        <span style="color:#c8d4c4;"> ${escapeModalHtml(sourceName)}</span>
        ${specificSourceUrl ? `<div style="margin-top:10px;"><a href="${escapeModalHtml(specificSourceUrl)}" target="_blank" rel="noopener noreferrer" style="color:#d4af37; text-decoration:underline;"><span lang="pt">Consultar artigo original ↗</span><span lang="en">View original article ↗</span></a></div>` : ''}
      </div>` : ''}
      <div style="margin-top: 20px; border-top: 1px solid rgba(201,162,39,0.1); padding-top: 14px; font-size: 0.75rem; color: #5a6e5a; line-height: 1.4;">
        <span lang="pt">Resumo informativo e original. Não constitui aconselhamento financeiro.</span>
        <span lang="en">Original informational summary. This is not financial advice.</span>
      </div>
    </div>
  `;

  modal._returnFocus = document.activeElement;
  modal.style.opacity = '1';
  modal.style.pointerEvents = 'all';
  window.requestAnimationFrame(() => modal.querySelector('#article-modal-close')?.focus());
  
  const activeLang = localStorage.getItem('site-lang') || 'pt';
  setLanguage(activeLang);
}

function closeArticleModal() {
  const modal = document.getElementById('article-modal');
  if (modal) {
    modal.style.opacity = '0';
    modal.style.pointerEvents = 'none';
    if (modal._returnFocus && typeof modal._returnFocus.focus === 'function') {
      modal._returnFocus.focus();
    }
  }
}

document.addEventListener('keydown', event => {
  if (event.key === 'Escape') closeArticleModal();
});

window.openArticle = openArticle;
window.closeArticleModal = closeArticleModal;

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


// Ticker end
// Trigger comment to run GitHub Actions news update

function updateCryptoList() {
  const tableBody = document.getElementById('crypto-table-body');
  if (!tableBody) return;

  const fallback = [
    { name: 'Bitcoin', symbol: 'BTC', price: 107280, chg: 1.20, cap: '2.11 T' },
    { name: 'Ethereum', symbol: 'ETH', price: 4120, chg: 0.85, cap: '494.2 B' },
    { name: 'BNB', symbol: 'BNB', price: 685, chg: -0.45, cap: '99.8 B' },
    { name: 'Solana', symbol: 'SOL', price: 242, chg: 3.12, cap: '112.5 B' },
    { name: 'XRP', symbol: 'XRP', price: 1.68, chg: -1.25, cap: '96.2 B' },
    { name: 'Cardano', symbol: 'ADA', price: 0.88, chg: 0.15, cap: '31.4 B' },
    { name: 'Dogecoin', symbol: 'DOGE', price: 0.42, chg: 5.40, cap: '61.1 B' },
    { name: 'Toncoin', symbol: 'TON', price: 7.20, chg: -0.30, cap: '18.1 B' },
    { name: 'Shiba Inu', symbol: 'SHIB', price: 0.000028, chg: 2.15, cap: '16.5 B' },
    { name: 'Avalanche', symbol: 'AVAX', price: 42.50, chg: 1.80, cap: '17.4 B' }
  ];

  function renderTable(data) {
    let html = '';
    data.forEach((coin, idx) => {
      const colorCls = coin.chg >= 0 ? '#10B981' : '#EF4444';
      const sign = coin.chg >= 0 ? '+' : '';
      const priceFormatted = coin.price >= 1 ? coin.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : coin.price.toFixed(6);
      
      html += `
        <tr style="border-bottom: 1px solid var(--border); transition: var(--transition);" onmouseover="this.style.background='rgba(255,255,255,0.01)'" onmouseout="this.style.background='none'">
          <td style="padding: 14px 8px; color: var(--muted); font-weight: 600;">${idx + 1}</td>
          <td style="padding: 14px 8px; font-weight: bold; color: var(--text);">
            ${coin.name} <span style="font-size: 0.75rem; color: var(--muted); margin-left: 6px; font-weight: normal;">${coin.symbol.toUpperCase()}</span>
          </td>
          <td style="padding: 14px 8px; text-align: right; font-weight: 600; color: var(--text);">$${priceFormatted}</td>
          <td style="padding: 14px 8px; text-align: right; font-weight: 600; color: ${colorCls};">${sign}${coin.chg.toFixed(2)}%</td>
          <td style="padding: 14px 8px; text-align: right; color: var(--text-secondary);">${coin.cap}</td>
        </tr>
      `;
    });
    tableBody.innerHTML = html;
  }

  // Try fetching from CoinGecko
  fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false')
    .then(r => r.json())
    .then(d => {
      if (Array.isArray(d) && d.length > 0) {
        const formatted = d.map(coin => ({
          name: coin.name,
          symbol: coin.symbol,
          price: coin.current_price,
          chg: coin.price_change_percentage_24h || 0,
          cap: coin.market_cap >= 1e12 ? (coin.market_cap / 1e12).toFixed(2) + ' T' : (coin.market_cap / 1e9).toFixed(1) + ' B'
        }));
        renderTable(formatted);
      } else {
        renderTable(fallback);
      }
    })
    .catch(() => {
      renderTable(fallback);
    });
}
