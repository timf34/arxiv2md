"""Tests for arXiv HTML parsing."""

from __future__ import annotations

from arxiv2md.html_parser import parse_arxiv_html


def test_extracts_metadata_and_sections() -> None:
    html = """
    <html>
      <body>
        <article class="ltx_document">
          <h1 class="ltx_title ltx_title_document">Sample Title</h1>
          <div class="ltx_authors">
            <span class="ltx_text ltx_font_bold">Alice<sup>1</sup></span>
            <span class="ltx_text ltx_font_bold">Bob<sup>2</sup></span>
          </div>
          <div class="ltx_abstract">
            <p>Abstract text.</p>
          </div>
          <section class="ltx_section" id="S1">
            <h2 class="ltx_title ltx_title_section">1 Intro</h2>
            <div class="ltx_para"><p>Intro text.</p></div>
          </section>
        </article>
      </body>
    </html>
    """

    parsed = parse_arxiv_html(html)

    assert parsed.title == "Sample Title"
    assert parsed.authors == ["Alice", "Bob"]
    assert parsed.abstract == "Abstract text."
    assert parsed.sections
    assert parsed.sections[0].title == "1 Intro"
    assert parsed.sections[0].html and "Intro text." in parsed.sections[0].html
