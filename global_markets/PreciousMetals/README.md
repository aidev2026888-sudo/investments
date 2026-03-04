# Precious Metals — Valuation Analysis

Multi-factor valuation framework for **Gold** and **Silver**, combining macro signals, miner fundamentals, price history, and market structure into actionable composite signals.

## Quick Start

```bash
# Requires Python 3.10+ with venv at repo root
cd global_markets/PreciousMetals
../../venv/Scripts/python.exe analyze.py

# For full accuracy, set FRED API key in .env:
#   FRED_API_KEY=your_key_here
```

**Output**: Console report + `Gold_valuation.png` + `Silver_valuation.png` + `Gold_report_{date}.md` + `Silver_report_{date}.md`

---

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

**Data source**: [FRED DFII10](https://fred.stlouisfed.org/series/DFII10) (primary) · yfinance `^TNX` minus breakeven estimate (fallback)

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

**Data source**: yfinance `priceToBook`, `operatingMargins`

**Limitation**: P/B is a lagging indicator (based on reported book value). Miners with write-downs or acquisition goodwill may have distorted book values. Operating margins provide a cross-check.

**Reference**: [Howard Marks — "The Most Important Thing"](https://www.oaktreecapital.com/) (cyclical margin of safety) · [World Gold Council — Gold Mining Costs](https://www.gold.org/goldhub/data/gold-costs)

---

### 3. Gold/GDX Ratio (Gold only)

**What it measures**: The ratio of gold's spot price to the GDX (VanEck Gold Miners ETF) price. When this ratio is high, gold is outperforming miners — suggesting margin pressure or operational struggles. When low, miners are leveraging gold's rise effectively.

**Data source**: yfinance `GC=F` / `GDX`

**Limitation**: Purely directional. GDX includes a basket of miners with varying exposure to gold vs. other metals. Not scored in the composite signal — used as supplementary context.

---

### 4. Price Percentile (10-Year)

| Zone | Percentile | Score | Meaning |
|------|-----------|-------|---------|
| Historically Cheap | < 40th | +1 | Price in the lower range of 10-year history |
| Mid-Range | 40th–80th | 0 | Normal |
| Historically Expensive | > 80th | −1 | Price in the upper quintile |

**What it measures**: Where the current price sits within its 10-year distribution. Provides context for whether the price is high or low relative to its own history.

**Data source**: yfinance `GC=F` (gold) / `SI=F` (silver), 10+ years of daily close prices

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

**Data source**: Computed from `GC=F` / `SI=F` spot prices

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

**Data sources**: yfinance `SLV` (inventory proxy) · [CFTC Commitments of Traders](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) (open interest, updated weekly on Fridays)

**Limitation**: SLV total assets is a rough proxy — it reflects one ETF, not total global inventory. CFTC data is weekly and lags by several days. The coverage ratio is **informational only** (not part of the composite scoring) because it is a short-term tactical indicator, not a valuation metric.

**Reference**: [CFTC COT Reports](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) · [Silver Institute — Supply & Demand](https://www.silverinstitute.org/silver-supply-demand/)

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

### Silver (4-Factor)

Same score → signal mapping as gold.

Factors: Real Yield + GSR + Miner P/B + Price Percentile

> **Note**: The COMEX coverage ratio is deliberately excluded from composite scoring. It is a tactical/monitoring metric displayed in the report for situational awareness.

---

## Output Files

| File | Description |
|------|-------------|
| `Gold_valuation.png` | Price history with percentile bands + real yield overlay |
| `Silver_valuation.png` | Price history with percentile bands + GSR overlay |

---

## Report Example

```
============================================================
  [GOLD]  Precious Metals (Gold)  --  Valuation Report
============================================================
  Gold Spot Price:      $5,163.10 /oz
  Miner Avg P/B:        2.98  (ELEVATED)
  Gold/GDX Ratio:       49.1
  Price Percentile (10yr): 99.7%
============================================================

  [REAL YIELD] US 10-Year TIPS Real Yield Analysis:
    Real Yield:     +1.76%
    Zone:           HEADWIND
    Interpretation: Real yield +1.76% -- moderate headwind for gold

    Logic: Gold has no yield. Its opportunity cost = real interest rate.
    [i] Real yield > 0%: positive real rates -> mild headwind for gold
============================================================

  [SAFETY MARGIN] Miner P/B -- Dynamic AISC Proxy:
    [NEM] P/B=3.81, OpMargin=58.3%, BookValue=$31.11
    [GOLD] P/B=2.15, OpMargin=0.4%, BookValue=$26.26
    --------
    Average: P/B=2.98  Zone: ELEVATED
    Gold miners P/B=2.98, OpMargin=29.3% -- high profitability;
    price well above AISC; limited safety margin

    Logic: When miner P/B < 1.0, mines are valued below book value
    -> gold price is near/below industry AISC -> maximum safety margin.
    When P/B > 4.0, extreme profitability -> no safety margin.

    Gold/GDX Ratio: 49.1
    (High ratio = gold outperforming miners = margin pressure)
============================================================

  [PERCENTILE] 10-Year Price Distribution:
     80th pctl = $2,105.38
     60th pctl = $1,840.44
     40th pctl = $1,598.46
     20th pctl = $1,285.54
  [!] Price is in the TOP 20% of 10-year range -- historically expensive
============================================================

  [SIGNAL] Composite Signal (Multi-Factor Model):
    Signal:     << SELL >>  (Score: -3, Confidence: 3/4)
    Factors:
      - Real Yield +1.76% (High -- headwind)
      - Miner P/B 2.98 (Limited Safety -- high profitability)
      - Price Percentile 100% (Historically Expensive)
============================================================

============================================================
  [SILVER]  Precious Metals (Silver)  --  Valuation Report
============================================================
  Silver Spot Price:    $83.79 /oz
  Gold Spot Price:      $5,163.10 /oz
  Gold/Silver Ratio:    61.6
  Silver Miner P/B:     4.38  (NO SAFETY MARGIN)
  Price Percentile (10yr): 99.2%
============================================================

  [GSR] Gold/Silver Ratio Analysis:
    Current GSR:    61.6
    Zone:           NORMAL
    GSR 61.6 -- silver at fair value relative to gold

    Logic: Historical GSR avg ~60-70. High GSR = silver cheap vs gold.
    [i] GSR in normal range
============================================================

  [SAFETY MARGIN] Silver Miner P/B -- Dynamic AISC Proxy:
    [AG] P/B=5.05, OpMargin=49.0%
    [PAAS] P/B=3.71, OpMargin=34.9%
    --------
    Average: P/B=4.38  Zone: NO SAFETY MARGIN
    Silver miners P/B=4.38, OpMargin=41.9% -- extreme profitability;
    price far above AISC; no safety margin
============================================================

  [INVENTORY] COMEX / Visible Silver Inventory:
    Source: SLV ETF (iShares Silver Trust)
    Status: COVERAGE COMFORTABLE
    SLV holds $51.5B in silver assets | Coverage ratio: 97.9%
    (COMFORTABLE) — 614,379,728 oz inventory vs 627,270,000 oz
    open interest

    [SQUEEZE RISK] Coverage Ratio: 97.9%
    [OK] Comfortable inventory coverage
============================================================

  [PERCENTILE] 10-Year Price Distribution:
     80th pctl = $27.46
     60th pctl = $23.37
     40th pctl = $18.30
     20th pctl = $16.52
  [!] Price is in TOP 20% of 10-year range
============================================================

  [SIGNAL] Composite Signal (Multi-Factor Model):
    Signal:     <<< STRONG SELL >>>  (Score: -4, Confidence: 4/5)
    Factors:
      - Real Yield +1.76% (High -- headwind)
      - GSR 61.6 (Normal range)
      - Miner P/B 4.38 (No Safety Margin)
      - Price Percentile 99% (Historically Expensive)
============================================================
```

---

## Architecture

```
PreciousMetals/
├── analyze.py                # Entry point — orchestrates gold + silver analysis
└── (outputs: Gold_valuation.png, Silver_valuation.png)

common/
├── gold_data_fetcher.py      # Data layer — yfinance, FRED, CFTC
├── gold_metrics.py           # Signal computation — zones, scores, classifications
├── gold_signals.py           # Composite signal — multi-factor scoring model
├── gold_reporter.py          # Console report formatting
└── gold_charting.py          # Chart generation (matplotlib)
```

## Dependencies

- `yfinance` — price data, miner fundamentals, SLV ETF
- `fredapi` — US 10Y TIPS real yield (requires free API key)
- `matplotlib` — chart generation
- `pandas` / `numpy` — data processing
- `requests` — CFTC COT report download
- `python-dotenv` — `.env` file loading
