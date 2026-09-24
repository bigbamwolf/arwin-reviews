#!/usr/bin/env python3
"""Generate one real, crawlable HTML page per review.

WHY THIS EXISTS
arwinreviews.com is a hash-routed SPA. Every review lives inside the window.LBR
array in reviews.js and every route is a "#/" fragment, which search engines
discard. The sitemap carried six URLs and five of them were fragments. Net
effect: 512 reviews and 138,274 words of original criticism collapsed into ONE
indexable page. That is why the site has no search traffic.

This writes /r/<slug>/index.html for every review, a hub at /r/, and a sitemap
listing all of them, so each review becomes its own indexable document with its
own title, description, schema.org Review markup and canonical URL.
"""
import json, os, re, html, datetime, shutil, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "r")
SITE = "https://arwinreviews.com"

def slugify(name, year):
    s = re.sub(r"[^a-z0-9]+", "-", f"{name} {year}".lower()).strip("-")
    return s

def stars(r):
    if not r: return ""
    full = int(r); half = 1 if r - full >= 0.5 else 0
    return "★" * full + ("½" if half else "")

def load():
    s = open(os.path.join(ROOT, "reviews.js"), encoding="utf8").read()
    return json.loads(s[s.index("["):s.rindex("]") + 1])

CSS = """*{box-sizing:border-box}
:root{--bg:#0a0c0e;--panel:#12171c;--line:rgba(255,255,255,.08);--ink:#ece9e2;
--muted:#9aa1aa;--faint:#6b727b;--gold:#e7b54a;
--serif:"Cormorant Garamond",Georgia,serif;--sans:"Inter",system-ui,sans-serif}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--gold);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:760px;margin:0 auto;padding:32px 20px 80px}
header.top{border-bottom:1px solid var(--line);padding:18px 20px;margin-bottom:8px}
header.top .inner{max-width:760px;margin:0 auto;display:flex;justify-content:space-between;
align-items:center;gap:16px;flex-wrap:wrap}
.brand{font-family:var(--serif);font-size:22px;letter-spacing:.06em;color:var(--ink)}
.brand b{color:var(--gold);font-weight:600}
nav a{color:var(--muted);font-size:13px;margin-left:18px}
.hero{display:flex;gap:24px;align-items:flex-start;margin:28px 0 8px;flex-wrap:wrap}
.hero img{width:150px;border-radius:6px;border:1px solid var(--line);flex:0 0 auto}
h1{font-family:var(--serif);font-size:38px;line-height:1.12;margin:0 0 6px;font-weight:600}
h1 .yr{color:var(--faint);font-weight:400}
.rating{color:var(--gold);font-size:22px;letter-spacing:.08em;margin:6px 0}
.meta{color:var(--faint);font-size:13px}
.review{font-family:var(--serif);font-size:21px;line-height:1.6;margin:26px 0 0;
white-space:pre-wrap}
.spoiler{border:1px solid var(--line);border-left:3px solid var(--gold);
background:var(--panel);padding:12px 16px;margin:22px 0;color:var(--muted);font-size:14px}
footer{border-top:1px solid var(--line);margin-top:46px;padding-top:20px;
color:var(--faint);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px 22px;margin-top:22px}
.grid a{font-size:15px;display:block;padding:4px 0;border-bottom:1px solid var(--line)}
.grid span{color:var(--faint);font-size:12px}
.slots{margin:40px 0 0;display:grid;gap:12px}
.slot{display:block;border:1px solid var(--line);background:var(--panel);
border-radius:8px;padding:16px 18px;transition:border-color .2s}
.slot:hover{border-color:var(--gold);text-decoration:none}
.slot-tag{display:inline-block;font-size:10px;letter-spacing:.16em;text-transform:uppercase;
color:var(--faint);border:1px solid var(--line);border-radius:3px;padding:2px 7px;margin-bottom:8px}
.slot-title{font-family:var(--serif);font-size:20px;color:var(--ink);margin:0 0 4px;font-weight:600}
.slot-body{color:var(--muted);font-size:14px;margin:0}
.slot-cta{display:inline-block;margin-top:9px;color:var(--gold);font-size:13px;letter-spacing:.04em}
.slot-note{color:var(--faint);font-size:11.5px;margin:2px 2px 0;line-height:1.5}
@media(max-width:560px){h1{font-size:29px}.review{font-size:19px}.hero img{width:112px}
.slot-title{font-size:18px}}"""

HEAD = """<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/r/review.css" />
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png" />"""

TOP = """<header class="top"><div class="inner">
<a class="brand" href="/">ARWIN <b>REVIEWS</b></a>
<nav><a href="/">Home</a><a href="/r/">All reviews</a><a href="/work.html">Work with Arwin</a></nav>
</div></header>"""

AFF_FALLBACK_WATCH = "https://www.justwatch.com/ph/search?q={q}"

def affiliate_lead():
    """Read the first PAYING affiliate link straight out of site_config.js so the
    515 review pages and the SPA hero slot can never drift apart. One place to
    paste a tracked link. Returns None on any parse trouble, and the pages then
    ship the advertiser pitch alone rather than breaking the build."""
    try:
        src = open(os.path.join(ROOT, "site_config.js"), encoding="utf8").read()
        start = src.index("affiliates:")
        block = src[start:src.index("\n  },", start)]
        for obj in re.findall(r"\{[^{}]*\}", block):
            url = re.search(r'url:\s*"([^"]*)"', obj)
            payout = re.search(r'payout:\s*"([^"]*)"', obj)
            if not url or url.group(1).startswith("TODO"):
                continue
            if payout and payout.group(1) != "none":
                name = re.search(r'name:\s*"([^"]*)"', obj)
                blurb = re.search(r'blurb:\s*"([^"]*)"', obj)
                cta = re.search(r'cta:\s*"([^"]*)"', obj)
                return {"url": url.group(1),
                        "name": name.group(1) if name else "Recommended",
                        "blurb": blurb.group(1) if blurb else "",
                        "cta": cta.group(1) if cta else "Take a look"}
        return None
    except Exception:
        return None

LEAD = None

def slots(title):
    """Ad inventory on a review page. Until 2026-09-25 these 515 pages, the only
    crawlable URLs on the site, carried no placement at all while every ad unit
    sat inside the hash routed SPA that Google cannot rank."""
    q = urllib.parse.quote_plus(title)
    out = ['<section class="slots">']
    if LEAD:
        out.append(
            f'<a class="slot" href="{html.escape(LEAD["url"])}" target="_blank" rel="sponsored noopener noreferrer">'
            f'<span class="slot-tag">Affiliate</span>'
            f'<p class="slot-title">{html.escape(LEAD["name"])}</p>'
            f'<p class="slot-body">{html.escape(LEAD["blurb"])}</p>'
            f'<span class="slot-cta">{html.escape(LEAD["cta"])} &#8599;</span></a>')
    out.append(
        f'<a class="slot" href="{AFF_FALLBACK_WATCH.format(q=q)}" target="_blank" rel="sponsored noopener noreferrer">'
        f'<span class="slot-tag">Where to watch</span>'
        f'<p class="slot-title">Stream {html.escape(title)} in the Philippines</p>'
        f'<p class="slot-body">A live check of every legal streaming option for this exact film, PH region.</p>'
        f'<span class="slot-cta">Check availability &#8599;</span></a>')
    out.append(
        '<a class="slot" href="/work.html">'
        '<span class="slot-tag">Slot open</span>'
        '<p class="slot-title">Your film here</p>'
        '<p class="slot-body">A paid, disclosed opening week placement on a Philippine film archive. '
        'P3,500 for the week at the founding rate. A real verdict, on the week your film matters most.</p>'
        '<span class="slot-cta">Book this slot &#8599;</span></a>')
    out.append('<p class="slot-note">Disclosed links. Nothing here buys a rating, and a paid '
               'placement never changes a verdict.</p>')
    out.append('</section>')
    return "\n".join(out)


def page(rv, slug):
    title = rv["name"]; year = rv.get("year") or ""
    st = stars(rv.get("rating"))
    body = (rv.get("review") or "").strip()
    desc = re.sub(r"\s+", " ", body)[:155]
    poster = rv.get("poster") or ""
    watched = rv.get("watched") or ""
    url = f"{SITE}/r/{slug}/"
    ld = {"@context": "https://schema.org", "@type": "Review",
          "itemReviewed": {"@type": "Movie", "name": title,
                           **({"datePublished": str(year)} if year else {})},
          "author": {"@type": "Person", "name": "Arwin Edward Bagaslao"},
          "publisher": {"@type": "Organization", "name": "ARWIN REVIEWS"},
          "url": url, "reviewBody": body}
    if rv.get("rating"):
        ld["reviewRating"] = {"@type": "Rating", "ratingValue": rv["rating"],
                              "bestRating": 5, "worstRating": 0.5}
    if watched: ld["datePublished"] = watched
    t = f"{title} ({year}) review" if year else f"{title} review"
    return f"""<!doctype html><html lang="en"><head>
<title>{html.escape(t)} · ARWIN REVIEWS</title>
{HEAD}
<meta name="description" content="{html.escape(desc)}" />
<link rel="canonical" href="{url}" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{html.escape(t)}" />
<meta property="og:description" content="{html.escape(desc)}" />
<meta property="og:url" content="{url}" />
{f'<meta property="og:image" content="{html.escape(poster)}" />' if poster else ''}
<meta name="twitter:card" content="summary_large_image" />
<script type="application/ld+json">{json.dumps(ld)}</script>
</head><body>
{TOP}
<div class="wrap">
<article>
<div class="hero">
{f'<img src="{html.escape(poster)}" alt="{html.escape(title)} poster" loading="lazy" />' if poster else ''}
<div>
<h1>{html.escape(title)} <span class="yr">{year}</span></h1>
<div class="rating">{st}</div>
<div class="meta">Reviewed by Arwin Edward Bagaslao{f" · {watched}" if watched else ""}</div>
</div>
</div>
{'<div class="spoiler">This review contains spoilers.</div>' if rv.get("spoiler") else ''}
<div class="review">{html.escape(body)}</div>
</article>
{slots(title)}
<footer>
<p>Part of <a href="/">ARWIN REVIEWS</a>, a Philippine film archive on global cinema.
{len(REVIEWS)} reviews and counting. <a href="/r/">Browse them all</a>.</p>
<p>Cinemas and distributors, the homepage slot is <a href="/work.html">open and priced</a>.</p>
</footer>
</div></body></html>"""

def hub(items):
    rows = "\n".join(
        f'<a href="/r/{s}/">{html.escape(r["name"])} <span>{r.get("year","")} {stars(r.get("rating"))}</span></a>'
        for s, r in items)
    return f"""<!doctype html><html lang="en"><head>
<title>All film reviews · ARWIN REVIEWS</title>
{HEAD}
<meta name="description" content="Every film review by Philippine critic Arwin Edward Bagaslao. {len(items)} reviews, {sum(r.get('words',0) for _,r in items):,} words, opening week to festival." />
<link rel="canonical" href="{SITE}/r/" />
</head><body>
{TOP}
<div class="wrap">
<h1>All reviews</h1>
<p class="meta">{len(items)} reviews, {sum(r.get('words',0) for _,r in items):,} words.</p>
<div class="grid">{rows}</div>
</div></body></html>"""

REVIEWS = []

def main():
    global REVIEWS, LEAD
    LEAD = affiliate_lead()
    print("affiliate lead:", LEAD["name"] if LEAD else "none paying yet, pitch only")
    REVIEWS = [r for r in load() if (r.get("review") or "").strip()]
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "review.css"), "w", encoding="utf8").write(CSS)
    seen, items = {}, []
    for r in REVIEWS:
        s = slugify(r["name"], r.get("year") or "")
        if s in seen:
            seen[s] += 1; s = f"{s}-{seen[s]}"
        else:
            seen[s] = 1
        d = os.path.join(OUT, s); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf8").write(page(r, s))
        items.append((s, r))
    items.sort(key=lambda x: x[1]["name"].lower())
    open(os.path.join(OUT, "index.html"), "w", encoding="utf8").write(hub(items))

    today = datetime.date.today().isoformat()
    urls = [(f"{SITE}/", "1.0"), (f"{SITE}/r/", "0.9"), (f"{SITE}/work.html", "0.6")]
    urls += [(f"{SITE}/r/{s}/", "0.8") for s, _ in items]
    body = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>monthly</changefreq><priority>{p}</priority></url>" for u, p in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body + "\n</urlset>\n")
    print(f"wrote {len(items)} review pages + hub, sitemap has {len(urls)} urls")

if __name__ == "__main__":
    main()
