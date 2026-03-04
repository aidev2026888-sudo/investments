"""
Precious Metals (Gold/Silver) -- Valuation Analysis

Analyzes gold and silver using dynamic, market-driven safety margin signals.

Gold: Real Yield (TIPS) + Miner P/B (NEM/GOLD) + Price Percentile + Gold/GDX
Silver: Gold/Silver Ratio + Real Yield + Miner P/B (AG/PAAS) + Inventory

Key Innovation: Replaces static AISC ($1,350) with dynamic miner P/B ratios
as the proxy for whether price is near, at, or far above production cost.
When miner P/B < 1.0, gold is near/below AISC -- maximum safety margin.

Usage:
    python analyze.py

    For FRED data (recommended), set environment variable:
        set FRED_API_KEY=your_api_key_here
"""

import sys
import os

# Allow imports from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.gold_data_fetcher import (
    fetch_gold_price_data,
    fetch_silver_price_data,
    fetch_real_yield,
    fetch_real_yield_series,
    compute_gold_silver_ratio,
    fetch_comex_silver_inventory,
    fetch_comex_open_interest,
    fetch_gold_miner_fundamentals,
    fetch_silver_miner_fundamentals,
    fetch_gold_gdx_ratio,
    fetch_shfe_silver_premium,
)
from common.gold_metrics import (
    compute_real_yield_signal,
    compute_safety_margin,
    compute_gold_percentile,
    compute_gold_percentile_values,
    compute_gsr_signal,
    compute_inventory_signal,
    compute_shfe_premium_signal,
)
from common.gold_signals import compute_gold_composite_signal, compute_silver_composite_signal
from common.gold_charting import generate_gold_chart, generate_silver_chart
from common.gold_reporter import (
    print_gold_report, print_silver_report,
    save_gold_report_md, save_silver_report_md,
)


# ==========================================
# Configuration
# ==========================================

YEARS_BACK = 10


def analyze_gold(real_yield, real_yield_df, output_dir):
    """Run gold valuation analysis with dynamic safety margin."""
    df = fetch_gold_price_data(years_back=YEARS_BACK)
    if df is None or df.empty:
        print("Failed to fetch gold price data. Skipping gold analysis.")
        return None, None

    spot_price = df.attrs.get("spot_price", df["price"].iloc[-1])

    # Metrics
    real_yield_signal = compute_real_yield_signal(real_yield)

    # Dynamic safety margin (miner P/B replaces static AISC)
    miner_data = fetch_gold_miner_fundamentals()
    miner_pb, safety_zone, safety_interp = compute_safety_margin(miner_data, "Gold")

    # Gold/GDX ratio
    gold_gdx_ratio = fetch_gold_gdx_ratio()

    # Price percentile
    price_percentile = compute_gold_percentile(df["price"], spot_price)
    percentile_values = compute_gold_percentile_values(df["price"])

    # Signal (uses miner_pb instead of aisc_premium_pct)
    signal_label, signal_factors, signal_score, confidence = (
        compute_gold_composite_signal(
            real_yield=real_yield,
            miner_pb=miner_pb,
            price_percentile=price_percentile,
        )
    )

    # Report
    print_gold_report(
        spot_price=spot_price,
        real_yield=real_yield,
        real_yield_signal=real_yield_signal,
        miner_pb=miner_pb,
        safety_zone=safety_zone,
        safety_interp=safety_interp,
        miner_data=miner_data,
        gold_gdx_ratio=gold_gdx_ratio,
        price_percentile=price_percentile,
        percentile_values=percentile_values,
        signal_label=signal_label,
        signal_factors=signal_factors,
        signal_score=signal_score,
        confidence=confidence,
        years_back=YEARS_BACK,
    )

    # Save markdown report
    save_gold_report_md(
        spot_price=spot_price, real_yield=real_yield,
        real_yield_signal=real_yield_signal, miner_pb=miner_pb,
        safety_zone=safety_zone, safety_interp=safety_interp,
        miner_data=miner_data, gold_gdx_ratio=gold_gdx_ratio,
        price_percentile=price_percentile, percentile_values=percentile_values,
        signal_label=signal_label, signal_factors=signal_factors,
        signal_score=signal_score, confidence=confidence,
        years_back=YEARS_BACK, output_dir=output_dir,
    )

    # Chart
    generate_gold_chart(
        df=df, spot_price=spot_price, price_percentile=price_percentile,
        percentile_values=percentile_values, real_yield=real_yield,
        real_yield_df=real_yield_df, years_back=YEARS_BACK,
        output_dir=output_dir,
    )

    return spot_price, df


def analyze_silver(gold_price, gold_df, real_yield, output_dir):
    """Run silver valuation analysis with dynamic safety margin."""
    silver_df = fetch_silver_price_data(years_back=YEARS_BACK)
    if silver_df is None or silver_df.empty:
        print("Failed to fetch silver price data. Skipping silver analysis.")
        return

    silver_spot = silver_df.attrs.get("spot_price", silver_df["price"].iloc[-1])

    # Gold/Silver Ratio
    gsr = compute_gold_silver_ratio(gold_price, silver_spot)
    gsr_signal = compute_gsr_signal(gsr)
    print(f"  Gold/Silver Ratio: {gsr:.1f}")

    # Dynamic safety margin (silver miner P/B)
    miner_data = fetch_silver_miner_fundamentals()
    miner_pb, safety_zone, safety_interp = compute_safety_margin(miner_data, "Silver")

    # Inventory + Open Interest for coverage ratio
    inventory_data = fetch_comex_silver_inventory(silver_spot=silver_spot)
    oi_data = fetch_comex_open_interest()
    inventory_signal = compute_inventory_signal(inventory_data, oi_data=oi_data)

    # Price percentile
    price_percentile = compute_gold_percentile(silver_df["price"], silver_spot)
    percentile_values = compute_gold_percentile_values(silver_df["price"])

    # SHFE Silver Premium
    shfe_premium_data = fetch_shfe_silver_premium(comex_price_usd_oz=silver_spot)
    shfe_premium_signal = None
    shfe_premium_pct = None
    if shfe_premium_data:
        shfe_premium_pct = shfe_premium_data["premium_pct"]
        shfe_premium_signal = compute_shfe_premium_signal(shfe_premium_pct)

    # Composite signal (uses miner_pb instead of aisc_premium_pct)
    signal_label, signal_factors, signal_score, confidence = (
        compute_silver_composite_signal(
            real_yield=real_yield,
            gsr=gsr,
            miner_pb=miner_pb,
            price_percentile=price_percentile,
            shfe_premium_pct=shfe_premium_pct,
        )
    )

    # Report
    print_silver_report(
        spot_price=silver_spot,
        gold_price=gold_price,
        gsr=gsr,
        gsr_signal=gsr_signal,
        real_yield=real_yield,
        miner_pb=miner_pb,
        safety_zone=safety_zone,
        safety_interp=safety_interp,
        miner_data=miner_data,
        inventory_data=inventory_data,
        inventory_signal=inventory_signal,
        shfe_premium_data=shfe_premium_data,
        shfe_premium_signal=shfe_premium_signal,
        price_percentile=price_percentile,
        percentile_values=percentile_values,
        signal_label=signal_label,
        signal_factors=signal_factors,
        signal_score=signal_score,
        confidence=confidence,
        years_back=YEARS_BACK,
    )

    # Save markdown report
    save_silver_report_md(
        spot_price=silver_spot, gold_price=gold_price, gsr=gsr,
        gsr_signal=gsr_signal, real_yield=real_yield, miner_pb=miner_pb,
        safety_zone=safety_zone, safety_interp=safety_interp,
        miner_data=miner_data, inventory_data=inventory_data,
        inventory_signal=inventory_signal, 
        shfe_premium_data=shfe_premium_data, shfe_premium_signal=shfe_premium_signal,
        price_percentile=price_percentile,
        percentile_values=percentile_values, signal_label=signal_label,
        signal_factors=signal_factors, signal_score=signal_score,
        confidence=confidence, years_back=YEARS_BACK, output_dir=output_dir,
    )

    # Chart
    generate_silver_chart(
        silver_df=silver_df, gold_df=gold_df, spot_price=silver_spot,
        price_percentile=price_percentile, percentile_values=percentile_values,
        gsr=gsr, years_back=YEARS_BACK, output_dir=output_dir,
    )


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Shared: fetch real yield (used by both gold and silver)
    real_yield = fetch_real_yield()
    real_yield_df = fetch_real_yield_series(years_back=YEARS_BACK)

    # === GOLD ===
    gold_price, gold_df = analyze_gold(real_yield, real_yield_df, output_dir)

    # === SILVER ===
    if gold_price is not None and gold_df is not None:
        analyze_silver(gold_price, gold_df, real_yield, output_dir)
    else:
        print("\n[WARN] Skipping silver analysis (gold data needed for GSR).")


if __name__ == "__main__":
    main()
