"""
charge_model.py — Recovery of the £10,000 asylum charge, per-person amortisation.

Every assumption is a named constant at the top so each step is easy to follow and
change. Run:  python3 charge_model.py

The charge is modelled like an income-contingent student loan (the analogy the
policy itself invites): each year a person repays RATE of any earnings above a
THRESHOLD, capped cumulatively at the £10,000 face value, until written off at the
HORIZON. We track the cap on *individual* earner types (not a population average),
because the cap only bites for the minority who earn well above the threshold.

Two modelling choices worth stating plainly:
  1. THRESHOLD-INDEXED. Student-loan thresholds rise with average earnings, so only
     *individual career progression* (earning faster than the average) crosses the
     threshold — economy-wide real wage growth does not. We therefore work in real,
     threshold-relative terms and add NO economy-wide growth. (Freezing the threshold
     in nominal terms instead would raise recovery.)
  2. PRESENT VALUE. Repayment is back-loaded into years ~15-40, so we report both
     nominal and present value at the HM Treasury Green Book real discount rate.
"""

# ---- policy parameters -----------------------------------------------------
CHARGE      = 10_000    # £ face value of the charge (Home Office press release)
RATE        = 0.09      # repayment rate on income above threshold (student-loan Plan 5)
THRESHOLD   = 25_000    # £ repayment threshold (student-loan Plan 5; ~= full-time min wage)
HORIZON     = 40        # years to write-off (student-loan Plan 5 term)
DISCOUNT    = 0.035     # real discount rate for present value (HMT Green Book)
GRANTED     = 48_000    # adults granted asylum & remaining, per annual cohort (~60% of ~80k)

# ---- earnings inputs (Home Office RIO 2015-2023, extrapolated past year 8) --
# Ramp of earnings toward each earner type's mature plateau. Captures very low
# early-year earnings (part-year/part-time: RIO median in-work ~£2.5k in year 1)
# rising to a plateau by ~year 12. Flat thereafter (threshold-indexed; see above).
RAMP_POINTS = [(1, 0.25), (3, 0.45), (5, 0.65), (8, 0.85), (12, 1.00)]

# Earner types: (share of granted cohort, mature full-time-equivalent earnings £).
# DATA anchors (RIO year 8): 52% not in work; among those in work, full-time median
# £23k and 19% earn >=£30k. ASSUMPTION: project to maturity (~year 12-15). The single
# most important assumption is how many eventually sustain earnings above £25k — set
# by CALIBRATION below. ~half never sustain threshold-relevant work.
CALIBRATIONS = {
    # label: list of (share, mature_plateau_£).  Shares must sum to 1.
    "conservative": [(0.55, 0), (0.11, 20_000), (0.12, 24_000),
                     (0.10, 27_000), (0.06, 31_000), (0.04, 36_000), (0.02, 44_000)],
    "central":      [(0.50, 0), (0.08, 20_000), (0.09, 24_000),
                     (0.11, 27_000), (0.09, 31_000), (0.08, 36_000), (0.05, 44_000)],
    "optimistic":   [(0.45, 0), (0.06, 20_000), (0.07, 24_000),
                     (0.12, 27_000), (0.11, 31_000), (0.10, 36_000), (0.09, 44_000)],
}
# eventually-above-£25k share implied: conservative 22%, central 33%, optimistic 42%.

def ramp(t):
    pts = RAMP_POINTS
    if t >= pts[-1][0]:
        return 1.0
    for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
        if y0 <= t <= y1:
            return v0 + (v1 - v0) * (t - y0) / (y1 - y0)
    return pts[0][1]

def amortise(groups, threshold=THRESHOLD, horizon=HORIZON):
    """Return dict of per-person recovery, PV, %-who-clear, per-ever-employed."""
    tot_nom = tot_pv = cleared = ee_share = ee_nom = 0.0
    for share, plateau in groups:
        bal, nom, pv = CHARGE, 0.0, 0.0
        for t in range(1, horizon + 1):
            earn = plateau * ramp(t)
            pay = min(bal, RATE * max(0, earn - threshold))
            bal -= pay
            nom += pay
            pv  += pay / (1 + DISCOUNT) ** t
        tot_nom += share * nom
        tot_pv  += share * pv
        if bal <= 0.5:
            cleared += share
        if plateau > 0:
            ee_share += share
            ee_nom   += share * nom
    return {
        "per_person_nominal": tot_nom,
        "per_person_pv": tot_pv,
        "pct_nominal": 100 * tot_nom / CHARGE,
        "pct_pv": 100 * tot_pv / CHARGE,
        "share_clearing": 100 * cleared,
        "per_ever_employed_nominal": ee_nom / ee_share if ee_share else 0,
        "agg_nominal_m": tot_nom * GRANTED / 1e6,
        "agg_pv_m": tot_pv * GRANTED / 1e6,
    }

if __name__ == "__main__":
    g = CALIBRATIONS["central"]

    print("HORIZON SENSITIVITY (central calibration, £25k threshold)")
    print(f"{'yrs':>4} {'nominal':>10} {'PV':>10} {'clear':>7}")
    for h in (10, 20, 30, 40):
        r = amortise(g, horizon=h)
        print(f"{h:>4} {r['pct_nominal']:>9.1f}% {r['pct_pv']:>9.1f}% {r['share_clearing']:>6.0f}%")

    print("\nCALIBRATION SENSITIVITY (40-yr, £25k threshold)")
    for label, grp in CALIBRATIONS.items():
        r = amortise(grp)
        print(f"  {label:>12}: nominal {r['pct_nominal']:4.1f}%  PV {r['pct_pv']:4.1f}%  "
              f"agg £{r['agg_pv_m']:.0f}m PV  (per ever-employed £{r['per_ever_employed_nominal']:.0f})")

    print("\nTHRESHOLD SENSITIVITY (central, 40-yr)")
    for thr in (25_000, 22_500, 20_000, 17_500, 15_000):
        r = amortise(g, threshold=thr)
        print(f"  £{thr:>6}: nominal {r['pct_nominal']:4.1f}%  PV {r['pct_pv']:4.1f}%")

    r = amortise(g)
    print(f"\nHEADLINE (central, £25k, 40-yr): "
          f"{r['pct_pv']:.0f}% PV / {r['pct_nominal']:.0f}% nominal; "
          f"£{r['agg_pv_m']:.0f}m PV per cohort; {r['share_clearing']:.0f}% ever clear the charge.")
