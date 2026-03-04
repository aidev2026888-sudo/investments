# FX Valuation Monitor

Five-dimensional currency valuation framework that generates actionable buy/sell/hold signals for 9 major currencies.

## Dimensions

| # | Dimension | Interpretation | Source |
|---|-----------|---------------|--------|
| 1 | **REER** (Real Effective Exchange Rate) | How far the spring is compressed | BIS |
| 2 | **Relative Price Level** (REER/NEER) | PPP-equivalent — cheap or expensive vs peers | BIS |
| 3 | **Current Account** (% GDP) | Fundamental strength — organic capital flows | World Bank |
| 4 | **Real Interest Rate Differential** | Catalyst — what releases the spring | BIS + FRED |
| 5 | **Credit-to-GDP Gap** | Financial stability — clean balance sheet = resilience | BIS |

### Credit-to-GDP Gap (5th Dimension)

Measures how far total private-sector credit (% of GDP) deviates from its HP-filtered long-term trend. Adopted by the **Basel Committee** as the official guide for the countercyclical capital buffer.

| Gap Level | Assessment | FX Score | Meaning |
|-----------|-----------|----------|---------|
| > +10pp | Credit Boom (Danger) | -2 | Currency at risk of crisis-driven collapse |
| +2 to +10pp | Above Trend (Caution) | -1 | Overheating, watch closely |
| -2 to +2pp | Near Trend (Healthy) | 0 | Neutral |
| -10 to -2pp | Below Trend (Healing) | +1 | Financial system recovering |
| < -10pp | Deep Deleveraging | +2 | Clean balance sheets, room to expand |

**Reliability:** The credit-to-GDP gap has strong empirical backing. BIS research (Drehmann & Tsatsaronis, 2014) found it is the **single best early-warning indicator** for banking crises, with a signal horizon of 1-5 years before crises materialize. It outperforms other indicators because:
- HP-filtered trend removes cyclical noise
- Basel III formally adopted it (not just academic)
- Works across developed and emerging economies
- Limitation: it's a **necessary but not sufficient** condition — a positive gap doesn't guarantee a crisis, but most crises were preceded by one

## Quick Start

```bash
# From the repo root
python global_markets/FX/analyze.py
```

### FRED API Key (optional)

Add your key to `.env` in the repo root for 10Y government bond yields:

```
FRED_API_KEY=your_key_here
```

Without it the system falls back to BIS central bank policy rates — still fully functional.

## Data Sources

| Source | Datasets | API |
|--------|----------|-----|
| **BIS** (primary) | REER, NEER, CPI, Policy Rates, Credit-to-GDP Gap | `stats.bis.org/api/v1` (SDMX REST, no key) |
| **World Bank** | Current Account (% GDP) | `api.worldbank.org/v2` (REST, no key) |
| **FRED** (optional) | 10Y Bond Yields | `fredapi` (requires `FRED_API_KEY`) |

## Currency Coverage

| Currency | BIS Code | WB Code | FRED 10Y Series | Notes |
|----------|----------|---------|------------------|-------|
| USD | US | US | GS10 | Base currency for rate differentials |
| JPY | JP | JP | IRLTLT01JPM156N | |
| CHF | CH | CH | IRLTLT01CHM156N | |
| EUR | XM | EMU→DEU | IRLTLT01EZM156N | CA uses Germany as Eurozone proxy |
| CNY | CN | CN | — | Uses BIS policy rate (no FRED) |
| AUD | AU | AU | IRLTLT01AUM156N | |
| SGD | SG | SG | — | MAS uses NEER policy, no rate data |
| CAD | CA | CA | IRLTLT01CAM156N | |
| GBP | GB | GB | IRLTLT01GBM156N | |

## Output

### Console Report

Per-currency detail (REER z-score, percentile, relative price level, CA balance, real rate differential, credit gap) plus a compact summary table with composite signals.

### Charts

| File | Description |
|------|-------------|
| `{CCY}_valuation_dashboard.png` | 3×2 panel: REER, RPL, Current Account, Real Rate, Credit Gap, Credit Ratio vs Trend |
| `fx_valuation_heatmap.png` | Overview heatmap across all currencies and 5 dimensions |
| `FX_report_{date}.md` | Date-stamped markdown report with all metrics and signals |

## Module Structure

```
FX/
├── analyze.py          # Main entry point
├── fx_config.py        # Currency profiles & framework settings
├── fx_data_fetcher.py  # BIS / World Bank / FRED data retrieval
├── fx_metrics.py       # Z-scores, RPL deviation, credit gap, composite signal
├── fx_charting.py      # 3×2 dashboards & heatmap
├── fx_reporter.py      # Console reporting
└── __init__.py
```

## Configuration

Edit `fx_config.py` to:

- **Add/remove currencies** — define a `CurrencyProfile` with BIS, World Bank, and FRED codes
- **Change lookback period** — default is 25 years
- **Change base currency** — default is USD for rate differentials

## Signal Interpretation

The composite score combines all five dimensions:

| Score | Signal | Meaning |
|-------|--------|---------|
| ≥ +6 | **STRONG BUY** | Deeply undervalued with all catalysts aligned |
| +3 to +5 | **BUY** | Undervalued with catalyst support |
| +1 to +2 | **LEAN BULLISH** | Mildly favorable |
| -1 to +1 | **NEUTRAL** | Fair value or offsetting factors |
| -2 to -3 | **LEAN BEARISH** | Overvalued, some warning signs |
| ≤ -6 | **STRONG SELL** | Overvalued with structural headwinds |

A true **safety margin** exists when all four conditions align:
1. REER at extreme low (z < -1.5)
2. Current account healthy (surplus)
3. Real rate differential turning (catalyst emerging)
4. Credit gap negative (system deleveraged, room to expand)
