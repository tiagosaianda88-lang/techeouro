import os
with open('scripts/update_news.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace PublisherAgent card rendering
old_meta = """  <div class="card-meta" onclick="event.stopPropagation();">
    <span>{date_html}</span>
    <span><span lang="pt">Fonte: </span><span lang="en">Source: </span><a href="{esc["url"]}" target="_blank" rel="noopener noreferrer" style="color: #d4af37; text-decoration: underline;">{esc["source"]}</a></span>
    <span><a href="{link}" style="color: inherit; text-decoration: none;"><span lang="pt">VER ANÁLISE →</span><span lang="en">VIEW ANALYSIS →</span></a></span>
  </div>"""

new_meta = """  <div class="card-meta" onclick="event.stopPropagation();">
    <div style="display: flex; gap: 10px; width: 100%; justify-content: space-between; flex-wrap: wrap;">
      <div>
        <span>{date_html} | </span>
        <span><a href="{esc["url"]}" target="_blank" rel="noopener noreferrer" style="color: #d4af37; text-decoration: underline;">{esc["source"]}</a></span>
      </div>
      <div style="display: flex; gap: 8px;">
        <a href="https://wa.me/?text=Olha%20esta%20not%C3%ADcia%3A%20{esc['url']}" target="_blank" rel="noopener noreferrer" style="background: #25D366; color: white; padding: 2px 8px; border-radius: 4px; text-decoration: none; font-weight: bold;">WhatsApp</a>
        <a href="{link}" style="background: var(--gold); color: black; padding: 2px 8px; border-radius: 4px; text-decoration: none; font-weight: bold;"><span lang="pt">LER TUDO</span><span lang="en">READ ALL</span></a>
      </div>
    </div>
  </div>"""

content = content.replace(old_meta, new_meta)

with open('scripts/update_news.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Publisher updated.")
