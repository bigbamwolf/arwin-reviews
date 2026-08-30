#!/usr/bin/env python3
"""ARWIN REVIEWS auto-sync. Pulls new activity and folds it in. No manual step.

Reads the public RSS feed and merges any NEW films, reviews, AND lists into
data.js / reviews.js. The 1,343 film base and the 139 list base stay put; new
items are added on top, stats refresh, new posters download, date stamps.

New films and reviews come through complete. New lists come through as cards
(title, blurb, category) the moment they are published, because list pages are
React rendered and their films are not in the static HTML. The full ranking and
cover for a new list backfill on the next full export rebuild (build_data.py).

Runs on a schedule via launchd or a GitHub Action, so the site stays current
without anyone exporting anything. Source is the RSS feed, backend plumbing only.
"""
import os, re, json, html, urllib.request, xml.etree.ElementTree as ET, datetime

SITE = os.path.dirname(os.path.abspath(__file__))
HANDLE = "bigbamwolf"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
NS = {"letterboxd": "https://letterboxd.com", "tmdb": "https://themoviedb.org"}


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://" + "letterboxd.com/"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read() if binary else r.read().decode("utf-8", "ignore")


def load_js(name, var):
    t = open(os.path.join(SITE, name), encoding="utf-8").read()
    return json.loads(t[t.index("=") + 1: t.rindex(";")].strip())


def write_js(name, var, obj):
    with open(os.path.join(SITE, name), "w", encoding="utf-8") as f:
        f.write("window.%s = %s;" % (var, json.dumps(obj, ensure_ascii=False, separators=(",", ":"))))


def slug(n, y):
    return re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-") + "-" + str(y or "na") + ".jpg"


def categorize(s, title):
    s = s.lower()
    CIN = ["roger-deakins", "hoyte-van-hoytema", "greig-fraser", "claudio-miranda",
           "linus-sandgren", "wally-pfister", "robert-richardson"]
    ACT = ["leonardo-dicaprio", "tom-cruise"]
    if any(x in s for x in CIN): return "Cinematographers"
    if any(x in s for x in ACT): return "Actors"
    # Catch ALL actor rankings before they leak into Moods & Themes via the
    # generic "<first>-<last>-ranked-..." pattern. Studios get matched later
    # by the STUDIO list, so "focus-features-ranked-..." still lands correctly.
    NON_PERSON_PREFIX = ("focus-features-", "universal-", "columbia-", "paramount-",
                          "warner-", "sony-", "disney-", "pixar-", "marvel-", "a24-",
                          "lionsgate-", "blumhouse-", "amblin-", "where-war-",
                          "asian-cinema-", "japanese-cinema-")
    if "-ranked-" in s and not s.startswith(NON_PERSON_PREFIX):
        if re.match(r"^[a-z]+-[a-z]+(-[a-z]+)?-ranked-", s):
            return "Actors"
    if any(x in s for x in ["james-bond", "mission-impossible"]): return "Genres & Sagas"
    if s.startswith("my-") and s.endswith("-ranking"): return "Auteurs"
    if re.search(r"ranked-(19|20)\d", s) or s.startswith("ranked-1") or s.startswith("ranked-2"):
        return "By Year"
    STUDIO = ["marvel", "a24", "disney", "dreamworks", "pixar", "blumhouse", "amblin", "lionsgate",
              "new-line", "relativity", "skydance", "summit", "tsg", "village-roadshow",
              "20th-century-fox", "legendary", "universal", "columbia", "paramount", "warner",
              "focus-features", "sony", "mgm", "united-artists", "searchlight"]
    if any(x in s for x in STUDIO): return "Studios"
    GENRE = ["action", "sci-fi", "comedy", "horror", "animation", "star-wars", "where-war",
             "james-bond", "mission-impossible"]
    if any(x in s for x in GENRE): return "Genres & Sagas"
    WORLD = ["asian-cinema", "japanese-cinema", "k-cinema", "pinoy-cinema", "subtitles"]
    if any(x in s for x in WORLD): return "World Cinema"
    return "Moods & Themes"


def clean_review(desc):
    # drop the poster image paragraph, any images and links
    d = re.sub(r"<p>\s*<img[^>]*>\s*</p>", "", desc, flags=re.I)
    d = re.sub(r"<img[^>]*>", "", d, flags=re.I)
    d = re.sub(r"</?a\b[^>]*>", "", d, flags=re.I)
    # block tags become plain-text paragraph breaks, then strip EVERY remaining tag
    d = re.sub(r"</(p|blockquote|div)>", "\n\n", d, flags=re.I)
    d = re.sub(r"<br\s*/?>", "\n", d, flags=re.I)
    d = re.sub(r"<[^>]+>", "", d)
    d = html.unescape(d)
    d = re.sub(r"\n+#[\w#\s]+$", "", d)
    d = re.sub(r"[ \t]+", " ", d)
    d = re.sub(r"\n{3,}", "\n\n", d)
    return d.strip()


LIST_URL = "https://" + "letterboxd.com/%s/list/%s/"


def fetch_list_full(slug, rss_desc, pm):
    """Full films + cover for a list. List page has the films+years, RSS desc is the fallback."""
    films, cover = [], None
    try:
        h = get(LIST_URL % (HANDLE, slug))
        slugs = re.findall(r'data-item-slug="([^"]+)"', h)
        names = re.findall(r'data-item-name="([^"]+)"', h)
        for i in range(min(len(slugs), len(names))):
            nm = html.unescape(names[i])
            ym = re.search(r"\((\d{4})\)\s*$", nm)
            films.append({"n": re.sub(r"\s*\(\d{4}\)\s*$", "", nm), "y": int(ym.group(1)) if ym else None})
        og = re.search(r'og:image" content="([^"]+)', h)
        if og and "film-poster" in og.group(1):
            cover = og.group(1)
    except Exception:
        pass
    if not films:  # fallback: ordered links in the RSS description
        for s, nm in re.findall(r'/film/([^/"]+)/">([^<]+)</a>', rss_desc):
            films.append({"n": html.unescape(nm), "y": None})
    for f in films:  # prefer a locally mapped poster as the cover, matches the site
        p = pm.get("%s|%s" % (f["n"], f["y"]))
        if p:
            cover = p; break
    return films, cover


def main():
    LB = load_js("data.js", "LB")
    LBR = load_js("reviews.js", "LBR")
    pm_path = os.path.join(SITE, "posters_map.json")
    pm = {}
    if os.path.isfile(pm_path):
        try:
            pm = json.load(open(pm_path))
        except Exception:
            pm = {}

    root = ET.fromstring(get("https://" + "letterboxd.com/%s/rss/" % HANDLE))
    film_keys = {"%s|%s" % (f["name"], f["year"]) for f in LB["films"]}
    review_keys = {"%s|%s" % (r["name"], r["year"]) for r in LBR}
    list_slugs = {l.get("slug") for l in LB["lists"]}
    new_films = new_reviews = new_posters = new_lists = drifted = 0

    for it in root.findall(".//item"):
        link = it.findtext("link") or ""

        # NEW or partial LISTS -> build full (films + cover) from the list page + RSS
        if "/list/" in link:
            m = re.search(r"/list/([^/]+)", link)
            ls = m.group(1) if m else None
            if not ls:
                continue
            existing = next((l for l in LB["lists"] if l.get("slug") == ls), None)
            # Do NOT skip a list just because it already has films and a cover.
            # A list only appears in the RSS when Boss CREATED or UPDATED it, so its
            # presence here is the change signal. Skipping on "complete" meant a list
            # he kept adding to was read once and never again: "Men Will Literally Save
            # the World Instead of Going to Therapy" sat at 364 on the site while
            # Letterboxd was already at 373. A stale count on a published card is worse
            # than no card. Re-read it and report the drift.
            desc = it.findtext("description") or ""
            lt = html.unescape(it.findtext("title") or ls.replace("-", " ").title())
            intro = re.sub(r"<ol>.*?</ol>", "", desc, flags=re.S)
            lb = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", intro)).strip()
            ym = re.search(r"((?:19|20)\d{2})", ls)
            films, cover = fetch_list_full(ls, desc, pm)
            entry = {"slug": ls, "title": lt, "cat": categorize(ls, lt), "blurb": lb[:240],
                     "tags": [], "count": len(films), "year": int(ym.group(1)) if ym else None,
                     "cover": cover, "films": films, "partial": (len(films) == 0)}
            if existing:
                was = existing.get("count", 0)
                if was and was != entry["count"]:
                    print("[DRIFT] %s  %d -> %d films" % (ls, was, entry["count"]))
                    drifted += 1
                existing.update(entry)
            else:
                LB["lists"].insert(0, entry); new_lists += 1
            continue

        ft = it.findtext("letterboxd:filmTitle", namespaces=NS)
        desc = it.findtext("description") or ""
        if not (ft and "film-poster" in desc):
            continue
        name = html.unescape(ft)
        fy = it.findtext("letterboxd:filmYear", namespaces=NS)
        year = int(fy) if fy and fy.isdigit() else None
        key = "%s|%s" % (name, year)
        rt = it.findtext("letterboxd:memberRating", namespaces=NS)
        rating = float(rt) if rt else None
        watched = it.findtext("letterboxd:watchedDate", namespaces=NS)
        rewatch = it.findtext("letterboxd:rewatch", namespaces=NS) == "Yes"
        img = re.search(r'<img src="([^"]+)"', desc)
        poster = pm.get(key)
        if img and not poster:
            try:
                fn = "img/" + slug(name, year)
                open(os.path.join(SITE, fn), "wb").write(get(img.group(1), binary=True))
                poster = fn; pm[key] = fn; new_posters += 1
            except Exception:
                poster = None

        if key not in film_keys:
            LB["films"].insert(0, {"name": name, "year": year, "rating": rating,
                                   "watched": watched, "review": False, "liked": False, "poster": poster})
            film_keys.add(key); new_films += 1
        review = clean_review(desc); plain = re.sub(r"<[^>]+>", "", review).strip()
        if plain and key not in review_keys:
            tags = [t.strip() for t in (it.findtext("letterboxd:tags", namespaces=NS) or "").split(",") if t.strip()]
            LBR.insert(0, {"name": name, "year": year, "rating": rating, "rewatch": rewatch,
                           "watched": watched, "tags": tags, "words": len(plain.split()),
                           "review": review, "poster": poster, "spoiler": plain[:40].lower().startswith("spoiler")})
            review_keys.add(key)
            for f in LB["films"]:
                if "%s|%s" % (f["name"], f["year"]) == key:
                    f["review"] = True
            new_reviews += 1

    # refresh the stats we can derive
    films = LB["films"]; rated = [f for f in films if f.get("rating") is not None]
    dist = {}
    for f in rated:
        dist[str(f["rating"])] = dist.get(str(f["rating"]), 0) + 1
    decades = {}
    for f in films:
        if f.get("year"):
            decades["%ds" % ((f["year"] // 10) * 10)] = decades.get("%ds" % ((f["year"] // 10) * 10), 0) + 1
    GEN = {"action": "Action", "sci-fi": "Sci-Fi", "comedy": "Comedy", "horror": "Horror",
           "animation": "Animation", "where-war": "War"}
    genres = {}
    # Reclassify ALL existing lists each run so category fixes propagate to old rows.
    for l in LB["lists"]:
        if l.get("slug"):
            new_cat = categorize(l["slug"], l.get("title") or "")
            if new_cat != l.get("cat"):
                l["cat"] = new_cat
    for l in LB["lists"]:
        for kk, nm in GEN.items():
            if (l.get("slug") or "").startswith(kk):
                genres[nm] = max(genres.get(nm, 0), l.get("count", 0))
    st = LB["stats"]
    st["films"] = len(films); st["rated"] = len(rated)
    st["avg"] = round(sum(f["rating"] for f in rated) / len(rated), 2) if rated else None
    st["reviews"] = len(LBR); st["reviewWords"] = sum(r["words"] for r in LBR)
    st["fiveStars"] = sum(1 for f in rated if f["rating"] == 5.0)
    st["dist"] = dist; st["decades"] = dict(sorted(decades.items()))
    st["lists"] = len(LB["lists"]); st["listCats"] = sorted({l["cat"] for l in LB["lists"]})
    st["genres"] = sorted(genres.items(), key=lambda x: -x[1])
    yr_now = str(datetime.date.today().year)
    st["thisYear"] = sum(1 for f in films if (f.get("watched") or "").startswith(yr_now))
    st["thisYearReviews"] = sum(1 for r in LBR if (r.get("watched") or "").startswith(yr_now))
    # Boss's full Year On Letterboxd block, refreshed every 6h, shown to members on arwinreviews/year
    yfilms = [f for f in films if (f.get("watched") or "").startswith(yr_now)]
    yreviews = [r for r in LBR if (r.get("watched") or "").startswith(yr_now)]
    if yfilms:
        yrated = [f for f in yfilms if f.get("rating") is not None]
        ydist = {}
        for f in yrated:
            ydist[str(f["rating"])] = ydist.get(str(f["rating"]), 0) + 1
        ydec = {}
        yrel = {}
        for f in yfilms:
            if f.get("year"):
                ydec["%ds" % ((f["year"] // 10) * 10)] = ydec.get("%ds" % ((f["year"] // 10) * 10), 0) + 1
                yrel[f["year"]] = yrel.get(f["year"], 0) + 1
        ymonth = {}
        for f in yfilms:
            m = (f.get("watched") or "")[:7]
            if m:
                ymonth[m] = ymonth.get(m, 0) + 1
        # daily streak inside this year
        ydates = sorted({f["watched"] for f in yfilms if f.get("watched")})
        ystreak = 1
        if len(ydates) > 1:
            run = best = 1
            prev = datetime.date.fromisoformat(ydates[0])
            for d in ydates[1:]:
                cur = datetime.date.fromisoformat(d)
                if (cur - prev).days == 1:
                    run += 1
                    if run > best:
                        best = run
                elif (cur - prev).days > 1:
                    run = 1
                prev = cur
            ystreak = best
        # top 10 rated highest in 2026 (then most recent if tied)
        top10 = sorted(
            [f for f in yfilms if f.get("rating") is not None],
            key=lambda f: (-(f.get("rating") or 0), -(int((f.get("watched") or "0").replace("-", "") or 0)))
        )[:10]
        # rough hours for the year using the same avgRuntime we already estimate
        yhours = None
        if st.get("avgRuntime"):
            yhours = round(len(yfilms) * st["avgRuntime"] / 60)
        st["year"] = {
            "label": yr_now,
            "films": len(yfilms),
            "rated": len(yrated),
            "reviews": len(yreviews),
            "words": sum(r.get("words", 0) for r in yreviews),
            "avg": round(sum(f["rating"] for f in yrated) / len(yrated), 2) if yrated else None,
            "fiveStars": sum(1 for f in yrated if f["rating"] == 5.0),
            "liked": sum(1 for f in yfilms if f.get("liked")),
            "hoursEst": yhours,
            "uniqueDays": len(ydates),
            "longestStreak": ystreak,
            "firstWatch": ydates[0] if ydates else None,
            "lastWatch": ydates[-1] if ydates else None,
            "dist": ydist,
            "decades": dict(sorted(ydec.items())),
            "months": dict(sorted(ymonth.items())),
            "topReleaseYear": (max(yrel.items(), key=lambda x: x[1]) if yrel else None),
            "top10": [{"name": f["name"], "year": f.get("year"), "rating": f.get("rating"), "poster": f.get("poster"), "watched": f.get("watched")} for f in top10]
        }
    st["likes"] = sum(1 for f in films if f.get("liked"))
    st["watchlist"] = len(LB.get("watchlist") or [])
    relyr = {}
    for f in films:
        if f.get("year"):
            relyr[f["year"]] = relyr.get(f["year"], 0) + 1
    if relyr:
        top = max(relyr.items(), key=lambda x: x[1])
        st["topReleaseYear"] = {"year": top[0], "count": top[1]}
    if decades:
        td = max(decades.items(), key=lambda x: x[1])
        st["topDecade"] = {"decade": td[0], "count": td[1]}
    try:
        oc = json.load(open(os.path.join(SITE, "omdb_cache.json")))
        import re as _re
        rts = []
        for v in oc.values():
            r = v.get("Runtime", "")
            if r and r != "N/A" and "min" in r:
                m = _re.findall(r"(\d+)", r)
                if m:
                    rts.append(int(m[0]))
        if rts:
            avg_rt = sum(rts) / len(rts)
            st["hoursEst"] = round(len(films) * avg_rt / 60)
            st["avgRuntime"] = round(avg_rt, 1)
    except Exception:
        pass
    dates = sorted({f["watched"] for f in films if f.get("watched")})
    if dates:
        run = best = 1
        prev = datetime.date.fromisoformat(dates[0])
        for d in dates[1:]:
            cur = datetime.date.fromisoformat(d)
            if (cur - prev).days == 1:
                run += 1
                if run > best:
                    best = run
            elif (cur - prev).days > 1:
                run = 1
            prev = cur
        st["longestStreak"] = best
        st["firstWatch"] = dates[0]
        st["lastWatch"] = dates[-1]
    joined = (LB.get("profile") or {}).get("joined")
    if joined:
        try:
            jd = datetime.date.fromisoformat(joined)
            st["daysOnLetterboxd"] = (datetime.date.today() - jd).days
        except Exception:
            pass
    prof = LB.get("profile") or {}
    if prof.get("followers") is not None:
        st["followers"] = prof["followers"]
    if prof.get("following") is not None:
        st["following"] = prof["following"]

    LB["generatedAt"] = datetime.date.today().isoformat()
    write_js("data.js", "LB", LB)
    write_js("reviews.js", "LBR", LBR)
    json.dump(pm, open(pm_path, "w"))
    # keep the predictor's archive current with every new watch and rank
    try:
        import update_predictor
        update_predictor.update(verbose=False)
    except Exception as e:
        print("predictor update skipped:", e)
    # bust the data + reviews cache + refresh SEO meta tags so search snippets
    # and social cards always quote the live counters
    try:
        ip = os.path.join(SITE, "index.html")
        idx = open(ip, encoding="utf-8").read()
        stamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        idx = re.sub(r'(data\.js\?v=)[^"]*', r"\g<1>" + stamp, idx)
        idx = re.sub(r'(reviews\.js\?v=)[^"]*', r"\g<1>" + stamp, idx)
        F = "{:,}".format(st["films"]); R = "{:,}".format(st["reviews"]); W = "{:,}".format(st["reviewWords"])
        long_phrase = "%s films logged, %s reviews, %s words" % (F, R, W)
        og_phrase = "%s films, %s reviews, %s words" % (F, R, W)
        tw_phrase = "%s films, %s reviews" % (F, R)
        idx = re.sub(r'[\d,]+ films logged, [\d,]+ reviews, [\d,]+ words', long_phrase, idx)
        idx = re.sub(r'[\d,]+ films, [\d,]+ reviews, [\d,]+ words',          og_phrase,   idx)
        idx = re.sub(r'[\d,]+ films, [\d,]+ reviews(?=\.|")',                 tw_phrase,   idx)
        idx = re.sub(r'("numberOfItems"\s*:\s*)\d+',                          r"\g<1>" + str(st["reviews"]), idx)
        open(ip, "w", encoding="utf-8").write(idx)
    except Exception:
        pass
    print("autosync: +%d films, +%d reviews, +%d lists, +%d posters. now %d films / %d reviews / %d lists."
          % (new_films, new_reviews, new_lists, new_posters, st["films"], st["reviews"], st["lists"]))

    # auto deploy to GitHub Pages when there's actually something new
    if not os.environ.get("GITHUB_ACTIONS"):
        # Local runs are followers, not writers. The GitHub Action is the single
        # deployer; two writers on main diverged and stranded 34 commits (2026-08-23).
        print("autosync: local run, deploy owned by GitHub Actions")
        return
    if (new_films + new_reviews + new_lists + new_posters) > 0:
        import subprocess
        env = dict(os.environ, GIT_AUTHOR_NAME="bigbamwolf", GIT_AUTHOR_EMAIL="arwinbagaslao@gmail.com",
                   GIT_COMMITTER_NAME="bigbamwolf", GIT_COMMITTER_EMAIL="arwinbagaslao@gmail.com")
        msg = "autosync: +%dr +%df +%dl +%dp" % (new_reviews, new_films, new_lists, new_posters)
        try:
            subprocess.run(["git", "-C", SITE, "add", "data.js", "reviews.js", "predictor.html",
                            "index.html", "img/"], check=True, env=env, timeout=30)
            r = subprocess.run(["git", "-C", SITE, "commit", "-q", "-m", msg],
                               env=env, timeout=30)
            if r.returncode == 0:
                subprocess.run(["git", "-C", SITE, "push", "-q", "origin", "main"],
                               check=True, env=env, timeout=120)
                print("autosync: deployed to GitHub Pages")
        except Exception as e:
            print("autosync: deploy skipped (%s)" % str(e)[:80])


if __name__ == "__main__":
    main()
