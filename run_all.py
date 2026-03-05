"""
Daily orchestrator — runs all asset analyzers and collects reports.

Usage:
    python run_all.py

Output:
    reports/{YYYY-MM-DD}/
        summary.json          — per-asset signal/score/key metrics
        SP500/                — markdown report + chart PNG
        DAX/
        CAC40/
        FTSE100/
        SMI/
        PreciousMetals/       — Gold + Silver reports + charts
        FX/                   — FX report + per-currency dashboards + heatmap
        CIS300/               — CSI 300 report + chart
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Delay between consecutive analyzer runs (seconds) to avoid API rate limits
DELAY_BETWEEN_RUNS = 15

# Directories
ROOT_DIR = Path(__file__).resolve().parent
GLOBAL_MARKETS = ROOT_DIR / "global_markets"
CIS300_DIR = ROOT_DIR / "CIS300"
REPORTS_DIR = ROOT_DIR / "reports"
VENV_PYTHON = ROOT_DIR / "venv" / "Scripts" / "python.exe"

# If venv python doesn't exist (Linux/Mac), try just 'python'
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)

TODAY = datetime.now().strftime("%Y-%m-%d")

# Asset analyzers: (name, working_dir, script)
ANALYZERS = [
    ("SP500",          GLOBAL_MARKETS / "SP500",          "analyze.py"),
    ("DAX",            GLOBAL_MARKETS / "DAX",            "analyze.py"),
    ("CAC40",          GLOBAL_MARKETS / "CAC40",          "analyze.py"),
    ("FTSE100",        GLOBAL_MARKETS / "FTSE100",        "analyze.py"),
    ("SMI",            GLOBAL_MARKETS / "SMI",            "analyze.py"),
    ("PreciousMetals", GLOBAL_MARKETS / "PreciousMetals", "analyze.py"),
    ("FX",             GLOBAL_MARKETS / "FX",             "analyze.py"),
    ("CIS300",         CIS300_DIR,                        "PE_percentile.py"),
]


def run_analyzer(name: str, cwd: Path, script: str) -> bool:
    """Run a single analyzer script. Returns True on success."""
    print(f"\n{'='*60}")
    print(f"  Running: {name} ({script})")
    print(f"{'='*60}")
    try:
        # Set UTF-8 encoding to handle Chinese characters (CIS300)
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        result = subprocess.run(
            [str(VENV_PYTHON), script],
            cwd=str(cwd),
            capture_output=False,
            timeout=300,  # 5 min max per analyzer
            env=env,
        )
        if result.returncode != 0:
            print(f"  [WARN] {name} exited with code {result.returncode}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  [WARN] {name} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"  [FAIL] {name} failed: {e}")
        return False


def collect_reports(name: str, source_dir: Path, dest_dir: Path):
    """Copy generated report files and charts to the dated output directory."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []

    for pattern in ["*_report_*.md", "*_report*.md", "*.png"]:
        for f in source_dir.glob(pattern):
            if TODAY in f.name or not f.name.endswith(".md"):
                # Copy today's reports and all PNGs
                shutil.copy2(f, dest_dir / f.name)
                copied.append(f.name)

    if copied:
        print(f"  [OK] Collected {len(copied)} files for {name}")
    else:
        print(f"  [WARN] No report files found for {name}")

    return copied


def extract_signal_from_report(report_path: Path) -> dict:
    """Parse a markdown report to extract signal label and score."""
    result = {"signal": "N/A", "score": 0}
    try:
        content = report_path.read_text(encoding="utf-8")

        # Match composite signal line: **<<< STRONG SELL >>>** — Score: -4
        # or: **<< SELL >>** — Score: -3
        signal_match = re.search(
            r'## Composite Signal\s*\n\*\*(.+?)\*\*.*?Score:\s*([+-]?\d+)',
            content
        )
        if not signal_match:
            # Fallback: match from summary table row
            signal_match = re.search(
                r'\|\s*\*\*Signal\*\*\s*\|\s*\*\*(.+?)\*\*\s*\(Score:\s*([+-]?\d+)\)',
                content
            )
        if signal_match:
            result["signal"] = signal_match.group(1).strip()
            result["score"] = int(signal_match.group(2))

    except Exception:
        pass
    return result


def build_summary(output_dir: Path) -> dict:
    """Build summary.json from all collected reports."""
    summary = {"date": TODAY, "assets": {}}

    for name, _, _ in ANALYZERS:
        asset_dir = output_dir / name
        if not asset_dir.exists():
            summary["assets"][name] = {"signal": "N/A", "score": 0, "status": "failed"}
            continue

        # Find the first markdown report
        reports = list(asset_dir.glob("*_report_*.md")) + list(asset_dir.glob("*_report*.md"))
        if not reports:
            summary["assets"][name] = {"signal": "N/A", "score": 0, "status": "no_report"}
            continue

        signal_data = extract_signal_from_report(reports[0])
        signal_data["status"] = "ok"
        signal_data["report_file"] = reports[0].name

        # List chart files
        charts = [f.name for f in asset_dir.glob("*.png")]
        if charts:
            signal_data["charts"] = charts

        summary["assets"][name] = signal_data

    return summary


def main():
    print(f"\n{'#'*60}")
    print(f"  DAILY ANALYSIS RUN — {TODAY}")
    print(f"{'#'*60}")

    output_dir = REPORTS_DIR / TODAY
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    for idx, (name, cwd, script) in enumerate(ANALYZERS):
        # Delay between runs to avoid yfinance / API rate limits
        if idx > 0:
            print(f"\n  [WAIT] Cooling down {DELAY_BETWEEN_RUNS}s to avoid rate limits...")
            time.sleep(DELAY_BETWEEN_RUNS)

        success = run_analyzer(name, cwd, script)
        results[name] = success

        if success:
            collect_reports(name, cwd, output_dir / name)

    # Build and save summary
    summary = build_summary(output_dir)
    summary_path = output_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n  [SUMMARY] Saved: {summary_path}")

    # Print results
    print(f"\n{'='*60}")
    print(f"  RESULTS — {TODAY}")
    print(f"{'='*60}")
    for name, success in results.items():
        status = "[OK]" if success else "[FAIL]"
        signal = summary["assets"].get(name, {}).get("signal", "N/A")
        score = summary["assets"].get(name, {}).get("score", 0)
        print(f"  {name:20s}  {status:10s}  Signal: {signal} (Score: {score:+d})")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
