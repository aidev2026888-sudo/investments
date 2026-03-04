"""
Metrics computation module for precious metals (Gold/Silver) analysis.

Provides functions for real yield signal classification, AISC margin
of safety, and gold price percentile ranking.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Optional, Tuple


# ==========================================
# Constants (reference only -- NOT used in signals)
# ==========================================

# Historical AISC references (for context, NOT for signal logic)
# These are approximate and change over time -- that's why we use
# miner P/B ratios as dynamic proxies instead.
# Gold AISC: ~$1,300-$1,400/oz as of 2024-2025
# Silver AISC: ~$17-$22/oz as of 2024-2025

# Legacy constants kept for backward compatibility only
AISC_DEFAULT = 1350.0
SILVER_AISC_DEFAULT = 20.0


# ==========================================
# Real Yield Analysis
# ==========================================

def compute_real_yield_signal(
    real_yield: Optional[float],
) -> Optional[Tuple[str, str]]:
    """Classify gold attractiveness based on the US 10Y real yield.

    Gold has no yield; its opportunity cost IS the real yield.
    When real yields are negative, cash/bonds lose purchasing power,
    making gold the superior store of value.

    Args:
        real_yield: US 10Y TIPS yield as decimal (e.g., 0.02 = 2%).

    Returns:
        Tuple of (zone_label, interpretation), or None if data unavailable.
        Zones:
          - "EXPENSIVE"  (real yield > 2%)  -> high opportunity cost for gold
          - "HEADWIND"   (1% - 2%)          -> moderate headwind
          - "NEUTRAL"    (0% - 1%)          -> neither tailwind nor headwind
          - "TAILWIND"   (-1% - 0%)         -> gold becomes attractive
          - "STRONG BUY" (< -1%)            -> gold is the best asset
    """
    if real_yield is None:
        return None

    ry_pct = real_yield * 100  # convert to percentage for display

    if ry_pct > 2.0:
        return ("EXPENSIVE",
                f"Real yield {ry_pct:+.2f}% -- high opportunity cost; gold under pressure")
    elif ry_pct > 1.0:
        return ("HEADWIND",
                f"Real yield {ry_pct:+.2f}% -- moderate headwind for gold")
    elif ry_pct > 0.0:
        return ("NEUTRAL",
                f"Real yield {ry_pct:+.2f}% -- mildly positive real rates; gold range-bound")
    elif ry_pct > -1.0:
        return ("TAILWIND",
                f"Real yield {ry_pct:+.2f}% -- negative real rates; gold attractive")
    else:
        return ("STRONG BUY",
                f"Real yield {ry_pct:+.2f}% -- deeply negative real rates; gold is king")


# ==========================================
# Dynamic Safety Margin (Miner P/B Proxy)
# ==========================================

def compute_safety_margin(
    miner_data: Optional[dict],
    metal_name: str = "Gold",
) -> Tuple[Optional[float], str, str]:
    """Compute safety margin using miner P/B ratio as dynamic AISC proxy.

    Core insight (Howard Marks: "everything is cyclical"):
    - Miner P/B < 1.0 = market says mines worth less than book value
      -> gold is AT or BELOW AISC -> MAXIMUM safety margin
    - Miner P/B > 4.0 = extreme profitability
      -> gold is FAR above AISC -> NO safety margin

    This replaces the static AISC comparison with a dynamic,
    market-driven signal that automatically adjusts as costs change.

    Args:
        miner_data: Dict from fetch_gold_miner_fundamentals() or
                     fetch_silver_miner_fundamentals().
        metal_name: "Gold" or "Silver" for display.

    Returns:
        Tuple of (avg_pb, zone_label, interpretation).
        avg_pb may be None if no data.
    """
    if miner_data is None:
        return (None, "NO DATA",
                f"Miner data unavailable -- cannot assess safety margin")

    avg_pb = miner_data["avg_pb"]
    avg_margin = miner_data.get("avg_op_margin")
    margin_str = f"{avg_margin*100:.1f}%" if avg_margin else "N/A"

    if avg_pb < 1.0:
        zone = "MAXIMUM SAFETY"
        interp = (f"{metal_name} miners P/B={avg_pb:.2f} (below book value!) "
                  f"OpMargin={margin_str} -- market says mines are worth less "
                  f"than their assets; price near/below AISC; historic buy signal")
    elif avg_pb < 1.5:
        zone = "STRONG SAFETY"
        interp = (f"{metal_name} miners P/B={avg_pb:.2f}, OpMargin={margin_str} "
                  f"-- miners valued near assets; price likely near AISC; strong buy zone")
    elif avg_pb < 2.5:
        zone = "MODERATE"
        interp = (f"{metal_name} miners P/B={avg_pb:.2f}, OpMargin={margin_str} "
                  f"-- normal profitability; price moderately above AISC")
    elif avg_pb < 4.0:
        zone = "ELEVATED"
        interp = (f"{metal_name} miners P/B={avg_pb:.2f}, OpMargin={margin_str} "
                  f"-- high profitability; price well above AISC; limited safety margin")
    else:
        zone = "NO SAFETY MARGIN"
        interp = (f"{metal_name} miners P/B={avg_pb:.2f}, OpMargin={margin_str} "
                  f"-- extreme profitability; price far above AISC; no safety margin")

    return avg_pb, zone, interp


# ==========================================
# Price Percentile
# ==========================================

def compute_gold_percentile(
    price_series: pd.Series,
    current_price: float,
) -> float:
    """Compute the percentile rank of current gold price within its history.

    Args:
        price_series: Historical gold prices (cleaned, no NaN).
        current_price: Current gold spot price.

    Returns:
        Percentile (0–100) indicating where current price falls.
    """
    clean = price_series.dropna()
    return float(stats.percentileofscore(clean, current_price))


def compute_gold_percentile_values(
    price_series: pd.Series,
    levels: list = None,
) -> Dict[int, float]:
    """Compute gold price values at reference percentile levels.

    Args:
        price_series: Historical gold prices.
        levels:       Percentile levels (default: [80, 60, 40, 20]).

    Returns:
        Dict mapping each percentile level to its price value.
    """
    if levels is None:
        levels = [80, 60, 40, 20]

    clean = price_series.dropna()
    return {p: float(np.percentile(clean, p)) for p in levels}


# ==========================================
# Gold/Silver Ratio (GSR)
# ==========================================

def compute_gsr_signal(
    gsr: float,
) -> Tuple[str, str]:
    """Classify silver valuation based on the Gold/Silver Ratio.

    The GSR is the single most important silver-specific indicator.
    Historical average ~60-70. When GSR is high, silver is cheap vs gold.

    Args:
        gsr: Gold/Silver Ratio (gold_price / silver_price).

    Returns:
        Tuple of (zone_label, interpretation).
        Zones:
          - "EXTREME DISCOUNT" (GSR > 90)  -> silver very cheap, strong buy
          - "CHEAP"            (80-90)      -> silver undervalued vs gold
          - "NORMAL"           (60-80)      -> fair value range
          - "EXPENSIVE"        (50-60)      -> silver rich vs gold
          - "EXTREME PREMIUM"  (< 50)       -> silver overvalued, caution
    """
    if gsr > 90:
        return ("EXTREME DISCOUNT",
                f"GSR {gsr:.1f} -- silver extremely cheap vs gold; "
                f"historically rare, strong buy signal")
    elif gsr > 80:
        return ("CHEAP",
                f"GSR {gsr:.1f} -- silver undervalued relative to gold")
    elif gsr > 60:
        return ("NORMAL",
                f"GSR {gsr:.1f} -- silver at fair value relative to gold")
    elif gsr > 50:
        return ("EXPENSIVE",
                f"GSR {gsr:.1f} -- silver relatively expensive vs gold")
    else:
        return ("EXTREME PREMIUM",
                f"GSR {gsr:.1f} -- silver extremely expensive vs gold; caution")


# ==========================================
# Inventory Signal
# ==========================================

def compute_inventory_signal(
    inventory_data: Optional[dict],
    oi_data: Optional[dict] = None,
) -> Optional[Tuple[str, str]]:
    """Provide an inventory assessment with optional COMEX coverage ratio.

    Uses SLV ETF total assets as a proxy for visible silver holdings.
    When open-interest data is also provided, computes a coverage ratio
    (est_oz / oi_oz) to flag squeeze risk.

    Coverage ratio zones:
      < 20%  → CRITICAL   (extreme squeeze risk — Jan 2026 was ~14%)
      20-40% → TIGHT      (elevated squeeze risk)
      40-70% → ADEQUATE   (normal range)
      > 70%  → COMFORTABLE (low squeeze risk)

    Args:
        inventory_data: Dict from fetch_comex_silver_inventory().
        oi_data:        Dict from fetch_comex_open_interest().

    Returns:
        Tuple of (label, interpretation), or None if no data.
    """
    if inventory_data is None:
        return None

    value = inventory_data.get("value")
    source = inventory_data.get("source", "Unknown")

    if value is None:
        return None

    # --- Base inventory description ---
    base_parts = []
    if "SLV" in source:
        value_b = value / 1e9
        base_parts.append(f"SLV holds ${value_b:.1f}B in silver assets")

    # --- Coverage ratio (if both inventory oz and OI oz available) ---
    est_oz = inventory_data.get("est_oz")
    coverage_ratio = None
    coverage_zone = None

    if est_oz and oi_data:
        oi_oz = oi_data.get("oi_oz")
        if oi_oz and oi_oz > 0:
            coverage_ratio = (est_oz / oi_oz) * 100.0  # as percentage

            if coverage_ratio < 20:
                coverage_zone = "CRITICAL"
            elif coverage_ratio < 40:
                coverage_zone = "TIGHT"
            elif coverage_ratio < 70:
                coverage_zone = "ADEQUATE"
            else:
                coverage_zone = "COMFORTABLE"

            base_parts.append(
                f"Coverage ratio: {coverage_ratio:.1f}% ({coverage_zone}) "
                f"— {est_oz:,.0f} oz inventory vs "
                f"{oi_oz:,.0f} oz open interest"
            )

    # --- Build final label and interpretation ---
    if coverage_zone:
        label = f"COVERAGE {coverage_zone}"
    elif "SLV" in source:
        label = "SLV PROXY"
    else:
        label = "DATA AVAILABLE"

    if base_parts:
        interp = " | ".join(base_parts)
    else:
        interp = f"Inventory from {source}: {value}"

    return (label, interp, coverage_ratio, coverage_zone)
