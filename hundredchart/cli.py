"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    ChartError,
    check_number,
    generate_problems,
    neighbors,
    position,
)
from .render import render_chart, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="hundredchart",
        description="百数表：可打印表格、位置查询与练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    chart = subparsers.add_parser("chart", help="输出百数表 SVG")
    chart.add_argument("--holes", default="", help="留空的数字，逗号分隔，如 3,17,58")
    chart.add_argument("--cell", type=int, default=44, help="格子边长，默认 44")
    chart.add_argument("-o", "--output", default=None, help="输出文件")

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--kinds", default=",".join(KINDS), help="题型，逗号分隔：position、neighbors、skip")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument("--title", default="百数表练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")

    pos = subparsers.add_parser("position", help="查询数字的行列")
    pos.add_argument("number", type=int, help="1–100 的数字")

    near = subparsers.add_parser("neighbors", help="查询上下左右的相邻数")
    near.add_argument("number", type=int, help="1–100 的数字")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_holes(text: str) -> List[int]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    values = []
    for part in parts:
        if not part.lstrip("-").isdigit():
            raise ChartError("留空数字必须是整数：%s" % part)
        values.append(check_number(int(part)))
    return values


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise ChartError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "chart":
            _write_output(render_chart(_parse_holes(args.holes), args.cell), args.output)
            return 0
        if args.command == "position":
            row, col = position(args.number)
            print("%d 在第 %d 行第 %d 列" % (args.number, row, col))
            return 0
        if args.command == "neighbors":
            items = neighbors(args.number)
            for key, label in (("up", "上"), ("down", "下"), ("left", "左"), ("right", "右")):
                print("%s：%s" % (label, items[key] if items[key] is not None else "无"))
            return 0
        problems = generate_problems(args.count, _parse_kinds(args.kinds), args.seed)
        _write_output(render_worksheet(problems, args.title, args.answers), args.output)
        return 0
    except ChartError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
