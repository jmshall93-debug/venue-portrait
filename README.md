# Venue Portrait

Upload a CSV of customer reviews and get a one-page editorial portrait of **what punters actually say**: atmosphere, pint, matchday buzz, food, service. Not just an average star rating.

Sample venue: fictional matchday pub **The 90th Minute**. Python, Streamlit, Plotly. Pitch-night green and lime, split hero, quote strip, review charts.

**Status:** In progress. See [`BUILD_LOG.md`](BUILD_LOG.md). Steps 1-10c done; hero, stats, quotes, and all three charts live in the browser shell.

## Goal

Turn review exports into a **voice of the venue** report a pub owner or marketer can skim in one screen: headline copy, key stats, pulled quotes, and charts for rating trend and recurring themes.

## What's in the report (target)

- **Split hero** - editorial title, label, and interpretation on the left; vertical stat cards on the right (review count, avg rating, 5-star %, theme count)
- **Quote strip** - 2-3 representative excerpts tagged by theme
- **Season arc** - average rating by month (line chart)
- **What gets mentioned** - theme lollipop bars (keyword buckets, no ML)
- **Star shape** - 1-5 histogram
- **Upload** - visitor CSV overrides bundled sample; sidebar hidden

Template copy only in v1 (no AI/Groq). Offline by default.

## How it works

```text
CSV -> parse.py -> ReviewProfile -> narrate.py (copy) + app.py (Streamlit + Plotly)
```

- **`parse.py`** - load CSV, coerce dates/ratings, theme keyword tagging, stats for charts
- **`narrate.py`** - story angles (`MATCHDAY_BUZZ`, `PINT_LED`, `SERVICE_GRUMBLE`, etc.) to title, label, interpretation
- **`app.py`** - pitch-night CSS, split layout, Plotly charts (port **8502** locally)

## Your data

| File | Purpose |
|------|---------|
| `data/sample_pub_reviews.csv` | Bundled demo - 90 synthetic reviews, safe to commit |
| `data/private_reviews.csv` | Your export - gitignored |
| `data/uploads/` | Local upload scratch - gitignored |

**Expected columns** (aliases tolerated): `date`, `rating` (1-5), `text`. Optional: `author`, `source` (Google, TripAdvisor).

**Theme tagging (v1):** rule-based keywords - e.g. atmosphere (terrace, buzz, vibe), pint (beer, lager, ale), matchday (kick-off, queue, busy), food (pie, chips, kitchen), service (staff, bar, wait).

## Run locally

**App (main):** double-click `run.bat` - opens **http://localhost:8502** in the browser.

**Parse smoke test:** double-click `run_parse.bat` - terminal stats only (dev harness).

```powershell
cd "C:\AI dreams\business\venue-portrait"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\run.bat
```

## Deploy

*Planned Step 13-14.*

- GitHub: [github.com/jmshall93-debug/venue-portrait](https://github.com/jmshall93-debug/venue-portrait)
- Streamlit Community Cloud, main file `app.py`

## Out of scope (v1)

Multi-venue picker, AI portrait, sentiment ML, scraping Google directly, compare-two-venues.

## Portfolio blurb

**Venue Portrait** - visual review portrait from a customer-review CSV. Rating arc, theme mentions, star distribution, representative quotes. Python, Streamlit, Plotly. Sample pub data included.

## Handover

Full source, demo data, run instructions. Private review exports stay local. Parse layer separate from UI so charts and copy can change independently.

