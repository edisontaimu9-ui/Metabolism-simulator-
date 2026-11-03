"""Unit tests for metabosim.reports.render."""

import base64

import pytest

from metabosim.reports.data import ReportData
from metabosim.reports.document import (
    BulletList,
    Document,
    FigureBlock,
    Paragraph,
    Section,
    Table,
    build_document,
)
from metabosim.reports.render import md_escape, render_html, render_markdown

_PNG = b"\x89PNG-fake-bytes"


def _doc() -> Document:
    return Document(
        title="T | <b>",
        sections=(
            Section(
                "S",
                (
                    Paragraph("para <i>x</i>"),
                    BulletList(("a_b", "c*d")),
                    Table(("H1", "H2"), (("x|y", "2"),)),
                    FigureBlock(key="weight", caption="Cap [1]", png=_PNG),
                ),
            ),
        ),
    )


@pytest.mark.unit
class TestMarkdownEscape:
    def test_escapes_special_characters(self) -> None:
        assert md_escape("a|b*c_d`e[f]<g>#h") == r"a\|b\*c\_d\`e\[f\]\<g\>\#h"

    def test_flattens_newlines(self) -> None:
        assert md_escape("a\nb") == "a b"


@pytest.mark.unit
class TestRenderMarkdown:
    def test_title_and_heading(self) -> None:
        md = render_markdown(_doc())
        assert md.startswith("# T \\| \\<b\\>\n")
        assert "## S\n" in md

    def test_table_is_well_formed(self) -> None:
        md = render_markdown(_doc())
        assert "| H1 | H2 |\n|---|---|\n| x\\|y | 2 |" in md

    def test_bullets(self) -> None:
        md = render_markdown(_doc())
        assert "- a\\_b\n- c\\*d" in md

    def test_figure_link_uses_figure_dir(self) -> None:
        md = render_markdown(_doc(), figure_dir="out_figures")
        assert "![Cap \\[1\\]](out_figures/weight.png)" in md

    def test_user_text_cannot_inject_markup(self) -> None:
        md = render_markdown(_doc())
        assert "<i>" not in md

    def test_ends_with_single_newline(self) -> None:
        md = render_markdown(_doc())
        assert md.endswith("\n") and not md.endswith("\n\n")


@pytest.mark.unit
class TestRenderHtml:
    def test_is_complete_document(self) -> None:
        out = render_html(_doc())
        assert out.startswith("<!DOCTYPE html>")
        assert out.rstrip().endswith("</html>")
        assert "<title>T | &lt;b&gt;</title>" in out

    def test_escapes_text(self) -> None:
        out = render_html(_doc())
        assert "<i>x</i>" not in out
        assert "para &lt;i&gt;x&lt;/i&gt;" in out

    def test_table_and_list(self) -> None:
        out = render_html(_doc())
        assert "<th>H1</th>" in out
        assert "<td>x|y</td>" in out
        assert "<li>c*d</li>" in out

    def test_figure_embedded_as_data_uri(self) -> None:
        out = render_html(_doc())
        encoded = base64.b64encode(_PNG).decode("ascii")
        assert f"data:image/png;base64,{encoded}" in out
        assert "<figcaption>Cap [1]</figcaption>" in out

    def test_no_external_resources(self) -> None:
        out = render_html(_doc())
        assert "http://" not in out and "https://" not in out

    def test_alt_text_quotes_escaped(self) -> None:
        doc = Document(
            "T",
            (Section("S", (FigureBlock("k", 'say "hi"', _PNG),)),),
        )
        assert 'alt="say &quot;hi&quot;"' in render_html(doc)


@pytest.mark.unit
class TestRealDocument:
    def test_markdown_and_html_agree_on_key_facts(self, full_data: ReportData) -> None:
        doc = build_document(full_data)
        md = render_markdown(doc)
        html_out = render_html(doc)
        for fragment in ("Key results", "Daily results", "References", "Fothergill"):
            assert fragment in md
            assert fragment in html_out
