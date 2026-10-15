#!/usr/bin/env python3
"""
render_animated.py — Render carousel slides to animated GIF + MP4 (1080x1350).

Uji coba opsi B: semua slide 1 carousel di-animate dulu untuk preview.
Pipeline: HTML + CSS keyframes -> Chrome headless frame capture (paused anim)
          -> ffmpeg stitch -> GIF + MP4

Usage:
  python render_animated.py <spec.json> --carousel 01 [--outdir DIR]
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_carousel import THEMES, make_slide_html, find_chrome, screenshot, _slugify

# ── Animation config ─────────────────────────────────────────────────────────
LOOP_SECONDS = 2.0
FPS = 10
NUM_FRAMES = int(LOOP_SECONDS * FPS)  # 20 frames
FRAME_INTERVAL = LOOP_SECONDS / NUM_FRAMES  # 0.1s

# ── Animation CSS ────────────────────────────────────────────────────────────

def make_anim_css(theme_name):
    """Return CSS keyframes + animated element rules for a theme."""
    t = THEMES.get(theme_name, THEMES["garis-jelas"])
    accent = t["accent"]
    panel_border = t["panel_border"]
    badge_bg = t["badge_bg"]

    return f"""
/* ── Animation keyframes (all 2s for seamless loop) ── */
@keyframes charBob {{
  0%, 100% {{ transform: translateY(0px); }}
  50% {{ transform: translateY(-12px); }}
}}
@keyframes floatEl {{
  0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
  33% {{ transform: translateY(-14px) rotate(4deg); }}
  66% {{ transform: translateY(-6px) rotate(-3deg); }}
}}
@keyframes captionPulse {{
  0%, 100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }}
  50% {{ box-shadow: 0 0 24px 6px {panel_border}55; }}
}}
@keyframes badgeBob {{
  0%, 100% {{ transform: translateY(0px) rotate(-2deg); }}
  50% {{ transform: translateY(-6px) rotate(2deg); }}
}}
@keyframes breathe {{
  0%, 100% {{ transform: scale(1); }}
  50% {{ transform: scale(1.025); }}
}}
@keyframes slideFade {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.97; }}
}}

/* ── Animated element base rules ── */
.character-area {{
  animation: charBob {LOOP_SECONDS}s ease-in-out infinite;
  will-change: transform;
}}
.badge {{
  animation: badgeBob {LOOP_SECONDS}s ease-in-out infinite;
  animation-delay: -0.3s;
  will-change: transform;
}}
.caption-box {{
  animation: captionPulse {LOOP_SECONDS}s ease-in-out infinite;
  will-change: box-shadow;
}}
.headline {{
  animation: breathe {LOOP_SECONDS}s ease-in-out infinite;
  transform-origin: left center;
  will-change: transform;
}}

/* Floating decorative dots */
.float-el {{
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  z-index: 1;
  animation: floatEl {LOOP_SECONDS}s ease-in-out infinite;
}}

/* Soft ambient tint layer */
.ambient {{
  position: absolute; inset:0;
  background: radial-gradient(ellipse at 30% 20%, {accent}22, transparent 60%),
              radial-gradient(ellipse at 80% 80%, {badge_bg}15, transparent 50%);
  animation: slideFade {LOOP_SECONDS}s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}}
"""


def make_float_elements(theme_name, num):
    """Return HTML for floating decorative dots, varied per slide number."""
    t = THEMES.get(theme_name, THEMES["garis-jelas"])
    accent = t["accent"]
    panel_border = t["panel_border"]
    primary = t["primary"]

    # Different dot layouts per slide for variety
    layouts = [
        # slide 1
        [
            (30, "#7EC8E3", "top:12%;left:6%;opacity:0.55", "-0.0s"),
            (18, accent, "top:22%;right:10%;opacity:0.6", "-0.7s"),
            (24, primary, "top:60%;left:4%;opacity:0.4", "-1.3s"),
            (14, panel_border, "top:70%;right:6%;opacity:0.5", "-0.4s"),
        ],
        # slide 2
        [
            (22, accent, "top:15%;right:8%;opacity:0.5", "-0.2s"),
            (16, "#7EC8E3", "top:30%;left:5%;opacity:0.55", "-1.0s"),
            (28, primary, "top:65%;right:4%;opacity:0.35", "-1.6s"),
        ],
        # slide 3
        [
            (26, "#7EC8E3", "top:10%;left:10%;opacity:0.5", "-0.5s"),
            (14, accent, "top:40%;right:7%;opacity:0.6", "-1.2s"),
            (20, panel_border, "top:75%;left:8%;opacity:0.45", "-0.1s"),
            (12, primary, "top:20%;right:20%;opacity:0.4", "-1.7s"),
        ],
        # slide 4
        [
            (18, primary, "top:14%;left:8%;opacity:0.5", "-0.9s"),
            (24, accent, "top:55%;right:5%;opacity:0.45", "-0.3s"),
            (15, "#7EC8E3", "top:35%;right:15%;opacity:0.55", "-1.5s"),
        ],
        # slide 5
        [
            (20, panel_border, "top:18%;right:9%;opacity:0.5", "-0.6s"),
            (28, "#7EC8E3", "top:50%;left:5%;opacity:0.4", "-1.4s"),
            (14, accent, "top:80%;right:12%;opacity:0.55", "-0.2s"),
            (16, primary, "top:8%;left:30%;opacity:0.35", "-1.1s"),
        ],
        # slide 6
        [
            (24, accent, "top:12%;left:12%;opacity:0.5", "-0.8s"),
            (16, primary, "top:45%;right:8%;opacity:0.5", "-0.1s"),
            (22, "#7EC8E3", "top:72%;left:6%;opacity:0.45", "-1.6s"),
        ],
        # slide 7
        [
            (30, "#7EC8E3", "top:10%;right:10%;opacity:0.5", "-0.4s"),
            (18, accent, "top:30%;left:7%;opacity:0.55", "-1.2s"),
            (20, primary, "top:68%;right:6%;opacity:0.4", "-0.7s"),
            (14, panel_border, "top:85%;left:15%;opacity:0.45", "-1.8s"),
        ],
    ]

    idx = (num - 1) % len(layouts)
    dots = layouts[idx]
    html = ""
    for size, color, pos, delay in dots:
        html += f'<div class="float-el" style="width:{size}px;height:{size}px;background:{color};{pos};animation-delay:{delay};"></div>\n'
    return html


def make_animated_html(theme_name, slide, total_slides, source_credit=""):
    """Base HTML + animation CSS + floating elements + ambient layer."""
    html = make_slide_html(theme_name, slide, total_slides, source_credit)
    num = slide.get("num", 1)

    anim_css = make_anim_css(theme_name)
    float_html = make_float_elements(theme_name, num)

    # Inject CSS before closing </style>
    html = html.replace("</style>", anim_css + "\n</style>")

    # Inject ambient layer + float elements right after <div class="slide ...">
    # Find the slide div opening and inject after it
    marker_start = '<div class="slide '
    idx = html.find(marker_start)
    if idx >= 0:
        # Find end of that opening tag
        tag_end = html.find(">", idx) + 1
        injection = '\n  <div class="ambient"></div>\n  ' + float_html
        html = html[:tag_end] + injection + html[tag_end:]

    return html


def pause_anim_html(base_html, t_offset):
    """Inject CSS to pause all animations at a specific time offset (seconds)."""
    pause_css = f"""
/* Frame capture: pause at t={t_offset:.2f}s */
*, *::before, *::after {{
  animation-play-state: paused !important;
  animation-delay: -{t_offset:.4f}s !important;
}}
"""
    return base_html.replace("</style>", pause_css + "\n</style>")


def stitch_gif(frames_dir, out_gif, fps=FPS):
    """Stitch PNG frames into optimized GIF via ffmpeg palette method."""
    pattern = os.path.join(frames_dir, "frame_%03d.png")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", pattern,
        "-vf",
        "split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
        "-loop", "0",
        out_gif,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(out_gif):
        raise RuntimeError(f"GIF stitch failed: {result.stderr[-400:]}")


def stitch_mp4(frames_dir, out_mp4, fps=FPS):
    """Stitch PNG frames into MP4 (H.264) via ffmpeg."""
    pattern = os.path.join(frames_dir, "frame_%03d.png")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "22",
        "-movflags", "+faststart",
        out_mp4,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(out_mp4):
        raise RuntimeError(f"MP4 stitch failed: {result.stderr[-400:]}")


def render_carousel_animated(spec_path, carousel_id, outdir, chrome_path=None):
    """Render one carousel fully animated to GIF + MP4 per slide."""
    chrome = chrome_path or find_chrome()
    if not chrome:
        print("ERROR: Chrome/Edge not found.")
        sys.exit(1)

    with open(spec_path, "r", encoding="utf-8-sig") as f:
        spec = json.load(f)

    target = None
    for c in spec.get("carousels", []):
        if c.get("id") == carousel_id:
            target = c
            break
    if not target:
        print(f"ERROR: carousel id {carousel_id} not found in spec")
        sys.exit(1)

    title = target.get("title", "untitled")
    theme = target.get("theme", "garis-jelas")
    slides = target.get("slides", [])
    source = target.get("source_credit", "")
    n = len(slides)

    outdir = Path(outdir)
    folder = outdir / f"{carousel_id}-{_slugify(title)}"
    folder.mkdir(parents=True, exist_ok=True)

    print(f">> Carousel {carousel_id}: {title}")
    print(f"   Theme: {theme} | Slides: {n} | Frames/slide: {NUM_FRAMES} @ {FPS}fps ({LOOP_SECONDS}s loop)")

    total_ok = 0
    total_fail = 0

    for slide in slides:
        num = slide.get("num", 1)
        print(f"\n  slide-{num:02d} ...", end="", flush=True)

        # Generate animated base HTML
        base_html = make_animated_html(theme, slide, n, source)

        # Per-slide temp frame dir
        frames_dir = tempfile.mkdtemp(prefix=f"anim_slide{num:02d}_")
        try:
            # Capture each frame
            for i in range(NUM_FRAMES):
                t_off = i * FRAME_INTERVAL
                frame_html = pause_anim_html(base_html, t_off)
                html_file = os.path.join(frames_dir, f"frame.html")
                png_file = os.path.join(frames_dir, f"frame_{i:03d}.png")

                with open(html_file, "w", encoding="utf-8") as hf:
                    hf.write(frame_html)

                screenshot(html_file, png_file, chrome)

            # Stitch GIF + MP4
            gif_path = str(folder / f"slide-{num:02d}.gif")
            mp4_path = str(folder / f"slide-{num:02d}.mp4")
            stitch_gif(frames_dir, gif_path)
            stitch_mp4(frames_dir, mp4_path)

            gif_kb = os.path.getsize(gif_path) // 1024
            mp4_kb = os.path.getsize(mp4_path) // 1024
            print(f"  [OK] GIF {gif_kb} KB | MP4 {mp4_kb} KB")
            total_ok += 1

        except Exception as e:
            print(f"  [FAIL] {e}")
            total_fail += 1
        finally:
            shutil.rmtree(frames_dir, ignore_errors=True)

    print(f"\n{'='*50}")
    print(f"Done: {total_ok} slides animated, {total_fail} errors")
    print(f"Output: {folder}")
    return total_fail


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Render animated carousel (GIF+MP4)")
    parser.add_argument("spec", help="Path to JSON spec file")
    parser.add_argument("--carousel", default="01", help="Carousel id to animate")
    parser.add_argument("--outdir", default="./output", help="Output directory")
    parser.add_argument("--chrome", default=None, help="Path to Chrome/Edge")
    args = parser.parse_args()

    errors = render_carousel_animated(args.spec, args.carousel, args.outdir, args.chrome)
    sys.exit(1 if errors > 0 else 0)
