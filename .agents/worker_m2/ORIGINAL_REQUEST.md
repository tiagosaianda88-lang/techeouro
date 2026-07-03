## 2026-07-03T12:36:19Z

Implement Milestone 2: Pipeline Implementation & Layout Integration.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Tasks:
1. Update RSS_FEEDS in scripts/update_news.py. Configure these active search feeds:
   - Expresso: `https://news.google.com/rss/search?q=when:3d+site:expresso.pt&hl=pt-PT&gl=PT&ceid=PT:pt`
   - Diário de Notícias: `https://news.google.com/rss/search?q=when:3d+site:dn.pt&hl=pt-PT&gl=PT&ceid=PT:pt`
   - Google Wall Street: `https://news.google.com/rss/search?q=when:3d+wall+street&hl=en-US&gl=US&ceid=US:en`
   - MarketWatch: `https://news.google.com/rss/search?q=when:3d+source:marketwatch&hl=en-US&gl=US&ceid=US:en`
   - Barron's: `https://news.google.com/rss/search?q=when:3d+source:barrons&hl=en-US&gl=US&ceid=US:en`
   Restrict RSS_FEEDS to ONLY these 5 active search feeds to keep the news focused and verify active feeds.
2. Propagate URL:
   - In CollectorAgent._collect_manual() in scripts/update_news.py, set `url=f"conteudos/{path.name}"` for manual files.
   - In EditorAgent.edit() prompt inside scripts/update_news.py, add `url` to the required properties (e.g. `category, source, url, title_pt, title_en, summary_pt, summary_en`). Explicitly instruct the model to return the `url` from the source material.
   - In VerifierAgent, add `"url"` to the REQUIRED list.
3. Update Fallback Payload:
   - In `conteudos/manual-news.json`, add `"url"` field to all 6 articles. For example, for the first article from `diario de noticias.txt`, use `"url": "conteudos/diario de noticias.txt"`. For others, use their respective paths.
4. Render Hyperlinks:
   - Update `PublisherAgent._render_article()` to display the news source as a hyperlink. In the `<div class="card-meta">` element, next to the date text (which is `<span lang="pt">HOJE</span><span lang="en">TODAY</span>`), add the source name linked to its original feed `url` inside <span> tags:
     `<span><span lang="pt">Fonte: </span><span lang="en">Source: </span><a href="{esc["url"]}" target="_blank" rel="noopener noreferrer" style="color: #d4af37; text-decoration: underline;">{esc["source"]}</a></span>`
5. Fix Verification & Test Suites:
   - In `scripts/test_update_news.py`, update `valid_payload()` to include `"url": "https://example.com"` in all mock articles.
   - In `scripts/verify_translations.py`, update the link checker at line 38 to exclude `'conteudos/'` links (e.g., change the `startswith` tuple to `('http', '#', 'mailto:', 'conteudos/')`).
6. Build and Run:
   - Run the news pipeline script: `python3 scripts/update_news.py`. Make sure exactly 6 articles are published to `index.html` and `noticias.html`.
   - Run `verify_translations.py` and `test_update_news.py` to verify they pass successfully.
Write your implementation details and command outputs to handoff.md under /Users/tmss1988/Desktop/netfily/.agents/worker_m2 and report when completed.
