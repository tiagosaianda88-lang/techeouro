import unittest

from update_news import (
    CATEGORY_LABELS,
    PublisherAgent,
    VerifierAgent,
    replace_news_block,
)


def valid_payload():
    return {
        "articles": [
            {
                "category": category,
                "source": "Reuters",
                "url": "https://example.com",
                "title_pt": f"Titulo {category}",
                "title_en": f"Title {category}",
                "summary_pt": f"Resumo verificado sobre {category}.",
                "summary_en": f"Verified summary about {category}.",
            }
            for category in list(CATEGORY_LABELS)[:6]
        ]
    }


class VerifierAgentTests(unittest.TestCase):
    def test_accepts_six_articles(self):
        result = VerifierAgent().verify(valid_payload(), {"Reuters"})
        self.assertEqual(len(result), 6)

    def test_allows_repeated_category(self):
        payload = valid_payload()
        payload["articles"][-1]["category"] = "economy"
        result = VerifierAgent().verify(payload, {"Reuters"})
        self.assertEqual(len(result), 6)

    def test_rejects_unknown_source(self):
        payload = valid_payload()
        payload["articles"][0]["source"] = "Invented Source"
        with self.assertRaisesRegex(ValueError, "unknown source"):
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


if __name__ == "__main__":
    unittest.main()
