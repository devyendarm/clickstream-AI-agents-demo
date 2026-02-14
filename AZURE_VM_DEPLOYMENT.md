# Azure VM Deployment Guide - Direct Code Files

Deploy your clickstream agent system to Azure VM using **direct code files** - no Docker, no registries, just simple file upload!

---

## Prerequisites

1. **Azure Account** - [Sign up for free](https://azure.microsoft.com/free/) ($200 credit)
2. **WinSCP or FileZilla** - For file transfer (optional, can use Azure Portal)

---

## Part 1: Create Azure Virtual Machine

### Step 1: Login to Azure Portal
1. Go to [https://portal.azure.com](https://portal.azure.com)
2. Sign in with your Microsoft account

### Step 2: Create Virtual Machine

1. Click **"Create a resource"** (top left)
2. Search for **"Virtual Machine"**
3. Click **"Create"**

### Step 3: Configure VM - Basics

**Basics Tab:**
- **Subscription:** Select your subscription
- **Resource Group:** Click "Create new" → Name it `clickstream-vm-rg`
- **Virtual machine name:** `clickstream-vm`
- **Region:** Choose closest region (e.g., `East US`)
- **Availability options:** No infrastructure redundancy required
- **Security type:** Standard
- **Image:** `Ubuntu Server 22.04 LTS - x64 Gen2`
- **Size:** Click "See all sizes" → Select `B2s` (2 vCPUs, 4GB RAM)
  - Cost: ~$30/month when running, ~$2/month when stopped

**Administrator account:**
- **Authentication type:** Password (easier for beginners)
- **Username:** `azureuser`
- **Password:** Create a strong password (save it!)

**Inbound port rules:**
- **Public inbound ports:** Allow selected ports
- **Select inbound ports:** Check `HTTP (80)`, `HTTPS (443)`, `SSH (22)`

Click **"Next: Disks >"**

### Step 4: Configure Disks

**Disks Tab:**
- **OS disk type:** Standard SSD (default)
- Leave other settings as default

Click **"Next: Networking >"**

### Step 5: Configure Networking

**Networking Tab:**
- **Virtual network:** (auto-created)
- **Subnet:** (auto-created)
- **Public IP:** (auto-created)
- **NIC network security group:** Basic
- **Public inbound ports:** Allow selected ports
- **Select inbound ports:** HTTP (80), HTTPS (443), SSH (22)

Click **"Review + create"**

### Step 6: Create VM

1. Review your settings
2. Click **"Create"**
3. Wait ~3-5 minutes for deployment

### Step 7: Get VM Public IP

1. Go to **"Resource groups"** → **"clickstream-vm-rg"**
2. Click **"clickstream-vm"**
3. Find **"Public IP address"** under Essentials
4. **Copy this IP** - you'll need it!

---

## Part 2: Upload Your Code Files

### Option A: Via Azure Portal (Easiest)

1. **Prepare your code:**
   ```powershell
   # Navigate to project
   cd c:\Users\mdevy\OneDrive\Projects\AI-Agents-Agents
   
   # Create a zip file
   Compress-Archive -Path * -DestinationPath clickstream-app.zip
   ```

2. **Upload via Azure Cloud Shell:**
   - In Azure Portal, click **Cloud Shell** icon (top right, looks like `>_`)
   - Choose **Bash**
   - Click **"Upload/Download files"** icon
   - Upload `clickstream-app.zip`
   - Run:
     ```bash
     # Copy to VM
     scp clickstream-app.zip azureuser@<YOUR_VM_IP>:~
     ```

### Option B: Via WinSCP (Recommended)

1. **Download WinSCP:** [https://winscp.net](https://winscp.net)
2. **Connect to VM:**
   - Host name: `<YOUR_VM_IP>`
   - User name: `azureuser`
   - Password: `<your-vm-password>`
   - Click **"Login"**
3. **Upload files:**
   - Drag and drop your entire project folder to `/home/azureuser/`

### Option C: Via Git (If you have GitHub)

```bash
# SSH into VM first
ssh azureuser@<YOUR_VM_IP>

# Clone your repo
git clone https://github.com/yourusername/clickstream-agents.git
cd clickstream-agents
```

---

## Part 3: Setup and Run Application

### Step 1: SSH into VM

```powershell
# From your local machine
ssh azureuser@<YOUR_VM_IP>
# Enter password when prompted
```

### Step 2: Install Dependencies

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv -y

# Navigate to your app
cd clickstream-app  # or wherever you uploaded

# Install Python packages
pip3 install -r requirements.txt
```

### Step 3: Configure Firewall for Port 5000

```bash
# Open port 5000
sudo ufw allow 5000/tcp
sudo ufw allow 22/tcp  # Keep SSH open
sudo ufw enable
```

**Also in Azure Portal:**
1. Go to your VM → **"Networking"** (left menu)
2. Click **"Add inbound port rule"**
3. **Destination port ranges:** `5000`
4. **Protocol:** TCP
5. **Name:** `Port_5000`
6. Click **"Add"**

### Step 4: Run the Application

```bash
# Run in background with nohup
nohup python3 app.py > app.log 2>&1 &

# Check if running
ps aux | grep app.py

# View logs
tail -f app.log
```

### Step 5: Access Your App

Open browser and go to:
```
http://<YOUR_VM_IP>:5000
```

🎉 **Your app is live!**

---

## Part 4: Start/Stop VM (Save Money!)

### ✅ Start VM (Before Demo)

**Via Azure Portal:**
1. Go to **Resource groups** → **clickstream-vm-rg** → **clickstream-vm**
2. Click **"Start"** button (top menu)
3. Wait ~1 minute
4. Access app at `http://<YOUR_VM_IP>:5000`

### ⏹️ Stop VM (After Demo - Stops Billing!)

**Via Azure Portal:**
1. Go to your VM
2. Click **"Stop"** button (top menu)
3. **Important:** Make sure it says "Stopped (deallocated)"
4. **Billing paused!** Only pay for storage (~$2/month)

### 📊 Check Status

1. Go to your VM in Azure Portal
2. Look at **"Status"** under Essentials:
   - `Running` = Billing active (~$30/month)
   - `Stopped (deallocated)` = Only storage cost (~$2/month)

---

## Part 5: Auto-Start Application on VM Boot

To make the app start automatically when you start the VM:

```bash
# SSH into VM
ssh azureuser@<YOUR_VM_IP>

# Create systemd service
sudo nano /etc/systemd/system/clickstream.service
```

**Paste this content:**
```ini
[Unit]
Description=Clickstream Agent System
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/home/azureuser/clickstream-app
ExecStart=/usr/bin/python3 /home/azureuser/clickstream-app/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and enable:**
```bash
# Save: Ctrl+O, Enter, Ctrl+X

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable clickstream.service
sudo systemctl start clickstream.service

# Check status
sudo systemctl status clickstream.service
```

Now the app starts automatically when you start the VM! 🚀

---

## Part 6: Update Application (After Code Changes)

### Option 1: Upload New Files

1. **Stop the app:**
   ```bash
   ssh azureuser@<YOUR_VM_IP>
   sudo systemctl stop clickstream.service  # If using systemd
   # OR
   pkill -f app.py  # If running with nohup
   ```

2. **Upload new files** (via WinSCP or SCP)

3. **Restart the app:**
   ```bash
   sudo systemctl start clickstream.service
   # OR
   nohup python3 app.py > app.log 2>&1 &
   ```

### Option 2: Use Git (Recommended)

```bash
ssh azureuser@<YOUR_VM_IP>
cd clickstream-app
git pull origin main
sudo systemctl restart clickstream.service
```

---

## Cost Breakdown

| Resource | Cost When Running | Cost When Stopped |
|----------|------------------|-------------------|
| **VM (B2s)** | ~$30/month | **$0** |
| **Storage (30GB SSD)** | ~$2/month | ~$2/month |
| **Total for 10-hour demo** | ~$0.40 | ~$2/month |

**💡 Pro Tip:** Always **Stop (deallocate)** the VM after demos to avoid compute charges!

---

## Troubleshooting

### Can't SSH into VM?
1. Check VM is running (Status: "Running")
2. Verify you're using correct IP address
3. Check password is correct
4. Ensure port 22 is open in Azure Network Security Group

### Can't access app at port 5000?
1. Verify app is running: `ps aux | grep app.py`
2. Check logs: `tail -f app.log`
3. Ensure port 5000 is open:
   - In VM firewall: `sudo ufw status`
   - In Azure NSG: Check inbound rules
4. Try accessing from VM itself: `curl http://localhost:5000`

### App crashes on startup?
```bash
# Check logs
tail -f app.log

# Common issues:
# - Missing dependencies: pip3 install -r requirements.txt
# - Port already in use: sudo lsof -i :5000
# - Database permission: chmod 666 clickstream.db
```

### Database resets after VM restart?
- This shouldn't happen with VM (unlike containers)
- Check database file exists: `ls -la clickstream.db`
- Ensure app has write permissions: `chmod 666 clickstream.db`

---

## Delete Everything (When Done)

To completely remove all resources and stop all charges:

1. Go to **"Resource groups"**
2. Click **"clickstream-vm-rg"**
3. Click **"Delete resource group"** (top menu)
4. Type the resource group name to confirm
5. Click **"Delete"**

**Everything is deleted - no more charges!**

---

## Quick Reference Commands

```bash
# SSH into VM
ssh azureuser@<YOUR_VM_IP>

# Start app manually
nohup python3 app.py > app.log 2>&1 &

# Stop app
pkill -f app.py

# View logs
tail -f app.log

# Check if app is running
ps aux | grep app.py

# Restart systemd service
sudo systemctl restart clickstream.service

# View systemd logs
sudo journalctl -u clickstream.service -f
```

---

## Summary

**Setup (One-time):**
1. ✅ Create Azure VM via Portal (~5 minutes)
2. ✅ Upload code files via WinSCP or SCP
3. ✅ Install Python & dependencies
4. ✅ Run app with systemd (auto-start)

**For Demos:**
1. 🚀 Start VM in Azure Portal
2. 🌐 Access `http://<VM_IP>:5000`
3. 🎯 Run your demo
4. 💰 Stop (deallocate) VM

**Cost:** ~$0.04/hour when running, ~$2/month when stopped!

**No Docker, no registries, no complexity - just simple file upload and run!** 🎉
