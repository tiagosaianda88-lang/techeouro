import unittest
import html
from update_news import VerifierAgent, PublisherAgent, CATEGORY_LABELS

class ExtremeInputsTests(unittest.TestCase):
    def setUp(self):
        self.verifier = VerifierAgent()
        self.publisher = PublisherAgent()
        self.valid_source = {"Reuters", "Diário de Notícias", "Bloomberg", "Manual Source"}

    def create_valid_article(self, **overrides):
        article = {
            "category": "economy",
            "source": "Reuters",
            "url": "https://reuters.com/news/123",
            "title_pt": "Título de teste",
            "title_en": "Test Title",
            "summary_pt": "R" * 230,
            "summary_en": "S" * 230,
            "body_pt": "Conteúdo de corpo de teste de longa duração.",
            "body_en": "Test body content of long duration.",
        }
        article.update(overrides)
        return article

    def test_special_characters_escaping(self):
        # HTML characters, quotes, backslashes, emojis
        special_str = "<b>Bold</b> & \"Quotes\" 'Single' \\Backslash \\n \\t 🦁 Lion"
        padded_special = (special_str + " " + ("contexto editorial seguro " * 20))[:240]
        article = self.create_valid_article(
            title_pt=special_str,
            title_en=special_str,
            summary_pt=padded_special,
            summary_en=padded_special
        )
        
        # Verify verifier passes it
        payload = {"articles": [self.create_valid_article(
            title_pt=f"{special_str} {i}",
            title_en=f"{special_str} {i}",
            summary_pt=padded_special,
            summary_en=padded_special
        ) for i in range(10)]}
        verified = self.verifier.verify(payload, self.valid_source)
        self.assertEqual(len(verified), 10)
        
        # Verify publisher escapes HTML tags
        rendered = self.publisher.render(verified)
        self.assertNotIn("<b>Bold</b>", rendered)
        self.assertIn("&lt;b&gt;Bold&lt;/b&gt;", rendered)
        self.assertIn("&amp;", rendered)
        self.assertIn("&quot;Quotes&quot;", rendered)
        self.assertIn("&#x27;Single&#x27;", rendered)
        self.assertIn("🦁 Lion", rendered)

    def test_very_long_texts(self):
        # 10,000 character string
        long_str = "A" * 10000
        
        payload = {"articles": [self.create_valid_article(
            title_pt=f"{long_str} {i}",
            title_en=f"{long_str} {i}",
            summary_pt=long_str,
            summary_en=long_str
        ) for i in range(10)]}
        with self.assertRaisesRegex(ValueError, "longer than|220-300"):
            self.verifier.verify(payload, self.valid_source)

    def test_empty_or_whitespace_fields(self):
        # Test empty URL
        payload = {"articles": [self.create_valid_article(url="   ", title_pt=f"Title {i}", title_en=f"Title {i}") for i in range(10)]}
        with self.assertRaisesRegex(ValueError, "missing url"):
            self.verifier.verify(payload, self.valid_source)

        # Test empty title
        payload = {"articles": [self.create_valid_article(title_pt="", title_en=f"Title {i}") for i in range(10)]}
        with self.assertRaisesRegex(ValueError, "missing title_pt"):
            self.verifier.verify(payload, self.valid_source)

    def test_invalid_urls(self):
        bad_urls = [
            "javascript:alert(1)",
            "http://",
            "not-a-url",
            "https://invalid space.com",
            "<script>alert(1)</script>"
        ]
        for url in bad_urls:
            payload = {"articles": [self.create_valid_article(url=url, title_pt=f"Title {i}", title_en=f"Title {i}") for i in range(10)]}
            with self.subTest(url=url):
                with self.assertRaisesRegex(ValueError, "invalid url"):
                    self.verifier.verify(payload, self.valid_source)

if __name__ == "__main__":
    unittest.main()
