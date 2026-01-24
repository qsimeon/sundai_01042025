#!/bin/bash
# Quick restart script for Sundai API on GCP
# Usage: ./deployment/restart_api.sh

set -e

PROJECT="sundaiiap2026"
VM="sundai-api-server"
ZONE="us-central1-a"

echo "🚀 Restarting Sundai API Server..."
echo ""

# 1. Start VM
echo "Starting VM..."
gcloud compute instances start $VM \
    --zone=$ZONE \
    --project=$PROJECT

echo "Waiting 30 seconds for VM to boot..."
sleep 30

# 2. Verify API is running
echo ""
echo "Checking API service status..."
gcloud compute ssh $VM --zone=$ZONE --project=$PROJECT --command='sudo systemctl status sundai-api.service --no-pager' 2>&1 | grep -v "X11" | head -10

# 3. Get external IP
echo ""
echo "🔍 Getting external IP..."
EXTERNAL_IP=$(gcloud compute instances describe $VM \
    --zone=$ZONE \
    --project=$PROJECT \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

# 4. Test API
echo ""
echo "Testing API health..."
HEALTH_CHECK=$(curl -s http://$EXTERNAL_IP:8000/health)

if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API may still be starting up, trying again in 10 seconds..."
    sleep 10
    HEALTH_CHECK=$(curl -s http://$EXTERNAL_IP:8000/health)
    if echo "$HEALTH_CHECK" | grep -q "healthy"; then
        echo "✅ API is healthy!"
    else
        echo "❌ API health check failed"
        exit 1
    fi
fi

echo ""
echo "✅ Server is running!"
echo ""
echo "📍 API Details:"
echo "   External IP: $EXTERNAL_IP"
echo "   API URL: http://$EXTERNAL_IP:8000"
echo "   Documentation: http://$EXTERNAL_IP:8000/docs"
echo "   Health Check: http://$EXTERNAL_IP:8000/health"
echo ""
echo "To stop the server later and save costs:"
echo "   gcloud compute instances stop $VM --zone=$ZONE --project=$PROJECT --quiet"
echo ""
