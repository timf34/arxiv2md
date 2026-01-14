"""Main module for the FastAPI application."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Import logging configuration first to intercept all logging
from arxiv2md.utils.logging_config import get_logger
from server.routers import dynamic, index, ingest, markdown_api

# Load environment variables from .env file
load_dotenv()

# Initialize logger for this module
logger = get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize the FastAPI application
app = FastAPI(docs_url=None, redoc_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Mount static files dynamically to serve CSS, JS, and other static assets
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")



@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint to verify that the server is running.

    **Returns**

    - **dict[str, str]**: A JSON object with a "status" key indicating the server's health status.

    """
    return {"status": "healthy"}


@app.head("/", include_in_schema=False)
async def head_root() -> HTMLResponse:
    """Respond to HTTP HEAD requests for the root URL.

    **This endpoint mirrors the headers and status code of the index page**
    for HTTP HEAD requests, providing a lightweight way to check if the server
    is responding without downloading the full page content.

    **Returns**

    - **HTMLResponse**: An empty HTML response with appropriate headers

    """
    return HTMLResponse(content=None, headers={"content-type": "text/html; charset=utf-8"})


@app.get("/robots.txt", include_in_schema=False)
async def robots() -> FileResponse:
    """Serve the robots.txt file to guide search engine crawlers.

    **This endpoint serves the ``robots.txt`` file located in the static directory**
    to provide instructions to search engine crawlers about which parts of the site
    they should or should not index.

    **Returns**

    - **FileResponse**: The ``robots.txt`` file located in the static directory

    """
    return FileResponse("static/robots.txt")


@app.get("/llms.txt")
async def llm_txt() -> FileResponse:
    """Serve the llm.txt file to provide information about the site to LLMs.

    **This endpoint serves the ``llms.txt`` file located in the static directory**
    to provide information about the site to Large Language Models (LLMs)
    and other AI systems that may be crawling the site.

    **Returns**

    - **FileResponse**: The ``llms.txt`` file located in the static directory

    """
    return FileResponse("static/llms.txt")


@app.get("/api", include_in_schema=True)
def openapi_json_get() -> JSONResponse:
    """Return the OpenAPI schema.

    **This endpoint returns the OpenAPI schema (openapi.json)**
    that describes the API structure, endpoints, and data models
    for documentation and client generation purposes.

    **Returns**

    - **JSONResponse**: The OpenAPI schema as JSON

    """
    return JSONResponse(app.openapi())


@app.api_route("/api", methods=["POST", "PUT", "DELETE", "OPTIONS", "HEAD"], include_in_schema=False)
@app.api_route("/api/", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"], include_in_schema=False)
def openapi_json() -> JSONResponse:
    """Return the OpenAPI schema for various HTTP methods.

    **This endpoint returns the OpenAPI schema (openapi.json)**
    for multiple HTTP methods, providing API documentation
    for clients that may use different request methods.

    **Returns**

    - **JSONResponse**: The OpenAPI schema as JSON

    """
    return JSONResponse(app.openapi())


# Include routers for modular endpoints
app.include_router(index)
app.include_router(ingest)
app.include_router(markdown_api)
app.include_router(dynamic)
