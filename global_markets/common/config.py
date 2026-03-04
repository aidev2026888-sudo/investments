"""
Configuration module for global market index analysis.

Defines the IndexConfig dataclass and shared constants used across all index analyzers.
"""

from dataclasses import dataclass, field
from typing import Optional


# ==========================================
# Shared Constants
# ==========================================

YEARS_BACK_DEFAULT = 10          # Default lookback period (years) for percentile calc
SELL_THRESHOLD = 80.0            # Percentile above which the market is considered overvalued
BUY_THRESHOLD = 20.0             # Percentile below which the market is considered undervalued

PERCENTILE_LEVELS = [80, 60, 40, 20]  # Reference percentile lines for charts

CAPE_ROLLING_YEARS_DEFAULT = 3   # Simplified CAPE: rolling average window in years
CAPE_ROLLING_DAYS_PER_YEAR = 252 # Trading days per year

CAPE_DEVIATION_HIGH = 15.0       # CAPE deviation > this % → overvalued signal
CAPE_DEVIATION_LOW = -15.0       # CAPE deviation < this % → undervalued signal

# Moving averages for chart
SHORT_MA = 60
LONG_MA = 120

# VIX Contrarian Indicator -- configurable thresholds
VIX_SPIKE_SURGE_PCT = 50       # Surge threshold (%) in lookback window
VIX_SPIKE_RETREAT_PCT = 20     # Drop from peak threshold (%)
VIX_SPIKE_MIN_PEAK = 25        # Minimum VIX peak to qualify as spike
VIX_LOOKBACK_DAYS = 20         # Rolling window for spike detection (trading days)


@dataclass
class IndexConfig:
    """Configuration for a single market index analysis.

    Attributes:
        name:               Human-readable index name (e.g. "S&P 500")
        ticker:             Yahoo Finance index ticker (e.g. "^GSPC")
        etf_ticker:         Country ETF ticker for PE data (e.g. "SPY")
        bond_yield_ticker:  Yahoo Finance ticker for 10-year govt bond yield
        currency:           Currency code (e.g. "USD", "EUR", "GBP", "CHF")
        country:            Country/region code (e.g. "US", "CH", "FR", "DE", "UK")
        years_back:         How many years of history to use for percentile
        cape_rolling_years: Rolling window for simplified CAPE
    """
    name: str
    ticker: str
    etf_ticker: str
    bond_yield_ticker: Optional[str] = None
    currency: str = "USD"
    country: str = "US"
    years_back: int = YEARS_BACK_DEFAULT
    cape_rolling_years: int = CAPE_ROLLING_YEARS_DEFAULT

    @property
    def cape_rolling_days(self) -> int:
        return self.cape_rolling_years * CAPE_ROLLING_DAYS_PER_YEAR

    @property
    def chart_filename(self) -> str:
        safe_name = self.name.replace(" ", "_").replace("&", "and")
        return f"{safe_name}_pe_valuation.png"
