"""Pydantic models for the API."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from server.server_config import MAX_FILE_SIZE_KB

if TYPE_CHECKING:
    from server.form_types import IntForm, OptStrForm, StrForm


class SectionFilterMode(str, Enum):
    """Section filtering modes."""

    INCLUDE = "include"
    EXCLUDE = "exclude"


# Alias for backward compatibility
PatternType = SectionFilterMode


class IngestRequest(BaseModel):
    """Request model for the /api/ingest endpoint."""

    model_config = ConfigDict(extra="allow")

    input_text: str = Field(..., description="arXiv URL or ID to ingest")
    remove_refs: bool = Field(default=False, description="Remove references from output")
    remove_toc: bool = Field(default=False, description="Remove table of contents from output")
    remove_inline_citations: bool = Field(
        default=False,
        description="Remove inline citations and internal paper links from output",
    )
    section_filter_mode: SectionFilterMode = Field(
        default=SectionFilterMode.EXCLUDE,
        description="Section filtering mode",
    )
    sections: list[str] = Field(default_factory=list, description="Section titles to filter")

    # Deprecated fields for gitingest compatibility
    max_file_size: int | None = Field(default=None, ge=1, le=MAX_FILE_SIZE_KB)
    pattern_type: SectionFilterMode | None = Field(default=None)
    pattern: str = Field(default="")
    token: str | None = Field(default=None)

    @field_validator("input_text")
    @classmethod
    def validate_input_text(cls, v: str) -> str:
        """Validate that input_text is not empty."""
        if not v.strip():
            raise ValueError("input_text cannot be empty")
        return v.strip()

    @field_validator("sections", mode="before")
    @classmethod
    def normalize_sections(cls, v: str | list[str] | None) -> list[str]:
        """Normalize section inputs from comma-separated strings or lists."""
        if not v:
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return [item.strip() for item in v if item.strip()]

    @field_validator("pattern")
    @classmethod
    def validate_pattern(cls, v: str) -> str:
        """Strip whitespace from pattern field."""
        return v.strip()


class IngestSuccessResponse(BaseModel):
    """Success response model for the /api/ingest endpoint."""

    arxiv_id: str | None = Field(default=None, description="arXiv identifier")
    version: str | None = Field(default=None, description="arXiv version")
    title: str | None = Field(default=None, description="Paper title")
    source_url: str | None = Field(default=None, description="Canonical arXiv abstract URL")
    summary: str = Field(..., description="Ingestion summary with token estimates")
    digest_url: str = Field(..., description="URL to download the full digest content")
    tree: str = Field(..., description="Section tree structure")
    sections_tree: str | None = Field(default=None, description="Section tree (alias for tree)")
    content: str = Field(..., description="Processed markdown content")
    remove_refs: bool | None = Field(default=None)
    remove_toc: bool | None = Field(default=None)
    section_filter_mode: str | None = Field(default=None)
    sections: list[str] | None = Field(default=None)

    # Deprecated fields for gitingest compatibility
    repo_url: str | None = Field(default=None)
    short_repo_url: str | None = Field(default=None)
    default_max_file_size: int | None = Field(default=None)
    pattern_type: str | None = Field(default=None)
    pattern: str | None = Field(default=None)


class IngestErrorResponse(BaseModel):
    """Error response model for the /api/ingest endpoint."""

    error: str = Field(..., description="Error message")


IngestResponse = Union[IngestSuccessResponse, IngestErrorResponse]


class QueryForm(BaseModel):
    """Form data for the query."""

    input_text: str
    remove_refs: bool = False
    remove_toc: bool = False
    section_filter_mode: str = SectionFilterMode.EXCLUDE.value
    sections: str = ""

    # Deprecated fields for gitingest compatibility
    max_file_size: int | None = None
    pattern_type: str | None = None
    pattern: str = ""
    token: str | None = None

    @classmethod
    def as_form(
        cls,
        input_text: StrForm,
        max_file_size: IntForm,
        pattern_type: StrForm,
        pattern: StrForm,
        token: OptStrForm,
    ) -> QueryForm:
        """Create a QueryForm from FastAPI form parameters."""
        return cls(
            input_text=input_text,
            max_file_size=max_file_size,
            pattern_type=pattern_type,
            pattern=pattern,
            token=token,
        )
