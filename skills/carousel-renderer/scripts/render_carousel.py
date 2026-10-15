#!/usr/bin/env python3
"""
carousel-renderer — Render carousel slides (HTML) to PNG 1080x1350 via Chrome headless.

Usage:
  python render_carousel.py <spec.json> [--outdir DIR] [--chrome PATH]

Input: JSON spec file describing themes, slides, and text content.
Output: PNG files organized per carousel folder.

Spec format:
{
  "carousels": [
    {
      "id": "01",
      "title": "Laporan 10 Menit",
      "theme": "gadget-masa-depan",
      "slides": [
        {
          "num": 1,
          "headline": "Laporan Jumat: 10 Menit. Bukan 1 Jam.",
          "subline": "",
          "caption_box": "10 MENIT",
          "character": "kakek-penemu-open"
        },
        ...
      ]
    }
  ]
}
"""

import json
import os
import struct
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

# ── Theme definitions ────────────────────────────────────────────────────────

THEMES = {
    "gadget-masa-depan": {
        "bg": "#BFE3F5", "primary": "#FFFFFF", "accent": "#F5A0B5",
        "text": "#1F4E79", "text_light": "#4A90B8", "border": "#1F4E79",
        "font_display": "'Trebuchet MS', 'Segoe UI', sans-serif",
        "font_body": "'Segoe UI', Arial, sans-serif",
        "badge_bg": "#1F4E79", "badge_text": "#FFFFFF",
        "panel_bg": "#FFFFFF", "panel_border": "#7EC8E3",
        "style": "rounded"
    },
    "bengkel-diagnostik": {
        "bg": "#1A1A1A", "primary": "#E86A33", "accent": "#4ECDC4",
        "text": "#F5F5F5", "text_light": "#AAAAAA", "border": "#4ECDC4",
        "font_display": "'Courier New', monospace", "font_body": "'Segoe UI', Arial, sans-serif",
        "badge_bg": "#E86A33", "badge_text": "#1A1A1A",
        "panel_bg": "#2A2A2A", "panel_border": "#4ECDC4",
        "style": "tech"
    },
    "garis-jelas": {
        "bg": "#F5EFE6", "primary": "#E86A33", "accent": "#2A5F5B",
        "text": "#1F1B18", "text_light": "#5A5550", "border": "#1F1B18",
        "font_display": "Georgia, 'Times New Roman', serif", "font_body": "Georgia, serif",
        "badge_bg": "#1F1B18", "badge_text": "#F5EFE6",
        "panel_bg": "#FFFDF5", "panel_border": "#1F1B18",
        "style": "comic"
    },
    "kantor-kacau": {
        "bg": "#FDF3C7", "primary": "#C0442E", "accent": "#5B8DB8",
        "text": "#1F1B18", "text_light": "#6B6560", "border": "#1F1B18",
        "font_display": "'Comic Sans MS', 'Segoe UI', cursive", "font_body": "'Segoe UI', Arial, sans-serif",
        "badge_bg": "#C0442E", "badge_text": "#FFFFFF",
        "panel_bg": "#FFFEF0", "panel_border": "#C0442E",
        "style": "comic"
    },
    "latihan-suci": {
        "bg": "#F5B84E", "primary": "#D64545", "accent": "#F5D76E",
        "text": "#1F1B18", "text_light": "#5A4A20", "border": "#1F1B18",
        "font_display": "'Impact', 'Arial Black', sans-serif", "font_body": "'Segoe UI', Arial, sans-serif",
        "badge_bg": "#D64545", "badge_text": "#FFFFFF",
        "panel_bg": "#FFF8E0", "panel_border": "#D64545",
        "style": "bold"
    },
    "malam-art-deco": {
        "bg": "#121212", "primary": "#B22222", "accent": "#C9A227",
        "text": "#E0E0E0", "text_light": "#8C8C8C", "border": "#C9A227",
        "font_display": "Georgia, 'Palatino Linotype', serif", "font_body": "'Segoe UI', Arial, sans-serif",
        "badge_bg": "#C9A227", "badge_text": "#121212",
        "panel_bg": "#1E1E1E", "panel_border": "#C9A227",
        "style": "deco"
    }
}

# ── HTML generation ──────────────────────────────────────────────────────────

def make_slide_html(theme_name, slide, total_slides, source_credit=""):
    t = THEMES.get(theme_name, THEMES["garis-jelas"])
    num = slide.get("num", 1)
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    caption_box = slide.get("caption_box", "")
    character = slide.get("character", "")

    # Character illustration slot (SVG placeholder based on theme)
    char_svg = _character_svg(theme_name, character)

    # Subline paragraph
    subline_html = f'<p class="subline">{subline}</p>' if subline else ""

    # Caption box (bottom)
    caption_html = ""
    if caption_box:
        caption_html = f'<div class="caption-box">{caption_box}</div>'

    # Source credit (last slide)
    credit_html = ""
    if source_credit and num == total_slides:
        credit_html = f'<div class="source-credit">{source_credit}</div>'

    # Style-specific border/panel decorations
    border_class = f"style-{t['style']}"

    html = f'''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1350px; overflow:hidden; }}
body {{ font-family: {t['font_body']}; background: {t['bg']}; position:relative; }}

.slide {{
  width:1080px; height:1350px;
  display:flex; flex-direction:column;
  position:relative; overflow:hidden;
}}

/* Badge */
.badge {{
  position:absolute; top:40px; right:40px;
  background:{t['badge_bg']}; color:{t['badge_text']};
  font-family:{t['font_display']}; font-size:28px; font-weight:bold;
  padding:10px 22px; border-radius:14px; z-index:10;
  letter-spacing:1px;
}}

/* Character area */
.character-area {{
  flex:1; display:flex; align-items:center; justify-content:center;
  padding:40px 60px 0 60px; min-height:0;
}}

.character-area svg {{
  max-width:100%; max-height:100%;
}}

/* Text area */
.text-area {{
  padding:0 70px 180px 70px;
  display:flex; flex-direction:column; gap:24px;
}}

.headline {{
  font-family:{t['font_display']};
  font-size:64px; font-weight:bold; line-height:1.15;
  color:{t['text']};
  text-align:left;
}}

.subline {{
  font-family:{t['font_body']};
  font-size:34px; line-height:1.4;
  color:{t['text_light']};
  text-align:left;
}}

/* Caption box */
.caption-box {{
  position:absolute; bottom:40px; left:70px; right:70px;
  background:{t['panel_bg']};
  border:3px solid {t['panel_border']};
  border-radius:{'20px' if t['style'] in ('rounded','comic') else '4px' if t['style']=='deco' else '0px'};
  padding:20px 30px;
  font-family:{t['font_display']};
  font-size:30px; font-weight:bold;
  color:{t['text']};
  text-align:center;
}}

/* Source credit */
.source-credit {{
  position:absolute; bottom:12px; left:70px; right:70px;
  font-size:20px; color:{t['text_light']};
  text-align:center;
}}

/* ── Theme-specific decorations ── */

/* Tech (Bengkel Diagnostik) */
.style-tech .slide::before {{
  content:''; position:absolute; top:0; left:0; right:0; height:6px;
  background: linear-gradient(90deg, {t['accent']}, {t['primary']}, {t['accent']});
}}
.style-tech .headline {{
  text-shadow: 0 0 20px rgba(78,205,196,0.3);
}}
.style-tech .text-area {{
  border-top: 2px solid {t['accent']};
  margin: 0 60px; padding: 30px 10px 170px 10px;
}}

/* Comic (Garis Jelas / Kantor Kacau) */
.style-comic .headline {{
  -webkit-text-stroke: 1px {t['text']};
}}
.style-comic .text-area {{
  background: {t['panel_bg']};
  border: 3px solid {t['border']};
  border-radius: 16px;
  margin: 0 50px; padding: 30px 30px 170px 30px;
}}

/* Bold (Latihan Suci) */
.style-bold .slide::before {{
  content:''; position:absolute; bottom:0; left:0; right:0; height:120px;
  background: linear-gradient(transparent, {t['primary']}22);
}}
.style-bold .headline {{
  text-shadow: 3px 3px 0 {t['accent']}, 6px 6px 0 {t['primary']}44;
}}

/* Deco (Malam Art Deco) */
.style-deco .slide::before {{
  content:''; position:absolute; top:0; left:0; right:0; height:4px;
  background: {t['accent']};
}}
.style-deco .slide::after {{
  content:''; position:absolute; bottom:0; left:0; right:0; height:4px;
  background: {t['accent']};
}}
.style-deco .headline {{
  color: {t['text']};
  letter-spacing: 1px;
}}

/* Rounded (Gadget Masa Depan) */
.style-rounded .text-area {{
  background: {t['panel_bg']};
  border-radius: 24px;
  border: 3px solid {t['panel_border']};
  margin: 0 50px; padding: 30px 30px 170px 30px;
}}
</style>
</head>
<body>
<div class="slide {border_class}">
  <div class="badge">{num}/{total_slides}</div>
  <div class="character-area">{char_svg}</div>
  <div class="text-area">
    <h1 class="headline">{headline}</h1>
    {subline_html}
  </div>
  {caption_html}
  {credit_html}
</div>
</body>
</html>'''

    return html


def _character_svg(theme_name, char_type):
    """Return a simple themed SVG character placeholder."""
    t = THEMES.get(theme_name, THEMES["garis-jelas"])
    c = t["text"]
    p = t["primary"]
    a = t["accent"]
    bg = t["panel_bg"]

    # Simple stylized character based on theme — original designs
    if theme_name == "gadget-masa-depan":
        # Round friendly inventor figure with a suitcase
        return f'''<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
  <circle cx="250" cy="180" r="80" fill="{p}" stroke="{c}" stroke-width="4"/>
  <circle cx="220" cy="165" r="12" fill="{c}"/>
  <circle cx="280" cy="165" r="12" fill="{c}"/>
  <path d="M210 200 Q250 230 290 200" fill="none" stroke="{c}" stroke-width="4"/>
  <rect x="170" y="270" width="160" height="120" rx="20" fill="{a}" stroke="{c}" stroke-width="4"/>
  <rect x="140" y="300" width="60" height="50" rx="10" fill="{p}" stroke="{c}" stroke-width="3"/>
  <rect x="300" y="300" width="60" height="50" rx="10" fill="{p}" stroke="{c}" stroke-width="3"/>
  <rect x="200" y="400" width="40" height="60" rx="8" fill="{c}"/>
  <rect x="260" y="400" width="40" height="60" rx="8" fill="{c}"/>
  <rect x="200" y="310" width="100" height="40" rx="6" fill="{bg}" stroke="{c}" stroke-width="3"/>
</svg>'''

    elif theme_name == "bengkel-diagnostik":
        # Robot technician with visor
        return f'''<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
  <rect x="180" y="100" width="140" height="120" rx="16" fill="{t['panel_bg']}" stroke="{a}" stroke-width="4"/>
  <rect x="200" y="140" width="100" height="30" rx="6" fill="{a}" opacity="0.8"/>
  <rect x="160" y="230" width="180" height="140" rx="12" fill="{t['panel_bg']}" stroke="{p}" stroke-width="4"/>
  <circle cx="250" cy="290" r="30" fill="{p}" opacity="0.6"/>
  <rect x="120" y="250" width="40" height="100" rx="8" fill="{a}" stroke="{a}" stroke-width="2"/>
  <rect x="340" y="250" width="40" height="100" rx="8" fill="{a}" stroke="{a}" stroke-width="2"/>
  <rect x="200" y="380" width="40" height="80" rx="8" fill="{t['text_light']}"/>
  <rect x="260" y="380" width="40" height="80" rx="8" fill="{t['text_light']}"/>
  <line x1="250" y1="60" x2="250" y2="100" stroke="{a}" stroke-width="4"/>
  <circle cx="250" cy="55" r="10" fill="{p}"/>
</svg>'''

    elif theme_name == "garis-jelas":
        # Explorer with quiff-free hair (original)
        return f'''<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="250" cy="170" rx="70" ry="80" fill="{bg}" stroke="{c}" stroke-width="4"/>
  <circle cx="225" cy="155" r="10" fill="{c}"/>
  <circle cx="275" cy="155" r="10" fill="{c}"/>
  <path d="M230 195 Q250 210 270 195" fill="none" stroke="{c}" stroke-width="3"/>
  <path d="M180 140 Q250 80 320 140" fill="{c}" stroke="{c}" stroke-width="2"/>
  <path d="M170 260 L160 400 L340 400 L330 260 Z" fill="{p}" stroke="{c}" stroke-width="4"/>
  <rect x="200" y="280" width="100" height="60" rx="4" fill="{bg}" stroke="{c}" stroke-width="2"/>
  <rect x="210" y="400" width="35" height="60" fill="{c}"/>
  <rect x="255" y="400" width="35" height="60" fill="{c}"/>
</svg>'''

    elif theme_name == "kantor-kacau":
        # Bumbling office tech handler
        return f'''<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
  <circle cx="250" cy="160" r="75" fill="{bg}" stroke="{c}" stroke-width="4"/>
  <circle cx="225" cy="148" r="11" fill="{c}"/>
  <circle cx="275" cy="148" r="11" fill="{c}"/>
  <ellipse cx="250" cy="190" rx="20" ry="10" fill="{p}"/>
  <path d="M185 250 L175 420 L325 420 L315 250 Z" fill="{a}" stroke="{c}" stroke-width="4"/>
  <rect x="210" y="280" width="80" height="50" rx="6" fill="{bg}" stroke="{c}" stroke-width="2"/>
  <rect x="210" y="420" width="35" height="55" fill="{c}"/>
  <rect x="255" y="420" width="35" height="55" fill="{c}"/>
  <path d="M310 270 L360 220" stroke="{p}" stroke-width="5" fill="none"/>
  <circle cx="365" cy="215" r="15" fill="{p}" stroke="{c}" stroke-width="3"/>
</svg>'''

    elif theme_name == "latihan-suci":
        # Martial artist in gi
        return f'''<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
  <circle cx="250" cy="150" r="70" fill="{bg}" stroke="{c}" stroke-width="4"/>
  <circle cx="228" cy="138" r="10" fill="{c}"/>
  <circle cx="272" cy="138" r="10" fill="{c}"/>
  <path d="M230 175 L270 175" stroke="{c}" stroke-width="3"/>
  <path d="M175 230 L165 400 L335 400 L325 230 Z" fill="{p}" stroke="{c}" stroke-width="4"/>
  <rect x="175" y="290" width="150" height="18" fill="{t['accent']}" stroke="{c}" stroke-width="2"/>
  <rect x="205" y="400" width="40" height="65" fill="{c}"/>
  <rect x="255" y="400" width="40" height="65" fill="{c}"/>
  <path d="M170 260 L120 200" stroke="{c}" stroke-width="6" stroke-linecap="round"/>
  <path d="M330 260 L380 200" stroke="{c}" stroke-width="6" stroke-linecap="round"/>
  <circle cx="250" cy="150" r="90" fill="none" stroke="{t['accent']}" stroke-width="2" opacity="0.4"/>
</svg>'''

    elif theme_name == "malam-art-deco":
        # Detective with hat and glasses
        return f'''<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
  <rect x="180" y="130" width="140" height="110" rx="8" fill="{t['panel_bg']}" stroke="{a}" stroke-width="3"/>
  <rect x="195" y="100" width="110" height="40" rx="4" fill="{t['text']}" stroke="{a}" stroke-width="3"/>
  <rect x="160" y="90" width="180" height="18" rx="4" fill="{t['text']}"/>
  <circle cx="220" cy="180" r="16" fill="{a}" opacity="0.8"/>
  <circle cx="280" cy="180" r="16" fill="{a}" opacity="0.8"/>
  <line x1="236" y1="180" x2="264" y2="180" stroke="{a}" stroke-width="3"/>
  <path d="M220 220 L280 220" stroke="{a}" stroke-width="3"/>
  <path d="M170 250 L160 430 L340 430 L330 250 Z" fill="{t['text']}" stroke="{a}" stroke-width="3"/>
  <rect x="210" y="280" width="80" height="4" fill="{a}"/>
  <rect x="205" y="430" width="40" height="55" fill="{t['text_light']}"/>
  <rect x="255" y="430" width="40" height="55" fill="{t['text_light']}"/>
</svg>'''

    else:
        # Generic fallback
        return f'''<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
  <circle cx="250" cy="250" r="120" fill="{p}" stroke="{c}" stroke-width="4" opacity="0.6"/>
  <text x="250" y="265" text-anchor="middle" font-size="48" fill="{c}" font-family="Arial">AI</text>
</svg>'''


# ── Chrome screenshot ────────────────────────────────────────────────────────

def find_chrome():
    """Locate Chrome or Edge executable."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def screenshot(html_path, png_path, chrome_path, width=1080, height=1350):
    """Screenshot an HTML file to PNG at exact dimensions."""
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--screenshot={png_path}",
        f"--window-size={width},{height}",
        "--hide-scrollbars",
        "--default-background-color=00000000",
        f"file:///{html_path.replace(os.sep, '/')}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if not os.path.exists(png_path):
        raise RuntimeError(f"Screenshot failed: {result.stderr[:200]}")
    return png_path


# ── Main pipeline ────────────────────────────────────────────────────────────

def render_spec(spec_path, outdir, chrome_path=None):
    """Render all carousels in a spec file."""
    chrome = chrome_path or find_chrome()
    if not chrome:
        print("ERROR: Chrome/Edge not found. Pass --chrome PATH")
        sys.exit(1)

    with open(spec_path, 'r', encoding='utf-8-sig') as f:
        spec = json.load(f)

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    total_pngs = 0
    total_errors = 0

    for carousel in spec.get("carousels", []):
        cid = carousel.get("id", "00")
        title = carousel.get("title", "untitled")
        theme = carousel.get("theme", "garis-jelas")
        slides = carousel.get("slides", [])
        source = carousel.get("source_credit", "")
        n = len(slides)

        folder = outdir / f"{cid}-{_slugify(title)}"
        folder.mkdir(parents=True, exist_ok=True)

        print(f"\n>> Carousel {cid}: {title} (theme: {theme}, {n} slides)")

        tmpdir = tempfile.mkdtemp(prefix="carousel_")

        try:
            for slide in slides:
                num = slide.get("num", 1)
                html = make_slide_html(theme, slide, n, source)
                html_file = os.path.join(tmpdir, f"slide-{num:02d}.html")
                png_file = str(folder / f"slide-{num:02d}.png")

                with open(html_file, 'w', encoding='utf-8') as hf:
                    hf.write(html)

                try:
                    screenshot(html_file, png_file, chrome)
                    size_kb = os.path.getsize(png_file) // 1024
                    print(f"  [OK] slide-{num:02d}.png  ({size_kb} KB)")
                    total_pngs += 1
                except Exception as e:
                    print(f"  [FAIL] slide-{num:02d} FAILED: {e}")
                    total_errors += 1
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n{'='*50}")
    print(f"Done: {total_pngs} PNGs rendered, {total_errors} errors")
    print(f"Output: {outdir}")
    return total_errors


def _slugify(text):
    """Make text safe for folder names."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:40]


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Render carousel HTML slides to PNG")
    parser.add_argument("spec", help="Path to JSON spec file")
    parser.add_argument("--outdir", default="./output", help="Output directory")
    parser.add_argument("--chrome", default=None, help="Path to Chrome/Edge executable")
    args = parser.parse_args()

    errors = render_spec(args.spec, args.outdir, args.chrome)
    sys.exit(1 if errors > 0 else 0)
