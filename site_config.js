/* ARWIN REVIEWS — money + brand config.
   Boss edits this file only. No logic here, just the knobs.
   Currency placeholders are PH pesos, swap freely. Links marked TODO. */
window.LBC = {

  /* MONEY 1 — promoted film / series slot. Clearly labeled, no popups, no autoplay.
     Swap in a paid placement, or leave as the house ad-sales pitch. */
  // mode "editorial" shows a Spotlight of Arwin's own best review (looks full, never empty).
  // Switch to "sponsor" and fill the fields below once a paying studio takes the slot.
  promo: {
    /* TOP SLOT RULE, locked 2026-06-12:
       - This slot is paid cinema/studio sponsorship FIRST. Never auto-Spotlight from LBR.
       - Manual config is OK. Boss can pick any single film (own review or sponsor) as the explicit feature.
       - Default fallback if nothing manual is set: "pitch" mode showing the "Your film here" advertiser pitch.
       Modes:
         "pitch"   -> empty state, shows "Your film here" pitch to advertisers
         "sponsor" -> a single featured film fills the slot. Set art = poster URL, fill kicker/title/tagline/cta/url. */
    /* Default state is "auto" — JS picks the most recent current-year film rated 4 stars or higher.
       Flip to "sponsor" only when a real cinema or studio buys the slot, then fill the fields below. */
    mode: "affiliate",   // AFFILIATE opened on the hero slot by Boss 2026-09-04.
                         // Flip to "sponsor" the moment a cinema pays, they outrank it.
    label: "Slot open",
    kicker: "Cinemas, this is your slot",
    title: "Your film here",
    tagline: "A paid, disclosed opening week slot. A real verdict, curated on the week your film matters most.",
    cta: "Contact Arwin",
    url: "#partner",
    art: "linear-gradient(135deg,#1b1207,#3a2410 55%,#0d0905)"
  },

  /* MONEY 2 — where to watch (affiliate). {q} is the film title, URL encoded. */
  whereToWatch: { label: "Where to watch", base: "https://www.justwatch.com/ph/search?q={q}" },

  /* MONEY 3 — membership. ONE lifetime unlock, repriced 2026-09-04 by Boss.
     WHY: the backend never had recurring billing (Code.gs hits the one time
     /v2/invoices endpoint) and validateCode_ never checked expiry, so P199 had
     ALWAYS bought forever access under a "per month" label. The old four tier
     table also shipped a broken Producer tier that displayed P499 and charged
     P199, because app.js infers the tier by /annual|year/ and everything else
     falls through to monthly. A monthly price also invited a comparison with
     Netflix PH at roughly P149, which this product loses. One honest one time
     price invites no comparison at all. */
  membership: {
    note: "One payment, yours forever. GCash, Maya, GrabPay, Visa or Mastercard through Xendit. Your unlock code lands in your email the moment it clears.",
    checkout: "#support",
    tiers: [
      { key: "fan", name: "Fan", price: "Free", period: "", highlight: false,
        perks: ["Every public review", "Browse all 746 lists", "Watchlist preview",
                "One free go at the predictor",
                "One free Find Your Next Watch pick"],
        cta: "Start reading", url: "#reviews" },
      { key: "lifetime", name: "Lifetime Unlock", price: "249", period: "one time, yours forever", highlight: true,
        perks: ["What Arwin Might Think, unlimited predictions, forever",
                "Find Your Next Watch, unlimited picks plus Past You review snippets",
                "No renewals, no subscription, no expiry",
                "Every future tool on the site, included",
                "Ad free reading"],
        cta: "Unlock for P249", url: "#join" }
    ]
  },

  /* MONEY 3b — the members only weekly watchlist teaser (Boss's idea). */
  weekWatchlist: {
    heading: "This Week's Watchlist",
    sub: "What I am watching and reviewing next. Members see it first, every Monday.",
    locked: ["Opening week theatrical drop", "One festival title", "A rewatch for a new ranking",
             "A subscriber request", "One wildcard"],
    cta: "Unlock with The Crew"
  },

  /* MEMBER BENEFIT — the "What Arwin Might Think" predictor (rebuilt in-house). */
  predictor: {
    title: "What Arwin Might Think",
    badge: "",
    blurb: "Name any film. My taste model, built on every rating I have ever given, calls the stars I would land on and the reasons why. Free members get one go. The Lifetime Unlock makes it unlimited, forever.",
    file: "predictor.html",
    cta: "Open the predictor"
  },

  /* MEMBER BENEFIT — Find Your Next Watch, mood to film matcher from the 1,351 archive. */
  moviemode: {
    title: "Find Your Next Watch",
    badge: "",
    blurb: "Tell me how you feel and how you want to land. I match you to a film from the archive, with a reason, and pull what past you wrote about it when you watched. Free members get one pick. The Lifetime Unlock makes it unlimited, with a deeper rationale.",
    file: "moviemode.html",
    cta: "Open Find Your Next Watch"
  },

  /* MONEY — work with Arwin (sponsored reviews, gear testing, cinema/brand partners) */
  partner: {
    heading: "Work with me",
    sub: "A serious, high intent film audience and a reviewer who actually finishes the 124,000 words. Here is how brands plug in.",
    email: "partnerships@arwinreviews.com",
    cards: [
      { tag: "For studios and streamers", title: "Sponsored Reviews",
        body: "A disclosed, honest opening week slot. A real verdict from a critic people trust, on the week it matters most.",
        cta: "Pitch a title" },
      { tag: "For brands and manufacturers", title: "Gear Testing",
        body: "Send the projector, the soundbar, the 4K player, the headphones. I put them to work across real films and report how they perform. Your call on the titles I test them with.",
        cta: "Send your kit" },
      { tag: "For cinemas and snacks", title: "Brand Partners",
        body: "Philippine cinemas, food and drink, premium snacks. Reach a local audience that plans its week around what to watch.",
        cta: "Start a partnership" }
    ]
  },

  /* MONEY — request a review, and the annual Year in Review perk */
  requestReview: {
    tag: "Skip the queue", title: "Request a Review",
    body: "Want my take on a specific film fast? Non members jump the queue. Crew members get free votes on what gets reviewed next.",
    price: "299", cta: "Request a film", url: "#join"
  },
  yearInReview: {
    tag: "The personal one", title: "Your Year, Curated",
    body: "Not just my year in the archive. Yours. Every film you predicted, every Find Your Next Watch pick you took, every tip you sent, every review you requested. A shareable card of how you spent your film year with me. Members get the first build, every December.",
    cta: "Members get it first", url: "#join", highlight: true
  },

  /* MONEY 4 — merch. Slogans pulled from Boss's own bio and list titles.
     No product photos yet, the cards render the graphic in type. */
  merch: {
    archived: true, // ARCHIVED 2026-06-01 by Boss. Section + nav link hidden, code kept. Flip to false to bring it back.
    storeNote: "Print on demand. Ships worldwide. Designs from the reviews you already love.",
    storeUrl: "#shop", // TODO: Shopify / printful storefront
    // Realistic blank tee mockup photos (front, centered). The earlier auto-fetched
    // photos rendered broken in-card, so this is OFF and the cards use the clean
    // drawn studio tee. To enable, drop two front-facing flat-lay tee photos at the
    // paths below (shirt filling most of the frame) and restore this line.
    mockup: {},
    products: [
      { slogan: "CFO BY DAY\nCINEPHILE BY NIGHT", tag: "The flagship tee", price: "1,290",
        fg: "#f4ead2", bg: "#0c0c0d", accent: "#e7b54a" },
      { slogan: "#ARWINREVIEWS", tag: "The brand tee", price: "1,190",
        fg: "#0c0c0d", bg: "#e7b54a", accent: "#0c0c0d" },
      { slogan: "5 STAR\nCLUB", tag: "Members cap", price: "990",
        fg: "#e7b54a", bg: "#141414", accent: "#e7b54a" },
      { slogan: "I PAID TO\nBE STRESSED", tag: "Horror tee", price: "1,290",
        fg: "#f3e6e6", bg: "#1a0606", accent: "#ff3b3b" },
      { slogan: "ERROR 404\nBRAIN NOT FOUND", tag: "Sci fi tee", price: "1,290",
        fg: "#7CFFB2", bg: "#06120c", accent: "#00e054" },
      { slogan: "SUBTITLES WERE\nNEVER THE PROBLEM", tag: "World cinema tee", price: "1,290",
        fg: "#101216", bg: "#e8e2d4", accent: "#101216" }
    ]
  },

  /* NEWSLETTER — Resend Broadcasts, server-side audience id in arwin-payments Script Props */
  newsletter: {
    enabled: true,
    heading: "Get every review in your inbox",
    sub: "One email a week. The reviews, the rankings, the picks. No spam, unsubscribe anytime.",
    cta: "Subscribe"
  },

  /* MONEY 8 — affiliate rail. Opened by Boss 2026-09-04.
     This is the SEPARATE placement the 2026-06-12 rule reserved for affiliate
     products. The top hero slot stays cinema and studio only, unchanged.
     Every card renders a visible "Affiliate" tag and the block carries a
     disclosure line, because an undisclosed affiliate link is the thing that
     actually cheapens a review site.
     Set enabled:false to pull the whole rail without touching code.
     Each item needs a REAL affiliate URL before it earns anything. Items
     with a url starting "TODO" are skipped at render, so the rail never
     ships a dead link. */
  affiliates: {
    enabled: true,
    eyebrow: "Disclosed partners",
    heading: "The Kit",
    lede: "Things I actually use to watch, track, and think about films. If you buy through these, the desk earns a small cut at no extra cost to you.",
    disclosure: "Affiliate links. I only list what I would recommend without the commission. A paid placement never buys a rating.",
    items: [
      { tag: "Streaming", name: "Where to watch",
        blurb: "Every review on this site links out to a live streaming check for that exact film, PH region.",
        cta: "Find a film", url: "https://www.justwatch.com/ph" },
      { tag: "Tickets", name: "Cinema tickets",
        blurb: "Opening week is the only honest way to see some films. Book the good screen.",
        cta: "Book a screening", url: "TODO_cinema_affiliate" },
      { tag: "Reading", name: "The film shelf",
        blurb: "The criticism and craft books that shaped how the reviews on this site get written.",
        cta: "See the shelf", url: "TODO_bookstore_affiliate" },
      { tag: "Home cinema", name: "The setup",
        blurb: "Projector, sound, and seating notes from building a room worth watching in.",
        cta: "See the setup", url: "TODO_gear_affiliate" }
    ]
  },

  /* MONEY 5, 6, 7 — support, ad sales. */
  support: {
    tipLabel: "Send a tip via GCash",
    xenditLabel: "Send a tip via Xendit",
    xenditTipUrl: "#tip-xendit",
    gcash: { name: "Arwin Edward M. Bagaslao", number: "09356708680", qr: "img/gcash-qr.png" },
    paypal: "https://paypal.me/arwinbagaslao",
    sponsorEmail: "partnerships@arwinreviews.com"
  }
};
