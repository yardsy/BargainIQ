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
 "tv-units":"Find shallow TV units under 40 cm deep: check console shelf dimensions, ventilation, cable access and delivered cost.",
 "coffee-tables":"Footprint, height, finish, cleaning instructions, stability and freight.",
 "desks":"Choose a shallow desk for a small home office: compare usable dimensions, knee clearance, load rating and assembly.",
 "robot-vacuums":"Thresholds, dock dimensions, floor tests, consumables, privacy and warranty.",
 "coffee-machines":"Drink workflow, grinder, heating, cleaning, accessories and servicing.",
 "mattresses":"Size, comfort, base compatibility, trial terms, delivery and warranty.",
 "sofas":"Footprint, access, seat depth, fabric care, delivery and returns.",
 "soundbars":"Dimensions, HDMI compatibility, speaker power, measured performance and warranty.",
 "tv-mounts":"VESA, weight, wall structure, viewing height, cable access and installation quote.",
 "tv-size":"Screen width, seating distance, room light, exact model and mounting cost.",
 "streaming":"App support, connection reliability, resolution, motion settings and subscription cost.",
 "washing-machines":"Capacity, programme limits, dimensions, energy, water and installation.",
 "air-fryers":"Cooking tasks, usable capacity, clearances, cleaning and accessories.",
 "laptops":"Applications, RAM, storage, display, battery tests, ports and warranty.",
 "gaming-pcs":"Exact parts, game benchmarks, power supply, cooling, upgrades and total cost.",
 "routers":"Connection compatibility, coverage, ports, update policy and total hardware cost.",
 "used-cars":"Variant, kilometres, history, inspection, registration and total cost.",
 "demo-cars":"Registration date, kilometres, condition, warranty, new-car alternative and price.",
 "car-finance":"Cash price, loan amount, term, fees, balloon and total payable.",
 "car-running-costs":"Annual distance, energy, insurance, registration, servicing, tyres and depreciation scenarios.",
 "delivery":"Compare delivered furniture prices in Australia, including postcode-specific freight, installation and return terms.",
 "price-history":"Exact product, retailer, observation dates, delivery, target price and current availability.",
 "refurbished":"Condition, testing, accessories, battery health where relevant, warranty and delivered cost.",
 "shopping-requests":"Create a requirements-first shopping request with a delivered budget, maximum dimensions, condition and compatibility.",
}

CATEGORIES={
  "furniture": [
    "Furniture and homewares",
    "Measure your room, check material and delivery requirements, and compare furniture that fits.",
    [
      "furniture",
      "tv-units",
      "coffee-tables",
      "desks",
      "mattresses",
      "sofas"
    ]
  ],
  "entertainment": [
    "TVs and entertainment",
    "Choose screen sizes, audio and installation for your space.",
    [
      "televisions",
      "soundbars",
      "tv-mounts",
      "tv-size",
      "streaming"
    ]
  ],
  "appliances": [
    "Electrical appliances",
    "Compare practical capacity, operating costs and maintenance.",
    [
      "appliances",
      "robot-vacuums",
      "coffee-machines",
      "washing-machines",
      "air-fryers"
    ]
  ],
  "computing": [
    "Computers and gaming",
    "Choose hardware that suits your applications, games and home network.",
    [
      "gaming",
      "laptops",
      "gaming-pcs",
      "routers"
    ]
  ],
  "automotive": [
    "Automotive",
    "Compare vehicle quotes, condition, finance costs and ownership expenses.",
    [
      "vehicles",
      "used-cars",
      "demo-cars",
      "car-finance",
      "car-running-costs"
    ]
  ],
  "shopping": [
    "Shopping and clearance",
    "Compare delivered prices, condition and actual observed price history.",
    [
      "clearance",
      "delivery",
      "price-history",
      "refurbished",
      "shopping-requests"
    ]
  ]
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
    by_slug={slug:(title,body) for slug,title,body in articles}
    assigned=[slug for _,_,slugs in CATEGORIES.values() for slug in slugs]
    if len(set(assigned))!=len(assigned) or set(assigned)!=set(by_slug):
        raise ValueError("Every guide must belong to exactly one category")
    category_links="".join(f'<li><a href="category-{key}.html">{escape(title)}</a></li>' for key,(title,_,_) in CATEGORIES.items())
    links="".join(f'<li><a href="guide-{slug}.html">{title}</a></li>' for slug,title,_ in articles)
    for key,(heading,description,slugs) in CATEGORIES.items():
        cards="".join(f'<article><h2><a href="guide-{slug}.html">{by_slug[slug][0]}</a></h2><p>{escape(DESCRIPTIONS[slug])}</p><a href="guide-{slug}.html">Read the guide</a></article>' for slug in slugs)
        page=f"""<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{escape(heading)} buying guides | BargainIQ</title><meta name="description" content="{escape(description,quote=True)}">{style}</head><body><header><a href="index.html">BargainIQ</a> · <a href="guides.html">Buying guides</a></header><main><h1>{escape(heading)}</h1><p>{escape(description)}</p><p>Independent buying guidance, not a live inventory catalogue.</p>{cards}<nav aria-label="Other categories"><ul>{category_links}</ul></nav></main><footer><a href="methodology.html">Editorial methodology</a> · <a href="about.html">About and privacy</a></footer></body></html>"""
        (output/f"category-{key}.html").write_text(page,encoding="utf-8")
    for slug,title,body in articles:
        key=next(k for k,(_,_,slugs) in CATEGORIES.items() if slug in slugs)
        heading,_,slugs=CATEGORIES[key]
        related="".join(f'<li><a href="guide-{s}.html">{by_slug[s][0]}</a></li>' for s in slugs if s!=slug)
        page=f"""<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{title} | BargainIQ</title><meta name="description" content="{escape(DESCRIPTIONS[slug],quote=True)}">{style}</head><body><header><a href="index.html">BargainIQ</a> · <a href="guides.html">Buying guides</a></header><main><article><h1>{title}</h1><p>Independent editorial guidance for Australian shoppers. Not a hands-on product review or live price comparison.</p>{body}</article><p><a href="category-{key}.html">More {escape(heading)} guides</a></p><h2>Related buying guides</h2><nav aria-label="Related guides"><ul>{related}</ul></nav><p><a href="index.html">Explore shopping tools</a></p></main><footer><a href="methodology.html">Editorial methodology</a> · <a href="about.html">About and privacy</a></footer></body></html>"""
        (output/f"guide-{slug}.html").write_text(page,encoding="utf-8")
    start=html.index('<nav aria-label="Guide topics">')
    end=html.index('</nav>',start)+len('</nav>')
    landing=html[:start]+f'<h2>Browse by category</h2><nav aria-label="Guide topics"><ul>{category_links}</ul></nav><p><a href="methodology.html">How we compare products</a></p>'+html[end:]
    # The hub links to complete articles instead of duplicating their full text.
    for slug,title,body in articles:
        landing=landing.replace(f'<article id="{slug}"><h2>{title}</h2>{body}</article>',f'<article id="{slug}"><h2><a href="guide-{slug}.html">{title}</a></h2><p>{escape(DESCRIPTIONS[slug])}</p><a href="guide-{slug}.html">Read the guide</a></article>',1)
    (output/"guides.html").write_text(landing,encoding="utf-8")
