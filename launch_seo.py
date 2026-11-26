"""Prepare a private-beta crawler policy and an offline launch sitemap."""
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
from editorial import CATEGORIES, DESCRIPTIONS

def prepare_beta(output):
    output=Path(output)
    # Keep crawlers out until the owner-approved launch gates are met.
    # This is not authentication; public beta URLs are still accessible.
    (output/"robots.txt").write_text("User-agent: *\nAllow: /\n",encoding="utf-8")
    # Permit crawlers to observe existing noindex directives; do not advertise a sitemap.

def write_launch_sitemap(output,destination,origin):
    """Generate a candidate offline sitemap. Do not publish during beta."""
    from urllib.parse import urlsplit
    parsed=urlsplit(origin)
    if parsed.scheme!="https" or not parsed.hostname or parsed.path not in ("","/") or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError("Expected HTTPS site origin")
    output=Path(output)
    names=["index.html","about.html","guides.html","methodology.html"]
    names += [f"category-{key}.html" for key in sorted(CATEGORIES)]
    names += [f"guide-{key}.html" for key in sorted(DESCRIPTIONS)]
    root=Element("urlset",xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for name in names:
        if not (output/name).is_file():
            raise ValueError(f"Missing public page: {name}")
        SubElement(SubElement(root,"url"),"loc").text=origin.rstrip("/")+"/"+("" if name=="index.html" else name)
    ElementTree(root).write(destination,encoding="utf-8",xml_declaration=True)
