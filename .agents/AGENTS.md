# Project Memory & Rules: Tech & Ouro

## Tiago's Launch & Roadmap Goals
* **Developer/Creator:** Tiago Miguel Saianda dos Santos. Works 150%, values high-quality, clean code. Owns a fully remodeled house with a pool and sea view in the Algarve.
* **Site Branding & Merchandise:** The golden lion logo (`logo-lion.jpg`) is a core brand asset intended for future merchandise (shirts, caps, cups). Design elements should respect this premium identity.
* **Phase 1 (Current):** Launch active for Portugal 🇵🇹, Brasil 🇧🇷, and UK 🇬🇧. Custom budget on Google Ads (€5-€10/day) to keep things affordable.
* **Phase 2 (6 to 9 Months):** Expand/uncomment Canada 🇨🇦, USA 🇺🇸, Ireland 🇮🇪, and Switzerland 🇨🇭 on the countries page, and raise the ad budget.
* **Phase 3 (2 Years):** Expand to Australia 🇦🇺 and New Zealand 🇳🇿.

## Coding Rules & Preferences
* **Bilingual Site:** The site is fully bilingual (PT/EN). All text tags should support `lang="pt"` and `lang="en"`.
* **Global Selector:** Navbars must include the `[ PT | EN ]` toggle and link to `script.js` at the bottom of the body.
* **Terminal Widget:** Keep the interactive `#term` widget in `terminal.html` intact (cleanly wrapped in the site template).
* **AI News Aggregator:** Automated via `scripts/update_news.py` and GitHub Actions using free RSS feeds.

## Interaction & Output Rules (Web Chat Synchronization)
* **Style:** Direct to the point, no fluff, no introductory or concluding sentences.
* **Language:** Bilingual (Portuguese/English).
* **Focus:** Target files in the `scripts` and `conteudos` folders.

## Current Status (End of Day 2 - Gemini Integration)
* **Safari Issue:** Safari Reader mode triggered automatically on `mercados.html` and `tech.html`. Fixed by replacing semantic tags (`<header>`, `<section>`) with `<div>`.
* **News Design:** Changed the image pipeline to use a CSS-only "Gold Mosaic" premium banner instead of relying on external image APIs. The site looks very premium.
* **Countries Page (`paises.html`):** Cleaned up layout, removed dummy cards, added a unified `<!-- AI_NEWS_START -->` block at the bottom for global news, keeping tabs clean for macro stats.
* **Gemini Automation:** The user created a Google AI Studio API key (`GEMINI_API_KEY`). It is exported in `~/.zshrc` and `~/.bash_profile`. The `update_news.py` script now successfully runs 100% automated AI journalism.
* **Next Assistant Instructions:** When Tiago opens a new conversation, acknowledge that you read this status and are ready to continue Phase 1 work at 150%. No need to repeat the history, just say you are the "Novo Diretor de Arte".
