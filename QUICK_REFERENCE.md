# Quick Reference Card

Essential commands for managing arxiv2md on DigitalOcean.

## SSH Connection
```bash
ssh root@209.97.185.144
```

## Update Application (After Pushing to GitHub)
```bash
cd /root/arxiv2md
sudo ./update.sh
```

## View Logs
```bash
# Real-time application logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Nginx access logs
tail -f /var/log/nginx/arxiv2md_access.log

# Nginx error logs
tail -f /var/log/nginx/arxiv2md_error.log
```

## Check Status
```bash
# Application health
curl https://arxiv2md.org/health

# Docker containers
docker-compose ps

# Nginx status
systemctl status nginx

# Systemd service
systemctl status arxiv2md
```

## Restart Services
```bash
# Restart application (via systemd)
systemctl restart arxiv2md

# Restart just Docker containers
docker-compose restart

# Restart Nginx
systemctl reload nginx
```

## Emergency - Application Down
```bash
cd /root/arxiv2md

# View recent logs
docker-compose logs --tail=50

# Restart everything
docker-compose down
docker-compose up -d

# Check health
sleep 5
curl http://localhost:8000/health
```

## SSL Certificate
```bash
# Check certificate status
certbot certificates

# Renew certificate (auto-renews via cron)
certbot renew

# Test renewal process
certbot renew --dry-run
```

## Resource Monitoring
```bash
# Docker resource usage
docker stats

# System resources
htop

# Disk usage
df -h

# Memory usage
free -h
```

## GitHub Actions
Push to main branch triggers automatic deployment:
```bash
git push origin main
```

View deployment status:
https://github.com/timf34/arxiv2md/actions

## Common Issues

### "Permission denied" when running scripts
```bash
chmod +x deploy.sh update.sh
```

### DNS not resolving
```bash
# Check DNS propagation
dig arxiv2md.org

# Wait 5-30 minutes for propagation
```

### SSL certificate error
```bash
# Ensure DNS is pointing to droplet first
dig arxiv2md.org

# Then run certbot
certbot --nginx -d arxiv2md.org -d www.arxiv2md.org
```

### Docker container won't start
```bash
# Check logs for errors
docker-compose logs

# Rebuild from scratch
docker-compose down
docker system prune -a
docker-compose up -d --build
```

## File Locations

- **Application**: `/root/arxiv2md`
- **Nginx config**: `/etc/nginx/sites-available/arxiv2md`
- **SSL certificates**: `/etc/letsencrypt/live/arxiv2md.org/`
- **Systemd service**: `/etc/systemd/system/arxiv2md.service`

## Important URLs

- **Production**: https://arxiv2md.org
- **Health check**: https://arxiv2md.org/health
- **GitHub**: https://github.com/timf34/arxiv2md
- **GitHub Actions**: https://github.com/timf34/arxiv2md/actions

## Support Files

- Full deployment guide: `DEPLOYMENT_STEPS.md`
- Detailed documentation: `DIGITALOCEAN_DEPLOYMENT.md`
- Issues: https://github.com/timf34/arxiv2md/issues
