# Tashkent Expat Listings: how the weekly refresh works

Owner: Louis Train (GitHub account `tashkent-listings`). The site is Google Sites. Each category page there embeds one of these GitHub Pages files by URL, so pushing to `main` updates the live site:

- https://tashkent-listings.github.io/art.html
- https://tashkent-listings.github.io/music.html
- https://tashkent-listings.github.io/theatre.html (Theatre & Film)
- https://tashkent-listings.github.io/dance.html
- https://tashkent-listings.github.io/sport.html
- https://tashkent-listings.github.io/calendar.html (all five categories, day by day)

## The audience rule (most important)

These are expat listings. Every listing must be in English or not depend on language:

- Allowed: ballet and dance, visual art, photography, sport, circus and other visual shows, films in English, and films with no dialogue.
- Music: include instrumental music (classical, organ, jazz, orchestral film-music and tribute concerts), opera (the words aren't meant to be followed), and music sung in English. International acts singing in other languages are fine (e.g. Cheb Mami).
- Music to leave out: Uzbek and Russian-language pop, estrada, rap and rock, including CIS acts singing in Russian. It depends too much on cultural context. Also leave out shows built around a regional celebrity (e.g. a Turkish TV-series actor with an orchestra).
- Plays, comedy, operetta, talks and kids' shows in Russian or Uzbek are excluded unless they have English surtitles.
- Do not list events outside Tashkent. ShowGo carries many regional concerts in Samarkand, Bukhara, Qarshi and Jizzakh, so check the venue.

## Coverage window

- List only events within 30 days of the run date (run date to run date + 30). `build.py` enforces this: set `RUN_DATE` and it drops dates outside the window. Exhibitions are listed while they are open, even if they close after the window.
- Page titles show the window, e.g. "Music · 31 Oct – 30 Nov 2026". The build writes these automatically.
- Drop anything that has already happened. Drop exhibitions that have closed.

## Tickets rule

- List an event only if tickets are on sale or an entry price is published. Free entry counts.
- Leave out anything with tickets TBA, TBC, "coming soon" or no published price.
- Exception: Cinematica's English-language films are listed from their announced start date even before showtimes go on sale (see Cinematica below). `build.py` refuses to build if a price contains TBA, TBC, "soon" or similar.
- Re-check each run whether held-back events have gone on sale, and add them when they have.

## Tone

- Describe each listing neutrally. The pages inform; they don't sell.
- State what it is, who performs or made it, the programme, length and age rating, and any practical conditions (language, ticket rules, closures).
- No superlatives or hype ("must-see", "unmissable", "legendary", "don't miss", "world-class"), no exclamation marks, no urging people to book.
- Badges are factual only: language access, "Free", "Few seats left", "Closes …", "New production", age ratings. No promotional badges such as "Big match".
- No subtitle under the page title and no footer note ("Listings checked on…").

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
- **Cinematica English-language films** (Tashkent City Mall): Cinematica shows selected films in English. The titles and start dates are posted monthly on Instagram @englishmovieclubuz. Each title then usually plays nightly at 20:30 for a week, in 2D with no subtitles.
  - List each as an ordinary film at Cinematica. Don't label it "English Movie Club" anywhere (title, badge or placeholder); use the "In English" badge.
  - Use `opens="YYYY-MM-DD"` in build.py. The card shows "From [day]" and is listed until the opening day passes. Meta: "English-language screenings in 2D, no subtitles. Showtimes are published a few days before."
  - Link to `https://cinematica.uz/movies/{id}` (the id from `https://cinematica.uz/api/v1/movies/soon`). If Cinematica hasn't listed the film yet, link to the Instagram account.
  - Posters: `file_poster` (horizontal) from `/api/v1/movies/{id}`. Cinematica's API doesn't flag language.
  - Price: the standard-hall range from current sessions (`/api/v1/repertory/movie/{id}/grouped`; ignore the VIP hall). On 31 Oct 2026 this was 35,000–70,000 UZS.
  - If Instagram can't be read, keep the existing cards and flag it in the summary.
- **kinoxona art cinema** (17 Chimkent St): films are shown in the original language with Russian subtitles. Include only English-language films, plus films with no dialogue. The programme appears about a week ahead on ShowGo (venue "Кинозал Чимкент, 17").
- **CCA Tashkent**: `https://ccat.uz/en/programme/...`. Check the homepage for closure notices.
- **Sport**: Pakhtakor, Uzbekistan national team, big tournaments in Tashkent. Use web search; iTicket's sport category has tickets once they're on sale.

## Building

All listing data lives in `tools/build.py` (the ART, MUSIC, THEATRE, DANCE and SPORT lists). Edit the data there. Items can carry dates beyond the window; the build keeps only the dates inside it. When an event's time differs from day to day, give `times={"YYYY-MM-DD": "19:30", ...}` alongside `dates`; the card and the calendar then show each day's own time.

- Write descriptions in plain English, in your own words, and don't copy source text.
- Badges: "In English", "English surtitles", "No dialogue", "Visual show", "Free", "Few seats left" (under about 60 tickets left), "Closes …", "New production".
- Set `RUN_DATE` to the run date.
- The calendar page is generated from the same five lists; it needs no data of its own. It shows dated events only: single dates and runs of under a week appear on each day. Exhibitions, longer runs (such as the circus) and Cinematica film runs are left off the calendar on purpose and stay on their own pages. The page hides days that have passed, so it stays correct between refreshes.
- `python3 tools/build.py live` writes the pages to the repo root, which is what the site shows.
- `python3 tools/build.py preview` writes them to `/preview/` for review.

## Checks before publishing

1. Every event URL returns 200. Fake slugs return 404 on iTicket, ShowGo and Afisha, so the check is meaningful.
2. Every image loads, and none is a generic placeholder. iTicket sometimes replaces an event's images, which makes the old URL return 403, so re-pull the image URLs from the detail API each run.
3. Every listing obeys the audience rule, the 30-day window, the tickets rule and the tone rule.
4. Every date and weekday is correct, with times in Tashkent time.

## Publishing workflow

- **Review period (until 30 Nov 2026):** build to `/preview/`, commit and push, then message Louis with:
  - a short summary of what was added, removed or changed;
  - the preview URLs (`https://tashkent-listings.github.io/preview/music.html` etc., including `preview/calendar.html`).

  Wait for him to reply "publish". Then rebuild with `live`, commit and push.
- **From 1 Dec 2026:** build straight to `live`, commit and push, and send Louis the summary afterwards.
