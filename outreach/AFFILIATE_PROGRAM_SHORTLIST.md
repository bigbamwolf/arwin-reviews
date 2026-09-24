# ARWIN REVIEWS, affiliate program shortlist

Researched 2026-09-24 against primary sources. Every rate that is not published is
recorded as UNKNOWN rather than estimated.

## The problem this solves

The hero slot on arwinreviews.com has run in `affiliate` mode since 2026-09-04 and
renders a card tagged AFFILIATE pointing at `https://www.justwatch.com/ph`. That URL
carries no affiliate id, no tracking parameter and no sub id, so the most valuable
placement on the site pays P0.00. Three of the four Kit cards were literal
`TODO_` placeholders and never rendered.

## Ranked shortlist

| # | Network | Fits which card | PH eligible | Traffic minimum | Self serve | Status |
|---|---|---|---|---|---|---|
| 1 | Involve Asia (Shopee PH, Lazada PH) | Home cinema, Reading | Yes, PH native | None | Yes, free | NO ACCOUNT YET |
| 2 | Amazon Associates | Reading (imported film books) | Yes | None | Yes, free | NO ACCOUNT YET |
| 3 | JustWatch Partner API | Streaming | Yes | Not published | NO, business development | NOT CONTACTED |
| 4 | PH cinema chains | Tickets | n/a | n/a | n/a | NO PROGRAM EXISTS |

## 1. Involve Asia, the strongest fit

The dominant affiliate network in the Philippines and the only route on this list that
reaches a Filipino reader's actual buying surface.

```
Cost to join ......... free
Website required ..... no, a social account or blog qualifies
Traffic minimum ...... none stated
Models ............... CPS, CPL, CPC
Merchants that matter  Shopee Philippines, Lazada Philippines
Link generation ...... Deeplink Generator inside the publisher console
```

Commission rates per merchant are NOT published outside the logged in console. Do not
quote a Shopee or Lazada rate until it is read off the campaign page.

Why it wins: the audience is Filipino. A reader who clicks a projector, a soundbar or a
film book buys it on Shopee or Lazada, not on a US storefront.

## 2. Amazon Associates, the fallback for the book shelf

```
PH publishers ........ eligible
Payout threshold ..... USD 10 direct deposit, USD 100 by check
Commission range ..... 1 to 10 percent by category
Payment lag .......... about 60 days after month end
```

Honest caveat: a PH reader buying an imported film criticism book pays international
shipping, so conversion is far worse than a local Shopee or Lazada listing. Use it only
for titles that genuinely have no local seller.

## 3. JustWatch, the category fit that is not self serve

JustWatch does run affiliate commissions through its Partner API and partners integrate
branded links into film pages. It is a business development relationship, not a signup
form. An enquiry has to go to their partner team the same way the BuySellAds enquiry did
on 2026-09-10 from `partnerships@arwinreviews.com`.

Until that lands, the current JustWatch link earns nothing and is now flagged
`payout: "none"` in `site_config.js` so it can never outrank a paying link in the hero.

## 4. Cinema tickets, dead end

No public affiliate or referral program exists for SM Cinema, Ayala Malls Cinemas,
Robinsons Movieworld or GMovies. The Tickets card is marked `network: "none"` and stays
dark until it is repurposed.

## What is already wired, 2026-09-24

* `site_config.js` affiliate items now carry `network`, `payout` and `note` fields, and
  the three placeholders name the exact program they are waiting on.
* `app.js` hero lead selection prefers a link whose `payout` is not `"none"`, falling
  back to any live link. The moment one real tracked link is pasted in, it takes the
  hero slot automatically, no code change.

## The one blocker

An Involve Asia publisher account does not exist. Creating it needs Boss's own identity
and payout details, so it is his atom. Everything downstream of it is already built.

## Traffic reality, so nothing gets oversold

```
Last 30 days   163 pageviews, 102 uniques   (tools/traffic_report.py)
```

Involve Asia imposes no traffic minimum, so this does not block the account. It does mean
first month earnings will be close to zero. The volume fix is the review page work, not
the network choice.
