"""Format arXiv sections into summary, tree, and content outputs."""

from __future__ import annotations

from typing import Iterable

try:
    import tiktoken
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None

from arxiv2md.schemas import IngestionResult, SectionNode


_ARXIV_ABS_BASE = "https://arxiv.org/abs/"


def format_paper(
    *,
    arxiv_id: str,
    version: str | None,
    title: str | None,
    authors: list[str],
    abstract: str | None,
    sections: list[SectionNode],
    include_toc: bool,
    include_abstract_in_tree: bool = True,
    include_frontmatter: bool = False,
) -> IngestionResult:
    """Create summary, section tree, and content."""
    tree_lines = ["Sections:"]
    if include_abstract_in_tree:
        tree_lines.append("Abstract")
    tree_lines.append(_create_sections_tree(sections))
    tree = "\n".join(tree_lines)
    content = _render_content(abstract=abstract, sections=sections, include_toc=include_toc)

    section_count = count_sections(sections)
    token_estimate = _format_token_count(tree + "\n" + content)

    summary_lines = []
    if title:
        summary_lines.append(f"Title: {title}")
    summary_lines.append(f"ArXiv: {arxiv_id}")
    if version:
        summary_lines.append(f"Version: {version}")
    if authors:
        summary_lines.append(f"Authors: {', '.join(authors)}")
    summary_lines.append(f"Sections: {section_count}")
    if token_estimate:
        summary_lines.append(f"Estimated tokens: {token_estimate}")

    summary = "\n".join(summary_lines)

    frontmatter = None
    if include_frontmatter:
        frontmatter = _generate_frontmatter(
            title=title,
            arxiv_id=arxiv_id,
            version=version,
            authors=authors,
            section_count=section_count,
            token_estimate=token_estimate,
        )

    return IngestionResult(summary=summary, sections_tree=tree, content=content, frontmatter=frontmatter)


def _generate_frontmatter(
    *,
    title: str | None,
    arxiv_id: str,
    version: str | None,
    authors: list[str],
    section_count: int,
    token_estimate: str | None,
) -> str:
    """Generate YAML frontmatter block with paper metadata."""
    lines = ["---"]
    if title:
        lines.append(f"title: \"{_escape_yaml_string(title)}\"")
    if version:
        lines.append(f"version: \"{version}\"")
    if authors:
        quoted = ", ".join(f'"{_escape_yaml_string(a)}"' for a in authors)
        lines.append(f"authors: [{quoted}]")
    lines.append(f"url: \"{_ARXIV_ABS_BASE}{arxiv_id}\"")
    lines.append(f"sections: {section_count}")
    if token_estimate:
        lines.append(f"estimated_tokens: \"{token_estimate}\"")
    lines.append("---")
    return "\n".join(lines)


def _escape_yaml_string(value: str) -> str:
    """Escape characters that are special in YAML string values."""
    return value.replace("\\", "\\\\").replace("\"", "\\\"")


def count_sections(sections: Iterable[SectionNode]) -> int:
    """Count total sections in the tree."""
    total = 0
    for section in sections:
        total += 1
        total += count_sections(section.children)
    return total


def _render_content(
    *,
    abstract: str | None,
    sections: list[SectionNode],
    include_toc: bool,
) -> str:
    blocks: list[str] = []
    if include_toc:
        toc = _render_toc(sections)
        if toc:
            blocks.append("## Contents\n" + toc)

    if abstract:
        blocks.append("## Abstract")
        blocks.append(abstract.strip())

    for section in sections:
        blocks.extend(_render_section(section))

    return "\n\n".join(block for block in blocks if block).strip()


def _render_section(section: SectionNode) -> list[str]:
    blocks: list[str] = []
    heading_prefix = "#" * min(section.level, 6)
    blocks.append(f"{heading_prefix} {section.title}")
    if section.markdown:
        blocks.append(section.markdown)
    for child in section.children:
        blocks.extend(_render_section(child))
    return blocks


def _render_toc(sections: list[SectionNode], indent: int = 0) -> str:
    lines: list[str] = []
    for section in sections:
        prefix = "  " * indent + "- "
        lines.append(prefix + section.title)
        if section.children:
            lines.append(_render_toc(section.children, indent + 1))
    return "\n".join(lines)


def _create_sections_tree(sections: list[SectionNode], indent: int = 0) -> str:
    lines: list[str] = []
    for section in sections:
        lines.append(" " * (indent * 4) + section.title)
        if section.children:
            lines.append(_create_sections_tree(section.children, indent + 1))
    return "\n".join(lines)


def _format_token_count(text: str) -> str | None:
    if not tiktoken:
        return None
    try:
        encoding = tiktoken.get_encoding("o200k_base")
        total_tokens = len(encoding.encode(text, disallowed_special=()))
    except Exception:
        return None

    if total_tokens >= 1_000_000:
        return f"{total_tokens / 1_000_000:.1f}M"
    if total_tokens >= 1_000:
        return f"{total_tokens / 1_000:.1f}k"
    return str(total_tokens)
