"""Ingestion pipeline for arXiv HTML -> Markdown."""

from __future__ import annotations

from arxiv2md.fetch import fetch_arxiv_html
from arxiv2md.html_parser import parse_arxiv_html
from arxiv2md.markdown import convert_fragment_to_markdown
from arxiv2md.output_formatter import format_paper
from arxiv2md.schemas import IngestionResult
from arxiv2md.sections import filter_sections

_REFERENCE_TITLES = ("references", "bibliography")
_ABSTRACT_TITLE = "abstract"


async def ingest_paper(
    *,
    arxiv_id: str,
    version: str | None,
    html_url: str,
    ar5iv_url: str | None = None,
    remove_refs: bool,
    remove_toc: bool,
    remove_inline_citations: bool = False,
    section_filter_mode: str,
    sections: list[str],
) -> tuple[IngestionResult, dict[str, str | list[str] | None]]:
    """Fetch, parse, and serialize an arXiv paper into Markdown.

    Parameters
    ----------
    remove_inline_citations : bool
        If True, completely remove inline citation links from the output.
        If False (default), citation URLs are stripped but text is kept.
    """
    html = await fetch_arxiv_html(html_url, arxiv_id=arxiv_id, version=version, use_cache=True, ar5iv_url=ar5iv_url)
    parsed = parse_arxiv_html(html)

    filtered_sections = filter_sections(parsed.sections, mode=section_filter_mode, selected=sections)
    if remove_refs:
        filtered_sections = filter_sections(filtered_sections, mode="exclude", selected=_REFERENCE_TITLES)

    # Check if abstract should be included based on section filter
    selected_lower = [s.lower() for s in sections]
    if section_filter_mode == "exclude":
        include_abstract = _ABSTRACT_TITLE not in selected_lower
    else:  # include mode
        include_abstract = not sections or _ABSTRACT_TITLE in selected_lower

    for section in filtered_sections:
        _populate_section_markdown(section, remove_inline_citations=remove_inline_citations)

    result = format_paper(
        arxiv_id=arxiv_id,
        version=version,
        title=parsed.title,
        authors=parsed.authors,
        abstract=parsed.abstract if include_abstract else None,
        sections=filtered_sections,
        include_toc=not remove_toc,
        include_abstract_in_tree=parsed.abstract is not None,
    )

    metadata = {
        "title": parsed.title,
        "authors": parsed.authors,
        "abstract": parsed.abstract,
    }

    return result, metadata


def _populate_section_markdown(section, *, remove_inline_citations: bool = False) -> None:
    if section.html:
        section.markdown = convert_fragment_to_markdown(section.html, remove_inline_citations=remove_inline_citations)
    for child in section.children:
        _populate_section_markdown(child, remove_inline_citations=remove_inline_citations)
