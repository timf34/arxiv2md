"""Ingest endpoint for the API."""

from typing import Union
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from arxiv2md.config import ARXIV2MD_CACHE_PATH
from server.models import IngestRequest
from server.routers_utils import COMMON_INGEST_RESPONSES, _perform_ingestion
from server.server_config import DEFAULT_FILE_SIZE_KB

router = APIRouter()


@router.post("/api/ingest", responses=COMMON_INGEST_RESPONSES)
async def api_ingest(
    request: Request,  # noqa: ARG001 (unused-function-argument) # pylint: disable=unused-argument
    ingest_request: IngestRequest,
) -> JSONResponse:
    """Ingest an arXiv paper and return processed content.

    **This endpoint processes an arXiv HTML page by fetching and parsing it,**
    then returns a summary with the paper's content. The response includes
    section tree structure, processed Markdown, and metadata about the ingestion.

    **Parameters**

    - **ingest_request** (`IngestRequest`): Pydantic model containing ingestion parameters

    **Returns**

    - **JSONResponse**: Success response with ingestion results or error response with appropriate HTTP status code

    """
    response = await _perform_ingestion(
        input_text=ingest_request.input_text,
        max_file_size=ingest_request.max_file_size,
        pattern_type=ingest_request.pattern_type.value if ingest_request.pattern_type else None,
        pattern=ingest_request.pattern,
        token=ingest_request.token,
        remove_refs=ingest_request.remove_refs,
        remove_toc=ingest_request.remove_toc,
        remove_inline_citations=ingest_request.remove_inline_citations,
        include_frontmatter=ingest_request.include_frontmatter,
        section_filter_mode=ingest_request.section_filter_mode.value,
        sections=ingest_request.sections,
    )
    return response


@router.get("/api/{user}/{repository}", responses=COMMON_INGEST_RESPONSES)
async def api_ingest_get(
    request: Request,  # noqa: ARG001 (unused-function-argument) # pylint: disable=unused-argument
    user: str,
    repository: str,
    max_file_size: int = DEFAULT_FILE_SIZE_KB,
    pattern_type: str = "exclude",
    pattern: str = "",
    token: str = "",
) -> JSONResponse:
    """Ingest an arXiv paper via GET and return processed content.

    **This endpoint processes an arXiv identifier or URL by fetching and parsing it,**
    returning processed content and metadata. Parameters are optional and can be
    provided as query parameters.

    **Path Parameters**
    - **user** (`str`): arXiv category or prefix (legacy IDs)
    - **repository** (`str`): arXiv identifier suffix

    **Query Parameters**
    - **max_file_size** (`int`, optional): Deprecated legacy parameter
    - **pattern_type** (`str`, optional): Deprecated legacy parameter
    - **pattern** (`str`, optional): Deprecated legacy parameter
    - **token** (`str`, optional): Deprecated legacy parameter

    **Returns**
    - **JSONResponse**: Success response with ingestion results or error response
    """
    response = await _perform_ingestion(
        input_text=f"{user}/{repository}",
        max_file_size=max_file_size,
        pattern_type=pattern_type,
        pattern=pattern,
        token=token or None,
        remove_refs=False,
        remove_toc=False,
        section_filter_mode="exclude",
        sections=[],
    )
    return response


@router.get("/api/download/file/{ingest_id}", response_model=None)
async def download_ingest(
    ingest_id: UUID,
) -> Union[RedirectResponse, FileResponse]:  # noqa: FA100 (future-rewritable-type-annotation) (pydantic)
    """Download the first text file produced for an ingest ID.

    **This endpoint retrieves the first ``*.txt`` file produced during the ingestion process**
    and returns it as a downloadable file from the local cache directory.

    **Parameters**

    - **ingest_id** (`UUID`): Identifier that the ingest step emitted

    **Returns**

    - **FileResponse**: Streamed response with media type ``text/plain`` for local files

    **Raises**

    - **HTTPException**: **404** - digest directory is missing or contains no ``*.txt`` file
    - **HTTPException**: **403** - the process lacks permission to read the directory or file

    """
    # Fall back to local file serving
    # Normalize and validate the directory path
    directory = (ARXIV2MD_CACHE_PATH / str(ingest_id)).resolve()
    if not str(directory).startswith(str(ARXIV2MD_CACHE_PATH.resolve())):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid ingest ID: {ingest_id!r}")

    if not directory.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Digest {ingest_id!r} not found")

    try:
        first_txt_file = next(directory.glob("*.txt"))
    except StopIteration as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No .txt file found for digest {ingest_id!r}",
        ) from exc

    try:
        return FileResponse(path=first_txt_file, media_type="text/plain", filename=first_txt_file.name)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied for {first_txt_file}",
        ) from exc
