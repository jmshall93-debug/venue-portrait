"""Load review CSV exports and derive venue portrait stats."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

COL_DATE = "date"
COL_RATING = "rating"
COL_TEXT = "text"
COL_AUTHOR = "author"
COL_SOURCE = "source"

_COLUMN_ALIASES = {
    "date": COL_DATE,
    "review date": COL_DATE,
    "review_date": COL_DATE,
    "rating": COL_RATING,
    "stars": COL_RATING,
    "star_rating": COL_RATING,
    "score": COL_RATING,
    "text": COL_TEXT,
    "review": COL_TEXT,
    "review_text": COL_TEXT,
    "comment": COL_TEXT,
    "body": COL_TEXT,
    "author": COL_AUTHOR,
    "reviewer": COL_AUTHOR,
    "name": COL_AUTHOR,
    "source": COL_SOURCE,
    "platform": COL_SOURCE,
}

THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "atmosphere": ("terrace", "buzz", "loud", "vibe", "atmosphere", "singing", "chants", "electric"),
    "pint": ("beer", "lager", "ale", "pint", "pricey", "pulled", "drink"),
    "matchday": ("kick-off", "kick off", "matchday", "match day", "pre-match", "pre match", "packed", "busy", "queue", "heaving", "rammed"),
    "food": ("pie", "chips", "kitchen", "food", "menu"),
    "service": ("staff", "bar", "wait", "service", "slow"),
    "screens": ("tv", "tvs", "screen", "screens", "game"),
    "away_fans": ("away fan", "away end", "away fans", "welcome"),
}

QUOTE_MAX_LEN = 120


@dataclass
class ReviewStats:
    """Derived concentration stats for copy and narrate briefs."""

    top_theme: str | None
    top_theme_share_pct: float
    theme_shares_top5: dict[str, float]
    unique_themes: int
    top_positive_theme: str | None
    top_negative_theme: str | None
    rating_std: float
    low_rating_count: int


@dataclass
class ReviewProfile:
    """Computed stats ready for charts and copy."""

    review_count: int
    avg_rating: float
    five_star_pct: float
    rating_std: float
    star_counts: pd.Series
    theme_weights: pd.Series
    theme_count: int
    top_positive_theme: str | None
    top_negative_theme: str | None
    representative_quotes: dict[str, str]
    monthly_avg_rating: pd.Series
    monthly_volume: pd.Series
    stats: ReviewStats


def load_csv(path: str | Path) -> pd.DataFrame:
    """Read CSV and normalize column names."""
    df = pd.read_csv(path)
    rename = {}
    for col in df.columns:
        key = col.strip().lower()
        if key in _COLUMN_ALIASES:
            rename[col] = _COLUMN_ALIASES[key]
    df = df.rename(columns=rename)

    missing = {COL_DATE, COL_RATING, COL_TEXT} - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {', '.join(sorted(missing))}")

    df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors="coerce")
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce")

    bad_rating = df[COL_RATING].isna() | (df[COL_RATING] < 1) | (df[COL_RATING] > 5)
    if bad_rating.any():
        n = int(bad_rating.sum())
        raise ValueError(f"CSV has {n} row(s) with invalid rating (need 1-5)")

    df[COL_RATING] = df[COL_RATING].astype(int)
    return df


def _star_histogram(ratings: pd.Series) -> pd.Series:
    counts = ratings.value_counts().sort_index()
    for star in range(1, 6):
        if star not in counts.index:
            counts.loc[star] = 0
    return counts.sort_index()


def _themes_for_text(text: object) -> list[str]:
    if pd.isna(text) or not str(text).strip():
        return []
    lowered = str(text).lower()
    hits = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            hits.append(theme)
    return hits


def _theme_weights(df: pd.DataFrame) -> pd.Series:
    rows: list[str] = []
    for text in df[COL_TEXT]:
        rows.extend(_themes_for_text(text))
    if not rows:
        return pd.Series(dtype=int)
    return pd.Series(rows).value_counts().sort_values(ascending=False)


def _theme_weights_for_frame(frame: pd.DataFrame) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype=int)
    return _theme_weights(frame)


def _excerpt(text: str, max_len: int = QUOTE_MAX_LEN) -> str:
    text = re.sub(r"\s+", " ", str(text).strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "..."


def _representative_quotes(df: pd.DataFrame, themes: pd.Series) -> dict[str, str]:
    quotes: dict[str, str] = {}
    used_excerpts: set[str] = set()
    used_prefixes: set[str] = set()
    prefix_len = 50
    for theme in themes.index:
        mask = df[COL_TEXT].apply(lambda t: theme in _themes_for_text(t))
        matches = df.loc[mask].sort_values(COL_RATING, ascending=False)
        for _, row in matches.iterrows():
            excerpt = _excerpt(row[COL_TEXT])
            prefix = excerpt[:prefix_len]
            if excerpt in used_excerpts or prefix in used_prefixes:
                continue
            quotes[theme] = excerpt
            used_excerpts.add(excerpt)
            used_prefixes.add(prefix)
            break
        if theme not in quotes and not matches.empty:
            quotes[theme] = _excerpt(matches.iloc[0][COL_TEXT])
    return quotes


def _monthly_series(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    dated = df.dropna(subset=[COL_DATE]).copy()
    if dated.empty:
        empty = pd.Series(dtype=float)
        return empty, empty

    dated["month"] = dated[COL_DATE].dt.to_period("M")
    monthly_avg = dated.groupby("month")[COL_RATING].mean().round(2)
    monthly_volume = dated.groupby("month").size()
    monthly_avg.index = monthly_avg.index.astype(str)
    monthly_volume.index = monthly_volume.index.astype(str)
    return monthly_avg, monthly_volume


def _theme_shares_top5(theme_weights: pd.Series, review_count: int) -> dict[str, float]:
    if theme_weights.empty or review_count == 0:
        return {}
    return {
        str(theme): round(100 * count / review_count, 1)
        for theme, count in theme_weights.head(5).items()
    }


def _compute_stats(
    review_count: int,
    ratings: pd.Series,
    theme_weights: pd.Series,
    top_positive_theme: str | None,
    top_negative_theme: str | None,
) -> ReviewStats:
    top_theme = str(theme_weights.index[0]) if not theme_weights.empty else None
    top_share = round(100 * theme_weights.iloc[0] / review_count, 1) if top_theme else 0.0
    return ReviewStats(
        top_theme=top_theme,
        top_theme_share_pct=top_share,
        theme_shares_top5=_theme_shares_top5(theme_weights, review_count),
        unique_themes=len(theme_weights),
        top_positive_theme=top_positive_theme,
        top_negative_theme=top_negative_theme,
        rating_std=round(float(ratings.std(ddof=0)), 2),
        low_rating_count=int((ratings <= 3).sum()),
    )


def analyze(df: pd.DataFrame) -> ReviewProfile:
    """Turn a normalized dataframe into chart-ready review stats."""
    ratings = df[COL_RATING]
    review_count = len(df)
    five_star_pct = round(100 * (ratings == 5).sum() / review_count, 1)
    theme_weights = _theme_weights(df)
    low_rated = df.loc[ratings <= 3]
    low_theme_weights = _theme_weights_for_frame(low_rated)

    top_positive_theme = str(theme_weights.index[0]) if not theme_weights.empty else None
    top_negative_theme = str(low_theme_weights.index[0]) if not low_theme_weights.empty else None
    monthly_avg_rating, monthly_volume = _monthly_series(df)

    stats = _compute_stats(
        review_count,
        ratings,
        theme_weights,
        top_positive_theme,
        top_negative_theme,
    )

    return ReviewProfile(
        review_count=review_count,
        avg_rating=round(float(ratings.mean()), 2),
        five_star_pct=five_star_pct,
        rating_std=stats.rating_std,
        star_counts=_star_histogram(ratings),
        theme_weights=theme_weights,
        theme_count=len(theme_weights),
        top_positive_theme=top_positive_theme,
        top_negative_theme=top_negative_theme,
        representative_quotes=_representative_quotes(df, theme_weights),
        monthly_avg_rating=monthly_avg_rating,
        monthly_volume=monthly_volume,
        stats=stats,
    )


def analyze_file(path: str | Path) -> ReviewProfile:
    return analyze(load_csv(path))


def narrative_brief(profile: ReviewProfile, venue_name: str = "The 90th Minute") -> dict:
    """Structured facts for templates and optional LLM - no raw review rows."""
    s = profile.stats
    return {
        "venue": venue_name,
        "review_count": profile.review_count,
        "avg_rating": profile.avg_rating,
        "five_star_pct": profile.five_star_pct,
        "rating_std": profile.rating_std,
        "theme_count": profile.theme_count,
        "top_theme": s.top_theme,
        "top_theme_share_pct": s.top_theme_share_pct,
        "theme_shares_top5": s.theme_shares_top5,
        "unique_themes": s.unique_themes,
        "top_positive_theme": s.top_positive_theme,
        "top_negative_theme": s.top_negative_theme,
        "low_rating_count": s.low_rating_count,
        "representative_quotes": profile.representative_quotes,
        "monthly_avg_rating": {str(k): float(v) for k, v in profile.monthly_avg_rating.items()},
        "monthly_volume": {str(k): int(v) for k, v in profile.monthly_volume.items()},
        "polarized": profile.rating_std >= 1.0 and s.low_rating_count >= 10,
        "steady_favourite": profile.avg_rating >= 4.0 and profile.five_star_pct < 35,
    }


def _format_histogram(star_counts: pd.Series) -> str:
    lines = []
    max_count = int(star_counts.max()) or 1
    for star in range(1, 6):
        count = int(star_counts.get(star, 0))
        bar = "#" * round(24 * count / max_count) if count else ""
        lines.append(f"  {star} star: {count:3d}  {bar}")
    return "\n".join(lines)


if __name__ == "__main__":
    default = Path(__file__).parent / "data" / "sample_pub_reviews.csv"
    profile = analyze_file(default)
    brief = narrative_brief(profile)

    print(f"Reviews:     {profile.review_count}")
    print(f"Avg rating:  {profile.avg_rating}")
    print(f"5-star %:    {profile.five_star_pct}%")
    print(f"Themes:      {profile.theme_count}")
    print("Star histogram:")
    print(_format_histogram(profile.star_counts))

    print("\nTop themes:")
    for theme, count in profile.theme_weights.head(5).items():
        pct = brief["theme_shares_top5"].get(str(theme), 0)
        print(f"  {theme}: {count} mentions ({pct}% of reviews)")

    print("\nSample quotes:")
    for theme, quote in list(profile.representative_quotes.items())[:2]:
        print(f'  [{theme}] "{quote}"')

    from narrate import template_portrait

    portrait = template_portrait(profile)
    print("\nPortrait:")
    print(portrait.title)
    print(portrait.label)
    print(portrait.interpretation)

    print(f"\nBrief keys: {list(brief.keys())}")
