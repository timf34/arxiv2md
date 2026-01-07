"""Tests for arXiv query parsing."""

from __future__ import annotations

import pytest

from arxiv2md.query_parser import parse_arxiv_input


@pytest.mark.parametrize(
    ("input_text", "arxiv_id", "version"),
    [
        ("2501.11120v1", "2501.11120v1", "v1"),
        ("https://arxiv.org/abs/2501.11120", "2501.11120", None),
        ("https://arxiv.org/pdf/2501.11120v2.pdf", "2501.11120v2", "v2"),
        ("cs/9901001v2", "cs/9901001v2", "v2"),
    ],
)
def test_parse_arxiv_inputs(input_text: str, arxiv_id: str, version: str | None) -> None:
    query = parse_arxiv_input(input_text)

    assert query.arxiv_id == arxiv_id
    assert query.version == version
    assert query.html_url == f"https://arxiv.org/html/{arxiv_id}"
    assert query.abs_url == f"https://arxiv.org/abs/{arxiv_id}"


def test_rejects_unknown_host() -> None:
    with pytest.raises(ValueError, match="Unsupported host"):
        parse_arxiv_input("https://example.com/abs/2501.11120")
