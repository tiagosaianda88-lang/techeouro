import argparse
import html
import ipaddress
import json
import os
import re
import tempfile
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit

import feedparser


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
    ("BBC UK Countries", "https://news.google.com/rss/search?q=when:1d+site:bbc.com/news+OR+site:bbc.co.uk/news+UK+OR+Britain+OR+London&hl=en-GB&gl=GB&ceid=GB:en"),
    ("CNBC", "https://news.google.com/rss/search?q=when:1d+source:cnbc&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters", "https://news.google.com/rss/search?q=when:1d+source:reuters&hl=en-US&gl=US&ceid=US:en"),
    ("Google Wall Street", "https://news.google.com/rss/search?q=when:1d+wall+street&hl=en-US&gl=US&ceid=US:en"),
    ("MarketWatch", "https://news.google.com/rss/search?q=when:1d+source:marketwatch&hl=en-US&gl=US&ceid=US:en"),
    ("Barron's", "https://news.google.com/rss/search?q=when:1d+source:barrons&hl=en-US&gl=US&ceid=US:en"),
    ("CBC Canada", "https://news.google.com/rss/search?q=when:1d+site:cbc.ca/news&hl=en-CA&gl=CA&ceid=CA:en"),
    ("RTE Ireland", "https://news.google.com/rss/search?q=when:1d+site:rte.ie/news&hl=en-IE&gl=IE&ceid=IE:en"),
    ("Swissinfo", "https://news.google.com/rss/search?q=when:1d+site:swissinfo.ch&hl=en-CH&gl=CH&ceid=CH:en"),
    ("Kitco & GoldSeek", "https://news.google.com/rss/search?q=when:1d+site:kitco.com+OR+site:goldseek.com&hl=en-US&gl=US&ceid=US:en"),
    ("Gold Prices", "https://news.google.com/rss/search?q=when:1d+gold+price+OR+precious+metals+OR+gold+market&hl=en-US&gl=US&ceid=US:en"),
    ("CoinDesk", "https://news.google.com/rss/search?q=when:1d+site:coindesk.com+OR+site:cointelegraph.com&hl=en-US&gl=US&ceid=US:en"),
]

START_MARKER = "<!-- AI_NEWS_START -->"
END_MARKER = "<!-- AI_NEWS_END -->"
INDEX_NEWS_LIMIT = 10
INDEX_NEW_ARTICLES_LIMIT = 6
SUMMARY_MIN_CHARS = 220
SUMMARY_MAX_CHARS = 300
TITLE_MAX_CHARS = 180
BODY_MAX_CHARS = 5000
URL_MAX_CHARS = 2048
INDEX_MARKET_FOCUS_SOURCES = ("infomoney", "bbc uk countries")
INDEX_MARKET_FOCUS_KEYWORDS = (
    "brasil",
    "brazil",
    "united kingdom",
    "britain",
    "great britain",
    "british",
    "london",
    "reino unido",
    "wimbledon",
    "silverstone",
    "ftse",
    "bank of england",
)
INDEX_MARKET_FOCUS_CATEGORIES = {"countries", "markets", "economy", "geopolitics", "sports"}
QUEUE_MANIFEST_PATH = Path("conteudos/news-queue-manifest.json")
QUEUE_DRAFT_SOURCES_PATH = Path("conteudos/news-draft-sources.json")
QUEUE_SOURCE_URLS = {
    "a bola": "https://www.abola.pt/",
    "bbc uk countries": "https://www.bbc.co.uk/news",
    "barrons": "https://www.barrons.com/",
    "cbc news canada": "https://www.cbc.ca/news",
    "diario de noticias": "https://www.dn.pt/",
    "jornal de negocios": "https://www.jornaldenegocios.pt/",
    "jornal de noticias": "https://www.jn.pt/",
    "kictonews golg crypto": "https://www.kitco.com/",
    "o benfica": "https://www.slbenfica.pt/",
    "o jogo": "https://www.ojogo.pt/",
    "record": "https://www.record.pt/",
    "reuters": "https://www.reuters.com/",
    "the wall strett journal": "https://www.wsj.com/",
}
SOURCE_ALIASES = {
    "wall street journal": "the wall strett journal",
    "the wall street journal": "the wall strett journal",
    "wsj": "the wall strett journal",
    "jornal noticias": "jornal de noticias",
    "jn": "jornal de noticias",
    "jornal negocios": "jornal de negocios",
    "ojogo": "o jogo",
}
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
        queue_metadata = self._load_queue_metadata()

        for path in sorted(self.content_dir.iterdir()):
            if path.name in {"sobre.txt", "disclaimer.txt", "index.txt", "paises.txt", "manual-news.json", "news-archive.json"}:
                continue
            suffix = path.suffix.lower()
            source_name, source_url = self._source_for_path(path, queue_metadata)
            if suffix == ".pdf":
                text = self._extract_pdf(path)
                if text:
                    cleaned = clean_placeholders(text)
                    blocks = split_into_blocks(cleaned)
                    for i, block in enumerate(blocks):
                        items.append(NewsItem(f"{source_name} (Part {i+1})", path.name, block[:12000], url=source_url))
            elif suffix == ".txt":
                text = path.read_text(encoding="utf-8")
                cleaned = clean_placeholders(text)
                blocks = split_into_blocks(cleaned)
                for i, block in enumerate(blocks):
                    items.append(NewsItem(f"{source_name} (Part {i+1})", path.name, block[:12000], url=source_url))
            elif suffix in {".png", ".jpg", ".jpeg"}:
                image = self._load_image(path)
                if image is not None:
                    images.append(image)
                    items.append(
                        NewsItem(source_name, path.name, "Attached screenshot for visual extraction", url=source_url)
                    )

        return items, images

    def _load_queue_metadata(self):
        if not QUEUE_MANIFEST_PATH.exists():
            return {}
        try:
            manifest = json.loads(QUEUE_MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
        metadata = {}
        for entry in manifest if isinstance(manifest, list) else []:
            if not isinstance(entry, dict):
                continue
            staged_name = entry.get("staged_name") or Path(entry.get("staged_path", "")).name
            source_label = clean_text(entry.get("source_label", ""))
            if staged_name and source_label:
                metadata[staged_name] = source_label
        return metadata

    @staticmethod
    def _source_for_path(path, queue_metadata):
        source_name = queue_metadata.get(path.name, path.name)
        source_key = normalize(source_name)
        source_url = QUEUE_SOURCE_URLS.get(source_key, f"conteudos/{path.name}")
        return source_name, source_url

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
        print(f"Collector: image extraction is skipped for {path}; no external image AI is configured.")
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
        items = sorted(
            items,
            key=lambda item: (-index_market_focus_score(asdict(item)), normalize(item.title)),
        )
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


class VerifierAgent:
    REQUIRED = ("category", "source", "url", "title_pt", "title_en", "summary_pt", "summary_en", "body_pt", "body_en")

    def verify(self, payload, known_sources):
        articles = payload.get("articles") if isinstance(payload, dict) else None
        if not isinstance(articles, list):
            raise ValueError("Verifier: expected a list of articles")
        articles = articles[:10]

        verified = []
        titles = set()
        normalized_sources = set()
        source_by_normalized = {}
        for s in known_sources:
            normalized = normalize(s)
            normalized_sources.add(normalized)
            source_by_normalized[normalized] = s
            base = re.sub(r"\s+\(part\s+\d+\)", "", s, flags=re.IGNORECASE)
            normalized_base = normalize(base)
            normalized_sources.add(normalized_base)
            source_by_normalized[normalized_base] = base

        for name, _ in RSS_FEEDS:
            normalized = normalize(name)
            normalized_sources.add(normalized)
            source_by_normalized[normalized] = name

        for position, article in enumerate(articles, 1):
            if not isinstance(article, dict):
                raise ValueError(f"Verifier: article {position} is not an object")
            missing = [field for field in self.REQUIRED if not clean_text(article.get(field, ""))]
            if missing:
                raise ValueError(f"Verifier: article {position} missing {', '.join(missing)}")
            article = {field: clean_text(article[field]) for field in self.REQUIRED}
            if article["category"] not in CATEGORY_LABELS:
                raise ValueError(f"Verifier: invalid category in article {position}")
            normalized_source = normalize(article["source"])
            if normalized_source not in normalized_sources:
                alias = SOURCE_ALIASES.get(normalized_source)
                if alias and normalize(alias) in normalized_sources:
                    article["source"] = source_by_normalized[normalize(alias)]
                else:
                    raise ValueError(f"Verifier: unknown source in article {position}")
            else:
                article["source"] = source_by_normalized[normalized_source]
            if not article["source"]:
                raise ValueError(f"Verifier: unknown source in article {position}")

            try:
                article["url"] = validate_article_url(article["url"])
            except ValueError as exc:
                raise ValueError(f"Verifier: article {position} has invalid url: {exc}") from exc

            for text_field in ("title_pt", "title_en", "summary_pt", "summary_en"):
                val = article[text_field]
                if not self._has_balanced_brackets(val):
                    raise ValueError(f"Verifier: article {position} has unbalanced parentheses/brackets in '{text_field}'")
                if text_field.startswith("title") and self._looks_sensationalist(val):
                    raise ValueError(f"Verifier: article {position} has sensationalist title in '{text_field}'")

            for title_field in ("title_pt", "title_en"):
                if len(article[title_field]) > TITLE_MAX_CHARS:
                    raise ValueError(f"Verifier: article {position} has title longer than {TITLE_MAX_CHARS} characters in '{title_field}'")

            for summary_field in ("summary_pt", "summary_en"):
                summary_length = len(article[summary_field])
                if not SUMMARY_MIN_CHARS <= summary_length <= SUMMARY_MAX_CHARS:
                    raise ValueError(
                        f"Verifier: article {position} summary must have {SUMMARY_MIN_CHARS}-{SUMMARY_MAX_CHARS} characters in '{summary_field}'"
                    )

            for body_field in ("body_pt", "body_en"):
                if len(article[body_field]) > BODY_MAX_CHARS:
                    raise ValueError(f"Verifier: article {position} has body longer than {BODY_MAX_CHARS} characters in '{body_field}'")

            key = normalize(article["title_pt"])
            if key in titles:
                raise ValueError(f"Verifier: duplicate title in article {position}")
            titles.add(key)
            verified.append(article)

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

    @staticmethod
    def _looks_sensationalist(text):
        cleaned = clean_text(text)
        letters = [char for char in cleaned if char.isalpha()]
        uppercase_ratio = (
            sum(1 for char in letters if char.isupper()) / len(letters)
            if letters
            else 0
        )
        blocked_terms = {
            "abala",
            "bomba",
            "bombshell",
            "caos",
            "choque",
            "chocante",
            "explosive",
            "panic",
            "panico",
            "pânico",
            "shocker",
        }
        normalized_terms = set(normalize(cleaned).split())
        return (8 <= len(letters) and len(cleaned) <= 240 and uppercase_ratio > 0.55) or bool(blocked_terms & normalized_terms)



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
<ins class="adsbygoogle"
     style="display:block"
     data-ad-format="fluid"
     data-ad-layout-key="-ec+6l-2v-aq+u1"
     data-ad-client="ca-pub-2757348402596933"
     data-ad-slot="8218810488"></ins>
</div>'''

    def publish(self, archive_articles, dry_run=False, extra_updates=None):
        publishable_articles = []
        rejected_articles = []
        for article in archive_articles:
            try:
                validate_article_url(article.get("url", ""))
            except ValueError:
                rejected_articles.append(article)
                continue
            publishable_articles.append(article)

        if rejected_articles:
            print(
                f"Publisher: withheld {len(rejected_articles)} archived articles without a safe, verifiable HTTPS source."
            )

        sorted_articles = [
            article
            for _, article in sorted(
                enumerate(publishable_articles),
                key=lambda indexed: (indexed[1].get("date", ""), indexed[0]),
                reverse=True,
            )
        ]

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
        originals = {}
        for path, categories in pages_categories.items():
            if not path.exists():
                raise FileNotFoundError(f"Publisher: required page {path} does not exist")

            if categories is None:
                filtered = sorted_articles
                if path.name == "index.html":
                    filtered = self._index_rotation(sorted_articles)
            else:
                filtered = [a for a in sorted_articles if a.get("category") in categories]

            rendered_html = self.render(filtered)
            content = path.read_text(encoding="utf-8")
            originals[path] = content
            updates[path] = replace_news_block(content, rendered_html)

        for path, content in (extra_updates or {}).items():
            path = Path(path)
            originals[path] = path.read_text(encoding="utf-8") if path.exists() else None
            updates[path] = content

        if dry_run:
            print(f"Publisher: dry run validated {len(updates)} files; no files written.")
            return updates

        written = []
        try:
            for path, content in updates.items():
                atomic_write(path, content)
                written.append(path)
                print(f"Publisher: updated {path}.")
        except Exception:
            for path in reversed(written):
                previous = originals[path]
                if previous is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, previous)
            raise
        return updates

    @staticmethod
    def _index_rotation(sorted_articles):
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_articles = [a for a in sorted_articles if a.get("date") == today_str]
        older_articles = [a for a in sorted_articles if a.get("date") != today_str]
        selected = today_articles[:INDEX_NEW_ARTICLES_LIMIT]
        selected.extend(older_articles[: INDEX_NEWS_LIMIT - len(selected)])

        if len(selected) < INDEX_NEWS_LIMIT:
            selected_ids = {a.get("url") or normalize(a.get("title_pt", "")) for a in selected}
            for article in sorted_articles:
                article_id = article.get("url") or normalize(article.get("title_pt", ""))
                if article_id in selected_ids:
                    continue
                selected.append(article)
                selected_ids.add(article_id)
                if len(selected) >= INDEX_NEWS_LIMIT:
                    break

        return promote_index_market_focus(selected[:INDEX_NEWS_LIMIT], sorted_articles)

    @staticmethod
    def _render_article(article):
        safe_article = dict(article)
        safe_article["url"] = validate_article_url(article.get("url", ""))
        esc = {key: html.escape(value, quote=True) for key, value in safe_article.items()}
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
  <div>
    <p class="card-cat"><span lang="pt">{category_pt}</span><span lang="en">{category_en}</span></p>
    <h2 class="card-title"><span lang="pt">{esc["title_pt"]}</span><span lang="en">{esc["title_en"]}</span></h2>
    <p class="card-desc"><span lang="pt">{esc["summary_pt"]}</span><span lang="en">{esc["summary_en"]}</span></p>
  </div>
  <div class="card-meta" onclick="event.stopPropagation();">
    <div style="display: flex; gap: 10px; width: 100%; justify-content: space-between; flex-wrap: wrap;">
      <div class="source-stack">
        <span>{date_html}</span>
        <span class="source-attribution"><span lang="pt">Fonte: </span><span lang="en">Source: </span><a href="{esc["url"]}" target="_blank" rel="noopener noreferrer">{esc["source"]}</a></span>
        <span class="editorial-attribution"><span lang="pt">Resumo editorial Tech &amp; Ouro</span><span lang="en">Editorial summary by Tech &amp; Ouro</span></span>
      </div>
      <div style="display: flex; gap: 8px; margin-left: auto;">
        <a href="#article" class="read-full-link" data-open-article="true" aria-label="Abrir artigo / Open article" data-section-link="{link}">→</a>
      </div>
    </div>
  </div>
</div>'''


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def validate_article_url(value):
    raw = clean_text(value)
    if not raw or len(raw) > URL_MAX_CHARS:
        raise ValueError("url is empty or too long")
    if any(char.isspace() for char in raw) or "\\" in raw:
        raise ValueError("url contains invalid whitespace or separators")

    try:
        parsed = urlsplit(raw)
        hostname = parsed.hostname
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("url cannot be parsed") from exc

    if parsed.scheme.lower() != "https" or not parsed.netloc or not hostname:
        raise ValueError("url must be an absolute https address")
    if parsed.username or parsed.password:
        raise ValueError("url must not include credentials")

    normalized_host = hostname.rstrip(".").lower()
    if normalized_host == "localhost" or normalized_host.endswith((".localhost", ".local")):
        raise ValueError("local addresses are not allowed")

    try:
        ip = ipaddress.ip_address(normalized_host)
    except ValueError:
        try:
            normalized_host.encode("idna")
        except UnicodeError as exc:
            raise ValueError("url hostname is invalid") from exc
    else:
        if not ip.is_global:
            raise ValueError("private or reserved IP addresses are not allowed")

    return raw


def normalize(value):
    value = unicodedata.normalize("NFKD", clean_text(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def article_identity(article):
    return article.get("url") or normalize(article.get("title_pt", ""))


def index_market_focus_score(article):
    source = normalize(article.get("source", ""))
    title = normalize(article.get("title_pt", ""))
    summary = normalize(article.get("summary_pt", ""))
    body = normalize(article.get("body_pt", ""))
    haystack = " ".join(part for part in (source, title, summary, body) if part)
    tokens = set(haystack.split())
    source_match = any(focus_source in source for focus_source in INDEX_MARKET_FOCUS_SOURCES)
    keyword_match = False
    for keyword in INDEX_MARKET_FOCUS_KEYWORDS:
        normalized_keyword = normalize(keyword)
        if not normalized_keyword:
            continue
        if " " in normalized_keyword:
            if normalized_keyword in haystack:
                keyword_match = True
                break
        elif normalized_keyword in tokens:
            keyword_match = True
            break

    score = 0
    if source_match:
        score += 8
    if keyword_match:
        score += 6
    if (source_match or keyword_match) and article.get("category") in INDEX_MARKET_FOCUS_CATEGORIES:
        score += 2
    if keyword_match and article.get("category") == "countries":
        score += 2
    return score


def promote_index_market_focus(selected, sorted_articles):
    focused = []
    used = set()
    for article in sorted_articles:
        if index_market_focus_score(article) <= 0:
            continue
        key = article_identity(article)
        if key in used:
            continue
        focused.append(article)
        used.add(key)
        if len(focused) >= 2:
            break

    if not focused:
        return selected

    combined = focused[:]
    used = {article_identity(article) for article in combined}
    for article in selected:
        key = article_identity(article)
        if key in used:
            continue
        combined.append(article)
        used.add(key)
        if len(combined) >= INDEX_NEWS_LIMIT:
            break
    return combined[:INDEX_NEWS_LIMIT]


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


def normalize_source_name(value):
    value = re.sub(r"\s+\(part\s+\d+\)$", "", str(value or ""), flags=re.IGNORECASE)
    return normalize(value)


def write_queue_draft_sources(selected):
    queue_sources = sorted({normalize_source_name(item.source) for item in selected})
    QUEUE_DRAFT_SOURCES_PATH.write_text(
        json.dumps(queue_sources, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def cleanup_published_queue_sources():
    if not QUEUE_MANIFEST_PATH.exists() or not QUEUE_DRAFT_SOURCES_PATH.exists():
        return

    try:
        manifest = json.loads(QUEUE_MANIFEST_PATH.read_text(encoding="utf-8"))
        selected_sources = set(json.loads(QUEUE_DRAFT_SOURCES_PATH.read_text(encoding="utf-8")))
    except Exception as exc:
        print(f"Queue cleanup: could not read queue metadata: {exc}")
        return

    if not isinstance(manifest, list) or not selected_sources:
        return

    remaining = []
    cleaned = 0
    for entry in manifest:
        if not isinstance(entry, dict):
            continue
        staged_name = entry.get("staged_name") or Path(entry.get("staged_path", "")).name
        entry_key = normalize_source_name(staged_name)
        if entry.get("status") == "staged" and entry_key in selected_sources:
            staged_path = Path(entry.get("staged_path", ""))
            try:
                if staged_path.exists() and staged_path.is_file():
                    staged_path.unlink()
                    cleaned += 1
                entry["status"] = "published-cleaned"
                entry["cleaned_at"] = datetime.now().isoformat(timespec="seconds")
            except Exception as exc:
                entry["status"] = "cleanup-failed"
                entry["cleanup_error"] = str(exc)
                remaining.append(entry)
                continue
        remaining.append(entry)

    QUEUE_MANIFEST_PATH.write_text(
        json.dumps(remaining, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    QUEUE_DRAFT_SOURCES_PATH.unlink(missing_ok=True)
    if cleaned:
        print(f"Queue cleanup: removed {cleaned} staged source file(s) after publish.")


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

        publisher = PublisherAgent()
        archive_update = json.dumps(filtered_archive, indent=2, ensure_ascii=False)
        publisher.publish(
            filtered_archive,
            dry_run=dry_run,
            extra_updates=None if dry_run else {archive_path: archive_update},
        )
        if not dry_run:
            print(f"Archive: updated and saved {len(filtered_archive)} active articles.")
        
        if not dry_run:
            # Delete draft after successful publish
            draft_path.unlink(missing_ok=True)
            cleanup_published_queue_sources()
            print("Publisher: Draft published and removed.")
        return

    # Generation action
    print("Generator: Starting news collection...")
    items, images = CollectorAgent().collect()
    if not items and not images:
        raise ValueError("Collector: no source material found")

    selected = SelectorAgent().select(items)
    write_queue_draft_sources(selected)
    
    manual_path = Path("conteudos/manual-news.json")
    if manual_path.exists():
        print("Generator: using conteudos/manual-news.json.")
        payload = json.loads(manual_path.read_text(encoding="utf-8"))
    else:
        raise ValueError("No AI provider is configured and conteudos/manual-news.json was not found")

    known_sources = {item.source for item in selected}
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
