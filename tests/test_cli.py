"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from hundredchart.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_chart_stdout(self):
        code, out, _ = run(["chart"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", out)

    def test_chart_holes(self):
        code, out, _ = run(["chart", "--holes", "3,17"])
        self.assertEqual(code, 0)
        self.assertNotIn(">3</text>", out)
        self.assertNotIn(">17</text>", out)

    def test_chart_bad_holes(self):
        code, _, err = run(["chart", "--holes", "3,x"])
        self.assertEqual(code, 2)
        self.assertIn("整数", err)

    def test_chart_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "chart.svg"
            code, out, _ = run(["chart", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("已写入", out)

    def test_position(self):
        code, out, _ = run(["position", "47"])
        self.assertEqual(code, 0)
        self.assertIn("第 5 行第 7 列", out)

    def test_position_invalid(self):
        code, _, err = run(["position", "101"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_neighbors(self):
        code, out, _ = run(["neighbors", "47"])
        self.assertEqual(code, 0)
        self.assertIn("上：37", out)
        self.assertIn("下：57", out)
        self.assertIn("左：46", out)
        self.assertIn("右：48", out)

    def test_neighbors_edge(self):
        code, out, _ = run(["neighbors", "1"])
        self.assertEqual(code, 0)
        self.assertIn("上：无", out)
        self.assertIn("左：无", out)

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="card"'), 3)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_single_kind(self):
        code, out, _ = run(["sheet", "--count", "5", "--kinds", "skip", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertIn("下一个数", out)

    def test_sheet_bad_kind(self):
        code, _, err = run(["sheet", "--kinds", "guess"])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_empty_kinds(self):
        code, _, err = run(["sheet", "--kinds", " , "])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_too_many(self):
        code, _, err = run(["sheet", "--count", "9999"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "chart.svg"
            code, _, _ = run(["chart", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
