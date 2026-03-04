"""
Metrics computation for the five-dimensional currency valuation framework.

Computes:
  - REER z-score (deviation from long-term mean in sigma)
  - Relative Price Level deviation (BIS-derived PPP)
  - Current Account assessment
  - Real interest rate differential vs base currency
  - Credit-to-GDP gap assessment (financial stability)
  - Composite valuation signal
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from fx_config import FXFrameworkConfig


# =====================================================================
# REER Analysis
# =====================================================================

def compute_reer_zscore(reer_df: pd.DataFrame) -> Tuple[float, float, float]:
    """Compute REER z-score from its full history.

    Returns:
        (current_reer, z_score, long_term_mean)
    """
    current = reer_df["reer"].iloc[-1]
    mean = reer_df["reer"].mean()
    std = reer_df["reer"].std()
    if std == 0:
        return current, 0.0, mean
    z = (current - mean) / std
    return current, z, mean


def compute_reer_percentile(reer_df: pd.DataFrame) -> float:
    """Compute current REER percentile within its historical distribution."""
    from scipy.stats import percentileofscore
    current = reer_df["reer"].iloc[-1]
    return percentileofscore(reer_df["reer"].dropna(), current, kind="rank")


# =====================================================================
# PPP Analysis
# =====================================================================

def compute_ppp_deviation(ppp_value: float, market_rate: float = 1.0) -> float:
    """Compute PPP deviation %.

    Positive = overvalued (more expensive than PPP fair value)
    Negative = undervalued
    """
    if ppp_value == 0:
        return 0.0
    return (market_rate / ppp_value - 1.0) * 100.0


# =====================================================================
# Current Account Assessment
# =====================================================================

def assess_current_account(ca_pct: float) -> Tuple[str, int]:
    """Assess current account balance as % GDP.

    Returns:
        (label, score) where score ranges from -2 to +2.
    """
    if ca_pct >= 6.0:
        return "Very Strong Surplus", 2
    elif ca_pct >= 2.0:
        return "Surplus", 1
    elif ca_pct >= -2.0:
        return "Balanced", 0
    elif ca_pct >= -4.0:
        return "Deficit", -1
    else:
        return "Large Deficit", -2


# =====================================================================
# Credit-to-GDP Gap Assessment
# =====================================================================

def assess_credit_gap(gap_pp: float) -> Tuple[str, int]:
    """Assess credit-to-GDP gap (pp deviation from trend).

    The credit-to-GDP gap measures how far total private credit
    (as % of GDP) deviates from its HP-filtered long-term trend.
    Adopted by Basel III as the guide for the countercyclical capital buffer.

    Interpretation:
      > +10pp  : Credit boom, systemic risk building -> negative for currency
      +2 to +10: Above trend, watch closely
      -2 to +2 : Near trend, healthy
      -10 to -2: Below trend, deleveraging (healing)
      < -10pp  : Deep deleveraging, room for expansion (stable base)

    For FX valuation:
      - Large positive gap = financial fragility = currency risk -> NEGATIVE
      - Large negative gap = clean balance sheet = currency stability -> POSITIVE

    Returns:
        (label, score) where score ranges from -2 to +2.
    """
    if gap_pp >= 10.0:
        return "Credit Boom (Danger)", -2
    elif gap_pp >= 2.0:
        return "Above Trend (Caution)", -1
    elif gap_pp >= -2.0:
        return "Near Trend (Healthy)", 0
    elif gap_pp >= -10.0:
        return "Below Trend (Healing)", 1
    else:
        return "Deep Deleveraging (Stable)", 2


# =====================================================================
# Real Interest Rate Differential
# =====================================================================

def compute_real_rate_differential(
    real_rates: Dict[str, pd.DataFrame],
    base_currency: str,
) -> Dict[str, float]:
    """Compute real rate differential vs base currency for each currency.

    Differential = real_rate(currency) - real_rate(base)
    Positive = currency has higher real rate -> attracting capital
    Negative = lower real rate -> capital outflow pressure

    Returns:
        Dict mapping currency code -> differential (percentage points).
    """
    if base_currency not in real_rates:
        print(f"  [WARN] No real rate data for base currency {base_currency}")
        return {}

    base_df = real_rates[base_currency]
    base_latest = base_df["real_rate"].iloc[-1]

    result = {}
    for code, df in real_rates.items():
        latest = df["real_rate"].iloc[-1]
        result[code] = latest - base_latest
    return result


# =====================================================================
# Composite Valuation Signal (5 Dimensions)
# =====================================================================

def compute_composite_signal(
    reer_z: float,
    ca_score: int,
    real_rate_diff: Optional[float],
    ppp_latest: Optional[float],
    credit_gap: Optional[float] = None,
) -> Tuple[str, List[str], int]:
    """Compute composite currency valuation signal.

    Five-dimensional scoring:

    1. REER Z-Score (structural valuation - the spring):
        > +2s  -> -3 | > +1s  -> -2 | > +0.5s -> -1
        < -2s  -> +3 | < -1s  -> +2 | < -0.5s -> +1

    2. Current Account (fundamental backing): -2 to +2

    3. Real Rate Differential (catalyst / trigger):
        > +2pp -> +2 | > +1pp -> +1 | < -1pp -> -1 | < -2pp -> -2

    4. PPP / Relative Price Level (long-term anchor):
        Informational factor (logged but not scored separately from REER)

    5. Credit-to-GDP Gap (financial stability):
        > +10pp -> -2 | > +2pp -> -1 | near 0 -> 0
        < -2pp  -> +1 | < -10pp-> +2

    Returns:
        (signal_label, factor_details, total_score)
    """
    score = 0
    factors: List[str] = []

    # Factor 1: REER Z-Score (structural valuation -- the spring)
    if reer_z >= 2.0:
        score -= 3
        factors.append(f"REER z={reer_z:+.2f} (Extremely Overvalued)")
    elif reer_z >= 1.0:
        score -= 2
        factors.append(f"REER z={reer_z:+.2f} (Overvalued)")
    elif reer_z >= 0.5:
        score -= 1
        factors.append(f"REER z={reer_z:+.2f} (Mildly Overvalued)")
    elif reer_z <= -2.0:
        score += 3
        factors.append(f"REER z={reer_z:+.2f} (Extremely Undervalued)")
    elif reer_z <= -1.0:
        score += 2
        factors.append(f"REER z={reer_z:+.2f} (Undervalued)")
    elif reer_z <= -0.5:
        score += 1
        factors.append(f"REER z={reer_z:+.2f} (Mildly Undervalued)")
    else:
        factors.append(f"REER z={reer_z:+.2f} (Fair Value)")

    # Factor 2: Current Account (fundamental backing)
    score += ca_score
    ca_labels = {2: "Very Strong Surplus", 1: "Surplus", 0: "Balanced",
                 -1: "Deficit", -2: "Large Deficit"}
    factors.append(f"Current Account: {ca_labels.get(ca_score, 'N/A')} (score {ca_score:+d})")

    # Factor 3: Real Rate Differential (catalyst / trigger)
    if real_rate_diff is not None:
        if real_rate_diff >= 2.0:
            score += 2
            factors.append(f"Real Rate Diff: {real_rate_diff:+.2f}pp (Strong Attraction)")
        elif real_rate_diff >= 1.0:
            score += 1
            factors.append(f"Real Rate Diff: {real_rate_diff:+.2f}pp (Moderate Attraction)")
        elif real_rate_diff <= -2.0:
            score -= 2
            factors.append(f"Real Rate Diff: {real_rate_diff:+.2f}pp (Strong Outflow)")
        elif real_rate_diff <= -1.0:
            score -= 1
            factors.append(f"Real Rate Diff: {real_rate_diff:+.2f}pp (Capital Outflow)")
        else:
            factors.append(f"Real Rate Diff: {real_rate_diff:+.2f}pp (Neutral)")

    # Factor 4: PPP / Relative Price Level (informational anchor)
    if ppp_latest is not None:
        factors.append(f"Rel. Price Level: {ppp_latest:.1f}")

    # Factor 5: Credit-to-GDP Gap (financial stability)
    if credit_gap is not None:
        cg_label, cg_score = assess_credit_gap(credit_gap)
        score += cg_score
        factors.append(f"Credit Gap: {credit_gap:+.1f}pp ({cg_label}, score {cg_score:+d})")

    # --- Aggregate Signal ---
    if score >= 6:
        label = ">>> STRONG BUY (Deeply Undervalued) <<<"
    elif score >= 3:
        label = ">> BUY (Undervalued) <<"
    elif score >= 1:
        label = "> LEAN BULLISH <"
    elif score <= -6:
        label = "<<< STRONG SELL (Extremely Overvalued) >>>"
    elif score <= -3:
        label = "<< SELL (Overvalued) >>"
    elif score <= -1:
        label = "< LEAN BEARISH >"
    else:
        label = "-- NEUTRAL / HOLD --"

    return label, factors, score
