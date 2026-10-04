# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
import unittest

from bgtools.analysis.recommender import pick_marks
from bgtools.core.domain import Minion


def m(name, tier, races, known=True):
    return Minion(name.lower(), name, 1, 1, tier, tuple(races), known=known)


class Marks(unittest.TestCase):
    def test_triple_target_beats_type_fit(self):
        tavern = [m("A", 3, ["Beast"]), m("B", 3, ["Beast"])]
        marks = pick_marks(tavern, "Beast", {"b": ("B", "why")})
        self.assertEqual(marks[1].kind, "triple")
        self.assertEqual(marks[1].text, "★ triple target: why")
        self.assertEqual(marks[0].kind, "fit")

    def test_at_most_two_marks_higher_tier_first(self):
        tavern = [m("A", 1, ["Beast"]), m("B", 5, ["Beast"]), m("C", 3, ["Beast"])]
        marks = pick_marks(tavern, "Beast", {})
        self.assertEqual(sorted(marks), [1, 2])

    def test_no_main_type_means_no_fit_marks(self):
        self.assertEqual(pick_marks([m("A", 1, ["Beast"])], None, {}), {})

    def test_all_type_fits_any_main_type(self):
        self.assertEqual(pick_marks([m("A", 1, ["All"])], "Murloc", {})[0].text, "✓ fits Murloc")

    def test_unknown_cards_are_never_marked(self):
        self.assertEqual(pick_marks([m("A", 1, [], known=False)], "Beast", {"a": ("A", "")}), {})


if __name__ == "__main__":
    unittest.main()
