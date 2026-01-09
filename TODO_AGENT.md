# arxiv2md Step-by-step TODO

## Phase 0: Plan alignment
- [x] Update `PLAN.md` to specify local-only caching (no S3 for v1).
- [x] Confirm forked-copy approach and module naming (`arxiv2md/*`).
- [x] Note removal of hosted service utilities (S3, metrics, Sentry, rate limiting) for v1.

## Phase 1: Scaffold reuse and renaming
- [x] Copy/reuse `gitingest` server scaffold into arxiv2md app namespace.
- [x] Rename templates and form JS/CSS references:
  - `git.jinja` -> `arxiv.jinja`
  - `git_form.jinja` -> `arxiv_form.jinja`
  - `git.js` -> `arxiv.js`
  - `git_form.js` -> `arxiv_form.js`
- [x] Update route wiring to render new arXiv pages.
- [x] Remove hosted-service utilities from the fork:
  - Drop S3 support code paths.
  - Remove metrics server + Sentry setup.
  - Remove rate limiting middleware if not needed for localhost.
- [x] Add `arxiv2md/config.py` with local cache path and size/time limits.

## Phase 2: Core models and request/response schema
- [x] Define `arxiv2md/schemas/*` for:
  - `ArxivQuery`
  - `SectionNode`
  - `IngestionResult`
- [x] Update `server/models.py`:
  - Request model fields: `input_text`, toggles (`remove_refs`, `remove_toc`), section filter selection.
  - Response model fields: `arxiv_id`, `version`, `title`, `summary`, `sections_tree`, `content`, `digest_url`.

## Phase 3: arXiv query parsing + normalization
- [x] Implement `arxiv2md/query_parser.py`:
  - Parse raw IDs and `abs/pdf/html` URLs.
  - Normalize to canonical ID + HTML URL.
  - Track display URL for UI.
- [ ] Add unit tests for normalization edge cases (versioned IDs, PDF URLs).

## Phase 4: HTML fetch + local cache
- [x] Implement `arxiv2md/fetch.py`:
  - Fetch HTML with timeouts and retry policy.
  - Validate `text/html`.
  - Cache HTML and/or markdown under `ARXIV2MD_CACHE_PATH` from `arxiv2md/config.py`.
- [x] Add cache key format and cache invalidation policy (simple TTL).

## Phase 5: HTML parse + section extraction
- [x] Implement `arxiv2md/html_parser.py`:
  - Extract metadata (title, authors, abstract).
  - Build heading-based section tree.
  - Collect raw HTML for each section.
- [ ] Add tests with sample HTML fragments.

## Phase 6: Markdown conversion
- [x] Implement `arxiv2md/markdown.py`:
  - Custom serializer over the `ltx_*` DOM structure.
  - MathML -> LaTeX, tables -> Markdown, equation tables -> `$$ ... $$`.
  - TOC and references optional include/exclude handling.
- [x] Add `scripts/inspect_arxiv_html.py` to inspect tag/class usage.
- [ ] Create fixtures to verify math and table conversions.

## Phase 7: Ingestion pipeline and output formatting
- [x] Implement `arxiv2md/ingestion.py`:
  - Orchestrate parse -> fetch -> convert -> section filter.
- [x] Implement `arxiv2md/output_formatter.py`:
  - Summary, section tree, content aggregation, token estimates.
- [x] Wire into `server/query_processor.py` and `server/routers/ingest.py`.

## Phase 8: Web UI update
- [x] Update `arxiv_form.jinja`:
  - Input placeholder and helper copy.
  - Toggles for remove refs/TOC and section filter mode.
- [ ] Update server_config.py examples and version links for arXiv usage.
- [ ] Update result labels to "Sections" and "Paper Content".
- [ ] Add section selector UI in left panel.

## Phase 9: CLI parity (optional but planned)
- [x] Add `arxiv2md/__main__.py` with CLI flags.
- [x] Ensure CLI output mirrors web summary + content.

## Phase 10: Tests and polish
- [ ] Add API integration test covering full ingest flow.
- [x] Add unit tests for parser + markdown conversion.
- [ ] Validate behavior on HTML-unavailable inputs.




