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

// Automatically load the user's preferred language when the page loads
document.addEventListener('DOMContentLoaded', () => {
  const savedLang = localStorage.getItem('site-lang') || 'pt';
  setLanguage(savedLang);
});
