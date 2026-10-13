# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""One way to get combat odds: calculate them exactly when the fight is small, else simulate."""

from typing import Sequence

from .combat_exact import DEFAULT_BUDGET, exact_odds
from .combat_sim import CombatOdds, Fighter, simulate


def estimate(you: Sequence[Fighter], opp: Sequence[Fighter], runs: int = 1000,
             seed: int = 0, budget: int = DEFAULT_BUDGET) -> CombatOdds:
    """Exact odds (method "exact") when the fight fits `budget` states, else `runs` simulated
    fights with `seed` (method "sampled"). The command and the tracker both call this."""
    return exact_odds(you, opp, budget) or simulate(you, opp, runs, seed)
