#!/usr/bin/env python3
"""
check_readme.py — fail if the README's published numbers have drifted from the model.

    python3 check_readme.py        # exit 0 = README agrees with numbers.json

The README's "Where each blog number comes from" table is hand-written prose. The model is
the source of truth. Historically the two have drifted every time an assumption moved (the
cohort rebase, the Channel C present value, the Channel B midpoint), and at least one
hand-computed figure was simply wrong. This guard closes that gap: it parses each row of the
mapping table, pulls the `numbers.json` key out of the middle column, and checks that the
model's value actually appears in the stated Value column.

Deliberately loose: it asserts the model's number is PRESENT in the cell, not that the cell
matches some canonical format — so "£82m (£48–109m)" satisfies charge_agg_pv_m = 82. It
catches drift, not prose style.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = json.loads((HERE / "numbers.json").read_text())
README = (HERE / "README.md").read_text()

ROW = re.compile(r"^\|(?P<claim>[^|]+)\|(?P<keys>[^|]+)\|(?P<value>[^|]+)\|\s*$", re.M)
BACKTICKED = re.compile(r"`([a-z_0-9…\.]+)`")


def nums_in(text):
    """Every number in a table cell, ignoring £ , × and en-dashes."""
    return {float(m) for m in re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))}


def expected(val):
    """The number(s) a key's value could legitimately print as."""
    if isinstance(val, list):
        return {float(v) for v in val}
    return {float(val)}


problems, checked = [], 0
for m in ROW.finditer(README):
    keys = BACKTICKED.findall(m.group("keys"))
    if not keys:
        continue
    cell = m.group("value")
    shown = nums_in(cell)
    for k in keys:
        if k.startswith("…") or k not in N:      # abbreviated refs like `…_range_m`
            continue
        checked += 1
        want = expected(N[k])
        if not want & shown:
            problems.append(
                f"  {k}\n"
                f"     model says : {N[k]}\n"
                f"     README says: {cell.strip()}\n"
                f"     claim      : {m.group('claim').strip()}"
            )

print(f"check_readme: {checked} mapped value(s) checked against numbers.json")
if problems:
    print(f"\nDRIFT DETECTED — {len(problems)} README value(s) disagree with the model:\n")
    print("\n\n".join(problems))
    print("\nRe-run `python3 model.py`, then update the README to match. The model is the truth.")
    sys.exit(1)
print("OK — every mapped README value matches the model.")
