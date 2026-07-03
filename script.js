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
document.addEventListener('DOMContentLoaded', () => {
  const savedLang = localStorage.getItem('site-lang') || 'pt';
  setLanguage(savedLang);
  updateHeroDate();
});

// Toggle Mobile Menu for responsive navigation
function toggleMobileMenu() {
  const navLinks = document.querySelector('.nav-links');
  const menuBtn = document.querySelector('.mobile-menu-btn');
  if (navLinks) navLinks.classList.toggle('active');
  if (menuBtn) menuBtn.classList.toggle('active');
}

