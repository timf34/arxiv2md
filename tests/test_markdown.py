"""Tests for Markdown serialization."""

from __future__ import annotations

from arxiv2md.markdown import convert_fragment_to_markdown


def test_math_and_tables_render() -> None:
    html = """
    <div class="ltx_para"><p>Equation <math>
        <annotation encoding="application/x-tex">x+y</annotation>
    </math></p></div>
    <table class="ltx_tabular">
        <tr><th>A</th><th>B</th></tr>
        <tr><td>1</td><td>2</td></tr>
    </table>
    <table class="ltx_equationgroup">
        <tr><td>E = mc^2 (1)</td></tr>
    </table>
    """

    markdown = convert_fragment_to_markdown(html)

    assert "$x+y$" in markdown
    assert "| A | B |" in markdown
    assert "| 1 | 2 |" in markdown
    assert "$$" in markdown
    assert "E = mc^2" in markdown


def test_table_with_tbody() -> None:
    """Test that tables with tbody/thead/tfoot structure are correctly converted."""
    html = """
    <table class="ltx_tabular">
        <tbody>
            <tr><th>Model</th><th>Accuracy</th></tr>
            <tr><td>Llama-7B</td><td>70.12</td></tr>
            <tr><td>Llama-13B</td><td>72.39</td></tr>
        </tbody>
    </table>
    """

    markdown = convert_fragment_to_markdown(html)

    # Should contain table structure
    assert "| Model | Accuracy |" in markdown
    assert "| --- | --- |" in markdown
    assert "| Llama-7B | 70.12 |" in markdown
    assert "| Llama-13B | 72.39 |" in markdown


def test_table_with_thead_tbody() -> None:
    """Test that tables with thead and tbody are correctly converted."""
    html = """
    <table class="ltx_tabular">
        <thead>
            <tr><th>Method</th><th>Result</th></tr>
        </thead>
        <tbody>
            <tr><td>Prune SW</td><td>0.0%</td></tr>
            <tr><td>Prune Non-SW</td><td>68.5%</td></tr>
        </tbody>
    </table>
    """

    markdown = convert_fragment_to_markdown(html)

    # Should contain table structure
    assert "| Method | Result |" in markdown
    assert "| Prune SW | 0.0% |" in markdown
    assert "| Prune Non-SW | 68.5% |" in markdown


def test_table_inside_figure() -> None:
    """Test that tables wrapped in figure elements (ltx_table) are correctly converted."""
    html = """
    <figure class="ltx_table" id="S3.T1">
        <table class="ltx_tabular ltx_centering ltx_guessed_headers ltx_align_middle">
            <thead class="ltx_thead">
                <tr class="ltx_tr">
                    <th class="ltx_td ltx_align_left ltx_th ltx_th_column">Model</th>
                    <th class="ltx_td ltx_align_center ltx_th ltx_th_column">Arc-c</th>
                    <th class="ltx_td ltx_align_center ltx_th ltx_th_column">Arc-e</th>
                </tr>
            </thead>
            <tbody class="ltx_tbody">
                <tr class="ltx_tr">
                    <td class="ltx_td ltx_align_left">Original</td>
                    <td class="ltx_td ltx_align_center">41.81</td>
                    <td class="ltx_td ltx_align_center">75.29</td>
                </tr>
                <tr class="ltx_tr">
                    <td class="ltx_td ltx_align_left">Prune SW</td>
                    <td class="ltx_td ltx_align_center">19.80</td>
                    <td class="ltx_td ltx_align_center">39.60</td>
                </tr>
            </tbody>
        </table>
        <figcaption class="ltx_caption ltx_centering">
            <span class="ltx_tag ltx_tag_table">Table 1: </span>
            <span class="ltx_text ltx_font_bold">Super Weight Importance</span>.
            Pruning the super weight significantly impairs quality.
        </figcaption>
    </figure>
    """

    markdown = convert_fragment_to_markdown(html)

    # Should contain the caption
    assert "Table 1:" in markdown
    assert "Super Weight Importance" in markdown
    # Should contain the actual table data
    assert "| Model | Arc-c | Arc-e |" in markdown
    assert "| Original | 41.81 | 75.29 |" in markdown
    assert "| Prune SW | 19.80 | 39.60 |" in markdown


def test_remove_inline_citations_citep() -> None:
    """Test that parenthetical citations (citep) are fully removed."""
    html = (
        '<p>We study deceptive alignment '
        '<cite class="ltx_cite ltx_citemacro_citep">'
        '(Anthropic, <a class="ltx_ref" href="#bib.bib4">2024</a>; '
        'OpenAI, <a class="ltx_ref" href="#bib.bib29">2024</a>)'
        '</cite> in large models.</p>'
    )

    result = convert_fragment_to_markdown(html, remove_inline_citations=True)
    assert "Anthropic" not in result
    assert "OpenAI" not in result
    assert "2024" not in result
    assert "deceptive alignment" in result
    assert "large models" in result


def test_remove_inline_citations_citet() -> None:
    """Test that textual citations (citet) are fully removed."""
    html = (
        '<p>As shown by '
        '<cite class="ltx_cite ltx_citemacro_citet">'
        'Treutlein et al. (<a class="ltx_ref" href="#bib.bib40">2024</a>)'
        '</cite>, this is important.</p>'
    )

    result = convert_fragment_to_markdown(html, remove_inline_citations=True)
    assert "Treutlein" not in result
    assert "this is important" in result


def test_remove_inline_citations_preserves_when_disabled() -> None:
    """Test that citations are preserved as plain text when removal is disabled."""
    html = (
        '<p>We study '
        '<cite class="ltx_cite ltx_citemacro_citep">'
        '(Anthropic, <a class="ltx_ref" href="#bib.bib4">2024</a>)'
        '</cite> things.</p>'
    )

    result = convert_fragment_to_markdown(html, remove_inline_citations=False)
    assert "Anthropic" in result
    assert "2024" in result


def test_remove_inline_citations_ignores_non_ltx_cite() -> None:
    """Test that plain cite tags without ltx_cite class are not removed."""
    html = '<p>See <cite>A Book Title</cite> for details.</p>'

    result = convert_fragment_to_markdown(html, remove_inline_citations=True)
    assert "A Book Title" in result


def test_resolve_relative_image_urls() -> None:
    """Test that relative image paths are resolved to absolute URLs."""
    html = """
    <figure>
        <img src="extracted/figures/fig1.png" alt="Architecture diagram"/>
        <figcaption>Figure 1: System overview</figcaption>
    </figure>
    """

    result = convert_fragment_to_markdown(html, base_url="https://arxiv.org/html/2501.11120v1")
    assert "https://arxiv.org/html/2501.11120v1/extracted/figures/fig1.png" in result
    assert "Figure 1: System overview" in result


def test_absolute_image_urls_unchanged() -> None:
    """Test that absolute image URLs are not modified."""
    html = """
    <figure>
        <img src="https://arxiv.org/html/2501.11120v1/assets/img.png" alt="Diagram"/>
        <figcaption>Figure 2: Results</figcaption>
    </figure>
    """

    result = convert_fragment_to_markdown(html, base_url="https://ar5iv.labs.arxiv.org/html/2501.11120v1")
    assert "https://arxiv.org/html/2501.11120v1/assets/img.png" in result


def test_no_base_url_preserves_relative_paths() -> None:
    """Test that without base_url, relative paths are preserved as-is."""
    html = """
    <figure>
        <img src="extracted/fig1.png" alt="Diagram"/>
    </figure>
    """

    result = convert_fragment_to_markdown(html)
    assert "extracted/fig1.png" in result


def test_span_paragraphs_in_framed_block_keep_their_text() -> None:
    """Test that paragraphs LaTeXML writes as ``span.ltx_p`` keep their text.

    Inside a framed box LaTeXML emits ``<span class="ltx_p">`` instead of
    ``<p>``, as in Section 4 of arXiv:2405.06624.
    """
    html = """
    <div class="ltx_para"><span class="ltx_inline-logical-block ltx_framed ltx_framed_rectangle">
    <span class="ltx_theorem ltx_theorem_example">
    <h6 class="ltx_title ltx_runin ltx_title_theorem"><span class="ltx_tag ltx_tag_theorem">Example 4.1</span> (Code Translation).</h6>
    <span class="ltx_para">
    <span class="ltx_p"><br class="ltx_break"/><span class="ltx_text ltx_font_bold">Problem</span>: Translate code in one programming language to another.</span>
    </span>
    <span class="ltx_para">
    <span class="ltx_p"><span class="ltx_text ltx_font_bold">Specification</span>: Functional correctness.</span>
    </span>
    </span>
    </span></div>
    """

    result = convert_fragment_to_markdown(html)
    assert "###### Example 4.1 (Code Translation)." in result
    assert "Problem: Translate code in one programming language to another." in result
    assert "Specification: Functional correctness." in result
