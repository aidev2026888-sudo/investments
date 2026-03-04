# S&P 500 — Valuation Analysis

Multi-factor valuation framework for the **S&P 500 Index** using SPY ETF data.

## Quick Start

```bash
cd global_markets/SP500
../../venv/Scripts/python.exe analyze.py
```

**Output**: Console report + `Sand_P_500_pe_valuation.png` + `Sand_P_500_report_{date}.md`

## Metrics Monitored

### 1. PE Percentile (10-Year)

| Zone | Percentile | Score |
|------|-----------|-------|
| Very Cheap | < 20th | +2 |
| Cheap | 20th–40th | +1 |
| Neutral | 40th–60th | 0 |
| Expensive | 60th–80th | −1 |
| Very Expensive | > 80th | −2 |

**What it measures**: Where the current trailing PE sits within its 10-year distribution. Uses SPY ETF's `trailingPE` from yfinance.

**Limitation**: PE based on trailing 12-month earnings. During earnings recessions, PE can spike mechanically (lower E → higher PE) creating false "expensive" signals. Forward PE is displayed when available but not scored.

**Reference**: [Shiller — Irrational Exuberance](http://www.econ.yale.edu/~shiller/data.htm)

---

### 2. Simplified CAPE Deviation

| Zone | Deviation | Score |
|------|----------|-------|
| Undervalued | < −15% | +1 |
| Normal | −15% to +15% | 0 |
| Overvalued | > +15% | −1 |

**What it measures**: Percentage deviation of current PE from its 3-year rolling average. This is a simplified version of the Shiller CAPE that smooths cyclical earnings noise. When the current PE is far above its rolling average, it signals short-term overheating.

**Limitation**: Only uses 3 years (vs Shiller's 10yr inflation-adjusted). Less robust for identifying secular over/undervaluation, but more responsive to regime changes.

**Reference**: [Robert Shiller — CAPE Ratio](https://www.multpl.com/shiller-pe)

---

### 3. Equity Risk Premium (ERP)

| Zone | ERP | Score |
|------|-----|-------|
| Very Attractive | > 6% | +2 |
| Attractive | 3–6% | +1 |
| Neutral | 0–3% | 0 |
| Expensive | < 0% | −1 |

**What it measures**: ERP = Earnings Yield (1/PE) − 10Y Bond Yield. Compares equity returns to the risk-free rate. When ERP is high, equities are cheap relative to bonds; when negative, bonds are more attractive.

**Data source**: PE from SPY, 10Y yield from yfinance `^TNX`

**Limitation**: Assumes earnings yield ≈ expected equity returns, which is a simplification. Does not account for earnings growth expectations. Available only for S&P 500 (where `^TNX` bond yield is used).

**Reference**: [Damodaran — Equity Risk Premiums](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html)

---

### 4. Buffett Indicator (when available)

| Zone | Ratio | Meaning |
|------|-------|---------|
| Undervalued | < 100% | Market cap below GDP |
| Moderate | 100–150% | Slightly to moderately overvalued |
| Overvalued | > 150% | Significantly overvalued |

**What it measures**: Total stock market capitalization / GDP. Warren Buffett called it "probably the best single measure of where valuations stand." Not always available programmatically.

**Limitation**: Globalization distorts the indicator — multinational companies earning abroad inflate market cap relative to domestic GDP.

**Reference**: [Buffett Indicator — currentmarketvaluation.com](https://www.currentmarketvaluation.com/models/buffett-indicator.php)

---

## Composite Signal

| Score | Signal |
|-------|--------|
| ≥ +4 | **STRONG BUY** |
| +2 to +3 | **BUY** |
| −1 to +1 | **NEUTRAL / HOLD** |
| −2 to −3 | **SELL** |
| ≤ −4 | **STRONG SELL** |

Factors: PE Percentile + CAPE Deviation + ERP

## Configuration

| Parameter | Value |
|-----------|-------|
| Index Ticker | `^GSPC` |
| ETF (PE data) | `SPY` |
| Bond Yield | `^TNX` (US 10Y) |
| Lookback | 10 years |
| CAPE Window | 3 years |

---

### 4. VIX Fear Gauge (Contrarian Indicator)

| VIX Zone | Level | Historical 12mo Return | Win Rate |
|----------|-------|----------------------|----------|
| EXTREME FEAR | > 40 | +52.3% avg | **100%** |
| HIGH FEAR | 30-40 | +28.9% avg | 83% |
| ELEVATED | 25-30 | +23.1% avg | 85% |
| NORMAL | 15-25 | Baseline | - |
| COMPLACENT | < 15 | Below average | - |

**What it measures**: The CBOE Volatility Index (VIX) measures 30-day implied volatility from S&P 500 options. Used as a contrarian "fear gauge" -- extreme fear historically marks market bottoms.

**Spike-Then-Retreat Signal**: When VIX surges rapidly (>50% in 20 trading days) and then drops back (>20% from peak), this signals fear has peaked and is subsiding. Historically avg +16% 12mo return, 85% win rate.

**Configurable thresholds** (in `common/config.py`):
- `VIX_SPIKE_SURGE_PCT = 50` (surge threshold %)
- `VIX_SPIKE_RETREAT_PCT = 20` (retreat threshold %)
- `VIX_SPIKE_MIN_PEAK = 25` (minimum peak to qualify)
- `VIX_LOOKBACK_DAYS = 20` (rolling window in trading days)

**Limitation**: VIX is informational only, **not scored in the composite signal**. High VIX doesn't guarantee a bottom -- markets can stay volatile for extended periods. The signal works best when combined with valuation metrics (PE, CAPE).

**References**:
- [Schroders -- VIX as contrarian buy signal](https://www.schroders.com/en-us/us/individual/insights/what-the-vix-is-telling-us/) -- VIX >32.9 yields avg +25% 12mo return
- [CBOE -- VIX and forward returns](https://www.cboe.com/insights/posts/vix-the-fear-index-and-forward-looking-returns/) -- VIX >30 yields avg +23% 12mo, >40 yields +33%
- [UBS -- VIX levels and equity returns](https://www.ubs.com/global/en/wealth-management/insights/) -- VIX >40 yields avg +30% with 95% gain probability
- [Whaley (2000) -- "The Investor Fear Gauge"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=225153) -- Original academic paper establishing VIX as a fear measure

## Dependencies

`yfinance`, `pandas`, `numpy`, `scipy`, `matplotlib`
