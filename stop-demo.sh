#!/bin/bash

# Azure Clickstream Agents - Stop Script
# This script stops your container to save costs

echo "⏹️  Stopping Clickstream Agents container..."

az container stop \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents

echo ""
echo "✅ Container stopped!"
echo "💰 Billing paused (only paying for Container Registry ~$5/month)"
echo ""
echo "To start again for your next demo, run: ./start-demo.sh"
