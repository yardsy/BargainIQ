import unittest
import tempfile
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from unittest.mock import patch
import shutil
import build_site

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.ids=set()
        self.robots=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.add(a["id"])
        if tag in ("a","script","img","link") and (a.get("href") or a.get("src")):
            self.links.append(a.get("href") or a.get("src"))
        if tag=="meta" and a.get("name")=="robots":self.robots.append(a.get("content",""))

class PublicBuildTests(unittest.TestCase):
    def test_built_artifact(self):
        root=Path(build_site.__file__).resolve().parent
        with tempfile.TemporaryDirectory() as d:
            stage=Path(d)
            for p in root.iterdir():
                if p.is_file() and p.suffix in (".html",".json",".js",".py"):
                    shutil.copy2(p,stage/p.name)
            with patch.object(build_site,"__file__",str(stage/"build_site.py")):
                build_site.main()
            out=stage/"public"
            pages={}
            for p in out.glob("*.html"):
                parser=Page()
                parser.feed(p.read_text(encoding="utf-8"))
                pages[p.name]=parser
            self.assertEqual(len(list(out.glob("guide-*.html"))),30)
            self.assertEqual(len(list(out.glob("category-*.html"))),6)
            for name,page in pages.items():
                for link in page.links:
                    u=urlsplit(link)
                    if u.scheme or u.netloc:continue
                    target=unquote(u.path).lstrip("/") or name
                    if target.startswith("${"):continue
                    self.assertTrue((out/target).is_file(),f"{name}: broken link {link}")
                    if u.fragment and target in pages:
                        self.assertIn(unquote(u.fragment),pages[target].ids,f"{name}: broken fragment {link}")
            self.assertFalse(list(out.glob("*.py")))
            self.assertFalse(list(out.glob("*.md")))
            self.assertFalse((out/"test_engagement.js").exists())
            self.assertFalse((out/"sitemap.xml").exists())
            self.assertTrue((out/"robots.txt").exists())
            headers=(out/"_headers").read_text()
            for header in ("X-Robots-Tag: noindex, nofollow","X-Frame-Options: DENY","Referrer-Policy: no-referrer","X-Content-Type-Options: nosniff"):
                self.assertIn(header,headers)
            for p in [out/"index.html",out/"account.html"]:
                self.assertNotIn('name="bargainiq-analytics-endpoint"',p.read_text())

    def test_rebuild_replaces_obsolete_output(self):
        root=Path(build_site.__file__).resolve().parent
        with tempfile.TemporaryDirectory() as d:
            stage=Path(d)
            for p in root.iterdir():
                if p.is_file() and p.suffix in (".html",".json",".js",".py"):
                    shutil.copy2(p,stage/p.name)
            out=stage/"public"
            out.mkdir()
            (out/"obsolete.html").write_text("obsolete")
            (out/"obsolete-folder").mkdir()
            (out/"obsolete-folder"/"old.txt").write_text("old")
            (stage/"retail.json").write_text('{"products":[]}')
            with patch.object(build_site,"__file__",str(stage/"build_site.py")):
                build_site.main()
                self.assertTrue((out/"retail.json").is_file())
                (stage/"retail.json").unlink()
                build_site.main()
            self.assertFalse((out/"obsolete.html").exists())
            self.assertFalse((out/"obsolete-folder").exists())
            self.assertFalse((out/"retail.json").exists())
            self.assertTrue((out/"index.html").is_file())
