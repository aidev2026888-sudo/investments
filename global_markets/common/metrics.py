"""
Metrics computation module for global market index analysis.

Provides functions for PE percentile, simplified CAPE, ERP,
and Buffett Indicator calculations.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple

from .config import PERCENTILE_LEVELS


def compute_pe_percentile(pe_series: pd.Series, current_pe: float) -> float:
    """Compute the percentile rank of current PE within a historical PE series.

    Args:
        pe_series:  Historical PE values (cleaned, no NaN).
        current_pe: The current PE value to rank.

    Returns:
        Percentile (0–100) indicating where current PE falls in the distribution.
    """
    clean = pe_series.dropna()
    return float(stats.percentileofscore(clean, current_pe))


def compute_percentile_values(
    pe_series: pd.Series,
    levels: List[int] = None,
) -> Dict[int, float]:
    """Compute the PE values at each reference percentile level.

    Args:
        pe_series: Historical PE values.
        levels:    List of percentile levels (default: [80, 60, 40, 20]).

    Returns:
        Dict mapping each percentile level to its PE value.
        Example: {80: 22.5, 60: 18.3, 40: 15.1, 20: 12.0}
    """
    if levels is None:
        levels = PERCENTILE_LEVELS

    clean = pe_series.dropna()
    return {p: float(np.percentile(clean, p)) for p in levels}


def compute_cape_deviation(current_pe: float, cape_value: Optional[float]) -> Optional[float]:
    """Compute the percentage deviation of current PE from its CAPE (rolling avg).

    Args:
        current_pe: Current PE ratio.
        cape_value: Simplified CAPE (rolling average PE).

    Returns:
        Deviation percentage (e.g., +15.3 means 15.3% above CAPE), or None.
    """
    if cape_value is None or cape_value == 0:
        return None
    return (current_pe - cape_value) / cape_value * 100.0


def compute_erp(
    current_pe: float,
    bond_yield_decimal: Optional[float],
) -> Optional[Tuple[float, float]]:
    """Compute the Equity Risk Premium (ERP).

    ERP = Earnings Yield (1/PE) − Risk-Free Rate (10-year bond yield)

    Args:
        current_pe:          Current PE ratio.
        bond_yield_decimal:  10-year government bond yield as decimal (e.g., 0.0425).

    Returns:
        Tuple of (earnings_yield, erp) as decimals, or None if bond yield unavailable.
    """
    if bond_yield_decimal is None:
        return None

    earnings_yield = 1.0 / current_pe
    erp = earnings_yield - bond_yield_decimal
    return earnings_yield, erp


def compute_buffett_indicator(
    market_cap: Optional[float],
    gdp: Optional[float],
) -> Optional[float]:
    """Compute the Buffett Indicator (Market Cap / GDP).

    Args:
        market_cap: Total market capitalization.
        gdp:        Nominal GDP in the same currency.

    Returns:
        Ratio as a percentage (e.g., 150.0 means market cap is 150% of GDP),
        or None if data is unavailable.
    """
    if market_cap is None or gdp is None or gdp == 0:
        return None
    return (market_cap / gdp) * 100.0


def compute_vix_signal(vix_data: Optional[dict]) -> Optional[Tuple[str, str, bool]]:
    """Interpret VIX data into a fear zone and description.

    Zones (based on empirical 35yr data):
      EXTREME FEAR (>40):  Avg 12mo return +52%, 100% win rate
      HIGH FEAR    (30-40): Avg 12mo return +29-45%, 83-96% win
      ELEVATED     (25-30): Avg 12mo return +23%, 85% win
      NORMAL       (15-25): Baseline market conditions
      COMPLACENT   (<15):   Low vol, potential complacency

    Returns:
        Tuple of (zone_label, description, is_spike_retreat) or None.
        This is informational only -- NOT included in composite signal.
    """
    if vix_data is None:
        return None

    vix = vix_data["current"]
    retreat = vix_data.get("is_spike_retreat", False)

    if vix >= 40:
        zone = "EXTREME FEAR"
        desc = (f"VIX {vix:.1f} -- historically avg +52% 12mo return, "
                "100% win rate. Strong contrarian buy zone.")
    elif vix >= 30:
        zone = "HIGH FEAR"
        desc = (f"VIX {vix:.1f} -- historically avg +29% 12mo return, "
                "83% win rate. Contrarian buy opportunity.")
    elif vix >= 25:
        zone = "ELEVATED"
        desc = (f"VIX {vix:.1f} -- above-average fear. "
                "Historically avg +23% 12mo return.")
    elif vix >= 15:
        zone = "NORMAL"
        desc = f"VIX {vix:.1f} -- within normal range."
    else:
        zone = "COMPLACENT"
        desc = (f"VIX {vix:.1f} -- low volatility, potential complacency. "
                "Historically associated with lower forward returns.")

    if retreat:
        desc += " ** VIX spike-retreat detected (peak passed, fear subsiding)."

    return zone, desc, retreat
