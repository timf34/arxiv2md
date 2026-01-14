"""Simple GET API endpoints for markdown conversion."""

from typing import Any

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from server.models import IngestErrorResponse, MarkdownJsonResponse
from server.query_processor import process_query

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

COMMON_API_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_200_OK: {"description": "Successful conversion"},
    status.HTTP_400_BAD_REQUEST: {"model": IngestErrorResponse, "description": "Invalid URL or processing error"},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": IngestErrorResponse, "description": "Internal server error"},
}


@router.get("/api/json", responses=COMMON_API_RESPONSES, response_model=MarkdownJsonResponse)
@limiter.limit("30/minute")
async def api_json(
    request: Request,
    url: str = Query(..., description="arXiv URL or ID (e.g., https://arxiv.org/abs/2301.07041 or 2301.07041)"),
    remove_refs: bool = Query(default=True, description="Remove references section"),
    remove_toc: bool = Query(default=True, description="Remove table of contents"),
    remove_citations: bool = Query(default=True, description="Remove inline citations"),
) -> JSONResponse:
    """Convert an arXiv paper to markdown and return JSON with metadata.

    **Example:**
    ```
    GET /api/json?url=2301.07041
    ```

    **Returns:**
    ```json
    {
      "arxiv_id": "2301.07041",
      "title": "Paper Title",
      "source_url": "https://arxiv.org/abs/2301.07041",
      "content": "# Paper Title\\n\\n## Abstract\\n..."
    }
    ```
    """
    try:
        result = await process_query(
            input_text=url,
            remove_refs=remove_refs,
            remove_toc=remove_toc,
            remove_inline_citations=remove_citations,
            section_filter_mode="exclude",
            sections=[],
        )

        if isinstance(result, IngestErrorResponse):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result.model_dump())

        response = MarkdownJsonResponse(
            arxiv_id=result.arxiv_id,
            title=result.title,
            source_url=result.source_url,
            content=result.content,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())

    except ValueError as ve:
        error_response = IngestErrorResponse(error=f"Validation error: {ve!s}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump())

    except Exception as exc:
        error_response = IngestErrorResponse(error=f"Internal server error: {exc!s}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response.model_dump())


@router.get("/api/markdown", responses=COMMON_API_RESPONSES)
@limiter.limit("30/minute")
async def api_markdown(
    request: Request,
    url: str = Query(..., description="arXiv URL or ID (e.g., https://arxiv.org/abs/2301.07041 or 2301.07041)"),
    remove_refs: bool = Query(default=True, description="Remove references section"),
    remove_toc: bool = Query(default=True, description="Remove table of contents"),
    remove_citations: bool = Query(default=True, description="Remove inline citations"),
) -> PlainTextResponse:
    """Convert an arXiv paper to markdown and return raw markdown text.

    **Example:**
    ```
    GET /api/markdown?url=2301.07041
    ```

    **Returns:** Plain text markdown content.
    """
    try:
        result = await process_query(
            input_text=url,
            remove_refs=remove_refs,
            remove_toc=remove_toc,
            remove_inline_citations=remove_citations,
            section_filter_mode="exclude",
            sections=[],
        )

        if isinstance(result, IngestErrorResponse):
            return PlainTextResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=f"Error: {result.error}",
            )

        return PlainTextResponse(status_code=status.HTTP_200_OK, content=result.content)

    except ValueError as ve:
        return PlainTextResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f"Validation error: {ve!s}")

    except Exception as exc:
        return PlainTextResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"Error: {exc!s}")
