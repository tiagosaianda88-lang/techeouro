# Implementation Plan - Tech & Ouro Live News Aggregator

## Milestone 1: Exploration & Codebase Analysis (Explorer)
- **Objective**: Analyze the codebase, current feed parser, Gemini models integration, and layout verification tool.
- **Status**: DONE (completed in previous run, findings and next steps verified).

## Milestone 2: Pipeline Implementation & Layout Integration (Worker)
- **Objective**: Update the pipeline code, configure feeds, and implement the verification bypass fix.
- **Tasks**:
  1. Fix the source names in `conteudos/manual-news.json` to be raw filenames (e.g., `"economia.txt"` instead of `"conteudos/economia.txt"`).
  2. Fix the verification bypass in `scripts/update_news.py` (lines 336-337) to verify articles against `known_sources` directly instead of `extended_sources`.
  3. Ensure Expresso, Diário de Notícias, Google Wall Street, MarketWatch, and Barron's search feeds are configured.
  4. Ensure URL propagation is complete and source name rendering is intact in HTML.
  5. Run the news update pipeline to update `index.html` and `noticias.html` with exactly 6 bilingual articles.
- **Worker**: teamwork_preview_worker

## Milestone 3: Verification & Auditing (Reviewer, Challenger, Auditor)
- **Objective**: Conduct rigorous correctness, bilingual compliance, valid link checking, and execution integrity checks.
- **Tasks**:
  1. Run unit tests (`test_update_news.py`).
  2. Run translation and broken link check (`verify_translations.py`).
  3. Verify card elements (6 cards, source hyperlinks, no layout glitches).
  4. Run Forensic Auditor to verify integrity.
- **Workers**: teamwork_preview_reviewer, teamwork_preview_challenger, teamwork_preview_auditor
