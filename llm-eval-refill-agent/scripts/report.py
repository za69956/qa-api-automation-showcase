"""Summarise a Promptfoo run into the release-gate numbers (reports/report.md)."""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "reports" / "promptfoo_results.json").read_text())
rows = data["results"]["results"]

stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # provider -> metric -> [pass, total]
fails = defaultdict(list)
for r in rows:
    prov = r["provider"]["label"]
    for comp in r["gradingResult"]["componentResults"]:
        m = comp["assertion"]["metric"]
        stats[prov][m][1] += 1
        stats[prov][m][0] += int(comp["pass"])
        if not comp["pass"]:
            fails[prov].append(f'{r["testCase"]["description"]}: {comp["reason"]}')

metrics = sorted({m for p in stats.values() for m in p})
lines = ["# Eval report: refill agent v1 vs v2", "",
         "| Metric | " + " | ".join(stats) + " |", "|---" * (len(stats) + 1) + "|"]
for m in metrics:
    cells = []
    for p in stats:
        ok, n = stats[p][m]
        cells.append(f"{ok}/{n}")
    lines.append(f"| {m} | " + " | ".join(cells) + " |")

lines += ["", "**False-confirmation rate** (refill replies claiming success without an EHR "
          "confirmation number / all refill attempts):", ""]
for p in stats:
    ok, n = stats[p]["no_false_confirmation"]
    rate = (n - ok) / n
    verdict = "PASS" if rate == 0 else "BLOCK"
    lines.append(f"- {p}: {rate:.0%} ({n - ok} of {n}) -> {verdict}")
lines += ["", "## Failures", ""]
for p, items in fails.items():
    lines.append(f"**{p}**")
    lines += [f"- {i}" for i in items]
    lines.append("")
(ROOT / "reports" / "report.md").write_text("\n".join(lines))
print("\n".join(lines[:12]))
cand = [p for p in stats if "v2" in p][0]
sys.exit(0 if all(stats[cand][m][0] == stats[cand][m][1] for m in metrics) else 1)
