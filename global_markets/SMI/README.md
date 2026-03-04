# SMI — Swiss Market Index — Valuation Analysis

Multi-factor valuation framework for the **Swiss Market Index** using EWL (iShares MSCI Switzerland) ETF data.

## Quick Start

```bash
cd global_markets/SMI
../../venv/Scripts/python.exe analyze.py
```

**Output**: Console report + `SMI_(Swiss_Market_Index)_pe_valuation.png` + `SMI_(Swiss_Market_Index)_report_{date}.md`

## Metrics Monitored

### 1. PE Percentile (10-Year)

| Zone | Percentile | Score |
|------|-----------|-------|
| Very Cheap | < 20th | +2 |
| Cheap | 20th–40th | +1 |
| Neutral | 40th–60th | 0 |
| Expensive | 60th–80th | −1 |
| Very Expensive | > 80th | −2 |

Uses EWL ETF's trailing PE from yfinance as a proxy for the SMI index PE.

### 2. Simplified CAPE Deviation

Percentage deviation of current PE from 3-year rolling average.

### 3. Equity Risk Premium (ERP)

Currently **not available** — Swiss 10Y bond yield is not set (`bond_yield_ticker=None`).

## Composite Signal

| Score | Signal |
|-------|--------|
| ≥ +4 | **STRONG BUY** |
| +2 to +3 | **BUY** |
| −1 to +1 | **NEUTRAL / HOLD** |
| −2 to −3 | **SELL** |
| ≤ −4 | **STRONG SELL** |

## Configuration

| Parameter | Value |
|-----------|-------|
| Index Ticker | `^SSMI` |
| ETF (PE data) | `EWL` |
| Bond Yield | None |
| Lookback | 10 years |
| CAPE Window | 3 years |

---

### VIX Fear Gauge (Contrarian Indicator)

| VIX Zone | Level | Hist. 12mo Return | Win Rate |
|----------|-------|--------------------|----------|
| EXTREME FEAR | > 40 | +52.3% avg | **100%** |
| HIGH FEAR | 30-40 | +28.9% avg | 83% |
| ELEVATED | 25-30 | +23.1% avg | 85% |

VIX measures 30-day implied volatility from S&P 500 options. Used as a global fear gauge for all equity markets. Spike-retreat thresholds are configurable in `common/config.py`. **Informational only -- not scored in composite.**

## References

- [Schroders -- VIX contrarian signal](https://www.schroders.com/en-us/us/individual/insights/what-the-vix-is-telling-us/)
- [CBOE -- VIX and forward returns](https://www.cboe.com/insights/posts/vix-the-fear-index-and-forward-looking-returns/)
- [Whaley (2000) -- "The Investor Fear Gauge"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=225153)
