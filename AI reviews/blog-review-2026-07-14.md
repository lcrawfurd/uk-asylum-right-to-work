# Blog review — "The UK's £10,000 asylum charge is worth £82 million…"

Reviewed 2026-07-14 against Lee's *How to Blog for Think Tanks* (Mirchandani / Green / Economist / Plain English). Draft: 1,993 words.

---

## PART A — Numbers check (against `model.py` / `numbers.json`)

The title and the aggregate £82m are correct and current. But the **individual section and the two right-to-work channels are stale** — they pre-date the model rebuild (85k adult base, 2-panel 40-year figure, dropped Panel C). Fix before publishing.

### ❌ Errors / stale numbers

| # | Blog says | Should be | Note |
|---|---|---|---|
| 1 | "24%… rising to **48 percent in the second year**" | 24% yr1 → **45% yr2 → 48% by year 8** | 48% is the *year-8* figure, not year 2. Straight factual error. |
| 2 | "reaching £31,000, **repays just £3,300 over 20 years**" | Repays the **full £10,000, but only by year 28 — worth ~£5,400 in present value** | Contradicts the sentence *before* it ("an 80th-percentile earner… who we can expect to actually repay the full charge"). This is the old slow-ramp earner; delete. |
| 3 | "contribute **four times more in tax (£45,000)**… start paying **five years sooner**" | Remove | This was Panel C (individual right-to-work). We dropped it: it rested 93% on an unpinned wage-plateau assumption the cited studies don't support (they measure *employment*, not *wages*). The honest individual right-to-work effect is only ~+£3,750. |
| 4 | "the third step… allow the refugee to work after three months, which **shifts both immediate and subsequent earnings upward**" | Remove / rewrite for 2 steps | No third step now. "Subsequent earnings upward" = the intensive-margin claim we cut. |
| 5 | Fig 3 note: "**over 20 years**… **all three panels**" | "Two panels over 40 years" | Figure is now 2-panel (A vs B), 40-year. |
| 6 | Channel B "**£130–220 million**" | **£140–234 million** | Rebased to 85k adults. |
| 7 | Channel C "**£115 million** per cohort" | **£122 million** | Rebased. |
| 8 | "reducing the work ban from **12 to three months**… **3 percentage points**" | Either "12 to **six** months" or a *larger* gain for 12→3 | The 3pp is calibrated for a **12→6** cut. Applying it to a 12→3 cut understates. Pick one period and keep it consistent. |
| 9 | "Around **100,000** people claim asylum… roughly **£82 million** per cohort" | Clarify the base | £82m derives from **~85,000 adults** × 60% grant = ~51,000 who can repay. 100k is *total* claims (incl. children who can't be charged). State the adult base, or £82m looks unsupported by the 100k headline. |
| 10 | Hotel section: "nearly a quarter work immediately… rises to **40 percent by the end of the first year**" | Reconcile | Contradicts "24%… in the first year" stated earlier. Model has 24% (yr1) → 45% (yr2); no 40% figure. |

### ⚠️ Worth checking

- **Title "£290 million"** — within our £210–420m range, but the *body* B+C (once fixed to £140–234m + £122m) sums to ~£300–310m. Either round the title to ~£300m or keep £290m as a conservative point — just make body and title reconcile.
- **"£144 per night… over five times more"** — actually **6.2×** (£144.98 vs £23.25). "Over five" is safe but you could say "over six."
- **Hotel saving "£250 million"** — model gives £300m (10% move-out) / £750m (25%). £250m reads as a deliberately conservative residual; fine, but state the basis.
- **"£3.1 billion on hotels"** — model uses £3.0bn (NAO). Trivial.

### ✅ Verified correct

£10,000 charge · £41,000 (2023/24) & £17,000 (2019/20) support cost · 24% employment yr1 · 13% earn ≥£20k (Migration Obs) · 9% above £25,000 · median full-time £23,000 · 13% above £25k by yr8 · two-thirds pay nothing / top 22% clear · half don't work at yr8 · 1% above £25k yr1 · £82m / "a sixth" · £11,000 per person (Channel B unit) · Hainmueller 4–5pp / Fasani 15% / up to a decade · "several times more" (3.8×).

---

## PART B — Writing review

### 1. Three-sentence summary (it passes — one clean idea)

1. The UK's new Bill imposes a £10,000 charge on asylum seekers to recoup support costs.
2. Modelled like a student loan, it recovers only ~£82m per cohort (a sixth of face value, over decades) — while letting people work sooner is worth several times more (~£290m) and arrives up front.
3. So "make them pay" is impossible without "let them work": the right to work is the far bigger fiscal prize.

Good — the piece has a single, coherent argument. The problem is **structure and length**, not focus.

### 2. Hard-rule violations

1. **Buried lede.** The £82m-vs-£290m finding — the whole point — doesn't arrive until ~paragraph 15, under "Across the whole asylum seeker population." The first third is Bill mechanics + support costs + ODA/aid-budget. The *title* punches; the *body* makes the reader wait. **Fix: state the finding in para 2–3.**
2. **Length: 1,993 words** — ~2.5× the 800-word target. Biggest single problem after the buried lede.
3. Footnotes: **none** (inline links). ✓
4. Chart: present (Figs 1–3). ✓ (but Fig 3 caption is stale — see Part A.)

### 3. Preparation checklist

| # | Check | Verdict | Reason |
|---|---|---|---|
| 1 | Finding in para 2–3? | **FAIL** | Lands ~⅔ down, under the population section. |
| 2 | Crowded-bus test? | **PARTIAL** | Title yes; body makes them work for it. |
| 3 | First two paras throat-clearing? | **PARTIAL** | Intro para is fine; but "Understanding the payment" + "cost of asylum support" delay the finding by ~800 words. |
| 4 | Every sentence <20 words? | **FAIL** | Several 35–50-word sentences (see line edits). |
| 5 | Active voice? | **PARTIAL** | "It has been compared…", "payments will be made…", "costs have been assigned…", "was spent on…". |
| 6 | Jargon removed? | **PARTIAL** | "ODA", "in-country refugee costs", "official development assistance" — spell out or cut for a general reader. |
| 7 | Zero footnotes? | **PASS** | — |
| 8 | Chart included? | **PASS** | Three, though Fig 3 needs re-labelling. |
| 9 | Title makes a claim? | **PASS** | Strong two-number claim — the best thing in the draft. |
| 10 | Under 800 words? | **FAIL** | 1,993. |
| 11 | Above-the-fold test? | **FAIL** | Stop after 5 paras and you've read about aid-budget accounting, not the charge-vs-work finding. |

### 4. Structure map (news pyramid vs actual)

The draft runs in **report order** (context → mechanics → costs → evidence → finding → implications), not **news-pyramid** (finding → evidence → context → so-what). The ODA/aid-budget section (3 paragraphs) is genuinely interesting but is a *second* story competing with the main one; it belongs lower, tighter, or in a companion piece.

### 5. Top 3 priority fixes

**Fix 1 — Punch early. Move the finding to para 2.**
Current para 2 is about the Bill's legal mechanics. Replace the opening run-up with the result:

> *The government says the £10,000 charge will help asylum seekers "contribute" to their support. We modelled it. Recovered like a student loan, it claws back only about £82 million a year — a sixth of its face value, dribbling in over decades. Letting the same people work while they wait is worth several times more, arrives up front, and — unlike the charge — actually helps them. You cannot make someone pay £10,000 out of earnings the state forbids them to earn.*

**Fix 2 — Cut to ~800–1,000 words.** The ODA/aid-budget section (para "Most of these costs…" through "£2.4 billion…") is ~250 words of a different argument — compress to two sentences or drop. The hotel section repeats the "double inefficiency" point the closing section already makes — merge them.

**Fix 3 — Rebuild the individual section around the *current* model** (this doubles as the Part-A fix). Replace the stale £3,300 / £45,000 / 20-year / three-panel passage with:

> *Take a refugee who does relatively well — the 80th percentile of earners, one of the ~fifth who ever repay in full. Even they clear the £10,000 only after 28 years of work, so in today's money the Exchequer nets barely £5,000 of it. Most refugees pay nothing.*

Then let the *aggregate* carry the right-to-work case (Channels B & C), rather than the individual chart — because one already-working person can't show a population effect.

### Line edits (worst offenders)

- *"The Home Office's own data notes that 24 percent of working-age people who were granted refugee status between 2015 and 2023 were in employment in the first year after being granted refugee status, rising to 48 percent in the second year."* (40 words, and the 48% is wrong)
  → **"Home Office data shows just 24% of refugees work in their first year with status, rising to 45% by year two and 48% by year eight."**
- *"It therefore seems plausible that a quarter would prefer their own accommodation … could still plausibly save a further £250 million per year."* (~50 words)
  → Split into two sentences; lead with the number.
- *"It has been compared to a student loan."* → **"The charge works like a student loan."**
- *"Most of these costs have been assigned to the UK's aid budget."* → **"The government charges most of these costs to the aid budget."**
