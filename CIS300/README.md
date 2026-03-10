# CSI 300 (沪深300) — Valuation Analysis

Multi-factor valuation framework for the **CSI 300 Index** (沪深300), China's benchmark equity index tracking the 300 largest A-share stocks listed on the Shanghai and Shenzhen exchanges.

## Metrics Monitored

### 1. PE Percentile (15-Year)

| Zone | Percentile | Score | Interpretation |
|------|-----------|-------|---------------|
| Very Cheap | < 20th | +2 | Deep value territory — historically bottoms |
| Cheap | 20th–40th | +1 | Below-average valuation — accumulation zone |
| Neutral | 40th–60th | 0 | Fair value by historical standards |
| Expensive | 60th–80th | −1 | Above-average — reduce exposure |
| Very Expensive | > 80th | −2 | Historical tops — high caution |

**What it measures**: Where the current trailing PE-TTM sits within its 15-year distribution. Sources data from the LiGe platform (理杏仁), the most widely-used valuation data provider for Chinese markets.

**Why 15 years**: The CSI 300 was launched in 2005. Using 15 years captures multiple full market cycles including the 2015 bubble/crash, 2018 trade war drawdown, and 2020–2021 recovery, giving robust percentile context.

**China-specific nuance**: Chinese equity markets tend to have higher volatility than developed markets (the CSI 300's PE range spans roughly 8x to 60x vs S&P 500's 12x to 35x), making percentile-based analysis more appropriate than fixed thresholds.

**Reference**: [LiGe PE-TTM Data](https://www.lixinger.com/) — Standard source for Chinese index PE data

---

### 2. Simplified CAPE Deviation

| Zone | Deviation from 3-Year Average | Score |
|------|------------------------------|-------|
| Undervalued | < −15% | +1 |
| Normal | −15% to +15% | 0 |
| Overvalued | > +15% | −1 |

**What it measures**: How much the current PE-TTM deviates from its 3-year rolling average, serving as a simplified cyclically-adjusted PE (CAPE). When the current PE significantly overshoots its rolling average, it often signals short-term overheating driven by speculative sentiment (particularly relevant in Chinese markets).

**Why this matters for China**: The A-share market is retail-dominated (~80% of daily turnover), which creates larger sentiment-driven deviations. Periods where PE spikes 15%+ above the 3-year average have historically preceded corrections (2015 peak, January 2018 peak).

**Limitation**: Only a 3-year window (vs Shiller's 10-year). This makes it more responsive to regime changes but less robust for identifying secular trends.

---

### 3. Equity Risk Premium (ERP)

| Zone | ERP | Score |
|------|-----|-------|
| Very Attractive | > 6% | +2 |
| Attractive | 3–6% | +1 |
| Neutral | 0–3% | 0 |
| Expensive | < 0% | −1 |

**What it measures**: ERP = Earnings Yield (1/PE) − 10Y Government Bond Yield. Compares what equities "pay" in earnings to the risk-free rate offered by Chinese government bonds.

**China-specific context**: China's 10-year government bond yield (sourced from ChinaBond) typically ranges 2.5%–4.0%. An ERP above 6% signals equities are extremely cheap relative to bonds — historically these entry points have delivered excellent 12-month forward returns.

**Limitation**: China's government bond market dynamics differ from developed markets. The PBoC's monetary policy transmission is less direct, and the bond yield may not fully reflect market-determined risk-free rates due to capital controls and state bank participation.

---

## Composite Signal

| Score | Signal | Chinese |
|-------|--------|---------|
| ≥ +4 | **STRONG BUY** | 强烈买入 |
| +2 to +3 | **BUY** | 买入 |
| −1 to +1 | **NEUTRAL / HOLD** | 持有 / 观望 |
| −2 to −3 | **SELL** | 卖出 |
| ≤ −4 | **STRONG SELL** | 强烈卖出 |

Factors: PE Percentile + CAPE Deviation + ERP

## Limitations & Caveats

- **Data quality**: Chinese financial data availability and consistency is generally lower than developed markets. Valuation data may have occasional gaps.
- **Policy sensitivity**: A-share markets are heavily influenced by government policy (CSRC, PBoC, NDRC). Regulatory changes can override valuation signals.
- **Capital controls**: The RMB is not fully convertible, which means foreign investors face additional constraints beyond what valuation signals suggest.
- **Sector composition**: The CSI 300 is heavily weighted toward financials, consumer staples, and technology — different from many global indices.
