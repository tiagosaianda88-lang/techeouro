import argparse
import html
import json
import os
import re
import tempfile
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

import feedparser
from google import genai


RSS_FEEDS = [
    ("Expresso", "https://news.google.com/rss/search?q=when:3d+site:expresso.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Diário de Notícias", "https://news.google.com/rss/search?q=when:3d+site:dn.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Google Wall Street", "https://news.google.com/rss/search?q=when:3d+wall+street&hl=en-US&gl=US&ceid=US:en"),
    ("MarketWatch", "https://news.google.com/rss/search?q=when:3d+source:marketwatch&hl=en-US&gl=US&ceid=US:en"),
    ("Barron's", "https://news.google.com/rss/search?q=when:3d+source:barrons&hl=en-US&gl=US&ceid=US:en"),
]

HTML_FILES = (Path("noticias.html"), Path("index.html"))
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
    "general": "index.html",
}
CATEGORY_LABELS = {
    "economy": ("ECONOMIA", "ECONOMY"),
    "markets": ("MERCADOS", "MARKETS"),
    "gold": ("OURO", "GOLD"),
    "crypto": ("CRIPTO", "CRYPTO"),
    "tech": ("TECNOLOGIA", "TECH"),
    "geopolitics": ("GEOPOLITICA", "GEOPOLITICS"),
    "sports": ("DESPORTO", "SPORTS"),
}


@dataclass(frozen=True)
class NewsItem:
    source: str
    title: str
    summary: str
    url: str = ""
    published: str = ""


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
            if path.name in {"sobre.txt", "disclaimer.txt", "index.txt", "paises.txt"}:
                continue
            suffix = path.suffix.lower()
            if suffix == ".pdf":
                text = self._extract_pdf(path)
                if text:
                    items.append(NewsItem(path.name, path.name, text[:12000], url=f"conteudos/{path.name}"))
            elif suffix == ".txt":
                text = path.read_text(encoding="utf-8").strip()
                if self._use_manual_text(text):
                    items.append(NewsItem(path.name, path.name, text[:12000], url=f"conteudos/{path.name}"))
            elif suffix in {".png", ".jpg", ".jpeg"}:
                image = self._load_image(path)
                if image is not None:
                    images.append(image)
                    items.append(
                        NewsItem(path.name, path.name, "Attached screenshot for visual extraction", url=f"conteudos/{path.name}")
                    )

        return items, images

    @staticmethod
    def _use_manual_text(text):
        if len(text) <= 50:
            return False
        placeholders = (
            "insere um titulo",
            "insert a manual",
            "insere uma noticia",
            "insere o corpo",
            "insert the body",
        )
        normalized = normalize(text)
        return not any(placeholder in normalized for placeholder in placeholders)

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
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:8]:
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
        return items


class SelectorAgent:
    """Removes duplicates before sending material to the model."""

    def select(self, items, limit=40):
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
You are the bilingual editor of Tech & Ouro. Select 6 factual, important
stories for investors and technology readers from the supplied material.

Rules:
- Prioritize manual source files (like those ending in .txt or .pdf, or image contents) over RSS feeds (like WSJ, Bloomberg, Reuters, etc.) if they are present in the source material.
- Never invent facts, dates, sources, quotes, prices, or events.
- Keep the source meaning. Write concise summaries of at most 2 sentences.
- Every story must have complete Portuguese and English text.
- category must be exactly one of: {', '.join(CATEGORY_LABELS)}.
- source must name one supplied source.
- Return JSON only, with an object containing an `articles` array.
- Each article must contain: category, source, url, title_pt, title_en,
  summary_pt, summary_en.
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
    REQUIRED = ("category", "source", "url", "title_pt", "title_en", "summary_pt", "summary_en")

    def verify(self, payload, known_sources):
        articles = payload.get("articles") if isinstance(payload, dict) else None
        if not isinstance(articles, list) or len(articles) != 6:
            raise ValueError("Verifier: expected 6 articles")

        verified = []
        titles = set()
        normalized_sources = {normalize(source) for source in known_sources}
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

            key = normalize(article["title_pt"])
            if key in titles:
                raise ValueError(f"Verifier: duplicate title in article {position}")
            titles.add(key)
            verified.append({field: clean_text(article[field]) for field in self.REQUIRED})

        print(f"Verifier: {len(verified)} articles approved.")
        return verified


class PublisherAgent:
    def render(self, articles):
        return "\n".join(self._render_article(article) for article in articles)

    def publish(self, rendered_html, dry_run=False):
        updates = {}
        for path in HTML_FILES:
            content = path.read_text(encoding="utf-8")
            updates[path] = replace_news_block(content, rendered_html)

        if dry_run:
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
        return f'''<div class="card">
  <div>
    <p class="card-cat"><span lang="pt">{category_pt}</span><span lang="en">{category_en}</span></p>
    <h2 class="card-title"><span lang="pt">{esc["title_pt"]}</span><span lang="en">{esc["title_en"]}</span></h2>
    <p class="card-desc"><span lang="pt">{esc["summary_pt"]}</span><span lang="en">{esc["summary_en"]}</span></p>
  </div>
  <div class="card-meta">
    <span><span lang="pt">HOJE</span><span lang="en">TODAY</span></span>
    <span><span lang="pt">Fonte: </span><span lang="en">Source: </span><a href="{esc["url"]}" target="_blank" rel="noopener noreferrer" style="color: #d4af37; text-decoration: underline;">{esc["source"]}</a></span>
    <span><a href="{link}" style="color: inherit; text-decoration: none;"><span lang="pt">VER ANÁLISE →</span><span lang="en">VIEW ANALYSIS →</span></a></span>
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


def run(dry_run=False):
    items, images = CollectorAgent().collect()
    if not items and not images:
        raise ValueError("Collector: no source material found")

    selected = SelectorAgent().select(items)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable not set. Falling back to conteudos/manual-news.json")
        manual_path = Path("conteudos/manual-news.json")
        if manual_path.exists():
            payload = json.loads(manual_path.read_text(encoding="utf-8"))
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
            else:
                raise e

    known_sources = {item.source for item in selected}
    articles = VerifierAgent().verify(payload, known_sources)
    publisher = PublisherAgent()
    publisher.publish(publisher.render(articles), dry_run=dry_run)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safe multi-agent news pipeline")
    parser.add_argument("--dry-run", action="store_true", help="do not modify site HTML")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
