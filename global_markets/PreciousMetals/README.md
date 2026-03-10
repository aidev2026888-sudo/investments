# Precious Metals — Valuation Analysis

Multi-factor valuation framework for **Gold** and **Silver**, combining macro signals, miner fundamentals, price history, and market structure into actionable composite signals.


## Metrics Monitored

### 1. US 10-Year Real Yield (TIPS)

| Zone | Real Yield | Score | Meaning |
|------|-----------|-------|---------|
| STRONG BUY | < −1% | +2 | Cash/bonds lose purchasing power → gold is best store of value |
| TAILWIND | −1% to 0% | +1 | Gold becomes attractive |
| NEUTRAL | 0% to 1% | 0 | Mild headwind |
| HEADWIND | 1% to 2% | −1 | Moderate opportunity cost |
| BEARISH | > 2% | −2 | High opportunity cost → bearish for gold |

**What it measures**: Gold has no yield. Its opportunity cost is the real (inflation-adjusted) interest rate. When real yields are negative, holding cash or bonds destroys purchasing power, making gold the superior asset.

**Limitation**: TIPS real yield reflects *market expectations*, not guaranteed real returns. During periods of financial repression, the TIPS rate itself can be distorted by central bank purchases.

**Reference**: [Erb & Harvey (2013) — "The Golden Dilemma"](https://doi.org/10.2469/faj.v69.n4.1) · [World Gold Council — Gold and interest rates](https://www.gold.org/goldhub/research/relevance-of-gold-as-a-strategic-asset)

---

### 2. Dynamic Safety Margin (Miner P/B Ratio)

| Zone | Avg P/B | Score | Meaning |
|------|---------|-------|---------|
| MAX SAFETY | < 1.0 | +2 | Mines valued below book → price near/below AISC |
| STRONG SAFETY | 1.0–1.5 | +1 | Near production cost → strong margin of safety |
| MODERATE | 1.5–2.5 | 0 | Normal profitability |
| ELEVATED | 2.5–4.0 | −1 | High profitability → limited safety |
| NO SAFETY MARGIN | > 4.0 | −2 | Extreme profitability → price far above AISC |

**What it measures**: Uses the Price-to-Book ratio of major miners as a **dynamic proxy for All-In Sustaining Cost (AISC)**. When miners trade below book value (P/B < 1.0), the market is pricing gold near or below production cost — the point of maximum safety margin.

**Tickers**: Gold — `NEM` (Newmont), `GOLD` (Barrick) · Silver — `AG` (First Majestic), `PAAS` (Pan American)

**Limitation**: P/B is a lagging indicator (based on reported book value). Miners with write-downs or acquisition goodwill may have distorted book values. Operating margins provide a cross-check.

**Reference**: [Howard Marks — "The Most Important Thing"](https://www.oaktreecapital.com/) (cyclical margin of safety) · [World Gold Council — Gold Mining Costs](https://www.gold.org/goldhub/data/gold-costs)

---

### 3. Gold/GDX Ratio (Gold only)

**What it measures**: The ratio of gold's spot price to the GDX (VanEck Gold Miners ETF) price. When this ratio is high, gold is outperforming miners — suggesting margin pressure or operational struggles. When low, miners are leveraging gold's rise effectively.

**Limitation**: Purely directional. GDX includes a basket of miners with varying exposure to gold vs. other metals. Not scored in the composite signal — used as supplementary context.

---

### 4. Price Percentile (10-Year)

| Zone | Percentile | Score | Meaning |
|------|-----------|-------|---------|
| Historically Cheap | < 40th | +1 | Price in the lower range of 10-year history |
| Mid-Range | 40th–80th | 0 | Normal |
| Historically Expensive | > 80th | −1 | Price in the upper quintile |

**What it measures**: Where the current price sits within its 10-year distribution. Provides context for whether the price is high or low relative to its own history.

**Limitation**: Precious metals can remain in "expensive" percentiles for extended periods during secular bull markets. A high percentile does not imply an imminent reversal. Additionally, reference percentile values (80th, 60th, 40th, 20th) are reported for context.

---

### 5. Gold/Silver Ratio — GSR (Silver only)

| Zone | GSR | Score | Meaning |
|------|-----|-------|---------|
| EXTREME DISCOUNT | > 90 | +2 | Silver very cheap relative to gold |
| CHEAP | 80–90 | +1 | Silver undervalued vs gold |
| NORMAL | 60–80 | 0 | Fair value range |
| EXPENSIVE | 50–60 | −1 | Silver rich vs gold |
| EXTREME PREMIUM | < 50 | −2 | Silver overvalued, caution |

**What it measures**: How many ounces of silver it takes to buy one ounce of gold. Historical average is ~60–70. GSR is the single most important silver-specific relative valuation indicator.

**Limitation**: The "correct" long-term average for GSR is debatable and has shifted over different eras. Industrial demand changes (e.g., solar panel growth) can structurally alter the ratio.

**Reference**: [LBMA — Gold/Silver Ratio](https://www.lbma.org.uk/prices-and-data) · [CPM Group Silver Yearbook](https://www.cpmgroup.com/)

---

### 6. COMEX Inventory & Coverage Ratio (Silver only)

| Coverage | Zone | Meaning |
|----------|------|---------|
| < 20% | **CRITICAL** | Extreme squeeze risk (Jan 2026 crash was ~14%) |
| 20–40% | **TIGHT** | Elevated risk — monitor closely |
| 40–70% | **ADEQUATE** | Normal range |
| > 70% | **COMFORTABLE** | Low squeeze risk |

**What it measures**: Two components:
1. **SLV ETF Total Assets** — proxy for visible silver inventory (estimated ounces = total assets ÷ silver spot price)
2. **COMEX Open Interest** — total outstanding futures contracts (from CFTC COT report), converted to ounces (× 5,000 oz/contract)

The **coverage ratio** = estimated inventory ÷ open interest. When inventory can cover only a small fraction of outstanding contracts, squeeze risk is elevated. The January 2026 precious metals crash was preceded by a coverage ratio of approximately 14%.

**Data sources**: Visible ETF inventory · [CFTC Commitments of Traders](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) (open interest)

**Limitation**: SLV total assets is a rough proxy — it reflects one ETF, not total global inventory. CFTC data is weekly and lags by several days. The coverage ratio is **informational only** (not part of the composite scoring) because it is a short-term tactical indicator, not a valuation metric.

**Reference**: [CFTC COT Reports](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) · [Silver Institute — Supply & Demand](https://www.silverinstitute.org/silver-supply-demand/)

---

### 7. SHFE Silver Premium (China Demand Proxy)

| Zone | Premium | Score | Meaning |
|------|---------|-------|---------|
| STRONG BULLISH | > 10% | +2 | Acute physical silver shortage in China |
| BULLISH | 5–10% | +1 | Strong Chinese industrial demand |
| NEUTRAL | 0–5% | 0 | Normal baseline physical demand |
| BEARISH | < 0% | −1 | Weak regional physical demand |

**What it measures**: The premium of the active silver futures contract on the Shanghai Futures Exchange (SHFE) or SGE Ag(T+D) over the London/COMEX spot price. Because China is a massive driver of industrial silver demand (especially for solar photovoltaics), a sustained, structural premium in Shanghai indicates tight local supply and robust industrial off-take that is front-running western financial markets.

**Data sources**: Shanghai Futures Exchange (SHFE) / Shanghai Gold Exchange (SGE).

**Limitation**: Chinese exchange data can be opaque or delayed compared to western financial reporting. Local physical premiums can occasionally detach from global spot prices during periods of extreme domestic speculation.

**Reference**: [Bloomberg — China's Premium on Gold and Silver](https://www.bloomberg.com/news/articles/2024-05-24/silver-surges-in-china-as-retail-investors-dive-into-haven-asset)

---

## Composite Signal Model

### Gold (3-Factor)

| Score Range | Signal |
|-------------|--------|
| ≥ +4 | **STRONG BUY** |
| +2 to +3 | **BUY** |
| −1 to +1 | **NEUTRAL / HOLD** |
| −3 to −2 | **SELL** |
| ≤ −4 | **STRONG SELL** |

Factors: Real Yield + Miner P/B + Price Percentile

### Silver (5-Factor)

Same score → signal mapping as gold.

Factors: Real Yield + GSR + Miner P/B + Price Percentile + SHFE Premium

> **Note**: The COMEX coverage ratio is deliberately excluded from composite scoring. It is a tactical/monitoring metric displayed in the report for situational awareness.

