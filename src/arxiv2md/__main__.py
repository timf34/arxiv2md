"""Command-line interface (CLI) for arxiv2md."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from arxiv2md.ingestion import ingest_paper
from arxiv2md.query_parser import parse_arxiv_input

DEFAULT_OUTPUT_FILE = "digest.txt"


def main() -> None:
    """Run the CLI entry point for arXiv ingestion."""
    # Ensure stdout can handle Unicode (e.g. accented author names) on Windows,
    # where the default console encoding is often cp1252.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = _parse_args()
    try:
        asyncio.run(_async_main(args))
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


async def _async_main(args: argparse.Namespace) -> None:
    query = parse_arxiv_input(args.input_text)

    sections = _collect_sections(args.sections, args.section)
    result, _metadata = await ingest_paper(
        arxiv_id=query.arxiv_id,
        version=query.version,
        html_url=query.html_url,
        ar5iv_url=query.ar5iv_url,
        remove_refs=args.remove_refs,
        remove_toc=args.remove_toc,
        remove_inline_citations=args.remove_inline_citations,
        include_images=args.include_images,
        html_base_url=query.html_url,
        section_filter_mode=args.section_filter_mode,
        sections=sections,
        include_frontmatter=args.frontmatter,
    )

    output_text = _format_output(
        result.summary,
        result.sections_tree,
        result.content,
        include_tree=args.include_tree,
        frontmatter=result.frontmatter,
    )
    output_target = args.output if args.output is not None else DEFAULT_OUTPUT_FILE

    if output_target == "-":
        sys.stdout.write(output_text)
        if not output_text.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()
    else:
        Path(output_target).write_text(output_text, encoding="utf-8")
        print(f"Output written to: {output_target}")
        print("\nSummary:")
        print(result.summary)


def _format_output(
    summary: str,
    tree: str,
    content: str,
    *,
    include_tree: bool,
    frontmatter: str | None = None,
) -> str:
    parts: list[str] = []
    if frontmatter:
        parts.append(frontmatter)
    else:
        parts.append(summary)
    if include_tree:
        parts.append(tree)
    parts.append(content)
    return "\n\n".join(parts).strip()


def _collect_sections(sections_csv: str | None, section_list: list[str] | None) -> list[str]:
    values: list[str] = []
    if sections_csv:
        values.extend(sections_csv.split(","))
    if section_list:
        values.extend(section_list)
    return [value.strip() for value in values if value and value.strip()]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="arxiv2md",
        description="Convert arXiv papers to clean Markdown. Particularly useful for prompting LLMs.",
    )
    parser.add_argument(
        "input_text",
        help="arXiv ID or URL (e.g., 2501.11120v1 or https://arxiv.org/abs/2501.11120)",
    )
    parser.add_argument(
        "--remove-refs",
        action="store_true",
        help="Remove bibliography/references sections from output.",
    )
    parser.add_argument(
        "--remove-toc",
        action="store_true",
        help="Remove table of contents from output.",
    )
    parser.add_argument(
        "--remove-inline-citations",
        action="store_true",
        help="Remove inline citation text (e.g., '(Smith et al., 2023)') from output.",
    )
    parser.add_argument(
        "--section-filter-mode",
        choices=("include", "exclude"),
        default="exclude",
        help="Section filtering mode when using --sections/--section.",
    )
    parser.add_argument(
        "--sections",
        default=None,
        help='Comma-separated section titles (e.g., "Abstract,Introduction").',
    )
    parser.add_argument(
        "--section",
        action="append",
        help="Repeatable section title filter (can be used multiple times).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path. Use '-' to write to stdout.",
    )
    parser.add_argument(
        "--include-images",
        action="store_true",
        help="Emit proper markdown image syntax with absolute arXiv URLs instead of plain text.",
    )
    parser.add_argument(
        "--include-tree",
        action="store_true",
        help="Include the section tree before the Markdown content.",
    )
    parser.add_argument(
        "--frontmatter",
        action="store_true",
        help="Prepend YAML frontmatter with paper metadata (title, authors, URL, etc.).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
