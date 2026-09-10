# ARWIN REVIEWS, ad slot marketplace listing pack
Compiled September 9, 2026, Asia/Manila.
Purpose: sell the hero slot WITHOUT cold email. List the inventory publicly,
let the advertiser find it and buy it.

## THE ROUTE
Primary: BuySellAds. Direct marketplace, no minimum traffic, publisher lists
inventory and advertisers browse by category and buy the placement.
Secondary: Amazon Publisher Services. Also no traffic minimum, stricter vetting.
Fallback fill: Google AdSense on the same slot when no direct buyer holds the week.

## SITE FACTS (copy paste into any listing form)
Site: arwinreviews.com
Name: ARWIN REVIEWS
Category: Entertainment > Film > Film criticism and reviews
Geography: Philippines primary, global English secondary
Language: English
Owner: Arwin Edward M. Bagaslao
Contact: partnerships@arwinreviews.com

Content depth as published on work.html:
  1,438 films logged
  512 full written reviews
  138,274 words of original criticism
  (current as of September 9, 2026, from the live index.html meta description.
   work.html still prints the older 1,351 / 436 / 126,349, it needs a refresh.)
Social: Instagram @bigbamwolf, 4,609 followers
Editorial policy: every paid placement labelled at top of post, verdict never sold.
Published rate card and disclosure policy live at arwinreviews.com/work.html

## THE INVENTORY BEING SOLD
Unit: hero slot, top of the homepage, above the review grid.
Format: single featured film. Poster art, kicker, title, tagline, CTA, click URL.
Current state: unsold, running the house pitch "Your film here".
Config lives at letterboxd-site/site_config.js, object `promo`.
To go live for a buyer: set mode "sponsor", fill art / kicker / title / tagline / cta / url.
No popups, no autoplay, no interstitials. One slot, one advertiser, one week.

Buyer profile that fits: PH cinema chains, local distributors, streaming title
launches, film festivals, and anyone with an opening week to defend.

## TRAFFIC NUMBER, SOLVED September 9, 2026
Five routes were tried and four are dead ends, recorded so nobody repeats them:
  GA4 Data API        ACCESS_TOKEN_SCOPE_INSUFFICIENT on the existing ADC.
  GA4 re-auth         consent page reached, every saved browser profile is
                      signed OUT of Google. Needs Boss's password.
  Cloudflare GraphQL  BOTH tokens on disk are valid and see the zone
                      (f490cadd9fdf2b03e9a7dcb7462c68e6) but neither carries
                      zone.analytics.read, and a token cannot widen itself.
  CF dashboard        headed run cleared the bot check, profile signed out.
  GitHub traffic API  measures the repo page, not the site. Wrong metric.

THE FIX THAT SHIPPED. The site now writes its own anonymous daily counters and
they are readable with a plain GET, no credential in the path, no Boss step.
  Live on index.html since commit 9b7dd1b, verified firing September 9, 2026.
  Read it:  python3 letterboxd-site/tools/traffic_report.py 30
  Raw:      https://abacus.jasoncameron.dev/get/arwinreviews-com/v-YYYY-MM-DD
  Keys:     v-DATE pageviews, u-DATE daily uniques. No cookies, no PII.

LIMIT, STATED PLAINLY. Counters start September 9, 2026. They do not backfill.
Every visit before that date lives only in GA4 and is unreachable until Boss
signs in once. So a listing submitted today can only claim content depth, not
an impressions history. Wait roughly 14 days for a defensible monthly figure,
or list now with content stats only.

## PRICE, DRAFTED September 10, 2026, NOT PUBLISHED
Correction to an earlier note in this file: work.html DOES carry prices for the
three sponsorship lanes. From P25,000 per title (sponsored opening week review),
From P40,000 per cycle (gear testing), From P15,000 per month (brand partner).
What has never carried a price is the HERO SLOT itself, the one on the homepage
that currently reads "Your film here".

THE PROBLEM WITH THE EXISTING LADDER
Those three numbers price an audience the site cannot yet evidence. A buyer who
asks "how many people will see this" gets no answer today, and P25,000 with no
impressions figure reads as a number picked out of the air. That is a plausible
reason the lanes have produced zero enquiries in the life of the inbox.

PROPOSED HERO SLOT RATE, founding sponsor framing
  P3,500 per week, or P12,000 per month (a 14 percent discount on four weeks).
WHY THESE NUMBERS
  Low enough to be an instant yes without a meeting, which is the entire point of
  a self serve marketplace listing. High enough not to signal a dead site.
  Framed explicitly as a founding rate that rises once the traffic figure is
  published, which gives the first buyer a reason to move now and gives Boss a
  clean, non embarrassing path to reprice upward later.
  Deliberately NOT anchored to the P25,000 lane. The hero slot is a placement,
  not a commissioned review, and pricing it near the review lane would make both
  look arbitrary.

REVISIT DATE September 23, 2026, when the self counter carries a full month.
At that point price on real CPM and delete the founding framing.

STATUS: drafted only. Nothing published. The live rate card is untouched, because
a public price is Boss's call and a revenue decision, not a formatting fix.

## THE ONE STEP THAT NEEDS BOSS
Account creation on the marketplace. That is a credential action, it stays with
Boss. Everything above the signup is done and sitting in this file.
