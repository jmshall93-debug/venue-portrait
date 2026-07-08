"""Template portraits from a review brief."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from parse import ReviewProfile, narrative_brief


class StoryAngle(str, Enum):
    MATCHDAY_BUZZ = "matchday_buzz"
    PINT_LED = "pint_led"
    SERVICE_GRUMBLE = "service_grumble"
    FOOD_SIDEBAR = "food_sidebar"
    POLARIZED = "polarized"
    STEADY_FAVOURITE = "steady_favourite"


@dataclass
class Portrait:
    title: str
    label: str
    interpretation: str
    source: str = "template"


THEME_LABELS = {
    "matchday": "matchday",
    "pint": "the pint",
    "atmosphere": "atmosphere",
    "service": "service",
    "food": "food",
    "screens": "the screens",
    "away_fans": "away fans",
}


def _theme_label(theme: str | None) -> str:
    if not theme:
        return "the reviews"
    return THEME_LABELS.get(theme, theme.replace("_", " "))


def _pick_phrase(key: str, options: list[str]) -> str:
    if not options:
        return ""
    return options[hash(key) % len(options)]


def _pick_story_angle(brief: dict) -> StoryAngle:
    if brief.get("polarized"):
        return StoryAngle.POLARIZED

    if brief.get("steady_favourite"):
        return StoryAngle.STEADY_FAVOURITE

    negative = brief.get("top_negative_theme")
    if negative == "service" and brief.get("low_rating_count", 0) >= 8:
        return StoryAngle.SERVICE_GRUMBLE
    if negative == "food" and brief.get("low_rating_count", 0) >= 6:
        return StoryAngle.FOOD_SIDEBAR

    top = brief.get("top_theme")
    if top == "pint":
        return StoryAngle.PINT_LED
    return StoryAngle.MATCHDAY_BUZZ


def _title_for_angle(angle: StoryAngle, brief: dict) -> str:
    venue = brief.get("venue", "The Venue")
    theme = _theme_label(brief.get("top_theme"))

    if angle == StoryAngle.MATCHDAY_BUZZ:
        return f"{venue}: Matchday Buzz"
    if angle == StoryAngle.PINT_LED:
        return f"{venue}: Pint-Led Praise"
    if angle == StoryAngle.SERVICE_GRUMBLE:
        return f"{venue}: Queue & Grumble"
    if angle == StoryAngle.FOOD_SIDEBAR:
        return f"{venue}: Pie Before Kick-Off"
    if angle == StoryAngle.POLARIZED:
        return f"{venue}: Love It, Moan Anyway"
    return f"{venue}: Steady Favourite"


def _label_for_angle(angle: StoryAngle, brief: dict) -> str:
    venue = brief.get("venue", "The venue")
    theme = _theme_label(brief.get("top_theme"))
    avg = brief.get("avg_rating", 0)
    key = venue

    if angle == StoryAngle.MATCHDAY_BUZZ:
        endings = [
            f"Punters talk {theme} first, ratings second.",
            f"A proper pre-match pub where {theme} sets the tone.",
            f"Built for Saturdays - {theme} carries the room.",
        ]
    elif angle == StoryAngle.PINT_LED:
        endings = [
            f"The pint gets mentioned as often as the result.",
            f"Beer quality leads; {theme} is the recurring headline.",
            f"Fair praise for the pour, even when it gets rammed.",
        ]
    elif angle == StoryAngle.SERVICE_GRUMBLE:
        endings = [
            f"Atmosphere saves it when {theme} slips on busy days.",
            f"The buzz is real; {theme} is where patience wears thin.",
            f"Fans keep coming back despite queue-and-wait grumbles.",
        ]
    elif angle == StoryAngle.FOOD_SIDEBAR:
        endings = [
            f"Pie and chips in the mix, but {theme} draws the complaints.",
            f"Drinks and buzz land well; {theme} is hit-and-miss.",
            f"Matchday fuel on the menu - not always on time.",
        ]
    elif angle == StoryAngle.POLARIZED:
        endings = [
            f"Strong on {theme}, split on the slower moments.",
            f"Four-star average with vocal grumbles in the mix.",
            f"Beloved terrace pub - not every visit lands the same.",
        ]
    else:
        endings = [
            f"Reliable {avg} stars across the season.",
            f"Consistent praise without much drama.",
            f"A settled local favourite in the reviews.",
        ]

    text = _pick_phrase(key, endings)
    return text[0].upper() + text[1:] if text else ""


def _interpretation_for_angle(angle: StoryAngle, brief: dict) -> str:
    venue = brief.get("venue", "This pub")
    top = _theme_label(brief.get("top_theme"))
    negative = _theme_label(brief.get("top_negative_theme"))
    count = brief.get("review_count", 0)
    avg = brief.get("avg_rating", 0)
    five = brief.get("five_star_pct", 0)

    if angle == StoryAngle.MATCHDAY_BUZZ:
        return (
            f"Across {count} reviews, {top} dominates what punters mention. "
            f"The average sits at {avg} stars - fans describe a pub that feels alive before kick-off, "
            f"even when queues and noise come with the territory."
        )
    if angle == StoryAngle.PINT_LED:
        return (
            f"Reviewers keep returning to {top}: well-kept lager, fair matchday prices, "
            f"and a room that fills early. {five}% hit five stars - the pint is part of the ritual, not an afterthought."
        )
    if angle == StoryAngle.SERVICE_GRUMBLE:
        return (
            f"The mood stays upbeat, but {negative} shows up most in lower-rated reviews. "
            f"Busy matchdays expose the bar queue; atmosphere and terrace buzz still pull people back."
        )
    if angle == StoryAngle.FOOD_SIDEBAR:
        return (
            f"Food mentions skew mixed - pie and chips land when the kitchen keeps pace, "
            f"but waits on packed Saturdays feed the grumbles. {venue} reads as a drinks-and-buzz pub first."
        )
    if angle == StoryAngle.POLARIZED:
        return (
            f"Ratings spread from glowing praise to specific complaints - often about {negative} on hectic days. "
            f"The overall picture is still positive at {avg} stars, with matchday energy as the draw."
        )
    return (
        f"A settled {avg}-star picture across the season: not flashy, not flawless, "
        f"but clearly a go-to for {top} and pre-match routine."
    )


def template_portrait(profile: ReviewProfile, venue_name: str | None = None) -> Portrait:
    brief = narrative_brief(profile, venue_name or "The 90th Minute")
    angle = _pick_story_angle(brief)
    return Portrait(
        title=_title_for_angle(angle, brief),
        label=_label_for_angle(angle, brief),
        interpretation=_interpretation_for_angle(angle, brief),
        source="template",
    )


if __name__ == "__main__":
    from pathlib import Path

    from parse import analyze_file

    sample = Path(__file__).parent / "data" / "sample_pub_reviews.csv"
    profile = analyze_file(sample)
    portrait = template_portrait(profile)

    print(portrait.title)
    print(portrait.label)
    print()
    print(portrait.interpretation)
