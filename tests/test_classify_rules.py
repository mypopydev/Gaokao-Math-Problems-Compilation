#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "classify"))
import classify  # noqa: E402


class PriorityRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ROOT / "docs" / "classify" / "taxonomy.json", encoding="utf-8") as fh:
            cls.taxo = json.load(fh)

    def assert_primary(self, text, expected):
        self.assertEqual(classify.classify(text, self.taxo)["primary"], expected)

    def test_conic_signal_overrides_line_circle_and_noise(self):
        self.assert_primary(r"椭圆 C: x^2/4+y^2/3=1 的右焦点为 F，直线 l 经过 F", "conic")
        self.assert_primary(r"抛物线 y^2=4x，点 A 到准线的距离为 3", "conic")

    def test_complex_context_keeps_complex_over_conic_choice_words(self):
        self.assert_primary(r"在复平面上，满足 |z-1|=|z+\i| 的复数 z 对应的点的轨迹为（椭圆/圆/直线）", "complex")

    def test_probability_signal_overrides_counting_noise(self):
        self.assert_primary(r"从 10 人中任选 3 人，恰有 1 男 2 女的概率", "prob")
        self.assert_primary(r"随机选取三个砝码，总质量为 9 克的概率", "prob")

    def test_nonstandard_signals_are_prioritized_without_treating_limit_as_calculus(self):
        self.assert_primary(r"极坐标方程 rho=5/(2-4cos theta) 所表示的曲线", "parametric")
        self.assert_primary(r"行列式 |a b; c d| 所有可能的值中最大的是", "matrix")
        self.assert_primary(r"无穷等比数列各项和的极限", "seq")
        self.assert_primary(r"对数方程的解集，利用对数运算法则化简", "elemfunc")

    def test_existing_priority_rules_remain_effective(self):
        self.assert_primary(r"函数 f(x)=\\sin x 的最小值", "trig")
        self.assert_primary(r"在棱锥中求体积", "solid_basic")
        self.assert_primary(r"复数 z 的实部", "complex")
        self.assert_primary(r"根据茎叶图求中位数", "stat")


if __name__ == "__main__":
    unittest.main()
