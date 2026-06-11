(function () {
  "use strict";
  var LB = window.LB, LBR = window.LBR || [], LBC = window.LBC || {};
  var $ = function (s, e) { return (e || document).querySelector(s); };
  var $$ = function (s, e) { return Array.prototype.slice.call((e || document).querySelectorAll(s)); };
  var MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  var FMON = ["January","February","March","April","May","June","July","August","September","October","November","December"];

  function stars(r) { if (!r) return ""; var out = "", f = Math.floor(r); for (var i=0;i<f;i++) out+="★"; if (r%1>=0.5) out+="½"; return out; }
  function stars5(r) {
    if (!r) return '<span class="s-off">★★★★★</span>';
    var full = Math.floor(r), half = r%1>=0.5, h = "";
    for (var i=0;i<full;i++) h += '<span class="s-on">★</span>';
    if (half) h += '<span class="s-on">½</span>';
    for (var j=0;j<5-full-(half?1:0);j++) h += '<span class="s-off">★</span>';
    return h;
  }
  function fmtDate(iso, full) { if (!iso) return ""; var p = iso.split("-"); if (p.length<3) return iso; return parseInt(p[2],10)+" "+(full?FMON:MON)[parseInt(p[1],10)-1]+" "+p[0]; }
  function num(n) { return (n==null)?"":Number(n).toLocaleString("en-US"); }
  function esc(s) { return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
  function attr(s) { return (s||"").replace(/"/g,""); }
  function strip(t) { return (t||"").replace(/<[^>]*>/g," ").replace(/\s+/g," ").trim(); }
  function paras(t) { return esc(t).split(/\n\s*\n/).map(function(b){return "<p>"+b.replace(/\n/g,"<br>")+"</p>";}).join(""); }

  function countUp(el, target, dec) {
    var start = performance.now(), dur = 1500;
    function ease(t){return 1-Math.pow(1-t,3);}
    function f(now){var p=Math.min((now-start)/dur,1),v=target*ease(p);el.textContent=dec?v.toFixed(dec):Math.round(v).toLocaleString("en-US");if(p<1)requestAnimationFrame(f);else el.textContent=dec?target.toFixed(dec):Number(target).toLocaleString("en-US");}
    requestAnimationFrame(f);
  }

  var st = LB.stats, pr = LB.profile;
  var reviewByKey = {};
  LBR.forEach(function (r) { reviewByKey[r.name + "|" + r.year] = r; });

  /* HERO */
  $("#heroKicker").textContent = "Cinephile dispatch · " + (pr.location || "");
  $("#heroSub").textContent = "Theatrical releases, festival titles, and opening week reactions. " + num(st.reviewWords) + " words and counting.";
  [
    { v: st.films, l: "Films" }, { v: st.reviews, l: "Reviews" },
    { v: st.reviewWords, l: "Words Written" }, { v: st.lists, l: "Lists" }
  ].forEach(function (s) {
    var d = document.createElement("div"); d.className = "stat";
    d.innerHTML = '<span class="v">0</span><span class="l">' + s.l + "</span>";
    $("#statBand").appendChild(d); countUp($(".v", d), s.v);
  });

  /* TOP SLOT — a real sponsor if set, otherwise an editorial Spotlight of his own work */
  (function () {
    var p = LBC.promo || {}, pe = $("#promo");
    if (p.mode === "sponsor") {
      pe.href = p.url || "#";
      pe.innerHTML =
        '<div class="promo-art" style="background:' + (p.art||"#161c22") + '"><span class="promo-tag">' + esc(p.label||"Promoted") + '</span></div>' +
        '<div class="promo-body"><div class="promo-kicker">' + esc(p.kicker||"") + '</div>' +
        '<div class="promo-title">' + esc(p.title||"") + '</div>' +
        '<div class="promo-tagline">' + esc(p.tagline||"") + '</div>' +
        '<span class="promo-cta">' + esc(p.cta||"Learn more") + ' &#8599;</span></div>';
      return;
    }
    var feat = LBR.filter(function(r){return r.rating>=4.5 && r.poster && r.words>80;})[0]
            || LBR.filter(function(r){return r.poster && r.words>60;})[0];
    if (!feat) { pe.parentNode.style.display = "none"; return; }
    var ex = strip(feat.review); if (ex.length>150) ex = ex.slice(0,150).replace(/\s+\S*$/,"")+"…";
    pe.removeAttribute("href"); pe.style.cursor = "pointer";
    pe.innerHTML =
      '<div class="promo-art" style="background-image:url('+feat.poster+');background-size:cover;background-position:center 18%"><span class="promo-tag">Spotlight</span></div>' +
      '<div class="promo-body"><div class="promo-kicker">This week on the desk</div>' +
      '<div class="promo-title">'+esc(feat.name)+' <span class="promo-stars">'+stars(feat.rating)+'</span></div>' +
      '<div class="promo-tagline">'+esc(ex)+'</div>' +
      '<span class="promo-cta">Read the review &#8599;</span></div>';
    pe.addEventListener("click", function(){ openReview(feat); });
  })();

  /* FAVORITES — five poster shelf */
  var GRAD = {
    "Dune: Part Two":"linear-gradient(150deg,#2c2010,#7a5320 90%)",
    "One Battle After Another":"linear-gradient(150deg,#2e1212,#84252a 90%)",
    "Django Unchained":"linear-gradient(150deg,#241408,#7a3c16 90%)",
    "A Star Is Born":"linear-gradient(150deg,#23112a,#7a205c 90%)",
    "Schindler's List":"linear-gradient(150deg,#0d0d0d,#3a3a3a 90%)"
  };
  LB.favorites.forEach(function (f, i) {
    var card = document.createElement("div");
    card.className = "fav reveal"; card.style.transitionDelay = (i*0.06)+"s";
    var art = f.poster
      ? '<img class="fav-img" src="'+f.poster+'" alt="'+attr(f.name)+'" />'
      : '<div class="fav-grad" style="background:'+(GRAD[f.name]||"linear-gradient(150deg,#1c2228,#384450)")+'"><span class="fav-gname">'+esc(f.name)+'</span></div>';
    card.innerHTML = '<div class="fav-poster">'+art+'<span class="fav-num">0'+(i+1)+'</span><span class="fav-tag">★</span></div>'+
      '<div class="fav-cap"><h3 class="fav-title">'+esc(f.name)+'</h3><span class="fav-year">'+(f.year||"")+'</span></div>';
    var r = reviewByKey[f.name+"|"+f.year];
    if (r) { card.style.cursor = "pointer"; card.addEventListener("click", function(){ openReview(r); }); }
    $("#favGrid").appendChild(card);
  });

  /* FEATURED REVIEWS */
  function miniPoster(r) {
    return r.poster ? '<img class="feature-poster" src="'+r.poster+'" alt="'+attr(r.name)+'" />'
                    : '<div class="feature-mini">'+esc(r.name)+'</div>';
  }
  $("#reviewsLede").textContent = LB.stats.reviews + " reviews on the desk. The latest cut below, the full archive one click away.";
  LBR.slice().sort(function(a,b){return (b.watched||"").localeCompare(a.watched||"") || (b.year||0)-(a.year||0);}).slice(0,6).forEach(function (r) {
    var ex = strip(r.review); if (ex.length>180) ex = ex.slice(0,180).replace(/\s+\S*$/,"")+"…";
    var c = document.createElement("div"); c.className = "feature reveal";
    c.innerHTML = '<div class="feature-top">'+miniPoster(r)+'<div class="feature-meta">'+
      '<div class="ft">'+esc(r.name)+'</div><div class="fy">'+(r.year||"")+'</div>'+
      '<div class="fs">'+stars(r.rating)+'</div></div></div>'+
      '<div class="feature-text">'+esc(ex)+'</div>'+
      '<div class="feature-foot"><span class="read">Read the verdict &#8594;</span>'+
      (r.rewatch?'<span class="badge-rw">Rewatch</span>':'')+'</div>';
    c.addEventListener("click", function(){ openReview(r); });
    $("#featuredReviews").appendChild(c);
  });
  /* REVIEWS LANDING (full archive, its own view) */
  (function () {
    var revs = LBR.slice();
    var rlTotal = $("#rlTotal"); if (rlTotal) rlTotal.textContent = num(revs.length);
    var rState = { q:"", filter:"all", sort:"new", shown:18 };
    var present = {};
    revs.forEach(function(r){ if (r.rating) present[r.rating] = true; });
    var chipDefs = [{v:"all",t:"All"}];
    [5,4.5,4,3.5,3,2.5,2,1.5,1,0.5].forEach(function(rt){ if (present[rt]) chipDefs.push({v:"r"+rt, t:stars(rt)}); });
    chipDefs.push({v:"rw",t:"Rewatch"});
    var rlChips = $("#rlChips");
    if (rlChips) chipDefs.forEach(function (c) {
      var b = document.createElement("button"); b.className = "chip"+(c.v==="all"?" active":""); b.textContent = c.t;
      b.addEventListener("click", function(){ rState.filter=c.v; rState.shown=18; $$(".chip",rlChips).forEach(function(x){x.classList.remove("active");}); b.classList.add("active"); renderRL(); });
      rlChips.appendChild(b);
    });
    function rlPass(r) {
      if (rState.q && r.name.toLowerCase().indexOf(rState.q)===-1) return false;
      if (rState.filter==="rw") return !!r.rewatch;
      if (rState.filter.charAt(0)==="r") return r.rating === parseFloat(rState.filter.slice(1));
      return true;
    }
    function rlSort(a) {
      var s = rState.sort;
      a.sort(function(x,y){
        if (s==="new") return (y.watched||"").localeCompare(x.watched||"") || (y.year||0)-(x.year||0);
        if (s==="old") return (x.watched||"").localeCompare(y.watched||"");
        if (s==="high") return (y.rating||0)-(x.rating||0) || (y.watched||"").localeCompare(x.watched||"");
        if (s==="low") return (x.rating||0)-(y.rating||0);
        if (s==="long") return (y.words||0)-(x.words||0);
        return 0;
      }); return a;
    }
    function rlCard(r) {
      var ex = strip(r.review); if (ex.length>240) ex = ex.slice(0,240).replace(/\s+\S*$/,"")+"…";
      var poster = r.poster ? '<img class="rl-poster" src="'+r.poster+'" alt="'+attr(r.name)+' poster" loading="lazy" />' : '<div class="rl-poster ph"><span>'+esc(r.name)+'</span></div>';
      var foot = [];
      if (r.watched) foot.push('<span class="rl-date">'+fmtDate(r.watched,false)+'</span>');
      if (r.words) foot.push('<span class="rl-words">'+num(r.words)+' words</span>');
      if (r.rewatch) foot.push('<span class="rl-rw">Rewatch</span>');
      var c = document.createElement("article"); c.className = "rl-card reveal in";
      c.innerHTML = poster +
        '<div class="rl-body"><div class="rl-head"><h3 class="rl-title">'+esc(r.name)+'</h3><span class="rl-year">'+(r.year||"")+'</span></div>'+
        '<div class="rl-stars">'+stars5(r.rating)+'</div>'+
        (ex?'<p class="rl-ex">'+esc(ex)+'</p>':'<p class="rl-ex muted">No written verdict, the stars carry it.</p>')+
        '<div class="rl-foot">'+foot.join("")+'</div></div>';
      c.addEventListener("click", function(){ openReview(r); });
      return c;
    }
    function renderRL() {
      var grid = $("#rlGrid"); if (!grid) return;
      var all = rlSort(revs.filter(rlPass)), slice = all.slice(0, rState.shown);
      grid.innerHTML = "";
      slice.forEach(function(r){ grid.appendChild(rlCard(r)); });
      $("#rlResult").textContent = num(all.length)+(all.length===1?" review":" reviews")+(rState.q?' for "'+rState.q+'"':"");
      $("#rlMore").hidden = all.length <= rState.shown;
    }
    var rlSearch = $("#rlSearch"); if (rlSearch) rlSearch.addEventListener("input", function(e){ rState.q=e.target.value.toLowerCase().trim(); rState.shown=18; renderRL(); });
    var rlSel = $("#rlSort"); if (rlSel) rlSel.addEventListener("change", function(e){ rState.sort=e.target.value; renderRL(); });
    var rlMore = $("#rlMore"); if (rlMore) rlMore.addEventListener("click", function(){ rState.shown += 18; renderRL(); });
    renderRL();
  })();

  /* PREDICTOR (member benefit, embedded tab) */
  (function () {
    var pc = LBC.predictor; if (!pc) return;
    if (pc.badge) $("#predBadge").textContent = pc.badge;
    if (pc.title) $("#predTitle").textContent = pc.title;
    if (pc.blurb) $("#predBlurb").textContent = pc.blurb;
    $("#predIframe").src = (pc.file || "predictor.html") + "?v=40";
  })();

  /* MOVIE MODE (member benefit, embedded tab) */
  (function () {
    var mc = LBC.moviemode; if (!mc) return;
    if (mc.badge) $("#mmBadge").textContent = mc.badge;
    if (mc.title) $("#mmTitle").textContent = mc.title;
    if (mc.blurb) $("#mmBlurb").textContent = mc.blurb;
    var f = $("#mmIframe"); if (f) f.src = (mc.file || "moviemode.html") + "?v=40";
  })();

  /* Auto height iframe matching: children postMessage their scrollHeight, parent resizes
     so the embedded section reads as part of the page, no inner scrollbar */
  window.addEventListener("message", function (e) {
    if (!e.data || typeof e.data.h !== "number") return;
    var id = e.data.frame === "mm" ? "mmIframe" : (e.data.frame === "pred" ? "predIframe" : null);
    if (!id) return;
    var f = document.getElementById(id); if (!f) return;
    var h = Math.max(240, e.data.h + 8);
    if (f.style.height !== h + "px") f.style.height = h + "px";
  });

  /* NUMBERS */
  [
    { v: st.films,        l: "Films Logged" },
    { v: st.hoursEst,     l: "Hours Watched", p: "approx" },
    { v: st.reviews,      l: "Reviews" },
    { v: st.reviewWords,  l: "Words Written" },
    { v: st.avg,          l: "Avg Rating", s: " ★", d: 2 },
    { v: st.fiveStars,    l: "Five Star" },
    { v: st.thisYear,     l: "Watched in " + new Date().getFullYear() },
    { v: st.likes,        l: "Liked" },
    { v: st.rewatches,    l: "Rewatches" },
    { v: st.longestStreak,l: "Longest Streak", s: " days" },
    { v: st.watchlist,    l: "Watchlist" },
    { v: st.followers,    l: "Followers" }
  ].forEach(function (t) {
    if (t.v === null || t.v === undefined) return;
    var d = document.createElement("div"); d.className = "bigstat";
    var head = t.p ? '<span class="bigstat-prefix">'+t.p+'</span> ' : '';
    d.innerHTML = '<div class="v">'+head+(t.d?t.v.toFixed(t.d):num(t.v))+(t.s||"")+'</div><div class="l">'+t.l+'</div>';
    $("#bigStats").appendChild(d);
  });
  (function(){
    var nu = $("#numbersUpdated"); if (!nu) return;
    var gen = LB.generatedAt || "", days = st.daysOnLetterboxd, dec = st.topDecade;
    var parts = [];
    if (gen) parts.push("Last refresh " + gen);
    if (days) parts.push(num(days) + " days on Letterboxd");
    if (dec && dec.decade) parts.push("Heaviest decade " + dec.decade);
    nu.textContent = parts.join(" · ");
  })();
  (function () {
    var order = ["5.0","4.5","4.0","3.5","3.0","2.5","2.0","1.5","1.0","0.5"], max = 0;
    order.forEach(function(k){ if((st.dist[k]||0)>max) max=st.dist[k]; });
    order.forEach(function (k) {
      var c = st.dist[k]||0, row = document.createElement("div"); row.className = "dist-row";
      row.innerHTML = '<span class="lab">'+stars(parseFloat(k))+'</span><span class="track"><span class="fill"></span></span><span class="cnt">'+c+'</span>';
      $("#distChart").appendChild(row);
      var fl = $(".fill", row); requestAnimationFrame(function(){ fl.style.width = (max?c/max*100:0)+"%"; });
    });
    var dec = st.decades, dmax = 0;
    Object.keys(dec).forEach(function(k){ if(dec[k]>dmax) dmax=dec[k]; });
    Object.keys(dec).sort().reverse().forEach(function (k) {
      var c = dec[k], row = document.createElement("div"); row.className = "dec-row";
      row.innerHTML = '<span class="lab">'+k+'</span><span class="track"><span class="fill"></span></span><span class="cnt">'+c+'</span>';
      $("#decadeChart").appendChild(row);
      var fl = $(".fill", row); requestAnimationFrame(function(){ fl.style.width = (dmax?c/dmax*100:0)+"%"; });
    });
    var gens = st.genres || [], gmax = gens.length ? gens[0][1] : 1;
    gens.forEach(function (g) {
      var w = gmax ? Math.round(g[1]/gmax*100) : 0;
      var row = document.createElement("div"); row.className = "gen-row";
      row.innerHTML = '<span class="lab">'+esc(g[0])+'</span><span class="track"><span class="fill" style="width:'+w+'%"></span></span><span class="cnt">'+g[1]+'</span>';
      $("#tagCloud").appendChild(row);
    });
  })();
  (function () {
    var bySlug = {}; (LB.lists||[]).forEach(function(l){ bySlug[l.slug] = l; });
    var dirs = (LB.auteurs||[]).filter(function(a){return a.cat==="Auteurs";}).slice(0,15);
    var html = '<h3>Auteurs on the desk</h3><div class="as-sub">'+st.auteurCount+' directors ranked, plus cinematographers and lead actors. Tap a name for the full ranking.</div><div class="auteur-rows">';
    dirs.forEach(function(a){ html += '<div class="auteur-row" data-slug="'+attr(a.slug)+'"><span class="who">'+esc(a.who)+'</span><span class="top">'+esc(a.top)+'</span></div>'; });
    html += '</div>'; $("#auteurStrip").innerHTML = html;
    $$(".auteur-row", $("#auteurStrip")).forEach(function(row){
      var l = bySlug[row.dataset.slug];
      if (l) { row.classList.add("clickable"); row.addEventListener("click", function(){ openList(l); }); }
    });
  })();

  /* VAULT */
  var films = LB.films.slice();
  $("#vaultCount").textContent = num(st.films);
  var vState = { q:"", filter:"all", sort:"rating", shown:6 };
  var present = {};
  films.forEach(function(f){ if (f.rating) present[f.rating] = true; });
  var chipDefs = [{v:"all",t:"All"}];
  [5,4.5,4,3.5,3,2.5,2,1.5,1,0.5].forEach(function(r){
    if (present[r]) chipDefs.push({v:"r"+r, t:stars(r)});
  });
  chipDefs.push({v:"rev",t:"Reviewed"},{v:"lk",t:"Liked"});
  chipDefs.forEach(function (c) {
    var b = document.createElement("button"); b.className = "chip"+(c.v==="all"?" active":""); b.textContent = c.t;
    b.addEventListener("click", function(){ vState.filter=c.v; vState.shown=12; $$(".chip",$("#vaultChips")).forEach(function(x){x.classList.remove("active");}); b.classList.add("active"); renderVault(); });
    $("#vaultChips").appendChild(b);
  });
  function vPass(f) {
    if (vState.q && f.name.toLowerCase().indexOf(vState.q)===-1) return false;
    if (vState.filter==="rev") return !!f.review;
    if (vState.filter==="lk") return !!f.liked;
    if (vState.filter.charAt(0)==="r") return f.rating === parseFloat(vState.filter.slice(1));
    return true;
  }
  function vSort(a) {
    var s = vState.sort;
    a.sort(function(x,y){
      if (s==="rating") return (y.rating||0)-(x.rating||0) || (x.name<y.name?-1:1);
      if (s==="ratingLow") return (x.rating||0)-(y.rating||0);
      if (s==="yearNew") return (y.year||0)-(x.year||0);
      if (s==="yearOld") return (x.year||0)-(y.year||0);
      if (s==="az") return x.name<y.name?-1:1;
      return 0;
    }); return a;
  }
  function renderVault() {
    var all = vSort(films.filter(vPass)), slice = all.slice(0, vState.shown), g = $("#vaultList");
    g.innerHTML = "";
    slice.forEach(function (f) {
      var row = document.createElement("div"); row.className = "vault-row";
      var poster = f.poster ? '<img class="vr-poster" src="'+f.poster+'" alt="" />' : '<div class="vr-poster"></div>';
      var sub = [(f.year||"")];
      var subHTML = '<span>'+(f.year||"")+'</span>'+(f.review?'<span class="rev">Review</span>':'')+(f.liked?'<span class="lk">&#9829; Liked</span>':'');
      row.innerHTML = poster +
        '<div class="vr-main"><div class="vr-title'+(f.review?' clickable':'')+'">'+esc(f.name)+'</div><div class="vr-sub">'+subHTML+'</div></div>'+
        '<div class="vr-stars">'+stars5(f.rating)+'</div>';
      var t = $(".vr-title", row);
      t.addEventListener("click", function () {
        var r = reviewByKey[f.name+"|"+f.year];
        if (r) openReview(r);
      });
      g.appendChild(row);
    });
    $("#vaultResult").textContent = num(all.length)+" films"+(vState.q?' for "'+vState.q+'"':"");
    $("#vaultMore").hidden = all.length <= vState.shown;
  }
  $("#vaultSearch").addEventListener("input", function(e){ vState.q=e.target.value.toLowerCase().trim(); vState.shown=60; renderVault(); });
  $("#vaultSort").addEventListener("change", function(e){ vState.sort=e.target.value; renderVault(); });
  $("#vaultMore").addEventListener("click", function(){ vState.shown = films.length; renderVault(); });
  renderVault();

  /* LISTS */
  var lists = LB.lists.slice();
  var lc = $("#listsCount"); if (lc) lc.textContent = num(st.lists || lists.length);
  var cats = ["All"].concat(st.listCats||[]);
  var lState = { cat:"All", limit:12 };
  cats.forEach(function (c) {
    var b = document.createElement("button"); b.className = "cat-tab"+(c==="All"?" active":""); b.textContent = c;
    b.addEventListener("click", function(){ lState.cat=c; lState.limit=12; $$(".cat-tab",$("#catTabs")).forEach(function(x){x.classList.remove("active");}); b.classList.add("active"); renderLists(); });
    $("#catTabs").appendChild(b);
  });
  function renderLists() {
    var g = $("#listGrid"); g.innerHTML = "";
    var filtered = lists.filter(function(l){ return lState.cat==="All" || l.cat===lState.cat; });
    if (lState.cat==="By Year") filtered.sort(function(a,b){ return (b.year||0)-(a.year||0); });
    filtered.slice(0, lState.limit).forEach(function (l) {
      var card = document.createElement("div"); card.className = "list-card";
      var blurb = (l.blurb && l.blurb.length>4) ? '<div class="lc-blurb">'+esc(l.blurb)+'</div>' : '';
      var cover = l.cover
        ? '<div class="lc-cover"><img src="'+l.cover+'" alt="" loading="lazy" /></div>'
        : '<div class="lc-cover ph"><span class="lc-ph-title">'+esc(l.title)+'</span></div>';
      card.innerHTML = cover + '<div class="lc-body">'+
        '<div class="lc-top"><span class="lc-cat">'+esc(l.cat)+'</span><span class="lc-count">'+(l.count?l.count+' films':'New, ranking soon')+'</span></div>'+
        '<div class="lc-title">'+esc(l.title)+'</div>'+blurb+'<div class="lc-open">See the ranking &#8594;</div></div>';
      card.addEventListener("click", function(){ openList(l); });
      g.appendChild(card);
    });
    var more = $("#listsMore");
    if (filtered.length > lState.limit) { more.hidden=false; more.textContent="See all "+filtered.length+(lState.cat==="All"?" lists":" in "+lState.cat); }
    else more.hidden = true;
  }
  $("#listsMore").addEventListener("click", function(){ lState.limit = 999; renderLists(); });
  renderLists();

  /* WEEK WATCHLIST (member perk) */
  (function () {
    var w = LBC.weekWatchlist; if (!w) return;
    var items = (w.locked||[]).map(function(t){ return '<div class="ww-item"><span class="lock">&#128274;</span><span class="blur">'+esc(t)+'</span></div>'; }).join("");
    $("#weekWatch").innerHTML = '<div class="ww-tag">Members only</div><h2>'+esc(w.heading)+'</h2>'+
      '<p class="ww-sub">'+esc(w.sub)+'</p><div class="ww-locked">'+items+'</div>'+
      '<a class="btn btn-join" href="#join">'+esc(w.cta||"Unlock")+'</a>';
  })();

  /* TIERS (membership) */
  (function () {
    var m = LBC.membership; if (!m) return;
    m.tiers.forEach(function (t) {
      var price = (/^\d/.test(t.price)) ? '<span class="cur">&#8369;</span>'+t.price : t.price;
      var perks = t.perks.map(function(p){
        var hl = /Year on the Desk|personalized to your activity/i.test(p);
        return '<li'+(hl?' class="perk-hl"':'')+'>'+esc(p)+(hl?' <span class="perk-new">NEW</span>':'')+'</li>';
      }).join("");
      var per = t.period ? esc(t.period) : "&nbsp;";
      var href = (/^\d/.test(t.price) && m.checkout) ? m.checkout : (t.url || "#");
      var blank = href.indexOf("http") === 0 ? ' target="_blank" rel="noopener"' : "";
      var d = document.createElement("div"); d.className = "tier"+(t.highlight?" hl":"");
      d.innerHTML = '<div class="t-name">'+esc(t.name)+'</div><div class="t-price">'+price+'</div>'+
        '<div class="t-period">'+per+'</div><ul class="t-perks">'+perks+'</ul>'+
        '<a class="btn '+(t.highlight?"btn-join":"btn-ghost")+'" href="'+href+'"'+blank+'>'+esc(t.cta)+'</a>';
      $("#tierGrid").appendChild(d);
      if (href === "#support") {
        var cbtn = $(".btn", d);
        if (cbtn) cbtn.addEventListener("click", function(e){
          e.preventDefault();
          var card = document.querySelector("#tipCard") || document.querySelector("#support");
          if (card) card.scrollIntoView({ behavior:"smooth", block:"center" });
          var box = $("#gcashBox"), tip = $("#tipBtn");
          if (box && box.hidden && tip) tip.click();
        });
      }
    });
    $("#tierNote").textContent = m.note||"";
  })();

  /* MERCH */
  (function () {
    var mc = LBC.merch; if (!mc) return;
    if (mc.archived) {
      var sec = document.getElementById("merch"); if (sec) sec.style.display = "none";
      $$('.nav-links a, .foot-links a').forEach(function(a){ if (a.getAttribute("href") === "#merch") a.style.display = "none"; });
      return;
    }
    $("#merchLede").textContent = mc.storeNote||"";
    var TEE = '<svg class="tee-svg" viewBox="0 0 240 200" preserveAspectRatio="xMidYMid meet" aria-hidden="true"><path d="M86 18 L52 30 L20 60 L44 92 L66 80 L66 188 L174 188 L174 80 L196 92 L220 60 L188 30 L154 18 C146 34 134 40 120 40 C106 40 94 34 86 18 Z"/></svg>';
    var mk = mc.mockup || {};
    mc.products.forEach(function (p) {
      var d = document.createElement("div"); d.className = "merch-card"; d.dataset.color = "black";
      var photos = "";
      if (mk.black) photos += '<img class="tee-photo blk" src="'+mk.black+'" alt="" onerror="this.closest(\'.merch-card\').classList.add(\'no-mock\')" />';
      if (mk.white) photos += '<img class="tee-photo wht" src="'+mk.white+'" alt="" onerror="this.closest(\'.merch-card\').classList.add(\'no-mock\')" />';
      if (!mk.black && !mk.white) d.classList.add("no-mock");
      d.innerHTML = '<div class="tee-mock">'+photos+'<div class="tee-fallback">'+TEE+'</div><div class="tee-print">'+esc(p.slogan)+'</div><span class="tee-pre">Preorder</span></div>'+
        '<div class="merch-body"><div class="m-info"><div class="m-tag">'+esc(p.tag)+'</div>'+
        '<div class="m-price">&#8369;'+p.price+'</div></div>'+
        '<div class="m-colors"><button class="swatch black active" title="Black" data-c="black"></button>'+
        '<button class="swatch white" title="White" data-c="white"></button></div>'+
        '<a class="m-buy" href="'+(mc.storeUrl||"#")+'">Preorder</a></div>';
      $$(".swatch", d).forEach(function(sw){ sw.addEventListener("click", function(){ d.dataset.color=sw.dataset.c; $$(".swatch",d).forEach(function(x){x.classList.remove("active");}); sw.classList.add("active"); }); });
      $("#merchGrid").appendChild(d);
    });
  })();

  /* PARTNER (work with the desk) + Year in Review */
  (function () {
    var p = LBC.partner;
    if (p) {
      if (p.heading) $("#partnerHeading").textContent = p.heading;
      if (p.sub) $("#partnerSub").textContent = p.sub;
      (p.cards||[]).forEach(function (c) {
        var mail = "mailto:"+(p.email||"")+"?subject="+encodeURIComponent(c.title+" — Arwin Reviews");
        var d = document.createElement("a"); d.className = "partner-card"; d.href = mail;
        d.innerHTML = '<span class="pc-tag">'+esc(c.tag)+'</span><h3>'+esc(c.title)+'</h3><p>'+esc(c.body)+'</p><span class="pc-cta">'+esc(c.cta)+' &#8599;</span>';
        $("#partnerGrid").appendChild(d);
      });
    }
    var y = LBC.yearInReview;
    if (y) $("#yirCard").innerHTML = '<div class="yir-l"><span class="yir-tag">'+esc(y.tag)+'</span><h3>'+esc(y.title)+'</h3><p>'+esc(y.body)+'</p></div>'+
      '<a class="btn btn-join" href="'+(y.url||"#join")+'">'+esc(y.cta)+'</a>';
  })();

  /* REQUEST A REVIEW + SUPPORT */
  (function () {
    var rr = LBC.requestReview, s = LBC.support || {};
    if (rr) {
      $("#rrTag").textContent = rr.tag || "Skip the queue";
      $("#rrTitle").textContent = rr.title || "Request a Review";
      $("#rrBody").textContent = rr.body || "";
      $("#rrBtn").href = "mailto:"+(s.sponsorEmail||"")+"?subject="+encodeURIComponent("Request a review");
      $("#rrBtn").textContent = rr.cta || "Request a film";
    }
    if (s.gcash) {
      $("#tipBtn").textContent = s.tipLabel || "Send via GCash";
      var box = $("#gcashBox");
      box.innerHTML = '<div class="gc-row"><span class="gc-k">GCash name</span><span class="gc-v">'+esc(s.gcash.name)+'</span></div>'+
        '<div class="gc-row"><span class="gc-k">GCash number</span><span class="gc-v">'+esc(s.gcash.number)+'</span></div>'+
        (s.gcash.qr ? '<img class="gc-qr" src="'+s.gcash.qr+'" alt="GCash QR" />' : '<div class="gc-note">Scan or send to the number above, any amount, thank you.</div>');
      $("#tipBtn").addEventListener("click", function(){ box.hidden = !box.hidden; $("#tipBtn").textContent = box.hidden ? (s.tipLabel||"Send via GCash") : "Hide"; });
    }
    if (s.paypal) { var pb = $("#paypalBtn"); if (pb) { pb.href = s.paypal; pb.hidden = false; } }
    var xBtn = $("#xenditTipBtn"), xBox = $("#xenditTipBox"), xGo = $("#xenditTipGo"), xMsg = $("#xenditTipMsg");
    if (xBtn && xBox) {
      xBtn.addEventListener("click", function(){
        xBox.hidden = !xBox.hidden;
        xBtn.textContent = xBox.hidden ? (s.xenditLabel || "Send via Xendit") : "Hide";
      });
    }
    if (xGo) {
      xGo.addEventListener("click", function(){
        var api = (window.ARWIN_PAYMENTS_API || "").trim();
        if (!api) { xMsg.style.color = "var(--muted)"; xMsg.textContent = "Xendit checkout coming online with Phase 2 deploy. GCash + PayPal work now."; return; }
        var amt = parseInt(($("#xenditTipAmt").value||"0"),10);
        var email = ($("#xenditTipEmail").value||"").trim();
        if (!amt || amt < 50) { xMsg.style.color = "var(--red)"; xMsg.textContent = "Amount must be at least P50."; return; }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { xMsg.style.color = "var(--red)"; xMsg.textContent = "Email needed for the receipt."; return; }
        xMsg.style.color = "var(--muted)"; xMsg.textContent = "Opening checkout...";
        xGo.disabled = true;
        fetch(api, { method: "POST", body: JSON.stringify({route:"create_tip_invoice", amount: amt, email: email}), headers: {"Content-Type":"text/plain"} })
          .then(function(r){return r.json()})
          .then(function(r){ if (r.ok && r.invoice_url) window.location.href = r.invoice_url; else { xMsg.style.color = "var(--red)"; xMsg.textContent = r.error || "Could not start checkout."; xGo.disabled = false; } })
          .catch(function(){ xMsg.style.color = "var(--red)"; xMsg.textContent = "Connection failed."; xGo.disabled = false; });
      });
    }
    $("#nlForm").addEventListener("submit", function (e) { e.preventDefault(); $("#nlForm").style.display="none"; $("#nlOk").hidden=false; });
  })();

  /* FOOTER */
  $("#footLine").innerHTML = num(st.films)+" films, "+st.reviews+" reviews, "+st.lists+" lists, every rating and word by "+esc(pr.name)+". Updated "+fmtDate(LB.generatedAt,true)+", and it keeps itself current.";

  /* REVIEW MODAL */
  var modal = $("#modal"), mbody = $("#modalBody");
  function openReview(r) {
    var poster = r.poster ? '<div class="m-poster"><img src="'+r.poster+'" alt="" /></div>'
                          : '<div class="m-poster"><div class="mini">'+esc(r.name)+'</div></div>';
    var badges = '<span class="m-badge date">'+fmtDate(r.watched,true)+'</span>'+
      (r.rewatch?'<span class="m-badge rewatch">Rewatch</span>':'')+(r.spoiler?'<span class="m-badge spoiler">Spoilers</span>':'');
    var body = r.review ? '<div class="m-review'+(r.spoiler?" blurred":"")+'">'+paras(r.review)+'</div>'+(r.spoiler?'<div class="m-spoiler-note">Tap to reveal spoilers</div>':'')
                        : '<div class="m-norev">No written verdict. The stars say it all.</div>';
    var tags = (r.tags&&r.tags.length)?'<div class="m-tags">'+r.tags.slice(0,10).map(function(t){return "<span>#"+esc(t)+"</span>";}).join("")+'</div>':"";
    mbody.innerHTML = poster + '<div class="m-side"><h3 class="m-title">'+esc(r.name)+'</h3>'+
      '<div class="m-year">'+(r.year||"")+'</div><div class="m-rating">'+stars(r.rating)+'</div>'+
      '<div class="m-badges">'+badges+'</div>'+body+tags+'</div>';
    if (r.spoiler) {
      var rev = $(".m-review",mbody), note = $(".m-spoiler-note",mbody);
      var rv = function(){ rev.classList.remove("blurred"); if(note) note.style.display="none"; };
      rev.addEventListener("click",rv); if(note) note.addEventListener("click",rv);
    }
    modal.hidden = false; document.body.style.overflow = "hidden";
  }
  function closeModal(){ modal.hidden = true; document.body.style.overflow = ""; }
  $$("[data-close]").forEach(function(b){ b.addEventListener("click",closeModal); });

  /* LIST MODAL */
  var listModal = $("#listModal");
  function openList(l) {
    var empty = !l.films || !l.films.length;
    var films = empty
      ? '<div class="lm-empty">This list was just published. The full ranking and cover sync on the next refresh.</div>'
      : l.films.map(function(f,i){
          var rk = f.n+"|"+f.y, has = !!reviewByKey[rk];
          return '<div class="lm-film"><span class="rank">'+(i+1)+'</span><span class="nm'+(has?" rev":"")+'" data-key="'+attr(rk)+'">'+esc(f.n)+'</span><span class="yr">'+(f.y||"")+'</span></div>';
        }).join("");
    $("#listModalBody").innerHTML = '<div class="list-modal-head"><div class="lm-cat">'+esc(l.cat)+(l.count?' · '+l.count+' films':'')+'</div>'+
      '<h3>'+esc(l.title)+'</h3>'+(l.blurb?'<p>'+esc(l.blurb)+'</p>':'')+
      (empty?'':'<p class="lm-hint">Titles in gold have a full review. Tap to read it.</p>')+'</div>'+
      '<div class="lm-films">'+films+'</div>';
    $$(".lm-film .nm.rev", $("#listModalBody")).forEach(function(nm){
      nm.addEventListener("click", function(){ var r = reviewByKey[nm.dataset.key]; if (r) { listModal.hidden=true; document.body.style.overflow=""; openReview(r); } });
    });
    listModal.hidden = false; document.body.style.overflow = "hidden";
  }
  $$("[data-close-list]").forEach(function(b){ b.addEventListener("click",function(){ listModal.hidden=true; document.body.style.overflow=""; }); });

  /* ARCHIVE */
  var archiveModal = $("#archiveModal");
  function renderArchive(q) {
    var list = $("#archiveList"); list.innerHTML = "";
    LBR.filter(function(r){ return !q || r.name.toLowerCase().indexOf(q)!==-1; }).forEach(function (r) {
      var ex = strip(r.review); if (ex.length>90) ex = ex.slice(0,90).replace(/\s+\S*$/,"")+"…";
      var row = document.createElement("div"); row.className = "arch-row";
      row.innerHTML = '<div class="ar-l"><div class="ar-t">'+esc(r.name)+'<span class="yr">'+(r.year||"")+'</span></div><div class="ar-ex">'+esc(ex)+'</div></div><div class="ar-s">'+stars(r.rating)+'</div>';
      row.addEventListener("click", function(){ archiveModal.hidden=true; openReview(r); });
      list.appendChild(row);
    });
  }
  function openArchive(){ renderArchive(""); $("#archiveSearch").value=""; archiveModal.hidden=false; document.body.style.overflow="hidden"; }
  $("#archiveSearch").addEventListener("input", function(e){ renderArchive(e.target.value.toLowerCase().trim()); });
  $$("[data-close-archive]").forEach(function(b){ b.addEventListener("click",function(){ archiveModal.hidden=true; document.body.style.overflow=""; }); });

  document.addEventListener("keydown", function (e) {
    if (e.key!=="Escape") return;
    [modal,listModal,archiveModal].forEach(function(m){ if(!m.hidden){ m.hidden=true; document.body.style.overflow=""; } });
  });

  /* REVEAL + NAV */
  var io;
  function observeReveals() {
    if (!("IntersectionObserver" in window)) { $$(".reveal").forEach(function(e){e.classList.add("in");}); return; }
    if (!io) io = new IntersectionObserver(function(ents){ ents.forEach(function(en){ if(en.isIntersecting){ en.target.classList.add("in"); io.unobserve(en.target); } }); }, { threshold:0.1, rootMargin:"0px 0px -40px 0px" });
    $$(".reveal:not(.in)").forEach(function(e){ io.observe(e); });
  }
  observeReveals();
  var nav = $("#nav");
  window.addEventListener("scroll", function(){ nav.classList.toggle("shrink", window.scrollY>40); }, { passive:true });

  /* SPA ROUTER, hash views + mobile drawer */
  (function () {
    var groups = {
      home:    [".hero", ".promo-wrap", "#favorites", "#reviews"],
      reviews: ["#reviewsLanding"],
      films:   ["#numbers", "#vault"],
      predict: ["#predictor"],
      moviemode: ["#moviemode"],
      lists:   ["#lists"],
      join:    ["#weekwatch", "#join", "#partner", "#support"]
    };
    var ALL = [".hero",".promo-wrap","#favorites","#reviews","#reviewsLanding","#numbers","#vault","#predictor","#moviemode","#lists","#weekwatch","#join","#partner","#support","#merch"];
    var ALIAS = { vault:"films", numbers:"films", stats:"films", review:"reviews", archive:"reviews", predictor:"predict", mood:"moviemode", mode:"moviemode", "movie-mode":"moviemode", partner:"join", support:"join", weekwatch:"join", merch:"home", shop:"home", promote:"join", top:"home", "":"home" };
    var SEO = {
      home:    { t:"ARWIN REVIEWS · Film Reviews and Ratings", d:"Film reviews, ratings, and ranked lists by Philippine critic Arwin Bagaslao. Theatrical, festival, and opening week verdicts." },
      reviews: { t:"Every Review on the Desk · ARWIN REVIEWS", d:"The full film review archive. Search and sort every verdict by Arwin Bagaslao, with ratings, stars, and the full take." },
      films:   { t:"All Films and Stats · ARWIN REVIEWS", d:"A searchable vault of every film logged, with star ratings, genres, decades, and auteur breakdowns." },
      predict: { t:"What Arwin Might Think · ARWIN REVIEWS", d:"A film rating predictor trained on Arwin's reviews. Get a likely score for any film before you watch it." },
      moviemode:{ t:"Find Your Next Watch · ARWIN REVIEWS", d:"Tell me how you feel and how you want to land. I match you to the right film from the desk, with a reason and a snippet from past you." },
      lists:   { t:"Ranked Film Lists · ARWIN REVIEWS", d:"Films ranked by director, cinematographer, decade, studio, genre, and mood." },
      join:    { t:"Join the Crew · ARWIN REVIEWS", d:"Back the desk. Unlock the predictor, the weekly watchlist, early reviews, and a vote on what gets reviewed next." }
    };
    function setMeta(sel, val){ var m=document.querySelector(sel); if(m) m.setAttribute("content", val); }
    function updateSEO(view){
      var s = SEO[view] || SEO.home;
      document.title = s.t;
      setMeta('meta[name="description"]', s.d);
      setMeta('meta[property="og:title"]', s.t);
      setMeta('meta[property="og:description"]', s.d);
      setMeta('meta[name="twitter:title"]', s.t);
      setMeta('meta[name="twitter:description"]', s.d);
      var url = "https://arwinreviews.com/#/" + (view==="home"?"":view);
      setMeta('meta[property="og:url"]', url);
      var cn = document.querySelector('link[rel="canonical"]'); if(cn) cn.setAttribute("href", url);
    }
    function resolve(t){ return groups[t] ? t : (ALIAS[t] || "home"); }
    function showOnly(view) {
      ALL.forEach(function(sel){ var e=document.querySelector(sel); if(e) e.style.display="none"; });
      (groups[view]||groups.home).forEach(function(sel){ var e=document.querySelector(sel); if(e){ e.style.display=""; $$(".reveal", e).forEach(function(x){ x.classList.add("in"); }); } });
      if (LBC.merch && LBC.merch.archived){ var m=document.querySelector("#merch"); if(m) m.style.display="none"; }
      $$(".nav-links a").forEach(function(a){ a.classList.toggle("active", a.getAttribute("data-route")===view); });
      updateSEO(view);
      if (window.gtag) gtag("event", "page_view", { page_path: location.hash || "#/", page_title: document.title });
      nav.classList.remove("open"); document.body.classList.remove("nav-open");
      var bg=$("#navBurger"); if(bg) bg.setAttribute("aria-expanded","false");
      window.scrollTo(0,0);
    }
    function route(){ showOnly(resolve(location.hash.replace(/^#\/?/, ""))); }
    window.addEventListener("hashchange", route);
    var burger = $("#navBurger");
    if (burger) burger.addEventListener("click", function(){
      var open = nav.classList.toggle("open"); document.body.classList.toggle("nav-open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", function(e){
      if (nav.classList.contains("open") && !nav.contains(e.target)) {
        nav.classList.remove("open"); document.body.classList.remove("nav-open");
        if (burger) burger.setAttribute("aria-expanded", "false");
      }
    });
    route();
  })();
})();
