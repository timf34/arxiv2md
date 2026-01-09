"""The dynamic router module defines handlers for dynamic path requests."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from server.server_config import EXAMPLE_REPOS, get_version_info, templates

router = APIRouter()


def _path_to_arxiv_url(path: str) -> str:
    """Convert a path like 'abs/2501.11120v1' or 'html/2501.11120v1' to an arXiv URL.

    Parameters
    ----------
    path : str
        The path from the URL (e.g., 'abs/2501.11120v1', 'html/2501.11120v1', '2501.11120v1')

    Returns
    -------
    str
        The full arXiv URL (e.g., 'https://arxiv.org/abs/2501.11120v1')

    """
    if not path:
        return ""

    # If path already looks like a full URL, return as-is
    if path.startswith(("http://", "https://")):
        return path

    # Handle paths like 'abs/2501.11120v1' or 'html/2501.11120v1'
    # Convert to https://arxiv.org/abs/... format
    path_parts = path.split("/")
    if path_parts[0] in ("abs", "html", "pdf"):
        # Path is like 'abs/2501.11120v1' or 'html/2501.11120v1'
        return f"https://arxiv.org/{path}"

    # Path is just the ID like '2501.11120v1'
    return f"https://arxiv.org/abs/{path}"


@router.get("/{full_path:path}", include_in_schema=False)
async def catch_all(request: Request, full_path: str) -> HTMLResponse:
    """Render the arxiv2md page with a pre-filled arXiv URL based on the provided path.

    This endpoint catches all GET requests with a dynamic path, constructs an arXiv URL
    using the ``full_path`` parameter, and renders the ``arxiv.jinja`` template with that URL.

    Parameters
    ----------
    request : Request
        The incoming request object, which provides context for rendering the response.
    full_path : str
        The full path extracted from the URL, which is used to build the arXiv URL.

    Returns
    -------
    HTMLResponse
        An HTML response containing the rendered template, with the arXiv URL
        pre-filled in the form.

    """
    arxiv_url = _path_to_arxiv_url(full_path)

    context = {
        "request": request,
        "repo_url": arxiv_url,
        "examples": EXAMPLE_REPOS,
        "default_max_file_size": 243,
    }
    context.update(get_version_info())

    return templates.TemplateResponse("arxiv.jinja", context)
