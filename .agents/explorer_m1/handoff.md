# Handoff Report: Tech & Ouro Live News Aggregator Exploration

## 1. Observation

### Feeds Configuration
* **Diário de Notícias & Expresso**: Currently absent from `RSS_FEEDS` in `scripts/update_news.py`. However, `scripts/update_countries.py` (line 30) defines a query search for Portugal's news containing these domains:
  ```python
  "portugal": {
      "name": "Portugal",
      "feed": "https://news.google.com/rss/search?q=when:3d+site:eco.sapo.pt+OR+site:jornaldenegocios.pt+OR+site:dn.pt+OR+site:expresso.pt&hl=pt-PT&gl=PT&ceid=PT:pt"
  }
  ```
* **Existing RSS Feeds**: Confirmed in `scripts/update_news.py` (lines 15-30):
  * **MarketWatch**: `https://news.google.com/rss/search?q=when:3d+source:marketwatch&hl=en-US&gl=US&ceid=US:en` (line 18)
  * **Barron's**: `https://news.google.com/rss/search?q=when:3d+source:barrons&hl=en-US&gl=US&ceid=US:en` (line 19)
  * **Google Wall Street**: `https://news.google.com/rss/search?q=when:3d+wall+street&hl=en-US&gl=US&ceid=US:en` (line 29)

### Source URL Extraction & Agent Propagation
* **CollectorAgent**:
  * RSS items (line 160): Extracts URL via `url=entry.get("link", "")`.
  * Manual items (lines 91, 95, 100): Instantiate `NewsItem(path.name, path.name, ...)` without passing a `url` parameter, defaulting to `""`.
* **EditorAgent**:
  * Prompt definition (lines 205-206) specifies return requirements:
    ```python
    - Each article must contain: category, source, title_pt, title_en,
      summary_pt, summary_en.
    ```
  * Gemini receives selected `NewsItem`s serialized as JSON (containing the `url` field) but does not map/return them.
* **VerifierAgent**:
  * Validation schema (line 221):
    ```python
    REQUIRED = ("category", "source", "title_pt", "title_en", "summary_pt", "summary_en")
    ```
  * Performs verification checks on elements of `REQUIRED` (lines 234-236):
    ```python
    missing = [field for field in self.REQUIRED if not clean_text(article.get(field, ""))]
    if missing:
        raise ValueError(f"Verifier: article {position} missing {', '.join(missing)}")
    ```
* **Fallback Data (`conteudos/manual-news.json`)**: Contains 6 articles without `"url"` fields.

### Layout Integration
* **PublisherAgent**:
  * Card rendering template (lines 272-286):
    ```python
    @staticmethod
    def _render_article(article):
        esc = {key: html.escape(value, quote=True) for key, value in article.items()}
        link = ALLOWED_LINKS[article["category"]]
        category_pt, category_en = CATEGORY_LABELS[article["category"]]
        return f'''<div class="card">
      <div>
        <p class="card-cat"><span lang="pt">{category_pt}</span><span lang="en">{category_en}</span></p>
        <h2 class="card-title"><span lang="pt">{esc["title_pt"]}</span><span lang="en">{esc["title_en"]}</span></h2>
        <p class="card-desc"><span lang="pt">{esc["summary_pt"]}</span><span lang="en">{esc["summary_en"]}</span></p>
      </div>
      <div class="card-meta">
        <span><span lang="pt">HOJE</span><span lang="en">TODAY</span></span>
        <span><a href="{link}" style="color: inherit; text-decoration: none;"><span lang="pt">VER ANÁLISE →</span><span lang="en">VIEW ANALYSIS →</span></a></span>
      </div>
    </div>'''
    ```
  * Does not reference or render `article["url"]` or `article["source"]`.

### Verification Tools
* **Unit Tests (`scripts/test_update_news.py`)**:
  * Uses a hardcoded `valid_payload()` mock (lines 11-24) to verify pipeline output. This payload lacks `url` attributes.
* **Translation Audit (`scripts/verify_translations.py`)**:
  * Collects internal relative links (lines 35-39) to assert their existence in the workspace:
    ```python
    if tag == 'a' and 'href' in attrs_dict:
        href = attrs_dict['href']
        # Only track local .html files
        if not href.startswith(('http', '#', 'mailto:')):
            self.links.append((href, self.getpos()))
    ```

---

## 2. Logic Chain

1. **Active RSS Feeds**: Google News RSS search queries are highly reliable because they normalize elements and bypass direct domain scraper protections (e.g. Cloudflare on direct newspaper sites).
   * For **Expresso**, we can use: `https://news.google.com/rss/search?q=when:3d+site:expresso.pt&hl=pt-PT&gl=PT&ceid=PT:pt`
   * For **Diário de Notícias**, we can use: `https://news.google.com/rss/search?q=when:3d+site:dn.pt&hl=pt-PT&gl=PT&ceid=PT:pt`
   * The other requested feeds (Google Wall Street, MarketWatch, Barron's) are already active in the `RSS_FEEDS` list.

2. **Source URL Propagation**:
   * To successfully pass the `url` field from extraction to layout, the pipeline needs to enforce its existence through all agents:
     * **CollectorAgent**: Needs to assign local paths (e.g. `f"conteudos/{path.name}"`) as `url` for manual files to avoid empty string values.
     * **EditorAgent**: Prompt must be updated to require `url` in the returned JSON object: `- Each article must contain: category, source, url, title_pt, title_en, summary_pt, summary_en.` and instruct the model to copy it exactly from the source items.
     * **VerifierAgent**: `REQUIRED` list must be expanded to include `"url"`.
     * **Fallback Data**: `conteudos/manual-news.json` needs to have `"url"` properties appended to all 6 article entries to avoid verifier exceptions during fallback/dry-runs.

3. **Hyperlink Rendering**:
   * The source name should be rendered inside `card-meta` next to the date text (since the date is translated, appending the source link after it aligns correctly). Adding it as an inline-styled `<a>` anchor tag using `target="_blank" rel="noopener noreferrer"` matches design preferences and prevents navigation away from the site.

4. **Verification Alignment**:
   * If `url` is added to `VerifierAgent.REQUIRED`, `test_update_news.py`'s `valid_payload()` will fail the test suite because it lacks the `url` field. Therefore, `valid_payload()` must be updated to include `"url": "https://..."` or similar values.
   * If manual news links like `conteudos/economia.txt` are rendered in `index.html` or `noticias.html`, `verify_translations.py` will identify them as local non-HTML links and raise "Broken link" errors because they are not listed in `all_valid_links` (which only scans for root `.html` files). The parser in `verify_translations.py` must be adjusted to exclude links starting with `conteudos/` (e.g., updating the startswith tuple to `('http', '#', 'mailto:', 'conteudos/')`).

---

## 3. Caveats

* **Network Restrictions**: Since we are in `CODE_ONLY` network mode, external feed downloads cannot be live-tested directly during investigation. However, the exact formats match existing structures.
* **Manual Source Target**: If relative URLs (e.g. `conteudos/economia.txt`) are rendered as `href` values on the frontend, users clicking them will fail to open them unless the server serves the `conteudos/` folder. This is a reasonable compromise for tracking source metadata without hosting external content.

---

## 4. Conclusion

To successfully parse and display the news source URLs:
1. Update `RSS_FEEDS` in `scripts/update_news.py` to add Diário de Notícias and Expresso using Google News RSS search queries.
2. In `CollectorAgent._collect_manual()`, set `url=f"conteudos/{path.name}"` for manual files.
3. In `EditorAgent.edit()`, modify prompt rules to return `url` from source material.
4. In `VerifierAgent`, add `"url"` to `REQUIRED`.
5. Update `conteudos/manual-news.json` to include `"url"` fields for all 6 articles.
6. In `PublisherAgent._render_article()`, update card HTML template to display the source as a hyperlink inside `card-meta`.
7. Update `valid_payload()` in `scripts/test_update_news.py` to include `"url"` fields.
8. Update `scripts/verify_translations.py` line 38 to exclude `'conteudos/'` links from local broken link checking.

---

## 5. Verification Method

To verify these changes after implementation (Milestone 2/3):

1. **Unit Tests**:
   ```bash
   PYTHONPATH=scripts python3 -m unittest scripts/test_update_news.py
   ```
   *Expected result*: All tests run and pass without verification errors.

2. **Translation & Link Verification**:
   ```bash
   python3 scripts/verify_translations.py
   ```
   *Expected result*: Both `index.html` and `noticias.html` report `Perfect` (broken link checking passes).

3. **Dry-Run News Rendering**:
   ```bash
   GEMINI_API_KEY="mock-or-real-key" python3 scripts/update_news.py --dry-run
   ```
   *Expected result*: A temporary `news-preview.html` file is generated, showing correct card structures with source name links.
