"""arxiv2md: ingest arXiv papers into Markdown."""

from __future__ import annotations

import asyncio
from typing import Literal

from arxiv2md.ingestion import ingest_paper as _ingest_paper
from arxiv2md.query_parser import parse_arxiv_input
from arxiv2md.schemas import ArxivQuery, IngestionResult

_VALID_FILTER_MODES = ("include", "exclude")


def _parse_id(arxiv_id: str) -> ArxivQuery:
    """Validate and parse an arXiv identifier, raising a friendly error."""
    try:
        return parse_arxiv_input(arxiv_id)
    except ValueError:
        raise ValueError(
            f"Could not parse arXiv ID or URL: {arxiv_id!r}\n"
            "Expected formats: '2501.11120', '2501.11120v1', "
            "'https://arxiv.org/abs/2501.11120'"
        ) from None


async def ingest_paper(
    arxiv_id: str,
    *,
    remove_refs: bool = True,
    remove_toc: bool = True,
    remove_inline_citations: bool = True,
    section_filter_mode: Literal["include", "exclude"] = "exclude",
    sections: list[str] | None = None,
    include_frontmatter: bool = False,
) -> IngestionResult:
    """Fetch, parse, and serialize an arXiv paper into Markdown.

    Args:
        arxiv_id: arXiv ID or URL (e.g. ``"2501.11120v1"`` or
            ``"https://arxiv.org/abs/2501.11120"``).
        remove_refs: Remove bibliography/references sections.
        remove_toc: Remove table of contents.
        remove_inline_citations: Remove inline citation text.
        section_filter_mode: ``"include"`` or ``"exclude"`` for section
            filtering.
        sections: Section titles to include/exclude. ``None`` means all
            sections.
        include_frontmatter: Prepend YAML frontmatter.

    Returns:
        IngestionResult with ``.content``, ``.summary``, ``.sections_tree``,
        and ``.frontmatter``.

    Raises:
        ValueError: If ``arxiv_id`` is not a recognised arXiv ID or URL, or
            ``section_filter_mode`` is invalid.
    """
    if section_filter_mode not in _VALID_FILTER_MODES:
        raise ValueError(
            f"section_filter_mode must be 'include' or 'exclude', "
            f"got {section_filter_mode!r}"
        )
    query = _parse_id(arxiv_id)
    result, _metadata = await _ingest_paper(
        arxiv_id=query.arxiv_id,
        version=query.version,
        html_url=query.html_url,
        ar5iv_url=query.ar5iv_url,
        remove_refs=remove_refs,
        remove_toc=remove_toc,
        remove_inline_citations=remove_inline_citations,
        section_filter_mode=section_filter_mode,
        sections=sections or [],
        include_frontmatter=include_frontmatter,
    )
    return result


def ingest_paper_sync(
    arxiv_id: str,
    *,
    remove_refs: bool = True,
    remove_toc: bool = True,
    remove_inline_citations: bool = True,
    section_filter_mode: Literal["include", "exclude"] = "exclude",
    sections: list[str] | None = None,
    include_frontmatter: bool = False,
) -> IngestionResult:
    """Synchronous version of :func:`ingest_paper`. Same parameters and
    behaviour — use this when not in an async context.

    Raises:
        RuntimeError: If called from within a running event loop. Use
            ``await ingest_paper(...)`` instead.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        raise RuntimeError(
            "ingest_paper_sync() cannot be called from a running event loop. "
            "Use 'await ingest_paper(...)' instead."
        )

    return asyncio.run(
        ingest_paper(
            arxiv_id,
            remove_refs=remove_refs,
            remove_toc=remove_toc,
            remove_inline_citations=remove_inline_citations,
            section_filter_mode=section_filter_mode,
            sections=sections,
            include_frontmatter=include_frontmatter,
        )
    )


__all__ = ["ingest_paper", "ingest_paper_sync"]
