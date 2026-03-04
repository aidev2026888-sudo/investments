"""
Composite signal scoring module for global market index analysis.

Implements a multi-factor model combining PE percentile, CAPE deviation,
and Equity Risk Premium into a single actionable signal.
"""

from typing import List, Optional, Tuple

from .config import CAPE_DEVIATION_HIGH, CAPE_DEVIATION_LOW


def compute_composite_signal(
    percentile: float,
    cape_deviation: Optional[float] = None,
    erp: Optional[float] = None,
) -> Tuple[str, List[str], int, str]:
    """Compute a composite valuation signal from multiple factors.

    Scoring rules:
      Factor 1 — PE Percentile:
        >80 → -2 (bearish)  |  60–80 → -1  |  40–60 → 0  |  20–40 → +1  |  <20 → +2 (bullish)

      Factor 2 — CAPE Deviation:
        >+15% → -1 (overvalued)  |  ±15% → 0  |  <-15% → +1 (undervalued)

      Factor 3 — ERP:
        <0% → -1 (expensive)  |  0–3% → 0  |  3–6% → +1  |  >6% → +2 (very attractive)

    Args:
        percentile:     Current PE percentile (0–100).
        cape_deviation: CAPE deviation percentage (optional).
        erp:            Equity Risk Premium as decimal (optional).

    Returns:
        Tuple of (signal_label, factor_details, total_score, confidence).
    """
    score = 0
    factors: List[str] = []

    # --- Factor 1: PE Percentile ---
    if percentile >= 80:
        score -= 2
        factors.append(f"PE Percentile {percentile:.0f}% (Very High)")
    elif percentile >= 60:
        score -= 1
        factors.append(f"PE Percentile {percentile:.0f}% (High)")
    elif percentile >= 40:
        factors.append(f"PE Percentile {percentile:.0f}% (Neutral)")
    elif percentile >= 20:
        score += 1
        factors.append(f"PE Percentile {percentile:.0f}% (Low)")
    else:
        score += 2
        factors.append(f"PE Percentile {percentile:.0f}% (Very Low)")

    # --- Factor 2: CAPE Deviation ---
    if cape_deviation is not None:
        if cape_deviation > CAPE_DEVIATION_HIGH:
            score -= 1
            factors.append(f"CAPE Deviation +{cape_deviation:.1f}% (Overvalued)")
        elif cape_deviation < CAPE_DEVIATION_LOW:
            score += 1
            factors.append(f"CAPE Deviation {cape_deviation:.1f}% (Undervalued)")
        else:
            factors.append(f"CAPE Deviation {cape_deviation:+.1f}% (Normal)")

    # --- Factor 3: Equity Risk Premium ---
    if erp is not None:
        erp_pct = erp * 100
        if erp_pct > 6:
            score += 2
            factors.append(f"ERP {erp_pct:.1f}% (Very Attractive)")
        elif erp_pct > 3:
            score += 1
            factors.append(f"ERP {erp_pct:.1f}% (Attractive)")
        elif erp_pct > 0:
            factors.append(f"ERP {erp_pct:.1f}% (Neutral)")
        else:
            score -= 1
            factors.append(f"ERP {erp_pct:.1f}% (Expensive)")

    # --- Aggregate Signal ---
    if score >= 4:
        label = ">>> STRONG BUY <<<"
    elif score >= 2:
        label = ">> BUY <<"
    elif score >= -1:
        label = "-- NEUTRAL / HOLD --"
    elif score >= -3:
        label = "<< SELL >>"
    else:
        label = "<<< STRONG SELL >>>"

    # Confidence: how many factors align in the same direction
    total_factors = 1 + (1 if cape_deviation is not None else 0) + (1 if erp is not None else 0)
    confidence = f"{abs(score)}/{total_factors + 1}"

    return label, factors, score, confidence
