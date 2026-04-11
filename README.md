# arxiv2md

<div align="center">
  <img src="assets/image.png" alt="arxiv2md" width="400">

  **arXiv papers → clean Markdown. Web app, REST API and CLI.**

  [Live Demo](https://arxiv2md.org) · [PyPI](https://pypi.org/project/arxiv2markdown/) · [Report Bug](https://github.com/timf34/arxiv2md/issues)
</div>

---

## Why?

[gitingest](https://gitingest.com) but for arXiv papers.

**The trick:** Just append `2md` to any arXiv URL:

```
https://arxiv.org/abs/2501.11120v1  →  https://arxiv2md.org/abs/2501.11120v1
```

## How It Works

Instead of parsing PDFs (slow, error-prone), arxiv2md parses the structured HTML that arXiv provides for newer papers. This means clean section boundaries, proper math (MathML → LaTeX), reliable tables, and fast processing — no OCR needed.

## Usage

### Web App

Visit [arxiv2md.org](https://arxiv2md.org) and paste any arXiv URL. The section tree lets you click to include/exclude sections before converting.

### CLI

```bash
pip install arxiv2markdown

# Basic usage
arxiv2md 2501.11120v1 -o paper.md

# Only extract specific sections
arxiv2md 2501.11120v1 --section-filter-mode include --sections "Abstract,Introduction" -o -

# Strip references and TOC
arxiv2md 2501.11120v1 --remove-refs --remove-toc -o -

# Include YAML frontmatter with paper metadata
arxiv2md 2501.11120v1 --frontmatter -o paper.md
```

### REST API

Two GET endpoints — no auth required:

```bash
# JSON response (with metadata)
curl "https://arxiv2md.org/api/json?url=2312.00752"

# Raw markdown
curl "https://arxiv2md.org/api/markdown?url=2312.00752"
```

| Param | Default | Description |
|-------|---------|-------------|
| `url` | required | arXiv URL or ID |
| `remove_refs` | `true` | Remove references |
| `remove_toc` | `true` | Remove table of contents |
| `remove_citations` | `true` | Remove inline citations |
| `frontmatter` | `false` | Prepend YAML frontmatter (`/api/markdown` only) |

Rate limit: 30 requests/minute per IP.

### Python Library

```python
from arxiv2md import ingest_paper_sync

result = ingest_paper_sync("2501.11120v1")
print(result.content)
```

An async version is also available for use inside async contexts (e.g. Jupyter notebooks, async frameworks):

```python
from arxiv2md import ingest_paper

result = await ingest_paper("2501.11120v1")
```

Both accept the same optional keyword arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `remove_refs` | `True` | Remove bibliography/references sections |
| `remove_toc` | `True` | Remove table of contents |
| `remove_inline_citations` | `True` | Remove inline citation text |
| `section_filter_mode` | `"exclude"` | `"include"` or `"exclude"` for section filtering |
| `sections` | `None` (all) | List of section titles to include/exclude |
| `include_frontmatter` | `False` | Prepend YAML frontmatter with paper metadata |

### For AI Agents

The REST API works out of the box with any AI agent or LLM workflow — no MCP server, no OAuth, no SDK. Just a GET request:

```bash
curl -s "https://arxiv2md.org/api/markdown?url=2501.11120" | head -50
```

Feed the output directly into your agent's context. Section filtering lets you keep only what matters and stay within token budgets.

## Development

```bash
pip install -e .[server]
uvicorn server.main:app --reload --app-dir src

# Run tests
pip install -e .[dev]
pytest tests
```

## Contributing

PRs welcome! Fork the repo, create a feature branch, add tests if applicable, and submit a PR.

## License

MIT

---