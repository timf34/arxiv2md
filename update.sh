#!/bin/bash
set -e

# Quick update script for arxiv2md
# Run this after pushing changes to GitHub

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_DIR="/root/arxiv2md"

echo -e "${GREEN}Updating arxiv2md...${NC}"

cd $APP_DIR

echo -e "${YELLOW}[1/4] Pulling latest changes...${NC}"
git pull origin main

echo -e "${YELLOW}[2/4] Rebuilding Docker image...${NC}"
docker-compose build

echo -e "${YELLOW}[3/4] Restarting containers...${NC}"
docker-compose up -d

echo -e "${YELLOW}[4/4] Checking health...${NC}"
sleep 5
curl -f http://localhost:8000/health && echo -e "\n${GREEN}Update complete!${NC}" || echo -e "\n${RED}Health check failed!${NC}"

echo ""
echo -e "${GREEN}View logs with: docker-compose logs -f${NC}"
