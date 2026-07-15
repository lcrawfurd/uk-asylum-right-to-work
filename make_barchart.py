#!/usr/bin/env python3
"""
make_barchart.py — regenerate figure-charge-vs-righttowork.svg from numbers.json.

    python3 make_barchart.py

The blog's headline figure: the £10,000 charge (what it recovers) against the two
right-to-work channels, all in present value per cohort. Horizontal bars, zero baseline
(lie factor 1.0), direct value labels, whiskers for the ranges, no gridlines. Charge in
red (the weak instrument); both right-to-work bars in teal (grouped by colour).
"""
import json
import shutil
import subprocess

N = json.load(open("numbers.json"))
charge, (c_lo, c_hi) = N["charge_agg_pv_m"], N["charge_agg_pv_range_m"]
b_lo, b_hi = N["channel_B_support_saved_m"]; b_mid = round((b_lo + b_hi) / 2)
cscar, (s_lo, s_hi) = N["channel_C_scarring_avoided_pv_m"], N["channel_C_pv_range_m"]
rtw_total = N["righttowork_total_pv_m"]; mult = N["righttowork_vs_charge_multiple"]

# ---- geometry ----
VBW, VBH = 820, 300
X0 = 250.0                     # bar baseline (after left labels)
SCALE = 1.9                    # px per £m
def bx(v): return round(X0 + v * SCALE, 1)

RED, TEAL, BLUE = "#D15553", "#006970", "#2D99B5"
INK, MUTE, HAIR = "#1A272A", "#52514e", "#c3c2b7"

def row(y, colour, val, lo, hi, l1, l2):
    """One bar with whisker + labels. y = vertical centre."""
    h = 22; top = y - h/2
    p = []
    # category label (right-aligned into the bar area)
    p.append(f'<text x="235" y="{y-2:.0f}" text-anchor="end" font-size="13" font-weight="600" fill="{INK}">{l1}</text>')
    p.append(f'<text x="235" y="{y+13:.0f}" text-anchor="end" font-size="11" fill="{MUTE}">{l2}</text>')
    # bar
    p.append(f'<rect x="{X0:.0f}" y="{top:.1f}" width="{bx(val)-X0:.1f}" height="{h}" rx="3" fill="{colour}"/>')
    # whisker
    p.append(f'<line x1="{bx(lo)}" y1="{y:.0f}" x2="{bx(hi)}" y2="{y:.0f}" stroke="{INK}" stroke-width="1.5" opacity="0.65"/>')
    for xx in (bx(lo), bx(hi)):
        p.append(f'<line x1="{xx}" y1="{y-5:.0f}" x2="{xx}" y2="{y+5:.0f}" stroke="{INK}" stroke-width="1.5" opacity="0.65"/>')
    # value + range labels, just past the high whisker
    lx = bx(hi) + 12
    p.append(f'<text x="{lx:.0f}" y="{y-1:.0f}" font-size="15" font-weight="700" fill="{INK}">£{val}m</text>')
    p.append(f'<text x="{lx:.0f}" y="{y+13:.0f}" font-size="11" fill="{MUTE}">£{lo}–{hi}m</text>')
    return "\n  ".join(p)

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 {VBW} {VBH}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Horizontal bar chart, present value per cohort. The £10,000 charge recovers about £{charge} million (range £{c_lo}–{c_hi}m). The right to work is worth far more: support saved while claims are pending about £{b_mid} million (£{b_lo}–{b_hi}m) and scarring avoided about £{cscar} million (£{s_lo}–{s_hi}m) — together roughly £{rtw_total} million, about {mult} times the charge." style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;">
  <rect x="0" y="0" width="{VBW}" height="{VBH}" rx="8" fill="#ffffff"/>
  <text x="20" y="30" font-size="17" font-weight="700" fill="{INK}">The £10,000 charge recovers a fraction of what the right to work is worth</text>
  <text x="20" y="50" font-size="12.5" fill="{MUTE}">Fiscal value to the Exchequer per annual cohort, present value (£ millions). Bar = central estimate; whisker = plausible range.</text>

  {row(95, RED, charge, c_lo, c_hi, "The £10,000 charge", "what it recovers")}

  <text x="20" y="146" font-size="11.5" font-weight="700" fill="{TEAL}" letter-spacing="0.5">THE RIGHT TO WORK</text>
  {row(178, TEAL, b_mid, b_lo, b_hi, "Support saved", "while claims are pending")}
  {row(220, BLUE, cscar, s_lo, s_hi, "Scarring avoided", "higher long-run employment")}

  <line x1="20" y1="250" x2="{VBW-20}" y2="250" stroke="{HAIR}" stroke-width="1"/>
  <text x="20" y="270" font-size="13" fill="{INK}"><tspan font-weight="700">Together, the right to work ≈ £{rtw_total}m</tspan> — about {mult}× the charge, and collected up front rather than over decades.</text>
  <text x="20" y="290" font-size="10" fill="{MUTE}">Sources: Home Office RIO; IPPR; NAO; Fasani et al. (2020); Hainmueller et al. (2016). Generated from model.py.</text>
</svg>
'''

SVG_PATH, PNG_PATH = "figure-charge-vs-righttowork.svg", "figure-charge-vs-righttowork.png"
with open(SVG_PATH, "w") as f:
    f.write(svg)
print(f"Wrote {SVG_PATH}")

# PNG at 2x for pasting into the blog/doc (SVG doesn't embed everywhere).
# Needs rsvg-convert (brew install librsvg); the SVG is still written without it.
if shutil.which("rsvg-convert"):
    subprocess.run(["rsvg-convert", "-w", str(VBW * 2), "-o", PNG_PATH, SVG_PATH], check=True)
    print(f"Wrote {PNG_PATH} ({VBW*2}px wide)")
else:
    print(f"! rsvg-convert not found — {PNG_PATH} not regenerated (brew install librsvg)")

print(f"  charge £{charge}m ({c_lo}-{c_hi}) | support £{b_mid}m ({b_lo}-{b_hi}) | "
      f"scarring £{cscar}m ({s_lo}-{s_hi}) | right to work £{rtw_total}m = {mult}x")
