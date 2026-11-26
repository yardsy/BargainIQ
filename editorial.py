"""Generate reviewed editorial articles from the trusted, committed guide library."""
import re
from pathlib import Path
from html import escape

DESCRIPTIONS={
 "furniture":"Measure furniture, delivery access and equipment clearance before buying.",
 "televisions":"Compare television sizes, screen technology, gaming inputs and installation.",
 "appliances":"Compare appliance dimensions, energy consumption and total ownership costs.",
 "gaming":"Choose a gaming monitor based on resolution, hardware and measured performance.",
 "vehicles":"Compare Australian new-car quotes, drive-away prices and delivery conditions.",
 "clearance":"Evaluate clearance prices, product condition, delivery and warranty.",
 "tv-units":"TV unit dimensions, shelf openings, ventilation, cable access and delivered cost.",
 "coffee-tables":"Footprint, height, finish, cleaning instructions, stability and freight.",
 "desks":"Usable width and depth, knee clearance, load rating, cable management and assembly.",
 "robot-vacuums":"Thresholds, dock dimensions, floor tests, consumables, privacy and warranty.",
 "coffee-machines":"Drink workflow, grinder, heating, cleaning, accessories and servicing.",
 "mattresses":"Size, comfort, base compatibility, trial terms, delivery and warranty.",
}

def build_guides(source,output):
    source,output=Path(source),Path(output)
    html=source.read_text(encoding="utf-8")
    articles=re.findall(r'<article id="([a-z0-9-]+)"><h2>(.*?)</h2>(.*?)</article>',html,re.S)
    if not articles or len({a[0] for a in articles})!=len(articles):
        raise ValueError("Missing or duplicate editorial articles")
    if any(slug not in DESCRIPTIONS for slug,_,_ in articles):
        raise ValueError("Missing editorial metadata")
    style=re.search(r'<style>.*?</style>',html,re.S).group()
    links="".join(f'<li><a href="guide-{slug}.html">{title}</a></li>' for slug,title,_ in articles)
    for slug,title,body in articles:
        related="".join(f'<li><a href="guide-{s}.html">{t}</a></li>' for s,t,_ in articles if s!=slug)
        page=f"""<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{title} | BargainIQ</title><meta name="description" content="{escape(DESCRIPTIONS[slug],quote=True)}">{style}</head><body><header><a href="index.html">BargainIQ</a> · <a href="guides.html">Buying guides</a></header><main><article><h1>{title}</h1><p>Independent editorial guidance for Australian shoppers. Not a hands-on product review or live price comparison.</p>{body}</article><h2>Related buying guides</h2><nav aria-label="Related guides"><ul>{related}</ul></nav><p><a href="index.html">Explore shopping tools</a></p></main><footer><a href="about.html">About and privacy</a></footer></body></html>"""
        (output/f"guide-{slug}.html").write_text(page,encoding="utf-8")
    start=html.index('<nav aria-label="Guide topics">')
    end=html.index('</nav>',start)+len('</nav>')
    landing=html[:start]+f'<nav aria-label="Guide topics"><ul>{links}</ul></nav>'+html[end:]
    # The hub links to complete articles instead of duplicating their full text.
    for slug,title,body in articles:
        landing=landing.replace(f'<article id="{slug}"><h2>{title}</h2>{body}</article>',f'<article id="{slug}"><h2><a href="guide-{slug}.html">{title}</a></h2><p>{escape(DESCRIPTIONS[slug])}</p><a href="guide-{slug}.html">Read the guide</a></article>',1)
    (output/"guides.html").write_text(landing,encoding="utf-8")
