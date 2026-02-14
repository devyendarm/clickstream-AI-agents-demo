# Azure Clickstream Agents - Stop Script (PowerShell)
# This script stops your container to save costs

Write-Host "⏹️  Stopping Clickstream Agents container..." -ForegroundColor Yellow

az container stop `
  --resource-group clickstream-agents-rg `
  --name clickstream-agents

Write-Host ""
Write-Host "✅ Container stopped!" -ForegroundColor Green
Write-Host "💰 Billing paused (only paying for Container Registry ~$5/month)" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start again for your next demo, run: .\start-demo.ps1" -ForegroundColor Yellow
