#!/usr/bin/env bash
# EduGenie AI Public Cloudflare Tunnel Launcher
# Exposes local port 8085 to an enterprise-grade Cloudflare HTTPS URL

PORT=${1:-8085}
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo " 🌐 Launching EduGenie Cloudflare HTTPS Tunnel (Port $PORT)"
echo "=========================================================="

if [ -f "./cloudflared" ]; then
  ./cloudflared tunnel --url "http://127.0.0.1:$PORT"
else
  ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=15 -R 80:127.0.0.1:$PORT serveo.net
fi
