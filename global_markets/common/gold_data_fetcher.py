"""
Data fetching module for precious metals (Gold/Silver) analysis.

Retrieves gold spot price from yfinance (GC=F) and US 10-Year TIPS
real yield from FRED (DFII10).
"""

import os
import yfinance as yf
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple

from dotenv import load_dotenv
load_dotenv()  # Load .env from repo root (searches upward)


# ==========================================
# Gold price data
# ==========================================

def fetch_gold_price_data(years_back: int = 10) -> Optional[pd.DataFrame]:
    """Fetch historical gold spot price data from yfinance (GC=F futures).

    Returns a DataFrame with columns: ['date', 'price']
    with the current spot price stored in df.attrs['spot_price'].
    Returns None if data cannot be fetched.
    """
    start_date = datetime.now() - relativedelta(years=years_back + 1)

    print(f"Fetching gold spot price data (GC=F)...")

    try:
        ticker = yf.Ticker("GC=F")
        hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), auto_adjust=True)

        if hist.empty:
            print(f"  [WARN] No historical price data for GC=F")
            return None

        df = pd.DataFrame()
        df["date"] = hist.index
        df["price"] = hist["Close"].values
        df = df.dropna().reset_index(drop=True)

        spot_price = float(df["price"].iloc[-1])
        df.attrs["spot_price"] = spot_price

        # Trim to analysis window
        cutoff_date = df["date"].max() - relativedelta(years=years_back)
        df = df[df["date"] >= cutoff_date].copy().reset_index(drop=True)

        print(f"  Current Gold Spot: ${spot_price:,.2f}/oz")
        print(f"  [OK] Loaded {len(df)} data points ({years_back}yr window)")
        return df

    except Exception as e:
        print(f"  [FAIL] Gold price data fetch failed: {e}")
        return None


# ==========================================
# Silver price data
# ==========================================

def fetch_silver_price_data(years_back: int = 10) -> Optional[pd.DataFrame]:
    """Fetch historical silver spot price data from yfinance (SI=F futures).

    Returns a DataFrame with columns: ['date', 'price']
    with the current spot price stored in df.attrs['spot_price'].
    Returns None if data cannot be fetched.
    """
    start_date = datetime.now() - relativedelta(years=years_back + 1)

    print(f"Fetching silver spot price data (SI=F)...")

    try:
        ticker = yf.Ticker("SI=F")
        hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), auto_adjust=True)

        if hist.empty:
            print(f"  [WARN] No historical price data for SI=F")
            return None

        df = pd.DataFrame()
        df["date"] = hist.index
        df["price"] = hist["Close"].values
        df = df.dropna().reset_index(drop=True)

        spot_price = float(df["price"].iloc[-1])
        df.attrs["spot_price"] = spot_price

        # Trim to analysis window
        cutoff_date = df["date"].max() - relativedelta(years=years_back)
        df = df[df["date"] >= cutoff_date].copy().reset_index(drop=True)

        print(f"  Current Silver Spot: ${spot_price:.2f}/oz")
        print(f"  [OK] Loaded {len(df)} data points ({years_back}yr window)")
        return df

    except Exception as e:
        print(f"  [FAIL] Silver price data fetch failed: {e}")
        return None


def compute_gold_silver_ratio(gold_price: float, silver_price: float) -> float:
    """Compute the Gold/Silver Ratio (GSR).

    GSR = Gold Price / Silver Price
    Historical average ~60-70. Values >80 suggest silver is cheap vs gold.
    """
    return gold_price / silver_price


def fetch_comex_silver_inventory(silver_spot: float = None) -> Optional[dict]:
    """Fetch COMEX silver visible inventory data.

    Uses SLV ETF totalAssets from yfinance as a proxy for visible
    silver inventory.  When silver_spot is provided, an estimated
    ounce count is derived (totalAssets / spot) for use in the
    coverage-ratio calculation.

    Returns dict with keys:
      - 'source': data source name
      - 'value': inventory value in USD
      - 'unit': unit description
      - 'nav': SLV NAV price (may be None)
      - 'est_oz': estimated ounces held (may be None)
    Or None if all sources fail.
    """
    print(f"Fetching COMEX/visible silver inventory data...")

    # SLV ETF as proxy (always available)
    try:
        slv = yf.Ticker("SLV")
        info = slv.info
        total_assets = info.get("totalAssets")
        nav = info.get("navPrice")

        if total_assets:
            print(f"  [SLV] Total Assets: ${total_assets:,.0f}")
            if nav:
                print(f"  [SLV] NAV: ${nav:.2f}")

            # Estimate physical ounces held in SLV
            est_oz = None
            if silver_spot and silver_spot > 0:
                est_oz = total_assets / silver_spot
                print(f"  [SLV] Est. Ounces: {est_oz:,.0f} oz "
                      f"(${total_assets:,.0f} / ${silver_spot:.2f})")

            return {
                "source": "SLV ETF (iShares Silver Trust)",
                "value": total_assets,
                "unit": "USD (total net assets)",
                "nav": nav,
                "est_oz": est_oz,
            }
    except Exception as e:
        print(f"  [WARN] SLV fetch failed: {e}")

    print(f"  [WARN] No inventory data available")
    return None


# COMEX silver contract = 5,000 troy ounces
COMEX_SILVER_CONTRACT_OZ = 5_000


def fetch_comex_open_interest() -> Optional[dict]:
    """Fetch COMEX silver futures open interest from CFTC COT report.

    Downloads the latest weekly Commitments of Traders (COT) report
    from the CFTC website.  The report is updated every Friday and
    reflects data from the preceding Tuesday.

    Returns dict with keys:
      - 'oi_contracts': open interest in number of contracts
      - 'oi_oz':        open interest in troy ounces
      - 'report_date':  date string from the COT report
    Or None if data is unavailable.
    """
    import requests

    CFTC_URL = "https://www.cftc.gov/dea/newcot/deafut.txt"

    print(f"Fetching COMEX silver open interest (CFTC COT)...")
    try:
        resp = requests.get(CFTC_URL, timeout=30)
        resp.raise_for_status()

        # Find the SILVER line (format: "SILVER - COMMODITY EXCHANGE INC.")
        silver_line = None
        for line in resp.text.strip().split("\n"):
            if "SILVER" in line.upper() and "COMMODITY EXCHANGE" in line.upper():
                silver_line = line
                break

        if silver_line is None:
            print(f"  [WARN] SILVER row not found in CFTC COT report")
            return None

        fields = [f.strip().strip('"') for f in silver_line.split(",")]

        # COT layout: field[2]=report_date, field[7]=open_interest_all
        report_date = fields[2] if len(fields) > 2 else "unknown"
        oi_raw = fields[7] if len(fields) > 7 else None

        if oi_raw is None:
            print(f"  [WARN] Could not parse OI from CFTC data")
            return None

        oi_contracts = int(oi_raw)
        oi_oz = oi_contracts * COMEX_SILVER_CONTRACT_OZ

        print(f"  [OI] Open Interest: {oi_contracts:,} contracts "
              f"({oi_oz:,.0f} oz)  [COT report: {report_date}]")
        return {
            "oi_contracts": oi_contracts,
            "oi_oz": oi_oz,
            "report_date": report_date,
        }

    except Exception as e:
        print(f"  [FAIL] CFTC COT fetch failed: {e}")
        return None


# ==========================================
# Miner Fundamentals (Dynamic AISC Proxy)
# ==========================================

# Gold miners: NEM (Newmont), GOLD (Barrick Gold)
GOLD_MINER_TICKERS = ["NEM", "GOLD"]

# Silver miners: AG (First Majestic Silver), PAAS (Pan American Silver)
SILVER_MINER_TICKERS = ["AG", "PAAS"]


def _fetch_miner_data(tickers: list, metal_name: str = "Gold") -> Optional[dict]:
    """Fetch P/B, operating margins, book value from major miners.

    Returns averaged metrics across the provided tickers, or None if
    all fail. Individual miner data is included for transparency.

    Returns dict with keys:
      - 'avg_pb': average P/B ratio
      - 'avg_op_margin': average operating margin (decimal)
      - 'miners': list of {ticker, pb, op_margin, book_value, price} dicts
    """
    print(f"Fetching {metal_name} miner fundamentals ({', '.join(tickers)})...")

    miners = []
    for tkr in tickers:
        try:
            t = yf.Ticker(tkr)
            info = t.info
            pb = info.get("priceToBook")
            op_margin = info.get("operatingMargins")
            book_value = info.get("bookValue")
            price = info.get("currentPrice") or info.get("regularMarketPrice")

            if pb is not None:
                miners.append({
                    "ticker": tkr,
                    "pb": pb,
                    "op_margin": op_margin,
                    "book_value": book_value,
                    "price": price,
                })
                margin_str = f"{op_margin*100:.1f}%" if op_margin else "N/A"
                print(f"  [{tkr}] P/B={pb:.2f}, OpMargin={margin_str}, "
                      f"BookValue=${book_value:.2f}" if book_value else
                      f"  [{tkr}] P/B={pb:.2f}, OpMargin={margin_str}")
            else:
                print(f"  [{tkr}] P/B not available")

        except Exception as e:
            print(f"  [{tkr}] Failed: {e}")

    if not miners:
        print(f"  [WARN] No miner data available")
        return None

    avg_pb = sum(m["pb"] for m in miners) / len(miners)
    margins = [m["op_margin"] for m in miners if m["op_margin"] is not None]
    avg_op_margin = sum(margins) / len(margins) if margins else None

    margin_str = f"{avg_op_margin*100:.1f}%" if avg_op_margin else "N/A"
    print(f"  [AVG] P/B={avg_pb:.2f}, OpMargin={margin_str} "
          f"(from {len(miners)} miners)")

    return {
        "avg_pb": avg_pb,
        "avg_op_margin": avg_op_margin,
        "miners": miners,
    }


def fetch_gold_miner_fundamentals() -> Optional[dict]:
    """Fetch fundamentals from major gold miners (NEM, GOLD).

    The P/B ratio of gold miners is the best dynamic proxy for whether
    gold price is near, above, or far above industry AISC.
    """
    return _fetch_miner_data(GOLD_MINER_TICKERS, "Gold")


def fetch_silver_miner_fundamentals() -> Optional[dict]:
    """Fetch fundamentals from major silver miners (AG, PAAS)."""
    return _fetch_miner_data(SILVER_MINER_TICKERS, "Silver")


def fetch_gold_gdx_ratio() -> Optional[float]:
    """Compute Gold/GDX price ratio.

    When this ratio is high (gold outperforming miners), it can signal
    that miners are struggling despite gold prices -- margins collapsing.
    When low, miners are leveraging gold's rise effectively.
    """
    print(f"Fetching Gold/GDX ratio...")
    try:
        gold = yf.Ticker("GC=F")
        gdx = yf.Ticker("GDX")

        gold_hist = gold.history(period="5d")
        gdx_hist = gdx.history(period="5d")

        if gold_hist.empty or gdx_hist.empty:
            print(f"  [WARN] Missing data for Gold/GDX ratio")
            return None

        gold_price = float(gold_hist["Close"].iloc[-1])
        gdx_price = float(gdx_hist["Close"].iloc[-1])
        ratio = gold_price / gdx_price

        print(f"  Gold/GDX Ratio: {ratio:.1f} "
              f"(Gold ${gold_price:,.0f} / GDX ${gdx_price:.2f})")
        return ratio

    except Exception as e:
        print(f"  [FAIL] Gold/GDX ratio failed: {e}")
        return None


# ==========================================
# US 10-Year Real Yield (TIPS) from FRED
# ==========================================

def _fetch_from_fred(series_id: str, years_back: int) -> Optional[pd.DataFrame]:
    """Internal helper: fetch a FRED time series.

    Returns DataFrame with columns ['date', 'value'] or None.
    """
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print(f"  [WARN] FRED_API_KEY not set. Cannot fetch {series_id} from FRED.")
        return None

    try:
        from fredapi import Fred
        fred = Fred(api_key=api_key)

        start_date = datetime.now() - relativedelta(years=years_back + 1)
        series = fred.get_series(series_id, observation_start=start_date)

        if series is None or series.empty:
            print(f"  [WARN] No data returned from FRED for {series_id}")
            return None

        df = pd.DataFrame()
        df["date"] = series.index
        df["value"] = series.values
        df = df.dropna().reset_index(drop=True)
        return df

    except ImportError:
        print(f"  [WARN] fredapi not installed. Run: pip install fredapi")
        return None
    except Exception as e:
        print(f"  [FAIL] FRED fetch failed for {series_id}: {e}")
        return None


def _fetch_real_yield_yfinance_fallback() -> Optional[float]:
    """Fallback: estimate real yield from yfinance.

    Uses nominal 10Y yield (^TNX) minus a rough breakeven inflation estimate.
    This is less accurate than FRED TIPS data but works without an API key.
    """
    print(f"  [INFO] Attempting yfinance fallback for real yield estimate...")
    try:
        # Nominal 10Y yield
        tnx = yf.Ticker("^TNX")
        hist = tnx.history(period="5d")
        if hist.empty:
            return None
        nominal = float(hist["Close"].iloc[-1])
        if nominal > 1:
            nominal = nominal / 100.0

        # Rough breakeven inflation (typically ~2.0-2.5%)
        # Use a fixed estimate since we can't easily get TIPS breakeven
        breakeven_inflation = 0.023  # 2.3% as rough mid-range estimate
        real_yield = nominal - breakeven_inflation

        print(f"  [WARN] Estimated real yield: {real_yield*100:.2f}% "
              f"(nominal {nominal*100:.2f}% - est. inflation {breakeven_inflation*100:.1f}%)")
        print(f"  [WARN] This is an approximation. Set FRED_API_KEY for accurate TIPS data.")
        return real_yield

    except Exception as e:
        print(f"  [FAIL] yfinance fallback failed: {e}")
        return None


def fetch_real_yield() -> Optional[float]:
    """Fetch the latest US 10-Year TIPS real yield as a decimal.

    Example: 2.0% → 0.02, -0.5% → -0.005

    Primary source: FRED DFII10
    Fallback: yfinance estimate (nominal yield - rough breakeven)

    Returns None if all sources fail.
    """
    print(f"Fetching US 10-Year Real Yield (TIPS)...")

    # Try FRED first
    df = _fetch_from_fred("DFII10", years_back=1)
    if df is not None and not df.empty:
        latest = float(df["value"].iloc[-1])
        # FRED returns in percentage (e.g., 2.05 for 2.05%)
        real_yield_decimal = latest / 100.0
        print(f"  US 10Y Real Yield (TIPS): {latest:.2f}% (from FRED)")
        return real_yield_decimal

    # Fallback to yfinance estimate
    return _fetch_real_yield_yfinance_fallback()


def fetch_real_yield_series(years_back: int = 10) -> Optional[pd.DataFrame]:
    """Fetch historical US 10-Year TIPS real yield series for charting.

    Returns DataFrame with columns: ['date', 'real_yield']
    where real_yield is in percentage (e.g., 2.05 for 2.05%).
    Returns None if FRED is unavailable.
    """
    print(f"Fetching US 10-Year Real Yield history ({years_back}yr)...")

    df = _fetch_from_fred("DFII10", years_back=years_back)
    if df is not None and not df.empty:
        df = df.rename(columns={"value": "real_yield"})
        print(f"  [OK] Loaded {len(df)} real yield data points")
        return df

    print(f"  [WARN] Real yield history not available (FRED_API_KEY not set)")
    return None

# ==========================================
# SHFE Silver Premium (China Demand Indicator)
# ==========================================

def fetch_shfe_silver_premium(comex_price_usd_oz: float) -> Optional[dict]:
    """Fetch SHFE silver price and compute premium over COMEX.

    Returns dict with SHFE price, CNY rate, and premium %.
    """
    print(f"Fetching SHFE Silver premium...")
    try:
        # 1. USD/CNY exchange rate
        ticker = yf.Ticker("CNY=X")
        usd_cny = ticker.info.get("regularMarketPrice") or ticker.fast_info.get("last_price")
        if not usd_cny:
            usd_cny = 7.20  # fallback approximation

        shfe_price_cny_kg = None

        # 2. Fetch from TradingView Scanner API (more reliable than Chinese feeds for external APIs)
        import requests
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        url = "https://scanner.tradingview.com/global/scan"
        payload = {
            "symbols": {"tickers": ["SHFE:AG1!"]},
            "columns": ["close"]
        }
        
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data.get("data") and len(data["data"]) > 0:
                    price = data["data"][0].get("d", [None])[0]
                    if price and price > 0:
                        shfe_price_cny_kg = price
        except Exception as e:
            print(f"  [WARN] TradingView fetch error: {e}")

        if not shfe_price_cny_kg:
            print("  [WARN] Could not fetch SHFE silver price.")
            return None

        # 3. Compute premium
        # 1 kg = 32.1507 troy ounces
        shfe_usd_oz = shfe_price_cny_kg / usd_cny / 32.1507
        premium_pct = (shfe_usd_oz / comex_price_usd_oz - 1) * 100

        print(f"  SHFE Silver: {shfe_price_cny_kg:,.0f} CNY/kg (${shfe_usd_oz:,.2f}/oz)")
        print(f"  Premium vs COMEX (${comex_price_usd_oz:,.2f}/oz): +{premium_pct:.1f}%")

        return {
            "shfe_price_cny_kg": shfe_price_cny_kg,
            "shfe_usd_oz": shfe_usd_oz,
            "usd_cny": usd_cny,
            "comex_usd_oz": comex_price_usd_oz,
            "premium_pct": premium_pct
        }

    except Exception as e:
        print(f"  [FAIL] SHFE silver premium fetch failed: {e}")
        return None
