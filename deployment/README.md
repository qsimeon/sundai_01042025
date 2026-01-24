# Sundai API - GCP Deployment Guide

## Quick Start (After Initial Deployment)

### ✅ Start the Server
```bash
./deployment/restart_api.sh
```

This will:
1. Start the VM
2. Wait for it to boot
3. Verify the API is running
4. Show you the URL to access it

### ❌ Stop the Server (Save Money!)
```bash
gcloud compute instances stop sundai-api-server \
    --zone=us-central1-a \
    --project=sundaiiap2026 \
    --quiet
```

**Cost Savings:**
- Running VM: ~$50/month
- Stopped VM: ~$5/month (just disk storage)

---

## System Details

### GCP Project
- **Project ID**: sundaiiap2026
- **VM Name**: sundai-api-server
- **Machine Type**: e2-standard-2 (2 vCPU, 8GB RAM)
- **Zone**: us-central1-a
- **Region**: Central (Iowa, USA)

### API Server
- **Port**: 8000
- **Framework**: FastAPI
- **Database**: SQLite at `/opt/sundai-bot/database/sundai.db`
- **Service Manager**: systemd
- **Service Name**: sundai-api.service

### Key Directories on VM
```
/opt/sundai-bot/
├── api/                          # FastAPI application
├── src/                          # Your original code
├── database/                     # SQLite database
├── logs/                         # API logs
├── generated_images/             # Generated images
├── .venv/                        # Python virtual environment
├── pyproject.toml               # Dependencies
└── sundai-api.service           # Systemd configuration
```

---

## Common Tasks

### 📊 Check API Status
```bash
gcloud compute instances describe sundai-api-server \
    --zone=us-central1-a \
    --project=sundaiiap2026
```

### 📋 View API Logs
```bash
gcloud compute ssh sundai-api-server \
    --zone=us-central1-a \
    --project=sundaiiap2026 \
    --command='sudo tail -f /opt/sundai-bot/logs/api.log'
```

### 🔧 SSH into VM (Debug)
```bash
gcloud compute ssh sundai-api-server \
    --zone=us-central1-a \
    --project=sundaiiap2026
```

Once SSH'd in:
```bash
# Check service status
sudo systemctl status sundai-api.service

# Restart service
sudo systemctl restart sundai-api.service

# View recent logs
sudo journalctl -u sundai-api.service -n 50
```

### 📤 Upload Code Changes
After making code changes locally, upload them:

```bash
# Copy updated files to VM
gcloud compute scp --recurse \
    src/ api/ database/ \
    sundai-api-server:/tmp/sundai-updates/ \
    --zone=us-central1-a \
    --project=sundaiiap2026

# SSH in and move files
gcloud compute ssh sundai-api-server \
    --zone=us-central1-a \
    --project=sundaiiap2026 \
    --command='sudo cp -r /tmp/sundai-updates/* /opt/sundai-bot/ && sudo systemctl restart sundai-api.service'
```

### 💾 Backup Database
```bash
gcloud compute scp \
    sundai-api-server:/opt/sundai-bot/database/sundai.db \
    ./backups/sundai-$(date +%Y%m%d).db \
    --zone=us-central1-a \
    --project=sundaiiap2026
```

---

## Initial Deployment (First Time Setup)

If you need to redeploy from scratch:

```bash
./deployment/deploy_api_simple.sh
```

This script will:
1. Create directories on the VM
2. Upload all code files
3. Install Python and dependencies
4. Initialize the database
5. Configure systemd service
6. Start the API

**Takes about 5-10 minutes depending on internet speed.**

---

## Environment Variables

The API reads from `.env` file. Important settings:

```env
# API Configuration
API_KEY=dev-key-change-in-production

# External Services (your existing .env)
OPENAI_API_KEY=...
REPLICATE_API_TOKEN=...
USE_OPENROUTER=true
OPENROUTER_API_KEY=...
```

To update environment variables:
1. Edit `.env` locally
2. Upload it: `gcloud compute scp .env sundai-api-server:/opt/sundai-bot/`
3. Restart service: `gcloud compute ssh ... --command='sudo systemctl restart sundai-api.service'`

---

## Costs

### Monthly Estimate (Running)
| Service | Cost |
|---------|------|
| Compute (e2-standard-2) | $50 |
| Storage (30GB disk) | $5 |
| Network egress | $1 |
| External APIs | $10-25 |
| **Total** | **$66-81** |

### Monthly (Stopped)
| Service | Cost |
|---------|------|
| Storage (30GB disk) | $5 |
| **Total** | **~$5** |

**Savings**: Stop the VM when not in use to save ~$50-75/month!

---

## Troubleshooting

### API Not Responding
```bash
# Check if VM is running
gcloud compute instances describe sundai-api-server \
    --format='get(status)'

# Check if service is running
gcloud compute ssh sundai-api-server \
    --command='sudo systemctl status sundai-api.service'

# View error logs
gcloud compute ssh sundai-api-server \
    --command='sudo journalctl -u sundai-api.service -n 100 | tail -50'
```

### Database Errors
```bash
# Check database file exists
gcloud compute ssh sundai-api-server \
    --command='ls -lh /opt/sundai-bot/database/sundai.db'

# Reinitialize database
gcloud compute ssh sundai-api-server \
    --command='cd /opt/sundai-bot && DATABASE_PATH=/opt/sundai-bot/database/sundai.db .venv/bin/python << "EOF"
from api.database import init_db
init_db()
print("Database reinitialized")
EOF'
```

### Out of Disk Space
Check disk usage:
```bash
gcloud compute ssh sundai-api-server \
    --command='df -h'
```

Clean up generated images if needed:
```bash
gcloud compute ssh sundai-api-server \
    --command='rm -rf /opt/sundai-bot/generated_images/*.png'
```

---

## Useful Links

- **GCP Console**: https://console.cloud.google.com
- **Compute Instances**: https://console.cloud.google.com/compute/instances
- **API Documentation**: http://34.61.132.208:8000/docs (when running)
- **Billing**: https://console.cloud.google.com/billing

---

## Next Steps

### Security
- [ ] Change `API_KEY` to a strong secret
- [ ] Store secrets in GCP Secret Manager
- [ ] Enable HTTPS with Cloud Load Balancer
- [ ] Restrict firewall to specific IPs if needed

### Monitoring
- [ ] Set up Cloud Logging
- [ ] Configure alerts for service failures
- [ ] Monitor disk space and API usage

### Scaling
- [ ] Migrate to PostgreSQL for larger deployments
- [ ] Add caching (Redis)
- [ ] Consider Cloud Run for serverless option

---

## Cheat Sheet

```bash
# Start server
./deployment/restart_api.sh

# Stop server (save money!)
gcloud compute instances stop sundai-api-server --zone=us-central1-a --project=sundaiiap2026 --quiet

# Check status
gcloud compute instances describe sundai-api-server --zone=us-central1-a --project=sundaiiap2026 | grep -i status

# View logs
gcloud compute ssh sundai-api-server --zone=us-central1-a --project=sundaiiap2026 --command='sudo tail -50 /opt/sundai-bot/logs/api.log'

# SSH into VM
gcloud compute ssh sundai-api-server --zone=us-central1-a --project=sundaiiap2026

# Test API (when running)
curl http://34.61.132.208:8000/health
```

---

**Created**: January 23, 2026
**Last Updated**: January 23, 2026
