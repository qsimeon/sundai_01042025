#!/bin/bash

##############################################################################
# Update a Secret in GCP Secret Manager
#
# Updates an existing secret in GCP Secret Manager.
#
# Usage:
#   ./deployment/update_secret.sh SECRET_NAME "new_value"
#
# Example:
#   ./deployment/update_secret.sh TELEGRAM_BOT_TOKEN "123456789:ABCDefg..."
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - GCP project set to 'sundaiiap2026'
#   - Secret must already exist in Secret Manager
##############################################################################

set -e  # Exit on error

# Configuration
PROJECT="sundaiiap2026"

# Validate arguments
if [ $# -lt 2 ]; then
    echo "❌ Error: Missing arguments"
    echo ""
    echo "Usage: ./deployment/update_secret.sh SECRET_NAME new_value"
    echo ""
    echo "Example:"
    echo "  ./deployment/update_secret.sh TELEGRAM_BOT_TOKEN \"123456789:ABCDefg...\""
    echo ""
    exit 1
fi

SECRET_NAME="$1"
NEW_VALUE="$2"

echo "🔐 Updating secret in GCP Secret Manager..."
echo "   Project: $PROJECT"
echo "   Secret: $SECRET_NAME"
echo ""

# Check if secret exists
if ! gcloud secrets describe "$SECRET_NAME" --project="$PROJECT" > /dev/null 2>&1; then
    echo "❌ Error: Secret '$SECRET_NAME' does not exist"
    echo ""
    echo "Available secrets:"
    gcloud secrets list --project="$PROJECT" --format="table(name)"
    exit 1
fi

# Add new version
echo "📝 Adding new version..."
echo -n "$NEW_VALUE" | gcloud secrets versions add "$SECRET_NAME" \
    --project="$PROJECT" \
    --data-file=- > /dev/null 2>&1

echo "✓ Secret updated"
echo ""
echo "="*60
echo "✅ SECRET UPDATE COMPLETE"
echo "="*60
echo ""
echo "New version is now active."
echo "The bot will use this value on next run."
echo ""
echo "To view secret versions:"
echo "  gcloud secrets versions list $SECRET_NAME --project=$PROJECT"
echo ""
