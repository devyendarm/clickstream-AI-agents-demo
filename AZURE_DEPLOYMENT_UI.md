# Azure Deployment Guide - Using Azure Portal UI

This guide shows you how to deploy the clickstream agent system using **only the Azure Portal web interface** - no command line tools needed!

---

## Prerequisites

1. **Azure Account** - [Sign up for free](https://azure.microsoft.com/free/) ($200 credit)
2. **Docker Desktop** - [Install Docker](https://www.docker.com/products/docker-desktop/)

---

## Part 1: Create Azure Container Registry (Private & Secure)

### Step 1: Login to Azure Portal
1. Go to [https://portal.azure.com](https://portal.azure.com)
2. Sign in with your Microsoft account

### Step 2: Create Container Registry

1. **Click "Create a resource"** (top left)
2. **Search for "Container Registry"**
3. **Click "Create"**

**Basics Tab:**
- **Subscription:** Select your subscription
- **Resource Group:** Click "Create new" → Name it `clickstream-agents-rg`
- **Registry name:** `clickstreamagents` (must be globally unique, try `clickstreamagentsYOURNAME` if taken)
- **Location:** Choose closest region (e.g., `East US`)
- **SKU:** `Basic` ($5/month)
- **Zone redundancy:** Disabled

Click **"Review + create"** → **"Create"**

Wait ~1 minute for deployment.

### Step 3: Enable Admin Access

1. Go to **"Resource groups"** → **"clickstream-agents-rg"**
2. Click your registry (e.g., `clickstreamagents`)
3. Click **"Access keys"** (left menu under Settings)
4. Toggle **"Admin user"** to **Enabled**
5. **Copy and save:**
   - Login server (e.g., `clickstreamagents.azurecr.io`)
   - Username
   - password (either one)

### Step 4: Push Image to Azure Container Registry

Open PowerShell and run:

```powershell
# Navigate to your project
cd c:\Users\mdevy\OneDrive\Projects\AI-Agents-Agents

# Login to ACR (replace with your values from Step 3)
docker login clickstreamagents.azurecr.io
# Username: <from Step 3>
# Password: <from Step 3>

# Build image
docker build -t clickstreamagents.azurecr.io/clickstream-agents:latest .

# Push to ACR
docker push clickstreamagents.azurecr.io/clickstream-agents:latest
```

✅ **Your image is now privately stored in Azure!**

---

## Part 2: Deploy Container Instance

### Step 1: Create Container Instance

1. In Azure Portal, **click "Create a resource"**
2. **Search for "Container Instances"**
3. **Click "Create"**

### Step 2: Configure Basic Settings

**Basics Tab:**
- **Subscription:** Select your subscription
- **Resource Group:** Select `clickstream-agents-rg` (created in Part 1)
- **Container name:** `clickstream-agents`
- **Region:** Same as your registry (e.g., `East US`)
- **Availability zones:** Leave unchecked
- **SKU:** Standard
- **Image source:** `Azure Container Registry`
- **Registry:** Select your registry (e.g., `clickstreamagents`)
- **Image:** `clickstream-agents`
- **Image tag:** `latest`
- **OS type:** `Linux`
- **Size:** 
  - CPU: `1`
  - Memory: `1.5 GB`

Click **"Next: Networking >"**

### Step 4: Configure Networking

**Networking Tab:**
- **Networking type:** `Public`
- **DNS name label:** `clickstream-agents-demo` (must be globally unique, try adding your name if taken)
- **DNS name label scope reuse:** `Tenant`
- **Ports:**
  - Protocol: `TCP`
  - Port: `5000`

Click **"Next: Advanced >"**

### Step 5: Configure Environment Variables (Optional)

**Advanced Tab:**
- **Restart policy:** `On failure`
- **Environment variables:** Click "Add"
  - Name: `OPENAI_API_KEY`
  - Value: `your-openai-api-key-here` (optional)

Click **"Review + create"**

### Step 6: Create Container

1. Review your settings
2. Click **"Create"**
3. Wait ~2 minutes for deployment

### Step 7: Get Your App URL

1. Go to **"Resource groups"** (left menu)
2. Click **"clickstream-agents-rg"**
3. Click **"clickstream-agents"** (your container)
4. Find **"FQDN"** under "Essentials"
5. Your app URL: `http://<your-fqdn>:5000`

**Example:** `http://clickstream-agents-demo.eastus.azurecontainer.io:5000`

---

## Part 3: Start/Stop Container (Save Money!)

### ✅ Start Container (Before Demo)

1. Go to **Azure Portal** → **Resource groups** → **clickstream-agents-rg**
2. Click **"clickstream-agents"**
3. Click **"Start"** button at the top
4. Wait ~30 seconds
5. Access your app at the FQDN URL

### ⏹️ Stop Container (After Demo - Stops Billing!)

1. Go to **Azure Portal** → **Resource groups** → **clickstream-agents-rg**
2. Click **"clickstream-agents"**
3. Click **"Stop"** button at the top
4. **Billing paused!** (You only pay when running)

### 📊 Check Status

1. Go to your container in Azure Portal
2. Look at **"State"** under "Essentials"
   - `Running` = Billing active
   - `Stopped` = No charges

### 📋 View Logs

1. Go to your container in Azure Portal
2. Click **"Containers"** (left menu)
3. Click **"Logs"** tab
4. See real-time application logs

---

## Part 4: Update Application (After Code Changes)

### Option A: Push New Image (Recommended)

1. **Rebuild and push image:**
   ```powershell
   # Login to ACR
   docker login clickstreamagents.azurecr.io
   
   # Rebuild
   docker build -t clickstreamagents.azurecr.io/clickstream-agents:latest .
   
   # Push
   docker push clickstreamagents.azurecr.io/clickstream-agents:latest
   ```

2. **In Azure Portal:**
   - Go to your container
   - Click **"Restart"** button (pulls latest image automatically)

### Option B: Quick Restart (If no code changes)

1. Go to your container in Azure Portal
2. Click **"Restart"** button

---

## Cost Breakdown

| Resource | Cost When Running | Cost When Stopped |
|----------|------------------|-------------------|
| **Container Instance** | ~$0.01-0.02/hour | **$0.00** |
| **Container Registry (Basic)** | ~$5/month | ~$5/month |
| **Total for 10-hour demo** | ~$5.20 | ~$5.00/month |

**💡 Pro Tip:** 
- Stop the container after demos to avoid compute charges
- Delete the entire resource group when completely done to stop ACR charges

---

## Troubleshooting

### Container won't start?
1. Go to container → **"Containers"** → **"Logs"** tab
2. Check for error messages
3. Common issues:
   - Wrong image name
   - Port 5000 not exposed in Dockerfile
   - Memory too low (increase to 2GB)

### Can't access the app?
1. Verify container **State** is "Running"
2. Check **FQDN** is correct
3. Make sure you're using `http://` not `https://`
4. Verify port `:5000` is in the URL

### Image not found?
1. Verify image exists in ACR:
   - Go to your Container Registry → **"Repositories"**
   - Should see `clickstream-agents` with tag `latest`
2. Check Admin user is enabled in ACR → **"Access keys"**
3. Make sure you pushed the image (Step 4 in Part 1)

---

## Delete Everything (When Done)

To completely remove all resources and stop all charges:

1. Go to **"Resource groups"**
2. Click **"clickstream-agents-rg"**
3. Click **"Delete resource group"** (top menu)
4. Type the resource group name to confirm
5. Click **"Delete"**

**Everything is deleted - no more charges!**

---

## Quick Reference

### Your App URL Format:
```
http://<dns-name-label>.<region>.azurecontainer.io:5000
```

Example:
```
http://clickstream-agents-demo.eastus.azurecontainer.io:5000
```

### Start/Stop Locations:
```
Azure Portal → Resource groups → clickstream-agents-rg → clickstream-agents → Start/Stop buttons
```

---

## Next Steps

1. ✅ Create Azure Container Registry (Part 1)
2. ✅ Push image to ACR (Part 1, Step 4)
3. ✅ Deploy container via Azure Portal (Part 2)
4. 🎯 Start container before demos (Part 3)
5. 💰 Stop container after demos (Part 3)

**Your demo is ready - privately and securely hosted!** 🚀🔒

Minimal command line (just 3 Docker commands) - rest is through the web UI!
