import argparse
import html
import json
import os
import re
import tempfile
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

import feedparser
from google import genai


RSS_FEEDS = [
    ("Expresso", "https://news.google.com/rss/search?q=when:7d+site:expresso.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Diário de Notícias", "https://news.google.com/rss/search?q=when:1d+site:dn.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("ECO", "https://news.google.com/rss/search?q=when:1d+site:eco.sapo.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Jornal de Negócios", "https://news.google.com/rss/search?q=when:1d+site:jornaldenegocios.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Público", "https://news.google.com/rss/search?q=when:1d+site:publico.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Correio da Manhã", "https://news.google.com/rss/search?q=when:1d+site:cmjornal.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Visão", "https://news.google.com/rss/search?q=when:7d+site:visao.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Sábado", "https://news.google.com/rss/search?q=when:7d+site:sabado.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("PCGuia", "https://news.google.com/rss/search?q=when:30d+site:pcguia.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("A Bola", "https://news.google.com/rss/search?q=when:1d+site:abola.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Record", "https://news.google.com/rss/search?q=when:1d+site:record.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("InfoMoney", "https://news.google.com/rss/search?q=when:1d+site:infomoney.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
    ("CNBC", "https://news.google.com/rss/search?q=when:1d+source:cnbc&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters", "https://news.google.com/rss/search?q=when:1d+source:reuters&hl=en-US&gl=US&ceid=US:en"),
    ("Google Wall Street", "https://news.google.com/rss/search?q=when:1d+wall+street&hl=en-US&gl=US&ceid=US:en"),
    ("MarketWatch", "https://news.google.com/rss/search?q=when:1d+source:marketwatch&hl=en-US&gl=US&ceid=US:en"),
    ("Barron's", "https://news.google.com/rss/search?q=when:1d+source:barrons&hl=en-US&gl=US&ceid=US:en"),
    ("CBC Canada", "https://news.google.com/rss/search?q=when:1d+site:cbc.ca/news&hl=en-CA&gl=CA&ceid=CA:en"),
    ("RTE Ireland", "https://news.google.com/rss/search?q=when:1d+site:rte.ie/news&hl=en-IE&gl=IE&ceid=IE:en"),
    ("Swissinfo", "https://news.google.com/rss/search?q=when:1d+site:swissinfo.ch&hl=en-CH&gl=CH&ceid=CH:en"),
    ("Kitco Gold", "https://news.google.com/rss/search?q=when:1d+gold+price+OR+precious+metals&hl=en-US&gl=US&ceid=US:en"),
    ("CoinDesk", "https://news.google.com/rss/search?q=when:1d+site:coindesk.com+OR+site:cointelegraph.com&hl=en-US&gl=US&ceid=US:en"),
]

START_MARKER = "<!-- AI_NEWS_START -->"
END_MARKER = "<!-- AI_NEWS_END -->"
ALLOWED_LINKS = {
    "economy": "economia.html",
    "markets": "mercados.html",
    "gold": "ouro.html",
    "crypto": "ouro.html#bitcoin",
    "sports": "desporto.html",
    "tech": "tech.html",
    "geopolitics": "geopolitica.html",
    "countries": "paises.html",
    "general": "index.html",
}
CATEGORY_LABELS = {
    "economy": ("ECONOMIA", "ECONOMY"),
    "markets": ("MERCADOS", "MARKETS"),
    "gold": ("OURO", "GOLD"),
    "crypto": ("CRIPTO", "CRYPTO"),
    "tech": ("TECNOLOGIA", "TECH"),
    "geopolitics": ("GEOPOLITICA", "GEOPOLITICS"),
    "countries": ("PAÍSES", "COUNTRIES"),
    "sports": ("DESPORTO", "SPORTS"),
}


@dataclass(frozen=True)
class NewsItem:
    source: str
    title: str
    summary: str
    url: str = ""
    published: str = ""


def clean_placeholders(text):
    placeholders = (
        "insere um titulo",
        "insert a manual",
        "insere uma noticia",
        "insere o corpo",
        "insert the body",
    )
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        normalized_line = normalize(line)
        if any(ph in normalized_line for ph in placeholders):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def split_into_blocks(text):
    # Split on card headers only if they are on a line by themselves, or on title headers
    blocks = re.split(r'(?im)(?:^\s*card\s*\d+\s*$|===\s*\S+\s*===)', text)
    valid_blocks = []
    for b in blocks:
        b_clean = b.strip()
        if len(b_clean) > 50:
            valid_blocks.append(b_clean)
    if not valid_blocks and len(text.strip()) > 50:
        return [text.strip()]
    return valid_blocks


class CollectorAgent:
    """Collects manual material and falls back/merges with RSS."""

    def __init__(self, content_dir="conteudos"):
        self.content_dir = Path(content_dir)

    def collect(self):
        manual, images = self._collect_manual()
        rss = self._collect_rss()
        items = manual + rss
        print(f"Collector: {len(manual)} manual sources, {len(images)} images, and {len(rss)} RSS items.")
        return items, images

    def _collect_manual(self):
        items = []
        images = []
        if not self.content_dir.exists():
            return items, images

        for path in sorted(self.content_dir.iterdir()):
            if path.name in {"sobre.txt", "disclaimer.txt", "index.txt", "paises.txt", "manual-news.json", "news-archive.json"}:
                continue
            suffix = path.suffix.lower()
            if suffix == ".pdf":
                text = self._extract_pdf(path)
                if text:
                    cleaned = clean_placeholders(text)
                    blocks = split_into_blocks(cleaned)
                    for i, block in enumerate(blocks):
                        items.append(NewsItem(f"{path.name} (Part {i+1})", path.name, block[:12000], url=f"conteudos/{path.name}"))
            elif suffix == ".txt":
                text = path.read_text(encoding="utf-8")
                cleaned = clean_placeholders(text)
                blocks = split_into_blocks(cleaned)
                for i, block in enumerate(blocks):
                    items.append(NewsItem(f"{path.name} (Part {i+1})", path.name, block[:12000], url=f"conteudos/{path.name}"))
            elif suffix in {".png", ".jpg", ".jpeg"}:
                image = self._load_image(path)
                if image is not None:
                    images.append(image)
                    items.append(
                        NewsItem(path.name, path.name, "Attached screenshot for visual extraction", url=f"conteudos/{path.name}")
                    )

        return items, images

    @staticmethod
    def _extract_pdf(path, max_pages=5):
        try:
            import pypdf

            reader = pypdf.PdfReader(path)
            pages = []
            for page in reader.pages[:max_pages]:
                if page_text := page.extract_text():
                    pages.append(page_text)
            return "\n".join(pages)
        except Exception as exc:
            print(f"Collector: could not read {path}: {exc}")
            return ""

    @staticmethod
    def _load_image(path):
        try:
            from google.genai import types

            mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
            return types.Part.from_bytes(data=path.read_bytes(), mime_type=mime)
        except Exception as exc:
            print(f"Collector: could not read image {path}: {exc}")
            return None

    @staticmethod
    def _collect_rss():
        items = []
        for source, feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    title = clean_text(entry.get("title", ""))
                    if not title:
                        continue
                    items.append(
                        NewsItem(
                            source=source,
                            title=title,
                            summary=clean_text(entry.get("summary", "")),
                            url=entry.get("link", ""),
                            published=entry.get("published", ""),
                        )
                    )
            except Exception as exc:
                print(f"Collector: error reading feed {source}: {exc}")
        return items


class SelectorAgent:
    """Removes duplicates before sending material to the model."""

    def select(self, items, limit=20):
        selected = []
        seen = set()
        for item in items:
            key = normalize(re.sub(r"\s+-\s+[^-]+$", "", item.title))
            if not key or key in seen:
                continue
            seen.add(key)
            selected.append(item)
            if len(selected) >= limit:
                break
        print(f"Selector: {len(selected)} unique sources selected.")
        return selected


class EditorAgent:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)

    def edit(self, items, images):
        source_json = json.dumps([asdict(item) for item in items], ensure_ascii=False)
        prompt = f"""
You are the bilingual editor of Tech & Ouro. Select 10 factual, important
stories for investors and technology readers from the supplied material.

Rules:
- Prioritize manual source files (like those ending in .txt or .pdf, or image contents) over RSS feeds (like WSJ, Bloomberg, Reuters, etc.) if they are present in the source material.
- Generate highly engaging, catchy, tabloid-style headlines (title_pt and title_en) designed to grab attention and drive clicks. The titles MUST be magnetic and irresistible, just like a British tabloid.
- However, the body of the article (body_pt and body_en) MUST remain a serious, factual, deep, and professional analysis of at least 220 to 300 words. We attract them with the tabloid title, but we retain them with high-quality, deep financial and technological information. Never invent facts.
- For the summary (summary_pt and summary_en), write a punchy, 2-sentence hook that bridges the shocking title with the serious facts.
- IMPORTANT ROUTING RULES: American news, especially from Wall Street sources, normally goes to the 'countries' category. American football news goes to the 'sports' category. The most bombastic and explosive news stories must be prioritized.
- Never invent facts, dates, sources, quotes, prices, or events.
- Every story must have complete Portuguese and English text.
- category must be exactly one of: {', '.join(CATEGORY_LABELS)}.
- source must name one supplied source.
- Return JSON only, with an object containing an `articles` array.
- Each article must contain: category, source, url, title_pt, title_en,
  summary_pt, summary_en, body_pt, body_en.
- You must return the exact `url` of the selected article from the source material. Do not invent or modify the URL.

Source material:
{source_json}
"""
        contents = [prompt, *images]
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config={"response_mime_type": "application/json"},
        )
        return json.loads(response.text)


class VerifierAgent:
    REQUIRED = ("category", "source", "url", "title_pt", "title_en", "summary_pt", "summary_en", "body_pt", "body_en")

    def verify(self, payload, known_sources):
        articles = payload.get("articles") if isinstance(payload, dict) else None
        if not isinstance(articles, list) or len(articles) == 0:
            raise ValueError("Verifier: expected at least 1 article")

        verified = []
        titles = set()
        normalized_sources = set()
        for s in known_sources:
            normalized_sources.add(normalize(s))
            base = re.sub(r"\s+\(part\s+\d+\)", "", s, flags=re.IGNORECASE)
            normalized_sources.add(normalize(base))

        for name, _ in RSS_FEEDS:
            normalized_sources.add(normalize(name))

        content_dir = Path("conteudos")
        if content_dir.exists():
            for path in content_dir.iterdir():
                if path.is_file():
                    normalized_sources.add(normalize(path.name))
                    normalized_sources.add(normalize(path.stem))

        for position, article in enumerate(articles, 1):
            if not isinstance(article, dict):
                raise ValueError(f"Verifier: article {position} is not an object")
            missing = [field for field in self.REQUIRED if not clean_text(article.get(field, ""))]
            if missing:
                raise ValueError(f"Verifier: article {position} missing {', '.join(missing)}")
            if article["category"] not in CATEGORY_LABELS:
                raise ValueError(f"Verifier: invalid category in article {position}")
            if normalize(article["source"]) not in normalized_sources:
                raise ValueError(f"Verifier: unknown source in article {position}")

            for text_field in ("title_pt", "title_en", "summary_pt", "summary_en"):
                val = article[text_field]
                if not self._has_balanced_brackets(val):
                    raise ValueError(f"Verifier: article {position} has unbalanced parentheses/brackets in '{text_field}'")

            key = normalize(article["title_pt"])
            if key in titles:
                raise ValueError(f"Verifier: duplicate title in article {position}")
            titles.add(key)
            verified.append({field: clean_text(article[field]) for field in self.REQUIRED})

        print(f"Verifier: {len(verified)} articles approved.")
        return verified

    @staticmethod
    def _has_balanced_brackets(text):
        pairs = {')': '(', ']': '[', '}': '{'}
        stack = []
        for char in text:
            if char in pairs.values():
                stack.append(char)
            elif char in pairs.keys():
                if not stack or stack[-1] != pairs[char]:
                    return False
                stack.pop()
        return len(stack) == 0


class PublisherAgent:
    def render(self, articles):
        rendered = []
        for i, article in enumerate(articles):
            rendered.append(self._render_article(article))
            if (i + 1) % 3 == 0 and (i + 1) != len(articles):
                rendered.append(self._render_adsense_infeed())
        return "\n".join(rendered)

    @staticmethod
    def _render_adsense_infeed():
        return '''<div class="card in-feed-ad" style="background: transparent; box-shadow: none; padding: 0; border: none;">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2757348402596933" crossorigin="anonymous"></script>
<ins class="adsbygoogle"
     style="display:block"
     data-ad-format="fluid"
     data-ad-layout-key="-ec+6l-2v-aq+u1"
     data-ad-client="ca-pub-2757348402596933"
     data-ad-slot="8218810488"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
</div>'''

    def publish(self, archive_articles, dry_run=False):
        sorted_articles = sorted(archive_articles, key=lambda x: x.get("date", ""), reverse=True)

        pages_categories = {
            Path("index.html"): None,  # limit to 10
            Path("noticias.html"): None,  # all active
            Path("economia.html"): ["economy"],
            Path("desporto.html"): ["sports"],
            Path("tech.html"): ["tech"],
            Path("geopolitica.html"): ["geopolitics"],
            Path("mercados.html"): ["markets"],
            Path("ouro.html"): ["gold", "crypto"],
            Path("paises.html"): ["countries"],
        }

        updates = {}
        for path, categories in pages_categories.items():
            if not path.exists():
                print(f"Publisher: warning, {path} does not exist. Skipping.")
                continue

            if categories is None:
                filtered = sorted_articles
                if path.name == "index.html":
                    filtered = sorted_articles[:10]
            else:
                filtered = [a for a in sorted_articles if a.get("category") in categories]

            rendered_html = self.render(filtered)
            content = path.read_text(encoding="utf-8")
            try:
                updates[path] = replace_news_block(content, rendered_html)
            except ValueError as e:
                print(f"Publisher: skipping {path} due to error: {e}")

        if dry_run:
            index_filtered = sorted_articles[:10]
            rendered_html = self.render(index_filtered)
            Path("news-preview.html").write_text(rendered_html, encoding="utf-8")
            print("Publisher: dry run written to news-preview.html; site HTML untouched.")
            return

        for path, content in updates.items():
            atomic_write(path, content)
            print(f"Publisher: updated {path}.")

    @staticmethod
    def _render_article(article):
        esc = {key: html.escape(value, quote=True) for key, value in article.items()}
        link = ALLOWED_LINKS[article["category"]]
        category_pt, category_en = CATEGORY_LABELS[article["category"]]
        
        art_date = article.get("date", "HOJE")
        today_str = datetime.now().strftime("%Y-%m-%d")
        if art_date == today_str:
            date_html = '<span lang="pt">HOJE</span><span lang="en">TODAY</span>'
        else:
            date_html = f'<span lang="pt">{art_date}</span><span lang="en">{art_date}</span>'
        
        body_pt = article.get("body_pt", "")
        body_en = article.get("body_en", "")
        
        esc_body_pt = html.escape(body_pt, quote=True)
        esc_body_en = html.escape(body_en, quote=True)
        
        return f'''<div class="card card-natgeo" onclick="openArticle(this)" data-body-pt="{esc_body_pt}" data-body-en="{esc_body_en}">
  <div class="card-header-placeholder">
    <span class="cat-icon" lang="pt">{category_pt}</span>
    <span class="cat-icon" lang="en">{category_en}</span>
  </div>
  <div>
    <p class="card-cat"><span lang="pt">{category_pt}</span><span lang="en">{category_en}</span></p>
    <h2 class="card-title"><span lang="pt">{esc["title_pt"]}</span><span lang="en">{esc["title_en"]}</span></h2>
    <p class="card-desc"><span lang="pt">{esc["summary_pt"]}</span><span lang="en">{esc["summary_en"]}</span></p>
  </div>
  <div class="card-meta" onclick="event.stopPropagation();">
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
  </div>
</div>'''


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize(value):
    value = unicodedata.normalize("NFKD", clean_text(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def replace_news_block(content, rendered_html):
    pattern = re.compile(
        f"({re.escape(START_MARKER)})(.*?)({re.escape(END_MARKER)})", re.DOTALL
    )
    if len(pattern.findall(content)) != 1:
        raise ValueError("Publisher: expected exactly one AI news marker block")
    return pattern.sub(lambda match: f"{match.group(1)}\n{rendered_html}\n{match.group(3)}", content)


def atomic_write(path, content):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def run(action="generate", dry_run=False):
    draft_path = Path("conteudos/news-draft.json")
    archive_path = Path("conteudos/news-archive.json")

    if action == "publish":
        if not draft_path.exists():
            print("Publisher: No news-draft.json found. Run generation first.")
            return

        try:
            new_articles = json.loads(draft_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Publisher: Failed to read draft: {e}")
            return
            
        print(f"Publisher: Loaded {len(new_articles)} articles from draft.")

        # Archive management
        if archive_path.exists():
            try:
                archive = json.loads(archive_path.read_text(encoding="utf-8"))
            except Exception:
                archive = []
        else:
            archive = []

        # Filter older than 20 days
        today = datetime.now()
        twenty_days_ago = today - timedelta(days=20)
        filtered_archive = []
        for art in archive:
            art_date_str = art.get("date")
            if not art_date_str:
                continue
            try:
                art_date = datetime.strptime(art_date_str, "%Y-%m-%d")
                if art_date >= twenty_days_ago:
                    filtered_archive.append(art)
            except Exception:
                pass

        # Merge new articles
        today_str = today.strftime("%Y-%m-%d")
        for art in new_articles:
            art["date"] = today_str
            filtered_archive = [x for x in filtered_archive if normalize(x.get("title_pt", "")) != normalize(art.get("title_pt", "")) and x.get("url") != art.get("url")]
            filtered_archive.append(art)

        # Save archive
        if not dry_run:
            archive_path.write_text(json.dumps(filtered_archive, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Archive: updated and saved {len(filtered_archive)} active articles.")

        publisher = PublisherAgent()
        publisher.publish(filtered_archive, dry_run=dry_run)
        
        if not dry_run:
            # Delete draft after successful publish
            draft_path.unlink(missing_ok=True)
            print("Publisher: Draft published and removed.")
        return

    # Generation action
    print("Generator: Starting news collection...")
    items, images = CollectorAgent().collect()
    if not items and not images:
        raise ValueError("Collector: no source material found")

    selected = SelectorAgent().select(items)
    
    is_fallback = False
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable not set. Falling back to conteudos/manual-news.json")
        manual_path = Path("conteudos/manual-news.json")
        if manual_path.exists():
            payload = json.loads(manual_path.read_text(encoding="utf-8"))
            is_fallback = True
        else:
            raise ValueError("GEMINI_API_KEY environment variable not set and conteudos/manual-news.json not found")
    else:
        try:
            payload = EditorAgent(api_key).edit(selected, images)
        except Exception as e:
            print(f"Gemini API call failed: {e}. Falling back to conteudos/manual-news.json")
            manual_path = Path("conteudos/manual-news.json")
            if manual_path.exists():
                payload = json.loads(manual_path.read_text(encoding="utf-8"))
                is_fallback = True
            else:
                raise e

    known_sources = {item.source for item in selected}
    if is_fallback and isinstance(payload, dict) and isinstance(payload.get("articles"), list):
        for art in payload["articles"]:
            if "source" in art:
                known_sources.add(art["source"])

    new_articles = VerifierAgent().verify(payload, known_sources)
    
    # Save to draft
    draft_path.write_text(json.dumps(new_articles, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generator: Saved {len(new_articles)} articles to {draft_path} for review.")
    print("Run with '--publish' to apply the draft to the site.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safe multi-agent news pipeline")
    parser.add_argument("--dry-run", action="store_true", help="do not modify site HTML")
    parser.add_argument("--publish", action="store_true", help="Publish the reviewed draft")
    args = parser.parse_args()
    action = "publish" if args.publish else "generate"
    run(action=action, dry_run=args.dry_run)
