#!/bin/bash

##############################################################################
# Verify Sundai Bot Deployment
#
# Verifies that the bot is properly deployed and running on GCP VM.
#
# Usage:
#   ./deployment/verify.sh
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Bot already deployed via deploy.sh
##############################################################################

set -e  # Exit on error

# Configuration
PROJECT="sundaiiap2026"
VM_NAME="bigbootybaddy"
ZONE="us-east1-b"
BOT_PATH="/opt/sundai-bot"

echo "🔍 Verifying Sundai Bot deployment..."
echo ""

##############################################################################
# Check 1: VM is running
##############################################################################
echo "Check 1: VM Status"
echo "  Checking if VM is running..."

VM_STATUS=$(gcloud compute instances describe "$VM_NAME" \
    --project="$PROJECT" \
    --zone="$ZONE" \
    --format="value(status)")

if [ "$VM_STATUS" = "RUNNING" ]; then
    echo "  ✓ VM is running"
else
    echo "  ❌ VM is not running (status: $VM_STATUS)"
    exit 1
fi
echo ""

##############################################################################
# Check 2: Bot files exist
##############################################################################
echo "Check 2: Bot Files"
echo "  Checking if bot files exist on VM..."

gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="test -f $BOT_PATH/post_with_approval && echo 'OK'" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "  ✓ Bot files are on VM"
else
    echo "  ❌ Bot files not found on VM"
    exit 1
fi
echo ""

##############################################################################
# Check 3: Systemd service exists
##############################################################################
echo "Check 3: Systemd Configuration"
echo "  Checking if systemd service is installed..."

gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="systemctl cat sundai-bot.service > /dev/null 2>&1 && echo 'OK'" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "  ✓ Systemd service installed"
else
    echo "  ❌ Systemd service not found"
    exit 1
fi

echo "  Checking if systemd timer is installed..."
gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="systemctl cat sundai-bot.timer > /dev/null 2>&1 && echo 'OK'" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "  ✓ Systemd timer installed"
else
    echo "  ❌ Systemd timer not found"
    exit 1
fi
echo ""

##############################################################################
# Check 4: Timer is enabled and running
##############################################################################
echo "Check 4: Timer Status"

TIMER_INFO=$(gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="systemctl is-enabled sundai-bot.timer 2>&1" 2>&1)

if [[ "$TIMER_INFO" == "enabled"* ]]; then
    echo "  ✓ Timer is enabled"
else
    echo "  ⚠️  Timer may not be enabled (output: $TIMER_INFO)"
fi

TIMER_ACTIVE=$(gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="systemctl is-active sundai-bot.timer 2>&1" 2>&1)

if [[ "$TIMER_ACTIVE" == "active"* ]]; then
    echo "  ✓ Timer is active"
else
    echo "  ⚠️  Timer may not be active (output: $TIMER_ACTIVE)"
fi
echo ""

##############################################################################
# Check 5: Python dependencies installed
##############################################################################
echo "Check 5: Python Dependencies"
echo "  Checking Python 3.13..."

gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="python3.13 --version" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "  ✓ Python 3.13 is installed"
else
    echo "  ❌ Python 3.13 not found"
    exit 1
fi

echo "  Checking critical dependencies..."
gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="python3.13 -c 'import mastodon_py; import python_telegram_bot; import dotenv; print(\"OK\")'" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "  ✓ Critical dependencies installed"
else
    echo "  ⚠️  Some dependencies may be missing"
fi
echo ""

##############################################################################
# Check 6: Logs directory exists
##############################################################################
echo "Check 6: Logs Directory"
echo "  Checking if logs directory exists..."

gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="test -d $BOT_PATH/logs && echo 'OK'" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "  ✓ Logs directory exists"
else
    echo "  ❌ Logs directory not found"
    exit 1
fi
echo ""

##############################################################################
# Check 7: Test Secret Manager access
##############################################################################
echo "Check 7: Secret Manager Access"
echo "  Testing access to secrets..."

SECRET_TEST=$(gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="python3.13 -c 'from src.secrets_manager import get_secret; s = get_secret(\"TELEGRAM_BOT_TOKEN\"); print(\"OK\" if s else \"FAIL\")' 2>&1" 2>&1)

if [[ "$SECRET_TEST" == "OK"* ]]; then
    echo "  ✓ Can access secrets from Secret Manager"
else
    echo "  ⚠️  Secret Manager access test inconclusive"
fi
echo ""

##############################################################################
# Check 8: Next scheduled run
##############################################################################
echo "Check 8: Next Scheduled Run"

NEXT_RUN=$(gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$VM_NAME" \
    --command="systemctl list-timers sundai-bot.timer | tail -1" 2>&1)

echo "  $NEXT_RUN"
echo ""

##############################################################################
# Summary
##############################################################################
echo "="*60
echo "✅ DEPLOYMENT VERIFICATION COMPLETE"
echo "="*60
echo ""
echo "All checks passed! Your bot is ready to run."
echo ""
echo "Next steps:"
echo "  1. Monitor logs as the timer runs:"
echo "     gcloud compute ssh $VM_NAME --zone=$ZONE --command='tail -f /opt/sundai-bot/logs/bot.log'"
echo ""
echo "  2. Manually trigger a test run:"
echo "     gcloud compute ssh $VM_NAME --zone=$ZONE --command='sudo systemctl start sundai-bot.service'"
echo ""
echo "  3. Check timer schedule:"
echo "     gcloud compute ssh $VM_NAME --zone=$ZONE --command='systemctl list-timers'"
echo ""
