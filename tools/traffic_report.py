#!/usr/bin/env python3
"""Pull arwinreviews.com traffic from the self readable daily counters.

WHY THIS EXISTS
GA4 (G-ZK111NQYT1) holds the full history but cannot be READ without an
interactive Google sign in. Both Cloudflare API tokens on this machine are
valid for the zone but carry no zone.analytics.read, and a token cannot widen
its own scope. So the site writes its own anonymous daily counters and this
reads them back with a plain GET, no credential anywhere in the loop.

Counters start from the day the beacon shipped. Anything before that lives
only in GA4 and needs Boss to sign in once.

Usage: python3 tools/traffic_report.py [days]
"""
import sys, json, datetime, urllib.request

NS = "arwinreviews-com"
GET = "https://abacus.jasoncameron.dev/get/" + NS + "/"

def read(key):
    try:
        with urllib.request.urlopen(GET + key, timeout=10) as r:
            return json.load(r).get("value", 0)
    except Exception:
        return 0

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    today = datetime.datetime.now(datetime.timezone.utc).date()
    rows, tv, tu = [], 0, 0
    for i in range(days - 1, -1, -1):
        d = (today - datetime.timedelta(days=i)).isoformat()
        v, u = read("v-" + d), read("u-" + d)
        tv += v; tu += u
        rows.append((d, v, u))
    live = [r for r in rows if r[1] or r[2]]
    print("ARWIN REVIEWS traffic, last %d days (UTC)" % days)
    print("-" * 44)
    for d, v, u in (live or rows[-7:]):
        print("%s   pageviews %-7d uniques %d" % (d, v, u))
    print("-" * 44)
    print("TOTAL   pageviews %d   uniques %d" % (tv, tu))
    if not live:
        print("\nNo data yet. The beacon only counts from the day it shipped.")

if __name__ == "__main__":
    main()
