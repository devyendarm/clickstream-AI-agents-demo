# Azure Deployment Guide - Clickstream Agent System

This guide will help you deploy the clickstream agent system to **Azure Container Instances (ACI)** with start/stop capability for demos.

---

## Prerequisites

1. **Azure Account** - [Sign up for free](https://azure.microsoft.com/free/)
2. **Azure CLI** - [Install Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
3. **Docker Desktop** - [Install Docker](https://www.docker.com/products/docker-desktop/)

---

## Step 1: Install Azure CLI (if not already installed)

### Windows:
```powershell
# Download and run the MSI installer
# https://aka.ms/installazurecliwindows
```

### Verify installation:
```bash
az --version
```

---

## Step 2: Login to Azure

```bash
az login
```

This will open your browser for authentication.

---

## Step 3: Create Azure Resources

### 3.1 Create Resource Group
```bash
az group create \
  --name clickstream-agents-rg \
  --location eastus
```

### 3.2 Create Azure Container Registry (ACR)
```bash
az acr create \
  --resource-group clickstream-agents-rg \
  --name clickstreamagents \
  --sku Basic
```

> **Note:** ACR name must be globally unique. If `clickstreamagents` is taken, try `clickstreamagents<yourname>`.

### 3.3 Enable Admin Access to ACR
```bash
az acr update \
  --name clickstreamagents \
  --admin-enabled true
```

---

## Step 4: Build and Push Docker Image

### 4.1 Login to ACR
```bash
az acr login --name clickstreamagents
```

### 4.2 Build Docker Image
```bash
# Navigate to your project directory
cd c:\Users\mdevy\OneDrive\Projects\AI-Agents-Agents

# Build the image
docker build -t clickstreamagents.azurecr.io/clickstream-agents:latest .
```

### 4.3 Push Image to ACR
```bash
docker push clickstreamagents.azurecr.io/clickstream-agents:latest
```

---

## Step 5: Deploy to Azure Container Instances

### 5.1 Get ACR Credentials
```bash
az acr credential show --name clickstreamagents
```

Copy the `username` and one of the `passwords`.

### 5.2 Create Container Instance
```bash
az container create \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents \
  --image clickstreamagents.azurecr.io/clickstream-agents:latest \
  --cpu 1 \
  --memory 1.5 \
  --registry-login-server clickstreamagents.azurecr.io \
  --registry-username <ACR_USERNAME> \
  --registry-password <ACR_PASSWORD> \
  --dns-name-label clickstream-agents-demo \
  --ports 5000 \
  --environment-variables OPENAI_API_KEY=<YOUR_OPENAI_KEY>
```

> **Replace:**
> - `<ACR_USERNAME>` - From step 5.1
> - `<ACR_PASSWORD>` - From step 5.1
> - `<YOUR_OPENAI_KEY>` - Your OpenAI API key (optional)

### 5.3 Get Public URL
```bash
az container show \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents \
  --query ipAddress.fqdn \
  --output tsv
```

Your app will be available at: `http://<fqdn>:5000`

---

## Step 6: Start/Stop Container (For Demos)

### ✅ Start Container (Before Demo)
```bash
az container start \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents
```

Wait ~30 seconds, then access your app.

### ⏹️ Stop Container (After Demo - Stops Billing)
```bash
az container stop \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents
```

### 📊 Check Status
```bash
az container show \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents \
  --query instanceView.state
```

### 📋 View Logs
```bash
az container logs \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents
```

---

## Step 7: Update Application (After Code Changes)

```bash
# 1. Rebuild image
docker build -t clickstreamagents.azurecr.io/clickstream-agents:latest .

# 2. Push to ACR
docker push clickstreamagents.azurecr.io/clickstream-agents:latest

# 3. Delete old container
az container delete \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents \
  --yes

# 4. Recreate container (use command from Step 5.2)
```

---

## Cost Breakdown

| Resource | Cost When Running | Cost When Stopped |
|----------|------------------|-------------------|
| **Container Instance** | ~$0.01-0.02/hour | $0.00 |
| **Container Registry** | ~$5/month | ~$5/month |
| **Total for 10-hour demo** | ~$5.20 | ~$5.00 |

**Tip:** Delete the entire resource group when done with demos to avoid ACR costs:
```bash
az group delete --name clickstream-agents-rg --yes
```

---

## Troubleshooting

### Container won't start?
```bash
# Check logs
az container logs --resource-group clickstream-agents-rg --name clickstream-agents

# Check events
az container show --resource-group clickstream-agents-rg --name clickstream-agents --query instanceView.events
```

### Can't access the app?
- Verify container is running: `az container show ... --query instanceView.state`
- Check FQDN: `az container show ... --query ipAddress.fqdn`
- Ensure port 5000 is open (it should be by default)

### Database resets on restart?
- This is expected with ACI (ephemeral storage)
- For persistent data, use Azure Database for PostgreSQL

---

## Quick Reference Commands

```bash
# Start demo
az container start --resource-group clickstream-agents-rg --name clickstream-agents

# Stop demo (stop billing)
az container stop --resource-group clickstream-agents-rg --name clickstream-agents

# Get URL
az container show --resource-group clickstream-agents-rg --name clickstream-agents --query ipAddress.fqdn -o tsv

# View logs
az container logs --resource-group clickstream-agents-rg --name clickstream-agents --follow

# Delete everything
az group delete --name clickstream-agents-rg --yes
```

---

## Next Steps

1. ✅ Deploy using steps above
2. 🔒 Add HTTPS with Azure Application Gateway (optional)
3. 📊 Replace SQLite with Azure PostgreSQL for persistence (optional)
4. 🌐 Add custom domain (optional)

**Your app will be live at:** `http://<your-fqdn>:5000`

Enjoy your demo! 🚀
