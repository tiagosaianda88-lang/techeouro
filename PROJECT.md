# Project: Tech & Ouro Live News Aggregator

## Architecture
- `scripts/update_news.py`: Main multi-agent pipeline script (Collector -> Selector -> Editor -> Verifier -> Publisher).
- `scripts/test_update_news.py`: Unit tests for the pipeline agents.
- `scripts/verify_translations.py`: Bilingual audit tool verifying layout and translations.
- `conteudos/`: Folder containing manual text sources and backup data.
- `index.html` & `noticias.html`: Target HTML pages with `<!-- AI_NEWS_START -->` markers.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Exploration & Analysis | Investigate existing code, test environment, and feed behavior | none | IN_PROGRESS |
| 2 | Pipeline Implementation | Configure feeds (Expresso, DN, MarketWatch, Barron's), extract source URLs, update renderer, update unit tests, and run update | M1 | PLANNED |
| 3 | Verification & Auditing | Run unit tests, verify translations and layout, audit integrity | M2 | PLANNED |

## Interface Contracts
### AI News JSON Payload
- Must contain exactly 6 articles.
- Each article: category (string), source (string), url (string), title_pt (string), title_en (string), summary_pt (string), summary_en (string).
- category must be one of the defined CATEGORY_LABELS.

## Code Layout
- `scripts/update_news.py`
- `scripts/test_update_news.py`
- `index.html`
- `noticias.html`
