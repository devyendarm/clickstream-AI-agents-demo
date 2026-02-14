# Azure Clickstream Agents - Quick Start Script (PowerShell)
# This script starts your container for a demo

Write-Host "🚀 Starting Clickstream Agents container..." -ForegroundColor Green

az container start `
  --resource-group clickstream-agents-rg `
  --name clickstream-agents

Write-Host "⏳ Waiting for container to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Get the URL
$URL = az container show `
  --resource-group clickstream-agents-rg `
  --name clickstream-agents `
  --query ipAddress.fqdn `
  --output tsv

Write-Host ""
Write-Host "✅ Container started!" -ForegroundColor Green
Write-Host "📍 Your app is available at: http://${URL}:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop the container (and stop billing), run: .\stop-demo.ps1" -ForegroundColor Yellow
