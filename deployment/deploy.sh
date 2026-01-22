#!/bin/bash

##############################################################################
# Sundai Bot Deployment Script
#
# Deploys the sundai_01042025 social media bot to GCP VM "bigbootybaddy"
# Sets up Python 3.13, dependencies, and systemd service/timer
#
# Usage:
#   ./deployment/deploy.sh
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - GCP project set to 'sundaiiap2026'
#   - VM 'bigbootybaddy' created in us-east1-b
#   - Secrets already uploaded to Secret Manager (run upload_secrets.sh first)
##############################################################################

set -e  # Exit on error

# Configuration
PROJECT="sundaiiap2026"
VM_NAME="bigbootybaddy"
ZONE="us-east1-b"
BOT_PATH="/opt/sundai-bot"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Starting deployment of Sundai Bot to $VM_NAME..."
echo "   Project: $PROJECT"
echo "   Zone: $ZONE"
echo "   Bot path: $BOT_PATH"
echo ""

##############################################################################
# Step 1: Copy code to VM
##############################################################################
echo "📦 Step 1: Uploading code to VM..."
gcloud compute scp --project="$PROJECT" --zone="$ZONE" \
    --recurse \
    "$SOURCE_DIR/src" \
    "$SOURCE_DIR/post_with_approval" \
    "$SOURCE_DIR/reply_with_approval" \
    "$SOURCE_DIR/pyproject.toml" \
    "$SOURCE_DIR/uv.lock" \
    "root@$VM_NAME:$BOT_PATH/" 2>&1 | head -20

echo "✓ Code uploaded"
echo ""

##############################################################################
# Step 2: Create logs directory
##############################################################################
echo "📁 Step 2: Setting up directories and permissions..."
gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="mkdir -p $BOT_PATH/logs && chmod 755 $BOT_PATH/logs" > /dev/null

echo "✓ Directories created"
echo ""

##############################################################################
# Step 3: Install Python 3.13 and uv (if not already installed)
##############################################################################
echo "🐍 Step 3: Installing Python 3.13 and dependencies..."

# SSH to VM and run installation commands
gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" --command='
set -e

# Check if Python 3.13 is already installed
if ! command -v python3.13 &> /dev/null; then
    echo "Installing Python 3.13..."
    apt-get update > /dev/null 2>&1
    apt-get install -y python3.13 python3.13-venv python3.13-dev > /dev/null 2>&1

    # Create symlink if needed
    update-alternatives --install /usr/local/bin/python3.13 python3.13 /usr/bin/python3.13 1
    echo "✓ Python 3.13 installed"
else
    echo "✓ Python 3.13 already installed"
fi

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null 2>&1
    source $HOME/.cargo/env
    echo "✓ uv installed"
else
    echo "✓ uv already installed"
fi
' > /dev/null 2>&1

echo "✓ Python 3.13 and uv ready"
echo ""

##############################################################################
# Step 4: Install dependencies
##############################################################################
echo "📚 Step 4: Installing Python dependencies..."
gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="cd $BOT_PATH && /root/.local/bin/uv sync --no-dev > /dev/null 2>&1" > /dev/null 2>&1

echo "✓ Dependencies installed"
echo ""

##############################################################################
# Step 5: Copy systemd service and timer files
##############################################################################
echo "⚙️  Step 5: Installing systemd service and timer..."

# Create temporary directory for service files
TEMP_DIR=$(mktemp -d)
cp "$SOURCE_DIR/deployment/sundai-bot.service" "$TEMP_DIR/"
cp "$SOURCE_DIR/deployment/sundai-bot.timer" "$TEMP_DIR/"

# Upload to VM
gcloud compute scp --project="$PROJECT" --zone="$ZONE" \
    "$TEMP_DIR/sundai-bot.service" \
    "$TEMP_DIR/sundai-bot.timer" \
    "root@$VM_NAME:/etc/systemd/system/" > /dev/null 2>&1

# Clean up
rm -rf "$TEMP_DIR"

# Reload systemd and enable service
gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="systemctl daemon-reload && systemctl enable sundai-bot.timer && systemctl enable sundai-bot.service" > /dev/null 2>&1

echo "✓ Systemd service and timer installed"
echo ""

##############################################################################
# Step 6: Start the timer
##############################################################################
echo "🚀 Step 6: Starting systemd timer..."
gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="systemctl start sundai-bot.timer && systemctl status sundai-bot.timer --no-pager" > /dev/null 2>&1

echo "✓ Timer started"
echo ""

##############################################################################
# Step 7: Verify deployment
##############################################################################
echo "✅ Step 7: Verifying deployment..."
gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="systemctl list-timers --all | grep sundai-bot" > /dev/null 2>&1

echo "✓ Deployment verified"
echo ""

##############################################################################
# Success
##############################################################################
echo "="*60
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "="*60
echo ""
echo "Bot deployed to: $BOT_NAME ($BOT_PATH)"
echo "Timer configured to run every 4 hours"
echo "Logs available at: /opt/sundai-bot/logs/"
echo ""
echo "Useful commands:"
echo "  View timer status:"
echo "    gcloud compute ssh $VM_NAME --zone=$ZONE --command='sudo systemctl status sundai-bot.timer'"
echo ""
echo "  View logs:"
echo "    gcloud compute ssh $VM_NAME --zone=$ZONE --command='tail -f /opt/sundai-bot/logs/bot.log'"
echo ""
echo "  Manually trigger bot:"
echo "    gcloud compute ssh $VM_NAME --zone=$ZONE --command='sudo systemctl start sundai-bot.service'"
echo ""
echo "  View next scheduled run:"
echo "    gcloud compute ssh $VM_NAME --zone=$ZONE --command='systemctl list-timers'"
echo ""
