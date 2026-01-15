"""Process a query by parsing input and generating a summary."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from arxiv2md.config import ARXIV2MD_CACHE_PATH
from arxiv2md.ingestion import ingest_paper
from arxiv2md.query_parser import parse_arxiv_input
from arxiv2md.utils.logging_config import get_logger
from server.models import IngestErrorResponse, IngestResponse, IngestSuccessResponse, PatternType
from server.server_config import MAX_DISPLAY_SIZE

logger = get_logger(__name__)

if TYPE_CHECKING:
    from arxiv2md.schemas.query import ArxivQuery


def _store_digest_content(query: ArxivQuery, digest_content: str) -> None:
    """Store digest content locally under the cache directory."""
    cache_dir = ARXIV2MD_CACHE_PATH / str(query.id)
    cache_dir.mkdir(parents=True, exist_ok=True)
    local_txt_file = cache_dir / "digest.txt"
    local_txt_file.write_text(digest_content, encoding="utf-8")


def _generate_digest_url(query: ArxivQuery) -> str:
    """Generate the digest URL for the local cache."""
    return f"/api/download/file/{query.id}"


async def process_query(
    input_text: str,
    *,
    remove_refs: bool = False,
    remove_toc: bool = False,
    remove_inline_citations: bool = False,
    section_filter_mode: str = "exclude",
    sections: list[str] | None = None,
    max_file_size: int | None = None,
    pattern_type: PatternType | None = None,
    pattern: str | None = None,
    token: str | None = None,
) -> IngestResponse:
    """Process an arXiv query and return a markdown summary."""
    # These parameters are kept for API compatibility but not used
    _ = max_file_size, pattern_type, pattern

    if token:
        logger.info("Token provided but ignored for arXiv ingestion")

    try:
        query = parse_arxiv_input(input_text)
    except Exception as exc:
        logger.warning("Failed to parse arXiv input", extra={"input_text": input_text, "error": str(exc)})
        return IngestErrorResponse(error=str(exc))

    query = query.model_copy(
        update={
            "remove_refs": remove_refs,
            "remove_toc": remove_toc,
            "remove_inline_citations": remove_inline_citations,
            "section_filter_mode": section_filter_mode,
            "sections": sections or [],
        }
    )

    try:
        result, metadata = await ingest_paper(
            arxiv_id=query.arxiv_id,
            version=query.version,
            html_url=query.html_url,
            ar5iv_url=query.ar5iv_url,
            remove_refs=query.remove_refs,
            remove_toc=query.remove_toc,
            remove_inline_citations=query.remove_inline_citations,
            section_filter_mode=query.section_filter_mode,
            sections=query.sections,
        )
        summary = result.summary
        tree = result.sections_tree
        content = result.content
        digest_content = tree + "\n" + content
        _store_digest_content(query, digest_content)
    except Exception as exc:
        logger.error("Query processing failed", extra={"url": query.html_url, "error": str(exc)})
        return IngestErrorResponse(error=str(exc))

    if len(content) > MAX_DISPLAY_SIZE:
        content = (
            f"(Content cropped to {MAX_DISPLAY_SIZE // 1_000}k characters, "
            "download full ingest to see more)\n" + content[:MAX_DISPLAY_SIZE]
        )

    _log_success(url=query.html_url, summary=summary)
    digest_url = _generate_digest_url(query)

    return IngestSuccessResponse(
        arxiv_id=query.arxiv_id,
        version=query.version,
        title=cast("str | None", metadata.get("title")),
        source_url=query.abs_url,
        summary=summary,
        digest_url=digest_url,
        tree=tree,
        sections_tree=tree,
        content=content,
        remove_refs=remove_refs,
        remove_toc=remove_toc,
        section_filter_mode=section_filter_mode,
        sections=query.sections,
    )


def _log_success(url: str, summary: str) -> None:
    """Log a successful query processing."""
    estimated_tokens = None
    token_marker = "Estimated tokens:"
    if token_marker in summary:
        estimated_tokens = summary.split(token_marker, 1)[1].strip().splitlines()[0].strip()
    logger.info(
        "Query processing completed successfully",
        extra={"url": url, "estimated_tokens": estimated_tokens},
    )
