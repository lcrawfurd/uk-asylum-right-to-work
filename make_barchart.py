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
from pathlib import Path

HERE = Path(__file__).resolve().parent   # read/write next to the script, never the CWD
N = json.load(open(HERE / "numbers.json"))
charge, (c_lo, c_hi) = N["charge_agg_pv_m"], N["charge_agg_pv_range_m"]
accom, (a_lo, a_hi) = N["channel_B_accommodation_m"], N["channel_B_accommodation_range_m"]
btax,  (t_lo, t_hi) = N["channel_B_tax_m"], N["channel_B_tax_range_m"]
cscar, (s_lo, s_hi) = N["channel_C_scarring_avoided_pv_m"], N["channel_C_pv_range_m"]
rtw_total = N["righttowork_total_pv_m"]; mult = N["righttowork_vs_charge_multiple"]

# ---- geometry ----
VBW, VBH = 900, 336
X0 = 250.0                     # bar baseline (after left labels)
SCALE = 1.9                    # px per £m
def bx(v): return round(X0 + v * SCALE, 1)

RED, TEAL, BLUE, GOLD = "#D15553", "#006970", "#2D99B5", "#B8860B"
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
<svg viewBox="0 0 {VBW} {VBH}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Horizontal bar chart, present value per cohort. The £10,000 charge recovers about £{charge} million (range £{c_lo}–{c_hi}m). The right to work is worth far more, in three parts: accommodation saved about £{accom} million (£{a_lo}–{a_hi}m), tax paid immediately about £{btax} million (£{t_lo}–{t_hi}m), and tax paid later from avoided scarring about £{cscar} million (£{s_lo}–{s_hi}m) — together roughly £{rtw_total} million, about {mult} times the charge." style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;">
  <rect x="0" y="0" width="{VBW}" height="{VBH}" rx="8" fill="#ffffff"/>
  <text x="20" y="30" font-size="17" font-weight="700" fill="{INK}">The £10,000 charge recovers a fraction of what the right to work is worth</text>
  <text x="20" y="50" font-size="12.5" fill="{MUTE}">Fiscal value to the Exchequer per annual cohort, present value (£m). Bar = central; whisker = key-assumption range, not a full envelope.</text>

  {row(95, RED, charge, c_lo, c_hi, "The £10,000 charge", "what it recovers")}

  <text x="20" y="146" font-size="11.5" font-weight="700" fill="{TEAL}" letter-spacing="0.5">THE RIGHT TO WORK</text>
  {row(178, TEAL, accom, a_lo, a_hi, "Accommodation saved", "support not paid while claims pending")}
  {row(220, GOLD, btax, t_lo, t_hi, "Tax paid immediately", "by those working sooner")}
  {row(262, BLUE, cscar, s_lo, s_hi, "Tax paid later", "less scarring, higher employment")}

  <line x1="20" y1="292" x2="{VBW-20}" y2="292" stroke="{HAIR}" stroke-width="1"/>
  <text x="20" y="311" font-size="13" fill="{INK}"><tspan font-weight="700">Together, the right to work ≈ £{rtw_total}m</tspan> — about {mult}× the charge, and collected up front rather than over decades.</text>
  <text x="20" y="329" font-size="10" fill="{MUTE}">Source: CGD/Authors' analysis of Home Office RIO; IPPR; NAO; Fasani et al. (2020); Hainmueller et al. (2016).</text>
</svg>
'''

SVG_PATH = HERE / "figure-charge-vs-righttowork.svg"
PNG_PATH = HERE / "figure-charge-vs-righttowork.png"
with open(SVG_PATH, "w") as f:
    f.write(svg)
print(f"Wrote {SVG_PATH}")

# PNG at 2x for pasting into the blog/doc (SVG doesn't embed everywhere).
# Needs rsvg-convert (brew install librsvg); the SVG is still written without it.
if shutil.which("rsvg-convert"):
    subprocess.run(["rsvg-convert", "-w", str(VBW * 2), "-o", str(PNG_PATH), str(SVG_PATH)], check=True)
    print(f"Wrote {PNG_PATH} ({VBW*2}px wide)")
else:
    print(f"! rsvg-convert not found — {PNG_PATH} not regenerated (brew install librsvg)")

print(f"  charge £{charge}m ({c_lo}-{c_hi}) | accommodation £{accom}m ({a_lo}-{a_hi}) | "
      f"tax now £{btax}m ({t_lo}-{t_hi}) | tax later £{cscar}m ({s_lo}-{s_hi}) | "
      f"right to work £{rtw_total}m = {mult}x")
