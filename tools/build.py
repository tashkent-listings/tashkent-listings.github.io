#!/usr/bin/env python3
"""Build embeddable HTML snippets for Tashkent Expat Listings (November 2026)."""
import datetime as dt
import html
import json
import os
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
CHECKED = "31 Oct 2026"

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
.tel-head p{margin:0;font-size:.85rem;color:var(--tel-muted)}
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
.tel-sub{grid-column:1/-1;margin:10px 0 0;font-size:1.05rem;color:var(--tel-navy);border-top:1px dashed var(--tel-line);padding-top:14px}
.tel-note{font-size:.76rem;color:var(--tel-muted);margin:16px 0 0}
""".strip()

JS = """(function(){var r=document.getElementById('%s');if(!r)return;var tabs=r.querySelectorAll('.tel-tab'),cards=r.querySelectorAll('.tel-card,.tel-sub');for(var i=0;i<tabs.length;i++){tabs[i].addEventListener('click',function(){var t=this.getAttribute('data-f');for(var j=0;j<tabs.length;j++){tabs[j].classList.remove('on');tabs[j].setAttribute('aria-selected','false');}this.classList.add('on');this.setAttribute('aria-selected','true');for(var k=0;k<cards.length;k++){var c=cards[k].getAttribute('data-f')||'';cards[k].hidden=!(t==='all'||(' '+c+' ').indexOf(' '+t+' ')>-1);}});}})();"""


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


def build(key, title, subtitle, label, tabs, items, extra_sections=None, note_extra=""):
    cid = f"tel-{key}"
    items = sorted(items, key=sort_key)
    counts = {f: sum(1 for i in items if f in i["f"]) for f, _ in tabs}
    extra_items = []
    for sec in extra_sections or []:
        extra_items += sec["items"]
    tab_html = f'<button class="tel-tab on" data-f="all" role="tab" aria-selected="true">All <span>({len(items) + len(extra_items)})</span></button>'
    for f, name in tabs:
        n = counts[f] + sum(1 for i in extra_items if f in i["f"])
        tab_html += f'<button class="tel-tab" data-f="{f}" role="tab" aria-selected="false">{esc(name)} <span>({n})</span></button>'
    cards = "\n".join(card(i, label) for i in items)
    for sec in extra_sections or []:
        fs = " ".join(sorted({f for i in sec["items"] for f in i["f"]}))
        cards += f'\n<h3 class="tel-sub" data-f="{fs}">{esc(sec["title"])}</h3>\n'
        cards += "\n".join(card(i, label) for i in sorted(sec["items"], key=sort_key))
    note = (
        f"Listings checked on {CHECKED} against iTicket, ShowGo, Afisha.uz and venue websites. "
        "Dates, times and prices can change, so please confirm with the venue before you go. "
        "Tap a venue name for directions. Everything here is either in English or doesn't depend on language." + (" " + note_extra if note_extra else "")
    )
    snippet = f"""<!-- Tashkent Expat Listings · {title} · {subtitle} · checked {CHECKED} -->
<style>
{CSS}
</style>
<div class="tel" id="{cid}">
<div class="tel-head"><h2>{esc(title)}</h2><p>{esc(subtitle)}</p></div>
<div class="tel-tabs" role="tablist">{tab_html}</div>
<div class="tel-grid">
{cards}
</div>
<p class="tel-note">{esc(note)}</p>
</div>
<script>{JS % cid}</script>
"""
    path = os.path.join(OUT, f"{key}-november-2026.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(snippet)
    return path, snippet, items + extra_items


# ---------------------------------------------------------------- ART
ART = [
    dict(t="BENCHELLAL, Monumental: Sculpting Past Tomorrow", v="histmus", until="2026-11-08",
         u="https://ccat.uz/en/programme/benchellal-monumental-sculpting-past-tomorrow", btn="Details",
         d="Dutch-Moroccan designer Mohamed Benchellal turns the geometry of modernist architecture into sculptural, wearable forms. First shown at the National Museum of Qatar, it now includes new pieces made during his CCA Tashkent residency.",
         p="Free", img=AF + "2026/08/0ee91cccb24dc2849af17c049888660a_m.webp",
         badges=[("Free", "free"), ("Closes 8 Nov", "hot")], f=["closing", "free"]),
    dict(t="In Search of Eden — Bobur Ismoilov", v="tauz", until="2026-11-07",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/13/tauz", btn="Details (RU)",
         d="A quiet solo show that treats Eden as an elusive ideal: home, childhood, love and inner calm. Small, reflective and easy to fit into a weekend wander.",
         p="Ask at the door", img=AF + "2026/10/8bc2bf9c0f5f09008aeae2b1f4cb26a7_m.webp",
         badges=[("Closes 7 Nov", "hot")], f=["closing"]),
    dict(t="Levitation — in memory of Bayat Mukhtarov", v="nbu", until="2026-11-14",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/21/levitation", btn="Details (RU)",
         d="Sculpture by Bayat Mukhtarov, one of the boldest voices of the Uzbek avant-garde, whose pared-back forms carry big philosophical ideas.",
         meta="Tue–Sat 10:00–17:00 (closed Sun & Mon)",
         p="10,000–50,000 UZS", img=AF + "2026/10/df872e8908892053090413589fac0aa4_m.webp",
         badges=[("Closes 14 Nov", "hot")], f=["closing"]),
    dict(t="Textures and Fragments — Yermolai Solzhenitsyn", v="ilkhom", until="2026-11-16",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/08/textures", btn="Details (RU)",
         d="Close-up photographs of patterns, surfaces and overlooked details, a visual diary about noticing beauty in ordinary places. Easy to pair with an evening show at the Ilkhom.",
         meta="Tue–Sun 11:00–18:00 (closed Mon)",
         p="Free", img=AF + "2026/10/6221bcf9919d73f706e49cc6fb441dee_m.webp",
         badges=[("Free", "free"), ("Photography", "")], f=["closing", "free"]),
    dict(t="Journey — Timur D'Vatz", v="andakulova", until="2026-11-18",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/12/dvatz-26", btn="Details (RU)",
         d="Solo show by a Royal Academy Schools graduate and BP Portrait Award winner whose career runs through Tashkent, Moscow, London and France. Expect alchemy, medieval tapestry, Celtic myth and a Pre-Raphaelite eye.",
         p="Free", img=AF + "2026/10/bd41b11c9995d4502412ef202d7e7702_m.webp",
         badges=[("Free", "free")], f=["closing", "free"]),
    dict(t="Book Graphics of Kydyrbay Nazhimov", v="library", until="2026-11-30",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/06/nazhimov", btn="Details (RU)",
         d="Book illustrations made mostly in scratchboard, where the image is scraped through wax and ink. Kids' sessions on printmaking, book design, animation and Karakalpak fairy tales run alongside (some need registration).",
         meta="Daily 10:00–21:00 · all ages",
         p="Free", img=AF + "2026/10/a4adb19b8cda2b16bd2141bd10d86200_m.webp",
         badges=[("Free", "free"), ("Family", "")], f=["closing", "free"]),
    dict(t="Life Beyond Measure — Zurab Tsereteli", v="nbu", until="2026-12-01",
         u="https://www.afisha.uz/ru/exhibitions/2026/08/13/vystavka-cereteli", btn="Details (RU)",
         d="Retrospective of the late Georgian-Russian monumentalist: paintings, sculpture, enamels, reliefs and silkscreens from early works to his late monumental series, with lectures and workshops alongside.",
         meta="Tue–Sat 10:00–17:00 (closed Sun & Mon)",
         p="Gallery ticket", img=AF + "2026/08/e1de191d47cac18a0f69fa7b49556130_m.webp",
         f=["long"]),
    dict(t="San'at Up", v="goethe", until="2026-12-12",
         u="https://www.afisha.uz/ru/exhibitions/2026/10/01/sanatup-gi", btn="Details (RU)",
         d="Prize-winning work by emerging artists from Uzbekistan and Tajikistan, hung along the institute's stairwell. A quick, free look at the region's next generation.",
         meta="10:00–19:00",
         p="Free", img=AF + "2026/09/1057ff60173b79351bfeccab600fafd4_m.webp",
         badges=[("Free", "free")], f=["long", "free"]),
    dict(t="Interflows", v="artepa", until="2026-12-15",
         u="https://www.afisha.uz/ru/exhibitions/2026/09/28/interflows", btn="Details (RU)",
         d="An exhibition about water in Central Asia by the DAVRA research group and Art Station, with new work by young regional artists and Saodat Ismailova's film Stains of Oxus. The show keeps evolving over its three-month run.",
         p="Free", img=AF + "2026/09/54a3063a884452f9b882db8ad30cca41_m.webp",
         badges=[("Free", "free")], f=["long", "free"]),
    dict(t="Savitsky's Diaries: Old and New", v="tcm", until="2027-01-24",
         u="https://iticket.uz/en/events/cultural-events/savitskys-diaries-old-and-new-2027",
         d="Multimedia show (painting, music, light and movement) about Igor Savitsky, the artist and collector who founded the Karakalpakstan State Museum of Art in Nukus. Organised by ACDF and curated by Aziza Izamova.",
         p="40,000–60,000 UZS", img=IT + "k2wro6npuQ0dyr2ezSgCQSu9UdFc3rToBaLdHDga.jpg",
         badges=[("Multimedia", "")], f=["long"]),
    dict(t="Chiroyli Vanitas — Elena Martynova", v="kinoxona", until="2026-11-30",
         u="https://www.afisha.uz/ru/cinema/2026/10/20/kinoxona", btn="Details (RU)",
         d="A solo photography show that opened with the kinoxona art cinema's move to its new home on Chimkent Street. Combine it with an English-language screening.",
         p="Free", img=AF + "2026/10/87bdc4dd60d4590b5cc0b123d321d9fd_m.webp",
         badges=[("Free", "free"), ("Photography", "")], f=["closing", "free"]),
    dict(t="Hikmah", v="cca", until="2027-01-31",
         u="https://ccat.uz/en/programme/hikmah-exhibition", btn="Details",
         d="The inaugural show at Tashkent's new Centre for Contemporary Arts, set in a restored 1912 diesel power station built for the city's first tramway. New commissions by Uzbek and international artists explore wisdom, spirit and the transformation of matter.",
         meta="Heads-up: the Centre is closed 10–20 November for technical reasons.",
         p="Free", img=AF + "2026/08/8d19dc8eb2f5bc2b8c6e6ec1aa41ccb7_m.webp",
         badges=[("Free", "free"), ("Closed 10–20 Nov", "hot")], f=["long", "free"]),
]

# ---------------------------------------------------------------- MUSIC
MUSIC = [
    # classical
    dict(t="Mozart & Chopin — Young Talents Chamber Orchestra", v="cons", dates=["2026-11-13"], time="19:00",
         u="https://iticket.uz/en/events/concerts/mozart-and-chopin-young-talents-chamber-orchestra",
         d="Austrian Classicism meets Polish Romanticism: an evening of Mozart and Chopin from a young chamber orchestra.",
         p="66,000–165,000 UZS", img=IT + "qwRxxi3d2cOs5NFvnwI8kHcNBz8DmCNj1dDr89CM.jpg", f=["classical"]),
    dict(t="From the New World — National Symphony Orchestra", v="turkiston", dates=["2026-11-23"], time="19:00",
         u="https://iticket.uz/en/events/concerts/iz-novogo-sveta",
         d="Rachmaninoff's The Rock and Haydn's Cello Concerto (soloist Sardor Ibragimov), building to Dvořák's Symphony No. 9. Conducted by Boburjon Kurbonaliev.",
         p="77,000–132,000 UZS", img=IT + "chuD6MvHrRwBn3GszCWdLv47l3VSpqAUKU9OZx6q.jpg", f=["classical"]),
    dict(t="An Evening of Organ Music — Soloists of Uzbekistan", v="cons", vlabel="State Conservatory (Organ Hall)",
         dates=["2026-11-27"], time="19:00",
         u="https://iticket.uz/en/events/concerts/vecher-organnoj-muzyki-solisty-uzbekistana",
         d="Bach, Albinoni's Adagio, Rheinberger's Organ Concerto in G minor, Respighi and Jenkins' Palladio, with organist Adelina Fatkhutdinova and conductor Anvar Raimdzhanov.",
         p="88,000–385,000 UZS", img=IT + "FLgbVLSlOu8sxvtCkQ3toUbsdqsPguvOzqqiUqb8.jpg",
         badges=[("Almost sold out", "hot")], f=["classical"]),
    # crossover
    dict(t="The Music of Hans Zimmer — Tynda Music", v="panorama", dates=["2026-11-14"], time="19:00",
         u="https://iticket.uz/en/events/concerts/the-music-of-hans-zimmer-tynda-music",
         d="Symphony orchestra and choir play Hans Zimmer's film scores.",
         p="230,000–700,000 UZS", img=IT + "qEutxJne5Fk4pgjwiFAOL0C0oWsF2gW1a9DtH03s.jpg", f=["crossover"]),
    dict(t="BURAK in BRAVO Orchestra", v="humo", dates=["2026-11-19"], time="19:30",
         u="https://showgo.uz/en/session/1376-burak-in-bravo-orchestra",
         d="Turkish actor Burak Özçivit headlines a stage show built around TV-series favourites, played live by the Bravo Orchestra.",
         p="From 297,000 UZS", img=SG + "2026/10/cropped_20261022202350_lzvj_Bravo_Burak_19-30.jpg", pos="center 25%",
         f=["crossover"]),
    dict(t="MICHAEL: Legendary Hits — Turkiston Chamber Orchestra", v="turkiston", dates=["2026-11-25"], time="19:00",
         u="https://iticket.uz/en/events/concerts/michael-legendarnye-hity",
         d="Billie Jean, Bad, Smooth Criminal, Thriller, Black or White and more, re-arranged for chamber orchestra.",
         p="66,000–275,000 UZS", img=IT + "7My29fzdiw9mf3TTAKc90ML5DRxDjwbYUSAlmtxo.jpg", f=["crossover"]),
    # opera & operetta
    dict(t="Tamerlano (Handel)", v="navoi", range=["2026-11-02", "2026-11-04"], time="19:00",
         u="https://iticket.uz/en/events/concerts/tamerlano-2026",
         d="Stefano Poda directs Handel's opera in Kirill Richter's contemporary reworking, played by the National Symphony Orchestra under Alibek Kabdurakhmanov with traditional Uzbek instruments added to the orchestra.",
         p="100,000–800,000 UZS", img=IT + "ekdExRDpGo188AcZzhtZR0btOQNcWgg5YvIwIh9W.jpg",
         badges=[("3 nights", "new")], f=["opera"]),
    dict(t="La Traviata (Verdi)", v="navoi", dates=["2026-11-08"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/dzh-verdi-traviata-opera-2626",
         d="Violetta and Alfredo's doomed love story, one of the most-performed operas in the world.",
         p="77,000–440,000 UZS", img=IT + "i4VLvZ1iN3Rxt35CrPO3v2NFVv4qxgX8oNB5Otgk.jpg", f=["opera"]),
    dict(t="Alisher Navoi (Mustafo Bafoev)", v="navoi", dates=["2026-11-10"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/m-bafoev-aliser-navoi-opera-9714",
         d="Uzbek national opera on the life of the 15th-century poet and statesman the theatre is named after. A good one to see while you're here.",
         p="55,000–165,000 UZS", img=IT + "OFpifJGjvxRtXfCVMkTGs3BVPl2ejF1BPZGj7K4b.jpg", f=["opera"]),
    dict(t="Don Giovanni (Mozart)", v="navoi", dates=["2026-11-14"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/vamocart-don-zhuan-opera-2626",
         d="Mozart's mix of drama, seduction, irony and the supernatural.",
         p="77,000–440,000 UZS", img=IT + "S4FjY4VGnklyB7uOwD7n3tjJwYUfjLCZZRTYAX9u.jpg", f=["opera"]),
    dict(t="Pagliacci (Leoncavallo)", v="navoi", dates=["2026-11-15"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/rleonkavallo-payacy-opera-9458",
         d="Short, searing verismo opera: a travelling clown troupe where the play turns real.",
         p="55,000–165,000 UZS", img=ITC + "BfhStzLOcWj2W4I6V19DK6EkKZiAfhVN07E9kGfq.jpg", f=["opera"]),
    dict(t="Un ballo in maschera (Verdi)", v="navoi", dates=["2026-11-19"], time="19:00",
         u="https://www.afisha.uz/ru/concerts/2024/10/08/g-verdi", btn="Tickets (RU)",
         d="Verdi's tale of political plotting and forbidden love that ends at a masked ball.",
         p="From 55,000 UZS", img=AF + "2024/10/2b200358b5e7b14fb0d7bbe2f14b082f_m.jpg", f=["opera"]),
    dict(t="La Bohème (Puccini)", v="navoi", dates=["2026-11-21"], time="19:00",
         u="https://www.afisha.uz/ru/theatres/2025/03/04/bogema", btn="Tickets (RU)",
         d="Puccini's young Parisian bohemians in love and in poverty, with the State Symphony Orchestra.",
         p="From 55,000 UZS", img=AF + "2025/03/946620b27a8c8241c4e1fa831693c10d_m.webp", f=["opera"]),
    dict(t="Carmen (Bizet)", v="navoi", dates=["2026-11-22"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/zhorzh-bize-karmen-opera",
         d="Konstantin Kamynin's new production moves the story to 1940s–50s Spain, with a Carmen who values freedom over love, fear and convention.",
         p="110,000–330,000 UZS", img=IT + "lQUeJ9lAxQ4BB96nLKg9iVDbgirMOyraweAmTRe0.jpg",
         badges=[("New production", "new")], f=["opera"]),
    # jazz rock rap
    dict(t="Jazzirama & Friends — IlkhomJazzClub", v="ilkhom", dates=["2026-11-03"], time="19:00",
         u="https://www.afisha.uz/ru/concerts/2026/10/13/jazzirama-11", btn="Tickets (RU)",
         d="The Ilkhom's jazz club opens its season with Tashkent band Jazzirama and guests including Mansur Tashmatov and maqom singer Nodira Pirmatova: standards, ethno-jazz and improvisation.",
         p="240,000–290,000 UZS", img=AF + "2026/10/fc7f51f39f3074272c0646f5856e9796_m.webp", f=["jazz"]),
    dict(t="Poshlaya Molly — 10th anniversary tour", v="yunusobod", dates=["2026-11-22"], time="20:00",
         u="https://iticket.uz/en/events/concerts/poshlayamolly",
         d="The Ukrainian pop-punk band's tenth-anniversary tour stops in Tashkent with the hits and rarities.",
         p="825,000–1,650,000 UZS", img=IT + "OAgKq14AWD5kJyr1shLWcdwueeJ5aTeLfLsuRnka.jpg",
         badges=[("18+", "")], f=["jazz"]),
    dict(t="KALEO — Live in Tashkent", v="humo", dates=["2026-11-27"], time="19:00",
         u="https://showgo.uz/en/session/1165-kaleo-live-in-tashkent",
         d="Icelandic blues-rock band best known for 'Way Down We Go'.",
         p="From 250,000 UZS", img=SG + "2026/09/cropped_20260907114146_lrqs_05261C4D-B221-4918-89BE-420BF156B13E.jpg",
         pos="center 30%", f=["jazz"]),
    dict(t="WORKERS — album presentation", v="sahna", dates=["2026-11-28"], time="19:00",
         u="https://www.afisha.uz/ru/concerts/2026/10/26/workers", btn="Tickets (RU)",
         d="Seven rappers from the WORKERS collective play their new album live plus solo tracks, with a merch fair in the foyer beforehand.",
         p="150,000 UZS", img=AF + "2026/10/e59c6d1e848203346d920d0dba5cd75b_m.webp", f=["jazz"]),
    # international pop
    dict(t="Valery Meladze", v="palace", dates=["2026-11-01"], time="19:30",
         u="https://iticket.uz/en/events/concerts/valerij-meladze2026",
         d="The romantic-ballad veteran returns with live band and the big hits.",
         p="250,000–3,300,000 UZS", img=IT + "Q8JnsjqzkRdONFlYiKGkJ4W1GhCOO4RmV1PeHUZr.jpg",
         badges=[("Few seats left", "hot")], f=["intl"]),
    dict(t="Cheb Mami", v="humo", dates=["2026-11-07"], time="20:00",
         u="https://iticket.uz/en/events/concerts/cheb-mami",
         d="The Algerian 'Prince of Raï' plays Tashkent for the first time.",
         p="150,000–2,000,000 UZS", img=IT + "jzp3aCFiqfPGykFUOudYAdj566hzkHzFCSiFyQHh.jpg",
         badges=[("First time in Tashkent", "new")], f=["intl"]),
    dict(t="Vanya Dmitrienko", v="humo", dates=["2026-11-12"], time="19:00",
         u="https://showgo.uz/en/session/1268-vania-dmitrienko-v-tashkente-2026",
         d="Arena show from the Russian pop singer.",
         p="From 150,000 UZS", img=SG + "2026/10/cropped_20261017074440_zamf_IMG_6610.jpg", pos="center 25%",
         f=["intl"]),
    dict(t="Philipp Kirkorov", v="humo", dates=["2026-11-13"], time="19:00",
         u="https://showgo.uz/en/session/1292-filipp-kirkorov-tashkent",
         d="The Russian pop showman brings his touring stage show to Humo Arena.",
         p="From 250,000 UZS", img=SG + "2026/10/cropped_20261015081939_emqf_photo_2026-10-15_13-19-23.jpg",
         pos="center 25%", f=["intl"]),
    dict(t="Autumn Story Festival", v="humo", dates=["2026-11-15"], time="19:00 (welcome zone from 15:00)",
         u="https://iticket.uz/en/events/concerts/festival-osennyaya-istoriya",
         d="A multi-artist pop festival pitched as a celebration for women, with an afternoon welcome zone before the main concert.",
         p="250,000–1,166,000 UZS", img=IT + "B29ceRwVlBisFYkq7B442Hp5MTebneldrxPSNK0x.jpg", f=["intl"]),
    dict(t="Abzal Uteshov", v="turkiston", dates=["2026-11-27"], time="19:00",
         u="https://showgo.uz/en/session/1350-abzal-uteshov-v-tashkente-2026",
         d="Heartfelt, emotional pop from the contemporary Kazakh singer.",
         p="From 250,000 UZS", img=SG + "2026/10/cropped_20261017111553_pusj_jpg.jpg", pos="center 25%",
         f=["intl"]),
    dict(t="Mariana Lokel — NANO Tour", v="panorama", dates=["2026-11-28"], time="18:00",
         u="https://showgo.uz/en/session/1335-mariana-lokel-nano-tur-osen-2026-v-tashkente",
         d="Autumn tour stop from the singer-songwriter.",
         p="From 450,000 UZS", img=SG + "2026/09/cropped_20260929160453_dtby_jpg.jpg", pos="center 25%",
         f=["intl"]),
    # uzbek pop
    dict(t="Shoxrux — Katta Show", v="humo", dates=["2026-11-01"], time="18:00",
         u="https://iticket.uz/en/events/concerts/shoxrux2026",
         d="Uzbek rap's veteran star back on the big stage with fan favourites like Balandda and Chilparchin, plus new material.",
         p="180,000–950,000 UZS", img=IT + "JPCAuH4HvrI7JW9IY7aMtjtcwa5xKQuM5sU9IhwW.jpg", f=["uzbek"]),
    dict(t="Otabek Madrahimov — 35 years on stage", v="palace", range=["2026-11-02", "2026-11-05"], time="19:30",
         u="https://iticket.uz/en/events/concerts/otabek-madrahimov",
         d="Four-night jubilee run from the much-loved estrada singer.",
         p="50,000–600,000 UZS", img=IT + "AOR1Z5yi2QfkpbJti3JRQQpaITdE3FliwRXDsu5y.jpg", f=["uzbek"]),
    dict(t="Ulug'bek Rahmatullayev — 25 years", v="palace", range=["2026-11-08", "2026-11-14"], time="19:30",
         u="https://iticket.uz/en/events/concerts/ulugbek-rahmatullayev-2026",
         d="A week of anniversary concerts covering 25 years of Uzbek pop hits.",
         p="80,000–500,000 UZS", img=IT + "wey2CaJpCLnjH9CPnm7CUYFzbRxg6SI87PXcKel8.jpg", f=["uzbek"]),
    dict(t="G'aybulla Tursunov — Quralay", v="humo", dates=["2026-11-20"], time="19:00",
         u="https://iticket.uz/en/events/concerts/gaybulla-tursunov2026",
         d="The two-time 'Best Singer' winner's first Humo Arena show (Janona, Yor, Quralay).",
         p="60,000–550,000 UZS", img=IT + "12InDgpy2OBZEG5C11LqJJrFQdFIcT0wwSVzov8q.jpg", f=["uzbek"]),
    dict(t="SAHAR — AYOL", v="humo", dates=["2026-11-21"], time="19:00",
         u="https://www.afisha.uz/ru/concerts/2026/09/30/sahar", btn="Tickets (RU)",
         d="The band presents its big new concert programme, AYOL.",
         p="150,000–450,000 UZS", img=AF + "2026/10/0bc7078e39b6c651ba9bc06637caf6dd_m.webp", f=["uzbek"]),
    dict(t="Yulduzlar Oqshomi (Evening of Stars)", v="panorama", dates=["2026-11-21"], time="19:00",
         u="https://iticket.uz/en/events/concerts/yulduzlar-oqshomi",
         d="Gala night with a line-up of popular Uzbek singers.",
         p="200,000–300,000 UZS", img=IT + "sVyYMowuK6gT7jCX88O5utO3pSAGhxTzHhDeHFIV.jpg", f=["uzbek"]),
    dict(t="Benom — The Best (Yangi)", v="palace", range=["2026-11-27", "2026-11-30"], time="19:30",
         u="https://iticket.uz/en/events/concerts/benom-guruhi-the-best-yangi",
         d="Four nights of live hits from the Uzbek pop group, plus a Saturday 28 Nov matinee at 15:00.",
         p="70,000–500,000 UZS", img=IT + "VsfkeoRtJekGpHkToQhYnFZBXpA85F4dLg7WDN7O.jpg", f=["uzbek"]),
]

# ---------------------------------------------------------------- THEATRE & FILM
CM = "https://cinematica.uz/uploads/movies/"
EMC = "https://www.instagram.com/englishmovieclubuz/"
EMC_META = "English run starts this day. In October the club's titles played nightly at 20:30 for a week (2D, no subtitles); exact times go up on its Instagram a few days before."
THEATRE = [
    # Ilkhom, English surtitles
    dict(t="White, White Black Stork", v="ilkhom", dates=["2026-11-04"], time="19:00",
         u="https://ilkhom.com/events/belyj-belyj-chyornyj-aist-eng-subs/", btn="Details & tickets",
         d="One of the Ilkhom's signature productions: forbidden love colliding with the customs of old Tashkent, built on Abdulla Qodiriy's unfinished novella with threads from his novel Days Gone By. Staged by Yolkin Tuychiev and Mark Weil. 1 hr 45, 14+.",
         meta="Performed in Russian with English surtitles.",
         p="150,000–180,000 UZS", img=AF + "2026/10/c97fe2cda316f786a373414dd1c54087_m.webp",
         badges=[("English surtitles", "eng")], f=["stage"]),
    dict(t="Seven Moons", v="ilkhom", dates=["2026-11-13"], time="19:00",
         u="https://ilkhom.com/events/sem-lun-eng-subs/", btn="Details & tickets",
         d="A Sufi parable after Alisher Navoi about a shah who has everything and loses it through pride. Vladimir Pankov's staging with Moscow's SounDrama studio blends live saxophones, nay, double bass and percussion with Eastern dance. 1 hr 45, 16+.",
         meta="Performed in Russian with English surtitles.",
         p="150,000–180,000 UZS", img=AF + "2026/08/fe6c19d4a1f69130ed8ab4273522874a_m.webp",
         badges=[("English surtitles", "eng"), ("Live music", "")], f=["stage"]),
    # visual
    dict(t="Charlie and the Sea Lions — circus", v="circus", range=["2026-10-31", "2026-12-06"],
         u="https://showgo.uz/en/session/1328-tsirk-charli-i-morskie-kotiki-tashkent-2026",
         d="A Russian circus season at the State Circus, headlined by German clown Charlie, with performing sea lions. Largely visual fun for all ages. Runs until 6 December.",
         p="From 70,000 UZS", img=SG + "2026/10/cropped_20261028071204_lbjl_photo_2026-10-28_12-10-55.jpg",
         pos="center 30%", ph="Circus", badges=[("No language needed", "eng")], f=["stage", "family"]),
    # kinoxona (original audio, Russian subtitles)
    dict(t="Planètes (2025)", v="kinoxona", dates=["2026-11-01"], time="12:00",
         u="https://showgo.uz/en/session/1396-odisseia-oduvanchikov-planetes-2025",
         d="Momoko Seto's Cannes Directors' Fortnight animation: after nuclear blasts destroy Earth, four dandelion seeds drift into space in search of somewhere to take root. Macro photography meets CGI.",
         meta="No dialogue.",
         p="90,000 UZS", img=SG + "2026/10/cropped_20261028070436_ykas_7.jpg", pos="center 30%", ph="kinoxona",
         badges=[("No dialogue", "eng")], f=["film"]),
    dict(t="The Little Shop of Horrors (1960)", v="kinoxona", dates=["2026-11-01"], time="16:00",
         u="https://showgo.uz/en/session/1392-malenkii-magazinchik-uzhasov-the-little-shop-of-horrors-1960",
         d="Roger Corman's cult black comedy about a florist's assistant and his bloodthirsty plant, on the big screen at the independent kinoxona art cinema.",
         meta="Original English audio, Russian subtitles.",
         p="90,000 UZS", img=SG + "2026/10/cropped_20261028064610_tzol_3_2.jpg", pos="center 30%", ph="kinoxona",
         badges=[("In English", "eng")], f=["film"]),
    dict(t="Lil Peep: Everybody's Everything (2019)", v="kinoxona", dates=["2026-11-01"], time="19:30",
         u="https://showgo.uz/en/session/1395-lil-peep-vsio-dlia-vsekh-everybodys-everything-2019",
         d="Documentary portrait of the emo-rap artist Lil Peep, told through his music, home videos and the people closest to him.",
         meta="Original English audio, Russian subtitles.",
         p="90,000 UZS", img=SG + "2026/10/cropped_20261028082900_hqkq_4.jpg", pos="center 30%", ph="kinoxona",
         badges=[("In English", "eng"), ("Few seats left", "hot")], f=["film"]),
    # Cinematica English Movie Club
    dict(t="The Cat in the Hat — English Movie Club", v="cinematica", dates=["2026-11-05"], time="English run starts",
         u=EMC, btn="English sessions",
         d="New animated Dr. Seuss adaptation with Bill Hader voicing the Cat, sent to liven up a rainy day for two bored siblings.",
         meta=EMC_META,
         p="Cinematica ticket prices", img=CM + "cdcf983f-9269-4574-9959-eb49aa4688bc.png", ph="English Movie Club",
         badges=[("In English", "eng"), ("Family", "")], f=["film", "family"]),
    dict(t="Ebenezer — English Movie Club", v="cinematica", dates=["2026-11-12"], time="English run starts",
         u=EMC, btn="English sessions",
         d="Johnny Depp plays Ebenezer Scrooge in a new take on A Christmas Carol.",
         meta=EMC_META,
         p="Cinematica ticket prices", img=None, ph="English Movie Club",
         badges=[("In English", "eng")], f=["film"]),
    dict(t="The Hunger Games: Sunrise on the Reaping — English Movie Club", v="cinematica", dates=["2026-11-19"],
         time="English run starts",
         u=EMC, btn="English sessions",
         d="Francis Lawrence's prequel set 24 years before the original trilogy: a young Haymitch Abernathy is thrown into the 50th Hunger Games. With Ralph Fiennes, Elle Fanning and Glenn Close. 12+.",
         meta=EMC_META,
         p="Cinematica ticket prices", img=CM + "63dfd810-9da2-4ff0-94b6-6b8fd3aa03d8.png", ph="English Movie Club",
         badges=[("In English", "eng")], f=["film"]),
]

# ---------------------------------------------------------------- DANCE
DANCE = [
    dict(t="Alice in Wonderland", v="navoi", dates=["2026-11-07"], time="12:00",
         u="https://iticket.uz/en/events/theaters-tashkent/s-muhamedov-alisa-v-strane-chudes-skazka-balet",
         d="S. Mukhamedov's family ballet mixes classical and contemporary choreography, with the White Rabbit and friends in bright costumes. A good first ballet. 3+.",
         p="77,000–220,000 UZS", img=IT + "9aFaAox6e71ak8LDEsfi37wl6bAq19WXz7d1rTPx.jpg",
         badges=[("Matinee", ""), ("Family", "")], f=["ballet", "family"]),
    dict(t="The Firebird & Scheherazade", v="navoi", dates=["2026-11-07"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/istravinskii-zar-ptica-n-rimskii-korsakov-sexerazada-9460",
         d="Ballets Russes double bill: Stravinsky's Firebird and Rimsky-Korsakov's Scheherazade.",
         p="77,000–220,000 UZS", img=IT + "FvJkI90rpzLeeblcDWq8bZW1Fl2moZEm7QxDuo0F.jpg", f=["ballet"]),
    dict(t="Romeo and Juliet (Prokofiev)", v="navoi", dates=["2026-11-13"], time="19:00",
         u="https://iticket.uz/en/events/theaters-tashkent/sprokofev-romeo-i-dzuletta-balet-9464",
         d="Prokofiev's full-length ballet, a cornerstone of the Bolshoi's repertoire. 12+.",
         p="77,000–220,000 UZS", img=IT + "kfmwpzfbtneKSG9i2OaUAOfiOnZnzaY2oSF9cpRw.jpg", f=["ballet"]),
]
DANCE_DEC = [
    dict(t="Romeo & Juliet — flamenco show", v="rusdrama", dates=["2026-12-08"], time="19:00",
         u="https://showgo.uz/en/session/1378-romeo-juliet-romeo-i-dzhuletta-legendarnaia-istoriia-liubvi-rasskazannaia-na-iazyke-tantsa-flamenko-shou",
         d="Spanish company Flamenco Live tells Shakespeare's story through flamenco dance, guitar and song.",
         p="From 150,000 UZS", img=SG + "2026/10/cropped_20261022140800_gmed_FLAMENCO_2026__10801350.jpg",
         pos="center 30%", ph="Flamenco", badges=[("December", "new")], f=["december"]),
    dict(t="The Nutcracker", v="turkiston", dates=["2026-12-16"], time="19:00",
         u="https://showgo.uz/en/session/1375-skazochnyi-balet-v-dvukh-deistviiakh-shchelkunchik-p-i-chaikovskii-i-libretto-m-petipa",
         d="Tchaikovsky's fairy-tale ballet in two acts, after Petipa's libretto. Book early for the holiday season.",
         p="From 150,000 UZS", img=SG + "2026/10/cropped_20261021052709_thpv_photo_2026-10-21_10-26-50.jpg",
         pos="center 30%", badges=[("December", "new"), ("Family", "")], f=["december", "family"]),
]

# ---------------------------------------------------------------- SPORT
SPORT = [
    dict(t="Pakhtakor vs Al-Nassr", v="pakhtakor", dates=["2026-11-02"], time="18:45",
         u="https://iticket.uz/en/events/sport/ppaalsr26",
         d="AFC Champions League Elite, league stage: Cristiano Ronaldo's Saudi side visit Tashkent. E-tickets must be activated in the iTicket app, QR codes go live 3 hours before kick-off, and tickets are non-refundable.",
         p="100,000–3,000,000 UZS", img=IT + "cUkWIkcGYLjLFZybW6Z4Cy7vKLx2WSJlMelRlDqt.jpg",
         badges=[("Big match", "hot")], ph="Football", f=["football"]),
    dict(t="Pakhtakor vs Kokand 1912", v="pakhtakor", dates=["2026-11-06"], time="kick-off TBC",
         u="https://www.pakhtakor.uz", btn="Club site",
         d="Uzbekistan Super League, round 27. An easy, affordable way to see Tashkent's biggest club late in the season.",
         p="Tickets at the stadium", img=None, ph="Super League", f=["football"]),
    dict(t="Uzbekistan vs Russia", v="pakhtakor", dates=["2026-11-12"], time="kick-off TBC",
         u="https://www.uzdaily.uz/en/uzbekistan-to-face-russia-in-tashkent-on-12-november/", btn="Match news",
         d="International friendly in the November FIFA window. Fabio Cannavaro's World Cup side host Russia. Watch iTicket for the ticket release.",
         p="On sale soon", img=None, ph="International friendly", f=["football"]),
    dict(t="Lokomotiv vs Pakhtakor", v="tbc", vlabel="Tashkent (Lokomotiv home fixture)", dates=["2026-11-20"],
         time="kick-off TBC", sort="2026-11-20",
         u="https://www.pakhtakor.uz", btn="Club site",
         d="A Tashkent derby in Super League round 28.",
         p="TBC", img=None, ph="Tashkent derby", f=["football"]),
    dict(t="World Boxing Cup Finals 2026", v="tbc", range=["2026-11-26", "2026-12-04"],
         u="https://worldboxing.org/dates-changed-for-world-boxing-cup-finals-2026-in-tashkent/", btn="Details",
         d="Season finale of World Boxing's Olympic-style series, with ranking points that feed seedings for 2027–28 Olympic qualifying. Uzbekistan's boxers are among the world's best, so expect a loud home crowd.",
         p="Tickets TBA", img=None, ph="Boxing", badges=[("World-class", "new")], f=["boxing"]),
]


def main():
    out = {}
    out["art"] = build(
        "art", "Art & Exhibitions — November 2026",
        "Exhibitions in Tashkent this month: no Russian or Uzbek needed", "Exhibition",
        [("free", "Free entry"), ("closing", "Closing in November"), ("long", "On into December & beyond")],
        ART)
    out["music"] = build(
        "music", "Music — November 2026",
        "Concerts, opera and gigs in Tashkent this month: music speaks for itself", "Music",
        [("classical", "Classical & organ"), ("opera", "Opera"), ("crossover", "Film & crossover"),
         ("jazz", "Jazz, rock & rap"), ("intl", "International pop"), ("uzbek", "Uzbek pop & estrada")],
        MUSIC)
    out["theatre"] = build(
        "theatre", "Theatre & Film — November 2026",
        "Plays with English surtitles, films in English and shows that need no language", "Theatre",
        [("stage", "Stage"), ("film", "Film"), ("family", "Family")],
        THEATRE,
        note_extra="Plays in Russian or Uzbek without English surtitles aren't listed. kinoxona screens films in their original language with Russian subtitles and publishes its programme about a week ahead, so check its ShowGo listings for more English-language titles later in the month. Opera is listed under Music and ballet under Dance.")
    out["dance"] = build(
        "dance", "Dance — November 2026",
        "Ballet in Tashkent this month, plus December dance worth booking now", "Ballet",
        [("ballet", "November ballet"), ("family", "Family"), ("december", "December")],
        DANCE, extra_sections=[dict(title="Book ahead for December", items=DANCE_DEC)])
    out["sport"] = build(
        "sport", "Sport — November 2026",
        "Matches and tournaments to catch in Tashkent this month", "Sport",
        [("football", "Football"), ("boxing", "Boxing")],
        SPORT,
        note_extra="Kick-off times for league matches and the national-team friendly were not yet confirmed at the time of checking.")

    # combined preview page
    parts = []
    nav = []
    for k, (path, snip, items) in out.items():
        nav.append(f'<a href="#sec-{k}">{k.title()}</a>')
        parts.append(f'<section id="sec-{k}" style="margin:0 0 56px">{snip}</section>')
    preview = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tashkent Expat Listings — November 2026 preview</title>
<style>body{{margin:0;background:#f8fafc}}.pv-nav{{position:sticky;top:0;z-index:9;background:#1e3a5f;padding:10px 16px;display:flex;gap:18px;font:600 14px 'Segoe UI',Roboto,Arial,sans-serif}}.pv-nav a{{color:#fff;text-decoration:none}}.pv-wrap{{padding:20px 12px}}</style>
</head><body><nav class="pv-nav">{''.join(nav)}</nav><div class="pv-wrap">{''.join(parts)}</div></body></html>"""
    with open(os.path.join(OUT, "preview-all-november-2026.html"), "w", encoding="utf-8") as fh:
        fh.write(preview)

    # manifest of links & images for checking
    manifest = []
    for k, (path, snip, items) in out.items():
        for it in items:
            manifest.append({"cat": k, "t": it["t"], "u": it["u"], "img": it.get("img")})
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    for k, (path, snip, items) in out.items():
        print(k, len(items), os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()


def build_site(dest="live"):
    """Standalone pages for GitHub Pages, embedded in Google Sites by URL.
    dest="live" writes to the repo root (what the site shows); dest="preview" writes to /preview/."""
    root = os.path.dirname(HERE)
    site = root if dest == "live" else os.path.join(root, "preview")
    os.makedirs(site, exist_ok=True)
    names = {"art": "Art", "music": "Music", "theatre": "Theatre & Film", "dance": "Dance", "sport": "Sport"}
    for key, label in names.items():
        snip = open(os.path.join(OUT, f"{key}-november-2026.html"), encoding="utf-8").read()
        page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{label} · Tashkent Expat Listings</title>
<style>html,body{{margin:0;background:#fff}}</style>
</head><body>
{snip}
</body></html>
"""
        with open(os.path.join(site, f"{key}.html"), "w", encoding="utf-8") as fh:
            fh.write(page)
    links = "".join(f'<li><a href="{k}.html">{v}</a></li>' for k, v in names.items())
    with open(os.path.join(site, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tashkent Expat Listings</title><style>body{{font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:640px;margin:40px auto;padding:0 16px;color:#1f2937}}h1{{color:#1e3a5f}}a{{color:#1e3a5f}}</style></head>
<body><h1>Tashkent Expat Listings</h1><p>English-friendly events in Tashkent, refreshed weekly.</p><ul>{links}</ul></body></html>
""")
    if dest == "live":
        open(os.path.join(site, ".nojekyll"), "w").close()
    return site


if __name__ == "__main__":
    import sys
    print(build_site(sys.argv[1] if len(sys.argv) > 1 else "live"))
