"""
Configuration for the five-dimensional currency valuation framework.

Monitors: REER, Relative Price Level (BIS PPP), Current Account,
          Real Interest Rate Differentials, Credit-to-GDP Gap.

All lists and parameters here are designed to be easily modified.
"""

from dataclasses import dataclass, field
from typing import Dict, List


# ==========================================
# Configurable Parameters
# ==========================================

YEARS_BACK_DEFAULT = 25  # Default lookback period (years)

# Reference currency for interest-rate differentials
BASE_CURRENCY = "USD"


@dataclass
class CurrencyProfile:
    """Configuration for a single currency in the framework."""

    code: str               # ISO currency code, e.g. "USD"
    name: str               # Human-readable name, e.g. "US Dollar"
    country_name: str       # Country / area name for reports

    # --- World Bank codes (for Current Account) ---
    wb_country: str         # 2-letter WB code, e.g. "US", "JP", "CH"

    # --- BIS codes ---
    bis_country: str        # BIS code for REER/NEER, e.g. "US", "JP", "XM"
    bis_credit_country: str = ""  # BIS code for WS_CREDIT_GAP (usually same as bis_country)

    # --- FRED series IDs (for nominal 10Y bond yield & CPI) ---
    fred_nominal_rate: str = ""  # e.g. "GS10" (US 10Y)
    fred_cpi: str = ""           # e.g. "CPIAUCSL" (US CPI)

    # --- BIS series IDs (alternative to FRED) ---
    bis_policy_rate_key: str = ""  # e.g. "US" for WS_CBPOL
    bis_cpi_key: str = ""          # e.g. "US" for WS_LONG_CPI


# ==========================================
# Default Currency List
# ==========================================

DEFAULT_CURRENCIES: List[CurrencyProfile] = [
    CurrencyProfile(
        code="USD", name="US Dollar", country_name="United States",
        wb_country="US", bis_country="US", bis_credit_country="US",
        fred_nominal_rate="GS10", fred_cpi="CPIAUCSL",
        bis_policy_rate_key="US", bis_cpi_key="US",
    ),
    CurrencyProfile(
        code="JPY", name="Japanese Yen", country_name="Japan",
        wb_country="JP", bis_country="JP", bis_credit_country="JP",
        fred_nominal_rate="IRLTLT01JPM156N", fred_cpi="CPALTT01JPM657N",
        bis_policy_rate_key="JP", bis_cpi_key="JP",
    ),
    CurrencyProfile(
        code="CHF", name="Swiss Franc", country_name="Switzerland",
        wb_country="CH", bis_country="CH", bis_credit_country="CH",
        fred_nominal_rate="IRLTLT01CHM156N", fred_cpi="CPALTT01CHM657N",
        bis_policy_rate_key="CH", bis_cpi_key="CH",
    ),
    CurrencyProfile(
        code="EUR", name="Euro", country_name="Euro Area",
        wb_country="EMU", bis_country="XM", bis_credit_country="XM",
        fred_nominal_rate="IRLTLT01EZM156N", fred_cpi="CPALTT01EZM657N",
        bis_policy_rate_key="XM", bis_cpi_key="XM",
    ),
    CurrencyProfile(
        code="CNY", name="Chinese Yuan", country_name="China",
        wb_country="CN", bis_country="CN", bis_credit_country="CN",
        fred_nominal_rate="", fred_cpi="",
        bis_policy_rate_key="CN", bis_cpi_key="CN",
    ),
    CurrencyProfile(
        code="AUD", name="Australian Dollar", country_name="Australia",
        wb_country="AU", bis_country="AU", bis_credit_country="AU",
        fred_nominal_rate="IRLTLT01AUM156N", fred_cpi="CPALTT01AUM657N",
        bis_policy_rate_key="AU", bis_cpi_key="AU",
    ),
    CurrencyProfile(
        code="SGD", name="Singapore Dollar", country_name="Singapore",
        wb_country="SG", bis_country="SG", bis_credit_country="SG",
        fred_nominal_rate="", fred_cpi="",
        bis_policy_rate_key="SG", bis_cpi_key="SG",
    ),
    CurrencyProfile(
        code="CAD", name="Canadian Dollar", country_name="Canada",
        wb_country="CA", bis_country="CA", bis_credit_country="CA",
        fred_nominal_rate="IRLTLT01CAM156N", fred_cpi="CPALTT01CAM657N",
        bis_policy_rate_key="CA", bis_cpi_key="CA",
    ),
    CurrencyProfile(
        code="GBP", name="British Pound", country_name="United Kingdom",
        wb_country="GB", bis_country="GB", bis_credit_country="GB",
        fred_nominal_rate="IRLTLT01GBM156N", fred_cpi="CPALTT01GBM657N",
        bis_policy_rate_key="GB", bis_cpi_key="GB",
    ),
]


# ==========================================
# Global Framework Configuration
# ==========================================

@dataclass
class FXFrameworkConfig:
    """Top-level configuration for the FX valuation framework."""

    currencies: List[CurrencyProfile] = field(default_factory=lambda: list(DEFAULT_CURRENCIES))
    years_back: int = YEARS_BACK_DEFAULT
    base_currency: str = BASE_CURRENCY

    @property
    def start_year(self) -> int:
        from datetime import datetime
        return datetime.now().year - self.years_back

    @property
    def currency_codes(self) -> List[str]:
        return [c.code for c in self.currencies]

    def get_profile(self, code: str) -> CurrencyProfile:
        for c in self.currencies:
            if c.code == code:
                return c
        raise ValueError(f"Currency '{code}' not in configuration")
