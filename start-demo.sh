#!/bin/bash

# Azure Clickstream Agents - Quick Start Script
# This script starts your container for a demo

echo "🚀 Starting Clickstream Agents container..."

az container start \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents

echo "⏳ Waiting for container to start (30 seconds)..."
sleep 30

# Get the URL
URL=$(az container show \
  --resource-group clickstream-agents-rg \
  --name clickstream-agents \
  --query ipAddress.fqdn \
  --output tsv)

echo ""
echo "✅ Container started!"
echo "📍 Your app is available at: http://${URL}:5000"
echo ""
echo "To stop the container (and stop billing), run: ./stop-demo.sh"
