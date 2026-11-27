import re
import tempfile
import unittest
from pathlib import Path
from editorial import build_guides,DESCRIPTIONS,CATEGORIES

class EditorialTests(unittest.TestCase):
    def test_generate(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)
            build_guides(Path(__file__).with_name("guides.html"),out)
            hub=(out/"guides.html").read_text()
            self.assertEqual(len(list(out.glob("guide-*.html"))),len(DESCRIPTIONS))
            for slug,description in DESCRIPTIONS.items():
                path=out/f"guide-{slug}.html"
                html=path.read_text()
                self.assertIn(f'href="{path.name}"',hub)
                self.assertIn(description,html)
                self.assertIn('content="noindex,nofollow"',html)
                self.assertEqual(len(re.findall(r"<h1>",html)),1)
                for link in re.findall(r'href="(guide-[a-z0-9-]+\.html)"',html):
                    self.assertTrue((out/link).is_file(),link)
            self.assertNotIn("Shopping checklist:",hub)
            self.assertEqual(len(DESCRIPTIONS),25)
            self.assertEqual(len(CATEGORIES),5)
            self.assertEqual(len(list(out.glob("category-*.html"))),5)
            for key,(title,description,slugs) in CATEGORIES.items():
                page=out/f"category-{key}.html"
                html=page.read_text()
                self.assertIn(f'href="{page.name}"',hub)
                self.assertIn(description,html)
                self.assertIn('href="methodology.html"',html)
                for slug in slugs:
                    self.assertIn(f'href="guide-{slug}.html"',html)
                    self.assertIn(f'href="{page.name}"',(out/f"guide-{slug}.html").read_text())
            self.assertTrue(Path(__file__).with_name("methodology.html").is_file())

    def test_duplicate_slug_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"source.html"
            source.write_text('<article id="furniture"><h2>A</h2></article>'*2)
            with self.assertRaises(ValueError):
                build_guides(source,root)
