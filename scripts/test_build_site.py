import tempfile
import unittest
from pathlib import Path

from build_site import build


class BuildSiteTests(unittest.TestCase):
    def test_build_contains_public_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = build(Path(tmp) / "public")
            self.assertTrue((destination / "index.html").exists())
            self.assertTrue((destination / "ads.txt").exists())
            self.assertTrue((destination / "robots.txt").exists())
            self.assertTrue((destination / "sitemap.xml").exists())
            self.assertFalse((destination / "conteudos").exists())
            self.assertFalse((destination / "scripts").exists())
            self.assertFalse((destination / ".git").exists())


if __name__ == "__main__":
    unittest.main()
