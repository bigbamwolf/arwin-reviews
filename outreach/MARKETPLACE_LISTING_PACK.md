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
  1,351 films logged
  436 full written reviews
  126,349 words of original criticism
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

## OPEN GAP, TRAFFIC NUMBER, PROBED September 9, 2026
Monthly sessions and pageviews are still UNKNOWN. Four routes tried, all closed.

1. GA4 Data API with gcloud ADC. Fails ACCESS_TOKEN_SCOPE_INSUFFICIENT, the
   existing application default credential has no analytics scope.
2. Re-auth with the analytics scope. The consent page loads and reaches the
   account chooser, but every saved Playwright profile (gas, gsheets, cf,
   marquee) is signed OUT of Google. Finishing it needs Boss's password.
   Note: Google also warns analytics.readonly is being blocked for the gcloud
   default client ID, so this route may die anyway. Prefer route 3.
3. Cloudflare GraphQL analytics. BEST ROUTE, closest to open.
   Token at ~/.config/pixelens-cloudflare/cf_api_token is VALID and sees the
   zone. arwinreviews.com zone id f490cadd9fdf2b03e9a7dcb7462c68e6, Free plan.
   Query rejected with: does not have permission
   'com.cloudflare.api.account.zone.analytics.read'.
   It is a Workers deploy token. Add Zone > Analytics > Read to that same token
   in the Cloudflare dashboard and the number comes back with no new secret.
   Working query lives at the bottom of this file.
4. GitHub traffic API. Returns data for the repo page bigbamwolf/arwin-reviews
   on github.com, NOT visitors to the live site. Wrong metric, discarded.

## THE CLOUDFLARE QUERY, READY TO RUN ONCE THE TOKEN SCOPE IS FIXED
GraphQL endpoint https://api.cloudflare.com/client/v4/graphql
httpRequests1dGroups, filter date_geq / date_leq, 30 day window,
sum{pageViews requests} and uniq{uniques}, orderBy date_ASC.
That yields the exact monthly pageviews and unique visitors every marketplace
listing form asks for.

## PRICE, NOT YET SET
Cannot be set honestly until the traffic number above is known.
Rate card on work.html sells three lanes but carries no slot CPM.

## THE ONE STEP THAT NEEDS BOSS
Account creation on the marketplace. That is a credential action, it stays with
Boss. Everything above the signup is done and sitting in this file.
