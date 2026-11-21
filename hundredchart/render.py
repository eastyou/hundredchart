"""百数表 SVG 与练习纸渲染。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import SIZE, TOTAL, ChartError, ChartProblem, check_number


def _fmt(value: float) -> str:
    return ("%.2f" % value).rstrip("0").rstrip(".")


def render_chart(holes: Sequence[int] = (), cell: int = 44) -> str:
    """绘制百数表，可把指定数字留空。"""
    if isinstance(cell, bool) or not isinstance(cell, int):
        raise ChartError("格子尺寸必须是整数")
    if cell < 24 or cell > 110:
        raise ChartError("格子尺寸必须在 24–110 之间")
    blanks = set()
    for value in holes:
        blanks.add(check_number(value))
    size = cell * SIZE
    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="百数表">' % (size, size, size, size),
        "<title>百数表</title>",
        '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (size, size),
    ]
    for value in range(1, TOTAL + 1):
        row, col = divmod(value - 1, SIZE)
        x = col * cell
        y = row * cell
        fill = "#fffaf0" if row % 2 else "#ffffff"
        text = str(value) if value not in blanks else ""
        color = "#1f2933"
        if row == 0:
            fill = "#ebf8ff"
        if col == 0:
            fill = "#ebf8ff"
        if value in blanks:
            color = "#cbd2d9"
        parts.append(
            '<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="#cbd2d9" '
            'stroke-width="0.8"/>' % (_fmt(x), _fmt(y), _fmt(cell), _fmt(cell), fill)
        )
        if text:
            parts.append(
                '<text x="%s" y="%s" font-size="%s" text-anchor="middle" fill="%s" '
                'font-family="Helvetica, Arial, sans-serif">%s</text>'
                % (
                    _fmt(x + cell / 2.0),
                    _fmt(y + cell * 0.66),
                    _fmt(cell * 0.36),
                    color,
                    text,
                )
            )
    parts.append("</svg>")
    return "\n".join(parts)


_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 5mm; text-align: center; color: #616e7c; font-size: 12px; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 4mm; page-break-inside: avoid; }
.prompt { font-size: 15px; line-height: 1.7; margin: 0 0 3mm; }
.answer-line { border-bottom: 1px dashed #9aa5b1; height: 28px; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #2b6cb0; padding-left: 3mm; color: #2c5282; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
@media print { .sheet { padding: 0; } }
""".strip()


def render_worksheet(
    problems: Sequence[ChartProblem],
    title: str = "百数表练习",
    answers: bool = False,
) -> str:
    """生成可打印的百数表练习纸。"""
    items = list(problems)
    if not items:
        raise ChartError("至少需要一道题")
    for item in items:
        if not isinstance(item, ChartProblem):
            raise ChartError("题目必须是 ChartProblem")
    cards = [
        '<div class="card"><p class="prompt">%d. %s</p><div class="answer-line"></div></div>'
        % (index, html.escape(item.prompt))
        for index, item in enumerate(items, 1)
    ]
    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<section class="cards">',
        "\n".join(cards),
        "</section>",
    ]
    if answers:
        rows = [
            "<tr><td>%d</td><td>%s</td><td>%s</td></tr>"
            % (index, html.escape(item.prompt), html.escape(item.answer))
            for index, item in enumerate(items, 1)
        ]
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            "<table><thead><tr><th>题号</th><th>题目</th><th>答案</th></tr></thead>"
            "<tbody>%s</tbody></table></section>" % "\n".join(rows)
        )
    sections.append("</main></body></html>")
    return "\n".join(sections)
