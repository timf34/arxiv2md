"""Reusable form type aliases for FastAPI form parameters."""

from __future__ import annotations

from typing import Annotated, TypeAlias

from fastapi import Form

StrForm: TypeAlias = Annotated[str, Form(...)]
IntForm: TypeAlias = Annotated[int, Form(...)]
OptStrForm: TypeAlias = Annotated[str | None, Form()]
