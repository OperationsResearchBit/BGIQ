# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
import unittest

from bgtools.analysis.board_type import build_profile


class BoardType(unittest.TestCase):
    def label(self, races, size=None):
        return build_profile(races, len(races) if size is None else size).label

    def test_empty_board(self):
        self.assertEqual(self.label([]), "No board yet")

    def test_clear_majority_is_a_build(self):
        self.assertEqual(self.label([["Beast"]] * 3 + [["Demon"]]), "Beast build")

    def test_two_of_a_type_is_leaning(self):
        self.assertEqual(self.label([["Murloc"], ["Murloc"], ["Demon"], ["Beast"], ["Mechanical"]]),
                         "Mixed types")
        self.assertEqual(self.label([["Murloc"], ["Murloc"], ["Demon"]]), "Leaning Murloc")

    def test_three_types_no_dominant_is_mixed(self):
        self.assertEqual(self.label([["Beast"], ["Demon"], ["Murloc"]]), "Mixed types")

    def test_all_type_minions_count_toward_the_main_type(self):
        p = build_profile([["Beast"], ["Beast"], ["All"]], 3)
        self.assertEqual((p.main, p.wild, p.label), ("Beast", 1, "Beast build"))

    def test_unknown_cards_still_count_toward_size(self):
        self.assertEqual(build_profile([["Beast"]], 2).label, "No clear type yet")


if __name__ == "__main__":
    unittest.main()
