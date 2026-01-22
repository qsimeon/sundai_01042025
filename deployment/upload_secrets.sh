#!/bin/bash

##############################################################################
# Upload Secrets to GCP Secret Manager
#
# Reads secrets from .env file and uploads each to GCP Secret Manager.
# This is a ONE-TIME operation - run this before deploy.sh
#
# Usage:
#   ./deployment/upload_secrets.sh
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - GCP project set to 'sundaiiap2026'
#   - .env file exists in project root
##############################################################################

set -e  # Exit on error

# Configuration
PROJECT="sundaiiap2026"
ENV_FILE=".env"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$SOURCE_DIR/$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE not found in $SOURCE_DIR"
    echo ""
    echo "The .env file must exist to upload secrets."
    echo "Please ensure .env is in the project root."
    exit 1
fi

echo "🔐 Uploading secrets to GCP Secret Manager..."
echo "   Project: $PROJECT"
echo "   Source: $SOURCE_DIR/$ENV_FILE"
echo ""

##############################################################################
# Parse and upload each secret
##############################################################################

# Count variables
total=$(grep -c "^[^#]" "$SOURCE_DIR/$ENV_FILE" || echo 0)
uploaded=0
skipped=0

while IFS='=' read -r key value; do
    # Skip empty lines and comments
    [[ -z "$key" ]] && continue
    [[ "$key" =~ ^# ]] && continue

    # Check if secret already exists
    if gcloud secrets describe "$key" --project="$PROJECT" > /dev/null 2>&1; then
        echo "⏭️  Skipping '$key' (already exists)"
        ((skipped++))
        continue
    fi

    echo "📤 Uploading '$key'..."

    # Create the secret
    echo -n "$value" | gcloud secrets create "$key" \
        --project="$PROJECT" \
        --replication-policy=automatic \
        --data-file=- > /dev/null 2>&1

    echo "   ✓ Created"
    ((uploaded++))

done < "$SOURCE_DIR/$ENV_FILE"

##############################################################################
# Summary
##############################################################################
echo ""
echo "="*60
echo "✅ SECRET UPLOAD COMPLETE"
echo "="*60
echo ""
echo "Summary:"
echo "  Uploaded: $uploaded new secrets"
echo "  Skipped: $skipped existing secrets"
echo ""
echo "To verify secrets were uploaded, run:"
echo "  gcloud secrets list --project=$PROJECT"
echo ""
echo "Next steps:"
echo "  1. Make sure GCP VM 'bigbootybaddy' has secret accessor role:"
echo "     gcloud projects add-iam-policy-binding $PROJECT \\"
echo "       --member='serviceAccount:sundai-bot-sa@$PROJECT.iam.gserviceaccount.com' \\"
echo "       --role='roles/secretmanager.secretAccessor'"
echo ""
echo "  2. Deploy the bot:"
echo "     ./deployment/deploy.sh"
echo ""
