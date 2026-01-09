# DigitalOcean Droplet Deployment Guide

Complete guide for deploying arxiv2md to DigitalOcean with Docker, Nginx, and SSL.

## Prerequisites

1. **DigitalOcean Account** with a droplet created
   - Recommended: Ubuntu 22.04 LTS
   - Size: Basic $6/month (1GB RAM, 25GB SSD)
   - Location: Choose closest to your users

2. **Domain Setup**
   - Point `arxiv2md.org` A record to your droplet IP
   - Point `www.arxiv2md.org` A record to your droplet IP
   - Wait for DNS propagation (5-30 minutes)

3. **SSH Access**
   - Add your SSH key when creating the droplet
   - Test: `ssh root@YOUR_DROPLET_IP`

## Quick Deploy (Automated)

### Step 1: Connect to your droplet
```bash
ssh root@YOUR_DROPLET_IP
```

### Step 2: Update the deploy script
Before running the automated deployment, you need to update the email in the deploy script:

```bash
# Download the repository
apt-get update
apt-get install -y git
git clone https://github.com/timf34/arxiv2md.git /root/arxiv2md
cd /root/arxiv2md

# Edit deploy.sh and change the EMAIL variable
nano deploy.sh
# Change: EMAIL="your-email@example.com"
# To:     EMAIL="your@actual-email.com"
```

### Step 3: Run automated deployment
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

The script will:
- ✅ Install Docker & Docker Compose
- ✅ Install Nginx
- ✅ Install Certbot (SSL)
- ✅ Clone repository
- ✅ Build Docker image
- ✅ Start application
- ✅ Configure Nginx
- ✅ Setup systemd service
- ✅ Setup SSL certificates
- ✅ Configure auto-renewal

### Step 4: Verify deployment
```bash
# Check Docker containers
docker-compose ps

# Check application health
curl http://localhost:8000/health

# Check Nginx
systemctl status nginx

# View logs
docker-compose logs -f
```

Visit `https://arxiv2md.org` - you should see your app!

---

## Manual Deploy (Step by Step)

If you prefer manual control or automated script fails:

### 1. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Install Nginx
```bash
sudo apt-get update
sudo apt-get install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 4. Clone Repository
```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/timf34/arxiv2md.git
cd arxiv2md
```

### 5. Build and Start Application
```bash
sudo docker-compose build
sudo docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### 6. Configure Nginx
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/arxiv2md
sudo ln -s /etc/nginx/sites-available/arxiv2md /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Setup SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate (update email!)
sudo certbot --nginx -d arxiv2md.org -d www.arxiv2md.org --email your@email.com --agree-tos

# Setup auto-renewal
sudo crontab -e
# Add this line:
0 3 * * * certbot renew --quiet --deploy-hook 'systemctl reload nginx'
```

### 8. Setup Systemd Service
```bash
sudo cp arxiv2md.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable arxiv2md
sudo systemctl start arxiv2md
```

---

## Updating the Application

After pushing changes to GitHub:

```bash
ssh root@YOUR_DROPLET_IP
cd /root/arxiv2md
sudo ./update.sh
```

Or manually:
```bash
cd /root/arxiv2md
git pull origin main
docker-compose build
docker-compose up -d
```

---

## Useful Commands

### Docker
```bash
# View logs
docker-compose logs -f

# Restart containers
docker-compose restart

# Stop containers
docker-compose down

# Rebuild
docker-compose build --no-cache

# View container status
docker-compose ps
```

### Systemd
```bash
# Status
sudo systemctl status arxiv2md

# Restart
sudo systemctl restart arxiv2md

# Stop
sudo systemctl stop arxiv2md

# View logs
sudo journalctl -u arxiv2md -f
```

### Nginx
```bash
# Reload config
sudo systemctl reload nginx

# Test config
sudo nginx -t

# View logs
sudo tail -f /var/log/nginx/arxiv2md_access.log
sudo tail -f /var/log/nginx/arxiv2md_error.log
```

### SSL
```bash
# Renew certificates manually
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificate expiry
sudo certbot certificates
```

---

## Monitoring

### Health Check
```bash
curl https://arxiv2md.org/health
```

### Resource Usage
```bash
# Docker stats
docker stats

# System resources
htop
df -h
free -h
```

### Logs
```bash
# Application logs
docker-compose logs -f --tail=100

# Nginx access logs
tail -f /var/log/nginx/arxiv2md_access.log

# Nginx error logs
tail -f /var/log/nginx/arxiv2md_error.log

# System logs
journalctl -xe
```

---

## Troubleshooting

### Application won't start
```bash
# Check Docker logs
docker-compose logs

# Check if port 8000 is in use
sudo netstat -tulpn | grep 8000

# Restart everything
docker-compose down
docker-compose up -d
```

### Nginx errors
```bash
# Test config
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

### SSL issues
```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# Check nginx SSL config
sudo nano /etc/nginx/sites-available/arxiv2md
```

### Container issues
```bash
# Remove all containers and rebuild
docker-compose down
docker system prune -a
docker-compose up -d --build
```

---

## Security Hardening

### 1. Firewall (UFW)
```bash
sudo apt-get install ufw
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Fail2ban
```bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Automatic Updates
```bash
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## Performance Optimization

### Enable HTTP/2 in Nginx
Already enabled in `nginx.conf`:
```nginx
listen 443 ssl http2;
```

### Increase file upload limits
Edit `/etc/nginx/nginx.conf`:
```nginx
client_max_body_size 20M;
```

### Docker resource limits
Edit `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
```

---

## Backup Strategy

### Backup cache volume
```bash
docker run --rm -v arxiv2md_arxiv2md_cache:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/cache-backup-$(date +%Y%m%d).tar.gz /data
```

### Restore cache
```bash
docker run --rm -v arxiv2md_arxiv2md_cache:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/cache-backup-YYYYMMDD.tar.gz -C /
```

---

## Cost Estimate

### DigitalOcean Basic Droplet
- **$6/month**: 1GB RAM, 1 vCPU, 25GB SSD
- **Bandwidth**: 1TB transfer
- **Backups**: +$1.20/month (optional)

### Domain
- **$10-15/year**: .org domain

### Total: ~$7/month

---

## Next Steps

After deployment:
1. ✅ Test all functionality
2. ✅ Setup monitoring (optional: UptimeRobot, StatusPage)
3. ✅ Configure backups
4. ✅ Setup CI/CD with GitHub Actions
5. ✅ Add rate limiting (if needed)
6. ✅ Setup analytics (optional)
