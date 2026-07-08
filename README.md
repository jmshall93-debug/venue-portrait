# Venue Portrait

> Editorial review intelligence for pubs, bars, restaurants and hospitality businesses.

**[Live demo on Streamlit Cloud](#live-demo)** · [Source on GitHub](https://github.com/jmshall93-debug/venue-portrait)

Turn a CSV of customer reviews into an editorial report highlighting what customers actually talk about - not just the average star rating.

![Dashboard](assets/hero.png)

---

## Features

- Monthly rating trends
- Representative customer quotes
- Automatic theme tagging from review text
- Rating distribution
- Mention frequency by topic
- Editorial dashboard built with Streamlit

---

## Example Dashboard

### Charts

![Charts](assets/charts.png)

### Full report walkthrough

![Demo](assets/demo.gif)

---

## Tech Stack

- Python
- Streamlit
- Plotly
- Pandas

---

## Architecture

```text
CSV Reviews
      |
      v
parse.py
      |
      v
Theme Extraction
      |
      v
Narrative Generator
      |
      v
Streamlit Dashboard
```

---

## Running locally

```powershell
git clone https://github.com/jmshall93-debug/venue-portrait.git
cd venue-portrait
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\run.bat
```

Opens **http://localhost:8502** in your browser.

---

## Your data

Export reviews as a CSV with **date**, **rating** (1-5), and **review text**. Optional columns: author, source (Google, TripAdvisor). A sample dataset for fictional pub **The 90th Minute** is included in `data/sample_pub_reviews.csv`.

---

## Live demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://venue-portrait.streamlit.app/)

Opens the bundled sample report for **The 90th Minute** (90 reviews, Aug 2025-May 2026).

### Deploy (first time)

1. Sign in at [share.streamlit.io](https://share.streamlit.io).
2. Click **Create app**.
3. Repository: `jmshall93-debug/venue-portrait`, branch: `main`, main file: `app.py`.
4. Click **Deploy**. Copy the `https://….streamlit.app/` URL.
5. Update the badge link above to your live URL and push to `main`.

No secrets or API keys required. The app loads `data/sample_pub_reviews.csv` by default.

---