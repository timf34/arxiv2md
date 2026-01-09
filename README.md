# arxiv2md

Convert arXiv HTML papers into clean Markdown suitable for LLM context windows. This repo contains:
- A FastAPI web app (local-first) that mirrors the gitingest UX.
- A CLI for one-off conversions.

## Requirements
- Python 3.10+

## Local Web App
1) Create a virtual environment and install server deps:
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e .[server]
```

2) Run the web server from the repo root:
```bash
uvicorn server.main:app --reload --app-dir src
```

3) Open:
```
http://127.0.0.1:8000
```

## CLI
1) Install the CLI:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # or source .venv/bin/activate
pip install -e .
```

2) Run:
```bash
arxiv2md 2501.11120v1 -o -
```

Common flags:
```bash
arxiv2md 2501.11120v1 \
  --remove-refs \
  --remove-toc \
  --section-filter-mode include \
  --sections "Abstract,Introduction" \
  -o -
```
Include the section tree before the content:
```bash
arxiv2md 2501.11120v1 --include-tree -o -
```

## Configuration
Environment variables (optional):
- ARXIV2MD_CACHE_PATH (default: .arxiv2md_cache)
- ARXIV2MD_CACHE_TTL_SECONDS (default: 86400)
- ARXIV2MD_FETCH_TIMEOUT_S (default: 10.0)
- ARXIV2MD_FETCH_MAX_RETRIES (default: 2)
- ARXIV2MD_FETCH_BACKOFF_S (default: 0.5)
- ARXIV2MD_USER_AGENT (default: arxiv2md/0.1 (+https://github.com/arxiv2md/arxiv2md))

## Tests
```bash
pip install -e .[dev]
pytest tests
```

## Deployment

For production deployment to DigitalOcean with Docker, Nginx, and SSL:

**Quick start:**
```bash
ssh root@YOUR_DROPLET_IP
git clone https://github.com/timf34/arxiv2md.git /root/arxiv2md
cd /root/arxiv2md
chmod +x deploy.sh
sudo ./deploy.sh
```

**Documentation:**
- **Step-by-step guide**: [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) - Complete walkthrough
- **Detailed reference**: [DIGITALOCEAN_DEPLOYMENT.md](DIGITALOCEAN_DEPLOYMENT.md) - Full documentation
- **Quick commands**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Common operations

**Automated deployment:**
See [.github/workflows/deploy.yml](.github/workflows/deploy.yml) for GitHub Actions setup.

## Thanks to...

Gitingest for paving the way and being a great tool! https://github.com/coderamp-labs/gitingest