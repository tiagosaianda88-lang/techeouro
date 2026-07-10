import unittest
from pathlib import Path

from update_news import (
    CATEGORY_LABELS,
    PublisherAgent,
    VerifierAgent,
    replace_news_block,
)


def valid_payload():
    categories = list(CATEGORY_LABELS)
    return {
        "articles": [
            {
                "category": categories[i % len(categories)],
                "source": "Reuters",
                "url": "https://example.com",
                "title_pt": f"Titulo {i}",
                "title_en": f"Title {i}",
                "summary_pt": f"Resumo verificado {i}. " + ("Contexto editorial original e claro para leitores da Tech & Ouro, com fonte atribuída, impacto económico, enquadramento internacional e linguagem prudente. " * 2)[:210],
                "summary_en": f"Verified summary {i}. " + ("Original and clear editorial context for Tech & Ouro readers, with attributed sourcing, economic impact, international framing and measured language. " * 2)[:210],
                "body_pt": f"Conteudo detalhado pt {i}.",
                "body_en": f"Detailed content en {i}.",
            }
            for i in range(10)
        ]
    }


class VerifierAgentTests(unittest.TestCase):
    def test_accepts_ten_articles(self):
        result = VerifierAgent().verify(valid_payload(), {"Reuters"})
        self.assertEqual(len(result), 10)

    def test_allows_repeated_category(self):
        payload = valid_payload()
        payload["articles"][-1]["category"] = "economy"
        result = VerifierAgent().verify(payload, {"Reuters"})
        self.assertEqual(len(result), 10)

    def test_rejects_unknown_source(self):
        payload = valid_payload()
        payload["articles"][0]["source"] = "Invented Source"
        with self.assertRaisesRegex(ValueError, "unknown source"):
            VerifierAgent().verify(payload, {"Reuters"})

    def test_rejects_source_name_that_only_contains_known_source(self):
        payload = valid_payload()
        payload["articles"][0]["source"] = "Reuters Fan Club"
        with self.assertRaisesRegex(ValueError, "unknown source"):
            VerifierAgent().verify(payload, {"Reuters"})

    def test_rejects_unsafe_url(self):
        payload = valid_payload()
        payload["articles"][0]["url"] = "javascript:alert(1)"
        with self.assertRaisesRegex(ValueError, "invalid url"):
            VerifierAgent().verify(payload, {"Reuters"})

    def test_rejects_summary_outside_editorial_range(self):
        payload = valid_payload()
        payload["articles"][0]["summary_en"] = "Too short."
        with self.assertRaisesRegex(ValueError, "220-300"):
            VerifierAgent().verify(payload, {"Reuters"})


class PublisherAgentTests(unittest.TestCase):
    def test_replaces_only_marker_contents(self):
        original = "before\n<!-- AI_NEWS_START -->old<!-- AI_NEWS_END -->\nafter"
        updated = replace_news_block(original, "new")
        self.assertEqual(
            updated,
            "before\n<!-- AI_NEWS_START -->\nnew\n<!-- AI_NEWS_END -->\nafter",
        )

    def test_render_escapes_model_output(self):
        article = valid_payload()["articles"][0]
        article["title_pt"] = '<script>alert("x")</script>'
        rendered = PublisherAgent().render([article])
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_render_includes_editorial_source_attribution(self):
        article = valid_payload()["articles"][0]
        rendered = PublisherAgent().render([article])
        self.assertIn("Fonte: ", rendered)
        self.assertIn("Source: ", rendered)
        self.assertIn("Resumo editorial Tech &amp; Ouro", rendered)
        self.assertIn("Editorial summary by Tech &amp; Ouro", rendered)

    def test_render_does_not_include_whatsapp_share_button(self):
        article = valid_payload()["articles"][0]
        rendered = PublisherAgent().render([article])
        self.assertNotIn("WhatsApp", rendered)
        self.assertNotIn("wa.me", rendered)


class ProviderSafetyTests(unittest.TestCase):
    def test_removed_provider_does_not_reappear(self):
        source = Path("scripts/update_news.py").read_text(encoding="utf-8")
        removed_provider = "gem" + "ini"
        blocked = [
            removed_provider.upper() + "_API_KEY",
            "google import genai",
            removed_provider + "-",
            removed_provider.title() + " API",
        ]
        for term in blocked:
            with self.subTest(term=term):
                self.assertNotIn(term, source)


if __name__ == "__main__":
    unittest.main()
