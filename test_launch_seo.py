import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from editorial import build_guides
from launch_seo import prepare_beta,write_launch_sitemap

class LaunchSEOTests(unittest.TestCase):
    def test_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            out=root/"public"
            out.mkdir()
            build_guides(Path(__file__).with_name("guides.html"),out)
            for name in ("index.html","about.html","methodology.html","account.html"):
                (out/name).touch()
            prepare_beta(out)
            self.assertNotIn("Sitemap:",(out/"robots.txt").read_text())
            self.assertFalse((out/"sitemap.xml").exists())
            dest=root/"candidate.xml"
            write_launch_sitemap(out,dest,"https://bargainiq.netlify.app")
            urls=[e.text for e in ET.parse(dest).getroot().iter() if e.tag.endswith("}loc")]
            self.assertEqual(len(urls),34)
            self.assertEqual(len(set(urls)),34)
            self.assertFalse(any("account.html" in u for u in urls))
            with self.assertRaises(ValueError):
                write_launch_sitemap(out,dest,"http://example.com")
