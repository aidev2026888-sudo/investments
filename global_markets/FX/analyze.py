"""
FX Valuation Framework -- Five-Dimensional Currency Monitor

Monitors REER, Relative Price Level, Current Account, Real Interest Rate
Differentials, and Credit-to-GDP Gap for configurable currencies.

Usage:
    python analyze.py

Configuration:
    Edit fx_config.py to change currencies, lookback period, etc.

Data Sources:
    - REER, NEER, CPI:    BIS (stats.bis.org) -- public SDMX API v1
    - Policy Rates:       BIS -- public SDMX API v1
    - PPP (Rel. Price):   Derived from BIS REER/NEER ratio
    - Credit-to-GDP Gap:  BIS WS_CREDIT_GAP -- public SDMX API v1
    - Current Acct:       World Bank REST API
    - 10Y Bond Yields:    FRED (fredapi) -- optional, requires FRED_API_KEY env var

    For FRED data, add to .env file in repo root:
        FRED_API_KEY=your_api_key_here
"""

import os
import sys

# Allow running from the FX directory directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fx_config import FXFrameworkConfig
from fx_data_fetcher import fetch_all_data
from fx_metrics import (
    compute_reer_zscore,
    compute_reer_percentile,
    assess_current_account,
    assess_credit_gap,
    compute_real_rate_differential,
    compute_composite_signal,
)
from fx_charting import generate_currency_dashboard, generate_overview_heatmap
from fx_reporter import (
    print_currency_report,
    print_summary_table,
    print_framework_note,
    print_separator,
    save_fx_report_md,
)


def main():
    # ==========================================
    # Configuration -- edit fx_config.py to change
    # ==========================================
    config = FXFrameworkConfig()

    print("\n" + "=" * 70)
    print("  FIVE-DIMENSIONAL CURRENCY VALUATION FRAMEWORK")
    print(f"  Currencies: {config.currency_codes}")
    print(f"  Period: {config.start_year} -> present ({config.years_back} years)")
    print(f"  Base: {config.base_currency}")
    print("=" * 70)

    # ==========================================
    # 1. Fetch all data
    # ==========================================
    data = fetch_all_data(config)

    reer = data["reer"]
    rpl = data["rpl"]  # Relative Price Level (REER/NEER = BIS-derived PPP)
    ca = data["current_account"]
    real_rates = data["real_rates"]
    credit_gap = data["credit_gap"]

    # ==========================================
    # 2. Compute metrics for each currency
    # ==========================================
    print("\n" + "=" * 70)
    print("  COMPUTING METRICS")
    print("=" * 70)

    # Real rate differentials
    rate_diffs = compute_real_rate_differential(real_rates, config.base_currency)

    summary_data = {}
    output_dir = os.path.dirname(os.path.abspath(__file__))

    for profile in config.currencies:
        code = profile.code
        print(f"\n  Processing {code} ({profile.country_name}) ...")

        # --- REER ---
        reer_current, reer_z, reer_mean = None, None, None
        reer_std = 0
        reer_pctile = None
        if code in reer:
            reer_current, reer_z, reer_mean = compute_reer_zscore(reer[code])
            reer_std = reer[code]["reer"].std()
            reer_pctile = compute_reer_percentile(reer[code])

        # --- Relative Price Level (BIS-derived PPP) ---
        rpl_latest, rpl_dev = None, None
        if code in rpl and not rpl[code].empty:
            rpl_latest = rpl[code]["rel_price_level"].iloc[-1]
            rpl_dev = rpl[code]["rpl_deviation_pct"].iloc[-1]

        # --- Current Account ---
        ca_latest, ca_year, ca_label, ca_score = None, None, None, 0
        if code in ca and not ca[code].empty:
            ca_latest = ca[code]["ca_pct_gdp"].iloc[-1]
            ca_year = int(ca[code]["year"].iloc[-1])
            ca_label, ca_score = assess_current_account(ca_latest)

        # --- Real Rate ---
        real_rate_val = None
        if code in real_rates and not real_rates[code].empty:
            real_rate_val = real_rates[code]["real_rate"].iloc[-1]
        rate_diff = rate_diffs.get(code)

        # --- Credit-to-GDP Gap ---
        credit_gap_val, credit_gap_label = None, None
        if code in credit_gap and not credit_gap[code].empty:
            credit_gap_val = credit_gap[code]["credit_gap"].iloc[-1]
            credit_gap_label, _ = assess_credit_gap(credit_gap_val)

        # --- Composite Signal ---
        signal_label, signal_factors, signal_score = compute_composite_signal(
            reer_z=reer_z if reer_z is not None else 0.0,
            ca_score=ca_score,
            real_rate_diff=rate_diff,
            ppp_latest=rpl_latest,
            credit_gap=credit_gap_val,
        )

        # Store summary
        summary_data[code] = {
            "reer_z": reer_z,
            "reer_current": reer_current,
            "reer_pctile": reer_pctile,
            "ca_latest": ca_latest,
            "ca_year": ca_year,
            "ca_label": ca_label,
            "ca_score": ca_score,
            "real_rate": real_rate_val,
            "real_rate_diff": rate_diff,
            "rpl_latest": rpl_latest,
            "rpl_deviation": rpl_dev,
            "credit_gap_val": credit_gap_val,
            "credit_gap_label": credit_gap_label,
            "signal_label": signal_label,
            "signal_factors": signal_factors,
            "composite_score": signal_score,
        }

        # --- Print per-currency report ---
        print_currency_report(
            code=code,
            country_name=profile.country_name,
            reer_current=reer_current,
            reer_z=reer_z,
            reer_mean=reer_mean,
            reer_pctile=reer_pctile,
            rpl_latest=rpl_latest,
            rpl_deviation=rpl_dev,
            ca_latest=ca_latest,
            ca_year=ca_year,
            ca_label=ca_label,
            real_rate=real_rate_val,
            real_rate_diff=rate_diff,
            credit_gap_val=credit_gap_val,
            credit_gap_label=credit_gap_label,
            base_currency=config.base_currency,
            signal_label=signal_label,
            signal_factors=signal_factors,
            signal_score=signal_score,
        )

        # --- Generate per-currency chart ---
        generate_currency_dashboard(
            code=code,
            country_name=profile.country_name,
            reer_df=reer.get(code),
            reer_z=reer_z if reer_z is not None else 0.0,
            reer_mean=reer_mean if reer_mean is not None else 100.0,
            reer_std=reer_std,
            rpl_df=rpl.get(code),
            ca_df=ca.get(code),
            real_rate_df=real_rates.get(code),
            real_rate_diff=rate_diff,
            credit_gap_df=credit_gap.get(code),
            base_currency=config.base_currency,
            output_dir=output_dir,
        )

    # ==========================================
    # 3. Summary table
    # ==========================================
    print_summary_table(summary_data, config.base_currency)
    print_framework_note()

    # ==========================================
    # 4. Overview heatmap + save report
    # ==========================================
    generate_overview_heatmap(summary_data, output_dir)
    save_fx_report_md(summary_data, config, output_dir=output_dir)

    print("\n  [OK] Analysis complete. Charts saved to:", output_dir)
    print()


if __name__ == "__main__":
    main()
