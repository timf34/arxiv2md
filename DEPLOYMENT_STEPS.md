# Deployment Steps for arxiv2md.org

Complete step-by-step guide to deploy arxiv2md to your DigitalOcean droplet.

## Server Information

- **Droplet**: ubuntu-s-1vcpu-1gb-amd-lon1-01
- **IP Address**: 209.97.185.144
- **Location**: LON1 (London)
- **Domain**: arxiv2md.org
- **Email**: timf34@gmail.com

---

## Step 1: Configure DNS

Before deploying, point your domain to the droplet.

### Add DNS Records

Go to your domain registrar (where you bought arxiv2md.org) and add these DNS records:

```
Type: A
Name: @
Value: 209.97.185.144
TTL: 3600

Type: A
Name: www
Value: 209.97.185.144
TTL: 3600
```

**Wait 5-30 minutes for DNS propagation.** Verify with:
```bash
dig arxiv2md.org
dig www.arxiv2md.org
```

---

## Step 2: Push Deployment Files to GitHub

From your local machine:

```bash
# Make deploy scripts executable
chmod +x deploy.sh update.sh

# Add all deployment files
git add .

# Commit
git commit -m "Add DigitalOcean deployment configuration"

# Push to GitHub
git push origin main
```

---

## Step 3: Initial Deployment to Droplet

### Connect to your droplet
```bash
ssh root@209.97.185.144
```

### Run the automated deployment script
```bash
# Download and run deploy script
apt-get update
apt-get install -y git
git clone https://github.com/timf34/arxiv2md.git /root/arxiv2md
cd /root/arxiv2md

# Make script executable and run it
chmod +x deploy.sh
sudo ./deploy.sh
```

The script will:
- ✅ Install Docker & Docker Compose
- ✅ Install Nginx
- ✅ Install Certbot (SSL)
- ✅ Build Docker image
- ✅ Start application
- ✅ Configure Nginx
- ✅ Setup systemd service
- ✅ Setup SSL certificates (interactive prompt)
- ✅ Configure auto-renewal

### When prompted for SSL setup:
1. Make sure DNS is already pointing to your droplet
2. Press `y` to setup SSL
3. Certbot will automatically configure HTTPS

---

## Step 4: Verify Deployment

### Check application health
```bash
curl http://localhost:8000/health
```

### Check Docker containers
```bash
docker-compose ps
```

### Check Nginx
```bash
systemctl status nginx
```

### Test your domain
Visit `https://arxiv2md.org` in your browser - you should see your app!

---

## Step 5: Setup GitHub Actions (Optional but Recommended)

This enables automatic deployment when you push to GitHub.

### 5.1: Generate SSH Key on Droplet

On your droplet:
```bash
# Generate a dedicated deployment key
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# View the private key (you'll need this for GitHub)
cat ~/.ssh/github_actions_deploy

# Add the public key to authorized_keys
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys
```

### 5.2: Add Secrets to GitHub

Go to your GitHub repository: `https://github.com/timf34/arxiv2md/settings/secrets/actions`

Click "New repository secret" and add these three secrets:

**Secret 1: DO_HOST**
```
209.97.185.144
```

**Secret 2: DO_USERNAME**
```
root
```

**Secret 3: DO_SSH_KEY**
```
[Paste the entire private key from ~/.ssh/github_actions_deploy]
```

### 5.3: Test GitHub Actions

Push a small change to trigger the workflow:

```bash
# Make a small change
echo "# Testing deployment" >> README.md

# Commit and push
git add README.md
git commit -m "Test automated deployment"
git push origin main
```

Go to `https://github.com/timf34/arxiv2md/actions` to watch the deployment.

---

## Future Deployments

After initial setup, updating is simple:

### Method 1: Automatic (GitHub Actions)
Just push to main:
```bash
git push origin main
```

GitHub Actions will automatically deploy to your droplet.

### Method 2: Manual (SSH)
SSH to droplet and run update script:
```bash
ssh root@209.97.185.144
cd /root/arxiv2md
sudo ./update.sh
```

---

## Useful Commands

### View logs
```bash
# Application logs
docker-compose logs -f

# Nginx access logs
tail -f /var/log/nginx/arxiv2md_access.log

# Nginx error logs
tail -f /var/log/nginx/arxiv2md_error.log

# Systemd logs
journalctl -u arxiv2md -f
```

### Restart services
```bash
# Restart application
systemctl restart arxiv2md

# Restart Nginx
systemctl restart nginx

# Restart just Docker containers
docker-compose restart
```

### Check SSL certificate
```bash
# View certificate info
certbot certificates

# Test renewal (dry run)
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal
```

---

## Troubleshooting

### Application won't start
```bash
docker-compose logs
docker-compose down
docker-compose up -d
```

### SSL certificate issues
```bash
# Check if DNS is propagating
dig arxiv2md.org

# Try obtaining certificate again
certbot --nginx -d arxiv2md.org -d www.arxiv2md.org
```

### Nginx errors
```bash
# Test config
nginx -t

# Check error logs
tail -f /var/log/nginx/error.log

# Restart
systemctl restart nginx
```

### GitHub Actions failing
1. Verify secrets are set correctly in GitHub
2. Check the Actions tab for error details
3. Ensure SSH key has proper permissions on droplet

---

## Security Checklist

After deployment, harden security:

```bash
# Setup firewall
apt-get install ufw
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# Install fail2ban
apt-get install fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Enable automatic security updates
apt-get install unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades
```

---

## Monitoring

### Setup UptimeRobot (Optional)
1. Go to https://uptimerobot.com
2. Add monitor for `https://arxiv2md.org/health`
3. Get notified if site goes down

### Check resource usage
```bash
# Docker stats
docker stats

# System resources
htop
df -h
free -h
```

---

## Next Steps

After successful deployment:

1. ✅ Test all functionality on production
2. ✅ Monitor logs for any errors
3. ✅ Setup UptimeRobot for monitoring
4. ✅ Consider adding rate limiting (if needed)
5. ✅ Plan API/MCP server architecture for future

---

## Support

For detailed deployment documentation, see `DIGITALOCEAN_DEPLOYMENT.md`.

For issues or questions:
- GitHub Issues: https://github.com/timf34/arxiv2md/issues
- Repository: https://github.com/timf34/arxiv2md
