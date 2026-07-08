"""Venue Portrait - Streamlit UI."""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import narrate
import parse
from narrate import template_portrait
from parse import ReviewProfile, analyze_file

DATA_DIR = Path(__file__).parent / "data"
SAMPLE_CSV = DATA_DIR / "sample_pub_reviews.csv"
VENUE_NAME = "The 90th Minute"

BG = "#0a1210"
SURFACE = "#111a16"
BORDER = "#1f2e28"
TEXT = "#e8ede9"
MUTED = "#8fa39a"
ACCENT = "#84cc16"
ACCENT_DIM = "#4d7c0f"
CREAM = "#f4f1e8"

CHART_HEIGHT = 300
SMALL_CHART_HEIGHT = 280
PLOTLY_CONFIG = {"displayModeBar": False}

CHART_LAYOUT = dict(
    margin=dict(t=48, l=12, r=12, b=12),
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(color=TEXT, size=12, family="DM Sans, Segoe UI, system-ui, sans-serif"),
    title=dict(font=dict(size=13, color=ACCENT), x=0, xanchor="left"),
)

PAGE_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
.stApp {{
    background:
        radial-gradient(ellipse 85% 50% at 12% -10%, rgba(132, 204, 22, 0.12) 0%, transparent 55%),
        {BG};
    color: {TEXT};
}}
.block-container {{
    font-family: "DM Sans", Segoe UI, system-ui, sans-serif;
    padding-top: 1.25rem;
    padding-bottom: 1rem;
    max-width: 1040px;
}}
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {{
    gap: 0.35rem;
}}
#MainMenu, footer, header[data-testid="stHeader"] {{ display: none; }}
[data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display: none; }}
.hero-row {{
    align-items: start;
}}
.stat-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.55rem;
}}
.venue-caption {{
    color: {ACCENT};
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 0.5rem 0;
}}
.portrait-title {{
    color: {CREAM};
    font-size: 2.15rem;
    font-weight: 700;
    line-height: 1.15;
    margin: 0 0 0.75rem 0;
}}
.portrait-label {{
    color: {TEXT};
    font-size: 1.05rem;
    font-weight: 500;
    line-height: 1.45;
    margin: 0 0 1rem 0;
}}
.portrait-body {{
    color: {MUTED};
    font-size: 0.95rem;
    line-height: 1.65;
    margin: 0;
    max-width: 36rem;
}}
.stat-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 0.65rem 0.85rem;
    margin: 0;
}}
.stat-label {{
    color: {MUTED};
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 0.25rem 0;
}}
.stat-value {{
    color: {CREAM};
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0;
}}
.stat-value-accent {{
    color: {ACCENT};
}}
.quote-strip {{
    margin-top: 0.85rem;
    margin-bottom: 1.25rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.65rem;
}}
.quote-card {{
    border-left: 3px solid {ACCENT};
    padding: 0.65rem 0.75rem 0.65rem 0.85rem;
    background: rgba(17, 26, 22, 0.65);
    border-radius: 0 8px 8px 0;
    height: 100%;
}}
.quote-text {{
    color: {CREAM};
    font-style: italic;
    font-size: 0.95rem;
    line-height: 1.55;
    margin: 0 0 0.35rem 0;
}}
.quote-tag {{
    color: {ACCENT_DIM};
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}
.section-label {{
    color: {ACCENT};
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1.35rem 0 0.5rem 0;
    padding-top: 0.85rem;
    border-top: 1px solid {BORDER};
}}
[data-testid="stPlotlyChart"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 0.35rem;
    margin-bottom: 0.35rem;
}}
</style>
"""


def _layout(height: int = CHART_HEIGHT, **extra):
    return {**CHART_LAYOUT, "height": height, **extra}


def _apply_axes(fig: go.Figure, show_y_grid: bool = False) -> go.Figure:
    fig.update_xaxes(
        showgrid=False,
        linecolor=BORDER,
        tickcolor=MUTED,
        tickfont=dict(color=MUTED, size=10),
    )
    fig.update_yaxes(
        showgrid=show_y_grid,
        gridcolor=BORDER,
        gridwidth=0.5,
        zeroline=False,
        linecolor=BORDER,
        tickcolor=MUTED,
        tickfont=dict(color=MUTED, size=10),
    )
    return fig


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _lerp_hex(low: str, high: str, t: float) -> str:
    r1, g1, b1 = _hex_to_rgb(low)
    r2, g2, b2 = _hex_to_rgb(high)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    )


def _bar_fill_colors(values: list[int] | list[float], low: str, high: str) -> list[str]:
    if not values:
        return []
    vmin, vmax = min(values), max(values)
    if vmax == vmin:
        return [high] * len(values)
    return [_lerp_hex(low, high, (v - vmin) / (vmax - vmin)) for v in values]


def _format_month(month_key: str) -> str:
    year, month = month_key.split("-")
    labels = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    return f"{labels[int(month) - 1]} '{year[2:]}"


def _theme_label(theme: str) -> str:
    return theme.replace("_", " ")


def season_arc_chart(profile: ReviewProfile) -> go.Figure | None:
    monthly = profile.monthly_avg_rating
    if monthly.empty:
        return None

    months = monthly.index.tolist()
    labels = [_format_month(str(m)) for m in months]
    ratings = monthly.values.tolist()
    volumes = [int(profile.monthly_volume.get(m, 0)) for m in months]

    fig = go.Figure(
        go.Scatter(
            x=labels,
            y=ratings,
            mode="lines+markers",
            line=dict(color=ACCENT, width=2),
            marker=dict(color=CREAM, size=8, line=dict(color=ACCENT, width=2)),
            customdata=volumes,
            hovertemplate="%{x}<br>Avg rating: %{y:.2f}<br>Reviews: %{customdata}<extra></extra>",
        )
    )
    fig.update_layout(
        **_layout(
            yaxis=dict(range=[1, 5], dtick=0.5, title=None),
            xaxis_title=None,
            yaxis_title=None,
        )
    )
    fig.update_layout(title=dict(text="Season arc", font=dict(size=13, color=ACCENT), x=0, xanchor="left"))
    return _apply_axes(fig, show_y_grid=True)


def theme_lollipop_chart(profile: ReviewProfile, limit: int = 7) -> go.Figure | None:
    weights = profile.theme_weights.head(limit).sort_values(ascending=True)
    if weights.empty:
        return None

    fig = go.Figure()
    for theme, count in weights.items():
        label = _theme_label(str(theme))
        fig.add_trace(
            go.Scatter(
                x=[0, int(count)],
                y=[label, label],
                mode="lines+markers",
                line=dict(color=ACCENT, width=2),
                marker=dict(size=[0, 10], color=ACCENT),
                showlegend=False,
                hovertemplate=f"{label}<br>Mentions: {int(count)}<extra></extra>",
            )
        )

    fig.update_layout(
        **_layout(
            height=SMALL_CHART_HEIGHT,
            margin=dict(t=48, l=12, r=16, b=12),
            xaxis=dict(title=None, rangemode="tozero"),
            yaxis=dict(
                title=None,
                categoryorder="array",
                categoryarray=weights.index.map(_theme_label).tolist(),
                automargin=True,
            ),
        )
    )
    fig.update_layout(title=dict(text="What gets mentioned", font=dict(size=13, color=MUTED), x=0, xanchor="left"))
    return _apply_axes(fig)


def star_histogram_chart(profile: ReviewProfile) -> go.Figure | None:
    counts = profile.star_counts
    if counts.empty:
        return None

    stars = list(range(1, 6))
    values = [int(counts.get(star, 0)) for star in stars]
    colors = _bar_fill_colors(values, ACCENT_DIM, ACCENT)

    fig = go.Figure(
        go.Bar(
            x=[f"{star} star" for star in stars],
            y=values,
            marker=dict(color=colors, line=dict(width=0)),
            hovertemplate="%{x}<br>Reviews: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        **_layout(
            height=SMALL_CHART_HEIGHT,
            margin=dict(t=48, l=12, r=12, b=40),
            xaxis_title=None,
            yaxis_title=None,
        )
    )
    fig.update_layout(title=dict(text="Star shape", font=dict(size=13, color=MUTED), x=0, xanchor="left"))
    return _apply_axes(fig)


def _stat_card(label: str, value: str, accent: bool = False) -> str:
    value_class = "stat-value stat-value-accent" if accent else "stat-value"
    return (
        '<div class="stat-card">'
        f'<p class="stat-label">{label}</p>'
        f'<p class="{value_class}">{value}</p>'
        "</div>"
    )


def _quote_card(theme: str, quote: str) -> str:
    tag = theme.replace("_", " ")
    return (
        '<div class="quote-card">'
        f'<p class="quote-text">"{quote}"</p>'
        f'<p class="quote-tag">{tag}</p>'
        "</div>"
    )


@st.cache_data
def load_profile():
    return analyze_file(SAMPLE_CSV)


def main() -> None:
    st.set_page_config(
        page_title="Venue Portrait",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(PAGE_CSS, unsafe_allow_html=True)

    profile = load_profile()
    portrait = template_portrait(profile, VENUE_NAME)

    st.markdown(f'<p class="venue-caption">Venue Portrait / {VENUE_NAME}</p>', unsafe_allow_html=True)

    left, right = st.columns([1.2, 0.8], gap="medium")

    with left:
        st.markdown(f'<h1 class="portrait-title">{portrait.title}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="portrait-label">{portrait.label}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="portrait-body">{portrait.interpretation}</p>', unsafe_allow_html=True)

    with right:
        stats = (
            _stat_card("Reviews", str(profile.review_count))
            + _stat_card("Avg rating", f"{profile.avg_rating:.2f}", accent=True)
            + _stat_card("5-star share", f"{profile.five_star_pct:.1f}%")
            + _stat_card("Themes tagged", str(profile.theme_count))
        )
        st.markdown(f'<div class="stat-grid">{stats}</div>', unsafe_allow_html=True)

    cards = [_quote_card(theme, quote) for theme, quote in list(profile.representative_quotes.items())[:3]]
    quotes_html = f'<div class="quote-strip">{"".join(cards)}</div>'
    st.markdown(quotes_html, unsafe_allow_html=True)

    st.markdown('<p class="section-label">Charts</p>', unsafe_allow_html=True)

    arc_fig = season_arc_chart(profile)
    if arc_fig is None:
        st.warning("No dated reviews for a season arc.")
    else:
        st.plotly_chart(arc_fig, width="stretch", config=PLOTLY_CONFIG)

    left_chart, right_chart = st.columns(2)
    with left_chart:
        theme_fig = theme_lollipop_chart(profile)
        if theme_fig is None:
            st.warning("No theme mentions in this export.")
        else:
            st.plotly_chart(theme_fig, width="stretch", config=PLOTLY_CONFIG)

    with right_chart:
        star_fig = star_histogram_chart(profile)
        if star_fig is None:
            st.warning("No star ratings in this export.")
        else:
            st.plotly_chart(star_fig, width="stretch", config=PLOTLY_CONFIG)


main()
