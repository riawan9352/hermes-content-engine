#!/usr/bin/env python3
"""
render_rigged.py — Puppet-rigged character animation for carousel test slides.

Karakter: kepala tetap, badan diperkecil ~1/5 (chibi), tangan/kaki riggable.
Test: slide 1, 2, 7 carousel 01. Full detail mode (blink, bounce, micro-motion).

Pipeline: rigged SVG + choreography CSS -> Chrome headless frame capture
          -> ffmpeg stitch -> GIF + MP4
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_carousel import THEMES, find_chrome, screenshot, _slugify

LOOP_SECONDS = 2.0
FPS = 10
NUM_FRAMES = int(LOOP_SECONDS * FPS)
FRAME_INTERVAL = LOOP_SECONDS / NUM_FRAMES

# ── Rigged character SVG ─────────────────────────────────────────────────────

def make_rigged_svg(theme_name):
    """Build puppet-rigged character SVG with all pose/expression variants.

    Proportions: head r=80 (unchanged), body 32x24 (~1/5 of 160x120),
    arms 60x50, legs 40x60 (unchanged). Flat cartoon style.
    All variants default opacity:0; choreography CSS controls visibility.
    """
    t = THEMES.get(theme_name, THEMES["gadget-masa-depan"])
    c = t["text"]        # navy outline
    p = t["primary"]     # white
    a = t["accent"]      # pink body
    bg = t["panel_bg"]

    # viewBox 500x500; movement via transform + overflow visible; .slide clips window
    return f'''<svg class="rig" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;">
<g class="char-root">

  <!-- TORSO (100x72, ~2.7x arm area, smaller than head 160) -->
  <g class="torso">
    <rect x="200" y="228" width="100" height="72" rx="22" fill="{a}" stroke="{c}" stroke-width="4"/>
    <!-- chest button detail -->
    <circle cx="250" cy="258" r="5" fill="{bg}" stroke="{c}" stroke-width="2"/>
  </g>

  <!-- LEGS (under body, at y=300; drawn AFTER torso so they stay visible) -->
  <g class="leg leg-left">
    <rect x="215" y="300" width="40" height="55" rx="10" fill="{c}"/>
  </g>
  <g class="leg leg-right">
    <rect x="255" y="300" width="40" height="55" rx="10" fill="{c}"/>
  </g>

  <!-- ARMS (attach at body sides x=200 / x=300) -->
  <g class="arm arm-left">
    <rect x="142" y="240" width="58" height="48" rx="14" fill="{p}" stroke="{c}" stroke-width="3"/>
  </g>
  <g class="arm arm-right">
    <rect x="300" y="240" width="58" height="48" rx="14" fill="{p}" stroke="{c}" stroke-width="3"/>
  </g>

  <!-- HEAD (unchanged size r=80) -->
  <g class="head">
    <circle cx="250" cy="150" r="80" fill="{p}" stroke="{c}" stroke-width="4"/>

    <!-- FACE VARIANTS (default hidden; choreography shows one) -->
    <g class="face">

      <!-- happy: wide smile, normal open eyes -->
      <g class="expr expr-happy">
        <circle cx="220" cy="140" r="11" fill="{c}"/>
        <circle cx="280" cy="140" r="11" fill="{c}"/>
        <path d="M210 170 Q250 200 290 170" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
      </g>

      <!-- sad: droopy eyes, frown -->
      <g class="expr expr-sad">
        <circle cx="220" cy="148" r="10" fill="{c}" opacity="0.85"/>
        <circle cx="280" cy="148" r="10" fill="{c}" opacity="0.85"/>
        <path d="M212 158 Q220 152 228 158" fill="none" stroke="{c}" stroke-width="2.5"/>
        <path d="M272 158 Q280 152 288 158" fill="none" stroke="{c}" stroke-width="2.5"/>
        <path d="M215 185 Q250 160 285 185" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
      </g>

      <!-- thinking: one brow raised, flat/tilt mouth -->
      <g class="expr expr-thinking">
        <circle cx="220" cy="145" r="11" fill="{c}"/>
        <circle cx="280" cy="142" r="11" fill="{c}"/>
        <!-- raised right brow -->
        <path d="M268 124 Q280 116 294 122" fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round"/>
        <!-- neutral left brow -->
        <path d="M208 126 L232 126" fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round"/>
        <!-- flat slightly tilted mouth -->
        <path d="M225 178 L275 172" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
      </g>

      <!-- laughing: closed happy eyes (> <), open mouth -->
      <g class="expr expr-laughing">
        <path d="M205 140 Q220 122 235 140" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
        <path d="M265 140 Q280 122 295 140" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
        <path d="M215 168 Q250 215 285 168 Z" fill="{c}" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>
      </g>

      <!-- focused: determined eyes, small firm smile -->
      <g class="expr expr-focused">
        <circle cx="220" cy="142" r="11" fill="{c}"/>
        <circle cx="280" cy="142" r="11" fill="{c}"/>
        <path d="M208 128 L234 124" fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round"/>
        <path d="M266 124 L292 128" fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round"/>
        <path d="M230 176 Q250 190 270 176" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
      </g>

      <!-- blink overlay: closed eyes line (shown briefly for blink) -->
      <g class="expr expr-blink">
        <path d="M208 142 L232 142" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
        <path d="M268 142 L292 142" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
        <!-- mouth from underlying expr shows through - blink only covers eyes -->
      </g>

    </g>
  </g>

</g>
</svg>'''


# ── Choreography definitions ─────────────────────────────────────────────────
# Each slide: expression windows, limb pose windows, trajectory, micro-anims.

CHOREOGRAPHIES = {
    1: {
        # HOOK: happy, wave right arm, walk in from left, stop center
        "traj": """
@keyframes traj {
  0%   { transform: translateX(-420px); }
  35%  { transform: translateX(0px); }
  100% { transform: translateX(0px); }
}
.char-root { animation: traj 2s cubic-bezier(0.22, 1, 0.36, 1) infinite; }
""",
        "expr_windows": {
            "expr-happy": [(0.0, 2.0)],   # visible whole loop
            "expr-blink": [(0.85, 0.95), (1.55, 1.62)],  # two blinks
        },
        "arm_poses": {
            # right arm waves whole time after arrival; left arm idle down
            "arm-right": {
                "show": [(0.3, 2.0)],      # wave pose visible from arrival
                "anim": """
@keyframes wave-arm {
  0%, 100% { transform: translateY(0px); }
  50%      { transform: translateY(-12px); }
}
.arm-right .pose-wave rect { animation: wave-arm 0.5s ease-in-out infinite; }
""",
            },
            "arm-left": {
                "show": [(0.0, 2.0)],
                "anim": "",
            },
        },
        "leg_poses": {
            "leg-left": {
                "show": [(0.0, 2.0)],
                "anim": """
@keyframes step-l {
  0%, 100% { transform: translateY(0px); }
  50%      { transform: translateY(-10px); }
}
.leg-left .pose-walk rect { animation: step-l 0.4s ease-in-out infinite; }
""",
            },
            "leg-right": {
                "show": [(0.0, 2.0)],
                "anim": """
@keyframes step-r {
  0%, 100% { transform: translateY(-10px); }
  50%      { transform: translateY(0px); }
}
.leg-right .pose-walk rect { animation: step-r 0.4s ease-in-out infinite; }
""",
            },
        },
        # dy/dx offsets: raise wave arm outward
        "pose_dy": {
            "arm-right": {"pose-wave": {"dy": -20, "dx": 25}},
        },
        # which pose visible per limb per time window
        "limb_pose_windows": {
            "arm-right": [("pose-wave", [(0.3, 2.0)]), ("pose-idle", [(0.0, 0.3)])],
            "arm-left": [("pose-idle", [(0.0, 2.0)])],
            "leg-left": [("pose-walk", [(0.0, 0.85)]), ("pose-stand", [(0.85, 2.0)])],
            "leg-right": [("pose-walk", [(0.0, 0.85)]), ("pose-stand", [(0.85, 2.0)])],
        },
        "torso_anim": """
@keyframes walk-bounce {
  0%, 100% { transform: translateY(0); }
  25%      { transform: translateY(-4px); }
  75%      { transform: translateY(-4px); }
}
.torso { animation: walk-bounce 0.4s ease-in-out infinite; }
.char-root .head { animation: walk-bounce 0.4s ease-in-out infinite; }
""",
        "arm_pose_variants": {
            "arm": ["right", "left"],
        },
        "leg_pose_variants": {
            "leg": ["left", "right"],
        },
    },

    2: {
        # PROBLEM: sad, arms droop, slump down in place
        "traj": """
@keyframes traj {
  0%   { transform: translateY(-40px); opacity: 0; }
  15%  { transform: translateY(0px); opacity: 1; }
  50%  { transform: translateY(0px); opacity: 1; }
  100% { transform: translateY(28px); opacity: 1; }
}
.char-root { animation: traj 2s ease-in-out infinite; }
""",
        "expr_windows": {
            "expr-sad": [(0.0, 2.0)],
            "expr-blink": [(1.1, 1.25)],  # slow sad blink
        },
        "arm_poses": {
            "arm-right": {"show": [(0.0, 2.0)], "anim": ""},
            "arm-left": {"show": [(0.0, 2.0)], "anim": ""},
        },
        "leg_poses": {
            "leg-left": {"show": [(0.0, 2.0)], "anim": ""},
            "leg-right": {"show": [(0.0, 2.0)], "anim": ""},
        },
        "limb_pose_windows": {
            "arm-right": [("pose-droop", [(0.0, 2.0)])],
            "arm-left": [("pose-droop", [(0.0, 2.0)])],
            "leg-left": [("pose-stand", [(0.0, 2.0)])],
            "leg-right": [("pose-stand", [(0.0, 2.0)])],
        },
        "pose_dy": {
            "arm-right": {"pose-droop": {"dy": 12, "dx": 0}},
            "arm-left": {"pose-droop": {"dy": 12, "dx": 0}},
        },
        "torso_anim": """
@keyframes sad-sway {
  0%, 100% { transform: rotate(-1.5deg) translateY(0); }
  50%      { transform: rotate(1.5deg) translateY(2px); }
}
.torso { animation: sad-sway 2s ease-in-out infinite; }
""",
        "arm_pose_variants": {
            "arm": ["right", "left"],
        },
        "leg_pose_variants": {
            "leg": ["left", "right"],
        },
    },

    7: {
        # CELEBRATION: laughing, both arms up, jump in from left, bounce, fade-exit up
        "traj": """
@keyframes traj {
  0%   { transform: translateX(-420px) translateY(0); }
  30%  { transform: translateX(0px) translateY(0); }
  50%  { transform: translateX(0px) translateY(-60px); }
  70%  { transform: translateX(0px) translateY(0); }
  85%  { transform: translateX(0px) translateY(-90px); opacity: 1; }
  100% { transform: translateX(0px) translateY(-300px); opacity: 0; }
}
.char-root { animation: traj 2s cubic-bezier(0.34, 1.56, 0.64, 1) infinite; }
""",
        "expr_windows": {
            "expr-laughing": [(0.0, 2.0)],
        },
        "arm_poses": {
            "arm-right": {
                "show": [(0.25, 2.0)],
                "anim": """
@keyframes cheer-r {
  0%, 100% { transform: translateY(0px); }
  50%      { transform: translateY(-8px); }
}
.arm-right .pose-raise rect { animation: cheer-r 0.35s ease-in-out infinite; }
""",
            },
            "arm-left": {
                "show": [(0.25, 2.0)],
                "anim": """
@keyframes cheer-l {
  0%, 100% { transform: translateY(0px); }
  50%      { transform: translateY(-8px); }
}
.arm-left .pose-raise rect { animation: cheer-l 0.35s ease-in-out infinite; }
""",
            },
        },
        "leg_poses": {
            "leg-left": {
                "show": [(0.0, 2.0)],
                "anim": """
@keyframes jump-l {
  0%, 100% { transform: translate(0px, 0px); }
  20%      { transform: translate(-18px, -22px); }
  40%      { transform: translate(0px, 0px); }
  60%      { transform: translate(-22px, -26px); }
  80%      { transform: translate(0px, 0px); }
}
.leg-left .pose-jump rect { animation: jump-l 0.5s ease-in-out infinite; }
""",
            },
            "leg-right": {
                "show": [(0.0, 2.0)],
                "anim": """
@keyframes jump-r {
  0%, 100% { transform: translate(0px, 0px); }
  20%      { transform: translate(18px, -22px); }
  40%      { transform: translate(0px, 0px); }
  60%      { transform: translate(22px, -26px); }
  80%      { transform: translate(0px, 0px); }
}
.leg-right .pose-jump rect { animation: jump-r 0.5s ease-in-out infinite; }
""",
            },
        },
        # dy/dx offsets: cheer arms outward; legs pre-spread for jump pose
        "pose_dy": {
            "arm-right": {"pose-raise": {"dy": -30, "dx": 30}},
            "arm-left": {"pose-raise": {"dy": -30, "dx": -30}},
            "leg-left": {"pose-jump": {"dy": 0, "dx": -8}},
            "leg-right": {"pose-jump": {"dy": 0, "dx": 8}},
        },
        "limb_pose_windows": {
            "arm-right": [("pose-raise", [(0.25, 2.0)]), ("pose-idle", [(0.0, 0.25)])],
            "arm-left": [("pose-raise", [(0.25, 2.0)]), ("pose-idle", [(0.0, 0.25)])],
            "leg-left": [("pose-jump", [(0.0, 2.0)])],
            "leg-right": [("pose-jump", [(0.0, 2.0)])],
        },
        "torso_anim": """
@keyframes jump-squash {
  0%, 100% { transform: scaleY(1); }
  25%      { transform: scaleY(1.06); }
  50%      { transform: scaleY(0.96); }
  75%      { transform: scaleY(1.06); }
}
.torso { animation: jump-squash 0.5s ease-in-out infinite; transform-box:fill-box; transform-origin:50% 100%; }
""",
        "arm_pose_variants": {
            "arm": ["right", "left"],
        },
        "leg_pose_variants": {
            "leg": ["left", "right"],
        },
    },
}


# ── HTML assembly ────────────────────────────────────────────────────────────

def _pose_windows_css(limb_type, limb_side, pose_name, windows):
    """Generate keyframes that show pose_name during given windows, hide otherwise."""
    # Build a percentage-based keyframe across the 2s loop
    stops = []
    for start, end in windows:
        s_pct = (start / LOOP_SECONDS) * 100
        e_pct = (end / LOOP_SECONDS) * 100
        stops.append((s_pct, e_pct))

    # Build keyframe: visible in windows, hidden outside
    kf_points = []
    # sort windows
    stops.sort()
    # start hidden
    prev_end = 0.0
    for s, e in stops:
        if s > prev_end:
            kf_points.append((prev_end, 0))
            kf_points.append((s, 0))
        kf_points.append((s, 1))
        kf_points.append((e, 1))
        prev_end = e
    if prev_end < 100:
        kf_points.append((prev_end, 0))
        kf_points.append((100, 0))

    # dedupe and build css
    lines = []
    seen = set()
    for pct, op in kf_points:
        pct_r = round(pct, 2)
        if pct_r in seen and op == 0:
            continue
        seen.add(pct_r)
        lines.append(f"  {pct_r}% {{ opacity: {op}; }}")

    kf_name = f"show-{limb_type}-{limb_side}-{pose_name}"
    css = f"@keyframes {kf_name} {{\n" + "\n".join(lines) + "\n}\n"
    css += f".{limb_type}-{limb_side} .{pose_name} {{ animation: {kf_name} {LOOP_SECONDS}s linear infinite; }}\n"
    return css


def _expr_windows_css(expr_name, windows):
    """Keyframes to show an expression during windows."""
    stops = sorted([(s / LOOP_SECONDS * 100, e / LOOP_SECONDS * 100) for s, e in windows])
    kf_points = []
    prev_end = 0.0
    for s, e in stops:
        if s > prev_end:
            kf_points.append((prev_end, 0))
            kf_points.append((s, 0))
        kf_points.append((s, 1))
        kf_points.append((e, 1))
        prev_end = e
    if prev_end < 100:
        kf_points.append((prev_end, 0))
        kf_points.append((100, 0))

    lines = []
    for pct, op in kf_points:
        lines.append(f"  {round(pct,2)}% {{ opacity: {op}; }}")

    kf_name = f"show-{expr_name}"
    css = f"@keyframes {kf_name} {{\n" + "\n".join(lines) + "\n}\n"
    css += f".expr.{expr_name} {{ animation: {kf_name} {LOOP_SECONDS}s linear infinite; }}\n"
    return css


def build_pose_variant_svg(limb_type, limb_side, pose_name, theme_name, dy=0, dx=0):
    """Return SVG snippet for a limb pose variant (hidden by default).

    dy/dx: offsets in SVG units to pre-position raised/lowered poses.
    """
    t = THEMES.get(theme_name, THEMES["gadget-masa-depan"])
    c = t["text"]
    p = t["primary"]

    # Determine rect coords based on limb (body 100x72 at x=200-300)
    if limb_type == "arm":
        if limb_side == "left":
            x, y, w, h = 142, 240, 58, 48
        else:
            x, y, w, h = 300, 240, 58, 48
    else:  # leg
        if limb_side == "left":
            x, y, w, h = 215, 300, 40, 55
        else:
            x, y, w, h = 255, 300, 40, 55

    x_adj = x + dx
    y_adj = y + dy
    # arms: white (primary); legs: navy (text color) — match base SVG fills
    fill = p if limb_type == "arm" else c

    return (f'<g class="{pose_name}">'
            f'<rect x="{x_adj}" y="{y_adj}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{c}" stroke-width="3"/>'
            f'</g>')


def make_rigged_html(theme_name, slide, total_slides, slide_num, source_credit=""):
    """Full HTML: layout + rigged character with pose variants + choreography CSS."""
    t = THEMES.get(theme_name, THEMES["gadget-masa-depan"])
    choreo = CHOREOGRAPHIES.get(slide_num)
    if not choreo:
        raise ValueError(f"No choreography defined for slide {slide_num}")

    num = slide.get("num", slide_num)
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    caption_box = slide.get("caption_box", "")

    # Base character SVG
    rig_svg = make_rigged_svg(theme_name)

    # Inject pose variants into each limb group (arms AND legs)
    pose_offsets = choreo.get("pose_dy", {})
    for variant_key in ("arm_pose_variants", "leg_pose_variants"):
        for limb_type, sides in choreo.get(variant_key, {}).items():
            for side in sides:
                limb_key = f"{limb_type}-{side}"
                pose_entries = choreo["limb_pose_windows"].get(limb_key, [])
                if not pose_entries:
                    continue
                # Build all snippets for this limb first
                snippets = []
                for pose_name, _windows in pose_entries:
                    off = pose_offsets.get(limb_key, {}).get(pose_name, {})
                    dy = off.get("dy", 0) if isinstance(off, dict) else (off or 0)
                    dx = off.get("dx", 0) if isinstance(off, dict) else 0
                    snippets.append(build_pose_variant_svg(limb_type, side, pose_name, theme_name, dy=dy, dx=dx))
                # Insert all at once before the limb group's closing tag
                marker = f'<g class="{limb_type} {limb_key}">'
                idx = rig_svg.find(marker)
                if idx >= 0:
                    # Find the matching close of THIS group (not nested ones)
                    # Scan forward counting open/close g tags
                    depth = 0
                    pos = idx
                    while pos < len(rig_svg):
                        next_open = rig_svg.find("<g", pos)
                        next_close = rig_svg.find("</g>", pos)
                        if next_close == -1:
                            break
                        if next_open != -1 and next_open < next_close:
                            depth += 1
                            pos = next_open + 2
                        else:
                            depth -= 1
                            if depth == 0:
                                # next_close is this group's closing tag
                                injection = "\n  " + "\n  ".join(snippets) + "\n  "
                                rig_svg = rig_svg[:next_close] + injection + rig_svg[next_close:]
                                break
                            pos = next_close + 4

    # Also need base rect hidden when poses exist (poses replace default)
    # Simpler: hide the base rect inside limb groups - poses handle visibility
    # Actually poses have their own rects; hide original rects:
    # We'll add CSS: .arm .base-rect, .leg .base-rect { display:none } when poses exist
    # For simplicity, mark original rects - but they don't have class. 
    # Alternative: pose variants ARE the only visible rects; hide originals via CSS
    # targeting first rect child:
    hide_base_css = ""
    if choreo.get("arm_pose_variants") or choreo.get("leg_pose_variants"):
        hide_base_css = """
.arm > rect:first-child, .leg > rect:first-child { display: none; }
"""

    # Build choreography CSS
    choreo_css = """
/* defaults: hide all variants; choreography animations reveal them */
.expr { opacity: 0; }
.pose-wave, .pose-idle, .pose-droop, .pose-raise, .pose-jump, .pose-walk, .pose-stand { opacity: 0; }
"""
    choreo_css += choreo["traj"]
    choreo_css += choreo.get("torso_anim", "")

    # Expression windows
    for expr, windows in choreo.get("expr_windows", {}).items():
        choreo_css += _expr_windows_css(expr, windows)

    # Limb pose windows
    for limb_key, pose_list in choreo.get("limb_pose_windows", {}).items():
        # limb_key like "arm-right" or "leg-left"
        parts = limb_key.split("-")
        limb_type, limb_side = parts[0], parts[1]
        for pose_name, windows in pose_list:
            choreo_css += _pose_windows_css(limb_type, limb_side, pose_name, windows)

    # Limb micro-animations
    for limb_key, data in choreo.get("arm_poses", {}).items():
        choreo_css += data.get("anim", "")
    for limb_key, data in choreo.get("leg_poses", {}).items():
        choreo_css += data.get("anim", "")

    choreo_css += hide_base_css

    # Floating dots (reuse simple version)
    float_html = ""
    for size, color, pos, delay in [
        (24, t["accent"], "top:15%;left:8%;opacity:0.5", "-0.3s"),
        (16, t["panel_border"], "top:28%;right:10%;opacity:0.55", "-1.1s"),
        (20, t["primary"], "top:62%;left:5%;opacity:0.4", "-0.7s"),
    ]:
        float_html += f'<div class="float-el" style="width:{size}px;height:{size}px;background:{color};{pos};animation-delay:{delay};"></div>\n'

    subline_html = f'<p class="subline">{subline}</p>' if subline else ""
    caption_html = f'<div class="caption-box">{caption_box}</div>' if caption_box else ""
    credit_html = f'<div class="source-credit">{source_credit}</div>' if source_credit and num == total_slides else ""

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

.badge {{
  position:absolute; top:40px; right:40px;
  background:{t['badge_bg']}; color:{t['badge_text']};
  font-family:{t['font_display']}; font-size:28px; font-weight:bold;
  padding:10px 22px; border-radius:14px; z-index:10;
  letter-spacing:1px;
  animation: badge-bob 2s ease-in-out infinite;
}}
@keyframes badge-bob {{
  0%, 100% {{ transform: translateY(0) rotate(-2deg); }}
  50% {{ transform: translateY(-5px) rotate(2deg); }}
}}

.character-area {{
  flex:1; display:flex; align-items:center; justify-content:center;
  padding:40px 60px 0 60px; min-height:0;
  overflow:visible;
}}
.character-area .rig {{
  width:85%; height:90%;
  overflow:visible;
}}

.text-area {{
  padding:0 70px 180px 70px;
  display:flex; flex-direction:column; gap:24px;
  background: {t['panel_bg']};
  border-radius: 24px;
  border: 3px solid {t['panel_border']};
  margin: 0 50px; padding: 30px 30px 170px 30px;
}}

.headline {{
  font-family:{t['font_display']};
  font-size:60px; font-weight:bold; line-height:1.15;
  color:{t['text']};
}}
.subline {{
  font-family:{t['font_body']};
  font-size:32px; line-height:1.4;
  color:{t['text_light']};
}}
.caption-box {{
  position:absolute; bottom:40px; left:70px; right:70px;
  background:{t['panel_bg']};
  border:3px solid {t['panel_border']};
  border-radius:20px;
  padding:20px 30px;
  font-family:{t['font_display']};
  font-size:30px; font-weight:bold;
  color:{t['text']};
  text-align:center;
  animation: cap-pulse 2s ease-in-out infinite;
}}
@keyframes cap-pulse {{
  0%, 100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }}
  50% {{ box-shadow: 0 0 20px 4px {t['panel_border']}55; }}
}}

.source-credit {{
  position:absolute; bottom:12px; left:70px; right:70px;
  font-size:20px; color:{t['text_light']};
  text-align:center;
}}

.float-el {{
  position:absolute; border-radius:50%; pointer-events:none; z-index:1;
  animation: float-el 2s ease-in-out infinite;
}}
@keyframes float-el {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-12px); }}
}}

.ambient {{
  position:absolute; inset:0;
  background: radial-gradient(ellipse at 30% 20%, {t['accent']}22, transparent 60%),
              radial-gradient(ellipse at 80% 80%, {t['badge_bg']}15, transparent 50%);
  pointer-events:none; z-index:0;
}}

/* ── CHOREOGRAPHY ── */
{choreo_css}
</style>
</head>
<body>
<div class="slide style-rounded">
  <div class="ambient"></div>
  {float_html}
  <div class="badge">{num}/{total_slides}</div>
  <div class="character-area">{rig_svg}</div>
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


def pause_anim_html(base_html, t_offset):
    """Pause all animations at time offset."""
    pause_css = f"""
*, *::before, *::after {{
  animation-play-state: paused !important;
  animation-delay: -{t_offset:.4f}s !important;
}}
"""
    return base_html.replace("</style>", pause_css + "\n</style>")


def stitch_gif(frames_dir, out_gif, fps=FPS):
    pattern = os.path.join(frames_dir, "frame_%03d.png")
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", pattern,
        "-vf", "split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
        "-loop", "0", out_gif,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(out_gif):
        raise RuntimeError(f"GIF failed: {r.stderr[-300:]}")


def stitch_mp4(frames_dir, out_mp4, fps=FPS):
    pattern = os.path.join(frames_dir, "frame_%03d.png")
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", pattern,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22",
        "-movflags", "+faststart", out_mp4,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(out_mp4):
        raise RuntimeError(f"MP4 failed: {r.stderr[-300:]}")


def render_rigged_test(spec_path, outdir, chrome_path=None, slide_nums=(1, 2, 7)):
    chrome = chrome_path or find_chrome()
    if not chrome:
        print("ERROR: Chrome not found"); sys.exit(1)

    with open(spec_path, "r", encoding="utf-8-sig") as f:
        spec = json.load(f)

    carousel = next((c for c in spec["carousels"] if c["id"] == "01"), None)
    if not carousel:
        print("ERROR: carousel 01 not found"); sys.exit(1)

    theme = carousel["theme"]
    slides = {s["num"]: s for s in carousel["slides"]}
    source = carousel.get("source_credit", "")
    total = len(carousel["slides"])

    outdir = Path(outdir)
    folder = outdir / "01-laporan-jumat-10-menit-rigged"
    folder.mkdir(parents=True, exist_ok=True)

    print(f">> Rigged test: carousel 01, slides {slide_nums}")
    print(f"   Theme: {theme} | Frames/slide: {NUM_FRAMES} @ {FPS}fps")

    ok = fail = 0
    for sn in slide_nums:
        slide = slides.get(sn)
        if not slide:
            print(f"  slide-{sn:02d} [SKIP] not in spec"); continue

        print(f"\n  slide-{sn:02d} ...", end="", flush=True)
        try:
            base_html = make_rigged_html(theme, slide, total, sn, source)
            frames_dir = tempfile.mkdtemp(prefix=f"rig_sn{sn}_")
            try:
                for i in range(NUM_FRAMES):
                    t_off = i * FRAME_INTERVAL
                    fh = pause_anim_html(base_html, t_off)
                    hf_path = os.path.join(frames_dir, "frame.html")
                    png_path = os.path.join(frames_dir, f"frame_{i:03d}.png")
                    with open(hf_path, "w", encoding="utf-8") as hf:
                        hf.write(fh)
                    screenshot(hf_path, png_path, chrome)

                gif_path = str(folder / f"slide-{sn:02d}.gif")
                mp4_path = str(folder / f"slide-{sn:02d}.mp4")
                stitch_gif(frames_dir, gif_path)
                stitch_mp4(frames_dir, mp4_path)
                g_kb = os.path.getsize(gif_path)//1024
                m_kb = os.path.getsize(mp4_path)//1024
                print(f"  [OK] GIF {g_kb} KB | MP4 {m_kb} KB")
                ok += 1
            finally:
                shutil.rmtree(frames_dir, ignore_errors=True)
        except Exception as e:
            print(f"  [FAIL] {e}")
            import traceback; traceback.print_exc()
            fail += 1

    print(f"\n{'='*50}")
    print(f"Done: {ok} ok, {fail} fail | Output: {folder}")
    return fail


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("--outdir", default="./output")
    parser.add_argument("--slides", default="1,2,7", help="Comma-separated slide numbers")
    parser.add_argument("--chrome", default=None)
    args = parser.parse_args()
    slide_nums = tuple(int(x) for x in args.slides.split(","))
    errors = render_rigged_test(args.spec, args.outdir, args.chrome, slide_nums)
    sys.exit(1 if errors > 0 else 0)
