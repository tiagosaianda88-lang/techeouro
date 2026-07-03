# Implementation Plan - Tech & Ouro Live News Aggregator

## Milestone 1: Exploration & Codebase Analysis (Explorer)
- **Objective**: Analyze the codebase, current feed parser, Gemini models integration, and layout verification tool.
- **Tasks**:
  1. Investigate feed parsing behavior and internet reachability.
  2. Analyze Gemini editor generation and manual fallback mechanism (`conteudos/manual-news.json`).
  3. Verify translation/bilingual requirements and how `verify_translations.py` checks them.
  4. Formulate the exact edits required for `update_news.py` and `test_update_news.py`.
- **Worker**: teamwork_preview_explorer

## Milestone 2: Pipeline Implementation & Layout Integration (Worker)
- **Objective**: Update the pipeline code, configure all required feeds, include source URLs in articles, and render valid source links.
- **Tasks**:
  1. Add Expresso, Diário de Notícias, and verify Google Wall Street, MarketWatch, Barron's in `RSS_FEEDS`.
  2. Update the `EditorAgent` prompt to require returning the `url` field from the source material.
  3. Update `VerifierAgent` to check for the `url` field and update tests in `test_update_news.py`.
  4. Update `PublisherAgent` to render the source name as a hyperlink (`url`) inside the article cards in `index.html` and `noticias.html`.
  5. Run `update_news.py` to fetch, verify, and publish the 6 bilingual articles.
- **Worker**: teamwork_preview_worker

## Milestone 3: Verification & Auditing (Reviewer, Challenger, Auditor)
- **Objective**: Conduct rigorous checks of correctness, completeness, bilingual compliance, valid links, and execution integrity.
- **Tasks**:
  1. Run unit tests (`test_update_news.py`).
  2. Run bilingual verification (`verify_translations.py`).
  3. Verify the generated news layout in `index.html` and `noticias.html` (6 cards, source links, bilingual text).
  4. Run Forensic Auditor to confirm integrity.
- **Workers**: teamwork_preview_reviewer, teamwork_preview_challenger, teamwork_preview_auditor
