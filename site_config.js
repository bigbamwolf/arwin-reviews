/* ARWIN REVIEWS — money + brand config.
   Boss edits this file only. No logic here, just the knobs.
   Currency placeholders are PH pesos, swap freely. Links marked TODO. */
window.LBC = {

  /* MONEY 1 — promoted film / series slot. Clearly labeled, no popups, no autoplay.
     Swap in a paid placement, or leave as the house ad-sales pitch. */
  // mode "editorial" shows a Spotlight of Arwin's own best review (looks full, never empty).
  // Switch to "sponsor" and fill the fields below once a paying studio takes the slot.
  promo: {
    mode: "editorial",
    label: "Promoted",
    kicker: "Featured this week",
    title: "Your film here",
    tagline: "A premium placement in front of a reader who has logged 1,343 films and written 124,000 words about them.",
    cta: "Talk to the desk",
    url: "#partner",
    art: "linear-gradient(135deg,#1b1207,#3a2410 55%,#0d0905)"
  },

  /* MONEY 2 — where to watch (affiliate). {q} is the film title, URL encoded. */
  whereToWatch: { label: "Where to watch", base: "https://www.justwatch.com/ph/search?q={q}" },

  /* MONEY 3 — membership. The Crew. Prices are placeholders. */
  membership: {
    note: "Cancel anytime. Founding members keep their rate for life.",
    // TODO Boss: replace YOURNAME with your Buy Me a Coffee handle once you create it.
    checkout: "https://buymeacoffee.com/YOURNAME/membership",
    tiers: [
      { name: "Fan", price: "Free", period: "", highlight: false,
        perks: ["Every public review", "Browse all 139 lists", "Watchlist preview",
                "Try the predictor, 3 films a day"],
        cta: "Start reading", url: "#reviews" },
      { name: "The Crew", price: "199", period: "per month", highlight: true,
        perks: ["This week's watchlist, what I review next",
                "VIP group chat, talk to me directly",
                "What Arwin Might Think, unlimited predictions",
                "Annual Year in Review card, yours first",
                "Full review archive, early access before public",
                "Vote on the next review and the next ranking",
                "Ad free reading", "10 percent off all merch"],
        cta: "Join the Crew", url: "#join" },
      { name: "Producer", price: "499", period: "per month", highlight: false,
        perks: ["Everything in The Crew", "Your name in the site credits",
                "Monthly live watch party, in person, Metro Manila", "Request a film for review",
                "20 percent off all merch"],
        cta: "Become a Producer", url: "#join" }
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
    badge: "Member benefit",
    blurb: "Name any film. My taste model, built on every rating I have ever given, calls the stars I would land on and the reasons why. Free members get three a day. The Crew gets it unlimited.",
    file: "predictor.html",
    cta: "Open the predictor"
  },

  /* MONEY — work with the desk (sponsored reviews, gear testing, cinema/brand partners) */
  partner: {
    heading: "Work with me",
    sub: "A serious, high intent film audience and a reviewer who actually finishes the 124,000 words. Here is how brands plug in.",
    email: "arwinbagaslao@gmail.com",
    cards: [
      { tag: "For studios and streamers", title: "Sponsored Reviews",
        body: "A disclosed, honest opening week slot. A real verdict from a desk people trust, on the week it matters most.",
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
    tag: "Every December", title: "Your Year in Review",
    body: "A shareable, personalized card of your film year, your stars, your standouts. Crew members get theirs first.",
    cta: "Members get it first", url: "#join"
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

  /* MONEY 5, 6, 7 — support, newsletter, ad sales. */
  support: {
    tipLabel: "Send a tip via GCash",
    gcash: { name: "Arwin Edward M. Bagaslao", number: "09356708680", qr: "img/gcash-qr.png" },
    newsletterAction: "#newsletter", // TODO: mailing list endpoint
    sponsorEmail: "arwinbagaslao@gmail.com"
  }
};
