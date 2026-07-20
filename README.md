# Venue Portrait

> Review intelligence for hospitality businesses - what customers actually talk about, not just the star average.

**[Live demo](https://venue-portrait-9ytnl8d4uvkcg5sqsbng52.streamlit.app/)** · [Source on GitHub](https://github.com/jmshall93-debug/venue-portrait)

Upload a CSV of customer reviews and get a one-page editorial report: themes, representative quotes, rating trend, and star distribution. Built as a fixed-scope demo for pubs, bars, and restaurants that want clearer signal from Google / TripAdvisor exports.

![Dashboard](assets/hero.png)

---

## Who it is for

Hospitality operators and advisers who already have review exports and need a readable summary for ops or board packs - without buying an enterprise review platform.

Demo data: fictional pub **The 90th Minute** (`data/sample_pub_reviews.csv`).

---

## Features

- Editorial headline and interpretation from the review set
- Stat cards (volume, average rating, 5-star share, themes tagged)
- Representative quotes by theme
- Season arc - monthly average rating
- Theme mention frequency
- Star rating distribution
- Sample dataset included; private exports stay local

---

## Example dashboard

### Charts

![Charts](assets/charts.png)

### Full report walkthrough

![Demo](assets/demo.gif)

---

## Tech stack

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

Export reviews as a CSV with **date**, **rating** (1-5), and **review text**. Optional columns: author, source (Google, TripAdvisor).

Place a private export at `data/private_reviews.csv` (gitignored) or use the bundled sample to explore the UI.
