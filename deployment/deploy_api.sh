#!/bin/bash
set -e

PROJECT="sundaiiap2026"
VM="sundai-api-server"
ZONE="us-central1-a"

echo "🚀 Deploying Sundai FastAPI..."
echo ""

# Check if VM is running
echo "Checking VM status..."
VM_STATUS=$(gcloud compute instances describe $VM \
    --zone=$ZONE \
    --format='get(status)' \
    --project=$PROJECT 2>/dev/null || echo "UNKNOWN")

if [ "$VM_STATUS" != "RUNNING" ]; then
    echo "⚠️  VM is not running. Starting VM..."
    gcloud compute instances start $VM \
        --zone=$ZONE \
        --project=$PROJECT
    echo "Waiting 30 seconds for VM to start..."
    sleep 30
fi

# 1. Create necessary directories on VM
echo ""
echo "📁 Creating directories on VM..."
gcloud compute ssh $VM --zone=$ZONE --project=$PROJECT --command='
    mkdir -p /opt/sundai-bot/logs
    mkdir -p /opt/sundai-bot/database
    mkdir -p /opt/sundai-bot/generated_images
'

# 2. Upload code
echo ""
echo "📤 Uploading code to VM..."
gcloud compute scp --recurse \
    --zone=$ZONE \
    --project=$PROJECT \
    src/ api/ database/ pyproject.toml .env \
    root@$VM:/opt/sundai-bot/ 2>/dev/null || \
gcloud compute scp --recurse \
    --zone=$ZONE \
    --project=$PROJECT \
    src/ api/ database/ pyproject.toml \
    root@$VM:/opt/sundai-bot/

# 3. Install system dependencies
echo ""
echo "🔧 Installing system dependencies..."
gcloud compute ssh $VM --zone=$ZONE --project=$PROJECT --command='
    apt-get update
    apt-get install -y python3.13 python3.13-venv sqlite3 libsqlite3-dev curl
    python3.13 --version
    sqlite3 --version
'

# 4. Setup Python environment with uv
echo ""
echo "🐍 Setting up Python environment..."
gcloud compute ssh $VM --zone=$ZONE --project=$PROJECT --command='
    cd /opt/sundai-bot

    # Install uv if not present
    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
    fi

    # Create virtual environment and install dependencies
    python3.13 -m venv .venv
    .venv/bin/pip install --upgrade pip setuptools wheel
    .venv/bin/pip install -r <(uv pip compile pyproject.toml 2>/dev/null || echo "fastapi uvicorn pydantic-settings python-multipart aiosqlite")
'

# 5. Initialize database
echo ""
echo "🗄️  Initializing database..."
gcloud compute ssh $VM --zone=$ZONE --project=$PROJECT --command='
    cd /opt/sundai-bot
    .venv/bin/python << "EOF"
from api.database import init_db
try:
    init_db()
    print("✓ Database initialized successfully")
except Exception as e:
    print(f"✗ Database initialization failed: {e}")
    exit(1)
EOF
'

# 6. Deploy systemd service
echo ""
echo "⚙️  Configuring systemd service..."
gcloud compute scp \
    --zone=$ZONE \
    --project=$PROJECT \
    deployment/sundai-api.service \
    root@$VM:/etc/systemd/system/

gcloud compute ssh $VM --zone=$ZONE --project=$PROJECT --command='
    systemctl daemon-reload
    systemctl enable sundai-api.service
    systemctl restart sundai-api.service
    echo "Waiting for API to start..."
    sleep 3
    systemctl status sundai-api.service --no-pager
'

# 7. Get external IP
echo ""
echo "🔍 Retrieving external IP..."
EXTERNAL_IP=$(gcloud compute instances describe $VM \
    --zone=$ZONE \
    --project=$PROJECT \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

if [ -z "$EXTERNAL_IP" ]; then
    echo "⚠️  Could not retrieve external IP. Checking VM status..."
    gcloud compute instances describe $VM --zone=$ZONE --project=$PROJECT
else
    echo ""
    echo "✅ Deployment Complete!"
    echo ""
    echo "📍 API Location:"
    echo "   Server IP: $EXTERNAL_IP"
    echo "   API URL:   http://$EXTERNAL_IP:8000"
    echo "   Docs:      http://$EXTERNAL_IP:8000/docs"
    echo "   Health:    http://$EXTERNAL_IP:8000/health"
    echo ""
    echo "🧪 Quick Test:"
    echo "   curl http://$EXTERNAL_IP:8000/health"
    echo ""
    echo "📊 View Logs:"
    echo "   gcloud compute ssh $VM --zone=$ZONE --project=$PROJECT --command='tail -f /opt/sundai-bot/logs/api.log'"
fi
