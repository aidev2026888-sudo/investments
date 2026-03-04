"""
Report module for global market index analysis.

Formats and prints a comprehensive valuation report to stdout,
and optionally saves a date-stamped markdown copy.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .config import IndexConfig, CAPE_DEVIATION_HIGH, CAPE_DEVIATION_LOW


def print_report(
    config: IndexConfig,
    current_pe: float,
    forward_pe: Optional[float],
    percentile: float,
    pe_percentile_values: Dict[int, float],
    cape_value: Optional[float],
    cape_deviation: Optional[float],
    erp_result: Optional[Tuple[float, float]],
    bond_yield: Optional[float],
    signal_label: str,
    signal_factors: List[str],
    signal_score: int,
    confidence: str,
    buffett_indicator: Optional[float] = None,
    vix_data: Optional[dict] = None,
    vix_signal: Optional[tuple] = None,
) -> None:
    """Print a comprehensive valuation report to the console.

    Args:
        config:               Index configuration.
        current_pe:           Current trailing PE.
        forward_pe:           Forward PE (may be None).
        percentile:           Current PE percentile.
        pe_percentile_values: Dict of {level: pe_value}.
        cape_value:           Simplified CAPE value.
        cape_deviation:       CAPE deviation percentage.
        erp_result:           Tuple of (earnings_yield, erp) or None.
        bond_yield:           10-year bond yield as decimal or None.
        signal_label:         Composite signal label.
        signal_factors:       List of factor descriptions.
        signal_score:         Composite score.
        confidence:           Confidence string.
        buffett_indicator:    Buffett Indicator (%) or None.
    """
    sep = "=" * 60

    print(f"\n{sep}")
    print(f"  [INDEX]  {config.name} ({config.ticker})  --  Valuation Report")
    print(f"{sep}")

    # --- Current PE ---
    print(f"  Current Trailing PE:  {current_pe:.2f}")
    if forward_pe is not None:
        print(f"  Current Forward PE:   {forward_pe:.2f}")
    if cape_value is not None:
        print(f"  {config.cape_rolling_years}yr Rolling Avg PE (CAPE):  {cape_value:.2f}")
    print(f"  PE Percentile ({config.years_back}yr):  {percentile:.1f}%")
    print(f"{sep}")

    # --- Percentile Values ---
    print(f"  PE Percentile Reference Values ({config.years_back}-year history):")
    for p in sorted(pe_percentile_values.keys(), reverse=True):
        marker = " ◀ Current" if abs(percentile - p) < 10 else ""
        print(f"    {p:3d}th pctl PE = {pe_percentile_values[p]:.2f}{marker}")
    print(f"{sep}")

    # --- Valuation Signal ---
    if percentile >= 80:
        print(f"  [!] OVERVALUED: PE is in the top 20% of the {config.years_back}-year range")
    elif percentile <= 20:
        print(f"  [*] UNDERVALUED: PE is in the bottom 20% of the {config.years_back}-year range")
    else:
        print(f"  [i] PE is in the middle range of the {config.years_back}-year distribution")

    # --- CAPE Deviation ---
    if cape_deviation is not None:
        print(f"\n  [CAPE] CAPE Deviation Analysis:")
        print(f"    Current PE:                  {current_pe:.2f}")
        print(f"    {config.cape_rolling_years}yr Rolling Avg PE (CAPE):  {cape_value:.2f}")
        print(f"    Deviation:                   {cape_deviation:+.2f}%")
        if cape_deviation > CAPE_DEVIATION_HIGH:
            print(f"    [!] PE is significantly above {config.cape_rolling_years}yr average -- short-term overheating")
        elif cape_deviation < CAPE_DEVIATION_LOW:
            print(f"    [*] PE is significantly below {config.cape_rolling_years}yr average -- potential undervaluation")
        else:
            print(f"    [OK] Deviation within normal range (+/-{CAPE_DEVIATION_HIGH}%)")
        print(f"{sep}")

    # --- ERP (Equity Risk Premium) ---
    if erp_result is not None and bond_yield is not None:
        earnings_yield, erp = erp_result
        print(f"\n  [ERP] Equity Risk Premium (ERP) -- Yield Gap Analysis:")
        print(f"    Earnings Yield (1/PE):   {earnings_yield * 100:.2f}%")
        print(f"    10-Year Bond Yield:      {bond_yield * 100:.2f}%")
        print(f"    ERP = {earnings_yield * 100:.2f}% - {bond_yield * 100:.2f}% = {erp * 100:.2f}%")

        if erp > 0.06:
            print(f"    [*] ERP > 6% -- Equities are extremely attractive vs bonds")
        elif erp > 0.03:
            print(f"    [*] ERP 3-6% -- Equities have moderate appeal vs bonds")
        elif erp > 0:
            print(f"    [i] ERP 0-3% -- Equities and bonds roughly comparable")
        else:
            print(f"    [!] ERP < 0% -- Bond yield exceeds earnings yield; equities expensive")
        print(f"{sep}")

    # --- Buffett Indicator ---
    if buffett_indicator is not None:
        print(f"\n  [BUFFETT] Buffett Indicator (Market Cap / GDP):")
        print(f"    Ratio: {buffett_indicator:.1f}%")
        if buffett_indicator > 150:
            print(f"    [!] > 150% -- Market is significantly overvalued relative to GDP")
        elif buffett_indicator > 100:
            print(f"    [i] 100-150% -- Market is moderately valued to slightly overvalued")
        else:
            print(f"    [*] < 100% -- Market is fairly valued to undervalued relative to GDP")
        print(f"{sep}")

    # --- Composite Signal ---
    print(f"\n  [SIGNAL] Composite Signal (Multi-Factor Model):")
    print(f"    Signal:     {signal_label}  (Score: {signal_score:+d}, Confidence: {confidence})")
    print(f"    Factors:")
    for f in signal_factors:
        print(f"      - {f}")
    print(f"{sep}\n")

    # --- VIX Fear Gauge ---
    if vix_data and vix_signal:
        zone, desc, is_retreat = vix_signal
        print(f"  [VIX] Fear Gauge (Contrarian Indicator):")
        print(f"    Current VIX:     {vix_data['current']:.1f}")
        print(f"    Zone:            {zone}")
        print(f"    Percentile (2yr): {vix_data['percentile']:.0f}th")
        print(f"    20d High:        {vix_data['high_20d']:.1f} (Surge: {vix_data['surge_pct']:+.0f}%, Retreat: {vix_data['retreat_pct']:.0f}%)")
        print(f"    {desc}")
        if is_retreat:
            print(f"    [!!] SPIKE-RETREAT: VIX peaked and is subsiding -- historically strong buy signal")
        print(f"{sep}\n")


def save_report_md(
    config: IndexConfig,
    current_pe: float,
    forward_pe: Optional[float],
    percentile: float,
    pe_percentile_values: Dict[int, float],
    cape_value: Optional[float],
    cape_deviation: Optional[float],
    erp_result: Optional[Tuple[float, float]],
    bond_yield: Optional[float],
    signal_label: str,
    signal_factors: List[str],
    signal_score: int,
    confidence: str,
    buffett_indicator: Optional[float] = None,
    vix_data: Optional[dict] = None,
    vix_signal: Optional[tuple] = None,
    output_dir: str = ".",
) -> str:
    """Save the valuation report as a date-stamped markdown file.

    Returns the path to the saved file.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    lines: List[str] = []

    lines.append(f"# {config.name} ({config.ticker}) — Valuation Report")
    lines.append(f"**Date**: {today}\n")

    # --- Summary ---
    lines.append("## Summary")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Trailing PE | {current_pe:.2f} |")
    if forward_pe is not None:
        lines.append(f"| Forward PE | {forward_pe:.2f} |")
    if cape_value is not None:
        lines.append(f"| {config.cape_rolling_years}yr CAPE | {cape_value:.2f} |")
    lines.append(f"| PE Percentile ({config.years_back}yr) | {percentile:.1f}% |")
    if bond_yield is not None:
        lines.append(f"| 10Y Bond Yield | {bond_yield * 100:.2f}% |")
    if erp_result is not None:
        lines.append(f"| Earnings Yield | {erp_result[0] * 100:.2f}% |")
        lines.append(f"| ERP | {erp_result[1] * 100:.2f}% |")
    if cape_deviation is not None:
        lines.append(f"| CAPE Deviation | {cape_deviation:+.1f}% |")
    if buffett_indicator is not None:
        lines.append(f"| Buffett Indicator | {buffett_indicator:.1f}% |")
    lines.append(f"| **Signal** | **{signal_label}** (Score: {signal_score:+d}) |")
    lines.append("")

    # --- PE Percentile ---
    lines.append("## PE Percentile Distribution")
    lines.append(f"| Percentile | PE Value |")
    lines.append(f"|-----------|---------|")
    for p in sorted(pe_percentile_values.keys(), reverse=True):
        marker = " ◀ Current" if abs(percentile - p) < 10 else ""
        lines.append(f"| {p}th | {pe_percentile_values[p]:.2f}{marker} |")

    if percentile >= 80:
        lines.append(f"\n> **⚠️ OVERVALUED**: PE is in the top 20% of the {config.years_back}-year range")
    elif percentile <= 20:
        lines.append(f"\n> **✅ UNDERVALUED**: PE is in the bottom 20% of the {config.years_back}-year range")
    else:
        lines.append(f"\n> PE is in the middle range of the {config.years_back}-year distribution")
    lines.append("")

    # --- CAPE Deviation ---
    if cape_deviation is not None:
        lines.append("## CAPE Deviation")
        lines.append(f"- Current PE: **{current_pe:.2f}**")
        lines.append(f"- {config.cape_rolling_years}yr Rolling Avg: **{cape_value:.2f}**")
        lines.append(f"- Deviation: **{cape_deviation:+.1f}%**")
        if cape_deviation > CAPE_DEVIATION_HIGH:
            lines.append(f"\n> ⚠️ PE is significantly above {config.cape_rolling_years}yr average — short-term overheating")
        elif cape_deviation < CAPE_DEVIATION_LOW:
            lines.append(f"\n> ✅ PE is significantly below {config.cape_rolling_years}yr average — potential undervaluation")
        else:
            lines.append(f"\n> Deviation within normal range (±{CAPE_DEVIATION_HIGH}%)")
        lines.append("")

    # --- ERP ---
    if erp_result is not None and bond_yield is not None:
        earnings_yield, erp = erp_result
        lines.append("## Equity Risk Premium (ERP)")
        lines.append(f"- Earnings Yield (1/PE): **{earnings_yield * 100:.2f}%**")
        lines.append(f"- 10Y Bond Yield: **{bond_yield * 100:.2f}%**")
        lines.append(f"- ERP: **{erp * 100:.2f}%**")
        if erp > 0.06:
            lines.append(f"\n> ✅ ERP > 6% — Equities are extremely attractive vs bonds")
        elif erp > 0.03:
            lines.append(f"\n> ✅ ERP 3–6% — Equities have moderate appeal vs bonds")
        elif erp > 0:
            lines.append(f"\n> ERP 0–3% — Equities and bonds roughly comparable")
        else:
            lines.append(f"\n> ⚠️ ERP < 0% — Bond yield exceeds earnings yield; equities expensive")
        lines.append("")

    # --- Buffett Indicator ---
    if buffett_indicator is not None:
        lines.append("## Buffett Indicator")
        lines.append(f"- Market Cap / GDP: **{buffett_indicator:.1f}%**")
        if buffett_indicator > 150:
            lines.append(f"\n> ⚠️ > 150% — Market significantly overvalued relative to GDP")
        elif buffett_indicator > 100:
            lines.append(f"\n> 100–150% — Moderately valued to slightly overvalued")
        else:
            lines.append(f"\n> ✅ < 100% — Fairly valued to undervalued relative to GDP")
        lines.append("")

    # --- Composite Signal ---
    lines.append("## Composite Signal")
    lines.append(f"**{signal_label}** — Score: {signal_score:+d}, Confidence: {confidence}\n")
    lines.append("| Factor | Assessment |")
    lines.append("|--------|-----------|")
    for f in signal_factors:
        lines.append(f"| {f} |  |")
    lines.append("")

    # --- VIX ---
    if vix_data and vix_signal:
        zone, desc, is_retreat = vix_signal
        lines.append("## VIX Fear Gauge")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Current VIX | {vix_data['current']:.1f} |")
        lines.append(f"| Zone | **{zone}** |")
        lines.append(f"| Percentile (2yr) | {vix_data['percentile']:.0f}th |")
        lines.append(f"| 20d High | {vix_data['high_20d']:.1f} |")
        lines.append(f"| Surge | {vix_data['surge_pct']:+.0f}% |")
        lines.append(f"| Retreat from peak | {vix_data['retreat_pct']:.0f}% |")
        lines.append(f"| Spike-Retreat | {'**YES**' if is_retreat else 'No'} |")
        lines.append(f"\n{desc}\n")

    # --- Write file ---
    safe_name = config.name.replace(" ", "_").replace("&", "and")
    filename = f"{safe_name}_report_{today}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"  [REPORT] Saved: {filepath}")
    return filepath
