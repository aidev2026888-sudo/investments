# 📊 Global Markets Monitor

**Quantitative multi-factor valuation dashboard** for equities, precious metals, and currencies—automated daily scoring across 8+ assets.

> Built with Python (analysis) + Next.js (dashboard), deployable to Azure.

---

## Dashboard Preview

| Feature | Description |
|---------|-------------|
| **Bento grid layout** | Hero, wide, tall, and normal cards with per-asset gradient accents |
| **Live signals** | Buy / Sell / Hold with composite scores |
| **Interactive charts** | Click-to-expand lightbox with Stripe-style bento expand icon |
| **Run from UI** | ▶ Run Analysis button triggers individual asset analyzers |
| **Methodology** | In-app financial explanations (technical setup filtered out) |
| **Signal history** | Track how signals change over time |

---

## Assets Monitored

### Equities
| Asset | Dimensions | Data Source |
|-------|-----------|-------------|
| **S&P 500** | PE Percentile, CAPE, ERP, VIX, Buffett Indicator | yfinance, FRED |
| **DAX 40** | PE Percentile, CAPE, ERP | yfinance |
| **CAC 40** | PE Percentile, CAPE, ERP | yfinance |
| **FTSE 100** | PE Percentile, CAPE, ERP | yfinance |
| **SMI** | PE Percentile, CAPE, ERP | yfinance |

### Precious Metals
| Asset | Dimensions | Data Source |
|-------|-----------|-------------|
| **Gold** | Real price, Gold/Silver ratio, Safety margin, Miner P/B | yfinance, FRED |
| **Silver** | Real price, Gold/Silver ratio, Safety margin, Miner margins | yfinance, FRED |

### FX & China
| Asset | Dimensions | Data Source |
|-------|-----------|-------------|
| **Multi-Currency FX** | REER z-score, PPP deviation, Yield differential, Terms of trade, Credit-to-GDP gap | BIS, World Bank, FRED, yfinance |
| **CSI 300** | PE Percentile (15yr), CAPE Deviation, ERP | AkShare, ChinaBond |

---

## Tech Stack

```
Python 3.10+          ← Analysis engine (yfinance, akshare, FRED, BIS)
Next.js 16            ← Dashboard (TypeScript, React)
Azure Functions       ← Daily timer trigger (06:00 UTC)
Azure Static Web Apps ← Dashboard hosting
Azure Blob Storage    ← Report storage
GitHub Actions        ← CI/CD
```

---

## Quick Start

### 1. Generate Reports
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
python run_all.py
```

### 2. Run Dashboard
```bash
cd dashboard
npm install
npm run dev -- -p 3456
# Open http://localhost:3456
```

### 3. Deploy to Azure
See **[DEPLOYMENT.md](DEPLOYMENT.md)** for full Azure deployment guide.

```bash
az login
bash infra/deploy.sh
```

---

## Architecture

```
investments/
├── global_markets/          # Analysis modules
│   ├── SP500/analyze.py
│   ├── DAX/analyze.py
│   ├── CAC40/analyze.py
│   ├── FTSE100/analyze.py
│   ├── SMI/analyze.py
│   ├── PreciousMetals/analyze.py
│   ├── FX/analyze.py
│   └── common/              # Shared metrics, charting, config
├── CIS300/PE_percentile.py  # CSI 300 analysis
├── run_all.py               # Daily orchestrator
├── reports/{date}/          # Generated output
│   ├── summary.json
│   └── {Asset}/*.md + *.png
├── dashboard/               # Next.js app
│   └── src/
│       ├── app/page.tsx     # Bento grid homepage
│       ├── components/      # ImageLightbox, TabPanel, etc.
│       └── lib/             # Data loading, types
├── infra/                   # Azure deployment
│   ├── deploy.sh
│   └── function_app/
└── DEPLOYMENT.md            # Azure deployment guide
```

---

## Scoring System

Each asset is scored across multiple valuation dimensions:

| Score Range | Signal | Meaning |
|-------------|--------|---------|
| ≥ +4 | **STRONG BUY** | Deep value across multiple metrics |
| +2 to +3 | **BUY** | Below-average valuation |
| −1 to +1 | **NEUTRAL** | Fair value |
| −2 to −3 | **SELL** | Above-average valuation |
| ≤ −4 | **STRONG SELL** | Expensive across multiple metrics |

---

## License

Private repository. All rights reserved.
