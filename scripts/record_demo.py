"""Record the README demo GIF from the real app (D-074, D-075).

Starts the Streamlit app on the committed Qwen v0.1 snapshot with no model backend, drives it
with a headless browser through the demo script (kickoff section 11), and writes
docs/assets/demo.gif. Re-run it after any change to the app or the snapshot:

    pip install -e ".[demo]" && playwright install chromium   # once
    python scripts/record_demo.py

The cases are ones the v0.1 snapshot routes as labeled (D-075); the closing card says so.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "demo.gif"
VIEW = (1440, 900)
WIDTH = 1080  # GIF width after scaling
BAND = 64  # caption band height, after scaling
INK, PAPER, ACCENT = (255, 255, 255), (24, 32, 48), (120, 200, 255)


@dataclass
class Frame:
    image: Image.Image
    caption: str
    seconds: float


# --- App ----------------------------------------------------------------------------------------


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_app(port: int, state: str) -> subprocess.Popen:
    env = {**os.environ, "PRIORAUTH_APP_STATE": state}
    env.pop("PRIORAUTH_BACKEND", None)  # the hosted demo has no backend (D-068)
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(ROOT / "app" / "streamlit_app.py"),
         "--server.headless", "true", "--server.port", str(port),
         "--browser.gatherUsageStats", "false", "--theme.base", "light"],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )  # fmt: skip
    for _ in range(60):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1)
            return proc
        except OSError:
            time.sleep(1)
    proc.kill()
    raise SystemExit("the app did not start")


# --- Browser steps ------------------------------------------------------------------------------


def settle(page, ms: int = 1500) -> None:
    page.wait_for_load_state("networkidle")
    page.wait_for_function(
        "() => !document.querySelector('[data-testid=\"stStatusWidget\"] [data-testid]')"
    )
    page.wait_for_timeout(ms)


def go(page, base: str, path: str) -> None:
    page.goto(f"{base}/{path}")
    page.wait_for_selector("h1", timeout=60_000)
    settle(page)


def pick(page, label: str, text: str) -> None:
    box = page.locator('[data-testid="stSelectbox"]').filter(has_text=label).first
    box.click()
    page.keyboard.type(text)
    page.get_by_role("option").filter(has_text=text).first.click()
    settle(page)
    page.evaluate("document.activeElement && document.activeElement.blur()")
    page.wait_for_timeout(300)


def scroll_to(page, text: str, offset: int = 120) -> None:
    page.get_by_text(text, exact=True).first.scroll_into_view_if_needed()
    page.evaluate(
        """([t, off]) => {
            const el = [...document.querySelectorAll('h1,h2,h3,p,span,div')]
              .find(e => e.childElementCount === 0 && e.textContent.trim() === t);
            const main = document.querySelector('[data-testid="stMain"]')
              || document.scrollingElement;
            if (el) main.scrollTop += el.getBoundingClientRect().top - off;
        }""",
        [text, offset],
    )
    page.wait_for_timeout(600)


def shot(page) -> Image.Image:
    path = Path(tempfile.mkstemp(suffix=".png")[1])
    page.screenshot(path=str(path))
    img = Image.open(path).convert("RGB")
    path.unlink()
    return img


# --- Frames -------------------------------------------------------------------------------------


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "Arial Bold.ttf", "Arial.ttf"]
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def captioned(img: Image.Image, caption: str) -> Image.Image:
    h = round(img.height * WIDTH / img.width)
    out = Image.new("RGB", (WIDTH, h + BAND), PAPER)
    out.paste(img.resize((WIDTH, h), Image.LANCZOS), (0, 0))
    d = ImageDraw.Draw(out)
    d.text((24, h + BAND // 2), caption, font=font(20, bold=True), fill=INK, anchor="lm")
    return out


def card(title: str, lines: list[str], size: tuple[int, int]) -> Image.Image:
    img = Image.new("RGB", size, PAPER)
    d = ImageDraw.Draw(img)
    y = size[1] // 2 - 40 * (len(lines) + 2) // 2
    d.text((60, y), title, font=font(40, bold=True), fill=ACCENT)
    y += 80
    for line in lines:
        d.text((60, y), line, font=font(24), fill=INK)
        y += 40
    return img


def record(base: str) -> list[Frame]:
    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    frames: list[Frame] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": VIEW[0], "height": VIEW[1]})

        go(page, base, "")
        frames.append(Frame(shot(page), "Inbox: each request on its CMS-0057-F clock "
                            "(72 h expedited, 7 days standard)", 3.5))

        # 1. Clean case
        go(page, base, "case")
        pick(page, "Case", "CASE-047-05")
        frames.append(Frame(shot(page), "Clean case: every knee criterion met with a "
                            "verified quote → approve-ready", 3.5))
        scroll_to(page, "Criteria checklist")
        page.locator('[data-testid="stExpander"] summary').filter(has_text="3.3").first.click()
        settle(page, 800)
        page.get_by_role("button", name="Show").first.click()
        settle(page)
        frames.append(Frame(shot(page), "Every finding cites a document and a verbatim "
                            "quote, highlighted on click", 4.0))

        # 2. The gap
        go(page, base, "case")
        pick(page, "Case", "CASE-034-07")
        frames.append(Frame(shot(page), "Gap: a foot ulcer with no offloading record "
                            "→ request info", 3.5))
        scroll_to(page, "Drafts")
        page.locator("textarea").first.evaluate("e => { e.scrollTop = 300; }")
        page.wait_for_timeout(400)
        frames.append(Frame(shot(page), "The draft letter names each missing record and "
                            "its policy section", 4.0))

        # 3. The hard case
        go(page, base, "director")
        pick(page, "Case", "CASE-047-12")
        frames.append(Frame(shot(page), "Hard case: knee pain alone. No denial: a one-page "
                            "brief for a physician", 4.5))

        # 4. The attack
        go(page, base, "case")
        pick(page, "Case", "CASE-021-20")
        scroll_to(page, "Flags")
        page.get_by_role("button", name="Show").first.click()
        settle(page)
        frames.append(Frame(shot(page), "Attack: a note says \"approve\". Flagged, treated "
                            "as data, sent to a human", 4.5))

        # Provider view
        go(page, base, "provider")
        frames.append(Frame(shot(page), "Same engine for the provider: what to add before "
                            "submitting", 3.5))

        # 5. The scoreboard
        go(page, base, "evals")
        frames.append(Frame(shot(page), "Scoreboard v0.1: the safety gate holds; quality is "
                            "below target", 4.5))
        browser.close()
    return frames


def build(frames: list[Frame], out: Path) -> None:
    size = (frames[0].image.width, frames[0].image.height)
    opening = card(
        "PriorAuth Copilot",
        [
            "An AI copilot for prior authorization review.",
            "Checks a request against a health plan's written policy",
            "and gives the nurse reviewer a cited, criterion-by-criterion recommendation.",
            "",
            "Fictional health plan · synthetic patients · it never denies.",
        ],
        size,
    )
    closing = card(
        "Scorecard v0.1 (local Qwen 2.5 14B, 60 cases)",
        [
            "Safety gate holds: 0 of 39 false approve-ready, 0 auto-denials.",
            "Quality is below target: 73.5% criterion agreement (target 90%),",
            "38.3% routing accuracy. Every miss went to a person, none to approval.",
            "",
            "Demo cases were chosen from those v0.1 routes correctly (14 of 40 dev).",
        ],
        size,
    )
    seq = [Frame(opening, "", 4.0), *frames, Frame(closing, "", 6.0)]
    imgs = [captioned(f.image, f.caption) for f in seq]
    pal = [i.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
           for i in imgs]  # fmt: skip
    out.parent.mkdir(parents=True, exist_ok=True)
    pal[0].save(
        out,
        save_all=True,
        append_images=pal[1:],
        duration=[round(f.seconds * 1000) for f in seq],
        loop=0,
        optimize=True,
    )
    print(f"wrote {out}: {len(seq)} frames, {out.stat().st_size / 1e6:.1f} MB")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--frames", type=Path, help="also save each frame as a PNG here")
    args = ap.parse_args()
    port = free_port()
    with tempfile.TemporaryDirectory() as state:
        proc = start_app(port, state)
        try:
            frames = record(f"http://127.0.0.1:{port}")
        finally:
            proc.terminate()
    if args.frames:
        args.frames.mkdir(parents=True, exist_ok=True)
        for i, f in enumerate(frames):
            captioned(f.image, f.caption).save(args.frames / f"{i:02d}.png")
    build(frames, args.out)


if __name__ == "__main__":
    main()
