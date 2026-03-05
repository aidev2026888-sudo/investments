"""Regenerate summary.json from existing reports."""
import json
import re
from pathlib import Path

REPORTS_DIR = Path(r"s:\work\repos\investments\reports\2026-03-05")


def extract_signal(report_path):
    result = {"signal": "N/A", "score": 0}
    try:
        content = report_path.read_text(encoding="utf-8")
        m = re.search(
            r"## Composite Signal\s*\n\*\*(.+?)\*\*.*?Score:\s*([+-]?\d+)",
            content,
        )
        if not m:
            m = re.search(
                r'\|\s*\*\*Signal\*\*\s*\|\s*\*\*(.+?)\*\*\s*\(Score:\s*([+-]?\d+)\)',
                content,
            )
        if m:
            result["signal"] = m.group(1).strip()
            result["score"] = int(m.group(2))
    except Exception as e:
        print(f"  Error: {e}")
    return result


summary = {"date": "2026-03-05", "assets": {}}

for d in sorted(REPORTS_DIR.iterdir()):
    if not d.is_dir():
        continue
    reports = list(d.glob("*report*.md"))
    charts = [f.name for f in d.glob("*.png")]
    if reports:
        sig = extract_signal(reports[0])
        sig["status"] = "ok"
        sig["report_file"] = reports[0].name
        if charts:
            sig["charts"] = charts
        summary["assets"][d.name] = sig
        print(f"  {d.name}: {sig['signal']} ({sig['score']:+d})")
    else:
        summary["assets"][d.name] = {"signal": "N/A", "score": 0, "status": "no_report"}
        print(f"  {d.name}: no reports found")

out = REPORTS_DIR / "summary.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {out}")
