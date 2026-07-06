import glob
import os

html_files = glob.glob('*.html')

newsletter_section = """
  <!-- Newsletter Section -->
  <section class="newsletter-section">
    <h2 class="newsletter-title">
      <span lang="pt">Junte-se à Tech & Ouro</span>
      <span lang="en">Join Tech & Ouro</span>
    </h2>
    <p class="newsletter-desc">
      <span lang="pt">Subscreva para receber no seu email as atualizações mais importantes sobre mercados, tecnologia e o futuro do ouro. Sem spam.</span>
      <span lang="en">Subscribe to receive the most important updates on markets, tech, and the future of gold right in your inbox. No spam.</span>
    </p>
    <form class="newsletter-form" name="newsletter" method="POST" data-netlify="true" netlify-honeypot="bot-field">
      <input type="hidden" name="form-name" value="newsletter" />
      <p style="display:none;"><input name="bot-field" /></p>
      <input type="email" name="email" class="newsletter-input" placeholder="O seu email / Your email" required>
      <button type="submit" class="newsletter-btn">
        <span lang="pt">Subscrever</span>
        <span lang="en">Subscribe</span>
      </button>
    </form>
  </section>
"""

footer_newsletter = """
      <div class="footer-desc footer-newsletter">
        <h3 class="newsletter-title" style="font-size: 1rem;"><span lang="pt">Newsletter</span><span lang="en">Newsletter</span></h3>
        <form class="newsletter-form" name="newsletter_footer" method="POST" data-netlify="true" netlify-honeypot="bot-field" style="margin-top: 10px;">
          <input type="hidden" name="form-name" value="newsletter_footer" />
          <p style="display:none;"><input name="bot-field" /></p>
          <input type="email" name="email" class="newsletter-input" placeholder="Email" required style="padding: 8px 12px;">
          <button type="submit" class="newsletter-btn" style="padding: 0 15px;">→</button>
        </form>
      </div>
"""

for file in html_files:
    if file == 'terminal.html':
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the footer description with the footer newsletter in all pages
    if '<div class="footer-desc">' in content and 'newsletter_footer' not in content:
        # Find the footer desc block
        import re
        content = re.sub(r'<div class="footer-desc">.*?</div>', footer_newsletter, content, flags=re.DOTALL)
        
    # Inject the big section only in index.html and sobre.html
    if file in ['index.html', 'sobre.html']:
        if '<div class="content-wrap"' in content and 'newsletter-section' not in content:
            idx = content.find('<div class="content-wrap"')
            if idx != -1:
                content = content[:idx] + newsletter_section + '\n' + content[idx:]
                
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done")
