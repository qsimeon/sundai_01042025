#!/bin/bash
set -e

PROJECT="sundaiiap2026"
VM="sundai-api-server"
ZONE="us-central1-a"

echo "🚀 Setting up GCP Infrastructure for Sundai Bot..."

# Note: Old VM deletion and new VM creation already done
# This script is for reference - infrastructure is already set up

echo "✅ Infrastructure setup complete!"
echo ""
echo "VM Details:"
echo "  Name: $VM"
echo "  Zone: $ZONE"
echo "  Machine Type: e2-standard-2"
echo "  Boot Disk: 30GB"
echo ""
echo "Next step: Run ./deployment/deploy_api.sh to deploy the API"
