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
    ("Expresso", "https://news.google.com/rss/search?q=when:3d+site:expresso.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Diário de Notícias", "https://news.google.com/rss/search?q=when:3d+site:dn.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("ECO", "https://news.google.com/rss/search?q=when:3d+site:eco.sapo.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Jornal de Negócios", "https://news.google.com/rss/search?q=when:3d+site:jornaldenegocios.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Público", "https://news.google.com/rss/search?q=when:3d+site:publico.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Correio da Manhã", "https://news.google.com/rss/search?q=when:3d+site:cmjornal.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Visão", "https://news.google.com/rss/search?q=when:3d+site:visao.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Sábado", "https://news.google.com/rss/search?q=when:3d+site:sabado.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("A Bola", "https://news.google.com/rss/search?q=when:3d+site:abola.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("Record", "https://news.google.com/rss/search?q=when:3d+site:record.pt&hl=pt-PT&gl=PT&ceid=PT:pt"),
    ("InfoMoney", "https://news.google.com/rss/search?q=when:3d+site:infomoney.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
    ("CNBC", "https://news.google.com/rss/search?q=when:3d+source:cnbc&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters", "https://news.google.com/rss/search?q=when:3d+source:reuters&hl=en-US&gl=US&ceid=US:en"),
    ("Google Wall Street", "https://news.google.com/rss/search?q=when:3d+wall+street&hl=en-US&gl=US&ceid=US:en"),
    ("MarketWatch", "https://news.google.com/rss/search?q=when:3d+source:marketwatch&hl=en-US&gl=US&ceid=US:en"),
    ("Barron's", "https://news.google.com/rss/search?q=when:3d+source:barrons&hl=en-US&gl=US&ceid=US:en"),
    ("CBC Canada", "https://news.google.com/rss/search?q=when:3d+site:cbc.ca/news&hl=en-CA&gl=CA&ceid=CA:en"),
    ("RTE Ireland", "https://news.google.com/rss/search?q=when:3d+site:rte.ie/news&hl=en-IE&gl=IE&ceid=IE:en"),
    ("Swissinfo", "https://news.google.com/rss/search?q=when:3d+site:swissinfo.ch&hl=en-CH&gl=CH&ceid=CH:en"),
    ("Kitco Gold", "https://news.google.com/rss/search?q=when:3d+gold+price+OR+precious+metals&hl=en-US&gl=US&ceid=US:en"),
    ("CoinDesk", "https://news.google.com/rss/search?q=when:3d+site:coindesk.com+OR+site:cointelegraph.com&hl=en-US&gl=US&ceid=US:en"),
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
    blocks = re.split(r'(?i)(?:card\s*\d+|===\s*\S+\s*===)', text)
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
- Do NOT rewrite, dramatize, or summarize the stories in a sensationalist, tabloid, or clickbait style. Our clients are sophisticated investors and technology professionals who value serious, dry, factual information.
- For manual source files, copy the original Portuguese and English text exactly as written for the summary and the body. Do not alter, shorten, or paraphrase manual source content.
- For RSS feed stories, the generated article body (body_pt and body_en) MUST be a detailed, professional, and dry analysis of at least 220 to 300 words (minimum 220 words). It should expand on the facts in the feed to explain the broader context, economic or technological implications, and background details in a serious, high-quality tone, without introducing any sensationalism or tabloid fluff.
- For RSS feed stories, the summary (summary_pt and summary_en) should be a concise 2-sentence summary.
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
        if not isinstance(articles, list) or len(articles) != 10:
            raise ValueError("Verifier: expected 10 articles")

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
        return "\n".join(self._render_article(article) for article in articles)

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
        
        body_pt = article.get("body_pt", "")
        body_en = article.get("body_en", "")
        
        esc_body_pt = html.escape(body_pt, quote=True)
        esc_body_en = html.escape(body_en, quote=True)
        
        return f'''<div class="card" onclick="openArticle(this)" data-body-pt="{esc_body_pt}" data-body-en="{esc_body_en}">
  <div>
    <p class="card-cat"><span lang="pt">{category_pt}</span><span lang="en">{category_en}</span></p>
    <h2 class="card-title"><span lang="pt">{esc["title_pt"]}</span><span lang="en">{esc["title_en"]}</span></h2>
    <p class="card-desc"><span lang="pt">{esc["summary_pt"]}</span><span lang="en">{esc["summary_en"]}</span></p>
  </div>
  <div class="card-meta" onclick="event.stopPropagation();">
    <span><span lang="pt">{art_date}</span><span lang="en">{art_date}</span></span>
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
    new_articles = VerifierAgent().verify(payload, known_sources)
    
    # Archive management
    archive_path = Path("conteudos/news-archive.json")
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
        # Remove any existing article with duplicate title or URL from archive
        filtered_archive = [x for x in filtered_archive if normalize(x["title_pt"]) != normalize(art["title_pt"]) and x["url"] != art["url"]]
        filtered_archive.append(art)

    # Save archive
    if not dry_run:
        archive_path.write_text(json.dumps(filtered_archive, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Archive: updated and saved {len(filtered_archive)} active articles.")

    publisher = PublisherAgent()
    publisher.publish(filtered_archive, dry_run=dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safe multi-agent news pipeline")
    parser.add_argument("--dry-run", action="store_true", help="do not modify site HTML")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
