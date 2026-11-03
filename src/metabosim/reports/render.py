"""
metabosim.reports.render
===========================

Renders a ``metabosim.reports.document.Document`` to Markdown or
self-contained HTML. Pure string functions: no file I/O (see
``metabosim.reports.writers``).

All document text is treated as plain text and escaped, so
user-supplied strings (a subject's name, an activity label, a report
title) cannot inject Markdown or HTML structure.
"""

from __future__ import annotations

import base64
import html
import re

from metabosim.reports.document import (
    BulletList,
    Document,
    FigureBlock,
    Paragraph,
    Table,
)

_MD_SPECIAL = re.compile(r"([\\`*_{}\[\]<>|#])")

_HTML_CSS = """
body { font-family: system-ui, sans-serif; max-width: 52rem; margin: 2rem auto;
  padding: 0 1rem; line-height: 1.5; color: #1a1a1a; }
h1 { font-size: 1.7rem; } h2 { font-size: 1.25rem; margin-top: 2rem;
  border-bottom: 1px solid #ccc; padding-bottom: .2rem; }
table { border-collapse: collapse; margin: 1rem 0; max-width: 100%; }
th, td { border: 1px solid #ccc; padding: .3rem .6rem; text-align: left; }
th { background: #f2f2f2; }
.table-wrap { overflow-x: auto; }
figure { margin: 1.2rem 0; } figure img { max-width: 100%; height: auto; }
figcaption { font-size: .9rem; color: #444; }
""".strip()


def md_escape(text: str) -> str:
    """Escape Markdown-significant characters and flatten newlines."""
    return _MD_SPECIAL.sub(r"\\\1", text.replace("\n", " "))


def render_markdown(document: Document, figure_dir: str = "figures") -> str:
    """Render ``document`` as Markdown.

    Figures are referenced as ``{figure_dir}/{key}.png`` (relative
    links); writing those files is the caller's job (see
    ``metabosim.reports.writers.save_markdown_report``).
    """
    lines: list[str] = [f"# {md_escape(document.title)}", ""]
    for section in document.sections:
        lines += [f"## {md_escape(section.heading)}", ""]
        for block in section.blocks:
            if isinstance(block, Paragraph):
                lines += [md_escape(block.text), ""]
            elif isinstance(block, BulletList):
                lines += [f"- {md_escape(item)}" for item in block.items]
                lines.append("")
            elif isinstance(block, Table):
                lines.append(
                    "| " + " | ".join(md_escape(h) for h in block.headers) + " |"
                )
                lines.append("|" + "|".join("---" for _ in block.headers) + "|")
                for row in block.rows:
                    lines.append("| " + " | ".join(md_escape(c) for c in row) + " |")
                lines.append("")
            elif isinstance(block, FigureBlock):
                caption = md_escape(block.caption)
                lines += [
                    f"![{caption}]({figure_dir}/{block.key}.png)",
                    "",
                    f"{caption}",
                    "",
                ]
    return "\n".join(lines).rstrip() + "\n"


def render_html(document: Document) -> str:
    """Render ``document`` as one self-contained HTML page (figures are
    embedded as base64 data URIs; no external resources)."""
    esc = html.escape
    out: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(document.title)}</title>",
        f"<style>{_HTML_CSS}</style>",
        "</head>",
        "<body>",
        f"<h1>{esc(document.title)}</h1>",
    ]
    for section in document.sections:
        out.append(f"<h2>{esc(section.heading)}</h2>")
        for block in section.blocks:
            if isinstance(block, Paragraph):
                out.append(f"<p>{esc(block.text)}</p>")
            elif isinstance(block, BulletList):
                out.append("<ul>")
                out += [f"<li>{esc(item)}</li>" for item in block.items]
                out.append("</ul>")
            elif isinstance(block, Table):
                out.append('<div class="table-wrap"><table>')
                out.append(
                    "<thead><tr>"
                    + "".join(f"<th>{esc(h)}</th>" for h in block.headers)
                    + "</tr></thead>"
                )
                out.append("<tbody>")
                for row in block.rows:
                    out.append(
                        "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
                    )
                out.append("</tbody></table></div>")
            elif isinstance(block, FigureBlock):
                encoded = base64.b64encode(block.png).decode("ascii")
                out.append(
                    "<figure>"
                    f'<img alt="{esc(block.caption, quote=True)}" '
                    f'src="data:image/png;base64,{encoded}">'
                    f"<figcaption>{esc(block.caption)}</figcaption>"
                    "</figure>"
                )
    out += ["</body>", "</html>"]
    return "\n".join(out) + "\n"
