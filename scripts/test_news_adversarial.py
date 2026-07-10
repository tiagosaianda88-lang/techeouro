import unittest
import html
import re
from update_news import (
    VerifierAgent,
    PublisherAgent,
    clean_text,
    normalize,
    replace_news_block,
    CATEGORY_LABELS,
)

class AdversarialNewsTests(unittest.TestCase):
    def setUp(self):
        self.verifier = VerifierAgent()
        self.publisher = PublisherAgent()

    def test_special_characters_escaping(self):
        """Test how special characters, HTML tags, and emojis are escaped in rendering."""
        xss_payload = {
            "category": "tech",
            "source": "🦁 Lion News & Co <script>alert(1)</script>",
            "url": "javascript:alert('XSS')",
            "title_pt": "Título <script>alert('pt')</script> & €",
            "title_en": "Title <script>alert('en')</script> & $",
            "summary_pt": "Resumo <iframe src='x'></iframe> 🦁 🇵🇹",
            "summary_en": "Summary <iframe src='x'></iframe> 🦁 🇬🇧",
            "body_pt": "Corpo com emoji 🦁 e XSS <script>alert('pt')</script>",
            "body_en": "Body with emoji 🦁 and XSS <script>alert('en')</script>",
        }
        
        safe_payload = dict(xss_payload, url="https://example.com/story")
        rendered = self.publisher.render([safe_payload])
        
        # Verify HTML tags inside variables are properly escaped
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<iframe>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;iframe", rendered)
        
        with self.assertRaisesRegex(ValueError, "absolute https"):
            self.publisher.render([xss_payload])

    def test_very_long_text(self):
        """Test how the pipeline handles very long strings in titles, summaries, and URLs."""
        long_title = "A" * 10000
        long_summary = "B" * 50000
        long_url = "https://" + "C" * 10000 + ".com"
        
        long_payload = {
            "category": "gold",
            "source": "Reuters",
            "url": long_url,
            "title_pt": long_title,
            "title_en": long_title,
            "summary_pt": long_summary,
            "summary_en": long_summary,
            "body_pt": long_summary,
            "body_en": long_summary,
        }
        
        payload = {"articles": [dict(long_payload, title_pt=f"{long_title} {i}", title_en=f"{long_title} {i}") for i in range(10)]}
        with self.assertRaisesRegex(ValueError, "invalid url|longer than|220-300"):
            self.verifier.verify(payload, {"Reuters"})

    def test_invalid_urls(self):
        """Test with empty or invalid/malformed URLs."""
        invalid_payloads = [
            # Empty URL
            {
                "category": "tech",
                "source": "Reuters",
                "url": "   ",
                "title_pt": "Title PT",
                "title_en": "Title EN",
                "summary_pt": "R" * 230,
                "summary_en": "S" * 230,
                "body_pt": "Body PT",
                "body_en": "Body EN",
            },
            # Path traversal / local file URL
            {
                "category": "tech",
                "source": "Reuters",
                "url": "../../../etc/passwd",
                "title_pt": "Title PT",
                "title_en": "Title EN",
                "summary_pt": "R" * 230,
                "summary_en": "S" * 230,
                "body_pt": "Body PT",
                "body_en": "Body EN",
            }
        ]
        
        for payload in invalid_payloads:
            with self.subTest(url=payload["url"]):
                with self.assertRaisesRegex(ValueError, "missing url|invalid url"):
                    self.verifier.verify({"articles": [dict(payload, title_pt=f"{payload['title_pt']} {i}", title_en=f"{payload['title_en']} {i}") for i in range(10)]}, {"Reuters"})

if __name__ == "__main__":
    unittest.main()
