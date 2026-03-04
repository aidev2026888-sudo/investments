"""
Data fetching module for global market index analysis.

Retrieves price history, PE ratios, bond yields, and VIX data via yfinance/FRED.
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple

from .config import (
    IndexConfig,
    VIX_SPIKE_SURGE_PCT, VIX_SPIKE_RETREAT_PCT,
    VIX_SPIKE_MIN_PEAK, VIX_LOOKBACK_DAYS,
)


def fetch_index_pe_data(config: IndexConfig) -> Optional[pd.DataFrame]:
    """Fetch historical price data and compute a proxy PE time series.

    Strategy:
      1. Download long price history for the ETF (extra years for CAPE rolling window).
      2. Get current trailingPE from ETF .info.
      3. Scale historical prices to create a proxy PE series:
         PE_t = (Price_t / Price_latest) * trailingPE_latest
         This preserves the shape/trend of relative valuation over time.

    Returns a DataFrame with columns: ['date', 'price', 'pe', 'pe_cape']
    or None if data cannot be fetched.
    """
    total_years = config.years_back + config.cape_rolling_years + 1  # extra buffer
    start_date = datetime.now() - relativedelta(years=total_years)

    print(f"Fetching data for {config.name} ({config.etf_ticker})...")

    try:
        etf = yf.Ticker(config.etf_ticker)

        # --- Current PE from ETF info ---
        info = etf.info
        trailing_pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")

        if trailing_pe is None and forward_pe is None:
            print(f"  [WARN] No PE data available for {config.etf_ticker}")
            return None

        current_pe = trailing_pe if trailing_pe else forward_pe
        pe_type = "Trailing PE" if trailing_pe else "Forward PE"
        print(f"  Current {pe_type}: {current_pe:.2f}")

        if forward_pe:
            print(f"  Forward PE: {forward_pe:.2f}")

        # --- Historical price data ---
        hist = etf.history(start=start_date.strftime("%Y-%m-%d"), auto_adjust=True)
        if hist.empty:
            print(f"  [WARN] No historical price data for {config.etf_ticker}")
            return None

        df = pd.DataFrame()
        df["date"] = hist.index
        df["price"] = hist["Close"].values
        df = df.dropna().reset_index(drop=True)

        # --- Build proxy PE series ---
        # Scale prices relative to latest price, then multiply by current PE
        latest_price = df["price"].iloc[-1]
        df["pe"] = (df["price"] / latest_price) * current_pe

        # --- Simplified CAPE: rolling mean PE ---
        df["pe_cape"] = (
            df["pe"]
            .rolling(window=config.cape_rolling_days, min_periods=1)
            .mean()
        )

        # --- Trim to analysis window ---
        cutoff_date = df["date"].max() - relativedelta(years=config.years_back)
        df = df[df["date"] >= cutoff_date].copy().reset_index(drop=True)

        # Store extra info for later use
        df.attrs["trailing_pe"] = trailing_pe
        df.attrs["forward_pe"] = forward_pe
        df.attrs["pe_type"] = pe_type

        print(f"  [OK] Loaded {len(df)} data points ({config.years_back}yr window)")
        return df

    except Exception as e:
        print(f"  [FAIL] Data fetch failed for {config.etf_ticker}: {e}")
        return None


def fetch_etf_info(config: IndexConfig) -> Optional[dict]:
    """Fetch current ETF info dict from yfinance.

    Returns dict with keys like trailingPE, forwardPE, marketCap, etc.
    """
    try:
        etf = yf.Ticker(config.etf_ticker)
        return etf.info
    except Exception as e:
        print(f"  [FAIL] Failed to fetch ETF info for {config.etf_ticker}: {e}")
        return None


def fetch_bond_yield(config: IndexConfig) -> Optional[float]:
    """Fetch the latest 10-year government bond yield as a decimal.

    Example: 4.25% → 0.0425

    Uses the bond_yield_ticker from config. Falls back to None if unavailable.
    """
    if not config.bond_yield_ticker:
        print(f"  [WARN] No bond yield ticker configured for {config.name}")
        return None

    print(f"Fetching 10-year bond yield ({config.bond_yield_ticker})...")

    try:
        ticker = yf.Ticker(config.bond_yield_ticker)
        hist = ticker.history(period="5d")

        if hist.empty:
            print(f"  [WARN] No bond yield data for {config.bond_yield_ticker}")
            return None

        latest_yield = float(hist["Close"].iloc[-1])

        # yfinance returns yields in percentage for most tickers (e.g., 4.25 for 4.25%)
        # Convert to decimal
        if latest_yield > 1:
            latest_yield_decimal = latest_yield / 100.0
        else:
            latest_yield_decimal = latest_yield

        print(f"  10-Year Bond Yield: {latest_yield_decimal * 100:.2f}%")
        return latest_yield_decimal

    except Exception as e:
        print(f"  [FAIL] Bond yield fetch failed: {e}")
        return None


def fetch_market_cap(config: IndexConfig) -> Optional[float]:
    """Fetch the total market cap of the ETF (proxy for index market cap).

    Returns market cap in the ETF's currency, or None if unavailable.
    """
    try:
        etf = yf.Ticker(config.etf_ticker)
        info = etf.info
        market_cap = info.get("totalAssets") or info.get("marketCap")
        return market_cap
    except Exception:
        return None


def fetch_vix_data() -> Optional[dict]:
    """Fetch VIX data and compute spike-retreat indicators.

    Uses configurable thresholds from config.py:
      VIX_SPIKE_SURGE_PCT, VIX_SPIKE_RETREAT_PCT,
      VIX_SPIKE_MIN_PEAK, VIX_LOOKBACK_DAYS

    Returns dict with keys:
      current, high_20d, surge_pct, retreat_pct, percentile,
      is_spike_retreat, data_source
    """
    print("Fetching VIX data...")
    vix_series = None

    # Primary: yfinance
    try:
        vix_raw = yf.download("^VIX", period="2y", progress=False)["Close"].squeeze()
        if hasattr(vix_raw, "columns"):
            vix_raw = vix_raw.iloc[:, 0]
        if len(vix_raw) > 50:
            vix_series = vix_raw.dropna()
            source = "yfinance (^VIX)"
    except Exception:
        pass

    # Fallback: FRED
    if vix_series is None or len(vix_series) < 50:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            from fredapi import Fred
            fred_key = os.getenv("FRED_API_KEY")
            if fred_key:
                fred = Fred(api_key=fred_key)
                vix_series = fred.get_series(
                    "VIXCLS",
                    observation_start=(datetime.now() - relativedelta(years=2)).strftime("%Y-%m-%d"),
                ).dropna()
                source = "FRED (VIXCLS)"
        except Exception:
            pass

    if vix_series is None or len(vix_series) < 50:
        print("  [WARN] VIX data unavailable from both yfinance and FRED")
        return None

    current = float(vix_series.iloc[-1])
    lookback = VIX_LOOKBACK_DAYS

    # 20d rolling max
    high_20d = float(vix_series.rolling(lookback).max().iloc[-1])

    # Surge: how much VIX rose in the lookback window
    vix_ago = float(vix_series.iloc[-lookback]) if len(vix_series) >= lookback else current
    surge_pct = ((high_20d - vix_ago) / vix_ago * 100) if vix_ago > 0 else 0.0

    # Retreat: how far current VIX has dropped from 20d high
    retreat_pct = ((current - high_20d) / high_20d * 100) if high_20d > 0 else 0.0

    # Percentile (within available data)
    percentile = float((vix_series < current).mean() * 100)

    # Spike-retreat detection using configurable thresholds
    is_spike_retreat = (
        high_20d >= VIX_SPIKE_MIN_PEAK
        and surge_pct >= VIX_SPIKE_SURGE_PCT
        and retreat_pct <= -VIX_SPIKE_RETREAT_PCT
    )

    print(f"  [VIX] Current: {current:.1f}, 20d High: {high_20d:.1f}, "
          f"Surge: {surge_pct:+.0f}%, Retreat: {retreat_pct:.0f}% ({source})")
    if is_spike_retreat:
        print(f"  [VIX] ** SPIKE-RETREAT DETECTED ** (peak>{VIX_SPIKE_MIN_PEAK}, "
              f"surge>{VIX_SPIKE_SURGE_PCT}%, retreat>{VIX_SPIKE_RETREAT_PCT}%)")

    return {
        "current": current,
        "high_20d": high_20d,
        "surge_pct": surge_pct,
        "retreat_pct": retreat_pct,
        "percentile": percentile,
        "is_spike_retreat": is_spike_retreat,
        "data_source": source,
    }
