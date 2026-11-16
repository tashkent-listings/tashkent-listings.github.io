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
RUN_DATE = "2026-11-16"   # set to the date of each refresh
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
    "azimut": ("AZIMUT Grand Hotel Tashkent", "AZIMUT Grand Hotel Tashkent, 107A Amir Temur Avenue"),
    "artikul": ("Studio Artikul 32", "Artikul 32, 34 Bogibuston Street, Tashkent"),
    "ichkari": ("ICHKARI museum", "41.2884310,69.2419630"),
    "anhor": ("Start: 2 Ankhor Embankment (near Urda)", "41.319756,69.266945"),
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
        if item.get("times"):   # different times on different days: {"2026-11-12": "19:30", ...}
            return "; ".join(f"{fmt_day(x)} · {item['times'].get(x.isoformat(), item.get('time', ''))}".rstrip(" ·")
                             for x in ds)
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
.tel-empty{grid-column:1/-1;font-size:.9rem;color:var(--tel-muted);margin:4px 0}
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
    if not items:   # nothing on sale in the window: a plain note instead of an empty grid and an "All (0)" tab
        tab_html = ""
        cards = '<p class="tel-empty">No events with tickets on sale for these dates yet.</p>'
    title = f"{name} · {title_range()}"
    tabs_div = f'<div class="tel-tabs" role="tablist">{tab_html}</div>\n' if tab_html else ""
    snippet = f"""<!-- Tashkent Expat Listings · {name} · updated {RUN_DATE} -->
<style>
{CSS}
</style>
<div class="tel" id="{cid}">
<div class="tel-head"><h2>{esc(title)}</h2></div>
{tabs_div}<div class="tel-grid">
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
    dict(t="Journey — Timur D'Vatz", v="andakulova", until="2026-11-18",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/12/dvatz-26", btn="Details (RU)",
         d="Solo exhibition by Timur D'Vatz, a graduate of the Royal Academy Schools and winner of the BP Portrait Award. The works draw on ancient history, medieval tapestry, Celtic mythology and alchemy.",
         p="Free", img=AF + "2026/10/bd41b11c9995d4502412ef202d7e7702_m.webp",
         badges=[("Free", "free"), ("Closes 18 Nov", "hot")], f=["closing", "free"]),
    dict(t="Book Graphics of Kydyrbay Nazhimov", v="library", until="2026-11-30",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/06/nazhimov", btn="Details (RU)",
         d="Book illustrations by Kydyrbay Nazhimov, mostly in scratchboard technique. A programme of children's workshops runs alongside; some sessions require registration.",
         meta="Daily 10:00–21:00. All ages.",
         p="Free", img=AF + "2026/10/a4adb19b8cda2b16bd2141bd10d86200_m.webp",
         badges=[("Free", "free"), ("Closes 30 Nov", "hot")], f=["closing", "free"]),
    dict(t="Chiroyli Vanitas — Elena Martynova", v="kinoxona", until="2026-11-30",
         u="https://www.afisha.uz/ru/cinema/2026/10/20/kinoxona", btn="Details (RU)",
         d="Solo photography exhibition by Elena Martynova at the kinoxona art cinema.",
         p="Free", img=AF + "2026/10/87bdc4dd60d4590b5cc0b123d321d9fd_m.webp",
         badges=[("Free", "free"), ("Photography", ""), ("Closes 30 Nov", "hot")], f=["closing", "free"]),
    dict(t="Life Beyond Measure — Zurab Tsereteli", v="nbu", until="2026-12-01",
         u="https://www.afisha.uz/ru/exhibitions/2026/08/13/vystavka-cereteli", btn="Details (RU)",
         d="Retrospective of Georgian-Russian artist Zurab Tsereteli (1934–2025): painting, sculpture, enamels, reliefs and silkscreens from across his career. Organised with the Russian Academy of Arts.",
         meta="Tue–Sat 10:00–17:00 (closed Sun and Mon).",
         p="10,000–50,000 UZS (gallery entry)", img=AF + "2026/08/e1de191d47cac18a0f69fa7b49556130_m.webp",
         badges=[("Closes 1 Dec", "hot")], f=["closing"]),
    dict(t="San'at Up", v="goethe", until="2026-12-12",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/01/sanatup-gi", btn="Details (RU)",
         d="Works by young artists from Uzbekistan and Tajikistan selected through the San'at Up competition, displayed in the institute's stairwell.",
         meta="10:00–19:00.",
         p="Free", img=AF + "2026/09/1057ff60173b79351bfeccab600fafd4_m.webp",
         badges=[("Free", "free")], f=["closing", "free"]),
    dict(t="Interflows", v="artepa", until="2026-12-15",
         u="https://www.afisha.uz/ru/exhibitions/2026/09/28/interflows", btn="Details (RU)",
         d="Exhibition on water in Central Asia and its ecological, political and social dimensions, by the DAVRA research group and Art Station. Includes work by young artists from the region and Saodat Ismailova's film Stains of Oxus. The display changes during the run.",
         p="Free", img=AF + "2026/09/54a3063a884452f9b882db8ad30cca41_m.webp",
         badges=[("Free", "free")], f=["closing", "free"]),
    dict(t="Savitsky's Diaries: Old and New", v="tcm", until="2027-01-24",
         u="https://iticket.uz/en/events/cultural-events/savitskys-diaries-old-and-new-2027",
         d="Multimedia exhibition combining painting, music, light and movement, about Igor Savitsky, founder of the Karakalpakstan State Museum of Art in Nukus. Organised by ACDF; curated by Aziza Izamova.",
         meta="Mon–Thu 10:00–23:00, Fri–Sun 10:00–00:00. 40,000 UZS Mon–Wed, 60,000 UZS Fri–Sun; free on Thursdays (no booking, first come first served). Half price for schoolchildren, students and pensioners at the iTicket box office; children under 10 free.",
         p="40,000–60,000 UZS (free on Thursdays)", img=IT + "PTE7PbtrvTfKwsFKxbi0SNnBL54hk4N35ezAPdCa.jpg",
         badges=[("Multimedia", "")], f=["long"]),
    dict(t="Yalt-Yult (Radiance)", v="ichkari", until="2027-02-06",
         u="https://www.afisha.uz/ru/exhibitions/2026/09/17/yaltyult", btn="Details (RU)",
         d="The ICHKARI museum's first temporary exhibition looks at conspicuous luxury in Uzbek culture and how ideas of status, beauty and making an impression changed over three eras. On show are mirrors, historical chapan robes, jewellery and other objects that once signalled their owners' standing.",
         meta="Daily 11:00–20:00.",
         p="60,000 UZS", img=AF + "2026/11/52e995473698d4d67735dfea995166f3_m.webp", f=["long"]),
    dict(t="Keramistan", v="artikul", dates=["2026-11-28", "2026-11-29"], time="11:00",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/19/keramistan", btn="Details (RU)",
         d="Ceramics expo-market: 14 studios and makers show work made around this edition's theme, the labyrinth. All pieces are for sale.",
         meta="Opens at 11:00 on both days.",
         p="Free", img=AF + "2026/10/22330fbcdc047af2aec8c9c6dfd9375e_m.webp",
         badges=[("Free", "free"), ("Two days", "")], f=["free"]),
    dict(t="Hikmah", v="cca", until="2027-01-31",
         u="https://ccat.uz/en/programme/hikmah-exhibition", btn="Details",
         d="Opening exhibition of the Centre for Contemporary Arts Tashkent: new commissions and recent works by Uzbek and international artists on wisdom, spirit and the transformation of matter. The centre occupies a restored 1912 diesel power station.",
         meta="The centre is closed 10–20 November.",
         p="Free", img=AF + "2026/08/8d19dc8eb2f5bc2b8c6e6ec1aa41ccb7_m.webp",
         badges=[("Free", "free"), ("Closed 10–20 Nov", "hot")], f=["long", "free"]),
]

# ---------------------------------------------------------------- MUSIC
MUSIC = [
    dict(t="Bach keyboard concertos — Conservatory Student Orchestra", v="cons", vlabel="State Conservatory (Grand Hall)",
         dates=["2026-11-17"], time="19:00",
         u="https://iticket.uz/en/events/concerts/isbax-koncert-studenceskogo-orkestra-gkuz-9841",
         d="The Conservatory's student orchestra, conductor Eldar Azimov, plays four Bach concertos for one, two and three keyboards (BWV 1056, 1060, 1063 and 1064). Soloists Elnura Mirzakamalova, Vasila Umarova and Luiza Kabdurakhmanova. 14+.",
         p="66,000–88,000 UZS", img=IT + "CuTQ5W1ddJUynEJuCWNT6pWkrnoKQc37mPDJGwjv.jpg", f=["classical"]),
    dict(t="A Journey through Organ Music: Eras and Styles", v="cons", dates=["2026-11-21"], time="19:00",
         u="https://iticket.uz/en/events/concerts/putesestvie-v-mir-organnoi-muzyki-epoxi-i-stili-9852",
         d="Organ recital by Munira Aminova and Bobir Mirsaidov of the Conservatory, from the Baroque onwards: works by Nivers, Bach, Liszt, Guilmant and Reger. 12+.",
         p="110,000–165,000 UZS", img=IT + "ATSzEziOKabGrTWFh1k6Go6iedj1sPGDo34hwU9s.jpg",
         badges=[("Few seats left", "hot")], f=["classical"]),
    dict(t="From the New World — National Symphony Orchestra", v="turkiston", dates=["2026-11-23"], time="19:00",
         u="https://iticket.uz/en/events/concerts/iz-novogo-sveta",
         d="Conductor Boburjon Kurbonaliev. Rachmaninoff, The Rock; Haydn, Cello Concerto (soloist Sardor Ibragimov); Dvořák, Symphony No. 9.",
         p="77,000–132,000 UZS", img=IT + "z0GYzQJ9cHD0T1MzrklNNRhWmu8laRf9eagfe1OX.jpg", f=["classical"]),
    dict(t="Palette of the 20th Century — chamber music", v="cons", dates=["2026-11-26"], time="19:00",
         u="https://iticket.uz/en/events/concerts/palitra-xx-veka-koncert-kamernoi-muzyki-9738",
         d="Chamber concert by soloists and teaching staff of the Conservatory: works by Shostakovich, Shchedrin, Schoenberg, Bloch, Zwaag, Bozza, Cage, Ireland and Piazzolla. 14+.",
         p="66,000 UZS", img=IT + "t27bwcqt2JyQIpA1MwAa8thQ07wzZtR4YLyc99qt.jpg", f=["classical"]),
    dict(t="Choir of the State Symphony Orchestra — 10th anniversary", v="cons", vlabel="State Conservatory (Grand Hall)",
         dates=["2026-11-27"], time="19:00",
         u="https://iticket.uz/en/events/concerts/yubileinyi-koncert-xora-pri-gosudarstvennom-simfoniceskom-orkestre-uzbekistana-9860",
         d="The choir of the State Symphony Orchestra of Uzbekistan marks ten years with a mixed choral programme: classical works, well-known popular pieces and music from several eras. Choirmaster Yulduz Khusnitdinova; artistic director Kamoliddin Urinbaev. 12+.",
         p="55,000–88,000 UZS", img=IT + "9iRwCiyrVdm1HPUM0zbL7hGvlyBAuEkfRXEmEFzc.jpg", f=["classical"]),
    dict(t="Conservatory 90th anniversary — vocal concert", v="cons", vlabel="State Conservatory (Organ Hall)",
         dates=["2026-12-01"], time="18:00",
         u="https://iticket.uz/en/events/concerts/koncert-klassa-professora-kasymovoi-mb-9858",
         d="Classical vocal concert for the 90th anniversary of the State Conservatory. Navoi Theatre soloists, including Kirill Borchaninov, Doniyor Alimov and Gulnar Aldzhanova, sing pieces from the international repertoire, accompanied by piano students from Professor Malika Kasymova's class. 12+.",
         p="66,000 UZS", img=IT + "xHWMrBeDmydLcEe731xElM7IZuBqIA5pRkVHhrPE.jpg", f=["classical"]),
    dict(t="Time of Classics — National Symphony Orchestra", v="turkiston", dates=["2026-12-02"], time="19:00",
         u="https://iticket.uz/en/events/concerts/vremya-klassiki",
         d="Conductor Boburjon Kurbonaliev. Sibelius, Valse triste and Symphony No. 2; Prokofiev, Piano Concerto No. 1 (soloist Nikita Stetsenko). 12+.",
         p="77,000–132,000 UZS", img=IT + "So5NetFzvGxqCrpb9lCevdbFWVu4acgZ6wo0YpLS.jpg", f=["classical"]),
    dict(t="The Four Seasons: Vivaldi & Piazzolla", v="cons", vlabel="State Conservatory (Organ Hall)",
         dates=["2026-12-04"], time="19:00",
         u="https://iticket.uz/en/events/concerts/vremena-goda-vivaldi-and-pyaccola",
         d="Turkiston Chamber Orchestra, conductor Muborak Lutfullaeva, plays Vivaldi's The Four Seasons alongside Piazzolla's The Four Seasons of Buenos Aires. 12+.",
         p="66,000–275,000 UZS", img=IT + "fHffwdF0Kwggb0SdTyd1sZIijFxBef0CLQzQKaWN.jpg", f=["classical"]),
    dict(t="Vienna Strauss Philharmonie Orchestra", v="panorama", dates=["2026-12-14"], time="18:30",
         u="https://showgo.uz/en/session/1285-vienna-strauss-philharmonie-orchestra-2026",
         d="First Tashkent concert by this Vienna orchestra, founded in 2014, touring with 27 musicians under conductor András Deák. Programme of Mozart, Brahms, Offenbach, Rossini, Kálmán and the Strauss family. About 1 hr 45 min. 7+.",
         p="From 200,000 UZS", img=AF + "2026/09/1a0d594804090e4f91bb27a4fc88e5c2_m.webp", f=["classical"]),
    dict(t="Rachmaninoff, Liszt & Bizet — piano duo", v="cons", vlabel="State Conservatory (Organ Hall)",
         dates=["2026-12-14"], time="18:30",
         u="https://www.afisha.uz/ru/concerts/2026/11/11/piano-duet-concert", btn="Details (RU)",
         d="Ilgiz Royanov and Nikita Stetsenko on two pianos: Liszt's Reminiscences of Don Juan, Rachmaninoff's Suite No. 2 and Symphonic Dances, and Anderson's fantasy on themes from Bizet's Carmen.",
         p="60,000 UZS", img=AF + "2026/11/cc4be8e917e521196d4c88f4814120be_m.webp", f=["classical"]),
    dict(t="Candle Fire: Neo × Classic — Bravo Orchestra", v="turkiston", dates=["2026-11-17"], time="19:30",
         u="https://showgo.uz/en/session/1428-cinema-music-tashkent",
         d="Candlelit concert by Bravo Orchestra pairing classical pieces by Vivaldi, Mozart, Schubert, Rachmaninoff and Verdi with neoclassical music by Ludovico Einaudi, Gibran Alcocer and Jamie Duffy. About 1 hr 40 min. 7+.",
         meta="Latecomers may be refused entry more than 10 minutes after the start.",
         p="From 197,000 UZS", img=SG + "2026/11/cropped_20261112011233_bhew_Candle_Fire_NEO_x_Classic_17-11.jpg",
         pos="center 40%", f=["crossover"]),
    dict(t="MICHAEL: Legendary Hits — Turkiston Chamber Orchestra", v="turkiston", dates=["2026-11-25"], time="19:00 & 21:30",
         u="https://iticket.uz/en/events/concerts/michael-legendarnye-hity",
         d="Orchestral arrangements of Michael Jackson songs, including Billie Jean, Bad, Smooth Criminal, Thriller and Black or White. Two performances.",
         p="66,000–275,000 UZS", img=None, f=["crossover"]),
    dict(t="Tribute to Andrea Bocelli — National Symphony Orchestra", v="turkiston", dates=["2026-12-11"], time="19:00",
         u="https://iticket.uz/en/events/concerts/posvyashenie-andrea-bocelli",
         d="The National Symphony Orchestra, conductor Boburjon Kurbonaliev, plays instrumental arrangements of songs and arias associated with the Italian tenor Andrea Bocelli. All ages.",
         p="66,000–220,000 UZS", img=IT + "CR0GLGdIyKLYIQb1spAO5AZ01cReackxDs4EYFwk.jpg", f=["crossover"]),
    dict(t="New Year Concert — Tynda Music", v="panorama", dates=["2026-12-12"], time="19:00",
         u="https://iticket.uz/en/events/concerts/novogodnij-koncert2026",
         d="Tynda Music's chamber orchestra plays Christmas and New Year favourites, including Jingle Bells, Let It Snow and White Christmas. 5+.",
         p="150,000–800,000 UZS", img=None, f=["crossover"]),
    dict(t="Anime soundtracks — Turkiston Chamber Orchestra", v="turkiston", dates=["2026-12-13"], time="19:00",
         u="https://iticket.uz/en/events/concerts/anime-saundtrek-koncert",
         d="The Turkiston Chamber Orchestra plays music from anime series and films, including Attack on Titan, Jujutsu Kaisen, Demon Slayer, Naruto, Death Note, Chainsaw Man, One Piece and the films of Hayao Miyazaki. All ages.",
         p="66,000–275,000 UZS", img=IT + "13UmiJNzYAemb1yYWH258QRJ0MOUcYqQHIjS6Qup.jpg", f=["crossover"]),
    dict(t="Un ballo in maschera (Verdi)", v="navoi", dates=["2026-11-19"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/dz-verdi-bal-maskarad-opera-9722",
         d="Verdi's opera, performed in two acts. 12+.",
         p="55,000–165,000 UZS", img=IT + "WOy6jtjahKm8mZ4MdjV0xelCSyJ7nPxPF9xP22sf.jpg", f=["opera"]),
    dict(t="La Bohème (Puccini)", v="navoi", dates=["2026-11-21"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/dz-puccini-bogema-opera-9723",
         d="Puccini's opera, with the State Symphony Orchestra of Uzbekistan. 6+.",
         p="55,000–165,000 UZS", img=IT + "ok42kDVwpppAvn3JKiSd34hNxS6acPYoJyqEjkqy.jpg", f=["opera"]),
    dict(t="Carmen (Bizet)", v="navoi", dates=["2026-11-22"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/zhorzh-bize-karmen-opera",
         d="Bizet's opera in a new production by Konstantin Kamynin, set in Spain in the 1940s–50s. 12+.",
         p="110,000–330,000 UZS", img=IT + "7RbkOlmye0oScrRN9hN56Wk0T8Tts88LNsfK3sjA.jpg",
         badges=[("New production", "new")], f=["opera"]),
    dict(t="Modern Jazz — State Jazz Orchestra", v="turkiston", dates=["2026-11-24"], time="19:00",
         u="https://iticket.uz/en/events/concerts/modern-jazz",
         d="The State Jazz Orchestra of Uzbekistan under Mansur Tashmatov in a big-band programme: pieces from the repertoire of Gordon Goodwin's Big Phat Band, Earth, Wind & Fire funk, and standards including Autumn Leaves and L-O-V-E. Singers Sevara Tulanova and Mukhamedali Dzhuraev, and Elbek Artykov's vocal group Tashkent Band.",
         p="66,000–275,000 UZS", img=IT + "GE4FeKC4mf4rLoqvMhs8dW6pJUExa0NrvOQysnHy.jpg", f=["jazz"]),
    dict(t="KALEO", v="humo", dates=["2026-11-27"], time="19:00",
         u="https://showgo.uz/en/session/1165-kaleo-live-in-tashkent",
         d="Icelandic blues-rock band, on a tour marking ten years since their debut album A/B. 16+.",
         p="From 250,000 UZS", img=None, f=["jazz"]),
    dict(t="Rock Concert — Tynda Music", v="turkiston", dates=["2026-11-28"], time="19:00",
         u="https://iticket.uz/en/events/concerts/rock-consert20",
         d="Almaty band Tynda Music plays rock hits from the 1970s to the 2000s, including Led Zeppelin, AC/DC, Pink Floyd, Queen, Metallica, Nirvana and Linkin Park, with classical instruments joining the band. About 90 minutes. No entry under 5; children from 5 need their own ticket.",
         p="410,000–530,000 UZS", img=IT + "64GN5A6zFttXbAzbuiaurK2uz7kCHkEqzkEBzA1Y.jpg", f=["jazz"]),
    dict(t="Toki Telpak-Furushon — Meros ensemble", v="ilkhom", dates=["2026-12-08"], time="19:00",
         u="https://ilkhom.com/events/muzykalno-tvorcheskij-vecher-fleshbeki/", btn="Details & tickets",
         d="Meros combines Central Asian traditional music with jazz improvisation, classical writing and electronics, and builds each programme around a historic building in Uzbekistan; this one takes the Toki Telpak-Furushon trading dome in Bukhara. With Yasmina Omar-Mun (vocals), Mamurjon Pulatov (vocals, sato, dutar), Sherzod Nazarov (doira, percussion), Sanjar Nafikov (keyboards) and Sukhrob Nazimov (winds, electronics). 1 hr 30 min, 14+.",
         p="170,000–210,000 UZS", img=None, ph="Ilkhom", f=["jazz"]),
]

# ---------------------------------------------------------------- THEATRE & FILM
CM = "https://cinematica.uz/uploads/movies/"
CM_META = "English-language screenings in 2D, no subtitles. Showtimes are published a few days before."
CM_PRICE = "35,000–70,000 UZS (standard halls)"
THEATRE = [
    dict(t="Charlie and the Sea Lions", v="circus", range=["2026-10-31", "2026-12-06"],
         u="https://showgo.uz/en/session/1407-tsirk-charli-i-morskie-lvy-tashkent-2026",
         d="Circus programme at the State Circus opening the new season: a sea lion act, clown Charlie from Germany, and about 30 aerialists, acrobats, jugglers and equilibrists. About 2 hours. Runs until 6 December.",
         p="70,000–350,000 UZS", img=SG + "2026/10/cropped_20261028071204_lbjl_photo_2026-10-28_12-10-55.jpg",
         pos="center 30%", ph="Circus", badges=[("Visual show", "eng")], f=["stage", "family"]),
    dict(t="Great Silk Road International Circus Festival", v="circus",
         dates=["2026-11-25", "2026-11-26", "2026-11-27"], time="17:00",
         u="https://iticket.uz/en/events/concerts/international-circus-festival-the-great-silk-road",
         d="International circus festival at the State Circus with performers from more than ten countries, including Uzbekistan, Mexico, Malaysia, Spain, Hungary, Russia, Kazakhstan and Kyrgyzstan: acrobats, gymnasts and animal acts. 3+.",
         p="150,000–350,000 UZS", img=IT + "hCvfuExjBEG21UkOWIk653JEqpTZyNmbd9jQ3CqD.jpg",
         ph="Circus", badges=[("Visual show", "eng")], f=["stage", "family"]),
    dict(t="Shadows of My House — audio play", v="ichkari", range=["2026-11-02", "2026-11-30"],
         u="https://www.afisha.uz/ru/gorod/2026/09/23/teni-doma", btn="Details & tickets (RU)",
         d="Audio play that accompanies the ICHKARI museum's exhibition. Visitors move through an old family house as the main character, a woman who grew up there, recalls the house, old Tashkent and its customs. About 2 hours.",
         meta="Audio available in English, Uzbek and Russian. Listed daily 2–30 November; choose a date when booking.",
         p="60,000 UZS", img=AF + "2026/10/c99a63573a6751860f4419f09cbd5d7f_m.webp", pos="center 35%", ph="ICHKARI",
         badges=[("In English", "eng")], f=["stage"]),
    dict(t="Tashkent Speaks — audio walk", v="anhor", range=["2026-11-17", "2026-11-30"],
         u="https://iticket.uz/en/events/cultural-events/walk-around-tashkent-tashkent-speaks",
         d="Audio performance on foot. Wearing headphones, the group walks 3.5 km from the Ankhor canal past the specialists' houses, along Navoi Street, across Mustaqillik Square and past the Romanov Palace, the History Museum and the Navoi Theatre to the Lotte Hotel, listening to a soundtrack built from the stories and voices of Tashkent residents. 1 hr 40 min, 7+.",
         meta="Daily at 10:00, and at 17:00 on most days. Audio in Russian or English; for English, tell the organisers by phone when booking. Tickets can't be moved to another date.",
         p="180,000 UZS", img=IT + "KBcUuwDsQCKJyilWXKEL4wilVZe9WODzEmqxlZsC.jpg", ph="Audio walk",
         badges=[("English on request", "eng")], f=["stage"]),
    dict(t="Underground Girls", v="ilkhom", dates=["2026-12-09"], time="19:00",
         u="https://ilkhom.com/events/podpolnye-devochki-eng-subs/", btn="Details & tickets",
         d="Production by Polish director Jakub Skrzywanek, drawing on Jenny Nordberg's book The Underground Girls of Kabul and on interviews with Afghan women who left the country or stayed after August 2021. It looks at freedom and the denial of women's rights. 1 hr 15 min, 16+.",
         meta="Performed in Russian with English surtitles.",
         p="280,000–330,000 UZS", img=AF + "2026/11/5f70c8ec1353aa8068e47ade77dc628f_m.webp", ph="Ilkhom",
         badges=[("English surtitles", "eng")], f=["stage"]),
    dict(t="Seven Moons", v="ilkhom", dates=["2026-12-13"], time="19:00",
         u="https://ilkhom.com/events/sem-lun-eng-subs/", btn="Details & tickets",
         d="Sufi parable after Alisher Navoi about a shah who loses everything through pride. Directed by Vladimir Pankov with the Moscow studio SounDrama, combining Eastern music and dance with Western rhythms. 1 hr 45 min, 16+.",
         meta="Performed in Russian with English surtitles.",
         p="280,000–330,000 UZS", img=AF + "2026/11/02b0b9a0fbbc9023cd50372e66b39b01_m.webp", ph="Ilkhom",
         badges=[("English surtitles", "eng"), ("Live music", "")], f=["stage"]),
    dict(t="The Hunger Games: Sunrise on the Reaping", v="cinematica", opens="2026-11-19",
         u="https://cinematica.uz/movies/1071", btn="Details",
         d="Prequel set 24 years before the original trilogy, in which a young Haymitch Abernathy competes in the 50th Hunger Games. Directed by Francis Lawrence; cast includes Ralph Fiennes, Elle Fanning and Glenn Close. 12+.",
         meta=CM_META,
         p=CM_PRICE, img=None, ph="Cinematica",
         badges=[("In English", "eng")], f=["film"]),
]

# ---------------------------------------------------------------- DANCE
DANCE = [
    dict(t="Cinderella (Prokofiev)", v="navoi", dates=["2026-11-28", "2026-11-29"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/s-prokofev-zolushka-balet-26",
         d="Prokofiev's full-length ballet based on the Cinderella fairy tale. 3+.",
         p="110,000–330,000 UZS", img=IT + "Il3RccNa4FieiPxvMPpTldE29ojI6dD5WWACz78F.jpg",
         badges=[("Family", "")], f=["ballet", "family"]),
    dict(t="Swan Lake — Saint Petersburg Ballet", v="panorama", dates=["2026-12-04"], time="19:00",
         u="https://iticket.uz/en/events/concerts/lebedinoe-ozero2027",
         d="The touring Saint Petersburg Ballet, with soloists from the Mariinsky and Mikhailovsky theatres, opens a three-day Tashkent visit with Tchaikovsky's ballet. Special guest Farukh Ruzimatov, with Navoi Theatre principal Daniyar Khasmanov. 5+.",
         meta="Danced to recorded music.",
         p="150,000–600,000 UZS", img=IT + "wGFwhDp95r1i4aEEGD6HHb5wMGPQhWun3lsxE80X.jpg", f=["ballet"]),
    dict(t="The Nutcracker — Saint Petersburg Ballet", v="panorama", dates=["2026-12-05", "2026-12-06"],
         times={"2026-12-05": "14:00 & 19:00", "2026-12-06": "14:00"},
         u="https://iticket.uz/en/events/concerts/shelkunchik226",
         d="Tchaikovsky's Christmas ballet, performed by the touring Saint Petersburg Ballet with soloists from the Mariinsky and Mikhailovsky theatres. Three performances. 6+.",
         meta="Danced to recorded music.",
         p="100,000–600,000 UZS", img=IT + "hj9JhYbJ1wk12C8z0tFpC9BJWEGMxJNckKnvRlAv.jpg",
         badges=[("Family", "")], f=["ballet", "family"]),
    dict(t="Best of World Ballet — Saint Petersburg Ballet gala", v="panorama", dates=["2026-12-06"], time="19:00",
         u="https://iticket.uz/en/events/concerts/gala-koncert-luchshee-iz-mirovogo-baleta26",
         d="Closing gala of the Saint Petersburg Ballet's Tashkent visit: well-known numbers from the classical ballet repertoire. 6+.",
         meta="Danced to recorded music.",
         p="250,000–650,000 UZS", img=IT + "8dEbNBY6ExeresBI0FPwXkus21jRqWNYucoqowP8.jpg", f=["ballet"]),
    dict(t="The Legend of Romeo and Juliet — flamenco show", v="rusdrama", dates=["2026-12-08"], time="19:00",
         u="https://showgo.uz/en/session/1378-romeo-juliet-romeo-i-dzhuletta-legendarnaia-istoriia-liubvi-rasskazannaia-na-iazyke-tantsa-flamenko-shou",
         d="The Spanish company Flamenco Live tells Shakespeare's story through flamenco dance, with live guitar and singing. About 1 hr 30 min.",
         p="From 150,000 UZS", img=SG + "2026/10/cropped_20261022140800_gmed_FLAMENCO_2026__10801350.jpg",
         pos="center 30%", ph="Flamenco", f=["flamenco"]),
    dict(t="The Nutcracker (Tchaikovsky)", v="turkiston", dates=["2026-12-16", "2026-12-17"], time="19:00",
         u="https://showgo.uz/en/session/1375-skazochnyi-balet-v-dvukh-deistviiakh-shchelkunchik-p-i-chaikovskii-i-libretto-m-petipa",
         d="Tchaikovsky's Christmas ballet in two acts, after Petipa's libretto, in a 1 hr 30 min version. The organisers don't name the company. 3+.",
         meta="Also on Thursday 17 December.",
         p="From 150,000 UZS", img=AF + "2026/10/4f037d3b5780c90e2dcc4c1f73c3c0f0_m.webp",
         badges=[("Family", "")], f=["ballet", "family"]),
]

# ---------------------------------------------------------------- SPORT
SPORT = [
    # Nothing on sale for 16 Nov – 16 Dec 2026. Held back until tickets are published:
    # Pakhtakor vs Tractor (AFC Champions League Elite), Pakhtakor Stadium, Mon 7 Dec 18:45 (iTicket, not yet on sale);
    # World Boxing Cup Finals, Tashkent, 26 Nov – 4 Dec (no venue or tickets announced).
]

PAGES = [
    ("art", "Art", "Exhibition", [("free", "Free entry"), ("closing", "Closing in the next 30 days"), ("long", "Running longer")], ART),
    ("music", "Music", "Music", [("classical", "Classical"), ("opera", "Opera"), ("crossover", "Film & crossover"),
                                 ("jazz", "Jazz, rock & world")], MUSIC),
    ("theatre", "Theatre & Film", "Theatre", [("stage", "Stage"), ("film", "Film"), ("family", "Family")], THEATRE),
    ("dance", "Dance", "Ballet", [("ballet", "Ballet"), ("flamenco", "Flamenco"), ("family", "Family")], DANCE),
    ("sport", "Sport", "Sport", [("football", "Football")], SPORT),
]


# ---------------------------------------------------------------- CALENDAR (day by day, all categories)
CAL_CSS = """
.tel-day{margin:0 0 18px}
.tel-day h3{font-size:1rem;color:var(--tel-navy);margin:0 0 8px}
.tel-day h3{padding:0 0 6px;border-bottom:2px solid var(--tel-line)}
.tel-day h3 .tel-today{display:none;margin-left:8px;background:var(--tel-gold);color:#fff;font-size:.7rem;padding:2px 8px;border-radius:999px;vertical-align:middle}
.tel-day.is-today h3 .tel-today{display:inline-block}
.tel-row{display:grid;grid-template-columns:62px 1fr;gap:10px;padding:8px 0;border-bottom:1px solid var(--tel-line)}
.tel-row:last-child{border-bottom:0}
.tel-row[hidden],.tel-day[hidden]{display:none}
.tel-time{font-size:.85rem;font-weight:700;color:var(--tel-navy);padding-top:1px}
.tel-row .tel-title{font-size:.95rem;margin:0 0 3px}
.tel-row .tel-badge{display:inline-block;margin-left:6px;vertical-align:1px;box-shadow:none;background:var(--tel-chip)}
.tel-row .tel-badge.eng{background:#1d4ed8;color:#fff}
.tel-row .tel-badge.free{background:#15803d;color:#fff}
.tel-row .tel-badge.hot{background:#b91c1c;color:#fff}
.tel-row .tel-badge.new{background:var(--tel-gold);color:#fff}
.tel-line2{font-size:.8rem;color:var(--tel-muted);display:flex;flex-wrap:wrap;gap:4px 12px;align-items:center}
.tel-line2 a{color:var(--tel-gold);text-decoration:none;font-weight:600}
.tel-line2 a:hover{text-decoration:underline}
.tel-cat{font-weight:700;color:var(--tel-ink)}
.tel-cat:before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;background:var(--c,#94a3b8)}
.tel-cat.art{--c:#7c3aed}.tel-cat.music{--c:#1d4ed8}.tel-cat.theatre{--c:#b91c1c}.tel-cat.dance{--c:#db2777}.tel-cat.sport{--c:#15803d}
""".strip()

# Hides days that have passed (Tashkent time) and handles the category tabs.
CAL_JS = """(function(){var r=document.getElementById('tel-calendar');if(!r)return;
var now=new Date(Date.now()+5*36e5).toISOString().slice(0,10);
var days=r.querySelectorAll('.tel-day');for(var i=0;i<days.length;i++){var dd=days[i].getAttribute('data-day');if(dd<now){days[i].remove();}else if(dd===now){days[i].classList.add('is-today');}}
var tabs=r.querySelectorAll('.tel-tab');
function apply(t){var rows=r.querySelectorAll('.tel-row');for(var k=0;k<rows.length;k++){rows[k].hidden=!(t==='all'||rows[k].getAttribute('data-f')===t);}
var groups=r.querySelectorAll('.tel-day');for(var g=0;g<groups.length;g++){groups[g].hidden=!groups[g].querySelector('.tel-row:not([hidden])');}}
for(var i=0;i<tabs.length;i++){tabs[i].addEventListener('click',function(){for(var j=0;j<tabs.length;j++){tabs[j].classList.remove('on');tabs[j].setAttribute('aria-selected','false');}this.classList.add('on');this.setAttribute('aria-selected','true');apply(this.getAttribute('data-f'));});}
apply('all');})();"""

SHORT_RUN_DAYS = 7   # ranges under a week are shown on each day; longer runs are left off the calendar


def cal_row(cat, catname, it, time_txt, extra=""):
    badges = "".join(
        f'<span class="tel-badge {cls}">{esc(txt)}</span>'
        for txt, cls in it.get("badges", [])
        if not txt.startswith("Closes") and not txt.endswith("performances")
    )
    vname = V[it["v"]][0] if it["v"] in V else it["v"]
    vlabel = it.get("vlabel", vname)
    m = maps(it["v"]) if it["v"] in V else None
    venue = (f'<a href="{esc(m)}" target="_blank" rel="noopener" title="Open in Google Maps">📍 {esc(vlabel)}</a>'
             if m else f"<span>📍 {esc(vlabel)}</span>")
    return (f'<div class="tel-row" data-f="{cat}"{extra}><div class="tel-time">{esc(time_txt)}</div><div>'
            f'<h4 class="tel-title"><a href="{esc(it["u"])}" target="_blank" rel="noopener">{esc(it["t"])}</a>{badges}</h4>'
            f'<div class="tel-line2"><span class="tel-cat {cat}">{esc(catname)}</span>{venue}<span>{esc(it["p"])}</span></div>'
            f'</div></div>')


def build_calendar():
    days = {}
    for cat, catname, _label, _tabs, items in PAGES:
        for it in filter(None, (in_window(i) for i in items)):
            if "until" in it or "opens" in it:
                continue   # exhibitions and Cinematica film runs stay on their own pages only
            elif "range" in it:
                a, b = d(it["range"][0]), d(it["range"][1])
                if (b - a).days >= SHORT_RUN_DAYS:
                    continue   # long runs (e.g. the circus) stay on their own page only
                x = max(a, TODAY)
                while x <= min(b, WINDOW_END):
                    days.setdefault(x.isoformat(), []).append((it.get("time", "99"), cat, catname, it, it.get("time", "")))
                    x += dt.timedelta(days=1)
            else:
                for x in it["dates"]:
                    tt = it.get("times", {}).get(x, it.get("time", ""))
                    days.setdefault(x, []).append((tt or "99", cat, catname, it, tt))
    present = {cat for v in days.values() for _, cat, *_ in v}
    tab_html = '<button class="tel-tab on" data-f="all" role="tab" aria-selected="true">All</button>'
    for cat, catname, *_ in PAGES:
        if cat in present:
            tab_html += f'<button class="tel-tab" data-f="{cat}" role="tab" aria-selected="false">{esc(catname)}</button>'
    day_html = ""
    for day in sorted(days):
        x = d(day)
        rows = "".join(cal_row(cat, catname, it, tt)
                       for _, cat, catname, it, tt in sorted(days[day], key=lambda e: (e[0], e[3]["t"])))
        day_html += (f'<section class="tel-day" data-day="{day}"><h3>{x.strftime("%A")} {x.day} {x.strftime("%B")}'
                     f'<span class="tel-today">Today</span></h3>{rows}</section>')
    title = f"Calendar · {title_range()}"
    snippet = f"""<!-- Tashkent Expat Listings · Calendar · updated {RUN_DATE} -->
<style>
{CSS}
{CAL_CSS}
</style>
<div class="tel" id="tel-calendar">
<div class="tel-head"><h2>{esc(title)}</h2></div>
<div class="tel-tabs" role="tablist">{tab_html}</div>
{day_html}
</div>
<script>{CAL_JS}</script>
"""
    with open(os.path.join(OUT, "calendar.html"), "w", encoding="utf-8") as fh:
        fh.write(snippet)
    return sum(len(v) for v in days.values())


def main():
    out = {}
    for key, name, label, tabs, items in PAGES:
        out[key] = build(key, name, label, tabs, items)
        print(key, len(out[key][2]))
    print("calendar (day entries)", build_calendar())
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
    for key, name in [("calendar", "Calendar")] + [(p[0], p[1]) for p in PAGES]:
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
    links = '<li><a href="calendar.html">Calendar</a></li>' + "".join(f'<li><a href="{k}.html">{n}</a></li>' for k, n, *_ in PAGES)
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
