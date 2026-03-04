"""
Data fetching module for the four-dimensional currency valuation framework.

Sources:
  - PPP:              World Bank REST API  -- indicator PA.NUS.PPP
  - REER:             BIS SDMX REST API v1 -- dataflow  WS_EER
  - Current Account:  World Bank REST API  -- indicator BN.CAB.XOKA.GD.ZS
  - Nominal Rates:    FRED (fredapi)       -- 10-Year govt bond yields
  - CPI:              BIS SDMX REST API v1 -- dataflow  WS_LONG_CPI
  - Policy Rates:     BIS SDMX REST API v1 -- dataflow  WS_CBPOL

All functions return pandas DataFrames indexed by year or date.
"""

import io
import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import requests

from dotenv import load_dotenv
load_dotenv()  # Load .env from repo root (searches upward)

from fx_config import CurrencyProfile, FXFrameworkConfig


# =====================================================================
# BIS SDMX REST API v1 helpers
# =====================================================================

BIS_API_BASE = "https://stats.bis.org/api/v1"


def _fetch_bis_csv(dataflow: str, key: str, start_period: str,
                   end_period: Optional[str] = None) -> Optional[pd.DataFrame]:
    """Fetch a BIS SDMX v1 dataflow as CSV and return a DataFrame.

    Args:
        dataflow:     e.g. "WS_EER"
        key:          e.g. "M.R.B.US"
        start_period: e.g. "2000-01"
        end_period:   e.g. "2025-12" (optional)

    Returns:
        DataFrame with columns from the CSV, or None on failure.
    """
    url = f"{BIS_API_BASE}/data/{dataflow}/{key}"
    params = {
        "startPeriod": start_period,
        "format": "csv",
    }
    if end_period:
        params["endPeriod"] = end_period

    try:
        print(f"  [BIS] Fetching {dataflow} / {key} ...")
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        if df.empty:
            print(f"  [WARN] Empty response from BIS for {dataflow}/{key}")
            return None
        print(f"  [OK] BIS returned {len(df)} rows")
        return df
    except Exception as e:
        print(f"  [FAIL] BIS fetch failed for {dataflow}/{key}: {e}")
        return None


# =====================================================================
# 1.  REER  -- Real Effective Exchange Rate from BIS
# =====================================================================

def fetch_reer(profiles: List[CurrencyProfile],
               start_year: int) -> Dict[str, pd.DataFrame]:
    """Fetch monthly REER (broad basket) from BIS for each currency.

    Returns:
        Dict mapping currency code -> DataFrame with columns ['date', 'reer'].
    """
    result: Dict[str, pd.DataFrame] = {}
    start_period = f"{start_year}-01"

    for p in profiles:
        key = f"M.R.B.{p.bis_country}"
        raw = _fetch_bis_csv("WS_EER", key, start_period)
        if raw is None:
            continue
        try:
            # BIS CSV columns: TIME_PERIOD, OBS_VALUE, ...
            df = pd.DataFrame()
            df["date"] = pd.to_datetime(raw["TIME_PERIOD"])
            df["reer"] = pd.to_numeric(raw["OBS_VALUE"], errors="coerce")
            df = df.dropna().sort_values("date").reset_index(drop=True)
            result[p.code] = df
            print(f"  [REER] {p.code}: {len(df)} months, "
                  f"{df['date'].min():%Y-%m} -> {df['date'].max():%Y-%m}")
        except Exception as e:
            print(f"  [FAIL] REER parse error for {p.code}: {e}")

    return result


# =====================================================================
# 2.  CPI  -- Consumer Price Index from BIS
# =====================================================================

def fetch_cpi_bis(profiles: List[CurrencyProfile],
                  start_year: int) -> Dict[str, pd.DataFrame]:
    """Fetch monthly CPI index from BIS for each currency area.

    Returns:
        Dict mapping currency code -> DataFrame with columns ['date', 'cpi'].
    """
    result: Dict[str, pd.DataFrame] = {}
    start_period = f"{start_year}-01"

    for p in profiles:
        key = f"M.{p.bis_cpi_key}.628"
        raw = _fetch_bis_csv("WS_LONG_CPI", key, start_period)
        if raw is None:
            continue
        try:
            df = pd.DataFrame()
            df["date"] = pd.to_datetime(raw["TIME_PERIOD"])
            df["cpi"] = pd.to_numeric(raw["OBS_VALUE"], errors="coerce")
            df = df.dropna().sort_values("date").reset_index(drop=True)
            result[p.code] = df
            print(f"  [CPI-BIS] {p.code}: {len(df)} months")
        except Exception as e:
            print(f"  [FAIL] CPI-BIS parse error for {p.code}: {e}")

    return result


# =====================================================================
# 3.  Policy Rates  -- Central Bank Policy Rates from BIS
# =====================================================================

def fetch_policy_rates_bis(profiles: List[CurrencyProfile],
                           start_year: int) -> Dict[str, pd.DataFrame]:
    """Fetch monthly central bank policy rates from BIS.

    Returns:
        Dict mapping currency code -> DataFrame with columns ['date', 'policy_rate'].
    """
    result: Dict[str, pd.DataFrame] = {}
    start_period = f"{start_year}-01"

    for p in profiles:
        key = f"M.{p.bis_policy_rate_key}"
        raw = _fetch_bis_csv("WS_CBPOL", key, start_period)
        if raw is None:
            continue
        try:
            df = pd.DataFrame()
            df["date"] = pd.to_datetime(raw["TIME_PERIOD"])
            df["policy_rate"] = pd.to_numeric(raw["OBS_VALUE"], errors="coerce")
            df = df.dropna().sort_values("date").reset_index(drop=True)
            result[p.code] = df
            print(f"  [POLICY-BIS] {p.code}: {len(df)} months")
        except Exception as e:
            print(f"  [FAIL] Policy rate parse error for {p.code}: {e}")

    return result


# =====================================================================
# 4.  Nominal 10-Year Bond Yields  -- from FRED
# =====================================================================

def _fetch_fred_series(series_id: str, start_date: str) -> Optional[pd.Series]:
    """Internal helper: fetch a FRED time series."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print(f"  [WARN] FRED_API_KEY not set. Cannot fetch {series_id}.")
        return None
    try:
        from fredapi import Fred
        fred = Fred(api_key=api_key)
        data = fred.get_series(series_id, observation_start=start_date)
        if data is None or data.empty:
            print(f"  [WARN] No data from FRED for {series_id}")
            return None
        return data.dropna()
    except Exception as e:
        print(f"  [FAIL] FRED fetch failed for {series_id}: {e}")
        return None


def fetch_nominal_rates_fred(profiles: List[CurrencyProfile],
                             start_year: int) -> Dict[str, pd.DataFrame]:
    """Fetch monthly 10-Year government bond yields from FRED.

    Returns:
        Dict mapping currency code -> DataFrame with ['date', 'nominal_rate'].
    """
    result: Dict[str, pd.DataFrame] = {}
    start_date = f"{start_year}-01-01"

    for p in profiles:
        if not p.fred_nominal_rate:
            continue
        series = _fetch_fred_series(p.fred_nominal_rate, start_date)
        if series is None:
            continue
        df = pd.DataFrame({"date": series.index, "nominal_rate": series.values})
        df["date"] = pd.to_datetime(df["date"])
        # Resample to month-end
        df = df.set_index("date").resample("ME").last().dropna().reset_index()
        result[p.code] = df
        print(f"  [FRED] {p.code} 10Y yield: {len(df)} months")

    return result


# =====================================================================
# 5.  PPP (Relative Price Level) -- derived from BIS NEER & REER
# =====================================================================
#
# BIS does not publish a standalone PPP dataset.
# However, REER/NEER ratio = relative price level index, which captures
# the same concept as PPP:
#   Relative Price Level = REER / NEER
#   If > 1: the country's prices are higher than trading partners (overvalued)
#   If < 1: prices are lower (undervalued)
#
# We also normalize against a reference period mean to get a deviation %.

def fetch_neer(profiles: List[CurrencyProfile],
               start_year: int) -> Dict[str, pd.DataFrame]:
    """Fetch monthly NEER (Nominal EER, broad basket) from BIS.

    Returns:
        Dict mapping currency code -> DataFrame with columns ['date', 'neer'].
    """
    result: Dict[str, pd.DataFrame] = {}
    start_period = f"{start_year}-01"

    for p in profiles:
        key = f"M.N.B.{p.bis_country}"
        raw = _fetch_bis_csv("WS_EER", key, start_period)
        if raw is None:
            continue
        try:
            df = pd.DataFrame()
            df["date"] = pd.to_datetime(raw["TIME_PERIOD"])
            df["neer"] = pd.to_numeric(raw["OBS_VALUE"], errors="coerce")
            df = df.dropna().sort_values("date").reset_index(drop=True)
            result[p.code] = df
            print(f"  [NEER] {p.code}: {len(df)} months, "
                  f"{df['date'].min():%Y-%m} -> {df['date'].max():%Y-%m}")
        except Exception as e:
            print(f"  [FAIL] NEER parse error for {p.code}: {e}")

    return result


def compute_relative_price_level(
    reer_data: Dict[str, pd.DataFrame],
    neer_data: Dict[str, pd.DataFrame],
) -> Dict[str, pd.DataFrame]:
    """Compute relative price level index from BIS REER/NEER ratio.

    Relative Price Level = REER / NEER * 100
    This is the BIS-derived PPP equivalent:
      > 100 means domestic prices higher than trade partners (overvalued)
      < 100 means domestic prices lower (undervalued)

    Returns:
        Dict mapping currency code -> DataFrame with
        ['date', 'reer', 'neer', 'rel_price_level', 'rpl_deviation_pct'].
    """
    result: Dict[str, pd.DataFrame] = {}

    for code in reer_data:
        if code not in neer_data:
            print(f"  [WARN] No NEER data for {code}, cannot compute relative price level")
            continue

        reer_df = reer_data[code].set_index("date")
        neer_df = neer_data[code].set_index("date")

        # Merge on date
        merged = reer_df.join(neer_df, how="inner").dropna()
        if merged.empty:
            continue

        # Relative price level: ratio of REER to NEER
        merged["rel_price_level"] = (merged["reer"] / merged["neer"]) * 100

        # Deviation from long-term mean (%)
        rpl_mean = merged["rel_price_level"].mean()
        merged["rpl_deviation_pct"] = (
            (merged["rel_price_level"] - rpl_mean) / rpl_mean * 100
        )

        merged = merged.reset_index()
        result[code] = merged
        latest_rpl = merged["rel_price_level"].iloc[-1]
        latest_dev = merged["rpl_deviation_pct"].iloc[-1]
        print(f"  [RPL] {code}: {len(merged)} months, "
              f"latest RPL={latest_rpl:.1f}, deviation={latest_dev:+.1f}%")

    return result


# =====================================================================
# 6.  World Bank data helper (for Current Account)
# =====================================================================

def _fetch_wb_indicator(indicator: str, country: str,
                        start_year: int, end_year: int) -> Optional[pd.DataFrame]:
    """Fetch a World Bank indicator via direct REST API.

    Returns DataFrame with ['year', 'value'] or None.
    """
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {
        "date": f"{start_year}:{end_year}",
        "format": "json",
        "per_page": "100",
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # WB API returns [metadata, records]
        if not isinstance(data, list) or len(data) < 2:
            return None

        records = data[1]
        if not records:
            return None

        rows = []
        for r in records:
            year = int(r.get("date", 0))
            val = r.get("value")
            if val is not None and year > 0:
                rows.append({"year": year, "value": float(val)})

        if not rows:
            return None

        df = pd.DataFrame(rows).sort_values("year").reset_index(drop=True)
        return df

    except Exception as e:
        print(f"  [FAIL] World Bank fetch error ({indicator}/{country}): {e}")
        return None



# =====================================================================
# 6.  Current Account (% of GDP)  -- from World Bank (direct HTTP API)
# =====================================================================

def fetch_current_account(profiles: List[CurrencyProfile],
                          start_year: int) -> Dict[str, pd.DataFrame]:
    """Fetch current account balance as % of GDP from World Bank.

    Indicator: BN.CAB.XOKA.GD.ZS

    Returns:
        Dict mapping currency code -> DataFrame with ['year', 'ca_pct_gdp'].
    """
    result: Dict[str, pd.DataFrame] = {}
    end_year = datetime.now().year

    for p in profiles:
        wb_code = p.wb_country
        if wb_code == "EMU":
            wb_code = "EMU"  # Try EMU first
        print(f"  [WB] Fetching Current Account for {p.code} ({wb_code}) ...")
        df = _fetch_wb_indicator("BN.CAB.XOKA.GD.ZS", wb_code, start_year, end_year)
        if df is None or df.empty:
            if wb_code == "EMU":
                # Try Germany as Eurozone proxy
                for fallback in ["EUU", "DEU"]:
                    print(f"  [WARN] {wb_code} not found, trying {fallback} ...")
                    df = _fetch_wb_indicator("BN.CAB.XOKA.GD.ZS", fallback, start_year, end_year)
                    if df is not None and not df.empty:
                        break
            if df is None or df.empty:
                print(f"  [WARN] No Current Account data for {p.code}")
                continue

        df = df.rename(columns={"value": "ca_pct_gdp"})
        result[p.code] = df
        print(f"  [CA] {p.code}: {len(df)} years, "
              f"{df['year'].min()} -> {df['year'].max()}")

    return result


# =====================================================================
# 7.  Compute Real Interest Rates  (nominal rate - CPI YoY%)
# =====================================================================

def compute_real_rates(
    nominal_rates: Dict[str, pd.DataFrame],
    cpi_data: Dict[str, pd.DataFrame],
    policy_rates: Dict[str, pd.DataFrame],
) -> Dict[str, pd.DataFrame]:
    """Compute real interest rates = nominal rate - CPI YoY%.

    Uses FRED 10Y yields as the primary nominal rate.
    Falls back to BIS policy rates if FRED is unavailable.
    CPI YoY% is computed from BIS CPI index.

    Returns:
        Dict mapping currency code -> DataFrame with
        ['date', 'nominal_rate', 'cpi_yoy', 'real_rate'].
    """
    result: Dict[str, pd.DataFrame] = {}

    for code in cpi_data:
        cpi_df = cpi_data[code].copy()
        cpi_df = cpi_df.set_index("date").sort_index()
        # Normalize dates to month-start (BIS uses 1st, FRED uses month-end)
        cpi_df.index = cpi_df.index.to_period("M").to_timestamp()
        # Compute YoY % change from CPI index
        cpi_df["cpi_yoy"] = cpi_df["cpi"].pct_change(periods=12) * 100

        # Prefer FRED 10Y yields, fall back to BIS policy rates
        if code in nominal_rates:
            rate_df = nominal_rates[code].copy().set_index("date").sort_index()
        elif code in policy_rates:
            rate_df = policy_rates[code].copy().set_index("date").sort_index()
            rate_df = rate_df.rename(columns={"policy_rate": "nominal_rate"})
        else:
            print(f"  [WARN] No nominal rate data for {code}, skipping real rate.")
            continue

        # Normalize rate dates to month-start to match CPI
        rate_df.index = rate_df.index.to_period("M").to_timestamp()

        # Merge on month
        merged = cpi_df[["cpi_yoy"]].join(rate_df[["nominal_rate"]], how="inner")
        merged = merged.dropna()
        if merged.empty:
            print(f"  [WARN] No overlapping CPI/rate data for {code}, skipping real rate.")
            continue
        merged["real_rate"] = merged["nominal_rate"] - merged["cpi_yoy"]
        merged = merged.reset_index()

        result[code] = merged
        print(f"  [REAL RATE] {code}: {len(merged)} months, "
              f"latest real rate = {merged['real_rate'].iloc[-1]:.2f}%")

    return result


# =====================================================================
# 8.  Credit-to-GDP Gap  -- from BIS (WS_CREDIT_GAP)
# =====================================================================

def fetch_credit_gap(profiles: List[CurrencyProfile],
                     start_year: int) -> Dict[str, pd.DataFrame]:
    """Fetch quarterly credit-to-GDP gap from BIS.

    The credit-to-GDP gap measures the deviation of total private-sector
    credit (as % of GDP) from its long-term trend (HP filter).
    It is the key early-warning indicator for banking crises (Basel III).

    BIS dataflow: WS_CREDIT_GAP, key: Q.{country}.P.A
      CG_DTYPE=C -> gap (pp deviation from trend)
      CG_DTYPE=B -> trend (long-term trend value)
      CG_DTYPE=A -> ratio (actual credit-to-GDP %)

    Returns:
        Dict mapping currency code -> DataFrame with
        ['date', 'credit_gap', 'credit_ratio', 'credit_trend'].
    """
    result: Dict[str, pd.DataFrame] = {}
    start_period = f"{start_year}-Q1"

    for p in profiles:
        bis_code = p.bis_credit_country or p.bis_country
        key = f"Q.{bis_code}.P.A"
        raw = _fetch_bis_csv("WS_CREDIT_GAP", key, start_period)
        if raw is None:
            continue
        try:
            # Separate by CG_DTYPE: C=gap, B=trend, A=ratio
            gap_df = raw[raw["CG_DTYPE"] == "C"][["TIME_PERIOD", "OBS_VALUE"]].copy()
            trend_df = raw[raw["CG_DTYPE"] == "B"][["TIME_PERIOD", "OBS_VALUE"]].copy()
            ratio_df = raw[raw["CG_DTYPE"] == "A"][["TIME_PERIOD", "OBS_VALUE"]].copy()

            if gap_df.empty:
                print(f"  [WARN] No credit gap data for {p.code}")
                continue

            # Parse dates (quarterly: 2024-Q1 -> 2024-03-31)
            gap_df["date"] = pd.PeriodIndex(gap_df["TIME_PERIOD"], freq="Q").to_timestamp("Q")
            gap_df["credit_gap"] = pd.to_numeric(gap_df["OBS_VALUE"], errors="coerce")

            merged = gap_df[["date", "credit_gap"]].copy()

            if not trend_df.empty:
                trend_df["date"] = pd.PeriodIndex(trend_df["TIME_PERIOD"], freq="Q").to_timestamp("Q")
                trend_df["credit_trend"] = pd.to_numeric(trend_df["OBS_VALUE"], errors="coerce")
                merged = merged.merge(trend_df[["date", "credit_trend"]], on="date", how="left")

            if not ratio_df.empty:
                ratio_df["date"] = pd.PeriodIndex(ratio_df["TIME_PERIOD"], freq="Q").to_timestamp("Q")
                ratio_df["credit_ratio"] = pd.to_numeric(ratio_df["OBS_VALUE"], errors="coerce")
                merged = merged.merge(ratio_df[["date", "credit_ratio"]], on="date", how="left")

            merged = merged.dropna(subset=["credit_gap"]).sort_values("date").reset_index(drop=True)
            result[p.code] = merged

            latest_gap = merged["credit_gap"].iloc[-1]
            print(f"  [CREDIT GAP] {p.code}: {len(merged)} quarters, "
                  f"latest gap = {latest_gap:+.1f}pp")
        except Exception as e:
            print(f"  [FAIL] Credit gap parse error for {p.code}: {e}")

    return result


# =====================================================================
# Master fetch function
# =====================================================================

def fetch_all_data(config: FXFrameworkConfig) -> dict:
    """Fetch all five dimensions of data for the configured currencies.

    Returns a dict with keys:
        'reer', 'neer', 'rpl' (relative price level), 'current_account',
        'real_rates', 'credit_gap', 'cpi', 'nominal_rates', 'policy_rates'
    Each value is a Dict[currency_code, DataFrame].
    """
    profiles = config.currencies
    start = config.start_year

    print("=" * 70)
    print(f"  Fetching data for: {config.currency_codes}")
    print(f"  Period: {start} -> {datetime.now().year}")
    print("=" * 70)

    # --- BIS data ---
    print("\n> REER (BIS)")
    reer = fetch_reer(profiles, start)

    print("\n> NEER (BIS)")
    neer = fetch_neer(profiles, start)

    print("\n> Relative Price Level (REER/NEER = BIS-derived PPP)")
    rpl = compute_relative_price_level(reer, neer)

    print("\n> CPI (BIS)")
    cpi = fetch_cpi_bis(profiles, start)

    print("\n> Policy Rates (BIS)")
    policy = fetch_policy_rates_bis(profiles, start)

    print("\n> Credit-to-GDP Gap (BIS)")
    credit_gap = fetch_credit_gap(profiles, start)

    # --- FRED data ---
    print("\n> Nominal 10Y Bond Yields (FRED)")
    nominal = fetch_nominal_rates_fred(profiles, start)

    # --- World Bank data ---
    print("\n> Current Account (World Bank)")
    ca = fetch_current_account(profiles, start)

    # --- Compute real rates ---
    print("\n> Computing Real Interest Rates")
    real_rates = compute_real_rates(nominal, cpi, policy)

    return {
        "reer": reer,
        "neer": neer,
        "rpl": rpl,
        "current_account": ca,
        "real_rates": real_rates,
        "credit_gap": credit_gap,
        "cpi": cpi,
        "nominal_rates": nominal,
        "policy_rates": policy,
    }

