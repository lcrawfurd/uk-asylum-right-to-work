#!/usr/bin/env python3
"""
model.py — Every number in the blog "The UK's £10,000 asylum charge vs the right to work",
computed in one place. Run it and it prints every figure and writes numbers.json:

    python3 model.py

The charge is modelled like an income-contingent student loan (the analogy the policy
invites): each year a person repays RATE of any earnings above THRESHOLD, capped at the
£10,000 face value, until written off at HORIZON. We track the cap on individual earner
types, not a population average, because the kink+cap make repayment nonlinear.

Two stated modelling choices:
  * THRESHOLD-INDEXED: student-loan thresholds rise with average earnings, so only
    individual career progression crosses the threshold; we add no economy-wide growth.
  * PRESENT VALUE: repayment is back-loaded, so we report nominal and PV (Green Book 3.5%).

Sources are noted inline. Every headline number in the blog maps to an entry in
numbers.json (see README).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent   # write next to the script, never the CWD

# ===================== 1. PARAMETERS & DATA =====================
# --- policy (charge modelled on student-loan Plan 5; the Bill sets no threshold/rate) ---
CHARGE, RATE, THRESHOLD, HORIZON, DISCOUNT = 10_000, 0.09, 25_000, 40, 0.035

# --- cohort (GOV.UK Immigration System Statistics, year ending Dec 2024) ---
# ~108k total claims / ~84k main applicants in 2024. The charge falls on ADULTS, so we
# use an adult base and EXCLUDE children. (Using ~100k total claims would fold in
# children who can't work or repay; that would give GRANTED=60k and a ~£96m charge.)
COHORT_ADULTS = 85_000     # adult asylum seekers who could be charged, per annual cohort
GRANT_RATE    = 0.60       # eventual grant rate incl. appeals (2024 initial rate was 47%)
GRANTED       = round(COHORT_ADULTS * GRANT_RATE)   # ~51,000 who can ever repay

# --- Home Office RIO 2015-2023: employment, hours, earnings ---
EMP_RATE   = {1: 0.24, 2: 0.45, 8: 0.48}   # share of refugees in ANY work, by yrs since status
FT_SHARE   = {1: 0.23, 8: 0.37}            # of those in work, share full-time (>=30 hrs/wk)
MED_FT     = 23_000                        # median full-time earnings, RIO yr 8
# Share of EMPLOYED refugees earning above the £25k threshold, by year since status.
# RIO publishes BANDS, not the £25k point: 6% of employed clear £20k in yr 1; 19% clear
# £30k by yr 8. The £25k share is INTERPOLATED between adjacent bands — estimated, not
# observed, and the largest single source of error in the yr1/yr8 shares (see README).
SHARE_EMPLOYED_ABOVE_25K = {1: 0.04, 8: 0.27}

# --- scarring from initial work bans (causal studies) ---
FASANI_PROP = 0.15         # ban cuts refugee employment 15% (proportional), up to a decade [IZA DP13149, 2020]
HAINMUELLER_PP = (4, 5)    # each extra year of limbo cuts employment 4-5pp [Science Advances, 2016]
BAN_CUT_YEARS = 0.5        # the reform modelled: 12 -> 6 months
SCAR_PERSIST_YEARS = 10    # scarring persists up to a decade
# Triangulating the two studies onto a 12->6 cut:
SCAR_GAIN_HAINMUELLER = tuple(pp * BAN_CUT_YEARS for pp in HAINMUELLER_PP)   # 2.0-2.5pp (linear in wait)
SCAR_GAIN_FASANI = (2.1, 4.7)   # 15% of the ~48% base = 8.5pp full gap; harm is front-loaded, so
                                # only ~1/4-1/2 is recovered by cutting the BACK six months.
# JUDGEMENT CALL, not a derivation: 3.0pp is our central read across the two ranges above.
# Channel C scales linearly in it. Neither study yields a UK 12->6 point estimate directly.
SCAR_GAIN_PP = 3.0
NET_FISCAL_PER_EMP_YR = 8_000   # tax gained + benefits saved per extra person-year employed (author est.)

# --- Channel B (support saved by working while the claim is pending) ---
ACCOM_COST_ASSUMED = 20_000     # ASSUMPTION: govt succeeds in ~halving SUPPORT_COST_PER_YEAR
                                # (£41k, hotel-inflated). Generous — see README.
SUPPORT_SAVED_ACCOMMODATION = round(ACCOM_COST_ASSUMED * BAN_CUT_YEARS)   # £10,000 (0.5 yr of it)
SUPPORT_SAVED_TAX = 1_300       # tax + NI on 6 months at ~£25k (author est.)
SUPPORT_SAVED_PER_TRANSITION = SUPPORT_SAVED_ACCOMMODATION + SUPPORT_SAVED_TAX   # £11,300
# NB the per-person value is itself uncertain (dispersal ~£6,000 / hotel ~£22,000 per person).
# The aggregate range below varies ONLY the employment share, holding this at central — so it
# is a sensitivity range, not a full uncertainty envelope. Stated as such in README + figure.
WORK_SOONER_SHARE = (0.15, 0.25)          # sensitivity range: share working sooner under a 6-month ban
WORK_SOONER_CENTRAL = sum(WORK_SOONER_SHARE) / 2   # 20% — midpoint of the range.
# Deliberately BELOW the 24% RIO year-1 refugee employment rate (EMP_RATE[1]): asylum seekers
# face more barriers than recognised refugees (no settled status, dispersal, shortage-list
# limits), so assuming parity with them would not be conservative. B scales linearly in this.

# --- hotels (NAO, Investigation into asylum accommodation, 2024) ---
HOTEL_BILL_PER_YEAR = 3_000_000_000       # ~£3bn/yr spent on asylum hotels
HOTEL_NIGHT, DISPERSAL_NIGHT = 144.98, 23.25   # £ per person per night
SUPPORT_COST_PER_YEAR = 41_000            # avg cost of supporting an asylum seeker 2023/24 (IPPR)

# ===================== helpers =====================
def ramp(t, pts=((1, .25), (3, .45), (5, .65), (8, .85), (12, 1.0))):
    """Earnings as a fraction of the mature plateau, by year since status (flat after yr 12)."""
    if t >= 12: return 1.0
    for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
        if y0 <= t <= y1:
            return v0 + (v1 - v0) * (t - y0) / (y1 - y0)
    return pts[0][1]

def tax(earn):
    """Income tax (20%) + employee NI (8%) above the £12,570 allowance."""
    return 0.28 * max(0, earn - 12_570)

def repay_stream(earnings, threshold=THRESHOLD, charge=CHARGE):
    """Per-year charge repayment: 9% of earnings above the threshold, capped at the balance."""
    bal, out = charge, []
    for e in earnings:
        r = min(bal, RATE * max(0, e - threshold)); bal -= r; out.append(r)
    return out

# ===================== 2. CHANNEL A — charge recovery =====================
# Earner types: (share of granted cohort, mature full-time-equivalent earnings £).
# Anchored to RIO year-8 (52% not in work; full-time median £23k), projected to maturity.
# The key assumption is how many EVER sustain earnings above £25k (implied share in comments).
CALIBRATIONS = {   # shares sum to 1
    "conservative": [(.55, 0), (.11, 20_000), (.12, 24_000), (.10, 27_000), (.06, 31_000), (.04, 36_000), (.02, 44_000)],  # 22% ever >£25k
    "central":      [(.50, 0), (.08, 20_000), (.09, 24_000), (.11, 27_000), (.09, 31_000), (.08, 36_000), (.05, 44_000)],  # 33%
    "optimistic":   [(.45, 0), (.06, 20_000), (.07, 24_000), (.12, 27_000), (.11, 31_000), (.10, 36_000), (.09, 44_000)],  # 42%
}
# Guard: a mis-edited share vector would silently rescale every Channel A output.
for _name, _g in CALIBRATIONS.items():
    assert abs(sum(s for s, _ in _g) - 1) < 1e-9, f"{_name}: earner-type shares must sum to 1"
    _above = sum(s for s, p in _g if p > THRESHOLD)
    assert 0.20 <= _above <= 0.45, f"{_name}: share ever above threshold ({_above:.0%}) looks wrong"

def amortise(groups, threshold=THRESHOLD, horizon=HORIZON):
    nom = pv = cleared = 0.0
    for share, plateau in groups:
        bal, n, p = CHARGE, 0.0, 0.0
        for t in range(1, horizon + 1):
            pay = min(bal, RATE * max(0, plateau * ramp(t) - threshold)); bal -= pay
            n += pay; p += pay / (1 + DISCOUNT) ** t
        nom += share * n; pv += share * p
        if bal <= 0.5: cleared += share
    return dict(pct_nom=100 * nom / CHARGE, pct_pv=100 * pv / CHARGE,
                clear=100 * cleared, agg_pv_m=pv * GRANTED / 1e6, agg_nom_m=nom * GRANTED / 1e6)

# ===================== 3. INDIVIDUAL 40-YEAR CASE (cited in the write-up) =====================
# One WORKING asylum seeker at the 80th percentile of ALL refugee earners (central
# calibration): a ~£31k mature plateau (~£26k at year 8) — just inside the ~22% who ever
# repay the charge in full. Shows how little the charge collects even from a top-fifth earner:
# it clears only by year 28, worth ~£5.4k in present value. Uses the same RIO ramp as the
# aggregate model, over the full 40-year write-off horizon. (The right-to-work fiscal case
# is a POPULATION effect — Channels B & C below — not something one worker's numbers can show.)
PLATEAU_A = 31_000
EARN_A = [PLATEAU_A * ramp(t) for t in range(1, HORIZON + 1)]

def trajectory(earnings):
    rep = repay_stream(earnings)
    s, clears = 0, None
    for i, r in enumerate(rep):
        s += r
        if clears is None and s >= CHARGE - 0.5: clears = i + 1
    pv = sum(r / (1 + DISCOUNT) ** (i + 1) for i, r in enumerate(rep))
    return dict(plateau=round(max(earnings)), tax=round(sum(tax(e) for e in earnings)),
                repaid=round(sum(rep)), repaid_pv=round(pv), clears_year=clears)

# ===================== 4. DISTRIBUTION / QUARTILES =====================
# Why a single "typical" earner misleads: repayment is kinked at the threshold and capped,
# so the median full-time worker (£23k, below threshold) repays £0 while the top quartile clears.
def quartile_repaid(plateau, horizon=20):
    return round(sum(repay_stream([plateau * ramp(t) for t in range(1, horizon + 1)])))

# ===================== 5. CHANNELS B & C =====================
def channel_B_m():                        # sensitivity range across WORK_SOONER_SHARE
    lo, hi = WORK_SOONER_SHARE
    return (COHORT_ADULTS * lo * SUPPORT_SAVED_PER_TRANSITION / 1e6,
            COHORT_ADULTS * hi * SUPPORT_SAVED_PER_TRANSITION / 1e6)

def channel_B_central_m(share=WORK_SOONER_CENTRAL):
    return COHORT_ADULTS * share * SUPPORT_SAVED_PER_TRANSITION / 1e6

def channel_B_split_m(share=WORK_SOONER_CENTRAL):
    """Channel B's two components: accommodation saved, and tax paid."""
    return (COHORT_ADULTS * share * SUPPORT_SAVED_ACCOMMODATION / 1e6,
            COHORT_ADULTS * share * SUPPORT_SAVED_TAX / 1e6)

def channel_C_m(emp_gain_pp=SCAR_GAIN_PP, persistence=SCAR_PERSIST_YEARS,
                fiscal=NET_FISCAL_PER_EMP_YR, pv=False):
    extra_employed = GRANTED * emp_gain_pp / 100
    years = sum(1 / (1 + DISCOUNT) ** t for t in range(1, persistence + 1)) if pv else persistence
    return extra_employed * fiscal * years / 1e6

SCAR_GAP_PP = round(EMP_RATE[8] / (1 - FASANI_PROP) - EMP_RATE[8], 3) * 100  # full-ban employment gap, pp

# ===================== 6. HOTELS =====================
HOTEL_MULTIPLE = round(HOTEL_NIGHT / DISPERSAL_NIGHT, 1)
def hotel_saving_m(share_moving):    # self-supporting workers who leave support entirely
    return HOTEL_BILL_PER_YEAR * share_moving / 1e6

# ===================== 7. ASSEMBLE & EMIT =====================
def all_numbers():
    A = amortise(CALIBRATIONS["central"])
    lo_pv = amortise(CALIBRATIONS["conservative"])["agg_pv_m"]
    hi_pv = amortise(CALIBRATIONS["optimistic"])["agg_pv_m"]
    tA = trajectory(EARN_A)
    B = channel_B_m(); C = channel_C_m()
    C_pv = channel_C_m(pv=True)                                       # C over 10 yrs, discounted
    C_pv_lo = channel_C_m(emp_gain_pp=2.0, fiscal=6_000, pv=True)     # low: 2pp x £6k
    C_pv_hi = channel_C_m(emp_gain_pp=4.7, fiscal=10_000, pv=True)    # high: 4.7pp x £10k
    B_central = channel_B_central_m()                                 # at the range midpoint (20%)
    B_accom, B_tax = channel_B_split_m()
    # Sum the ROUNDED parts, so the published components always add to the published total
    # (readers add up what they see; £192m + £102m must not print as £294m by luck).
    rtw_total_pv = round(B_central) + round(C_pv)
    N = {
        # --- Channel A: the charge ---
        "charge_recovered_pv_pct": round(A["pct_pv"]),
        "charge_recovered_nominal_pct": round(A["pct_nom"]),
        "charge_agg_pv_m": round(A["agg_pv_m"]),
        "charge_agg_pv_range_m": [round(lo_pv), round(hi_pv)],
        "charge_agg_nominal_m": round(A["agg_nom_m"]),
        "rab_charge_pct": round(100 - A["pct_pv"]),
        "share_ever_clear_pct": round(A["clear"]),
        "cohort_adults": COHORT_ADULTS, "granted": GRANTED,
        # --- share above threshold (share of ALL refugees) ---
        "share_above_25k_yr1_pct": round(EMP_RATE[1] * SHARE_EMPLOYED_ABOVE_25K[1] * 100),
        "share_above_25k_yr8_pct": round(EMP_RATE[8] * SHARE_EMPLOYED_ABOVE_25K[8] * 100),
        # --- individual case: 80th-percentile earner, 40-year horizon (cited in the text) ---
        "indiv_plateau_earnings": tA["plateau"],
        "indiv_tax40_statusquo": tA["tax"],
        "indiv_repaid40_statusquo": tA["repaid"],
        "indiv_repaid_pv_statusquo": tA["repaid_pv"],
        "indiv_charge_clears_year_statusquo": tA["clears_year"],
        # --- distribution / quartiles (20-yr repaid) ---
        "q_bottom_15k": quartile_repaid(15_000), "q_median_23k": quartile_repaid(MED_FT),
        "q_upper_32k": quartile_repaid(32_000), "q_top_42k": quartile_repaid(42_000),
        # --- Channels B & C ---
        "channel_B_support_saved_m": [round(B[0]), round(B[1])],      # sensitivity range (15–25%)
        "work_sooner_central_pct": round(WORK_SOONER_CENTRAL * 100),  # 20% — midpoint, below RIO's 24%
        "channel_B_central_m": round(B_central),
        "channel_B_accommodation_m": round(B_accom),
        "channel_B_tax_m": round(B_tax),
        "channel_C_scarring_avoided_m": round(C),                     # nominal, 10 yrs
        "channel_C_scarring_avoided_pv_m": round(C_pv),               # present value
        "channel_C_pv_range_m": [round(C_pv_lo), round(C_pv_hi)],
        "righttowork_total_pv_m": round(rtw_total_pv),                # B(mid) + C(PV)
        "scarring_gap_pp": round(SCAR_GAP_PP, 1), "scarring_gain_from_cut_pp": SCAR_GAIN_PP,
        # --- full-time work (RIO) ---
        "fulltime_share_of_employed_yr1_pct": round(FT_SHARE[1] * 100),
        "fulltime_share_of_employed_yr8_pct": round(FT_SHARE[8] * 100),
        "fulltime_share_of_all_yr8_pct": round(EMP_RATE[8] * FT_SHARE[8] * 100),
        # --- hotels ---
        "hotel_bill_bn": round(HOTEL_BILL_PER_YEAR / 1e9, 1),
        "hotel_vs_dispersal_multiple": HOTEL_MULTIPLE,
        "hotel_night": HOTEL_NIGHT, "dispersal_night": DISPERSAL_NIGHT,
        "hotel_saving_10pct_m": round(hotel_saving_m(0.10)),
        "hotel_saving_25pct_m": round(hotel_saving_m(0.25)),
    }
    N["righttowork_vs_charge_multiple"] = round(rtw_total_pv / N["charge_agg_pv_m"], 1)
    return N

if __name__ == "__main__":
    N = all_numbers()
    with open(HERE / "numbers.json", "w") as f:
        json.dump(N, f, indent=2)
    print("Wrote numbers.json\n")
    print("THE CHARGE (Channel A)")
    print(f"  Recovers {N['charge_recovered_pv_pct']}% in present value ({N['charge_recovered_nominal_pct']}% nominal); "
          f"£{N['charge_agg_pv_m']}m PV per cohort (range £{N['charge_agg_pv_range_m'][0]}-{N['charge_agg_pv_range_m'][1]}m).")
    print(f"  RAB charge (share written off, PV): {N['rab_charge_pct']}%. Ever fully clear: {N['share_ever_clear_pct']}%.")
    print(f"  Share of all refugees above £25k: {N['share_above_25k_yr1_pct']}% (yr1) -> {N['share_above_25k_yr8_pct']}% (yr8).")
    print("\nONE WORKING PERSON (80th percentile of all refugees), 40 YEARS")
    print(f"  ~£{N['indiv_plateau_earnings']:,} plateau, 40-yr tax £{N['indiv_tax40_statusquo']:,}; the £10,000 charge "
          f"is repaid in full but only by year {N['indiv_charge_clears_year_statusquo']} — worth just "
          f"£{N['indiv_repaid_pv_statusquo']:,} in present value.")
    print("\nDISTRIBUTION (20-yr repaid by earner)")
    print(f"  bottom-Q £{N['q_bottom_15k']} | median (£23k) £{N['q_median_23k']} | "
          f"upper-Q (£32k) £{N['q_upper_32k']:,} | top (£42k) £{N['q_top_42k']:,}")
    print("\nTHE RIGHT TO WORK")
    print(f"  Channel B (support saved): £{N['channel_B_support_saved_m'][0]}-{N['channel_B_support_saved_m'][1]}m.")
    print(f"  Channel C (scarring avoided): £{N['channel_C_scarring_avoided_m']}m "
          f"(full-ban gap {N['scarring_gap_pp']}pp; +{N['scarring_gain_from_cut_pp']}pp from a 12->6 cut).")
    print(f"  Right to work is ~{N['righttowork_vs_charge_multiple']}x the charge (PV).")
    print("\nFULL-TIME WORK (RIO)")
    print(f"  {N['fulltime_share_of_employed_yr1_pct']}% of employed refugees full-time in yr1 -> "
          f"{N['fulltime_share_of_employed_yr8_pct']}% by yr8; {N['fulltime_share_of_all_yr8_pct']}% of ALL refugees full-time by yr8.")
    print("\nHOTELS (NAO)")
    print(f"  £{N['hotel_bill_bn']}bn/yr; £{N['hotel_night']}/night vs £{N['dispersal_night']} dispersal = "
          f"{N['hotel_vs_dispersal_multiple']}x; saving at 10-25% move-out: £{N['hotel_saving_10pct_m']}-{N['hotel_saving_25pct_m']}m/yr.")
