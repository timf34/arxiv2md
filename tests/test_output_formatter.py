"""Tests for output formatting, including frontmatter generation."""

from __future__ import annotations

from arxiv2md.output_formatter import format_paper
from arxiv2md.schemas import SectionNode


def _make_sections() -> list[SectionNode]:
    """Create a minimal section tree for testing."""
    child = SectionNode(title="1.1 Background", level=3, html="<p>Background info.</p>")
    return [
        SectionNode(title="1 Introduction", level=2, html="<p>Intro text.</p>", children=[child]),
        SectionNode(title="2 Methods", level=2, html="<p>Methods text.</p>"),
    ]


def test_frontmatter_disabled_by_default() -> None:
    result = format_paper(
        arxiv_id="2501.11120v1",
        version="v1",
        title="Test Paper",
        authors=["Alice", "Bob"],
        abstract="Abstract text.",
        sections=_make_sections(),
        include_toc=False,
    )
    assert result.frontmatter is None


def test_frontmatter_contains_all_fields() -> None:
    result = format_paper(
        arxiv_id="2501.11120v1",
        version="v1",
        title="Test Paper",
        authors=["Alice", "Bob"],
        abstract="Abstract text.",
        sections=_make_sections(),
        include_toc=False,
        include_frontmatter=True,
    )
    assert result.frontmatter is not None
    assert result.frontmatter.startswith("---")
    assert result.frontmatter.endswith("---")
    assert 'title: "Test Paper"' in result.frontmatter
    assert 'version: "v1"' in result.frontmatter
    assert 'authors: ["Alice", "Bob"]' in result.frontmatter
    assert 'url: "https://arxiv.org/abs/2501.11120v1"' in result.frontmatter
    assert "sections: 3" in result.frontmatter


def test_frontmatter_omits_version_when_none() -> None:
    result = format_paper(
        arxiv_id="2501.11120",
        version=None,
        title="Test Paper",
        authors=["Alice"],
        abstract="Abstract text.",
        sections=_make_sections(),
        include_toc=False,
        include_frontmatter=True,
    )
    assert result.frontmatter is not None
    assert "version:" not in result.frontmatter
    assert 'url: "https://arxiv.org/abs/2501.11120"' in result.frontmatter


def test_frontmatter_omits_title_when_none() -> None:
    result = format_paper(
        arxiv_id="2501.11120",
        version=None,
        title=None,
        authors=["Alice"],
        abstract=None,
        sections=_make_sections(),
        include_toc=False,
        include_frontmatter=True,
    )
    assert result.frontmatter is not None
    assert "title:" not in result.frontmatter


def test_frontmatter_omits_authors_when_empty() -> None:
    result = format_paper(
        arxiv_id="2501.11120",
        version=None,
        title="Test",
        authors=[],
        abstract=None,
        sections=_make_sections(),
        include_toc=False,
        include_frontmatter=True,
    )
    assert result.frontmatter is not None
    assert "authors:" not in result.frontmatter


def test_frontmatter_escapes_special_yaml_chars_in_title() -> None:
    result = format_paper(
        arxiv_id="2501.11120",
        version=None,
        title='A "Quoted" Title: With Colons',
        authors=["Alice"],
        abstract=None,
        sections=_make_sections(),
        include_toc=False,
        include_frontmatter=True,
    )
    assert result.frontmatter is not None
    assert r'title: "A \"Quoted\" Title: With Colons"' in result.frontmatter


def test_frontmatter_does_not_affect_summary() -> None:
    result_with = format_paper(
        arxiv_id="2501.11120v1",
        version="v1",
        title="Test Paper",
        authors=["Alice"],
        abstract="Abstract text.",
        sections=_make_sections(),
        include_toc=False,
        include_frontmatter=True,
    )
    result_without = format_paper(
        arxiv_id="2501.11120v1",
        version="v1",
        title="Test Paper",
        authors=["Alice"],
        abstract="Abstract text.",
        sections=_make_sections(),
        include_toc=False,
        include_frontmatter=False,
    )
    assert result_with.summary == result_without.summary
    assert result_with.content == result_without.content
