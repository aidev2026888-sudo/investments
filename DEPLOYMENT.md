# Global Markets Monitor — Deployment Guide

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Azure Function  │────▶│  Blob Storage    │◀────│  Next.js    │
│  (Daily Timer)   │     │  (Reports)       │     │  Dashboard  │
│  06:00 UTC       │     │  summary.json    │     │  (SWA)      │
└─────────────────┘     └──────────────────┘     └─────────────┘
```

**Cost:** $0/month on Azure free tiers.

---

## Prerequisites

Before deploying, ensure you have:

### 1. Azure Account
- An active Azure subscription (free tier works)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed

### 2. Login to Azure CLI
```bash
az login
az account show  # Verify you're on the right subscription
```

### 3. GitHub Repository
- Push this repo to GitHub (required for Static Web App CI/CD)
- Have a GitHub personal access token ready (Azure will request OAuth)

### 4. Environment Variables
Create a `.env` file at the repo root with any API keys:
```
FRED_API_KEY=your_fred_api_key_here
```

### 5. Node.js & Python
- Node.js 20+ (for dashboard build)
- Python 3.10+ with `requirements.txt` installed

---

## Deploy

### Step 1: Provision Azure Resources

```bash
chmod +x infra/deploy.sh
bash infra/deploy.sh
```

This creates:
| Resource | Name | Purpose |
|----------|------|---------|
| Resource Group | `rg-investments-monitor` | Container for all resources |
| Storage Account | `stinvestmentsdata` | Blob storage for reports |
| Function App | `func-investments-daily` | Timer trigger (daily 06:00 UTC) |
| Static Web App | `swa-investments-dashboard` | Hosts the Next.js dashboard |

### Step 2: Deploy the Function App

```bash
cd infra/function_app
pip install -r requirements.txt
func azure functionapp publish func-investments-daily
```

### Step 3: Configure Secrets

In your GitHub repo → Settings → Secrets, add:

| Secret | Value |
|--------|-------|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | From Azure SWA output |
| `FRED_API_KEY` | Your FRED API key |

### Step 4: Push to Deploy

```bash
git add -A
git commit -m "Deploy dashboard"
git push origin master
```

The GitHub Action at `.github/workflows/deploy.yml` will auto-build and deploy.

---

## Running Locally

```bash
# 1. Generate reports
python run_all.py

# 2. Start dashboard
cd dashboard
npm install
npm run dev -- -p 3456
# Open http://localhost:3456
```

---

## Daily Schedule

The Azure Function runs at **06:00 UTC** daily:
1. Executes `run_all.py` (all 8 analyzers with 15s delay)
2. Uploads reports to Azure Blob Storage
3. Dashboard reads from blob storage on next page load

To trigger manually:
```bash
# From Azure Portal → Function App → daily_run → Run
# Or from the dashboard → Click any asset → ▶ Run Analysis
```

---

## Monitoring

- **Azure Portal** → Function App → Monitor → Invocations
- **Dashboard** → Each asset card shows status dot (green = data available)
- **Logs** → `reports/{date}/summary.json` contains all signals and scores
