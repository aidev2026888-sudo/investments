#!/bin/bash
# ==================================================
# Azure Deployment Script
# Provisions: Resource Group, Storage Account,
#             Function App (Timer Trigger), Static Web App
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - GitHub repo: https://github.com/aidev2026888-sudo/investments.git
#
# Usage:
#   chmod +x infra/deploy.sh
#   bash infra/deploy.sh
# ==================================================

set -euo pipefail

# --------------- Configuration ---------------
RESOURCE_GROUP="rg-investments-monitor"
LOCATION="eastasia"                          # Close to SG/CN for BIS/SHFE data
STORAGE_ACCOUNT="stinvestmentsdata"          # Must be globally unique, lowercase
FUNCTION_APP="func-investments-daily"
STATIC_WEB_APP="swa-investments-dashboard"
GITHUB_REPO="https://github.com/aidev2026888-sudo/investments"
GITHUB_BRANCH="master"

# --------------- 1. Resource Group ---------------
echo "==> Creating Resource Group: $RESOURCE_GROUP"
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none

# --------------- 2. Storage Account ---------------
echo "==> Creating Storage Account: $STORAGE_ACCOUNT"
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --kind StorageV2 \
  --output none

# Create blob container for reports
STORAGE_KEY=$(az storage account keys list \
  --resource-group "$RESOURCE_GROUP" \
  --account-name "$STORAGE_ACCOUNT" \
  --query '[0].value' -o tsv)

az storage container create \
  --name "reports" \
  --account-name "$STORAGE_ACCOUNT" \
  --account-key "$STORAGE_KEY" \
  --output none

echo "   Storage container 'reports' created."

# --------------- 3. Function App ---------------
echo "==> Creating Function App: $FUNCTION_APP"

# Create an App Service Plan (Consumption/Serverless)
az functionapp create \
  --resource-group "$RESOURCE_GROUP" \
  --consumption-plan-location "$LOCATION" \
  --runtime python \
  --runtime-version 3.10 \
  --functions-version 4 \
  --name "$FUNCTION_APP" \
  --storage-account "$STORAGE_ACCOUNT" \
  --os-type Linux \
  --output none

# Configure environment variables
echo "   Setting Function App configuration..."
az functionapp config appsettings set \
  --name "$FUNCTION_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --settings \
    "AzureWebJobsStorage=$(az storage account show-connection-string --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --query connectionString -o tsv)" \
    "REPORTS_STORAGE_CONNECTION=$(az storage account show-connection-string --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --query connectionString -o tsv)" \
    "PYTHONIOENCODING=utf-8" \
  --output none

echo "   Function App created. Deploy with: func azure functionapp publish $FUNCTION_APP"

# --------------- 4. Static Web App ---------------
echo "==> Creating Static Web App: $STATIC_WEB_APP"
az staticwebapp create \
  --name "$STATIC_WEB_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --source "$GITHUB_REPO" \
  --branch "$GITHUB_BRANCH" \
  --app-location "/dashboard" \
  --output-location "out" \
  --login-with-github \
  --output none

HOSTNAME=$(az staticwebapp show \
  --name "$STATIC_WEB_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --query "defaultHostname" -o tsv)

echo ""
echo "============================================"
echo "  DEPLOYMENT COMPLETE"
echo "============================================"
echo "  Resource Group:   $RESOURCE_GROUP"
echo "  Storage Account:  $STORAGE_ACCOUNT"
echo "  Function App:     $FUNCTION_APP"
echo "  Static Web App:   https://$HOSTNAME"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Deploy Function App:  cd infra/function_app && func azure functionapp publish $FUNCTION_APP"
echo "  2. Dashboard auto-deploys via GitHub Actions on push to $GITHUB_BRANCH"
echo "  3. Daily scheduler runs at 06:00 UTC automatically"
