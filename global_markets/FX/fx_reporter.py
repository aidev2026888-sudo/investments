"""
Report generation for the five-dimensional currency valuation framework.

Prints a structured text report to console showing all metrics and
the composite signal for each currency, and saves a date-stamped
markdown copy.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from fx_config import FXFrameworkConfig


def print_separator(char: str = "=", width: int = 70):
    print(char * width)


def print_currency_report(
    code: str,
    country_name: str,
    reer_current: Optional[float],
    reer_z: Optional[float],
    reer_mean: Optional[float],
    reer_pctile: Optional[float],
    rpl_latest: Optional[float],
    rpl_deviation: Optional[float],
    ca_latest: Optional[float],
    ca_year: Optional[int],
    ca_label: Optional[str],
    real_rate: Optional[float],
    real_rate_diff: Optional[float],
    credit_gap_val: Optional[float],
    credit_gap_label: Optional[str],
    base_currency: str,
    signal_label: str,
    signal_factors: List[str],
    signal_score: int,
):
    """Print a detailed valuation report for one currency."""
    print_separator()
    print(f"  {code} -- {country_name}")
    print_separator()

    # REER
    print("\n  > Real Effective Exchange Rate (REER)")
    if reer_current is not None:
        print(f"    Current REER:   {reer_current:.1f}")
        print(f"    Long-term Mean: {reer_mean:.1f}")
        print(f"    Z-Score:        {reer_z:+.2f}")
        if reer_pctile is not None:
            print(f"    Percentile:     {reer_pctile:.1f}th")
    else:
        print("    Data unavailable")

    # Relative Price Level (BIS-derived PPP)
    print("\n  > Relative Price Level (REER/NEER)")
    if rpl_latest is not None:
        print(f"    Price Level:    {rpl_latest:.1f}")
        if rpl_deviation is not None:
            dev_label = "Expensive" if rpl_deviation > 5 else "Cheap" if rpl_deviation < -5 else "Near mean"
            print(f"    vs LT Mean:     {rpl_deviation:+.1f}% ({dev_label})")
    else:
        print("    Data unavailable")

    # Current Account
    print("\n  > Current Account (% GDP)")
    if ca_latest is not None:
        print(f"    Balance:        {ca_latest:+.2f}%  (as of {ca_year})")
        print(f"    Assessment:     {ca_label}")
    else:
        print("    Data unavailable")

    # Real Interest Rate
    print(f"\n  > Real Interest Rate (vs {base_currency})")
    if real_rate is not None:
        print(f"    Real Rate:      {real_rate:.2f}%")
        if real_rate_diff is not None:
            print(f"    Differential:   {real_rate_diff:+.2f} pp vs {base_currency}")
    else:
        print("    Data unavailable")

    # Credit-to-GDP Gap
    print("\n  > Credit-to-GDP Gap (BIS)")
    if credit_gap_val is not None:
        print(f"    Gap:            {credit_gap_val:+.1f} pp from trend")
        if credit_gap_label:
            print(f"    Assessment:     {credit_gap_label}")
    else:
        print("    Data unavailable")

    # Composite Signal
    print(f"\n  > COMPOSITE SIGNAL")
    print(f"    {'-' * 40}")
    print(f"    {signal_label}")
    print(f"    Score: {signal_score:+d}")
    print(f"    {'-' * 40}")
    for f in signal_factors:
        print(f"      * {f}")

    print()


def print_summary_table(summary_data: Dict[str, dict], base_currency: str):
    """Print a compact summary table for all currencies."""
    print_separator("=")
    print("  FIVE-DIMENSIONAL CURRENCY VALUATION SUMMARY")
    print_separator("=")

    # Header
    print(f"\n  {'CCY':<6} {'REER Z':>7} {'CA%GDP':>7} {'RateDf':>7} "
          f"{'CrGap':>6} {'Score':>6}  Signal")
    print(f"  {'-' * 62}")

    for code, d in summary_data.items():
        reer_z = d.get("reer_z")
        ca = d.get("ca_latest")
        diff = d.get("real_rate_diff")
        cg = d.get("credit_gap_val")
        score = d.get("composite_score", 0)
        label = d.get("signal_label", "N/A")

        reer_str = f"{reer_z:+.2f}" if reer_z is not None else "N/A"
        ca_str = f"{ca:+.1f}" if ca is not None else "N/A"
        diff_str = f"{diff:+.1f}" if diff is not None else "N/A"
        cg_str = f"{cg:+.1f}" if cg is not None else "N/A"

        # Short label
        short = label.strip("<> ").split("(")[0].strip()
        if len(short) > 18:
            short = short[:18]

        print(f"  {code:<6} {reer_str:>7} {ca_str:>7} {diff_str:>7} "
              f"{cg_str:>6} {score:>+6d}  {short}")

    print()


def print_framework_note():
    """Print a note about the five-dimensional framework."""
    print_separator("-")
    print("  FRAMEWORK INTERPRETATION:")
    print("  -------------------------")
    print("  * PPP & REER   -> Potential energy (how far the spring is compressed)")
    print("  * Current Acct -> Fundamental strength (organic capital flows)")
    print("  * Real Rate    -> Catalyst (what releases the spring)")
    print("  * Credit Gap   -> Financial stability (clean balance sheet = resilience)")
    print()
    print("  True SAFETY MARGIN exists when:")
    print("    [OK] REER is at extreme low (z < -1.5)")
    print("    [OK] Current Account is healthy (surplus)")
    print("    [OK] Real rate differential is turning (catalyst emerging)")
    print("    [OK] Credit gap is negative (system deleveraged, room to expand)")
    print_separator("-")


def save_fx_report_md(
    summary_data: Dict[str, dict],
    config,
    output_dir: str = ".",
) -> str:
    """Save the complete FX analysis as a date-stamped markdown file."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines: List[str] = []

    lines.append(f"# FX Valuation Framework — Report")
    lines.append(f"**Date**: {today}")
    lines.append(f"**Currencies**: {config.currency_codes}")
    lines.append(f"**Base**: {config.base_currency}\n")

    # Summary table
    lines.append("## Summary")
    lines.append(f"| CCY | REER Z | CA%GDP | Rate Diff | Cr.Gap | Score | Signal |")
    lines.append(f"|-----|--------|--------|-----------|--------|-------|--------|")
    for code, d in summary_data.items():
        rz = f"{d['reer_z']:+.2f}" if d.get('reer_z') is not None else "N/A"
        ca = f"{d['ca_latest']:+.1f}" if d.get('ca_latest') is not None else "N/A"
        rd = f"{d['real_rate_diff']:+.1f}" if d.get('real_rate_diff') is not None else "N/A"
        cg = f"{d['credit_gap_val']:+.1f}" if d.get('credit_gap_val') is not None else "N/A"
        sc = d.get('composite_score', 0)
        lab = d.get('signal_label', 'N/A').strip('<> ')
        lines.append(f"| {code} | {rz} | {ca} | {rd} | {cg} | {sc:+d} | {lab} |")
    lines.append("")

    # Per-currency details
    for code, d in summary_data.items():
        lines.append(f"## {code}")
        lines.append(f"| Dimension | Value | Assessment |")
        lines.append(f"|-----------|-------|------------|")

        rz = d.get('reer_z')
        lines.append(f"| REER Z-Score | {rz:+.2f} | {_reer_label(rz)} |" if rz is not None else "| REER | N/A | |")

        rpl = d.get('rpl_latest')
        rpl_dev = d.get('rpl_deviation')
        if rpl is not None:
            dev_label = "Expensive" if (rpl_dev or 0) > 5 else "Cheap" if (rpl_dev or 0) < -5 else "Near mean"
            lines.append(f"| Rel. Price Level | {rpl:.1f} ({rpl_dev:+.1f}%) | {dev_label} |")
        else:
            lines.append(f"| Rel. Price Level | N/A | |")

        ca_val = d.get('ca_latest')
        ca_label = d.get('ca_label', '')
        lines.append(f"| Current Account | {ca_val:+.2f}% GDP | {ca_label} |" if ca_val is not None else "| Current Account | N/A | |")

        rr = d.get('real_rate')
        rd = d.get('real_rate_diff')
        if rr is not None:
            diff_str = f"({rd:+.1f} pp vs {config.base_currency})" if rd is not None else ""
            lines.append(f"| Real Rate | {rr:.2f}% {diff_str} | |")
        else:
            lines.append(f"| Real Rate | N/A | |")

        cg = d.get('credit_gap_val')
        cg_label = d.get('credit_gap_label', '')
        lines.append(f"| Credit Gap | {cg:+.1f} pp | {cg_label} |" if cg is not None else "| Credit Gap | N/A | |")

        sc = d.get('composite_score', 0)
        lab = d.get('signal_label', 'N/A')
        lines.append(f"\n**Signal**: {lab} (Score: {sc:+d})\n")
        for f in d.get('signal_factors', []):
            lines.append(f"- {f}")
        lines.append("")

    filepath = os.path.join(output_dir, f"FX_report_{today}.md")
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"  [REPORT] Saved: {filepath}")
    return filepath


def _reer_label(z: float) -> str:
    """Short assessment label for REER z-score."""
    if z < -1.5:
        return "Very Cheap"
    elif z < -0.5:
        return "Cheap"
    elif z < 0.5:
        return "Fair Value"
    elif z < 1.5:
        return "Rich"
    else:
        return "Very Rich"
