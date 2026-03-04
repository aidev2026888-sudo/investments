"""
Chart generation for the five-dimensional currency valuation framework.

Produces:
  1. Per-currency 3x2 dashboard (REER, RPL, CA, Real Rate, Credit Gap, Signal)
  2. Overview heatmap across all currencies x all dimensions
"""

import os

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from typing import Dict, Optional

from fx_config import FXFrameworkConfig

# ---- Style ----
plt.style.use("seaborn-v0_8-darkgrid")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Arial", "Helvetica", "DejaVu Sans"],
    "axes.titlesize": 12,
    "axes.labelsize": 10,
})

# Color palette (9 currencies)
COLORS = {
    "USD": "#2196F3",
    "JPY": "#E91E63",
    "CHF": "#4CAF50",
    "EUR": "#FF9800",
    "CNY": "#F44336",
    "AUD": "#9C27B0",
    "SGD": "#00BCD4",
    "CAD": "#795548",
    "GBP": "#3F51B5",
}
NEUTRAL_COLOR = "#607D8B"


def _get_color(code: str) -> str:
    return COLORS.get(code, NEUTRAL_COLOR)


# =====================================================================
# Per-currency 3x2 Dashboard
# =====================================================================

def generate_currency_dashboard(
    code: str,
    country_name: str,
    reer_df: Optional[pd.DataFrame],
    reer_z: float,
    reer_mean: float,
    reer_std: float,
    rpl_df: Optional[pd.DataFrame],
    ca_df: Optional[pd.DataFrame],
    real_rate_df: Optional[pd.DataFrame],
    real_rate_diff: Optional[float],
    credit_gap_df: Optional[pd.DataFrame],
    base_currency: str,
    output_dir: str,
) -> str:
    """Generate a 3x2 dashboard for one currency.

    Returns path to saved PNG.
    """
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle(
        f"{code} ({country_name}) -- Five-Dimensional Valuation Dashboard",
        fontsize=15, fontweight="bold", y=0.99,
    )
    color = _get_color(code)

    # ---- Panel 1: REER with z-score bands ----
    ax = axes[0, 0]
    if reer_df is not None and not reer_df.empty:
        ax.plot(reer_df["date"], reer_df["reer"], color=color, linewidth=1.5, label="REER")
        ax.axhline(reer_mean, color="gray", linestyle="--", linewidth=1, alpha=0.8, label=f"Mean: {reer_mean:.1f}")
        for n_sigma, alpha_fill in [(1, 0.12), (2, 0.06)]:
            ax.axhspan(
                reer_mean - n_sigma * reer_std,
                reer_mean + n_sigma * reer_std,
                alpha=alpha_fill, color="gray",
                label=f"+/-{n_sigma}s",
            )
        current = reer_df["reer"].iloc[-1]
        ax.scatter([reer_df["date"].iloc[-1]], [current], color="red", zorder=5, s=50)
        ax.annotate(
            f"z={reer_z:+.2f}\n{current:.1f}",
            xy=(reer_df["date"].iloc[-1], current),
            xytext=(10, 10), textcoords="offset points",
            fontsize=9, fontweight="bold", color="red",
            arrowprops=dict(arrowstyle="->", color="red", lw=1),
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.legend(loc="upper left", fontsize=7, framealpha=0.9)
    ax.set_title("Real Effective Exchange Rate (REER)")
    ax.set_ylabel("REER Index")

    # ---- Panel 2: Relative Price Level (BIS-derived PPP) ----
    ax = axes[0, 1]
    if rpl_df is not None and not rpl_df.empty:
        ax.plot(rpl_df["date"], rpl_df["rel_price_level"],
                color=color, linewidth=1.5, label="Rel. Price Level")
        rpl_mean = rpl_df["rel_price_level"].mean()
        ax.axhline(rpl_mean, color="gray", linestyle="--", linewidth=1,
                   alpha=0.8, label=f"Mean: {rpl_mean:.1f}")
        latest_rpl = rpl_df["rel_price_level"].iloc[-1]
        latest_dev = rpl_df["rpl_deviation_pct"].iloc[-1]
        ax.scatter([rpl_df["date"].iloc[-1]], [latest_rpl],
                   color="red", zorder=5, s=50)
        ax.annotate(
            f"{latest_rpl:.1f}\n({latest_dev:+.1f}%)",
            xy=(rpl_df["date"].iloc[-1], latest_rpl),
            xytext=(10, 10), textcoords="offset points",
            fontsize=9, fontweight="bold", color="red",
            arrowprops=dict(arrowstyle="->", color="red", lw=1),
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.legend(loc="upper left", fontsize=7)
    else:
        ax.text(0.5, 0.5, "RPL data unavailable", transform=ax.transAxes,
                ha="center", va="center", fontsize=12, color="gray")
    ax.set_title("Relative Price Level (REER/NEER)")
    ax.set_ylabel("Price Level Index\n(>mean = expensive)")

    # ---- Panel 3: Current Account (% GDP) ----
    ax = axes[1, 0]
    if ca_df is not None and not ca_df.empty:
        ca_colors = [("#4CAF50" if v >= 0 else "#F44336") for v in ca_df["ca_pct_gdp"]]
        ax.bar(ca_df["year"], ca_df["ca_pct_gdp"], color=ca_colors, alpha=0.75, width=0.8)
        ax.axhline(0, color="black", linewidth=0.8)
        latest_ca = ca_df["ca_pct_gdp"].iloc[-1]
        latest_yr = ca_df["year"].iloc[-1]
        ax.annotate(
            f"{latest_yr}: {latest_ca:+.1f}%",
            xy=(latest_yr, latest_ca),
            xytext=(0, 15 if latest_ca >= 0 else -20),
            textcoords="offset points",
            fontsize=9, fontweight="bold",
            ha="center",
        )
    else:
        ax.text(0.5, 0.5, "Current Account data unavailable", transform=ax.transAxes,
                ha="center", va="center", fontsize=12, color="gray")
    ax.set_title("Current Account Balance (% GDP)")
    ax.set_ylabel("% of GDP")

    # ---- Panel 4: Real Interest Rate ----
    ax = axes[1, 1]
    if real_rate_df is not None and not real_rate_df.empty:
        ax.plot(real_rate_df["date"], real_rate_df["real_rate"],
                color=color, linewidth=1.5, label=f"{code} Real Rate")
        ax.axhline(0, color="black", linewidth=0.8, linestyle="-")
        latest_real = real_rate_df["real_rate"].iloc[-1]
        diff_text = f"Real Rate: {latest_real:.2f}%"
        if real_rate_diff is not None:
            diff_text += f"\nvs {base_currency}: {real_rate_diff:+.2f}pp"
        ax.annotate(
            diff_text,
            xy=(real_rate_df["date"].iloc[-1], latest_real),
            xytext=(-80, 20), textcoords="offset points",
            fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
            arrowprops=dict(arrowstyle="->", color="gray", lw=1),
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.legend(loc="upper left", fontsize=8)
    else:
        ax.text(0.5, 0.5, "Real rate data unavailable", transform=ax.transAxes,
                ha="center", va="center", fontsize=12, color="gray")
    ax.set_title(f"Real Interest Rate (Nominal - CPI YoY)")
    ax.set_ylabel("Real Rate (%)")

    # ---- Panel 5: Credit-to-GDP Gap ----
    ax = axes[2, 0]
    if credit_gap_df is not None and not credit_gap_df.empty:
        # Plot the gap as a filled area chart
        gap_vals = credit_gap_df["credit_gap"]
        dates = credit_gap_df["date"]
        ax.fill_between(dates, gap_vals, 0,
                        where=(gap_vals >= 0), color="#F44336", alpha=0.4, label="Above Trend")
        ax.fill_between(dates, gap_vals, 0,
                        where=(gap_vals < 0), color="#4CAF50", alpha=0.4, label="Below Trend")
        ax.plot(dates, gap_vals, color=color, linewidth=1.5)
        ax.axhline(0, color="black", linewidth=1)
        # Danger zones
        ax.axhline(10, color="#D32F2F", linestyle="--", linewidth=0.8, alpha=0.7, label="Danger +10pp")
        ax.axhline(-10, color="#388E3C", linestyle="--", linewidth=0.8, alpha=0.7)
        # Latest value
        latest_gap = gap_vals.iloc[-1]
        ax.scatter([dates.iloc[-1]], [latest_gap], color="red", zorder=5, s=50)
        ax.annotate(
            f"{latest_gap:+.1f}pp",
            xy=(dates.iloc[-1], latest_gap),
            xytext=(10, 10), textcoords="offset points",
            fontsize=10, fontweight="bold", color="red",
            arrowprops=dict(arrowstyle="->", color="red", lw=1),
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.legend(loc="upper left", fontsize=7)
    else:
        ax.text(0.5, 0.5, "Credit gap data unavailable", transform=ax.transAxes,
                ha="center", va="center", fontsize=12, color="gray")
    ax.set_title("Credit-to-GDP Gap (BIS)")
    ax.set_ylabel("Deviation from Trend (pp)")

    # ---- Panel 6: Credit-to-GDP Ratio vs Trend ----
    ax = axes[2, 1]
    if credit_gap_df is not None and not credit_gap_df.empty and "credit_ratio" in credit_gap_df.columns:
        dates = credit_gap_df["date"]
        ax.plot(dates, credit_gap_df["credit_ratio"],
                color=color, linewidth=1.5, label="Actual Ratio")
        if "credit_trend" in credit_gap_df.columns:
            ax.plot(dates, credit_gap_df["credit_trend"],
                    color="gray", linestyle="--", linewidth=1.5, label="HP Trend")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.legend(loc="upper left", fontsize=8)
        # Latest values
        latest_ratio = credit_gap_df["credit_ratio"].iloc[-1]
        ax.annotate(
            f"{latest_ratio:.1f}%",
            xy=(dates.iloc[-1], latest_ratio),
            xytext=(-60, 10), textcoords="offset points",
            fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
            arrowprops=dict(arrowstyle="->", color="gray", lw=1),
        )
    else:
        ax.text(0.5, 0.5, "Credit ratio data unavailable", transform=ax.transAxes,
                ha="center", va="center", fontsize=12, color="gray")
    ax.set_title("Total Credit-to-GDP Ratio vs Trend")
    ax.set_ylabel("Credit / GDP (%)")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    filepath = os.path.join(output_dir, f"{code}_valuation_dashboard.png")
    plt.savefig(filepath, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"  [CHART] Saved: {filepath}")
    return filepath


# =====================================================================
# Overview Heatmap -- all currencies x all dimensions
# =====================================================================

def generate_overview_heatmap(
    summary_data: Dict[str, dict],
    output_dir: str,
) -> str:
    """Generate a heatmap showing all currencies across all 5 dimensions.

    Returns path to saved PNG.
    """
    currencies = list(summary_data.keys())
    dimensions = ["REER Z", "CA Score", "Rate Diff", "Credit Gap", "Composite"]
    dim_keys = ["reer_z", "ca_score", "real_rate_diff", "credit_gap_val", "composite_score"]

    # Build matrix
    matrix = np.zeros((len(currencies), len(dimensions)))
    annotations = [['' for _ in dimensions] for _ in currencies]

    for i, ccy in enumerate(currencies):
        d = summary_data[ccy]
        for j, key in enumerate(dim_keys):
            val = d.get(key, 0)
            if val is None:
                val = 0
            matrix[i, j] = val
            if isinstance(val, float):
                annotations[i][j] = f"{val:+.1f}"
            else:
                annotations[i][j] = f"{val:+d}"

    fig, ax = plt.subplots(figsize=(12, max(4, len(currencies) * 1.0)))

    # Custom colormap: red (overvalued) -> white (neutral) -> green (undervalued)
    from matplotlib.colors import LinearSegmentedColormap
    colors_cmap = ["#D32F2F", "#FFCDD2", "#FFFFFF", "#C8E6C9", "#388E3C"]
    cmap = LinearSegmentedColormap.from_list("valuation", colors_cmap, N=256)

    vmax = max(abs(matrix.min()), abs(matrix.max()), 3)
    im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=-vmax, vmax=vmax)

    # Annotations
    for i in range(len(currencies)):
        for j in range(len(dimensions)):
            ax.text(j, i, annotations[i][j],
                    ha="center", va="center", fontsize=10, fontweight="bold",
                    color="black" if abs(matrix[i, j]) < vmax * 0.6 else "white")

    ax.set_xticks(range(len(dimensions)))
    ax.set_xticklabels(dimensions, fontsize=11)
    ax.set_yticks(range(len(currencies)))
    ax.set_yticklabels(currencies, fontsize=12, fontweight="bold")
    ax.set_title("Currency Valuation Heatmap - Five Dimensions", fontsize=14, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("<- Bullish (Undervalued)    Bearish (Overvalued) ->", fontsize=9)

    plt.tight_layout()
    filepath = os.path.join(output_dir, "fx_valuation_heatmap.png")
    plt.savefig(filepath, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"  [CHART] Saved: {filepath}")
    return filepath
