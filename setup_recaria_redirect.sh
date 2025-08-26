#!/bin/bash

# Setup script for recaria.org to UNIBOS redirect
set -e

echo "🚀 Setting up recaria.org redirect to UNIBOS..."

# Create nginx configuration for recaria.org
cat << 'EOF' > /tmp/recaria.org.conf
server {
    listen 80;
    listen [::]:80;
    server_name recaria.org www.recaria.org;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logs
    access_log /var/log/nginx/recaria.org.access.log;
    error_log /var/log/nginx/recaria.org.error.log;

    # Proxy to UNIBOS Django backend
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for real-time features
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if needed)
    location /static/ {
        alias /home/ubuntu/unibos/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/ubuntu/unibos/backend/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
EOF

echo "📝 Nginx configuration created"

# Commands to run on server
echo ""
echo "==================================================================="
echo "📋 RUN THESE COMMANDS ON ROCKSTEADY SERVER:"
echo "==================================================================="
echo ""
echo "# 1. Copy nginx configuration:"
echo "sudo cp /tmp/recaria.org.conf /etc/nginx/sites-available/"
echo "sudo ln -sf /etc/nginx/sites-available/recaria.org.conf /etc/nginx/sites-enabled/"
echo ""
echo "# 2. Test nginx configuration:"
echo "sudo nginx -t"
echo ""
echo "# 3. Reload nginx:"
echo "sudo systemctl reload nginx"
echo ""
echo "# 4. Install SSL certificate (optional but recommended):"
echo "sudo apt-get update"
echo "sudo apt-get install -y certbot python3-certbot-nginx"
echo "sudo certbot --nginx -d recaria.org -d www.recaria.org"
echo ""
echo "==================================================================="
echo ""