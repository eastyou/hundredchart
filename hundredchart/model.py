"""百数表的数据模型。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

SIZE = 10
TOTAL = SIZE * SIZE
KINDS = ("position", "neighbors", "skip")


class ChartError(ValueError):
    """百数表相关的输入错误。"""


def check_number(value: int, name: str = "数字") -> int:
    """校验 1–100 的整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ChartError("%s必须是整数" % name)
    if value < 1 or value > TOTAL:
        raise ChartError("%s必须在 1–%d 之间" % (name, TOTAL))
    return value


def position(number: int) -> Tuple[int, int]:
    """返回从 1 开始的行、列。"""
    value = check_number(number)
    row, col = divmod(value - 1, SIZE)
    return row + 1, col + 1


def value_at(row: int, col: int) -> int:
    """按行列取数字。"""
    for value, name in ((row, "行"), (col, "列")):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ChartError("%s必须是整数" % name)
        if value < 1 or value > SIZE:
            raise ChartError("%s必须在 1–%d 之间" % (name, SIZE))
    return (row - 1) * SIZE + col


def neighbors(number: int) -> Dict[str, Optional[int]]:
    """返回上下左右的相邻数，越界为 None。"""
    value = check_number(number)
    row, col = position(value)
    return {
        "up": value - SIZE if row > 1 else None,
        "down": value + SIZE if row < SIZE else None,
        "left": value - 1 if col > 1 else None,
        "right": value + 1 if col < SIZE else None,
    }


def row_values(row: int) -> List[int]:
    """返回一行。"""
    return [value_at(row, col) for col in range(1, SIZE + 1)]


def column_values(col: int) -> List[int]:
    """返回一列。"""
    return [value_at(row, col) for row in range(1, SIZE + 1)]


def skip_sequence(step: int) -> List[int]:
    """从 step 开始按步长跳到 100。"""
    if isinstance(step, bool) or not isinstance(step, int):
        raise ChartError("步长必须是整数")
    if step < 2 or step > 10:
        raise ChartError("步长必须在 2–10 之间")
    return list(range(step, TOTAL + 1, step))


def missing_numbers(
    count: int = 10,
    seed: Optional[int] = None,
    interior: bool = False,
) -> List[int]:
    """随机挑选要遮住的数字。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise ChartError("数量必须是整数")
    if count < 1:
        raise ChartError("数量至少为 1")
    pool = [
        value
        for value in range(1, TOTAL + 1)
        if not interior or all(item is not None for item in neighbors(value).values())
    ]
    if count > len(pool):
        raise ChartError("数量不能超过 %d" % len(pool))
    rng = random.Random(seed)
    return rng.sample(pool, count)


@dataclass(frozen=True)
class ChartProblem:
    """一道百数表题。"""

    kind: str
    number: int
    step: int = 0

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ChartError("题型只能是 position、neighbors 或 skip")
        check_number(self.number)
        if self.kind == "neighbors":
            if any(item is None for item in neighbors(self.number).values()):
                raise ChartError("相邻数题必须选表格内部的数字")
        if self.kind == "skip":
            if self.step < 2 or self.step > 10:
                raise ChartError("步长必须在 2–10 之间")
            if self.number + self.step > TOTAL:
                raise ChartError("跳过 100 的题目无效")

    @property
    def prompt(self) -> str:
        """题干。"""
        if self.kind == "position":
            return "数字 %d 在百数表的第几行第几列？" % self.number
        if self.kind == "neighbors":
            return "数字 %d 的上、下、左、右分别是多少？" % self.number
        return "从 %d 开始每次加 %d，下一个数是多少？" % (self.number, self.step)

    @property
    def answer(self) -> str:
        """标准答案。"""
        if self.kind == "position":
            row, col = position(self.number)
            return "第%d行第%d列" % (row, col)
        if self.kind == "neighbors":
            items = neighbors(self.number)
            return "%d、%d、%d、%d" % (
                items["up"],
                items["down"],
                items["left"],
                items["right"],
            )
        return str(self.number + self.step)


def generate_problems(
    count: int = 8,
    kinds: Sequence[str] = KINDS,
    seed: Optional[int] = None,
) -> List[ChartProblem]:
    """随机生成不重复的百数表题。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise ChartError("题目数量必须是整数")
    if count < 1:
        raise ChartError("题目数量至少为 1")
    chosen = list(kinds)
    if not chosen:
        raise ChartError("至少需要一种题型")
    for kind in chosen:
        if kind not in KINDS:
            raise ChartError("未知题型：%s" % kind)

    combos: List[ChartProblem] = []
    for kind in chosen:
        for number in range(1, TOTAL + 1):
            if kind == "neighbors" and any(
                item is None for item in neighbors(number).values()
            ):
                continue
            if kind == "skip":
                for step in (2, 3, 4, 5, 10):
                    if number + step <= TOTAL:
                        combos.append(ChartProblem(kind, number, step))
            else:
                combos.append(ChartProblem(kind, number))
    if count > len(combos):
        raise ChartError("题目数量不能超过 %d" % len(combos))
    rng = random.Random(seed)
    rng.shuffle(combos)
    return combos[:count]
