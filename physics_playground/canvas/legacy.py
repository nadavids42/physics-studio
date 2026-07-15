"""Shared helpers for building lightweight canvas/HTML hero animations.

Physics stays in numpy/Python as before. This module only handles turning a
precomputed trajectory into a smooth, kid-friendly animation that runs client
side (via requestAnimationFrame), instead of a matplotlib figure regenerated
frame-by-frame from Python.
"""

import streamlit as st

# Shared JS: array interpolation, easing, and a tiny particle system.
# Every mission's script can rely on these being defined.
CANVAS_JS_UTILS = r"""
function lerp(a, b, t) { return a + (b - a) * t; }

function sampleArray(arr, frac) {
  frac = Math.min(1, Math.max(0, frac));
  const idx = frac * (arr.length - 1);
  const i0 = Math.floor(idx);
  const i1 = Math.min(arr.length - 1, i0 + 1);
  const local = idx - i0;
  return lerp(arr[i0], arr[i1], local);
}

function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
function easeInOutSine(t) { return -(Math.cos(Math.PI * t) - 1) / 2; }

class Particles {
  constructor() { this.items = []; }
  burst(x, y, count, colors) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1.5 + Math.random() * 3.5;
      this.items.push({
        x: x, y: y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 1.5,
        life: 1.0,
        size: 2 + Math.random() * 3,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    }
  }
  update(dt) {
    for (const p of this.items) {
      p.x += p.vx; p.y += p.vy;
      p.vy += 0.12;
      p.life -= dt * 1.6;
    }
    this.items = this.items.filter(function (p) { return p.life > 0; });
  }
  draw(ctx) {
    for (const p of this.items) {
      ctx.globalAlpha = Math.max(0, p.life);
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }
}

function drawFace(ctx, cx, cy, r, opts) {
  opts = opts || {};
  const eyeOffsetX = r * 0.32;
  const eyeOffsetY = -r * 0.05;
  const eyeR = r * (opts.wideEyes ? 0.16 : 0.11);

  ctx.fillStyle = "white";
  ctx.beginPath(); ctx.arc(cx - eyeOffsetX, cy + eyeOffsetY, eyeR, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(cx + eyeOffsetX, cy + eyeOffsetY, eyeR, 0, Math.PI * 2); ctx.fill();

  ctx.fillStyle = "#1a1a1a";
  const pupilR = eyeR * 0.55;
  ctx.beginPath(); ctx.arc(cx - eyeOffsetX, cy + eyeOffsetY, pupilR, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(cx + eyeOffsetX, cy + eyeOffsetY, pupilR, 0, Math.PI * 2); ctx.fill();

  ctx.strokeStyle = "#1a1a1a";
  ctx.lineWidth = Math.max(1.5, r * 0.06);
  ctx.beginPath();
  ctx.arc(cx, cy + r * 0.28, r * 0.28, 0.15 * Math.PI, 0.85 * Math.PI);
  ctx.stroke();
}
"""


def build_doc(canvas_width: int, canvas_height: int, extra_css: str, body_html: str, script_body: str) -> str:
    """Wrap a canvas + script into a standalone HTML document for st.iframe."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0; padding: 0; background: transparent;
    font-family: -apple-system, 'Segoe UI', Roboto, sans-serif;
    overflow: hidden;
  }}
  #stage {{ position: relative; width: {canvas_width}px; height: {canvas_height}px; }}
  canvas {{ display: block; border-radius: 18px; }}
  .msg-bubble {{
    position: absolute; left: 50%; bottom: 14px; transform: translateX(-50%);
    background: white; border-radius: 14px; padding: 10px 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
    font-size: 15px; font-weight: 600; color: #333; text-align: center;
    opacity: 0; transition: opacity 0.5s ease, transform 0.5s ease;
    max-width: 88%; pointer-events: none;
  }}
  .msg-bubble.show {{ opacity: 1; transform: translateX(-50%) translateY(-4px); }}
  .hint-text {{
    position: absolute; left: 50%; top: 12px; transform: translateX(-50%);
    font-size: 13px; color: #888; font-weight: 500;
  }}
  {extra_css}
</style>
</head>
<body>
<div id="stage">
{body_html}
</div>
<script>
{CANVAS_JS_UTILS}
{script_body}
</script>
</body>
</html>
"""


def show(html_doc: str, height: int = 420):
    st.iframe(html_doc, height=height)