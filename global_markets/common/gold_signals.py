"""
Composite signal scoring module for precious metals (Gold/Silver) analysis.

Implements a multi-factor model combining real yield, AISC margin,
and price percentile into a single actionable signal.
"""

from typing import List, Optional, Tuple


def compute_gold_composite_signal(
    real_yield: Optional[float] = None,
    miner_pb: Optional[float] = None,
    price_percentile: Optional[float] = None,
) -> Tuple[str, List[str], int, str]:
    """Compute a composite valuation signal for gold.

    Scoring rules:

      Factor 1 -- Real Yield (inverted: low/negative = bullish gold):
        > 2%    -> -2 (bearish)
        1%-2%   -> -1
        0%-1%   ->  0
        -1%-0%  -> +1
        < -1%   -> +2 (bullish)

      Factor 2 -- Miner P/B (dynamic AISC proxy):
        > 4.0   -> -2 (no safety margin, extreme profitability)
        2.5-4.0 -> -1 (elevated, limited safety)
        1.5-2.5 ->  0 (normal profitability)
        1.0-1.5 -> +1 (near AISC, strong safety)
        < 1.0   -> +2 (below book value = below AISC, max safety)

      Factor 3 -- Price Percentile (in 10-year history):
        > 80th  -> -1 (historically expensive)
        40-80th ->  0
        < 40th  -> +1 (historically cheap)

    Aggregate labels:
      >= 4 -> STRONG BUY   >= 2 -> BUY   >= -1 -> HOLD   >= -3 -> SELL   else -> STRONG SELL

    Args:
        real_yield:       US 10Y TIPS yield as decimal (e.g., 0.02).
        miner_pb:         Average miner P/B ratio (from NEM + GOLD).
        price_percentile: Price percentile in 10-year range (0-100).

    Returns:
        Tuple of (signal_label, factor_details, total_score, confidence).
    """
    score = 0
    factors: List[str] = []

    # --- Factor 1: Real Yield ---
    if real_yield is not None:
        ry_pct = real_yield * 100
        if ry_pct > 2.0:
            score -= 2
            factors.append(f"Real Yield {ry_pct:+.2f}% (Very High -- bearish gold)")
        elif ry_pct > 1.0:
            score -= 1
            factors.append(f"Real Yield {ry_pct:+.2f}% (High -- headwind)")
        elif ry_pct > 0.0:
            factors.append(f"Real Yield {ry_pct:+.2f}% (Neutral)")
        elif ry_pct > -1.0:
            score += 1
            factors.append(f"Real Yield {ry_pct:+.2f}% (Negative -- tailwind)")
        else:
            score += 2
            factors.append(f"Real Yield {ry_pct:+.2f}% (Deeply Negative -- strong tailwind)")

    # --- Factor 2: Miner P/B (Dynamic AISC Proxy) ---
    if miner_pb is not None:
        if miner_pb > 4.0:
            score -= 2
            factors.append(f"Miner P/B {miner_pb:.2f} (No Safety Margin -- extreme profitability)")
        elif miner_pb > 2.5:
            score -= 1
            factors.append(f"Miner P/B {miner_pb:.2f} (Limited Safety -- high profitability)")
        elif miner_pb > 1.5:
            factors.append(f"Miner P/B {miner_pb:.2f} (Moderate -- normal profitability)")
        elif miner_pb > 1.0:
            score += 1
            factors.append(f"Miner P/B {miner_pb:.2f} (Strong Safety -- near AISC)")
        else:
            score += 2
            factors.append(f"Miner P/B {miner_pb:.2f} (Max Safety -- below book value!)")

    # --- Factor 3: Price Percentile ---
    if price_percentile is not None:
        if price_percentile >= 80:
            score -= 1
            factors.append(f"Price Percentile {price_percentile:.0f}% (Historically Expensive)")
        elif price_percentile >= 40:
            factors.append(f"Price Percentile {price_percentile:.0f}% (Mid-Range)")
        else:
            score += 1
            factors.append(f"Price Percentile {price_percentile:.0f}% (Historically Cheap)")

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

    # Confidence: how many factors contributed
    total_factors = (
        (1 if real_yield is not None else 0)
        + (1 if miner_pb is not None else 0)
        + (1 if price_percentile is not None else 0)
    )
    confidence = f"{abs(score)}/{total_factors + 1}"

    return label, factors, score, confidence


def compute_silver_composite_signal(
    real_yield: Optional[float] = None,
    gsr: Optional[float] = None,
    miner_pb: Optional[float] = None,
    price_percentile: Optional[float] = None,
    shfe_premium_pct: Optional[float] = None,
) -> Tuple[str, List[str], int, str]:
    """Compute a composite valuation signal for silver.

    Scoring rules:

      Factor 1 -- Real Yield (same as gold, shared macro driver):
        > 2%   -> -2 | 1-2% -> -1 | 0-1% -> 0 | -1-0% -> +1 | < -1% -> +2

      Factor 2 -- Gold/Silver Ratio (silver-specific):
        > 90   -> +2 (extreme discount)
        80-90  -> +1 (cheap)
        60-80  ->  0 (normal)
        50-60  -> -1 (expensive)
        < 50   -> -2 (extreme premium)

      Factor 3 -- Miner P/B (dynamic AISC proxy, from AG/PAAS):
        > 4.0  -> -2 | 2.5-4.0 -> -1 | 1.5-2.5 -> 0 | 1.0-1.5 -> +1 | < 1.0 -> +2

      Factor 4 -- Price Percentile (10-year):
        > 80th -> -1 | 40-80 -> 0 | < 40th -> +1

      Factor 5 -- SHFE Silver Premium (Chinese Industrial Demand):
        > 10%  -> +2 | 5-10% -> +1 | 0-5% -> 0 | < 0% -> -1

    Args:
        real_yield:       US 10Y TIPS yield as decimal.
        gsr:              Gold/Silver Ratio.
        miner_pb:         Average silver miner P/B ratio (from AG + PAAS).
        price_percentile: Price percentile (0-100).
        shfe_premium_pct: SHFE premium over COMEX spot (%).

    Returns:
        Tuple of (signal_label, factor_details, total_score, confidence).
    """
    score = 0
    factors: List[str] = []

    # --- Factor 1: Real Yield (same logic as gold) ---
    if real_yield is not None:
        ry_pct = real_yield * 100
        if ry_pct > 2.0:
            score -= 2
            factors.append(f"Real Yield {ry_pct:+.2f}% (Very High -- bearish)")
        elif ry_pct > 1.0:
            score -= 1
            factors.append(f"Real Yield {ry_pct:+.2f}% (High -- headwind)")
        elif ry_pct > 0.0:
            factors.append(f"Real Yield {ry_pct:+.2f}% (Neutral)")
        elif ry_pct > -1.0:
            score += 1
            factors.append(f"Real Yield {ry_pct:+.2f}% (Negative -- tailwind)")
        else:
            score += 2
            factors.append(f"Real Yield {ry_pct:+.2f}% (Deeply Negative -- strong tailwind)")

    # --- Factor 2: Gold/Silver Ratio ---
    if gsr is not None:
        if gsr > 90:
            score += 2
            factors.append(f"GSR {gsr:.1f} (Extreme Discount -- silver very cheap)")
        elif gsr > 80:
            score += 1
            factors.append(f"GSR {gsr:.1f} (Cheap vs Gold)")
        elif gsr > 60:
            factors.append(f"GSR {gsr:.1f} (Normal range)")
        elif gsr > 50:
            score -= 1
            factors.append(f"GSR {gsr:.1f} (Expensive vs Gold)")
        else:
            score -= 2
            factors.append(f"GSR {gsr:.1f} (Extreme Premium -- silver overvalued)")

    # --- Factor 3: Miner P/B (Dynamic AISC Proxy) ---
    if miner_pb is not None:
        if miner_pb > 4.0:
            score -= 2
            factors.append(f"Miner P/B {miner_pb:.2f} (No Safety Margin)")
        elif miner_pb > 2.5:
            score -= 1
            factors.append(f"Miner P/B {miner_pb:.2f} (Limited Safety)")
        elif miner_pb > 1.5:
            factors.append(f"Miner P/B {miner_pb:.2f} (Moderate)")
        elif miner_pb > 1.0:
            score += 1
            factors.append(f"Miner P/B {miner_pb:.2f} (Strong Safety -- near AISC)")
        else:
            score += 2
            factors.append(f"Miner P/B {miner_pb:.2f} (Max Safety -- below book!)")

    # --- Factor 4: Price Percentile ---
    if price_percentile is not None:
        if price_percentile >= 80:
            score -= 1
            factors.append(f"Price Percentile {price_percentile:.0f}% (Historically Expensive)")
        elif price_percentile >= 40:
            factors.append(f"Price Percentile {price_percentile:.0f}% (Mid-Range)")
        else:
            score += 1
            factors.append(f"Price Percentile {price_percentile:.0f}% (Historically Cheap)")

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

    total_factors = (
        (1 if real_yield is not None else 0)
        + (1 if gsr is not None else 0)
        + (1 if miner_pb is not None else 0)
        + (1 if price_percentile is not None else 0)
        + (1 if shfe_premium_pct is not None else 0)
    )
    confidence = f"{abs(score)}/{total_factors + 1}"

    return label, factors, score, confidence
