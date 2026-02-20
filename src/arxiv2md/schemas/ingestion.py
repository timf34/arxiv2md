"""Ingestion output model."""

from __future__ import annotations

from pydantic import BaseModel


class IngestionResult(BaseModel):
    """Final ingestion output."""

    summary: str
    sections_tree: str
    content: str
    frontmatter: str | None = None
