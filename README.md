# UK asylum £10,000 charge — right to work (BOTEC)

Back-of-the-envelope analysis + figures for the CGD blog **"The UK's £10,000 Asylum Seeker Payment Must Be Paired With The Right To Work"** (Dempster, Crawfurd, Mitchell).

**Live report:** https://lcrawfurd.github.io/uk-asylum-right-to-work/

## Files
- **`index.html`** — the deliverable (served as the live report above). Single self-contained, theme-aware HTML report with all three figures + explanations. Leads with the one-person 20-year story, then scales to the cohort.
- `BOTEC-asylum-10k-repayment.md` — the working BOTEC brief (full detail, transparent assumptions table, sensitivity, verification box). Links to the figure files below by relative path, so keep them together.
- **`charge_model.py`** — the charge-recovery amortisation as a documented, runnable script. Every number in Channel A is printed by it (`python3 charge_model.py`); assumptions are named constants at the top.
- `BOTEC-asylum-figure3.html` — **Figure 1**: the animated one-person / 20-year interactive (status quo → + £10k charge → + right-to-work). Built to the **CGD Interactive Toolkit** standard (see below).
- `BOTEC-asylum-figure.html` — **Figure 2**: the charge (~£77m PV) vs the two right-to-work channels (~£200–400m PV) per cohort.
- `BOTEC-asylum-figure2.html` — **Figure 3**: refugee earnings vs the £25k repayment threshold (year 1 vs year 8).
- `TRACKING.md` — analytics events for the Figure 1 interactive (per CGD standard).

> Figure *file* numbers are historical (build order); the report renumbers them 1–2–3 in reading order, as above.

## Headline findings (lifetime, present value)
- Over a full 40-year working life the £10,000 charge recovers about **16% of face value in present value** (~28% nominal) — **~£77m PV per cohort** (~£45–103m across calibrations) — and only from the **~quarter of refugees who reach and hold full-time earnings above the £25k threshold**. About half never sustain that work and repay nothing. In student-loan terms, a **~84% RAB charge** (vs ~50% on graduate loans). *(A 10-year window shows ~5%; the full-horizon figure is higher but back-loaded — hence the PV framing.)*
- The right to work is worth **several times more, and sooner** — ~£200–400m PV per cohort (~3× the charge, like-for-like), via avoided support costs (Channel B) and avoided employment scarring (Channel C, calibrated on Fasani, Frattini & Minale 2020 and Hainmueller, Hangartner & Lawrence 2016).
- The charge is **parasitic** on the right to work: every pound repaid comes from someone earning above the threshold, which the ban prevents.
- Accounting for refusals makes the charge look *worse*, not better. Every number independently re-derived (see the verification box in the `.md`).

## The Figure 1 interactive (CGD Interactive Toolkit)
`BOTEC-asylum-figure3.html` is built to the [CGD Interactive Toolkit](https://github.com/Center-for-Global-Development/cgd-interactive-toolkit): CGD brand palette (Light Teal / Blue / Red, Inter as the Sofia Pro stand-in); an iframe-inside build (no outer chrome, transparent background, no fixed height, CGD `postMessage` resize); keyboard-accessible step controls with visible focus, `prefers-reduced-motion` support, an SVG title/desc and a data-table fallback; and the CGD analytics `postMessage` contract (`interactive_name: uk-asylum-charge-figure1`, see `TRACKING.md`).

**Before embedding on cgdev.org:** loop in comms (per the toolkit README); swap Inter → licensed **Sofia Pro**; confirm the GTM/GA4 listener is live for the analytics events. The other two figures + the report chrome are *not* yet on the CGD palette — rebrand them to match if the whole piece is going onto cgdev.org.

## Open follow-ups
- Reconciliation box vs the #LiftTheBan **£181m / £650m** coalition estimate.
- Add **remittances** as a fourth (development-lens) channel (~£31m/yr forgone, 2018).
- **Distribution vs mean earner:** the Figure 1 line is one representative worker; because repayment is kinked at the threshold and capped, the *median* full-time worker (£23k) repays £0 while the top quartile clears the £10k. The aggregate model already handles this; a distribution/quartile version of Figure 1 is worth adding.

## Sources
Home Office *Immigration System Statistics* & *Refugee Integration Outcomes (RIO) 2015–2023*; IPPR; NAO; Migration Observatory; student-loan Plan 5 terms; Fasani, Frattini & Minale (2020); Hainmueller, Hangartner & Lawrence (2016); #LiftTheBan coalition.
