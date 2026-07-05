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
        }
        
        rendered = self.publisher.render([xss_payload])
        
        # Verify HTML tags inside variables are properly escaped
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<iframe>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;iframe", rendered)
        
        # Verify quotes are escaped in attribute values
        self.assertIn("javascript:alert(&#x27;XSS&#x27;)", rendered)
        
        # But wait! Is "javascript:alert" allowed as a URL scheme?
        # Check if the href attribute contains the raw javascript: protocol:
        self.assertIn('href="javascript:alert(&#x27;XSS&#x27;)"', rendered)
        print("\n[Adversarial Test] XSS payload rendered into link href: ", xss_payload["url"])

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
        }
        
        # Verifier check
        try:
            payload = {"articles": [dict(long_payload, title_pt=f"{long_title} {i}", title_en=f"{long_title} {i}") for i in range(8)]}
            verified = self.verifier.verify(payload, {"Reuters"})
            self.assertEqual(len(verified), 8)
            print("[Adversarial Test] Long text passed VerifierAgent without size limits.")
        except Exception as e:
            print(f"[Adversarial Test] Long text failed VerifierAgent: {e}")
            raise e

        # Publisher render
        rendered = self.publisher.render(verified)
        self.assertTrue(len(rendered) > 360000)
        print(f"[Adversarial Test] Rendered HTML length for long text: {len(rendered)} characters")

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
                "summary_pt": "Summary PT",
                "summary_en": "Summary EN",
            },
            # Path traversal / local file URL
            {
                "category": "tech",
                "source": "Reuters",
                "url": "../../../etc/passwd",
                "title_pt": "Title PT",
                "title_en": "Title EN",
                "summary_pt": "Summary PT",
                "summary_en": "Summary EN",
            }
        ]
        
        for payload in invalid_payloads:
            # Let's see if VerifierAgent rejects empty URLs or trailing whitespace
            try:
                # Verifier checks clean_text(article.get('url'))
                # For "   ", clean_text returns "" which causes it to raise error
                self.verifier.verify({"articles": [dict(payload, title_pt=f"{payload['title_pt']} {i}", title_en=f"{payload['title_en']} {i}") for i in range(8)]}, {"Reuters"})
                print(f"[Adversarial Test] URL validation passed for URL: '{payload['url']}'")
            except ValueError as e:
                print(f"[Adversarial Test] URL validation expectedly failed for URL: '{payload['url']}' - Error: {e}")

if __name__ == "__main__":
    unittest.main()
