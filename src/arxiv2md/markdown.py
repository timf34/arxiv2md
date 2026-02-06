"""Convert arXiv HTML to Markdown with a custom serializer."""

from __future__ import annotations

import re
from typing import Iterable

try:
    from bs4 import BeautifulSoup
    from bs4.element import NavigableString, Tag
except ImportError as exc:  # pragma: no cover - runtime dependency check
    raise RuntimeError("BeautifulSoup4 is required for HTML parsing (pip install beautifulsoup4).") from exc


_EQUATION_TABLE_RE = re.compile(r"ltx_equationgroup|ltx_eqn_align|ltx_eqn_table")


def convert_html_to_markdown(html: str, *, remove_refs: bool = False, remove_toc: bool = False) -> str:
    """Convert arXiv HTML into Markdown."""
    soup = BeautifulSoup(html, "html.parser")
    toc_markdown = None
    toc_nav = soup.find("nav", class_=re.compile(r"ltx_TOC"))
    if toc_nav and not remove_toc:
        toc_markdown = _serialize_toc(toc_nav)

    _strip_unwanted_elements(soup)
    if remove_refs:
        for ref in soup.find_all("section", class_=re.compile(r"ltx_bibliography")):
            ref.decompose()

    convert_all_mathml_to_latex(soup)
    fix_tabular_tables(soup)

    root = _find_document_root(soup)
    title_tag = root.find("h1", class_=re.compile(r"ltx_title_document"))
    authors_tag = root.find("div", class_=re.compile(r"ltx_authors"))
    abstract_tag = root.find("div", class_=re.compile(r"ltx_abstract"))

    blocks: list[str] = []
    if title_tag:
        blocks.append(f"# {_normalize_text(title_tag.get_text(' ', strip=True))}")
    if authors_tag:
        authors_text = _normalize_text(authors_tag.get_text(" ", strip=True))
        if authors_text:
            blocks.append(f"Authors: {authors_text}")
    if toc_markdown:
        blocks.append("## Contents\n" + toc_markdown)
    if abstract_tag:
        blocks.extend(_serialize_abstract(abstract_tag))

    for tag in (title_tag, authors_tag, abstract_tag):
        if tag:
            tag.decompose()

    blocks.extend(_serialize_children(root))

    return "\n\n".join(block for block in blocks if block).strip()


def convert_fragment_to_markdown(html: str, *, remove_inline_citations: bool = False) -> str:
    """Convert an HTML fragment into Markdown without title/author/abstract handling.

    Parameters
    ----------
    html : str
        The HTML fragment to convert.
    remove_inline_citations : bool
        If True, completely remove inline citation links. If False (default),
        citation links are converted to plain text (URL stripped).
    """
    soup = BeautifulSoup(html, "html.parser")
    _strip_unwanted_elements(soup)
    convert_all_mathml_to_latex(soup)
    fix_tabular_tables(soup)
    blocks = _serialize_children(soup, remove_inline_citations=remove_inline_citations)
    return "\n\n".join(block for block in blocks if block).strip()


def _find_document_root(soup: BeautifulSoup) -> Tag:
    root = soup.find("article", class_=re.compile(r"ltx_document"))
    if root:
        return root
    if soup.body:
        return soup.body
    return soup


def _strip_unwanted_elements(soup: BeautifulSoup) -> None:
    for tag in soup.find_all(["script", "style", "noscript", "link", "meta"]):
        tag.decompose()
    for tag in soup.select("nav.ltx_page_navbar, nav.ltx_TOC"):
        tag.decompose()
    for tag in soup.select("button.sr-only, div.package-alerts, div.ltx_pagination, footer"):
        tag.decompose()


def convert_all_mathml_to_latex(root: BeautifulSoup) -> None:
    for math in root.find_all("math"):
        annotation = math.find("annotation", attrs={"encoding": "application/x-tex"})
        if annotation and annotation.text:
            latex_source = annotation.text.strip()
            latex_source = re.sub(r"(?<!\\)%", "", latex_source)
            latex_source = re.sub(r"\\([_^])", r"\1", latex_source)
            latex_source = re.sub(r"\\(?=[\[\]])", "", latex_source)
            math.replace_with(f"${latex_source}$")
        else:
            math.replace_with(math.get_text(" ", strip=True))


def fix_tabular_tables(root: BeautifulSoup) -> None:
    tables = root.find_all("table", class_=re.compile(r"ltx_tabular"))
    for table in tables:
        _remove_all_attributes(table)
        for child in table.find_all(["tbody", "thead", "tfoot", "tr", "td", "th"]):
            _remove_all_attributes(child)


def _remove_all_attributes(tag: Tag) -> None:
    tag.attrs = {}


def _serialize_children(container: Tag, *, remove_inline_citations: bool = False) -> list[str]:
    blocks: list[str] = []
    for child in container.children:
        if isinstance(child, NavigableString):
            continue
        if not isinstance(child, Tag):
            continue
        blocks.extend(_serialize_block(child, remove_inline_citations=remove_inline_citations))
    return blocks


def _serialize_block(tag: Tag, *, remove_inline_citations: bool = False) -> list[str]:
    if tag.name in {"section", "article", "div", "span"}:
        return _serialize_children(tag, remove_inline_citations=remove_inline_citations)

    if tag.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        level = int(tag.name[1])
        heading = _normalize_text(tag.get_text(" ", strip=True))
        if not heading:
            return []
        return [f"{'#' * level} {heading}"]

    if tag.name == "p":
        paragraph = _serialize_paragraph(tag, remove_inline_citations=remove_inline_citations)
        return [paragraph] if paragraph else []

    if tag.name in {"ul", "ol"}:
        lines = _serialize_list(tag, remove_inline_citations=remove_inline_citations)
        return ["\n".join(lines)] if lines else []

    if tag.name == "figure":
        figure = _serialize_figure(tag, remove_inline_citations=remove_inline_citations)
        return [figure] if figure else []

    if tag.name == "table":
        table_md = _serialize_table(tag, remove_inline_citations=remove_inline_citations)
        return [table_md] if table_md else []

    if tag.name == "blockquote":
        content = _normalize_text(_serialize_inline(tag, remove_inline_citations=remove_inline_citations))
        if not content:
            return []
        return ["> " + content]

    if tag.name == "br":
        return []

    return _serialize_children(tag, remove_inline_citations=remove_inline_citations)


def _serialize_abstract(tag: Tag) -> list[str]:
    blocks = ["## Abstract"]
    paragraphs = tag.find_all("p")
    if not paragraphs:
        content = _normalize_text(tag.get_text(" ", strip=True))
        if content:
            blocks.append(content)
        return blocks

    for paragraph in paragraphs:
        text = _serialize_paragraph(paragraph)
        if text:
            blocks.append(text)
    return blocks


def _serialize_paragraph(tag: Tag, *, remove_inline_citations: bool = False) -> str:
    content = _serialize_inline(tag, remove_inline_citations=remove_inline_citations)
    content = _cleanup_inline_text(content)
    return content


def _is_citation_link(href: str | None) -> bool:
    """Check if a link is a citation reference (e.g., #bib.bib7)."""
    if not href:
        return False
    return "#bib." in href or href.startswith("#bib")


def _is_internal_paper_link(href: str | None) -> bool:
    """Check if a link is an internal paper section reference (e.g., arxiv.org/html/...#S2.SS1)."""
    if not href:
        return False
    return "arxiv.org/html/" in href and "#" in href and "#bib" not in href


def _serialize_inline(node: Tag | NavigableString, *, remove_inline_citations: bool = False) -> str:
    if isinstance(node, NavigableString):
        return str(node)

    if node.name == "br":
        return "\n"

    if node.name in {"em", "i"}:
        return f"*{_serialize_children_inline(node, remove_inline_citations=remove_inline_citations)}*"

    if node.name in {"strong", "b"}:
        return f"**{_serialize_children_inline(node, remove_inline_citations=remove_inline_citations)}**"

    if node.name == "a":
        text = _serialize_children_inline(node, remove_inline_citations=remove_inline_citations).strip()
        href = node.get("href")
        # Handle citation links specially
        if _is_citation_link(href):
            if remove_inline_citations:
                return ""  # Completely remove citation
            return text  # Keep text only, strip URL
        # Handle internal paper links (section references)
        if remove_inline_citations and _is_internal_paper_link(href):
            return text  # Keep text only, strip URL
        # Regular links: keep full markdown link
        if href:
            return f"[{text or href}]({href})"
        return text

    if node.name == "sup":
        text = _serialize_children_inline(node, remove_inline_citations=remove_inline_citations).strip()
        return f"^{text}" if text else ""

    if node.name == "cite":
        return _serialize_children_inline(node, remove_inline_citations=remove_inline_citations)

    if node.name == "math":
        text = node.get_text(" ", strip=True)
        return f"${text}$" if text else ""

    if "ltx_note" in node.get("class", []):
        text = _normalize_text(_serialize_children_inline(node, remove_inline_citations=remove_inline_citations))
        return f"({text})" if text else ""

    return _serialize_children_inline(node, remove_inline_citations=remove_inline_citations)


def _serialize_children_inline(tag: Tag, *, remove_inline_citations: bool = False) -> str:
    return "".join(_serialize_inline(child, remove_inline_citations=remove_inline_citations) for child in tag.children)


def _cleanup_inline_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text.strip()


def _serialize_list(list_tag: Tag, indent: int = 0, *, remove_inline_citations: bool = False) -> list[str]:
    lines: list[str] = []
    for item in list_tag.find_all("li", recursive=False):
        item_text_parts: list[str] = []
        nested_lists: list[Tag] = []
        for child in item.children:
            if isinstance(child, Tag) and child.name in {"ul", "ol"}:
                nested_lists.append(child)
            else:
                item_text_parts.append(_serialize_inline(child, remove_inline_citations=remove_inline_citations))
        item_text = _cleanup_inline_text("".join(item_text_parts))
        prefix = "  " * indent + "- "
        lines.append(prefix + item_text if item_text else prefix.rstrip())
        for nested in nested_lists:
            lines.extend(_serialize_list(nested, indent + 1, remove_inline_citations=remove_inline_citations))
    return lines


def _serialize_toc(toc_nav: Tag) -> str:
    list_tag = toc_nav.find("ol")
    if not list_tag:
        return ""
    lines = _serialize_list(list_tag)
    return "\n".join(lines)


def _serialize_table(table: Tag, *, remove_inline_citations: bool = False) -> str:
    classes = " ".join(table.get("class", []))
    if _EQUATION_TABLE_RE.search(classes):
        eqn_text = _normalize_text(table.get_text(" ", strip=True))
        if not eqn_text:
            return ""
        return f"$$ {eqn_text} $$"

    rows = []
    # Find rows in tbody, thead, tfoot, or directly in table
    # Handle nested structure where rows might be inside tbody/thead/tfoot
    tbody_elements = table.find_all(["tbody", "thead", "tfoot"], recursive=False)
    
    if tbody_elements:
        # Table has tbody/thead/tfoot structure - find rows within them
        for tbody in tbody_elements:
            for row in tbody.find_all("tr", recursive=False):
                cells = row.find_all(["th", "td"], recursive=False)
                if not cells:
                    continue
                values = []
                for cell in cells:
                    cell_text = _cleanup_inline_text(_serialize_inline(cell, remove_inline_citations=remove_inline_citations)).replace("\n", "<br>")
                    values.append(cell_text)
                rows.append(values)
    else:
        # Table has no tbody/thead/tfoot - find rows directly in table
        for row in table.find_all("tr", recursive=False):
            cells = row.find_all(["th", "td"], recursive=False)
            if not cells:
                continue
            values = []
            for cell in cells:
                cell_text = _cleanup_inline_text(_serialize_inline(cell, remove_inline_citations=remove_inline_citations)).replace("\n", "<br>")
                values.append(cell_text)
            rows.append(values)

    if not rows:
        return ""

    max_cols = max(len(row) for row in rows)
    normalized = [row + [""] * (max_cols - len(row)) for row in rows]
    header = normalized[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _serialize_figure(figure: Tag, *, remove_inline_citations: bool = False) -> str:
    # Check if this is a table figure (ltx_table class)
    figure_classes = " ".join(figure.get("class", []))
    is_table_figure = "ltx_table" in figure_classes

    caption_tag = figure.find("figcaption")
    caption = _normalize_text(_serialize_inline(caption_tag, remove_inline_citations=remove_inline_citations)) if caption_tag else ""

    lines = []

    if is_table_figure:
        # Handle table figures - find and serialize the embedded table
        # Note: fix_tabular_tables strips attributes, so search for any table element
        table = figure.find("table")
        if table:
            table_md = _serialize_table(table, remove_inline_citations=remove_inline_citations)
            if caption:
                lines.append(f"**{caption}**")
            if table_md:
                lines.append(table_md)
        elif caption:
            # Fallback if no table found but has caption
            lines.append(f"Table: {caption}")
    else:
        # Handle regular image figures
        img = figure.find("img")
        src = img.get("src") if img else None
        alt = img.get("alt") if img else None

        if caption:
            lines.append(f"Figure: {caption}")
        if src:
            image_label = alt or "Image"
            lines.append(f"{image_label}: {src}")

    return "\n".join(lines).strip()


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
