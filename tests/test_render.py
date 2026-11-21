"""百数表渲染测试。"""

import unittest

from hundredchart.model import TOTAL, ChartError, generate_problems
from hundredchart.render import render_chart, render_worksheet


class ChartRenderTest(unittest.TestCase):
    def test_svg(self):
        svg = render_chart()
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn('viewBox="0 0 440 440"', svg)

    def test_all_numbers(self):
        svg = render_chart()
        for value in (1, 2, 10, 55, 100):
            self.assertIn(">%d</text>" % value, svg)

    def test_holes(self):
        svg = render_chart([3, 17, 58])
        for value in (3, 17, 58):
            self.assertNotIn(">%d</text>" % value, svg)
        self.assertIn(">4</text>", svg)

    def test_hole_bounds(self):
        with self.assertRaises(ChartError):
            render_chart([0])

    def test_custom_cell(self):
        svg = render_chart(cell=60)
        self.assertIn('viewBox="0 0 600 600"', svg)

    def test_cell_small(self):
        with self.assertRaises(ChartError):
            render_chart(cell=10)

    def test_cell_bool(self):
        with self.assertRaises(ChartError):
            render_chart(cell=True)

    def test_rect_count(self):
        svg = render_chart()
        self.assertEqual(svg.count("<rect"), TOTAL + 1)


class WorksheetRenderTest(unittest.TestCase):
    def setUp(self):
        self.items = generate_problems(6, seed=11)

    def test_skeleton(self):
        page = render_worksheet(self.items)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertTrue(page.rstrip().endswith("</html>"))

    def test_cards(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="card"'), 6)

    def test_no_answers(self):
        self.assertNotIn("参考答案", render_worksheet(self.items))

    def test_answers(self):
        page = render_worksheet(self.items, answers=True)
        self.assertIn("参考答案", page)
        self.assertEqual(page.count("<tr>"), 7)

    def test_custom_title(self):
        page = render_worksheet(self.items, title="二班百数表")
        self.assertIn("二班百数表", page)

    def test_empty(self):
        with self.assertRaises(ChartError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(ChartError):
            render_worksheet(["47"])

    def test_prompts(self):
        page = render_worksheet(self.items)
        for item in self.items:
            self.assertIn(item.prompt, page)

    def test_escaping(self):
        page = render_worksheet(self.items, title="A&B")
        self.assertIn("A&amp;B", page)


if __name__ == "__main__":
    unittest.main()
