# DAX (Germany) — Valuation Analysis

Multi-factor valuation framework for the **DAX Index** using EWG (iShares MSCI Germany) ETF data.

## Quick Start

```bash
cd global_markets/DAX
../../venv/Scripts/python.exe analyze.py
```

**Output**: Console report + `DAX_pe_valuation.png` + `DAX_report_{date}.md`

## Metrics Monitored

### 1. PE Percentile (10-Year)

| Zone | Percentile | Score |
|------|-----------|-------|
| Very Cheap | < 20th | +2 |
| Cheap | 20th–40th | +1 |
| Neutral | 40th–60th | 0 |
| Expensive | 60th–80th | −1 |
| Very Expensive | > 80th | −2 |

Uses EWG ETF's trailing PE from yfinance as a proxy for the DAX index PE.

### 2. Simplified CAPE Deviation

Percentage deviation of current PE from 3-year rolling average. Signals short-term overheating (> +15%) or undervaluation (< −15%).

### 3. Equity Risk Premium (ERP)

ERP = Earnings Yield (1/PE) − 10Y Bond Yield. Currently **not available** for DAX — German 10Y Bund yield (`bond_yield_ticker`) is set to `None` since it's not easily accessible via yfinance.

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
| Index Ticker | `^GDAXI` |
| ETF (PE data) | `EWG` |
| Bond Yield | None (German 10Y Bund not available) |
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

- [Shiller -- CAPE Ratio](https://www.multpl.com/shiller-pe)
- [Damodaran -- Equity Risk Premiums](https://pages.stern.nyu.edu/~adamodar/)
- [Schroders -- VIX contrarian signal](https://www.schroders.com/en-us/us/individual/insights/what-the-vix-is-telling-us/)
- [CBOE -- VIX and forward returns](https://www.cboe.com/insights/posts/vix-the-fear-index-and-forward-looking-returns/)
- [Whaley (2000) -- "The Investor Fear Gauge"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=225153)
