# hundredchart

[![CI](https://github.com/eastyou/hundredchart/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/hundredchart/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

10×10 百数表生成器：完整表格、留空练习、位置与相邻数查询、跳数序列，一次备好一年级的数感训练材料。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 完整百数表 SVG
hundredchart chart -o chart.svg

# 遮住 12 个数字，打印成填空表
hundredchart chart --holes 3,17,28,39,44,55,61,72,86,93,98,100 -o blank.svg

# 生成 10 道位置 / 相邻数 / 跳数混合练习，附答案
hundredchart sheet --count 10 --seed 1 --answers -o sheet.html

# 查询数字位置
hundredchart position 47
# 47 在第 5 行第 7 列

# 查询上下左右
hundredchart neighbors 47
```

## 功能

- 10×10 百数表 SVG，格子尺寸可调
- 指定数字留空，直接生成填空表
- 三种题型：行列位置、上下左右相邻数、跳数
- 相邻数自动处理边界，越界显示“无”
- 跳数支持步长 2–10，序列不越过 100
- 题目去重，随机种子可复现
- A4 打印排版，答案单独一页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
