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

## Dimensions Details

### 1. Real Effective Exchange Rate (REER) Z-Score

| Zone | Z-Score | Score | Meaning |
|------|---------|-------|---------|
| Extremely Undervalued | < −2.0 | +3 | Compressing the spring deeply |
| Undervalued | −2.0 to −1.0 | +2 | High potential energy |
| Mildly Undervalued | −1.0 to −0.5 | +1 | Slight historical discount |
| Fair Value | −0.5 to +0.5 | 0 | Mean reversion |
| Mildly Overvalued | +0.5 to +1.0 | −1 | Slight premium |
| Overvalued | +1.0 to +2.0 | −2 | Stretched valuation |
| Extremely Overvalued | > +2.0 | −3 | Dangerously over-extended |

**What it measures**: REER compares a currency's value against a weighted basket of trading partners, adjusted for inflation. The Z-Score measures how many standard deviations the current REER is from its long-term (25-year) historical mean. 
**Interpretation**: Acts as our "structural valuation" or the "spring". Extreme deviations eventually revert.

---

### 2. Relative Price Level (PPP Proxy)

**What it measures**: Derived by dividing REER by NEER (Nominal Effective Exchange Rate). This serves as a proxy for Purchasing Power Parity (PPP), telling us whether a country's price levels are fundamentally cheap or expensive relative to its peers.
**Interpretation**: Used as an informational anchor (not scored separately) to provide context. If REER is cheap but RPL is highly expensive, the currency might simply be inflating away its nominal value.

---

### 3. Current Account (% GDP)

| Zone | Balance (% GDP) | Score | Meaning |
|------|-----------------|-------|---------|
| Very Strong Surplus | ≥ +6.0% | +2 | Massive organic capital inflow |
| Surplus | +2.0% to +6.0% | +1 | Healthy export/savings dynamic |
| Balanced | −2.0% to +2.0% | 0 | Neutral capital flows |
| Deficit | −4.0% to −2.0% | −1 | Reliant on external financing |
| Large Deficit | < −4.0% | −2 | Highly vulnerable to capital flight |

**What it measures**: The net trade balance plus net income from abroad, scaled to the size of the economy.
**Interpretation**: Represents fundamental, organic currency demand. A country running a large deficit must constantly attract foreign capital to prevent its currency from depreciating. A surplus country is fundamentally strong.

---

### 4. Real Interest Rate Differential

| Zone | Diff vs Base (pp) | Score | Meaning |
|------|-------------------|-------|---------|
| Strong Attraction | ≥ +2.0 pp | +2 | High real yield pulls capital strongly |
| Moderate Attraction | +1.0 to +2.0 pp | +1 | Favorable yield advantage |
| Neutral | −1.0 to +1.0 pp | 0 | Rates are effectively at parity |
| Capital Outflow | −2.0 to −1.0 pp | −1 | Investors seeking better yields elsewhere |
| Strong Outflow | < −2.0 pp | −2 | Deeply negative relative real yield |

**What it measures**: Subtracts domestic inflation from the 10-year government bond yield to find the *real* return, then compares it to the base currency (usually USD).
**Interpretation**: This is the **catalyst**. A currency can be fundamentally cheap (REER) for years, but the "spring" is only released when interest rate differentials shift in its favor, attracting hot money.

---

### 5. Credit-to-GDP Gap

| Gap Level | Assessment | Score | Meaning |
|-----------|-----------|----------|---------|
| > +10pp | Credit Boom (Danger) | -2 | Currency at risk of crisis-driven collapse |
| +2 to +10pp | Above Trend (Caution) | -1 | Overheating, watch closely |
| -2 to +2pp | Near Trend (Healthy) | 0 | Neutral |
| -10 to -2pp | Below Trend (Healing) | +1 | Financial system recovering |
| < -10pp | Deep Deleveraging | +2 | Clean balance sheets, room to expand |

**What it measures**: How far total private-sector credit (% of GDP) deviates from its HP-filtered long-term trend. Adopted by the **Basel Committee**.
**Interpretation**: Financial stability. A large positive gap (credit boom) strongly predicts banking crises 1-5 years out, which inevitably crush the currency. A negative gap implies a clean balance sheet capable of supporting future growth.



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
