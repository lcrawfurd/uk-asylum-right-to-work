#!/usr/bin/env python3
"""
make_figure.py — regenerate figure-one-worker.svg from model.py, so every plotted
coordinate is exact (no hand-drawing).

    python3 make_figure.py

The figure shows one working asylum seeker at the 80th percentile of all refugee
earners, over the full 40-year charge horizon, in three panels:
  A  status quo (12-month ban)
  B  A + the £10,000 charge (same earnings; shows the repayment)
  C  right to work at 3 months (earlier start, less scarring) + the charge
Each panel: gross earnings (blue line), annual income tax + NI (green area),
and annual charge repayment stacked on top (red area).
"""
import model as m

# ---- data (straight from the model) ----
YRS = m.HORIZON
earn_A, earn_C = m.EARN_A, m.EARN_C
tax_A = [m.tax(e) for e in earn_A]
tax_C = [m.tax(e) for e in earn_C]
rep_A = m.repay_stream(earn_A)
rep_C = m.repay_stream(earn_C)
tj_A, tj_C = m.trajectory(earn_A), m.trajectory(earn_C)

# ---- layout ----
YBASE, YTOP, YMAX = 380.0, 122.9, 40_000        # £0 at y=380, £40k at y=122.9
PANEL_W = 258.0
X0 = {"A": 72.0, "B": 392.0, "C": 712.0}

def xt(x0, t):                                   # year t (1..YRS) -> x
    return x0 + (t - 1) / (YRS - 1) * PANEL_W
def yv(v):                                        # £ value -> y
    return round(YBASE - v * (YBASE - YTOP) / YMAX, 1)
def pts(seq):
    return " ".join(f"{round(x,1)},{round(y,1)}" for x, y in seq)

def panel(key, title, sub, earn, tax, rep, foot):
    x0 = X0[key]; x1 = x0 + PANEL_W
    P = []
    P.append(f'<text x="{x0:.0f}" y="96" fill="#0b0b0b" font-size="13" font-weight="650">{title}</text>'
             f'<text x="{x0:.0f}" y="110" fill="#52514e" font-size="11">{sub}</text>')
    # gridlines + y labels (only on panel A carries the £ labels)
    grid = "".join(f'<line x1="{x0:.0f}" y1="{yv(v):.1f}" x2="{x1:.0f}" y2="{yv(v):.1f}"/>'
                   for v in (0, 10000, 20000, 30000, 40000))
    P.append(f'<g stroke="#e1e0d9" stroke-width="1">{grid}</g>')
    if key == "A":
        labs = "".join(f'<text x="66" y="{yv(v)+4:.1f}">£{v//1000}k</text>' if v else
                       f'<text x="66" y="{yv(v)+4:.1f}">£0</text>' for v in (0,10000,20000,30000,40000))
        P.append(f'<g fill="#898781" font-size="10.5" text-anchor="end">{labs}</g>')
    # tax area (green), baseline -> tax[t]
    tax_pts = [(x0, YBASE)] + [(xt(x0, t+1), yv(tax[t])) for t in range(YRS)] + [(x1, YBASE)]
    P.append(f'<polygon fill="#1baf7a" fill-opacity="0.9" points="{pts(tax_pts)}"/>')
    # repayment area (red), stacked on tax: tax[t] -> tax[t]+rep[t]
    if any(rep):
        top = [(xt(x0, t+1), yv(tax[t] + rep[t])) for t in range(YRS)]
        bot = [(xt(x0, t+1), yv(tax[t])) for t in range(YRS-1, -1, -1)]
        P.append(f'<polygon fill="#e34948" fill-opacity="0.92" points="{pts(top+bot)}"/>')
    # earnings line (blue)
    earn_pts = [(xt(x0, t+1), yv(earn[t])) for t in range(YRS)]
    P.append(f'<polyline fill="none" stroke="#2a78d6" stroke-width="2" points="{pts(earn_pts)}"/>')
    # x-axis ticks
    ticks = "".join(f'<text x="{xt(x0, t):.1f}" y="394">{t}</text>' for t in (1,10,20,30,40))
    P.append(f'<g fill="#898781" font-size="10.5" text-anchor="middle">{ticks}</g>')
    # footer lines
    for i, (txt, bold) in enumerate(foot):
        y = 416 + i*15
        w = ' font-weight="600"' if bold else ''
        col = "#0b0b0b" if bold else "#52514e"
        P.append(f'<text x="{x0:.0f}" y="{y}" fill="{col}" font-size="{12 if bold else 11}"{w}>{txt}</text>')
    return "\n  ".join(P)

def k(v):    # £176782 -> "£177k"
    return f"£{round(v/1000)}k"

aria = (f"Three 40-year panels for one working asylum seeker at the 80th percentile of refugee "
        f"earners. A, status quo: about £{m.PLATEAU_A//1000}k plateau, 40-year tax {k(tj_A['tax'])}, no charge. "
        f"B, plus £10,000 charge: same earnings and tax; the £10,000 is repaid in full but only by year "
        f"{tj_A['clears_year']}, worth about £{round(tj_A['repaid_pv']/100)/10}k in present value. "
        f"C, work rights at 3 months plus charge: earnings reach about £{m.PLATEAU_C//1000}k, 40-year tax "
        f"{k(tj_C['tax'])} ({k(tj_C['tax']-tj_A['tax'])} more than A), charge cleared by year {tj_C['clears_year']}.")

foot1 = (f"Illustrative: one working asylum seeker at the 80th percentile of all refugee earners "
         f"(~£{m.PLATEAU_A//1000}k mature plateau, ~£26k at year 8).")
foot2 = ("Earnings follow the RIO ramp; tax = income tax + NI (28% above £12,570); charge = 9% above "
         "£25,000, capped at £10,000, over 40 years.")

pv_k = round(tj_A['repaid_pv']/100)/10
SVG = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 1000 486" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{aria}" style="max-width:100%;height:auto;font-family:system-ui,-apple-system,'Segoe UI',sans-serif;">
  <rect x="0" y="0" width="1000" height="486" rx="8" fill="#ffffff"/>
  <line x1="330" y1="66" x2="352" y2="66" stroke="#2a78d6" stroke-width="2"/><text x="358" y="70" fill="#52514e" font-size="12">Gross earnings</text>
  <rect x="470" y="60" width="12" height="12" rx="2" fill="#1baf7a"/><text x="488" y="70" fill="#52514e" font-size="12">Income tax + NI paid</text>
  <rect x="628" y="60" width="12" height="12" rx="2" fill="#e34948"/><text x="646" y="70" fill="#52514e" font-size="12">£10k charge repaid</text>
  {panel("A", "A · Status quo", "12-month work ban, no charge", earn_A, tax_A, [0]*YRS,
         [(f"40-yr tax paid: {k(tj_A['tax'])}", True), ("No repayment charge.", False)])}
  {panel("B", "B · + £10,000 charge", "Same ban, plus repayment", earn_A, tax_A, rep_A,
         [(f"40-yr tax paid: {k(tj_A['tax'])} (same as A)", True),
          (f"Charge repaid in full — but only by year {tj_A['clears_year']},", False),
          (f"worth ~£{pv_k}k in today's money.", False)])}
  {panel("C", "C · Work rights at 3 months + charge", "Earlier work, less scarring", earn_C, tax_C, rep_C,
         [(f"40-yr tax paid: {k(tj_C['tax'])} ({k(tj_C['tax']-tj_A['tax'])} more)", True),
          (f"Charge cleared by year {tj_C['clears_year']} — and", False),
          (f"{k(tj_C['tax']-tj_A['tax'])} more tax than the status quo.", False)])}
  <text x="72" y="466" fill="#898781" font-size="10.5">{foot1}</text>
  <text x="72" y="479" fill="#898781" font-size="10.5">{foot2}</text>
</svg>
'''

with open("figure-one-worker.svg", "w") as f:
    f.write(SVG)
print("Wrote figure-one-worker.svg")
print(f"  A/B: plateau £{tj_A['plateau']:,}, 40-yr tax £{tj_A['tax']:,}, repaid £{tj_A['repaid']:,} "
      f"(PV £{tj_A['repaid_pv']:,}), clears yr {tj_A['clears_year']}")
print(f"  C:   plateau £{tj_C['plateau']:,}, 40-yr tax £{tj_C['tax']:,}, clears yr {tj_C['clears_year']}")
