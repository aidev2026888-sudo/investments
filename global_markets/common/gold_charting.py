"""
Chart generation module for precious metals (Gold/Silver) analysis.

Generates a dual-axis chart: gold price history with AISC floor
and (optionally) US 10Y real yield overlay.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from typing import Dict, Optional

from .gold_metrics import AISC_DEFAULT, SILVER_AISC_DEFAULT


def generate_gold_chart(
    df: pd.DataFrame,
    spot_price: float,
    price_percentile: float,
    percentile_values: Dict[int, float],
    real_yield: Optional[float] = None,
    real_yield_df: Optional[pd.DataFrame] = None,
    aisc: float = AISC_DEFAULT,
    years_back: int = 10,
    output_dir: str = ".",
) -> str:
    """Generate and save a gold valuation chart.

    Left Y-axis:  Gold price with AISC floor and percentile bands.
    Right Y-axis:  US 10Y Real Yield (if data available).

    Args:
        df:                Gold price DataFrame with 'date', 'price' columns.
        spot_price:        Current gold spot price.
        price_percentile:  Percentile of current price.
        percentile_values: Dict of {percentile_level: price_value}.
        real_yield:        Current real yield decimal (for annotation).
        real_yield_df:     Real yield history DataFrame ('date', 'real_yield').
        aisc:              AISC floor price.
        years_back:        Years of history shown.
        output_dir:        Directory to save chart.

    Returns:
        Absolute path to the saved chart image.
    """
    plt.style.use("seaborn-v0_8-darkgrid")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "Helvetica", "DejaVu Sans"]

    has_yield_data = real_yield_df is not None and not real_yield_df.empty

    fig, ax1 = plt.subplots(figsize=(14, 7))

    # ========================================
    # Left Y-axis: Gold Price
    # ========================================

    # Price line
    ax1.plot(
        df["date"], df["price"],
        label="Gold Spot Price", color="goldenrod", linewidth=1.5, alpha=0.85,
    )

    # Moving averages
    ma_60 = df["price"].rolling(window=60).mean()
    ma_200 = df["price"].rolling(window=200).mean()
    ax1.plot(df["date"], ma_60, label="60-day MA", color="darkorange", linewidth=1, alpha=0.7)
    ax1.plot(df["date"], ma_200, label="200-day MA", color="saddlebrown", linewidth=1.5, alpha=0.8)

    # Current price line
    ax1.axhline(
        y=spot_price, color="black", linestyle="--", linewidth=1.5,
        label=f"Current: ${spot_price:,.0f} ({price_percentile:.0f}th pctl)",
    )

    # AISC floor
    ax1.axhline(
        y=aisc, color="#e74c3c", linestyle="-", linewidth=2.5, alpha=0.8,
        label=f"AISC Floor: ${aisc:,.0f}",
    )
    # Shade area below AISC
    ax1.axhspan(0, aisc, alpha=0.06, color="red", label=None)

    # Percentile reference lines
    pctl_colors = {80: "#e74c3c", 60: "#e67e22", 40: "#27ae60", 20: "#2980b9"}
    pctl_styles = {80: "-.", 60: ":", 40: ":", 20: "-."}
    for p, price_val in sorted(percentile_values.items(), reverse=True):
        ax1.axhline(
            y=price_val,
            color=pctl_colors.get(p, "gray"),
            linestyle=pctl_styles.get(p, ":"),
            alpha=0.6, linewidth=1,
            label=f"{p}th Pctl: ${price_val:,.0f}",
        )

    ax1.set_ylabel("Gold Price (USD/oz)", fontsize=11, color="goldenrod")
    ax1.tick_params(axis="y", labelcolor="goldenrod")

    # ========================================
    # Right Y-axis: Real Yield (optional)
    # ========================================
    if has_yield_data:
        ax2 = ax1.twinx()

        # Color the real yield line by sign: green when negative, red when positive
        ax2.plot(
            real_yield_df["date"], real_yield_df["real_yield"],
            color="steelblue", linewidth=1.5, alpha=0.7,
            label="US 10Y Real Yield (%)",
        )

        # Zero line for real yield
        ax2.axhline(y=0, color="steelblue", linestyle="--", linewidth=1, alpha=0.4)

        # Fill above/below zero
        ax2.fill_between(
            real_yield_df["date"], real_yield_df["real_yield"], 0,
            where=real_yield_df["real_yield"] >= 0,
            alpha=0.1, color="red", interpolate=True,
        )
        ax2.fill_between(
            real_yield_df["date"], real_yield_df["real_yield"], 0,
            where=real_yield_df["real_yield"] < 0,
            alpha=0.1, color="green", interpolate=True,
        )

        ax2.set_ylabel("US 10Y Real Yield (%)", fontsize=11, color="steelblue")
        ax2.tick_params(axis="y", labelcolor="steelblue")

        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2,
                   loc="upper left", fontsize=8, framealpha=0.9)
    else:
        ax1.legend(loc="upper left", fontsize=8, framealpha=0.9)

    # ========================================
    # Title and formatting
    # ========================================
    title = f"Gold (XAU/USD)  —  {years_back}-Year Valuation Analysis"
    if real_yield is not None:
        ry_pct = real_yield * 100
        title += f"\nUS 10Y Real Yield: {ry_pct:+.2f}%"
        if ry_pct < 0:
            title += " (Negative → Bullish Gold)"
        elif ry_pct > 2:
            title += " (High → Bearish Gold)"

    ax1.set_title(title, fontsize=13, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.6)

    # X-axis formatting
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()

    plt.tight_layout()

    # Save
    filepath = os.path.join(output_dir, "Gold_valuation.png")
    plt.savefig(filepath, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"  [CHART] Chart saved: {filepath}")
    return filepath


def generate_silver_chart(
    silver_df: pd.DataFrame,
    gold_df: pd.DataFrame,
    spot_price: float,
    price_percentile: float,
    percentile_values: Dict[int, float],
    gsr: float,
    aisc: float = SILVER_AISC_DEFAULT,
    years_back: int = 10,
    output_dir: str = ".",
) -> str:
    """Generate and save a silver valuation chart.

    Left Y-axis:  Silver price with AISC floor and percentile bands.
    Right Y-axis:  Gold/Silver Ratio overlay.

    Args:
        silver_df:         Silver price DataFrame with 'date', 'price'.
        gold_df:           Gold price DataFrame with 'date', 'price'.
        spot_price:        Current silver spot price.
        price_percentile:  Percentile of current silver price.
        percentile_values: Dict of {percentile_level: price_value}.
        gsr:               Current Gold/Silver Ratio.
        aisc:              Silver AISC floor price.
        years_back:        Years of history shown.
        output_dir:        Directory to save chart.

    Returns:
        Absolute path to the saved chart image.
    """
    plt.style.use("seaborn-v0_8-darkgrid")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "Helvetica", "DejaVu Sans"]

    fig, ax1 = plt.subplots(figsize=(14, 7))

    # ========================================
    # Left Y-axis: Silver Price
    # ========================================
    ax1.plot(
        silver_df["date"], silver_df["price"],
        label="Silver Spot Price", color="silver", linewidth=1.5, alpha=0.85,
    )

    # Moving averages
    ma_60 = silver_df["price"].rolling(window=60).mean()
    ma_200 = silver_df["price"].rolling(window=200).mean()
    ax1.plot(silver_df["date"], ma_60, label="60-day MA", color="gray", linewidth=1, alpha=0.7)
    ax1.plot(silver_df["date"], ma_200, label="200-day MA", color="dimgray", linewidth=1.5, alpha=0.8)

    # Current price
    ax1.axhline(
        y=spot_price, color="black", linestyle="--", linewidth=1.5,
        label=f"Current: ${spot_price:.2f} ({price_percentile:.0f}th pctl)",
    )

    # AISC floor
    ax1.axhline(
        y=aisc, color="#e74c3c", linestyle="-", linewidth=2.5, alpha=0.8,
        label=f"AISC Floor: ${aisc:.0f}",
    )
    ax1.axhspan(0, aisc, alpha=0.06, color="red", label=None)

    # Percentile reference lines
    pctl_colors = {80: "#e74c3c", 60: "#e67e22", 40: "#27ae60", 20: "#2980b9"}
    pctl_styles = {80: "-.", 60: ":", 40: ":", 20: "-."}
    for p, price_val in sorted(percentile_values.items(), reverse=True):
        ax1.axhline(
            y=price_val,
            color=pctl_colors.get(p, "gray"),
            linestyle=pctl_styles.get(p, ":"),
            alpha=0.6, linewidth=1,
            label=f"{p}th Pctl: ${price_val:.2f}",
        )

    ax1.set_ylabel("Silver Price (USD/oz)", fontsize=11, color="gray")
    ax1.tick_params(axis="y", labelcolor="gray")

    # ========================================
    # Right Y-axis: Gold/Silver Ratio
    # ========================================
    # Compute historical GSR from aligned dates
    merged = silver_df.merge(gold_df, on="date", suffixes=("_silver", "_gold"))
    if not merged.empty:
        merged["gsr"] = merged["price_gold"] / merged["price_silver"]

        ax2 = ax1.twinx()
        ax2.plot(
            merged["date"], merged["gsr"],
            color="goldenrod", linewidth=1.5, alpha=0.7,
            label=f"Gold/Silver Ratio (current: {gsr:.1f})",
        )

        # GSR reference lines
        ax2.axhline(y=80, color="green", linestyle=":", linewidth=1, alpha=0.5,
                     label="GSR 80 (silver cheap)")
        ax2.axhline(y=60, color="orange", linestyle=":", linewidth=1, alpha=0.5,
                     label="GSR 60 (fair value)")

        ax2.set_ylabel("Gold/Silver Ratio", fontsize=11, color="goldenrod")
        ax2.tick_params(axis="y", labelcolor="goldenrod")

        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2,
                   loc="upper left", fontsize=8, framealpha=0.9)
    else:
        ax1.legend(loc="upper left", fontsize=8, framealpha=0.9)

    # ========================================
    # Title
    # ========================================
    title = f"Silver (XAG/USD)  --  {years_back}-Year Valuation Analysis"
    title += f"\nGold/Silver Ratio: {gsr:.1f}"
    if gsr > 80:
        title += " (Silver Cheap vs Gold)"
    elif gsr < 50:
        title += " (Silver Expensive vs Gold)"

    ax1.set_title(title, fontsize=13, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.6)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()

    plt.tight_layout()

    filepath = os.path.join(output_dir, "Silver_valuation.png")
    plt.savefig(filepath, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"  [CHART] Chart saved: {filepath}")
    return filepath
