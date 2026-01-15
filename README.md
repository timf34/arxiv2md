# arxiv2md

<div align="center">
  <img src="assets/image.png" alt="arxiv2md" width="400">

  **Convert arXiv papers to clean Markdown for LLMs**

  [Live Demo](https://arxiv2md.org) · [Documentation](DIGITALOCEAN_DEPLOYMENT.md) · [Report Bug](https://github.com/timf34/arxiv2md/issues)
</div>

---

## Why?

I got tired of copy-pasting arXiv PDFs/HTML into LLMs and fighting references, TOCs, and token bloat. So I made [gitingest.com](https://gitingest.com) but for arXiv papers.

**The trick:** Just append `2md` to any arXiv URL:

```
https://arxiv.org/abs/2501.11120v1  →  https://arxiv2md.org/abs/2501.11120v1
```

## Features

- **Zero friction**: Append `2md` to any arXiv URL (works with `/abs/`, `/html/`, `/pdf/`)
- **Section filtering**: Remove references, appendix, or select only specific sections
- **Clean output**: No messy PDFs or broken formatting
- **Section tree**: Visual overview - click to include/exclude sections
- **LLM-optimized**: Token counts, clean citations
- **Fast**: Cached results, direct HTML parsing

## How It Works

arxiv2md is fast because it takes advantage of arXiv's HTML format for papers. Instead of parsing PDFs (slow, error-prone), we directly parse the structured HTML that arXiv provides for newer papers. This gives us:

- Clean section boundaries and hierarchies
- Proper math rendering (MathML → Markdown)
- Reliable table extraction
- Fast processing (no OCR or PDF parsing)

The HTML is converted to Markdown using BeautifulSoup4, with custom logic for handling citations, math equations, and paper structure.

## Usage

### Web App

Visit [arxiv2md.org](https://arxiv2md.org) and paste any arXiv URL, or append `2md` to an arXiv URL in your browser.

### CLI

```bash
# Install
pip install -e .

# Basic usage
arxiv2md 2501.11120v1 -o paper.md

# Only include specific sections
arxiv2md 2501.11120v1 --section-filter-mode include --sections "Abstract,Introduction" -o -

# Remove references and TOC
arxiv2md 2501.11120v1 --remove-refs --remove-toc -o -
```

### API

Two GET endpoints for programmatic access:

```bash
# JSON response (with metadata)
curl "https://arxiv2md.org/api/json?url=2312.00752"

# Raw markdown
curl "https://arxiv2md.org/api/markdown?url=2312.00752"
```

**Parameters:**
| Param | Default | Description |
|-------|---------|-------------|
| `url` | required | arXiv URL or ID |
| `remove_refs` | `true` | Remove references |
| `remove_toc` | `true` | Remove table of contents |
| `remove_citations` | `true` | Remove inline citations |

**Rate limit:** 30 requests/minute per IP.

## Section Filtering

**Exclude mode** (default): Remove unwanted sections like References or Appendix
**Include mode**: Extract only what you need like "Abstract,Introduction,Conclusion"

The section tree in the UI lets you click sections to toggle them in/out.

## Development

```bash
# Run locally
python -m venv .venv
source .venv/bin/activate
pip install -e .[server]
uvicorn server.main:app --reload --app-dir src

# Run tests
pip install -e .[dev]
pytest tests
```

## Deployment

One-command deployment to DigitalOcean with Docker, Nginx, and SSL:

```bash
git clone https://github.com/timf34/arxiv2md.git /root/arxiv2md
cd /root/arxiv2md
chmod +x deploy.sh
sudo ./deploy.sh
```

See [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) for details.

## Tech Stack

- FastAPI backend with BeautifulSoup4 for HTML parsing
- Tailwind CSS frontend
- Docker + Nginx + Let's Encrypt for deployment
- Local file cache with TTL

## Contributing

PRs welcome! Fork the repo, create a feature branch, add tests if applicable, and submit a PR.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Inspired by [gitingest](https://github.com/coderamp-labs/gitingest) for digesting Git repos.

Star this repo if you find it useful!