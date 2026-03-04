"""
Report module for precious metals (Gold/Silver) analysis.

Formats and prints comprehensive valuation reports using dynamic
miner P/B ratios, and saves date-stamped markdown copies.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def print_gold_report(
    spot_price: float,
    real_yield: Optional[float],
    real_yield_signal: Optional[Tuple[str, str]],
    miner_pb: Optional[float],
    safety_zone: str,
    safety_interp: str,
    miner_data: Optional[dict],
    gold_gdx_ratio: Optional[float],
    price_percentile: float,
    percentile_values: Dict[int, float],
    signal_label: str,
    signal_factors: List[str],
    signal_score: int,
    confidence: str,
    years_back: int = 10,
) -> None:
    """Print a comprehensive gold valuation report to the console."""
    sep = "=" * 60

    print(f"\n{sep}")
    print(f"  [GOLD]  Precious Metals (Gold)  --  Valuation Report")
    print(f"{sep}")

    # --- Current Price ---
    print(f"  Gold Spot Price:      ${spot_price:,.2f} /oz")
    if miner_pb is not None:
        print(f"  Miner Avg P/B:        {miner_pb:.2f}  ({safety_zone})")
    if gold_gdx_ratio is not None:
        print(f"  Gold/GDX Ratio:       {gold_gdx_ratio:.1f}")
    print(f"  Price Percentile ({years_back}yr): {price_percentile:.1f}%")
    print(f"{sep}")

    # --- Real Yield Analysis ---
    print(f"\n  [REAL YIELD] US 10-Year TIPS Real Yield Analysis:")
    if real_yield is not None:
        ry_pct = real_yield * 100
        print(f"    Real Yield:     {ry_pct:+.2f}%")
        if real_yield_signal:
            zone, interp = real_yield_signal
            print(f"    Zone:           {zone}")
            print(f"    Interpretation: {interp}")

        print(f"\n    Logic: Gold has no yield. Its opportunity cost = real interest rate.")
        if ry_pct > 2.0:
            print(f"    [!] Real yield > 2%: high opportunity cost -> bearish for gold")
        elif ry_pct > 0:
            print(f"    [i] Real yield > 0%: positive real rates -> mild headwind for gold")
        else:
            print(f"    [*] Real yield < 0%: negative real rates -> gold is the best asset")
    else:
        print(f"    [WARN] Real yield data unavailable")
    print(f"{sep}")

    # --- Dynamic Safety Margin (Miner P/B) ---
    print(f"\n  [SAFETY MARGIN] Miner P/B -- Dynamic AISC Proxy:")
    if miner_data is not None and miner_data.get("miners"):
        for m in miner_data["miners"]:
            margin_str = f"{m['op_margin']*100:.1f}%" if m.get('op_margin') else "N/A"
            print(f"    [{m['ticker']}] P/B={m['pb']:.2f}, "
                  f"OpMargin={margin_str}"
                  + (f", BookValue=${m['book_value']:.2f}" if m.get('book_value') else ""))
        print(f"    --------")
        print(f"    Average: P/B={miner_pb:.2f}  Zone: {safety_zone}")
        print(f"    {safety_interp}")
    else:
        print(f"    [WARN] Miner data unavailable")

    print(f"\n    Logic: When miner P/B < 1.0, mines are valued below book value")
    print(f"    -> gold price is near/below industry AISC -> maximum safety margin.")
    print(f"    When P/B > 4.0, extreme profitability -> no safety margin.")

    if gold_gdx_ratio is not None:
        print(f"\n    Gold/GDX Ratio: {gold_gdx_ratio:.1f}")
        print(f"    (High ratio = gold outperforming miners = margin pressure)")
    print(f"{sep}")

    # --- Price Percentile ---
    print(f"\n  [PERCENTILE] {years_back}-Year Price Distribution:")
    for p in sorted(percentile_values.keys(), reverse=True):
        marker = " < Current" if abs(price_percentile - p) < 10 else ""
        print(f"    {p:3d}th pctl = ${percentile_values[p]:,.2f}{marker}")

    if price_percentile >= 80:
        print(f"  [!] Price is in the TOP 20% of {years_back}-year range -- historically expensive")
    elif price_percentile <= 20:
        print(f"  [*] Price is in the BOTTOM 20% of {years_back}-year range -- historically cheap")
    else:
        print(f"  [i] Price is in the middle range of {years_back}-year distribution")
    print(f"{sep}")

    # --- Composite Signal ---
    print(f"\n  [SIGNAL] Composite Signal (Multi-Factor Model):")
    print(f"    Signal:     {signal_label}  (Score: {signal_score:+d}, Confidence: {confidence})")
    print(f"    Factors:")
    for f in signal_factors:
        print(f"      - {f}")
    print(f"{sep}\n")


def print_silver_report(
    spot_price: float,
    gold_price: float,
    gsr: float,
    gsr_signal: tuple,
    real_yield: Optional[float],
    miner_pb: Optional[float],
    safety_zone: str,
    safety_interp: str,
    miner_data: Optional[dict],
    inventory_data: Optional[dict],
    inventory_signal: Optional[Tuple[str, str]],
    price_percentile: float,
    percentile_values: Dict[int, float],
    signal_label: str,
    signal_factors: List[str],
    signal_score: int,
    confidence: str,
    years_back: int = 10,
) -> None:
    """Print a comprehensive silver valuation report to the console."""
    sep = "=" * 60

    print(f"\n{sep}")
    print(f"  [SILVER]  Precious Metals (Silver)  --  Valuation Report")
    print(f"{sep}")

    # --- Current Price ---
    print(f"  Silver Spot Price:    ${spot_price:.2f} /oz")
    print(f"  Gold Spot Price:      ${gold_price:,.2f} /oz")
    print(f"  Gold/Silver Ratio:    {gsr:.1f}")
    if miner_pb is not None:
        print(f"  Silver Miner P/B:     {miner_pb:.2f}  ({safety_zone})")
    print(f"  Price Percentile ({years_back}yr): {price_percentile:.1f}%")
    print(f"{sep}")

    # --- Gold/Silver Ratio ---
    gsr_zone, gsr_interp = gsr_signal
    print(f"\n  [GSR] Gold/Silver Ratio Analysis:")
    print(f"    Current GSR:    {gsr:.1f}")
    print(f"    Zone:           {gsr_zone}")
    print(f"    {gsr_interp}")
    print(f"\n    Logic: Historical GSR avg ~60-70. High GSR = silver cheap vs gold.")
    if gsr > 80:
        print(f"    [*] GSR > 80: silver is undervalued relative to gold")
    elif gsr < 50:
        print(f"    [!] GSR < 50: silver is overvalued relative to gold")
    else:
        print(f"    [i] GSR in normal range")
    print(f"{sep}")

    # --- Dynamic Safety Margin (Miner P/B) ---
    print(f"\n  [SAFETY MARGIN] Silver Miner P/B -- Dynamic AISC Proxy:")
    if miner_data is not None and miner_data.get("miners"):
        for m in miner_data["miners"]:
            margin_str = f"{m['op_margin']*100:.1f}%" if m.get('op_margin') else "N/A"
            print(f"    [{m['ticker']}] P/B={m['pb']:.2f}, OpMargin={margin_str}")
        print(f"    --------")
        print(f"    Average: P/B={miner_pb:.2f}  Zone: {safety_zone}")
        print(f"    {safety_interp}")
    else:
        print(f"    [WARN] Silver miner data unavailable")
    print(f"{sep}")

    # --- Inventory ---
    if inventory_data is not None:
        print(f"\n  [INVENTORY] COMEX / Visible Silver Inventory:")
        print(f"    Source: {inventory_data.get('source', 'N/A')}")
        if inventory_signal:
            inv_label, inv_interp = inventory_signal[0], inventory_signal[1]
            coverage_ratio = inventory_signal[2] if len(inventory_signal) > 2 else None
            coverage_zone = inventory_signal[3] if len(inventory_signal) > 3 else None
            print(f"    Status: {inv_label}")
            print(f"    {inv_interp}")
            if coverage_ratio is not None:
                print(f"\n    [SQUEEZE RISK] Coverage Ratio: {coverage_ratio:.1f}%")
                if coverage_zone == "CRITICAL":
                    print(f"    [!!!] CRITICAL: Inventory covers <20% of open interest")
                    print(f"    [!!!] Extreme squeeze risk (Jan 2026 crash was ~14%)")
                elif coverage_zone == "TIGHT":
                    print(f"    [!!] TIGHT: Elevated squeeze risk — monitor closely")
                elif coverage_zone == "ADEQUATE":
                    print(f"    [i] Adequate inventory coverage")
                else:
                    print(f"    [OK] Comfortable inventory coverage")
        print(f"{sep}")

    # --- Price Percentile ---
    print(f"\n  [PERCENTILE] {years_back}-Year Price Distribution:")
    for p in sorted(percentile_values.keys(), reverse=True):
        marker = " < Current" if abs(price_percentile - p) < 10 else ""
        print(f"    {p:3d}th pctl = ${percentile_values[p]:.2f}{marker}")

    if price_percentile >= 80:
        print(f"  [!] Price is in TOP 20% of {years_back}-year range")
    elif price_percentile <= 20:
        print(f"  [*] Price is in BOTTOM 20% of {years_back}-year range")
    else:
        print(f"  [i] Price is in the middle range")
    print(f"{sep}")

    # --- Composite Signal ---
    print(f"\n  [SIGNAL] Composite Signal (Multi-Factor Model):")
    print(f"    Signal:     {signal_label}  (Score: {signal_score:+d}, Confidence: {confidence})")
    print(f"    Factors:")
    for f in signal_factors:
        print(f"      - {f}")
    print(f"{sep}\n")


def save_gold_report_md(
    spot_price: float,
    real_yield: Optional[float],
    real_yield_signal: Optional[Tuple[str, str]],
    miner_pb: Optional[float],
    safety_zone: str,
    safety_interp: str,
    miner_data: Optional[dict],
    gold_gdx_ratio: Optional[float],
    price_percentile: float,
    percentile_values: Dict[int, float],
    signal_label: str,
    signal_factors: List[str],
    signal_score: int,
    confidence: str,
    years_back: int = 10,
    output_dir: str = ".",
) -> str:
    """Save gold valuation report as a date-stamped markdown file."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines: List[str] = []

    lines.append(f"# Gold — Valuation Report")
    lines.append(f"**Date**: {today}\n")

    # Summary table
    lines.append("## Summary")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Gold Spot | ${spot_price:,.2f}/oz |")
    if real_yield is not None:
        lines.append(f"| Real Yield (TIPS) | {real_yield*100:+.2f}% |")
    if miner_pb is not None:
        lines.append(f"| Miner Avg P/B | {miner_pb:.2f} ({safety_zone}) |")
    if gold_gdx_ratio is not None:
        lines.append(f"| Gold/GDX Ratio | {gold_gdx_ratio:.1f} |")
    lines.append(f"| Price Percentile ({years_back}yr) | {price_percentile:.1f}% |")
    lines.append(f"| **Signal** | **{signal_label}** (Score: {signal_score:+d}) |")
    lines.append("")

    # Real Yield
    if real_yield is not None:
        lines.append("## Real Yield Analysis")
        ry_pct = real_yield * 100
        lines.append(f"- Real Yield: **{ry_pct:+.2f}%**")
        if real_yield_signal:
            lines.append(f"- Zone: **{real_yield_signal[0]}**")
            lines.append(f"- {real_yield_signal[1]}")
        lines.append("")

    # Safety Margin
    if miner_data is not None and miner_data.get("miners"):
        lines.append("## Safety Margin (Miner P/B)")
        lines.append("| Ticker | P/B | OpMargin | Book Value |")
        lines.append("|--------|-----|----------|------------|")
        for m in miner_data["miners"]:
            margin = f"{m['op_margin']*100:.1f}%" if m.get('op_margin') else "N/A"
            bv = f"${m['book_value']:.2f}" if m.get('book_value') else "N/A"
            lines.append(f"| {m['ticker']} | {m['pb']:.2f} | {margin} | {bv} |")
        lines.append(f"\n**Average P/B: {miner_pb:.2f}** — Zone: {safety_zone}")
        lines.append(f"{safety_interp}\n")

    # Percentile
    lines.append(f"## Price Percentile ({years_back}yr)")
    lines.append("| Percentile | Price |")
    lines.append("|-----------|-------|")
    for p in sorted(percentile_values.keys(), reverse=True):
        marker = " ◀" if abs(price_percentile - p) < 10 else ""
        lines.append(f"| {p}th | ${percentile_values[p]:,.2f}{marker} |")
    lines.append("")

    # Composite Signal
    lines.append("## Composite Signal")
    lines.append(f"**{signal_label}** — Score: {signal_score:+d}, Confidence: {confidence}\n")
    for f in signal_factors:
        lines.append(f"- {f}")
    lines.append("")

    filepath = os.path.join(output_dir, f"Gold_report_{today}.md")
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"  [REPORT] Saved: {filepath}")
    return filepath


def save_silver_report_md(
    spot_price: float,
    gold_price: float,
    gsr: float,
    gsr_signal: tuple,
    real_yield: Optional[float],
    miner_pb: Optional[float],
    safety_zone: str,
    safety_interp: str,
    miner_data: Optional[dict],
    inventory_data: Optional[dict],
    inventory_signal: Optional[Tuple[str, str]],
    price_percentile: float,
    percentile_values: Dict[int, float],
    signal_label: str,
    signal_factors: List[str],
    signal_score: int,
    confidence: str,
    years_back: int = 10,
    output_dir: str = ".",
) -> str:
    """Save silver valuation report as a date-stamped markdown file."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines: List[str] = []

    lines.append(f"# Silver — Valuation Report")
    lines.append(f"**Date**: {today}\n")

    # Summary table
    lines.append("## Summary")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Silver Spot | ${spot_price:.2f}/oz |")
    lines.append(f"| Gold Spot | ${gold_price:,.2f}/oz |")
    lines.append(f"| Gold/Silver Ratio | {gsr:.1f} |")
    if miner_pb is not None:
        lines.append(f"| Miner Avg P/B | {miner_pb:.2f} ({safety_zone}) |")
    lines.append(f"| Price Percentile ({years_back}yr) | {price_percentile:.1f}% |")
    lines.append(f"| **Signal** | **{signal_label}** (Score: {signal_score:+d}) |")
    lines.append("")

    # GSR
    gsr_zone, gsr_interp = gsr_signal
    lines.append("## Gold/Silver Ratio")
    lines.append(f"- Current GSR: **{gsr:.1f}** — Zone: **{gsr_zone}**")
    lines.append(f"- {gsr_interp}\n")

    # Safety Margin
    if miner_data is not None and miner_data.get("miners"):
        lines.append("## Safety Margin (Miner P/B)")
        lines.append("| Ticker | P/B | OpMargin |")
        lines.append("|--------|-----|----------|")
        for m in miner_data["miners"]:
            margin = f"{m['op_margin']*100:.1f}%" if m.get('op_margin') else "N/A"
            lines.append(f"| {m['ticker']} | {m['pb']:.2f} | {margin} |")
        lines.append(f"\n**Average P/B: {miner_pb:.2f}** — Zone: {safety_zone}")
        lines.append(f"{safety_interp}\n")

    # Inventory
    if inventory_data is not None and inventory_signal:
        lines.append("## COMEX / Inventory")
        lines.append(f"- Source: {inventory_data.get('source', 'N/A')}")
        inv_label = inventory_signal[0]
        inv_interp = inventory_signal[1]
        coverage_ratio = inventory_signal[2] if len(inventory_signal) > 2 else None
        coverage_zone = inventory_signal[3] if len(inventory_signal) > 3 else None
        lines.append(f"- Status: **{inv_label}**")
        lines.append(f"- {inv_interp}")
        if coverage_ratio is not None:
            lines.append(f"\n**Squeeze Risk — Coverage Ratio: {coverage_ratio:.1f}% ({coverage_zone})**")
            if coverage_zone == "CRITICAL":
                lines.append(f"\n> ⚠️ CRITICAL: Inventory covers <20% of open interest — extreme squeeze risk")
            elif coverage_zone == "TIGHT":
                lines.append(f"\n> ⚠️ TIGHT: Elevated squeeze risk — monitor closely")
        lines.append("")

    # Percentile
    lines.append(f"## Price Percentile ({years_back}yr)")
    lines.append("| Percentile | Price |")
    lines.append("|-----------|-------|")
    for p in sorted(percentile_values.keys(), reverse=True):
        marker = " ◀" if abs(price_percentile - p) < 10 else ""
        lines.append(f"| {p}th | ${percentile_values[p]:.2f}{marker} |")
    lines.append("")

    # Composite Signal
    lines.append("## Composite Signal")
    lines.append(f"**{signal_label}** — Score: {signal_score:+d}, Confidence: {confidence}\n")
    for f in signal_factors:
        lines.append(f"- {f}")
    lines.append("")

    filepath = os.path.join(output_dir, f"Silver_report_{today}.md")
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"  [REPORT] Saved: {filepath}")
    return filepath
