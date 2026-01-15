"""Parse and normalize arXiv inputs."""

from __future__ import annotations

import re
from typing import Final
from urllib.parse import urlparse
from uuid import uuid4

from arxiv2md.config import ARXIV2MD_CACHE_PATH
from arxiv2md.schemas import ArxivQuery

_ARXIV_HOST: Final = "arxiv.org"
_ARXIV_PATH_KINDS: Final = {"abs", "pdf", "html"}
_ARXIV_ID_RE: Final = re.compile(
    r"^(?P<base>(\d{4}\.\d{4,5}|[a-zA-Z-]+/\d{7}))(v(?P<version>\d+))?$",
)


def parse_arxiv_input(input_text: str) -> ArxivQuery:
    """Parse a raw arXiv ID or URL into a normalized query object."""
    raw = input_text.strip()
    if not raw:
        raise ValueError("input_text cannot be empty")

    normalized_id, version = _extract_arxiv_id(raw)
    html_url = f"https://{_ARXIV_HOST}/html/{normalized_id}"
    ar5iv_url = f"https://ar5iv.labs.arxiv.org/html/{normalized_id}"
    abs_url = f"https://{_ARXIV_HOST}/abs/{normalized_id}"
    query_id = uuid4()

    return ArxivQuery(
        input_text=raw,
        arxiv_id=normalized_id,
        version=version,
        html_url=html_url,
        ar5iv_url=ar5iv_url,
        abs_url=abs_url,
        id=query_id,
        cache_dir=ARXIV2MD_CACHE_PATH / str(query_id),
    )


def _extract_arxiv_id(raw: str) -> tuple[str, str | None]:
    """Extract and normalize an arXiv identifier from raw input."""
    cleaned = _strip_arxiv_prefix(raw)
    if _looks_like_url(cleaned):
        return _extract_from_url(cleaned)
    return _normalize_id(cleaned)


def _strip_arxiv_prefix(value: str) -> str:
    if value.lower().startswith("arxiv:"):
        return value.split(":", 1)[1].strip()
    return value


def _looks_like_url(value: str) -> bool:
    # Check for full URLs
    if value.startswith(("http://", "https://", "arxiv.org/")):
        return True
    # Check for path-style inputs like "html/2501.11120v1" or "abs/2501.11120v1"
    if "/" in value:
        first_part = value.split("/")[0]
        if first_part in _ARXIV_PATH_KINDS:
            return True
    return False


def _extract_from_url(url: str) -> tuple[str, str | None]:
    # Handle path-style inputs like "html/2501.11120v1" or "abs/2501.11120v1"
    if not url.startswith(("http://", "https://", "arxiv.org/")):
        first_part = url.split("/")[0]
        if first_part in _ARXIV_PATH_KINDS:
            url = f"https://arxiv.org/{url}"

    if url.startswith("arxiv.org/"):
        url = f"https://{url}"

    parsed = urlparse(url)
    if parsed.netloc and _ARXIV_HOST not in parsed.netloc:
        raise ValueError(f"Unsupported host: {parsed.netloc}")

    path_parts = [part for part in parsed.path.split("/") if part]
    if not path_parts:
        raise ValueError("Invalid arXiv URL: missing path")

    if path_parts[0] in _ARXIV_PATH_KINDS and len(path_parts) >= 2:
        kind = path_parts[0]
        arxiv_part = path_parts[1]
        if kind == "pdf" and arxiv_part.endswith(".pdf"):
            arxiv_part = arxiv_part[: -len(".pdf")]
        return _normalize_id(arxiv_part)

    # Accept direct paths like /<id> or /<id>vN
    return _normalize_id(path_parts[0])


def _normalize_id(value: str) -> tuple[str, str | None]:
    match = _ARXIV_ID_RE.match(value)
    if not match:
        raise ValueError(f"Unrecognized arXiv identifier: {value}")

    base = match.group("base")
    version_digits = match.group("version")
    version = f"v{version_digits}" if version_digits else None
    normalized = f"{base}{version}" if version else base
    return normalized, version
