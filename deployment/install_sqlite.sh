#!/bin/bash
# SQLite installation reference script
# This is called by deploy_api.sh automatically

set -e

echo "Installing SQLite3..."

apt-get update
apt-get install -y sqlite3 libsqlite3-dev

# Verify installation
echo "Verifying SQLite installation..."
sqlite3 --version

echo "✅ SQLite installation complete"
