#!/bin/bash
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color


echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  arxiv2md Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Configuration
DOMAIN="arxiv2md.org"
EMAIL="timf34@gmail.com"
APP_DIR="/root/arxiv2md"
REPO_URL="https://github.com/timf34/arxiv2md.git"

echo -e "${YELLOW}Domain: $DOMAIN${NC}"
echo -e "${YELLOW}App directory: $APP_DIR${NC}"

# Update system
echo -e "${GREEN}[1/8] Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install Docker
echo -e "${GREEN}[2/8] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
    echo -e "${GREEN}Docker installed successfully${NC}"
else
    echo -e "${YELLOW}Docker already installed${NC}"
fi

# Install Docker Compose
echo -e "${GREEN}[3/8] Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose installed successfully${NC}"
else
    echo -e "${YELLOW}Docker Compose already installed${NC}"
fi

# Install Nginx
echo -e "${GREEN}[4/8] Installing Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
    systemctl enable nginx
    echo -e "${GREEN}Nginx installed successfully${NC}"
else
    echo -e "${YELLOW}Nginx already installed${NC}"
fi

# Install Certbot
echo -e "${GREEN}[5/8] Installing Certbot for SSL...${NC}"
if ! command -v certbot &> /dev/null; then
    apt-get install -y certbot python3-certbot-nginx
    echo -e "${GREEN}Certbot installed successfully${NC}"
else
    echo -e "${YELLOW}Certbot already installed${NC}"
fi

# Clone/update repository
echo -e "${GREEN}[6/8] Setting up application...${NC}"
if [ -d "$APP_DIR" ]; then
    echo -e "${YELLOW}Application directory exists, updating...${NC}"
    cd $APP_DIR
    git pull origin main
else
    echo -e "${GREEN}Cloning repository...${NC}"
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# Build and start Docker container
echo -e "${GREEN}[7/8] Building and starting Docker containers...${NC}"
docker-compose build
docker-compose up -d

# Wait for application to start
echo -e "${YELLOW}Waiting for application to start...${NC}"
sleep 10

# Test health endpoint
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}Application is healthy!${NC}"
else
    echo -e "${RED}Warning: Health check failed. Check logs with: docker-compose logs${NC}"
fi

# Setup Nginx
echo -e "${GREEN}[8/8] Configuring Nginx...${NC}"
cp nginx.conf /etc/nginx/sites-available/arxiv2md
ln -sf /etc/nginx/sites-available/arxiv2md /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo -e "${GREEN}Nginx configured successfully${NC}"
else
    echo -e "${RED}Nginx configuration error!${NC}"
    exit 1
fi

# Setup systemd service
echo -e "${GREEN}Setting up systemd service...${NC}"
cp arxiv2md.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable arxiv2md
echo -e "${GREEN}Systemd service configured${NC}"

# Setup SSL with Let's Encrypt
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}SSL Setup${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Before setting up SSL, make sure:${NC}"
echo -e "${YELLOW}1. Your domain ($DOMAIN) points to this server${NC}"
echo -e "${YELLOW}2. You've updated EMAIL in this script${NC}"
echo ""
read -p "Do you want to setup SSL now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Modify nginx config to comment out SSL lines temporarily
    sed -i 's/listen 443 ssl/#listen 443 ssl/g' /etc/nginx/sites-available/arxiv2md
    sed -i 's/ssl_certificate/#ssl_certificate/g' /etc/nginx/sites-available/arxiv2md
    systemctl reload nginx

    # Get SSL certificate
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $EMAIL

    # Restore original nginx config
    cp nginx.conf /etc/nginx/sites-available/arxiv2md
    systemctl reload nginx

    echo -e "${GREEN}SSL configured successfully!${NC}"
else
    echo -e "${YELLOW}Skipping SSL setup. Run certbot manually later:${NC}"
    echo -e "${YELLOW}certbot --nginx -d $DOMAIN -d www.$DOMAIN${NC}"
fi

# Setup automatic SSL renewal
echo -e "${GREEN}Setting up automatic SSL renewal...${NC}"
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --deploy-hook 'systemctl reload nginx'") | crontab -

# Final status
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Application Status:${NC}"
docker-compose ps
echo ""
echo -e "${GREEN}Useful Commands:${NC}"
echo -e "  View logs:           ${YELLOW}docker-compose logs -f${NC}"
echo -e "  Restart:             ${YELLOW}systemctl restart arxiv2md${NC}"
echo -e "  Stop:                ${YELLOW}systemctl stop arxiv2md${NC}"
echo -e "  Nginx reload:        ${YELLOW}systemctl reload nginx${NC}"
echo -e "  Check health:        ${YELLOW}curl http://localhost:8001/health${NC}"
echo ""
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${GREEN}Your site is available at: https://$DOMAIN${NC}"
else
    echo -e "${YELLOW}Your site is available at: http://$DOMAIN${NC}"
    echo -e "${YELLOW}Remember to setup SSL with: certbot --nginx -d $DOMAIN -d www.$DOMAIN${NC}"
fi
