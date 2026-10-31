# Tashkent Expat Listings: how the weekly refresh works

Owner: Louis Train (GitHub account `tashkent-listings`). The site is Google Sites. Each category page there embeds one of these GitHub Pages files by URL, so pushing to `main` updates the live site:

- https://tashkent-listings.github.io/art.html
- https://tashkent-listings.github.io/music.html
- https://tashkent-listings.github.io/theatre.html (Theatre & Film)
- https://tashkent-listings.github.io/dance.html
- https://tashkent-listings.github.io/sport.html

## The audience rule (most important)

These are expat listings. Every listing must be in English or not depend on language:

- Allowed: music of any kind, opera (it's sung), ballet and dance, visual art, photography, sport, circus and other visual shows, films in English, and films with no dialogue.
- Plays, comedy, operetta, talks and kids' shows in Russian or Uzbek are excluded unless they have English surtitles.
- Do not list events outside Tashkent. ShowGo carries many regional concerts in Samarkand, Bukhara, Qarshi and Jizzakh, so check the venue.

## Coverage window

- List events from the run date to the end of the current month.
- From the 20th of a month, also include the following month.
- Titles say which month(s) are covered, e.g. "Music — November–December 2026".
- Drop anything that has already happened. Drop exhibitions that have closed.

## Sources and how to read them

The shell can reach these domains: iticket.uz, *.iticket.uz, showgo.uz, *.afisha.uz, ilkhom.com, cinematica.uz, ccat.uz. Use curl or Python for them.

- **iTicket** (Navoi Theatre opera and ballet, the Conservatory, Humo Arena, the Palace of Friendship of Peoples, Turkiston, Panorama, sport):
  - list: `https://api.iticket.uz/en/v5/events?client=web&category_slug={concerts|theaters-tashkent|cultural-events|sport|kids|other-events}&page=N` (15 per page; follow `next_page_url`)
  - detail: `https://api.iticket.uz/en/v5/events/{category_slug}/{slug}?client=web`. Gives sessions (`session_starts_at` is UTC, add 5 hours for Tashkent), venue coordinates, min/max price, tickets left (`available_tickets_count`) and images.
  - Public link: `https://iticket.uz/en/events/{category_slug}/{slug}`
  - Image: `facebook_url` (1200×628). If that is the generic `opengraph.jpg`, use `cover_url`.
- **ShowGo** (arena pop, touring shows, the circus, kinoxona films, flamenco):
  - Event data sits in the server-rendered HTML of `https://showgo.uz/ru` and the category pages `/ru/category/{koserts|detyam|cinemas|...}`. Parse it, or use WebFetch.
  - Links: `https://showgo.uz/en/session/{id-slug}`
  - Images: `https://showgo.uz/_next/image?url={urlencoded https://api.showgo.uz/storage/images/<path>}&w=640&q=75`. Never use the originals, which can be 5000px or more.
- **Afisha.uz (RU)**: exhibitions (`/ru/exhibitions`), extra Navoi operas (venue schedule at `/ru/places/teatr-alishera-navoi`), small gigs (`/ru/concerts`) and cinema (`/ru/cinema`). Image is the article's og:image (`…_m.webp`).
- **Ilkhom Theatre**: the full month is at `https://ilkhom.com/wp-admin/admin-ajax.php?action=wcs_get_events_json&start=YYYY-MM-DD&end=YYYY-MM-DD`. Times are labelled +00:00 but are actually local. Include only shows whose title contains "eng. subs" (English surtitles). Ilkhom concerts, such as IlkhomJazzClub, count as music.
- **Cinematica English Movie Club** (Tashkent City Mall): the club's Instagram @englishmovieclubuz posts a monthly list of English-language titles with start dates. Each title then usually plays nightly at 20:30 for a week, in 2D with no subtitles.
  - Cinematica's own API doesn't flag language. Use `https://cinematica.uz/api/v1/movies/soon` and `/movies/{id}` only for posters (`file_poster`, horizontal) and release dates.
  - If Instagram can't be read, keep the existing club cards and flag it in the summary.
- **kinoxona art cinema** (17 Chimkent St): films are shown in the original language with Russian subtitles. Include only English-language films, plus films with no dialogue. The programme appears about a week ahead on ShowGo (venue "Кинозал Чимкент, 17").
- **CCA Tashkent**: `https://ccat.uz/en/programme/...`. Check the homepage for closure notices.
- **Sport**: Pakhtakor, Uzbekistan national team, big tournaments in Tashkent. Use web search; iTicket's sport category has tickets once they're on sale.

## Building

All listing data lives in `tools/build.py` (the ART, MUSIC, THEATRE, DANCE, DANCE_DEC and SPORT lists). Edit the data there.

- Write descriptions in plain English, in your own words, and don't copy source text.
- Badges: "In English", "English surtitles", "No dialogue", "No language needed", "Free", "Few seats left" (under about 60 tickets left), "Closes …", "Premiere".
- Set `CHECKED` to the run date.
- `python3 tools/build.py live` writes the pages to the repo root, which is what the site shows.
- `python3 tools/build.py preview` writes them to `/preview/` for review.

## Checks before publishing

1. Every event URL returns 200. Fake slugs return 404 on iTicket, ShowGo and Afisha, so the check is meaningful.
2. Every image loads, and none is a generic placeholder.
3. Every listing obeys the audience rule and the coverage window.
4. Every date and weekday is correct, with times in Tashkent time.

## Publishing workflow

- **Review period (until 30 Nov 2026):** build to `/preview/`, commit and push, then message Louis with:
  - a short summary of what was added, removed or changed;
  - the preview URLs (`https://tashkent-listings.github.io/preview/music.html` etc.).

  Wait for him to reply "publish". Then rebuild with `live`, commit and push.
- **From 1 Dec 2026:** build straight to `live`, commit and push, and send Louis the summary afterwards.
