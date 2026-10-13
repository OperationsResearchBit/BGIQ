# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Checks for simcore. Run:  python simcore\\test_simcore.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from simcore import Fighter, estimate, simulate          # noqa: E402
from simcore import parse_board                          # noqa: E402


def win_tie_loss(you, opp):
    r = estimate(you, opp)
    return round(r.win, 6), round(r.tie, 6), round(r.loss, 6)


class Rules(unittest.TestCase):
    def test_bigger_minion_wins(self):
        self.assertEqual(win_tie_loss(parse_board("5/5"), parse_board("3/3")), (1.0, 0.0, 0.0))

    def test_equal_minions_tie(self):
        self.assertEqual(win_tie_loss(parse_board("3/3"), parse_board("3/3")), (0.0, 1.0, 0.0))

    def test_divine_shield_absorbs_a_hit(self):
        self.assertEqual(win_tie_loss(parse_board("2/2 shield"), parse_board("2/2")), (1.0, 0.0, 0.0))

    def test_venomous_kills_anything(self):
        self.assertEqual(win_tie_loss(parse_board("1/1 venom"), parse_board("9/9")), (0.0, 1.0, 0.0))

    def test_effect_is_counted_not_modeled(self):
        self.assertEqual(estimate(parse_board("3/3 effect"), parse_board("1/1")).unmodeled, 1)


class Estimate(unittest.TestCase):
    YOU, OPP = parse_board("4/5, 2/3 shield"), parse_board("3/4 taunt, 5/2")

    def test_small_fight_is_exact(self):
        r = estimate(self.YOU, self.OPP)
        self.assertEqual((r.method, r.runs), ("exact", 0))
        self.assertAlmostEqual(r.win + r.tie + r.loss, 1.0)

    def test_over_budget_samples_and_repeats(self):
        a = estimate(self.YOU, self.OPP, runs=300, seed=4, budget=1)
        self.assertEqual((a.method, a.runs), ("sampled", 300))
        self.assertEqual(a, simulate(self.YOU, self.OPP, 300, 4))

    def test_sampled_agrees_with_exact(self):
        exact, sampled = estimate(self.YOU, self.OPP), estimate(self.YOU, self.OPP, runs=10000, budget=1)
        self.assertLess(abs(exact.win - sampled.win), 0.02)


class Parsing(unittest.TestCase):
    def test_keywords_and_order(self):
        board = parse_board("5/5 taunt, 3/2 ds wf")
        self.assertEqual(board, [Fighter(5, 5, taunt=True), Fighter(3, 2, shield=True, windfury=True)])

    def test_bad_input_raises(self):
        for bad in ("five/5", "3/3 fast"):
            with self.assertRaises(ValueError):
                parse_board(bad)


if __name__ == "__main__":
    unittest.main()
