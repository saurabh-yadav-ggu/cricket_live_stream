#!/usr/bin/env bash
# ==============================================================================
# StreamBox - AWS EC2 / Lightsail Automated Setup & Deployment Script
# Tested on: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo "🚀 Starting StreamBox AWS Deployment Setup..."
echo "=========================================================="

# 1. Update and install prerequisites
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release git ufw nginx

# 2. Install official Docker Engine and Docker Compose Plugin
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker Engine..."
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo systemctl enable --now docker
    sudo usermod -aG docker "$USER" || true
fi

# 3. Configure Nginx Reverse Proxy
echo "🌐 Configuring Nginx reverse proxy..."
if [ -f "./nginx.conf" ]; then
    sudo cp ./nginx.conf /etc/nginx/sites-available/streambox
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo ln -sf /etc/nginx/sites-available/streambox /etc/nginx/sites-enabled/streambox
    sudo nginx -t && sudo systemctl reload nginx
fi

# 4. Configure UFW Firewall rules
echo "🛡️ Configuring Firewall rules (Ports 22, 80, 443)..."
sudo ufw allow 22/tcp || true
sudo ufw allow 80/tcp || true
sudo ufw allow 443/tcp || true
sudo ufw allow 8000/tcp || true
sudo ufw --force enable || true

# 5. Build and launch StreamBox via Docker Compose
echo "🐳 Launching StreamBox container..."
docker compose down || true
docker compose up -d --build

# 6. Verify healthcheck
echo "⏳ Verifying application health..."
sleep 5
if curl -s http://127.0.0.1:8000/health | grep -q "healthy"; then
    echo "✅ StreamBox is successfully running and healthy!"
    echo "Access your streaming player at: http://$(curl -s http://checkip.amazonaws.com)"
else
    echo "⚠️ StreamBox started, check container logs with: docker compose logs -f"
fi
