#!/usr/bin/env python3
"""ARWIN REVIEWS static SEO build, v2 (drop in replacement for tools/build_review_pages.py).

Writes, from reviews.js + data.js + omdb.json:
  /r/<slug>/index.html       one page per film (rewatches merged), Review + Movie + Breadcrumb JSON-LD
  /r/<old-slug>-2/           redirect stubs for retired duplicate URLs (noindex, canonical to the main page)
  /r/index.html              all reviews hub
  /lists/<slug>/index.html   ranked list pages with ItemList JSON-LD
  /lists/index.html          lists hub
  /sitemap.xml               every indexable URL with a real lastmod
  index.html                 static latest reviews + ranked years block between SEO markers (if markers exist)
Optional: --indexnow pings Bing/Yandex IndexNow with URLs whose lastmod is today.
"""
import json, os, re, html, datetime, shutil, urllib.parse, urllib.request, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "r")
LOUT = os.path.join(ROOT, "lists")
SITE = "https://arwinreviews.com"
GA_ID = "G-ZK111NQYT1"
INDEXNOW_KEY = "0fd74882ca254c76a6adc73233330d08"
LETTERBOXD = "https://letterboxd.com/bigbamwolf/"
INSTAGRAM = "https://www.instagram.com/bigbamwolf/"
CRITIC = "Arwin Edward Bagaslao"
THIN_WORDS = 40
LIST_MIN_PAGE = 8
LIST_MIN_INDEX = 10
LIST_SKIP = re.compile(r"watchlist|wishlist|your life in film", re.I)
SEO_START, SEO_END = "<!-- SEO:STATIC -->", "<!-- /SEO:STATIC -->"
TODAY = datetime.date.today().isoformat()


def slugify(name, year=""):
    s = re.sub(r"[^a-z0-9]+", "-", f"{name} {year}".lower()).strip("-")
    return s


def stars(r):
    if not r: return ""
    full = int(r); half = 1 if r - full >= 0.5 else 0
    return "★" * full + ("½" if half else "")


def rating_text(r):
    if not r: return ""
    return (f"{r:.1f}".rstrip("0").rstrip(".")) + "/5"


def load_js_array(name):
    s = open(os.path.join(ROOT, name), encoding="utf8").read()
    return json.loads(s[s.index("["):s.rindex("]") + 1])


def load_data():
    d = open(os.path.join(ROOT, "data.js"), encoding="utf8").read()
    return json.loads(d[d.index("{"):d.rindex("}") + 1])


META_FIELDS = ("Year", "Director", "Genre", "Runtime", "imdbID")


def load_omdb():
    meta = os.path.join(ROOT, "film_meta.json")
    raw = os.path.join(ROOT, "omdb.json")
    out = {}
    if os.path.exists(raw):
        try:
            for k, v in json.load(open(raw, encoding="utf8")).items():
                if isinstance(v, dict) and v.get("Response") == "True":
                    out[k] = {f: v.get(f, "") for f in META_FIELDS}
        except Exception:
            out = {}
    if out:
        json.dump(out, open(meta, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        return out
    if os.path.exists(meta):
        try:
            return json.load(open(meta, encoding="utf8"))
        except Exception:
            pass
    return {}


def adsense_tag():
    try:
        src = open(os.path.join(ROOT, "site_config.js"), encoding="utf8").read()
        m = re.search(r'adsense:\s*\{\s*client:\s*"([^"]*)"', src)
        c = m.group(1).strip() if m else ""
    except Exception:
        c = ""
    if not re.fullmatch(r"ca-pub-\d{16}", c): return ""
    return (f'<!-- ADSENSE -->\n<meta name="google-adsense-account" content="{c}" />\n'
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={c}" '
            f'crossorigin="anonymous"></script>\n<!-- /ADSENSE -->')


def omdb_for(omdb, name, year):
    v = omdb.get(f"{name}|{year}")
    if not v: return None
    if str(v.get("Year", ""))[:4] != str(year): return None
    return v


def na(x):
    return "" if not x or x == "N/A" else x


def poster_url(p):
    if not p: return ""
    if p.startswith("http"): return p
    return "/" + p.lstrip("/")


def thumb_url(p):
    if not p or p.startswith("http"): return ""
    base = os.path.splitext(os.path.basename(p))[0]
    t = os.path.join(ROOT, "img", "t", base + ".webp")
    return f"/img/t/{base}.webp" if os.path.exists(t) else ""


def clean_text(body):
    t = body
    t = re.sub(r"(?im)^\s*non[\s-]?spoiler(?:\s+thoughts?)?\s*(?:\(summary\))?\s*:\s*", "", t)
    t = re.sub(r"(?im)^\s*this review contains spoilers[^\n]*\n?", "", t)
    t = re.sub(r"[⚠️]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def summary_part(body):
    m = re.search(r"(?i)spoilers ahead", body)
    return clean_text(body[:m.start()] if m else body)


def clip(text, n):
    if len(text) <= n: return text
    cut = text[:n].rsplit(" ", 1)[0].rstrip(",;:.")
    return cut + "…"


def first_sentence(text, n=170):
    m = re.match(r"(.{40,}?[.!?])(\s|$)", text)
    return clip(m.group(1) if m else text, n)


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
.cred{color:var(--faint);font-size:12.5px;margin-top:4px;letter-spacing:.02em}
.guest{display:inline-block;font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);border:1px solid rgba(231,181,74,.4);border-radius:3px;padding:2px 7px;margin-bottom:8px}
.slot-note{color:var(--faint);font-size:11.5px;margin:2px 2px 0;line-height:1.5}
@media(max-width:560px){h1{font-size:29px}.review{font-size:19px}.hero img{width:112px}
.slot-title{font-size:18px}}"""
CSS += """
.verdict{color:var(--muted);font-size:14px;margin:2px 0 0}
.crumbs{font-size:12.5px;color:var(--faint);margin:18px 0 0}.crumbs a{color:var(--muted)}
.facts{color:var(--faint);font-size:13px;margin:6px 0 0}
.earlier{margin:34px 0 0;padding-top:18px;border-top:1px solid var(--line)}
.earlier h2,.related h2,.inlists h2{font-family:var(--serif);font-size:24px;margin:0 0 10px;font-weight:600}
.earlier .review{font-size:19px;margin-top:10px}
.related{margin:40px 0 0}.related h3{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);margin:18px 0 6px;font-weight:500}
.related ul,.inlists ul{list-style:none;padding:0;margin:0}
.related li,.inlists li{padding:5px 0;border-bottom:1px solid var(--line);font-size:15px}
.related li span,.inlists li span{color:var(--faint);font-size:12.5px;margin-left:6px}
.inlists{margin:34px 0 0}
ol.ranked{list-style:none;padding:0;margin:24px 0 0;counter-reset:rk}
ol.ranked li{display:flex;gap:14px;align-items:flex-start;padding:14px 0;border-bottom:1px solid var(--line)}
ol.ranked .n{font-family:var(--serif);font-size:28px;color:var(--gold);min-width:42px;text-align:right;line-height:1}
ol.ranked img{width:60px;height:90px;object-fit:cover;border-radius:4px;border:1px solid var(--line);flex:0 0 auto}
ol.ranked .t{font-family:var(--serif);font-size:21px;line-height:1.2}
ol.ranked .s{color:var(--gold);font-size:14px;margin:2px 0}
ol.ranked p{margin:4px 0 0;color:var(--muted);font-size:14px;line-height:1.5}
.tagline{font-family:var(--serif);font-style:italic;color:var(--muted);font-size:19px;margin:4px 0 0}
.listgrp h2{font-family:var(--serif);font-size:24px;margin:30px 0 6px}
"""

HEAD = """<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/r/review.css" />
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/img/apple-touch-icon.png" />
<meta name="theme-color" content="#0a0c0e" />
<meta property="og:site_name" content="ARWIN REVIEWS" />
<meta property="og:locale" content="en_PH" />
<script async src="https://www.googletagmanager.com/gtag/js?id=""" + GA_ID + """"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','""" + GA_ID + """');</script>
<script>(function(){var B="https://abacus.jasoncameron.dev/hit/arwinreviews-com/";function d(){var x=new Date();return x.getUTCFullYear()+"-"+String(x.getUTCMonth()+1).padStart(2,"0")+"-"+String(x.getUTCDate()).padStart(2,"0")}function p(k){try{fetch(B+k,{mode:"cors",keepalive:true})}catch(e){}}var t=d();try{if(localStorage.getItem("arv_seen")!==t){localStorage.setItem("arv_seen",t);p("u-"+t)}}catch(e){}p("v-"+t);p("r-"+t)})();</script>
<script defer src="/region.js"></script>"""

TOP = """<header class="top"><div class="inner">
<a class="brand" href="/">ARWIN <b>REVIEWS</b></a>
<nav><a href="/">Home</a><a href="/r/">All reviews</a><a href="/lists/">Ranked lists</a><a href="/press.html">Press</a><a href="/work.html">Work with Arwin</a></nav>
</div></header>"""

PERSON = {"@type": "Person", "@id": SITE + "/#arwin", "name": CRITIC,
          "url": SITE + "/", "jobTitle": "Film Critic", "nationality": "Filipino",
          "sameAs": [LETTERBOXD, INSTAGRAM]}
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "ARWIN REVIEWS", "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/img/favicon-192.png", "width": 192, "height": 192},
       "sameAs": [LETTERBOXD, INSTAGRAM]}


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
SHOP = None
CRED = ""

def config_block(key):
    src = open(os.path.join(ROOT, "site_config.js"), encoding="utf8").read()
    start = src.index(key + ":")
    return src[start:src.index("\n  },", start)]

def shop_rail():
    """Own it rail config. Returns None unless enabled with at least one real
    affiliate id, so a plain non earning search link never ships."""
    try:
        b = config_block("shopRail")
        if not re.search(r"enabled:\s*true", b):
            return None
        out = []
        for shop, label in (("shopee", "Shopee"), ("lazada", "Lazada")):
            m = re.search(shop + r':\s*\{\s*id:\s*"([^"]*)",\s*template:\s*"([^"]*)"', b)
            if m and m.group(1) and m.group(2):
                out.append((label, m.group(1), m.group(2)))
        suf = re.search(r'suffix:\s*"([^"]*)"', b)
        return {"shops": out, "suffix": suf.group(1) if suf else ""} if out else None
    except Exception:
        return None

def credentials_line():
    """Stats from data.js plus real memberships from site_config.js."""
    parts = []
    try:
        d = open(os.path.join(ROOT, "data.js"), encoding="utf8").read()
        st = json.loads(d[d.index("{"):d.rindex("}") + 1])["stats"]
        parts += [f"{st['reviews']:,} reviews", f"{st['films']:,} films logged",
                  f"{st['reviewWords']:,} words"]
    except Exception:
        pass
    try:
        parts += re.findall(r'"([^"]+)"', re.search(r"memberships:\s*\[([^\]]*)\]",
                            config_block("credentials")).group(1))
    except Exception:
        pass
    return " · ".join(html.escape(x) for x in parts)

def slots(title):
    """Ad inventory on a review page. Until 2026-09-25 these 515 pages, the only
    crawlable URLs on the site, carried no placement at all while every ad unit
    sat inside the hash routed SPA that Google cannot rank."""
    q = urllib.parse.quote_plus(title)
    out = ['<section class="slots">']
    if SHOP:
        sq = urllib.parse.quote_plus(f"{title} {SHOP['suffix']}".strip())
        for label, aid, tpl in SHOP["shops"]:
            out.append(
                f'<a class="slot" href="{html.escape(tpl.format(q=sq, id=aid))}" target="_blank" rel="sponsored noopener noreferrer">'
                f'<span class="slot-tag">Affiliate · {label}</span>'
                f'<p class="slot-title">Own {html.escape(title)}</p>'
                f'<p class="slot-body">Blu-rays, steelbooks, books and merch for this film on {label}. The desk earns a small cut at no extra cost to you.</p>'
                f'<span class="slot-cta">Search {label} &#8599;</span></a>')
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
        f'<p class="slot-title">Where to stream {html.escape(title)}</p>'
        f'<p class="slot-body">A live check of every legal streaming option for this exact film, in your country.</p>'
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

def ldjson(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def crumbs_html(items):
    parts = [f'<a href="{u.replace(SITE, "") or "/"}">{html.escape(n)}</a>' for n, u in items[:-1]]
    parts.append(html.escape(items[-1][0]))
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " › ".join(parts) + "</nav>"


def img_tag(poster, alt, w, h, eager=False):
    if not poster: return ""
    full = poster_url(poster)
    th = thumb_url(poster)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    img = f'<img src="{html.escape(full)}" alt="{html.escape(alt)}" width="{w}" height="{h}" {load} decoding="async" />'
    if th:
        return f'<picture><source srcset="{th}" type="image/webp" />{img}</picture>'
    return img


def film_page(f, related_html, lists_html):
    title, year = f["name"], f["year"]
    latest = f["entries"][0]
    guest = latest.get("author")
    rating = latest.get("rating")
    body = (latest.get("review") or "").strip()
    summ = summary_part(body)
    rt = rating_text(rating)
    lead = f"{title} ({year}) review" if year else f"{title} review"
    desc = clip((f"Rated {rt}. " if rt else "") + summ, 156)
    page_title = lead + (f", {rt}" if rt and not guest else "") + (f" by {guest}" if guest else "")
    full_title = page_title + " · ARWIN REVIEWS"
    if len(full_title) > 65: full_title = page_title
    url = f"{SITE}/r/{f['slug']}/"
    poster = latest.get("poster") or ""
    om = f.get("omdb") or {}
    director = na(om.get("Director"))
    genres = [g.strip() for g in na(om.get("Genre")).split(",") if g.strip()]
    movie = {"@type": "Movie", "name": title}
    if year: movie["dateCreated"] = str(year)
    if poster: movie["image"] = SITE + poster_url(poster) if not poster.startswith("http") else poster
    if director: movie["director"] = [{"@type": "Person", "name": d.strip()} for d in director.split(",")]
    if genres: movie["genre"] = genres
    if na(om.get("imdbID")): movie["sameAs"] = f"https://www.imdb.com/title/{om['imdbID']}/"
    author = ({"@type": "Person", "name": guest, **({"url": latest["author_url"]} if latest.get("author_url") else {})}
              if guest else {"@id": PERSON["@id"]})
    review = {"@type": "Review", "@id": url + "#review", "itemReviewed": movie, "author": author,
              "publisher": {"@id": ORG["@id"]}, "url": url, "inLanguage": "en",
              "reviewBody": clip(summ, 700)}
    if rating:
        review["reviewRating"] = {"@type": "Rating", "ratingValue": rating, "bestRating": 5, "worstRating": 0.5}
    if latest.get("watched"): review["datePublished"] = latest["watched"]
    if f["modified"]: review["dateModified"] = f["modified"]
    trail = [("Home", SITE + "/"), ("Reviews", SITE + "/r/"), (f"{title} ({year})" if year else title, url)]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": url, "url": url, "name": page_title, "isPartOf": {"@id": SITE + "/#website"},
         "breadcrumb": {"@id": url + "#crumbs"}, "primaryImageOfPage": movie.get("image")},
        {**crumbs_ld(trail), "@id": url + "#crumbs"}, review, PERSON, ORG]}
    robots = "noindex, follow" if f["thin"] else "index, follow, max-image-preview:large, max-snippet:-1"
    byline = (f'Guest review by <a href="{html.escape(latest["author_url"])}" rel="noopener" target="_blank">{html.escape(guest)}</a>'
              if guest and latest.get("author_url") else f"Guest review by {html.escape(guest)}" if guest
              else f'Reviewed by <a href="{LETTERBOXD}" rel="me noopener" target="_blank">{CRITIC}</a>')
    facts = " · ".join(x for x in [", ".join(genres[:3]), f"Directed by {director}" if director else "",
                                     na(om.get("Runtime"))] if x)
    earlier = ""
    for e in f["entries"][1:]:
        eb = (e.get("review") or "").strip()
        if not eb: continue
        earlier += (f'<section class="earlier"><h2>Earlier take, {html.escape(e.get("watched") or "")}'
                    f'{" · " + stars(e.get("rating")) if e.get("rating") else ""}</h2>'
                    f'<div class="review">{html.escape(eb)}</div></section>')
    og_img = (SITE + poster_url(poster)) if poster and not poster.startswith("http") else poster
    return f"""<!doctype html><html lang="en"><head>
<title>{html.escape(full_title)}</title>
{HEAD}
<meta name="description" content="{html.escape(desc)}" />
<meta name="robots" content="{robots}" />
<link rel="canonical" href="{url}" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{html.escape(page_title)}" />
<meta property="og:description" content="{html.escape(desc)}" />
<meta property="og:url" content="{url}" />
{f'<meta property="og:image" content="{html.escape(og_img)}" /><meta property="og:image:alt" content="{html.escape(title)} poster" /><meta name="twitter:image" content="{html.escape(og_img)}" />' if og_img else ''}
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{html.escape(page_title)}" />
<meta name="twitter:description" content="{html.escape(desc)}" />
{f'<meta property="article:published_time" content="{latest["watched"]}" />' if latest.get("watched") else ''}
{ldjson(graph)}
</head><body>
{TOP}
<div class="wrap">
{crumbs_html(trail)}
<article>
<div class="hero">
{img_tag(poster, f"{title} ({year}) poster", 150, 225, eager=True)}
<div>
<h1>{html.escape(title)} <span class="yr">({year})</span> review</h1>
<div class="rating" aria-label="{html.escape(rt.replace('/5', ' out of 5') + ' stars') if rt else ''}">{stars(rating)}</div>
{f'<div class="verdict">Rated {rt}</div>' if rt else ''}
{'<span class="guest">Guest review</span>' if guest else ''}
<div class="meta">{byline}{f" · {html.escape(latest['watched'])}" if latest.get('watched') else ""}</div>
{f'<div class="facts">{html.escape(facts)}</div>' if facts else ''}
{'' if guest or not CRED else f'<div class="cred">{CRED}</div>'}
</div>
</div>
{'<div class="spoiler">This review contains spoilers.</div>' if latest.get("spoiler") else ''}
<div class="review">{html.escape(body)}</div>
{earlier}
</article>
{lists_html}
{related_html}
{slots(title)}
<footer>
<p>Part of <a href="/">ARWIN REVIEWS</a>, a Philippine film archive on global cinema.
{N_REVIEWS} reviews and counting. <a href="/r/">Browse them all</a> or see the <a href="/lists/">ranked lists</a>.</p>
<p>Follow along on <a href="{LETTERBOXD}" rel="me noopener" target="_blank">Letterboxd</a> and <a href="{INSTAGRAM}" rel="me noopener" target="_blank">Instagram</a>.</p>
<p>Distributors and PR teams, <a href="/press.html">invite me to a press screening</a>. Cinemas, the homepage slot is <a href="/work.html">open and priced</a>.</p>
<p>Want your own verdict here? <a href="/write.html">Write a guest review</a>.</p>
</footer>
</div></body></html>"""


def redirect_stub(to_slug):
    u = f"{SITE}/r/{to_slug}/"
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8" /><title>Moved</title>'
            f'<link rel="canonical" href="{u}" /><meta name="robots" content="noindex, follow" />'
            f'<meta http-equiv="refresh" content="0; url=/r/{to_slug}/" /></head>'
            f'<body><p>This review moved to <a href="/r/{to_slug}/">/r/{to_slug}/</a>.</p></body></html>')


def li_link(f):
    r = f["entries"][0].get("rating")
    return (f'<li><a href="/r/{f["slug"]}/">{html.escape(f["name"])}</a>'
            f'<span>{f["year"]} {stars(r)}</span></li>')


def related_block(f, by_dir, by_year, by_genre):
    used = {f["slug"]}
    groups = []
    om = f.get("omdb") or {}
    for d in [x.strip() for x in na(om.get("Director")).split(",") if x.strip()][:1]:
        pool = [x for x in by_dir.get(d, []) if x["slug"] not in used and not x["thin"]][:5]
        if pool:
            used.update(x["slug"] for x in pool)
            groups.append((f"More {d} films I reviewed", pool))
    g = [x.strip() for x in na(om.get("Genre")).split(",") if x.strip()]
    if g:
        r0 = f["entries"][0].get("rating") or 0
        pool = sorted([x for x in by_genre.get(g[0], []) if x["slug"] not in used and not x["thin"]],
                      key=lambda x: (abs((x["entries"][0].get("rating") or 0) - r0), -(int(x["year"] or 0))))[:5]
        if pool:
            used.update(x["slug"] for x in pool)
            groups.append((f"More {g[0].lower()} reviews", pool))
    pool = sorted([x for x in by_year.get(f["year"], []) if x["slug"] not in used and not x["thin"]],
                  key=lambda x: -(x["entries"][0].get("rating") or 0))[:5]
    if pool:
        groups.append((f"Other {f['year']} films I reviewed", pool))
    if not groups: return ""
    out = ['<section class="related"><h2>Keep reading</h2>']
    for h, pool in groups:
        out.append(f"<h3>{html.escape(h)}</h3><ul>" + "".join(li_link(x) for x in pool) + "</ul>")
    out.append("</section>")
    return "\n".join(out)


def lists_block(f, film_lists):
    ls = film_lists.get((f["name"], f["year"]), [])[:6]
    if not ls: return ""
    items = "".join(
        f'<li><a href="/lists/{l["seo_slug"]}/">{html.escape(l["seo_h1"])}</a><span>#{rank} of {len(l["films"])}</span></li>'
        for l, rank in ls)
    return f'<section class="inlists"><h2>Where it ranks</h2><ul>{items}</ul></section>'


DECADE = re.compile(r"^(\d{4})s$")


PEOPLE = ("Actors", "Auteurs", "Cinematographers", "Studios")


def plural_subject(l, subj):
    if l["cat"] in PEOPLE: return False
    return bool(re.search(r"(Films|Movies|Dramas|Comedies|Thrillers|Sagas|Westerns|Musicals|Biopics|Sequels|s)$", subj))


def list_seo(l):
    t = html.unescape(l["title"]).strip()
    head, _, tail = t.partition(":")
    head, tail = head.strip(), tail.strip()
    if re.fullmatch(r"Ranked", head, re.I):
        y = tail
        if re.fullmatch(r"(19|20)\d\d", y):
            return f"best-movies-of-{y}-ranked", f"Best Movies of {y}, Ranked", "", "year"
        m = DECADE.match(y)
        if m:
            return f"best-movies-of-the-{y}-ranked", f"Best Movies of the {y}, Ranked", "", "year"
        return None
    m = re.match(r"^(?:My|Arwin['’]s)\s+(.+?)\s+(?:Ranking|Top List)$", head, re.I)
    if m:
        subj = m.group(1)
        h1 = f"{subj}, Ranked" if plural_subject(l, subj) else f"{subj} Movies, Ranked"
        return slugify(h1.replace(",", "")), h1, tail, "subject"
    m = re.match(r"^(.+?)\s+Ranked$", head, re.I)
    if m:
        subj = m.group(1)
        h1 = f"{subj}, Ranked" if plural_subject(l, subj) else f"{subj} Movies, Ranked"
        return slugify(h1.replace(",", "")), h1, tail, "subject"
    return slugify(t)[:60].strip("-"), t, "", "theme"


def list_page(l, film_index, film_ratings, reviews_by_key):
    url = f"{SITE}/lists/{l['seo_slug']}/"
    h1 = l["seo_h1"]
    n = len(l["films"])
    title = f"{h1} ({n} films) · ARWIN REVIEWS"
    if len(title) > 65: title = f"{h1} ({n} films)"
    blurb = html.unescape(l.get("blurb") or "").strip()
    top = ", ".join(x["n"] for x in l["films"][:3])
    desc = clip(f"{n} films ranked by Filipino critic {CRITIC}. Top picks: {top}. " + blurb, 156)
    rows, items = [], []
    for i, x in enumerate(l["films"], 1):
        key = (x["n"], x.get("y"))
        f = reviews_by_key.get(key)
        r = film_ratings.get(key)
        poster = (film_index.get(key) or {}).get("poster") or ""
        link = f"/r/{f['slug']}/" if f else ""
        snippet = first_sentence(summary_part(f["entries"][0].get("review") or "")) if f else ""
        name = html.escape(x["n"])
        tl = f'<a href="{link}">{name}</a>' if link else name
        rows.append(f'<li><span class="n">{i}</span>{img_tag(poster, x["n"] + " poster", 60, 90)}'
                    f'<div><div class="t">{tl} <span class="yr">({x.get("y") or ""})</span></div>'
                    f'{f"<div class=s>{stars(r)}</div>" if r else ""}'
                    f'{f"<p>{html.escape(snippet)}</p>" if snippet else ""}</div></li>')
        it = {"@type": "ListItem", "position": i}
        if link:
            it["url"] = SITE + link
        else:
            it["item"] = {"@type": "Movie", "name": x["n"], **({"dateCreated": str(x["y"])} if x.get("y") else {})}
        items.append(it)
    trail = [("Home", SITE + "/"), ("Ranked lists", SITE + "/lists/"), (h1, url)]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url, "url": url, "name": h1, "description": desc,
         "author": {"@id": PERSON["@id"]}, "breadcrumb": {"@id": url + "#crumbs"},
         "mainEntity": {"@id": url + "#list"}},
        {**crumbs_ld(trail), "@id": url + "#crumbs"},
        {"@type": "ItemList", "@id": url + "#list", "name": h1, "itemListOrder": "https://schema.org/ItemListOrderDescending",
         "numberOfItems": n, "itemListElement": items},
        PERSON]}
    robots = "index, follow, max-image-preview:large" if l["seo_index"] else "noindex, follow"
    return f"""<!doctype html><html lang="en"><head>
<title>{html.escape(title)}</title>
{HEAD}
<meta name="description" content="{html.escape(desc)}" />
<meta name="robots" content="{robots}" />
<link rel="canonical" href="{url}" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{html.escape(h1)}" />
<meta property="og:description" content="{html.escape(desc)}" />
<meta property="og:url" content="{url}" />
<meta property="og:image" content="{SITE}/img/og-card.png" />
<meta name="twitter:card" content="summary_large_image" />
{ldjson(graph)}
</head><body>
{TOP}
<div class="wrap">
{crumbs_html(trail)}
<h1>{html.escape(h1)}</h1>
{f'<p class="tagline">{html.escape(l["seo_tag"])}</p>' if l.get("seo_tag") else ''}
<p class="meta">{n} films, ranked on my own star ratings by {CRITIC}. Updated {l["seo_mod"]}.</p>
{f'<p>{html.escape(blurb)}</p>' if blurb else ''}
<ol class="ranked">{"".join(rows)}</ol>
<footer>
<p>More rankings in the <a href="/lists/">lists hub</a>. Every verdict lives in <a href="/r/">all reviews</a>.</p>
<p>Follow along on <a href="{LETTERBOXD}" rel="me noopener" target="_blank">Letterboxd</a> and <a href="{INSTAGRAM}" rel="me noopener" target="_blank">Instagram</a>.</p>
</footer>
</div></body></html>"""


def lists_hub(pub):
    order = ["year", "subject", "theme"]
    names = {"year": "Best movies by year", "subject": "Directors, actors, studios and genres", "theme": "Moods and themes"}
    out = []
    for k in order:
        ls = [l for l in pub if l["seo_kind"] == k and l["seo_index"]]
        if k == "year":
            ls.sort(key=lambda l: l["seo_h1"], reverse=True)
        else:
            ls.sort(key=lambda l: -len(l["films"]))
        if not ls: continue
        rows = "".join(f'<a href="/lists/{l["seo_slug"]}/">{html.escape(l["seo_h1"])} <span>{len(l["films"])} films</span></a>' for l in ls)
        out.append(f'<section class="listgrp"><h2>{names[k]}</h2><div class="grid">{rows}</div></section>')
    n = sum(1 for l in pub if l["seo_index"])
    return f"""<!doctype html><html lang="en"><head>
<title>Ranked movie lists · ARWIN REVIEWS</title>
{HEAD}
<meta name="description" content="{n} ranked movie lists by Filipino film critic {CRITIC}: best movies of every year, directors and actors ranked from best to worst, and themed picks." />
<link rel="canonical" href="{SITE}/lists/" />
{ldjson({"@context": "https://schema.org", "@graph": [{"@type": "CollectionPage", "@id": SITE + "/lists/", "url": SITE + "/lists/", "name": "Ranked movie lists", "author": {"@id": PERSON["@id"]}}, crumbs_ld([("Home", SITE + "/"), ("Ranked lists", SITE + "/lists/")]), PERSON]})}
</head><body>
{TOP}
<div class="wrap">
<h1>Ranked movie lists</h1>
<p class="meta">{n} lists, every one ranked on my own star ratings.</p>
{"".join(out)}
</div></body></html>"""


def hub(films):
    rows = "\n".join(
        f'<a href="/r/{f["slug"]}/">{html.escape(f["name"])} <span>{f["year"]} {stars(f["entries"][0].get("rating"))}'
        f'{" · guest review by " + html.escape(f["entries"][0]["author"]) if f["entries"][0].get("author") else ""}</span></a>'
        for f in films)
    words = sum(len((e.get("review") or "").split()) for f in films for e in f["entries"])
    latest = sorted(films, key=lambda f: f["modified"] or "", reverse=True)[:12]
    lt = "".join(li_link(f) for f in latest)
    return f"""<!doctype html><html lang="en"><head>
<title>All film reviews · ARWIN REVIEWS</title>
{HEAD}
<meta name="description" content="Every film review by Filipino critic {CRITIC}. {len(films)} films reviewed, {words:,} words, from opening week releases to classics." />
<link rel="canonical" href="{SITE}/r/" />
{ldjson({"@context": "https://schema.org", "@graph": [{"@type": "CollectionPage", "@id": SITE + "/r/", "url": SITE + "/r/", "name": "All film reviews", "author": {"@id": PERSON["@id"]}}, crumbs_ld([("Home", SITE + "/"), ("Reviews", SITE + "/r/")]), PERSON]})}
</head><body>
{TOP}
<div class="wrap">
<h1>All film reviews</h1>
<p class="meta">{len(films)} films reviewed, {words:,} words. See also the <a href="/lists/">ranked lists</a>.</p>
<section class="related"><h2>Latest reviews</h2><ul>{lt}</ul></section>
<h2 style="font-family:var(--serif);font-size:24px;margin:34px 0 0">A to Z</h2>
<div class="grid">{rows}</div>
</div></body></html>"""


def homepage_block(films, pub):
    latest = sorted(films, key=lambda f: f["modified"] or "", reverse=True)[:12]
    years = sorted([l for l in pub if l["seo_kind"] == "year" and l["seo_index"]], key=lambda l: l["seo_h1"], reverse=True)[:8]
    a = "".join(f'<li><a href="/r/{f["slug"]}/">{html.escape(f["name"])} ({f["year"]}) review</a></li>' for f in latest)
    b = "".join(f'<li><a href="/lists/{l["seo_slug"]}/">{html.escape(l["seo_h1"])}</a></li>' for l in years)
    return (f'{SEO_START}\n<nav class="seo-static" aria-label="Latest reviews and rankings" '
            f'style="max-width:1100px;margin:40px auto;padding:0 16px;font-size:14px;line-height:1.8">'
            f'<h2 style="font-size:16px">Latest reviews</h2><ul style="columns:2;padding-left:18px">{a}</ul>'
            f'<h2 style="font-size:16px">Best movies by year</h2><ul style="columns:2;padding-left:18px">{b}</ul>'
            f'<p><a href="/r/">All reviews</a> · <a href="/lists/">All ranked lists</a></p></nav>\n{SEO_END}')


def patch_homepage(block):
    p = os.path.join(ROOT, "index.html")
    s = open(p, encoding="utf8").read()
    if SEO_START not in s or SEO_END not in s:
        print("homepage: SEO markers missing, static block skipped")
        return
    s = re.sub(re.escape(SEO_START) + r".*?" + re.escape(SEO_END), lambda m: block, s, flags=re.S)
    open(p, "w", encoding="utf8").write(s)
    print("homepage: static latest reviews block refreshed")


def indexnow(urls):
    if not urls: return
    body = json.dumps({"host": "arwinreviews.com", "key": INDEXNOW_KEY,
                       "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt", "urlList": urls[:10000]}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"indexnow: {r.status} for {len(urls)} urls")
    except Exception as e:
        print(f"indexnow: skipped ({str(e)[:80]})")


N_REVIEWS = 0


def main():
    global LEAD, SHOP, CRED, HEAD, N_REVIEWS
    LEAD = affiliate_lead()
    SHOP = shop_rail()
    CRED = credentials_line()
    ad = adsense_tag()
    if ad: HEAD = HEAD + "\n" + ad
    print("adsense:", "ON" if ad else "off")
    data = load_data()
    omdb = load_omdb()
    reviews = [r for r in load_js_array("reviews.js") if (r.get("review") or "").strip()]
    N_REVIEWS = len(reviews)

    films, order, retired = {}, [], {}
    seen = {}
    for r in reviews:
        base = slugify(r["name"], r.get("year") or "")
        seen[base] = seen.get(base, 0) + 1
        if seen[base] > 1:
            retired[f"{base}-{seen[base]}"] = base
        if base not in films:
            films[base] = {"slug": base, "name": r["name"], "year": r.get("year") or "", "entries": []}
            order.append(base)
        films[base]["entries"].append(r)
    for f in films.values():
        f["entries"].sort(key=lambda e: e.get("watched") or "", reverse=True)
        f["modified"] = f["entries"][0].get("watched") or ""
        f["omdb"] = omdb_for(omdb, f["name"], f["year"])
        f["thin"] = sum(len((e.get("review") or "").split()) for e in f["entries"]) < THIN_WORDS

    gpath = os.path.join(ROOT, "guest_reviews.json")
    guests = json.load(open(gpath, encoding="utf8")) if os.path.exists(gpath) else []
    for g in guests:
        if not (g.get("author") and (g.get("review") or "").strip()): continue
        s = slugify(g["name"], g.get("year") or "") + "-by-" + slugify(g["author"], "")
        films[s] = {"slug": s, "name": g["name"], "year": g.get("year") or "", "entries": [g],
                    "modified": g.get("watched") or "", "omdb": omdb_for(omdb, g["name"], g.get("year") or ""),
                    "thin": len(g["review"].split()) < THIN_WORDS}

    allf = list(films.values())
    by_dir, by_year, by_genre = {}, {}, {}
    for f in allf:
        if f["entries"][0].get("author"): continue
        by_year.setdefault(f["year"], []).append(f)
        om = f["omdb"] or {}
        for d in [x.strip() for x in na(om.get("Director")).split(",") if x.strip()]:
            by_dir.setdefault(d, []).append(f)
        for g in [x.strip() for x in na(om.get("Genre")).split(",") if x.strip()][:1]:
            by_genre.setdefault(g, []).append(f)
    for v in by_dir.values():
        v.sort(key=lambda x: -(x["entries"][0].get("rating") or 0))

    reviews_by_key = {(f["name"], f["year"]): f for f in allf if not f["entries"][0].get("author")}
    film_index = {(x["name"], x["year"]): x for x in data.get("films", [])}
    film_ratings = {k: v.get("rating") for k, v in film_index.items()}

    pub, used_slugs = [], set()
    for l in data.get("lists", []):
        if LIST_SKIP.search(l.get("title", "")): continue
        if len(l.get("films", [])) < LIST_MIN_PAGE: continue
        seo = list_seo(l)
        if not seo: continue
        slug, h1, tag, kind = seo
        if not slug: continue
        if slug in used_slugs:
            prev = next(x for x in pub if x["seo_slug"] == slug)
            if len(l["films"]) <= len(prev["films"]): continue
            pub.remove(prev)
        used_slugs.add(slug)
        mods = [film_index.get((x["n"], x.get("y")), {}).get("watched") or "" for x in l["films"]]
        pub.append({**l, "seo_slug": slug, "seo_h1": h1, "seo_tag": tag, "seo_kind": kind,
                    "seo_mod": max(mods) if any(mods) else TODAY,
                    "seo_index": kind == "year" or len(l["films"]) >= LIST_MIN_INDEX})

    film_lists = {}
    for l in pub:
        if not l["seo_index"]: continue
        for i, x in enumerate(l["films"], 1):
            film_lists.setdefault((x["n"], x.get("y")), []).append((l, i))
    for v in film_lists.values():
        v.sort(key=lambda t: (t[0]["seo_kind"] != "year", t[1]))

    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "review.css"), "w", encoding="utf8").write(CSS)
    for f in allf:
        d = os.path.join(OUT, f["slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf8").write(
            film_page(f, related_block(f, by_dir, by_year, by_genre), lists_block(f, film_lists)))
    for old, new in retired.items():
        if old in films: continue
        d = os.path.join(OUT, old); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf8").write(redirect_stub(new))
    allf.sort(key=lambda f: f["name"].lower())
    open(os.path.join(OUT, "index.html"), "w", encoding="utf8").write(hub(allf))

    if os.path.isdir(LOUT): shutil.rmtree(LOUT)
    os.makedirs(LOUT, exist_ok=True)
    for l in pub:
        d = os.path.join(LOUT, l["seo_slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf8").write(
            list_page(l, film_index, film_ratings, reviews_by_key))
    open(os.path.join(LOUT, "index.html"), "w", encoding="utf8").write(lists_hub(pub))

    patch_homepage(homepage_block(allf, pub))

    newest = max((f["modified"] for f in allf if f["modified"]), default=TODAY)
    urls = [(f"{SITE}/", newest), (f"{SITE}/r/", newest), (f"{SITE}/lists/", newest)]
    for p in ("work.html", "press.html", "write.html", "contact.html", "moviemode.html"):
        fp = os.path.join(ROOT, p)
        if os.path.exists(fp):
            urls.append((f"{SITE}/{p}", datetime.date.fromtimestamp(os.path.getmtime(fp)).isoformat()))
    urls += [(f"{SITE}/r/{f['slug']}/", f["modified"] or newest) for f in allf if not f["thin"]]
    urls += [(f"{SITE}/lists/{l['seo_slug']}/", l["seo_mod"]) for l in pub if l["seo_index"]]
    body = "\n".join(f"  <url><loc>{u}</loc><lastmod>{m}</lastmod></url>" for u, m in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")
    thin = sum(1 for f in allf if f["thin"])
    print(f"wrote {len(allf)} film pages ({thin} thin, noindex), {len(retired)} redirect stubs, "
          f"{len(pub)} list pages ({sum(1 for l in pub if l['seo_index'])} indexable), sitemap {len(urls)} urls")
    if "--indexnow" in sys.argv:
        recent = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
        indexnow([u for u, m in urls if m >= recent])


if __name__ == "__main__":
    main()
