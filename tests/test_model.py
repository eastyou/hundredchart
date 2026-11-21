"""百数表模型测试。"""

import unittest

from hundredchart.model import (
    SIZE,
    TOTAL,
    ChartError,
    ChartProblem,
    check_number,
    column_values,
    generate_problems,
    missing_numbers,
    neighbors,
    position,
    row_values,
    skip_sequence,
    value_at,
)


class PositionTest(unittest.TestCase):
    """逐一验证 1–100 的行列与取值。"""


def _make_position_test(value):
    def test(self):
        row, col = position(value)
        self.assertEqual(row, (value - 1) // SIZE + 1)
        self.assertEqual(col, (value - 1) % SIZE + 1)
        self.assertEqual(value_at(row, col), value)

    test.__doc__ = "%d 的位置" % value
    return test


for _value in range(1, TOTAL + 1):
    setattr(PositionTest, "test_%03d" % _value, _make_position_test(_value))


class NeighborTest(unittest.TestCase):
    """逐一验证内部数字的上下左右。"""


def _make_neighbor_test(value):
    def test(self):
        items = neighbors(value)
        self.assertEqual(items["up"], value - SIZE)
        self.assertEqual(items["down"], value + SIZE)
        self.assertEqual(items["left"], value - 1)
        self.assertEqual(items["right"], value + 1)
        self.assertEqual(len(set(items.values())), 4)

    test.__doc__ = "%d 的相邻数" % value
    return test


_index = 0
for _row in range(2, SIZE):
    for _col in range(2, SIZE):
        _value = (_row - 1) * SIZE + _col
        setattr(NeighborTest, "test_%02d" % _index, _make_neighbor_test(_value))
        _index += 1


class EdgeTest(unittest.TestCase):
    def test_first_cell(self):
        items = neighbors(1)
        self.assertIsNone(items["up"])
        self.assertIsNone(items["left"])
        self.assertEqual(items["right"], 2)
        self.assertEqual(items["down"], 11)

    def test_last_cell(self):
        items = neighbors(100)
        self.assertIsNone(items["down"])
        self.assertIsNone(items["right"])
        self.assertEqual(items["left"], 99)
        self.assertEqual(items["up"], 90)

    def test_top_edge(self):
        self.assertIsNone(neighbors(5)["up"])

    def test_bottom_edge(self):
        self.assertIsNone(neighbors(95)["down"])

    def test_left_edge(self):
        self.assertIsNone(neighbors(21)["left"])

    def test_right_edge(self):
        self.assertIsNone(neighbors(30)["right"])


class RowsAndColumnsTest(unittest.TestCase):
    def test_row_one(self):
        self.assertEqual(row_values(1), list(range(1, 11)))

    def test_row_ten(self):
        self.assertEqual(row_values(10), list(range(91, 101)))

    def test_column_one(self):
        self.assertEqual(column_values(1), [1, 11, 21, 31, 41, 51, 61, 71, 81, 91])

    def test_column_ten(self):
        self.assertEqual(column_values(10), list(range(10, 101, 10)))

    def test_row_invalid(self):
        with self.assertRaises(ChartError):
            row_values(0)

    def test_column_invalid(self):
        with self.assertRaises(ChartError):
            column_values(11)

    def test_value_bool(self):
        with self.assertRaises(ChartError):
            value_at(True, 1)

    def test_value_range(self):
        with self.assertRaises(ChartError):
            value_at(1, 11)


class CheckAndSkipTest(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(check_number(1), 1)
        self.assertEqual(check_number(100), 100)

    def test_zero(self):
        with self.assertRaises(ChartError):
            check_number(0)

    def test_above(self):
        with self.assertRaises(ChartError):
            check_number(101)

    def test_bool(self):
        with self.assertRaises(ChartError):
            check_number(True)

    def test_string(self):
        with self.assertRaises(ChartError):
            check_number("5")

    def test_skip_two(self):
        self.assertEqual(skip_sequence(2)[:5], [2, 4, 6, 8, 10])
        self.assertEqual(skip_sequence(2)[-1], 100)

    def test_skip_five(self):
        self.assertEqual(skip_sequence(5), list(range(5, 101, 5)))

    def test_skip_ten(self):
        self.assertEqual(skip_sequence(10), list(range(10, 101, 10)))

    def test_skip_three(self):
        self.assertEqual(skip_sequence(3)[-1], 99)

    def test_skip_invalid(self):
        with self.assertRaises(ChartError):
            skip_sequence(1)

    def test_skip_bool(self):
        with self.assertRaises(ChartError):
            skip_sequence(True)


class MissingTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(missing_numbers(10, seed=1)), 10)

    def test_unique(self):
        values = missing_numbers(20, seed=2)
        self.assertEqual(len(values), len(set(values)))

    def test_interior(self):
        for value in missing_numbers(10, seed=3, interior=True):
            self.assertTrue(all(item is not None for item in neighbors(value).values()))

    def test_seed_reproducible(self):
        self.assertEqual(missing_numbers(8, seed=4), missing_numbers(8, seed=4))

    def test_zero(self):
        with self.assertRaises(ChartError):
            missing_numbers(0)

    def test_bool(self):
        with self.assertRaises(ChartError):
            missing_numbers(True)

    def test_too_many(self):
        with self.assertRaises(ChartError):
            missing_numbers(101)

    def test_too_many_interior(self):
        with self.assertRaises(ChartError):
            missing_numbers(65, interior=True)


class ProblemTest(unittest.TestCase):
    def test_position_prompt(self):
        item = ChartProblem("position", 47)
        self.assertIn("47", item.prompt)
        self.assertEqual(item.answer, "第5行第7列")

    def test_neighbors_answer(self):
        item = ChartProblem("neighbors", 47)
        self.assertEqual(item.answer, "37、57、46、48")

    def test_neighbors_edge_rejected(self):
        with self.assertRaises(ChartError):
            ChartProblem("neighbors", 1)

    def test_skip_answer(self):
        item = ChartProblem("skip", 20, 5)
        self.assertEqual(item.answer, "25")

    def test_skip_overflow(self):
        with self.assertRaises(ChartError):
            ChartProblem("skip", 98, 5)

    def test_bad_kind(self):
        with self.assertRaises(ChartError):
            ChartProblem("guess", 5)

    def test_frozen(self):
        item = ChartProblem("position", 5)
        with self.assertRaises(AttributeError):
            item.kind = "skip"  # type: ignore[misc]


class GenerateTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_problems(10, seed=1)), 10)

    def test_unique(self):
        items = generate_problems(20, seed=2)
        keys = [(item.kind, item.number, item.step) for item in items]
        self.assertEqual(len(keys), len(set(keys)))

    def test_single_kind(self):
        items = generate_problems(8, ["position"], seed=3)
        self.assertTrue(all(item.kind == "position" for item in items))

    def test_neighbors_interior(self):
        for item in generate_problems(20, ["neighbors"], seed=4):
            self.assertTrue(all(value is not None for value in neighbors(item.number).values()))

    def test_seed_reproducible(self):
        self.assertEqual(generate_problems(8, seed=5), generate_problems(8, seed=5))

    def test_zero(self):
        with self.assertRaises(ChartError):
            generate_problems(0)

    def test_empty_kinds(self):
        with self.assertRaises(ChartError):
            generate_problems(3, [])

    def test_bad_kind(self):
        with self.assertRaises(ChartError):
            generate_problems(3, ["guess"])

    def test_too_many(self):
        with self.assertRaises(ChartError):
            generate_problems(9999)


if __name__ == "__main__":
    unittest.main()
