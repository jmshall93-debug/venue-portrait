"""Capture README screenshots from a running Venue Portrait app.

Usage:
    .\\.venv\\Scripts\\python.exe -m streamlit run app.py --server.port 8502 --server.headless true
    .\\.venv\\Scripts\\python.exe scripts\\capture_readme_assets.py

Or pass --start to launch Streamlit automatically.

Requires playwright + pillow in the active venv (local capture only; not a Cloud dependency).
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
URL = "http://localhost:8502"
VIEWPORT = {"width": 1280, "height": 900}
PY = Path(sys.executable)


def _wait_for_server(timeout: int = 90) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(URL, timeout=2):
                return
        except Exception:
            time.sleep(1)
    raise RuntimeError(f"Streamlit did not respond at {URL}")


def _wait_for_app(page) -> None:
    page.goto(URL, wait_until="networkidle", timeout=90_000)
    page.wait_for_selector(".venue-caption", timeout=60_000)
    page.wait_for_selector(".portrait-title", timeout=30_000)
    page.wait_for_function(
        '() => document.querySelectorAll(\'[data-testid="stPlotlyChart"]\').length >= 3',
        timeout=60_000,
    )
    page.wait_for_timeout(2500)


def _capture_hero(page) -> None:
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)
    bounds = page.evaluate(
        """
        (pad) => {
            const start = document.querySelector('.venue-caption');
            const quotes = document.querySelector('.quote-strip');
            if (!start || !quotes) return null;
            const y = Math.max(0, start.getBoundingClientRect().top - pad);
            const bottom = quotes.getBoundingClientRect().bottom;
            return {
                x: 0,
                y,
                width: window.innerWidth,
                height: Math.max(120, bottom - y + pad),
            };
        }
        """,
        12,
    )
    if not bounds:
        raise RuntimeError("Hero region not found")
    page.screenshot(path=str(ASSETS / "hero.png"), clip=bounds)


def _capture_charts(page) -> None:
    page.locator(".section-label", has_text="Charts").first.scroll_into_view_if_needed()
    page.wait_for_timeout(1500)
    # Expand Streamlit main so full-page screenshot includes below-the-fold charts.
    page.evaluate(
        """
        () => {
            const main = document.querySelector('[data-testid="stMain"]');
            const app = document.querySelector('.stApp');
            if (!main || !app) return;
            const h = main.scrollHeight;
            main.style.height = `${h}px`;
            main.style.overflow = 'visible';
            app.style.height = `${h}px`;
            app.style.overflow = 'visible';
        }
        """
    )
    page.wait_for_timeout(800)
    bounds = page.evaluate(
        """
        (pad) => {
            const labels = [...document.querySelectorAll('.section-label')];
            const start = labels.find(el => el.textContent.trim() === 'Charts');
            const charts = [...document.querySelectorAll('[data-testid="stPlotlyChart"]')];
            if (!start || charts.length < 3) return null;
            let bottom = 0;
            for (const chart of charts) {
                bottom = Math.max(bottom, chart.getBoundingClientRect().bottom + window.scrollY);
            }
            const y = Math.max(0, start.getBoundingClientRect().top + window.scrollY - pad);
            return {
                x: 0,
                y,
                width: window.innerWidth,
                height: Math.max(120, bottom - y + pad),
            };
        }
        """,
        16,
    )
    if not bounds:
        raise RuntimeError("Charts region not found")

    source_path = ASSETS / "_charts-source.png"
    page.screenshot(path=str(source_path), full_page=True)
    scale = 2
    with Image.open(source_path) as image:
        top = int(bounds["y"] * scale)
        bottom = min(image.height, int((bounds["y"] + bounds["height"]) * scale))
        crop = (0, top, min(image.width, int(bounds["width"] * scale)), bottom)
        image.crop(crop).save(ASSETS / "charts.png")
    source_path.unlink(missing_ok=True)
    print(f"charts crop css={bounds['width']}x{bounds['height']} px scale2 -> {(bottom-top)}h")


def _capture_demo_gif(page) -> None:
    """Short scroll walkthrough for README."""
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(600)

    frames: list[Image.Image] = []
    scroll_ys = page.evaluate(
        """
        () => {
            const main = document.querySelector('[data-testid="stMain"]') || document.body;
            const maxY = Math.max(0, main.scrollHeight - window.innerHeight);
            if (maxY < 80) return [0];
            const steps = 5;
            return Array.from({ length: steps }, (_, i) => Math.round((maxY * i) / (steps - 1)));
        }
        """
    )

    for y in scroll_ys:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(700)
        raw = page.screenshot(type="png")
        frames.append(Image.open(io.BytesIO(raw)).convert("P", palette=Image.ADAPTIVE))

    if not frames:
        raise RuntimeError("No frames captured for demo.gif")

    out = ASSETS / "demo.gif"
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=700,
        loop=0,
        optimize=True,
    )


def capture() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=2)
        _wait_for_app(page)
        _capture_hero(page)
        _capture_charts(page)
        _capture_demo_gif(page)
        browser.close()

    for name in ("hero.png", "charts.png", "demo.gif"):
        path = ASSETS / name
        if not path.exists():
            raise RuntimeError(f"Missing capture: {path}")
        print(f"wrote {path} ({path.stat().st_size:,} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture Venue Portrait README assets.")
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start Streamlit on port 8502 before capturing.",
    )
    args = parser.parse_args()

    streamlit_proc = None
    if args.start:
        streamlit_proc = subprocess.Popen(
            [
                str(PY),
                "-m",
                "streamlit",
                "run",
                "app.py",
                "--server.port",
                "8502",
                "--server.headless",
                "true",
            ],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _wait_for_server()

    try:
        capture()
    finally:
        if streamlit_proc is not None:
            streamlit_proc.terminate()
            streamlit_proc.wait(timeout=15)


if __name__ == "__main__":
    main()
