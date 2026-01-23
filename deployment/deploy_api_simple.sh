#!/bin/bash
set -e

PROJECT="sundaiiap2026"
VM="sundai-api-server"
ZONE="us-central1-a"

echo "🚀 Deploying Sundai FastAPI..."
echo ""

# Check if VM is running
echo "Checking VM status..."
gcloud compute instances describe $VM --zone=$ZONE --project=$PROJECT --format='get(status)' || echo "VM not found"

# Prepare deployment package
echo "📦 Preparing deployment package..."
mkdir -p /tmp/sundai-deploy
cp -r src/ api/ database/ pyproject.toml /tmp/sundai-deploy/
cp deployment/sundai-api.service /tmp/sundai-deploy/
cp .env /tmp/sundai-deploy/ 2>/dev/null || echo "  (no .env file)"

# Create deployment script that runs on VM
cat > /tmp/deploy_on_vm.sh << 'VMSCRIPT'
#!/bin/bash
set -e

echo "Starting deployment on VM..."
echo ""

# 1. Create directories
echo "📁 Creating directories..."
sudo mkdir -p /opt/sundai-bot/{logs,database,generated_images}

# 2. Copy files
echo "📤 Setting up files..."
sudo cp -r /tmp/sundai-deploy/* /opt/sundai-bot/
sudo chown -R root:root /opt/sundai-bot

# 3. Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get update > /dev/null 2>&1
sudo apt-get install -y python3.13 python3.13-venv sqlite3 libsqlite3-dev curl > /dev/null 2>&1

# 4. Setup Python environment
echo "🐍 Setting up Python environment..."
cd /opt/sundai-bot
python3.13 -m venv .venv

# Install pip and dependencies
.venv/bin/pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Install FastAPI and dependencies
.venv/bin/pip install \
    fastapi>=0.109.0 \
    uvicorn[standard]>=0.27.0 \
    pydantic-settings>=2.1.0 \
    python-multipart>=0.0.6 \
    aiosqlite>=0.19.0 \
    anthropic \
    google-cloud-secret-manager \
    mastodon-py \
    notion-client \
    openai \
    pydantic \
    python-dotenv \
    python-telegram-bot \
    replicate \
    requests \
    google-generativeai > /dev/null 2>&1

# 5. Initialize database
echo "🗄️  Initializing database..."
cd /opt/sundai-bot
.venv/bin/python << 'PYEOF'
from api.database import init_db
try:
    init_db()
    print("✓ Database initialized")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)
PYEOF

# 6. Deploy systemd service
echo "⚙️  Configuring systemd service..."
sudo cp /opt/sundai-bot/sundai-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sundai-api.service
sudo systemctl restart sundai-api.service

# Wait for service to start
sleep 2

# 7. Check service status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service status:"
sudo systemctl status sundai-api.service --no-pager

VMSCRIPT

# Upload deployment script and files to VM
echo "📤 Uploading to VM..."
gcloud compute scp --recurse /tmp/sundai-deploy $VM:/tmp/ --zone=$ZONE --project=$PROJECT
gcloud compute scp /tmp/deploy_on_vm.sh $VM:/tmp/ --zone=$ZONE --project=$PROJECT

# Run deployment script on VM
echo "Running deployment script on VM..."
gcloud compute ssh $VM --zone=$ZONE --project=$PROJECT << 'SSHEOF'
bash /tmp/deploy_on_vm.sh
SSHEOF

# Get external IP and display info
echo ""
echo "🔍 Retrieving external IP..."
EXTERNAL_IP=$(gcloud compute instances describe $VM \
    --zone=$ZONE \
    --project=$PROJECT \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

if [ -z "$EXTERNAL_IP" ]; then
    echo "⚠️  Could not retrieve external IP"
else
    echo ""
    echo "📍 API Server is running!"
    echo ""
    echo "  Server IP: $EXTERNAL_IP"
    echo "  API URL:   http://$EXTERNAL_IP:8000"
    echo "  Docs:      http://$EXTERNAL_IP:8000/docs"
    echo "  Health:    http://$EXTERNAL_IP:8000/health"
    echo ""
    echo "🧪 Quick Test:"
    echo "  curl http://$EXTERNAL_IP:8000/health"
    echo ""
    echo "📊 View Logs:"
    echo "  gcloud compute ssh $VM --zone=$ZONE --project=$PROJECT --command='sudo tail -f /opt/sundai-bot/logs/api.log'"
fi

# Cleanup
echo ""
echo "🧹 Cleaning up temporary files..."
rm -rf /tmp/sundai-deploy /tmp/deploy_on_vm.sh
