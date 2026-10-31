#!/usr/bin/env python3
"""Build the Tashkent Expat Listings pages (art, music, theatre & film, dance, sport).

Rules (see METHOD.md): English or language-independent events only; only events within
WINDOW_DAYS of RUN_DATE; only events with tickets on sale or a published entry price (free counts);
neutral, factual descriptions."""
import datetime as dt
import html
import json
import os
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
RUN_DATE = "2026-10-31"   # set to the date of each refresh
WINDOW_DAYS = 30
TODAY = dt.date.fromisoformat(RUN_DATE)
WINDOW_END = TODAY + dt.timedelta(days=WINDOW_DAYS)

IT = "https://cdn.iticket.uz/event/facebook/"
ITC = "https://cdn.iticket.uz/event/cover/"
AF = "https://www.afisha.uz/uploads/media/"
class _SG(str):
    """ShowGo originals can be 5000px+; serve them through ShowGo's own 640px image optimiser."""
    def __add__(self, path):
        return "https://showgo.uz/_next/image?url=" + urllib.parse.quote("https://api.showgo.uz/storage/images/" + path, safe="") + "&w=640&q=75"


SG = _SG("")

# name, coords-or-query
V = {
    "navoi": ("Navoi Theatre (Bolshoi)", "41.309277,69.271248"),
    "humo": ("Humo Arena", "41.308170,69.2515825"),
    "palace": ("Palace of Friendship of Peoples", "41.3086,69.2417"),
    "turkiston": ("Turkiston Palace of Arts", "41.321520,69.269421"),
    "cons": ("State Conservatory of Uzbekistan", "41.314108,69.2550667"),
    "panorama": ("Panorama Cinema Palace", "41.319057,69.260254"),
    "unions": ("Palace of Trade Unions", "41.3088281,69.2769381"),
    "yunusobod": ("Yunusobod Sports Complex", "41.34654,69.28321"),
    "tcm": ("Tashkent City Mall, 2nd floor", "41.3161731,69.2498485"),
    "rusdrama": ("Russian Drama Theatre", "41.310288,69.2704618"),
    "operetta": ("Operetta Theatre (Musical Comedy)", "41.283403,69.208047"),
    "uzdrama": ("State Drama Theatre", "41.3252302,69.241066"),
    "youth": ("Theatre of Young Spectators", "41.3241787,69.254167"),
    "pakhtakor": ("Pakhtakor Central Stadium", "41.3154616,69.2602372"),
    "tplus": ("Theatre+ (ex-Zarafshan)", "41.312811,69.273405"),
    "ilkhom": ("Ilkhom Theatre", "Ilkhom Theatre, 5 Pakhtakor Street, Tashkent"),
    "cca": ("CCA Tashkent", "Centre for Contemporary Arts Tashkent"),
    "nbu": ("Gallery of Fine Arts of Uzbekistan (NBU)", "Gallery of Fine Arts of Uzbekistan, 2 Buyuk Turon, Tashkent"),
    "histmus": ("State Museum of History of Uzbekistan", "State Museum of History of Uzbekistan, Tashkent"),
    "goethe": ("Goethe-Institut Tashkent", "Goethe-Institut Tashkent"),
    "artepa": ("ARTepa Gallery, Green University", "Green University, Osiyo Street, Tashkent"),
    "library": ("Republican Children's Library", "Republican Children's Library, 47 Yahyo Gulomov Street, Tashkent"),
    "andakulova": ("Andakulova Gallery", "Andakulova Gallery, 7 Bobur Zokirov Street, Tashkent"),
    "tauz": ("TÁUZ art space", "TAUZ art space, Furkat Street, Tashkent"),
    "kinoxona": ("kinoxona art cinema", "17 Chimkent Street, Tashkent"),
    "sahna": ("Sahna Stand-Up Club", "17 Matbuotchilar Street, Tashkent"),
    "circus": ("State Circus of Uzbekistan", "Tashkent State Circus"),
    "cinematica": ("Cinematica, Tashkent City Mall (4th floor)", "41.3165,69.254"),
    "tbc": ("Tashkent (venue TBC)", None),
}


def maps(key):
    name, q = V[key]
    if not q:
        return None
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q, safe=",")


def d(s):
    return dt.date.fromisoformat(s)


def fmt_day(x):
    return f"{x.strftime('%a')} {x.day} {x.strftime('%b')}"


def when_text(item):
    """Build the date chip text."""
    if "opens" in item:
        return f"From {fmt_day(d(item['opens']))}"
    if "until" in item:
        u = d(item["until"])
        y = f" {u.year}" if u.year != 2026 else ""
        return f"Until {fmt_day(u)}{y}"
    if "range" in item:
        a, b = d(item["range"][0]), d(item["range"][1])
        y = f" {b.year}" if b.year != 2026 else ""
        t = f" · {item['time']}" if item.get("time") else ""
        if a.month == b.month:
            return f"{a.strftime('%a')} {a.day} – {fmt_day(b)}{y}{t}"
        return f"{fmt_day(a)} – {fmt_day(b)}{y}{t}"
    if "dates" in item:
        ds = [d(x) for x in item["dates"]]
        t = f" · {item['time']}" if item.get("time") else ""
        if len(ds) == 1:
            return f"{fmt_day(ds[0])}{t}"
        if len(ds) == 2:
            if ds[0].month == ds[1].month:
                return f"{ds[0].strftime('%a')} {ds[0].day} & {fmt_day(ds[1])}{t}"
            return f"{fmt_day(ds[0])} & {fmt_day(ds[1])}{t}"
        return ", ".join(f"{x.strftime('%a')} {x.day}" for x in ds[:-1]) + f" & {fmt_day(ds[-1])}{t}"
    return item.get("when", "")


def sort_key(item):
    if "sort_override" in item:
        return item["sort_override"]
    if "until" in item:
        return item["until"]
    if "opens" in item:
        return item["opens"]
    if "range" in item:
        return item["range"][0]
    if "dates" in item:
        return item["dates"][0]
    return item.get("sort", "2026-11-01")


def money(lo, hi=None):
    if lo == 0 and not hi:
        return "Free"
    if hi and hi != lo:
        return f"{lo:,}–{hi:,} UZS"
    return f"From {lo:,} UZS" if hi is None else f"{lo:,} UZS"


def esc(s):
    return html.escape(s, quote=True)


CSS = """
.tel{--tel-ink:#1f2937;--tel-navy:#1e3a5f;--tel-gold:#b8860b;--tel-muted:#64748b;--tel-line:#e2e8f0;--tel-chip:#edf2f7;font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--tel-ink);line-height:1.45;max-width:1080px;margin:0 auto;padding:8px}
.tel *{box-sizing:border-box}
.tel,.tel h2,.tel h3,.tel p{text-align:left;letter-spacing:normal;text-transform:none}
.tel h2,.tel h3{font-family:inherit;padding:0;border:0;background:none}
.tel-head{margin:0 0 12px}
.tel-head h2{font-size:1.45rem;color:var(--tel-navy);margin:0 0 2px}
.tel-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 16px;padding:0 0 12px;border-bottom:2px solid var(--tel-line)}
.tel-tab{background:var(--tel-chip);color:var(--tel-navy);border:0;padding:7px 13px;margin:0;border-radius:6px;font-family:inherit;font-size:.84rem;font-weight:600;line-height:1.2;text-transform:none;letter-spacing:normal;box-shadow:none;cursor:pointer}
.tel-tab:hover{background:#cbd5e1}
.tel-tab.on{background:var(--tel-navy);color:#fff}
.tel-tab span{opacity:.7;font-weight:500}
.tel-grid{display:grid;grid-template-columns:1fr;gap:16px}
@media(min-width:620px){.tel-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(min-width:960px){.tel-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
.tel-card{background:#fff;border:1px solid var(--tel-line);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 1px 4px rgba(15,23,42,.06)}
.tel-card[hidden]{display:none}
.tel-img{position:relative;aspect-ratio:1.91/1;background:linear-gradient(135deg,#1e3a5f 0%,#2b4c7e 60%,#b8860b 160%);overflow:hidden}
.tel-img img{position:absolute!important;inset:0;width:100%!important;height:100%!important;max-width:none!important;margin:0!important;padding:0!important;border:0!important;border-radius:0!important;object-fit:cover;display:block;box-shadow:none!important}
.tel-ph{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;color:#fff;text-align:center;padding:12px}
.tel-ph b{font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;opacity:.85}
.tel-ph i{font-style:normal;font-size:1.05rem;font-weight:700;line-height:1.25}
.tel-badges{position:absolute;top:8px;left:8px;right:8px;display:flex;flex-wrap:wrap;gap:4px;z-index:2}
.tel-badge{background:rgba(255,255,255,.94);color:var(--tel-navy);font-size:.68rem;font-weight:700;padding:2px 8px;border-radius:999px;box-shadow:0 1px 2px rgba(0,0,0,.15)}
.tel-badge.hot{background:#b91c1c;color:#fff}
.tel-badge.free{background:#15803d;color:#fff}
.tel-badge.new{background:var(--tel-gold);color:#fff}
.tel-badge.eng{background:#1d4ed8;color:#fff}
.tel-body{padding:14px 16px 14px;display:flex;flex-direction:column;flex:1}
.tel-title{font-size:1.04rem;line-height:1.3;margin:0 0 4px}
.tel-title a{color:var(--tel-navy);text-decoration:none}
.tel-title a:hover{color:var(--tel-gold);text-decoration:underline}
.tel-venue{font-size:.85rem;font-weight:600;color:var(--tel-gold)}
.tel-venue a{color:var(--tel-gold);text-decoration:none}
.tel-venue a:hover{text-decoration:underline}
.tel-when{align-self:flex-start;background:#f1f5f9;color:var(--tel-navy);font-size:.79rem;font-weight:600;padding:3px 8px;border-radius:4px;margin:8px 0}
.tel-desc{font-size:.86rem;color:#334155;margin:0 0 12px}
.tel-desc ul{margin:4px 0 0;padding-left:18px}
.tel-meta{font-size:.78rem;color:var(--tel-muted);margin:-6px 0 12px}
.tel-foot{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:auto;padding-top:10px;border-top:1px solid var(--tel-line)}
.tel-price{font-size:.82rem;font-weight:600;color:var(--tel-ink)}
.tel-btn{display:inline-block;border:0;line-height:1.3;background:var(--tel-navy);color:#fff!important;text-decoration:none;padding:6px 12px;border-radius:4px;font-size:.79rem;font-weight:600;white-space:nowrap;transition:background .2s}
.tel-btn:hover{background:var(--tel-gold)}
""".strip()

JS = """(function(){var r=document.getElementById('%s');if(!r)return;var tabs=r.querySelectorAll('.tel-tab'),cards=r.querySelectorAll('.tel-card');for(var i=0;i<tabs.length;i++){tabs[i].addEventListener('click',function(){var t=this.getAttribute('data-f');for(var j=0;j<tabs.length;j++){tabs[j].classList.remove('on');tabs[j].setAttribute('aria-selected','false');}this.classList.add('on');this.setAttribute('aria-selected','true');for(var k=0;k<cards.length;k++){var c=cards[k].getAttribute('data-f')||'';cards[k].hidden=!(t==='all'||(' '+c+' ').indexOf(' '+t+' ')>-1);}});}})();"""


def card(it, label):
    badges = "".join(
        f'<span class="tel-badge {cls}">{esc(txt)}</span>' for txt, cls in it.get("badges", [])
    )
    pos = f' style="object-position:{it["pos"]}"' if it.get("pos") else ""
    img = ""
    if it.get("img"):
        img = (
            f'<img src="{esc(it["img"])}" alt="{esc(it["t"])}" loading="lazy" decoding="async" '
            f'referrerpolicy="no-referrer"{pos} onerror="this.remove()">'
        )
    ph_top = it.get("ph", label)
    vname = V[it["v"]][0] if it["v"] in V else it["v"]
    vlabel = it.get("vlabel", vname)
    m = maps(it["v"]) if it["v"] in V else None
    venue = (
        f'<a href="{esc(m)}" target="_blank" rel="noopener" title="Open in Google Maps">📍 {esc(vlabel)}</a>'
        if m
        else f"📍 {esc(vlabel)}"
    )
    meta = f'<div class="tel-meta">{esc(it["meta"])}</div>' if it.get("meta") else ""
    desc = it["d"] if it.get("raw") else esc(it["d"])
    return f"""<article class="tel-card" data-f="{esc(' '.join(it['f']))}">
<div class="tel-img"><div class="tel-ph"><b>{esc(ph_top)}</b><i>{esc(it['t'])}</i></div>{img}<div class="tel-badges">{badges}</div></div>
<div class="tel-body">
<h3 class="tel-title"><a href="{esc(it['u'])}" target="_blank" rel="noopener">{esc(it['t'])}</a></h3>
<div class="tel-venue">{venue}</div>
<div class="tel-when">{esc(when_text(it))}</div>
<p class="tel-desc">{desc}</p>{meta}
<div class="tel-foot"><span class="tel-price">{esc(it['p'])}</span><a class="tel-btn" href="{esc(it['u'])}" target="_blank" rel="noopener">{esc(it.get('btn','Tickets'))} ↗</a></div>
</div>
</article>"""



# ---------------------------------------------------------------- rules
NOT_ON_SALE = ("tba", "tbc", "soon", "not published", "ask at", "check with")


def in_window(it):
    """Trim an item to the 30-day window. Returns the item (possibly with fewer dates) or None."""
    it = dict(it)
    if "until" in it:  # exhibitions: listed while open
        return it if d(it["until"]) >= TODAY and d(it.get("from", RUN_DATE)) <= WINDOW_END else None
    if "opens" in it:  # film runs: listed from a few days before they open until the opening day passes
        return it if TODAY <= d(it["opens"]) <= WINDOW_END else None
    if "range" in it:
        a, b = d(it["range"][0]), d(it["range"][1])
        return it if b >= TODAY and a <= WINDOW_END else None
    if "dates" in it:
        keep = [x for x in it["dates"] if TODAY <= d(x) <= WINDOW_END]
        if not keep:
            return None
        it["dates"] = keep
        return it
    raise ValueError(f"{it['t']}: no date")


def check(it):
    p = it["p"].lower()
    if any(w in p for w in NOT_ON_SALE):
        raise ValueError(f"{it['t']}: tickets not on sale / price not published ({it['p']})")
    if not it.get("u", "").startswith("https://"):
        raise ValueError(f"{it['t']}: missing link")


def title_range():
    y = f" {WINDOW_END.year}"
    return f"{TODAY.day} {TODAY.strftime('%b')} – {WINDOW_END.day} {WINDOW_END.strftime('%b')}{y}"


def build(key, name, label, tabs, items):
    cid = f"tel-{key}"
    for it in items:
        check(it)
    items = sorted(filter(None, (in_window(i) for i in items)), key=sort_key)
    counts = {f: sum(1 for i in items if f in i["f"]) for f, _ in tabs}
    tab_html = f'<button class="tel-tab on" data-f="all" role="tab" aria-selected="true">All <span>({len(items)})</span></button>'
    for f, tname in tabs:
        if counts[f]:
            tab_html += f'<button class="tel-tab" data-f="{f}" role="tab" aria-selected="false">{esc(tname)} <span>({counts[f]})</span></button>'
    cards = "\n".join(card(i, label) for i in items)
    title = f"{name} · {title_range()}"
    snippet = f"""<!-- Tashkent Expat Listings · {name} · updated {RUN_DATE} -->
<style>
{CSS}
</style>
<div class="tel" id="{cid}">
<div class="tel-head"><h2>{esc(title)}</h2></div>
<div class="tel-tabs" role="tablist">{tab_html}</div>
<div class="tel-grid">
{cards}
</div>
</div>
<script>{JS % cid}</script>
"""
    path = os.path.join(OUT, f"{key}.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(snippet)
    return path, snippet, items


# ---------------------------------------------------------------- ART (exhibitions: listed while open)
ART = [
    dict(t="BENCHELLAL, Monumental: Sculpting Past Tomorrow", v="histmus", until="2026-11-08",
         u="https://ccat.uz/en/programme/benchellal-monumental-sculpting-past-tomorrow", btn="Details",
         d="Sculptural garments by Dutch-Moroccan designer Mohamed Benchellal, based on the forms of modernist architecture. First shown at the National Museum of Qatar; this version adds works made during his CCA Tashkent residency.",
         p="Free", img=AF + "2026/08/0ee91cccb24dc2849af17c049888660a_m.webp",
         badges=[("Free", "free"), ("Closes 8 Nov", "hot")], f=["closing", "free"]),
    dict(t="Levitation — in memory of Bayat Mukhtarov", v="nbu", until="2026-11-14",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/21/levitation", btn="Details (RU)",
         d="Exhibition of work by sculptor Bayat Mukhtarov, a figure of the Uzbek avant-garde.",
         meta="Tue–Sat 10:00–17:00 (closed Sun and Mon).",
         p="10,000–50,000 UZS", img=AF + "2026/10/df872e8908892053090413589fac0aa4_m.webp",
         badges=[("Closes 14 Nov", "hot")], f=["closing"]),
    dict(t="Textures and Fragments — Yermolai Solzhenitsyn", v="ilkhom", until="2026-11-16",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/08/textures", btn="Details (RU)",
         d="Photographs of textures and details in natural and built surroundings, shown in the foyer of the Ilkhom Theatre.",
         meta="Tue–Sun 11:00–18:00 (closed Mon).",
         p="Free", img=AF + "2026/10/6221bcf9919d73f706e49cc6fb441dee_m.webp",
         badges=[("Free", "free"), ("Photography", "")], f=["closing", "free"]),
    dict(t="Journey — Timur D'Vatz", v="andakulova", until="2026-11-18",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/12/dvatz-26", btn="Details (RU)",
         d="Solo exhibition by Timur D'Vatz, a graduate of the Royal Academy Schools and winner of the BP Portrait Award. The works draw on ancient history, medieval tapestry, Celtic mythology and alchemy.",
         p="Free", img=AF + "2026/10/bd41b11c9995d4502412ef202d7e7702_m.webp",
         badges=[("Free", "free")], f=["closing", "free"]),
    dict(t="Book Graphics of Kydyrbay Nazhimov", v="library", until="2026-11-30",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/06/nazhimov", btn="Details (RU)",
         d="Book illustrations by Kydyrbay Nazhimov, mostly in scratchboard technique. A programme of children's workshops runs alongside; some sessions require registration.",
         meta="Daily 10:00–21:00. All ages.",
         p="Free", img=AF + "2026/10/a4adb19b8cda2b16bd2141bd10d86200_m.webp",
         badges=[("Free", "free")], f=["closing", "free"]),
    dict(t="Chiroyli Vanitas — Elena Martynova", v="kinoxona", until="2026-11-30",
         u="https://www.afisha.uz/ru/cinema/2026/10/20/kinoxona", btn="Details (RU)",
         d="Solo photography exhibition by Elena Martynova at the kinoxona art cinema.",
         p="Free", img=AF + "2026/10/87bdc4dd60d4590b5cc0b123d321d9fd_m.webp",
         badges=[("Free", "free"), ("Photography", "")], f=["closing", "free"]),
    dict(t="Life Beyond Measure — Zurab Tsereteli", v="nbu", until="2026-12-01",
         u="https://www.afisha.uz/ru/exhibitions/2026/08/13/vystavka-cereteli", btn="Details (RU)",
         d="Retrospective of Georgian-Russian artist Zurab Tsereteli (1934–2025): painting, sculpture, enamels, reliefs and silkscreens from across his career. Organised with the Russian Academy of Arts.",
         meta="Tue–Sat 10:00–17:00 (closed Sun and Mon).",
         p="10,000–50,000 UZS (gallery entry)", img=AF + "2026/08/e1de191d47cac18a0f69fa7b49556130_m.webp",
         f=["long"]),
    dict(t="San'at Up", v="goethe", until="2026-12-12",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/01/sanatup-gi", btn="Details (RU)",
         d="Works by young artists from Uzbekistan and Tajikistan selected through the San'at Up competition, displayed in the institute's stairwell.",
         meta="10:00–19:00.",
         p="Free", img=AF + "2026/09/1057ff60173b79351bfeccab600fafd4_m.webp",
         badges=[("Free", "free")], f=["long", "free"]),
    dict(t="Interflows", v="artepa", until="2026-12-15",
         u="https://www.afisha.uz/ru/exhibitions/2026/09/28/interflows", btn="Details (RU)",
         d="Exhibition on water in Central Asia and its ecological, political and social dimensions, by the DAVRA research group and Art Station. Includes work by young artists from the region and Saodat Ismailova's film Stains of Oxus. The display changes during the run.",
         p="Free", img=AF + "2026/09/54a3063a884452f9b882db8ad30cca41_m.webp",
         badges=[("Free", "free")], f=["long", "free"]),
    dict(t="Savitsky's Diaries: Old and New", v="tcm", until="2027-01-24",
         u="https://iticket.uz/en/events/cultural-events/savitskys-diaries-old-and-new-2027",
         d="Multimedia exhibition combining painting, music, light and movement, about Igor Savitsky, founder of the Karakalpakstan State Museum of Art in Nukus. Organised by ACDF; curated by Aziza Izamova.",
         p="40,000–60,000 UZS", img=IT + "k2wro6npuQ0dyr2ezSgCQSu9UdFc3rToBaLdHDga.jpg",
         badges=[("Multimedia", "")], f=["long"]),
    dict(t="Hikmah", v="cca", until="2027-01-31",
         u="https://ccat.uz/en/programme/hikmah-exhibition", btn="Details",
         d="Opening exhibition of the Centre for Contemporary Arts Tashkent: new commissions and recent works by Uzbek and international artists on wisdom, spirit and the transformation of matter. The centre occupies a restored 1912 diesel power station.",
         meta="The centre is closed 10–20 November.",
         p="Free", img=AF + "2026/08/8d19dc8eb2f5bc2b8c6e6ec1aa41ccb7_m.webp",
         badges=[("Free", "free"), ("Closed 10–20 Nov", "hot")], f=["long", "free"]),
]

# ---------------------------------------------------------------- MUSIC
MUSIC = [
    dict(t="Mozart & Chopin — Young Talents Chamber Orchestra", v="cons", dates=["2026-11-13"], time="19:00",
         u="https://iticket.uz/en/events/concerts/mozart-and-chopin-young-talents-chamber-orchestra",
         d="Works by Mozart and Chopin performed by the Young Talents Chamber Orchestra.",
         p="66,000–165,000 UZS", img=IT + "qwRxxi3d2cOs5NFvnwI8kHcNBz8DmCNj1dDr89CM.jpg", f=["classical"]),
    dict(t="From the New World — National Symphony Orchestra", v="turkiston", dates=["2026-11-23"], time="19:00",
         u="https://iticket.uz/en/events/concerts/iz-novogo-sveta",
         d="Conductor Boburjon Kurbonaliev. Rachmaninoff, The Rock; Haydn, Cello Concerto (soloist Sardor Ibragimov); Dvořák, Symphony No. 9.",
         p="77,000–132,000 UZS", img=IT + "chuD6MvHrRwBn3GszCWdLv47l3VSpqAUKU9OZx6q.jpg", f=["classical"]),
    dict(t="An Evening of Organ Music — Soloists of Uzbekistan", v="cons", vlabel="State Conservatory (Organ Hall)",
         dates=["2026-11-27"], time="19:00",
         u="https://iticket.uz/en/events/concerts/vecher-organnoj-muzyki-solisty-uzbekistana",
         d="Soloists of Uzbekistan chamber orchestra, conductor Anvar Raimdzhanov, with organist Adelina Fatkhutdinova. Bach, Albinoni, Rheinberger (Organ Concerto in G minor), Respighi and Jenkins.",
         p="88,000–385,000 UZS", img=IT + "FLgbVLSlOu8sxvtCkQ3toUbsdqsPguvOzqqiUqb8.jpg",
         badges=[("Few seats left", "hot")], f=["classical"]),
    dict(t="The Music of Hans Zimmer — Tynda Music", v="panorama", dates=["2026-11-14"], time="19:00",
         u="https://iticket.uz/en/events/concerts/the-music-of-hans-zimmer-tynda-music",
         d="Film music by Hans Zimmer performed by a symphony orchestra and choir.",
         p="230,000–700,000 UZS", img=IT + "qEutxJne5Fk4pgjwiFAOL0C0oWsF2gW1a9DtH03s.jpg", f=["crossover"]),

    dict(t="MICHAEL: Legendary Hits — Turkiston Chamber Orchestra", v="turkiston", dates=["2026-11-25"], time="19:00",
         u="https://iticket.uz/en/events/concerts/michael-legendarnye-hity",
         d="Orchestral arrangements of Michael Jackson songs, including Billie Jean, Bad, Smooth Criminal, Thriller and Black or White.",
         p="66,000–275,000 UZS", img=IT + "7My29fzdiw9mf3TTAKc90ML5DRxDjwbYUSAlmtxo.jpg", f=["crossover"]),
    dict(t="Tamerlano (Handel)", v="navoi", range=["2026-11-02", "2026-11-04"], time="19:00",
         u="https://iticket.uz/en/events/concerts/tamerlano-2026",
         d="Handel's opera directed by Stefano Poda, in an arrangement by Kirill Richter. National Symphony Orchestra of Uzbekistan, conductor Alibek Kabdurakhmanov, with traditional Uzbek instruments.",
         p="100,000–800,000 UZS", img=IT + "ekdExRDpGo188AcZzhtZR0btOQNcWgg5YvIwIh9W.jpg",
         badges=[("3 performances", "new")], f=["opera"]),
    dict(t="La Traviata (Verdi)", v="navoi", dates=["2026-11-08"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/dzh-verdi-traviata-opera-2626",
         d="Verdi's opera in three acts.",
         p="77,000–440,000 UZS", img=IT + "i4VLvZ1iN3Rxt35CrPO3v2NFVv4qxgX8oNB5Otgk.jpg", f=["opera"]),
    dict(t="Alisher Navoi (Mustafo Bafoev)", v="navoi", dates=["2026-11-10"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/m-bafoev-aliser-navoi-opera-9714",
         d="Opera by Mustafo Bafoev about the life of the 15th-century poet and statesman Alisher Navoi.",
         p="55,000–165,000 UZS", img=IT + "OFpifJGjvxRtXfCVMkTGs3BVPl2ejF1BPZGj7K4b.jpg", f=["opera"]),
    dict(t="Don Giovanni (Mozart)", v="navoi", dates=["2026-11-14"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/vamocart-don-zhuan-opera-2626",
         d="Mozart's opera in two acts.",
         p="77,000–440,000 UZS", img=IT + "S4FjY4VGnklyB7uOwD7n3tjJwYUfjLCZZRTYAX9u.jpg", f=["opera"]),
    dict(t="Pagliacci (Leoncavallo)", v="navoi", dates=["2026-11-15"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/rleonkavallo-payacy-opera-9458",
         d="Leoncavallo's opera in two acts, set among a travelling theatre troupe.",
         p="55,000–165,000 UZS", img=ITC + "QZtusilsj1kCteXDi7z6zD9ei4PUxNAnElwSbU7G.jpg", f=["opera"]),
    dict(t="Un ballo in maschera (Verdi)", v="navoi", dates=["2026-11-19"], time="19:00",
         u="https://www.afisha.uz/ru/concerts/2024/10/08/g-verdi", btn="Tickets (RU)",
         d="Verdi's opera, performed in two acts.",
         p="From 55,000 UZS", img=AF + "2024/10/2b200358b5e7b14fb0d7bbe2f14b082f_m.jpg", f=["opera"]),
    dict(t="La Bohème (Puccini)", v="navoi", dates=["2026-11-21"], time="19:00",
         u="https://www.afisha.uz/ru/theatres/2025/03/04/bogema", btn="Tickets (RU)",
         d="Puccini's opera, with the State Symphony Orchestra of Uzbekistan.",
         p="From 55,000 UZS", img=AF + "2025/03/946620b27a8c8241c4e1fa831693c10d_m.webp", f=["opera"]),
    dict(t="Carmen (Bizet)", v="navoi", dates=["2026-11-22"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/zhorzh-bize-karmen-opera",
         d="Bizet's opera in a new production by Konstantin Kamynin, set in Spain in the 1940s–50s.",
         p="110,000–330,000 UZS", img=IT + "lQUeJ9lAxQ4BB96nLKg9iVDbgirMOyraweAmTRe0.jpg",
         badges=[("New production", "new")], f=["opera"]),
    dict(t="Jazzirama — IlkhomJazzClub", v="ilkhom", dates=["2026-11-03"], time="19:00",
         u="https://www.afisha.uz/ru/concerts/2026/10/13/jazzirama-11", btn="Tickets (RU)",
         d="Season opening of the IlkhomJazzClub. Tashkent band Jazzirama with guest vocalists including Mansur Tashmatov and maqom singer Nodira Pirmatova: jazz standards, ethno-jazz and improvisation.",
         p="240,000–290,000 UZS", img=AF + "2026/10/fc7f51f39f3074272c0646f5856e9796_m.webp", f=["jazz"]),

    dict(t="KALEO", v="humo", dates=["2026-11-27"], time="19:00",
         u="https://showgo.uz/en/session/1165-kaleo-live-in-tashkent",
         d="Icelandic blues-rock band.",
         p="From 250,000 UZS", img=SG + "2026/09/cropped_20260907114146_lrqs_05261C4D-B221-4918-89BE-420BF156B13E.jpg",
         pos="center 30%", f=["jazz"]),


    dict(t="Cheb Mami", v="humo", dates=["2026-11-07"], time="20:00",
         u="https://iticket.uz/en/events/concerts/cheb-mami",
         d="Algerian raï singer Cheb Mami in his first concert in Tashkent.",
         p="150,000–2,000,000 UZS", img=IT + "jzp3aCFiqfPGykFUOudYAdj566hzkHzFCSiFyQHh.jpg", f=["jazz"]),












]

# ---------------------------------------------------------------- THEATRE & FILM
CM = "https://cinematica.uz/uploads/movies/"
CM_META = "English-language screenings in 2D, no subtitles. Showtimes are published a few days before."
CM_PRICE = "35,000–70,000 UZS (standard halls)"
THEATRE = [
    dict(t="White, White Black Stork", v="ilkhom", dates=["2026-11-04"], time="19:00",
         u="https://ilkhom.com/events/belyj-belyj-chyornyj-aist-eng-subs/", btn="Details & tickets",
         d="Ilkhom Theatre production based on Abdulla Qodiriy's unfinished novella 'From the Notebook of Kalvak Makhzum', with material from his novel 'Days Gone By': young love and social convention in old Tashkent. Directed by Yolkin Tuychiev and Mark Weil. 1 hr 45 min, 14+.",
         meta="In Russian with English surtitles.",
         p="150,000–180,000 UZS", img=AF + "2026/10/c97fe2cda316f786a373414dd1c54087_m.webp",
         badges=[("English surtitles", "eng")], f=["stage"]),
    dict(t="Seven Moons", v="ilkhom", dates=["2026-11-13"], time="19:00",
         u="https://ilkhom.com/events/sem-lun-eng-subs/", btn="Details & tickets",
         d="Sufi parable after Alisher Navoi about a shah who loses everything through pride. Directed by Vladimir Pankov with the Moscow studio SounDrama, with live saxophone, nay, double bass and percussion. 1 hr 45 min, 16+.",
         meta="In Russian with English surtitles.",
         p="150,000–180,000 UZS", img=AF + "2026/08/fe6c19d4a1f69130ed8ab4273522874a_m.webp",
         badges=[("English surtitles", "eng"), ("Live music", "")], f=["stage"]),
    dict(t="Charlie and the Sea Lions", v="circus", range=["2026-10-31", "2026-12-06"],
         u="https://showgo.uz/en/session/1328-tsirk-charli-i-morskie-kotiki-tashkent-2026",
         d="Russian circus programme at the State Circus, featuring clown Charlie from Germany and a sea lion act. Runs until 6 December.",
         p="From 70,000 UZS", img=SG + "2026/10/cropped_20261028071204_lbjl_photo_2026-10-28_12-10-55.jpg",
         pos="center 30%", ph="Circus", badges=[("Visual show", "eng")], f=["stage", "family"]),
    dict(t="Planètes (2025)", v="kinoxona", dates=["2026-11-01"], time="12:00",
         u="https://showgo.uz/en/session/1396-odisseia-oduvanchikov-planetes-2025",
         d="Animated film by Momoko Seto, selected for the Directors' Fortnight at Cannes: after Earth is destroyed, four dandelion seeds travel through space. Combines macro photography and computer animation.",
         meta="No dialogue.",
         p="90,000 UZS", img=SG + "2026/10/cropped_20261028070436_ykas_7.jpg", pos="center 30%", ph="kinoxona",
         badges=[("No dialogue", "eng")], f=["film"]),
    dict(t="The Little Shop of Horrors (1960)", v="kinoxona", dates=["2026-11-01"], time="16:00",
         u="https://showgo.uz/en/session/1392-malenkii-magazinchik-uzhasov-the-little-shop-of-horrors-1960",
         d="Roger Corman's black comedy about a florist's assistant and a carnivorous plant.",
         meta="Original English audio with Russian subtitles.",
         p="90,000 UZS", img=SG + "2026/10/cropped_20261028064610_tzol_3_2.jpg", pos="center 30%", ph="kinoxona",
         badges=[("In English", "eng")], f=["film"]),
    dict(t="Lil Peep: Everybody's Everything (2019)", v="kinoxona", dates=["2026-11-01"], time="19:30",
         u="https://showgo.uz/en/session/1395-lil-peep-vsio-dlia-vsekh-everybodys-everything-2019",
         d="Documentary about the musician Lil Peep, drawing on his music, home video and interviews with people close to him.",
         meta="Original English audio with Russian subtitles.",
         p="90,000 UZS", img=SG + "2026/10/cropped_20261028082900_hqkq_4.jpg", pos="center 30%", ph="kinoxona",
         badges=[("In English", "eng"), ("Few seats left", "hot")], f=["film"]),
    dict(t="The Cat in the Hat", v="cinematica", opens="2026-11-05",
         u="https://cinematica.uz/movies/1049", btn="Details",
         d="Animated Dr. Seuss adaptation in which the Cat, voiced by Bill Hader, visits two siblings stuck indoors on a rainy day.",
         meta=CM_META,
         p=CM_PRICE, img=CM + "cdcf983f-9269-4574-9959-eb49aa4688bc.png", ph="Cinematica",
         badges=[("In English", "eng"), ("Family", "")], f=["film", "family"]),
    dict(t="Ebenezer: A Christmas Carol", v="cinematica", opens="2026-11-12",
         u="https://www.instagram.com/englishmovieclubuz/", btn="Details",
         d="Adaptation of Dickens's A Christmas Carol, with Johnny Depp as Ebenezer Scrooge.",
         meta=CM_META,
         p=CM_PRICE, img=None, ph="Cinematica",
         badges=[("In English", "eng")], f=["film"]),
    dict(t="The Hunger Games: Sunrise on the Reaping", v="cinematica", opens="2026-11-19",
         u="https://cinematica.uz/movies/1071", btn="Details",
         d="Prequel set 24 years before the original trilogy, in which a young Haymitch Abernathy competes in the 50th Hunger Games. Directed by Francis Lawrence; cast includes Ralph Fiennes, Elle Fanning and Glenn Close. 12+.",
         meta=CM_META,
         p=CM_PRICE, img=CM + "63dfd810-9da2-4ff0-94b6-6b8fd3aa03d8.png", ph="Cinematica",
         badges=[("In English", "eng")], f=["film"]),
]

# ---------------------------------------------------------------- DANCE
DANCE = [
    dict(t="Alice in Wonderland", v="navoi", dates=["2026-11-07"], time="12:00",
         u="https://iticket.uz/en/events/theaters-tashkent/s-muhamedov-alisa-v-strane-chudes-skazka-balet",
         d="Ballet by S. Mukhamedov based on Lewis Carroll's story, combining classical and contemporary choreography. 3+.",
         p="77,000–220,000 UZS", img=IT + "9aFaAox6e71ak8LDEsfi37wl6bAq19WXz7d1rTPx.jpg",
         badges=[("Matinee", ""), ("Family", "")], f=["family"]),
    dict(t="The Firebird & Scheherazade", v="navoi", dates=["2026-11-07"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/istravinskii-zar-ptica-n-rimskii-korsakov-sexerazada-9460",
         d="Double bill of Stravinsky's The Firebird and Rimsky-Korsakov's Scheherazade.",
         p="77,000–220,000 UZS", img=IT + "FvJkI90rpzLeeblcDWq8bZW1Fl2moZEm7QxDuo0F.jpg", f=["ballet"]),
    dict(t="Romeo and Juliet (Prokofiev)", v="navoi", dates=["2026-11-13"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/sprokofev-romeo-i-dzuletta-balet-9464",
         d="Prokofiev's full-length ballet. 12+.",
         p="77,000–220,000 UZS", img=IT + "kfmwpzfbtneKSG9i2OaUAOfiOnZnzaY2oSF9cpRw.jpg", f=["ballet"]),
]

# ---------------------------------------------------------------- SPORT
SPORT = [
    dict(t="Pakhtakor vs Al-Nassr", v="pakhtakor", dates=["2026-11-02"], time="18:45",
         u="https://iticket.uz/en/events/sport/ppaalsr26",
         d="AFC Champions League Elite, league stage, matchday 4. Al-Nassr's squad includes Cristiano Ronaldo. E-tickets must be activated in the iTicket app; QR codes become active three hours before kick-off. Tickets are non-refundable.",
         p="100,000–3,000,000 UZS", img=IT + "cUkWIkcGYLjLFZybW6Z4Cy7vKLx2WSJlMelRlDqt.jpg",
         ph="Football", f=["football"]),
]

PAGES = [
    ("art", "Art", "Exhibition", [("free", "Free entry"), ("closing", "Closing in the next 30 days"), ("long", "Running longer")], ART),
    ("music", "Music", "Music", [("classical", "Classical & organ"), ("opera", "Opera"), ("crossover", "Film & crossover"),
                                 ("jazz", "Jazz, rock & world")], MUSIC),
    ("theatre", "Theatre & Film", "Theatre", [("stage", "Stage"), ("film", "Film"), ("family", "Family")], THEATRE),
    ("dance", "Dance", "Ballet", [("ballet", "Ballet"), ("family", "Family")], DANCE),
    ("sport", "Sport", "Sport", [("football", "Football")], SPORT),
]


def main():
    out = {}
    for key, name, label, tabs, items in PAGES:
        out[key] = build(key, name, label, tabs, items)
        print(key, len(out[key][2]))
    manifest = [{"cat": k, "t": it["t"], "u": it["u"], "img": it.get("img")} for k, (_, _, items) in out.items() for it in items]
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    return out


def build_site(dest="live"):
    """Standalone pages for GitHub Pages, embedded in Google Sites by URL.
    dest="live" writes to the repo root (what the site shows); dest="preview" writes to /preview/."""
    root = os.path.dirname(HERE)
    site = root if dest == "live" else os.path.join(root, "preview")
    os.makedirs(site, exist_ok=True)
    for key, name, *_ in PAGES:
        snip = open(os.path.join(OUT, f"{key}.html"), encoding="utf-8").read()
        page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} · Tashkent Expat Listings</title>
<style>html,body{{margin:0;background:#fff}}</style>
</head><body>
{snip}
</body></html>
"""
        with open(os.path.join(site, f"{key}.html"), "w", encoding="utf-8") as fh:
            fh.write(page)
    links = "".join(f'<li><a href="{k}.html">{n}</a></li>' for k, n, *_ in PAGES)
    with open(os.path.join(site, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tashkent Expat Listings</title><style>body{{font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:640px;margin:40px auto;padding:0 16px;color:#1f2937}}h1{{color:#1e3a5f}}a{{color:#1e3a5f}}</style></head>
<body><h1>Tashkent Expat Listings</h1><ul>{links}</ul></body></html>
""")
    if dest == "live":
        open(os.path.join(site, ".nojekyll"), "w").close()
    return site


if __name__ == "__main__":
    import sys
    main()
    print(build_site(sys.argv[1] if len(sys.argv) > 1 else "live"))
