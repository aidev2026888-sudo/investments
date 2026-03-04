"""
Chart generation module for global market index analysis.

Generates PE valuation trend charts with percentile reference lines,
CAPE overlay, and ERP annotation.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from typing import Dict, Optional, Tuple

from .config import IndexConfig, SHORT_MA, LONG_MA


def generate_chart(
    config: IndexConfig,
    df: pd.DataFrame,
    current_pe: float,
    percentile: float,
    pe_percentile_values: Dict[int, float],
    erp_info: Optional[Tuple[float, float, float]] = None,
    output_dir: str = ".",
) -> str:
    """Generate and save a PE valuation trend chart.

    Args:
        config:               Index configuration.
        df:                   DataFrame with 'date', 'pe', 'pe_cape' columns.
        current_pe:           Current PE value.
        percentile:           Current PE percentile.
        pe_percentile_values: Dict of {percentile_level: pe_value}.
        erp_info:             Optional tuple of (earnings_yield, erp, bond_yield).
        output_dir:           Directory to save the chart.

    Returns:
        Absolute path to the saved chart image.
    """
    # Use a clean style
    plt.style.use("seaborn-v0_8-darkgrid")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "Helvetica", "DejaVu Sans"]

    fig, ax = plt.subplots(figsize=(14, 7))

    # --- PE line + moving averages ---
    ax.plot(
        df["date"], df["pe"],
        label=f"Trailing PE (proxy)", color="dodgerblue", alpha=0.5, linewidth=1,
    )

    # Short & long moving averages
    ma_short = df["pe"].rolling(window=SHORT_MA).mean()
    ma_long = df["pe"].rolling(window=LONG_MA).mean()
    ax.plot(df["date"], ma_short, label=f"{SHORT_MA}-day MA", color="orange", linewidth=1.5)
    ax.plot(df["date"], ma_long, label=f"{LONG_MA}-day MA", color="darkred", linewidth=2)

    # --- CAPE line ---
    if "pe_cape" in df.columns:
        cape_val = df["pe_cape"].iloc[-1]
        ax.plot(
            df["date"], df["pe_cape"],
            label=f"{config.cape_rolling_years}yr Rolling Avg PE (CAPE): {cape_val:.2f}",
            color="purple", linewidth=2.5, linestyle="-", alpha=0.85,
        )

    # --- Current PE horizontal line ---
    ax.axhline(
        y=current_pe, color="black", linestyle="--", linewidth=1.5,
        label=f"Current PE: {current_pe:.2f} ({percentile:.1f}th pctl)",
    )

    # --- Percentile reference lines ---
    pctl_colors = {80: "#e74c3c", 60: "#e67e22", 40: "#27ae60", 20: "#2980b9"}
    pctl_styles = {80: "-.", 60: ":", 40: ":", 20: "-."}
    for p, pe_val in sorted(pe_percentile_values.items(), reverse=True):
        ax.axhline(
            y=pe_val,
            color=pctl_colors.get(p, "gray"),
            linestyle=pctl_styles.get(p, ":"),
            alpha=0.7, linewidth=1.2,
            label=f"{p}th Percentile PE: {pe_val:.2f}",
        )

    # --- Title ---
    title = f"{config.name}  —  {config.years_back}-Year PE Valuation Trend"
    if erp_info:
        ey, erp, by = erp_info
        title += (
            f"\nERP = {erp*100:.2f}%  "
            f"(Earnings Yield {ey*100:.2f}% − Bond Yield {by*100:.2f}%)"
        )

    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylabel("Price/Earnings Ratio")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.grid(True, linestyle=":", alpha=0.6)

    # X-axis formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()

    plt.tight_layout()

    # Save
    filepath = os.path.join(output_dir, config.chart_filename)
    plt.savefig(filepath, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"  [CHART] Chart saved: {filepath}")
    return filepath
