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
