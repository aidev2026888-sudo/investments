"""
CAC 40 (France) — Valuation Analysis

Analyzes the CAC 40 index using EWQ ETF data from yfinance.
Metrics: PE Percentile, Simplified CAPE, ERP (Yield Gap), Composite Signal.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.config import IndexConfig
from common.data_fetcher import fetch_index_pe_data, fetch_bond_yield, fetch_vix_data
from common.metrics import (
    compute_pe_percentile,
    compute_percentile_values,
    compute_cape_deviation,
    compute_erp,
    compute_vix_signal,
)
from common.signals import compute_composite_signal
from common.charting import generate_chart
from common.reporter import print_report, save_report_md


# ==========================================
# Index Configuration
# ==========================================

CONFIG = IndexConfig(
    name="CAC 40",
    ticker="^FCHI",
    etf_ticker="EWQ",
    bond_yield_ticker=None,         # France/EU 10Y not easily available; skipped
    currency="EUR",
    country="FR",
    years_back=10,
    cape_rolling_years=3,
)


def main():
    # 1. Fetch PE data
    df = fetch_index_pe_data(CONFIG)
    if df is None or df.empty:
        print("Failed to fetch data. Exiting.")
        return

    # 2. Compute metrics
    current_pe = df["pe"].iloc[-1]
    forward_pe = df.attrs.get("forward_pe")
    percentile = compute_pe_percentile(df["pe"], current_pe)
    pe_percentile_values = compute_percentile_values(df["pe"])

    cape_value = df["pe_cape"].iloc[-1] if "pe_cape" in df.columns else None
    cape_deviation = compute_cape_deviation(current_pe, cape_value)

    # 3. Fetch bond yield & compute ERP
    bond_yield = fetch_bond_yield(CONFIG)
    erp_result = compute_erp(current_pe, bond_yield)

    # 4. Composite signal
    erp_val = erp_result[1] if erp_result else None
    signal_label, signal_factors, signal_score, confidence = compute_composite_signal(
        percentile, cape_deviation, erp_val
    )

    # 4b. VIX Fear Gauge
    vix_data = fetch_vix_data()
    vix_signal = compute_vix_signal(vix_data)

    # 5. Print report
    print_report(
        config=CONFIG, current_pe=current_pe, forward_pe=forward_pe,
        percentile=percentile, pe_percentile_values=pe_percentile_values,
        cape_value=cape_value, cape_deviation=cape_deviation,
        erp_result=erp_result, bond_yield=bond_yield,
        signal_label=signal_label, signal_factors=signal_factors,
        signal_score=signal_score, confidence=confidence,
        vix_data=vix_data, vix_signal=vix_signal,
    )

    # 6. Generate chart + save report
    output_dir = os.path.dirname(os.path.abspath(__file__))
    save_report_md(
        config=CONFIG, current_pe=current_pe, forward_pe=forward_pe,
        percentile=percentile, pe_percentile_values=pe_percentile_values,
        cape_value=cape_value, cape_deviation=cape_deviation,
        erp_result=erp_result, bond_yield=bond_yield,
        signal_label=signal_label, signal_factors=signal_factors,
        signal_score=signal_score, confidence=confidence,
        vix_data=vix_data, vix_signal=vix_signal,
        output_dir=output_dir,
    )
    erp_info = (erp_result[0], erp_result[1], bond_yield) if erp_result else None
    generate_chart(
        config=CONFIG, df=df, current_pe=current_pe, percentile=percentile,
        pe_percentile_values=pe_percentile_values, erp_info=erp_info,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    main()
