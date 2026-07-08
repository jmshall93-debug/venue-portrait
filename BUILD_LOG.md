# Venue Portrait - build log

**Status:** Paused - portfolio #2  
**Clock:** Stopped at 2026-06-16 15:53:02 +03:00  
**Session started:** 2026-06-16 15:24:52 +03:00  
**Session ended:** 2026-06-16 15:53:02 +03:00  
**This session:** ~28m (Steps 3-9, layout fixes, app running)  
**Realistic dev time (total):** ~49m so far

| Block | When | Dev time |
|-------|------|----------|
| Steps 1-2 - scaffold + sample CSV | 2026-06-11 | ~11m |
| Cleanup + README + folder consolidation | 2026-06-15 | ~10m |
| Steps 3-9 - parse, narrate, app shell, hero, stats, quotes | 2026-06-16 | ~28m |
| **Total** | | **~49m** |

Granular build: one step per review. No git push or deploy until Steps 13-14.

**Project path:** `C:\AI dreams\business\venue-portrait`

## Clock rules

- **Start** when you say go on build work (e.g. Step 3).
- **Do not stop** between steps. Your inspection, testing, and chat in the same session all count.
- **Stop** only when you say **end session**, **stop clock**, or similar.
- Pauses for "continue" between steps are not clock stops.

## Milestones

- Step 0 - `README.md` (project goal and target spec in-repo)
- Step 1 - folder skeleton (requirements, gitignore, data/)
- Step 2 - sample_pub_reviews.csv (90 reviews, The 90th Minute, Aug 2025-May 2026)
- Step 3 - `parse.py` load + basic stats (CLI)
- Step 4 - themes, quotes, monthly arc, `ReviewProfile`, `narrative_brief()`
- Step 5 - `narrate.py` + CLI portrait output
- Step 6 - `app.py` pitch-night shell, `run.bat`, `.streamlit/config.toml`
- Step 7 - split hero, portrait copy
- Step 8 - stat cards (2x2 grid)
- Step 9 - quote strip (3 columns)
- Step 10a - season arc line chart
- Step 10b - theme lollipop bars
- Step 10c - star histogram

## Next up

- Step 11 - CSV upload override

## Data spec

### Files

| File | Purpose |
|------|---------|
| `data/sample_pub_reviews.csv` | Bundled demo - 90 synthetic reviews, safe to commit |
| `data/private_reviews.csv` | Your export - gitignored |
| `data/uploads/` | Local upload scratch - gitignored |

### Expected columns

Aliases tolerated for column names.

| Column | Required | Notes |
|--------|----------|-------|
| `date` | Yes | Review date |
| `rating` | Yes | Integer 1-5 |
| `text` | Yes | Review body |
| `author` | No | Reviewer name |
| `source` | No | e.g. Google, TripAdvisor |

### Theme tagging

Rule-based keywords (no ML). Themes in `parse.py`:

- **atmosphere** - terrace, buzz, vibe, singing, electric
- **pint** - beer, lager, ale, pint, pulled
- **matchday** - kick-off, matchday, packed, busy, queue, heaving
- **food** - pie, chips, kitchen, food, menu
- **service** - staff, bar, wait, service, slow
- **screens** - tv, screen, game
- **away_fans** - away fan, away end, welcome

### Dev harness

`run_parse.bat` - terminal stats only (parse smoke test, no browser).

### Out of scope

Multi-venue picker, AI portrait, sentiment ML, scraping Google directly, compare-two-venues.

Template copy only (no Groq/LLM). Offline by default.

## Links

- Repo: https://github.com/jmshall93-debug/venue-portrait
- Live: https://venue-portrait.streamlit.app/ (set on first Streamlit Cloud deploy)
