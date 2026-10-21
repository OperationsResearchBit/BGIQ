# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""One way to get combat odds: calculate them exactly when the fight is small, else simulate."""

from typing import Sequence

from .combat_exact import DEFAULT_BUDGET, exact_odds
from .combat_sim import CombatOdds, Fighter, simulate


def estimate(you: Sequence[Fighter], opp: Sequence[Fighter], runs: int = 1000,
             seed: int = 0, budget: int = DEFAULT_BUDGET, you_tier: int = 0, opp_tier: int = 0,
             pool: Sequence[Fighter] = ()) -> CombatOdds:
    """Exact odds (method "exact") when the fight fits `budget` states, else `runs` simulated
    fights with `seed` (method "sampled"). The command and the tracker both call this.
    Give the hero tiers to get hero damage; give `pool` for "summon a random tier N minion"."""
    return (exact_odds(you, opp, budget, you_tier, opp_tier)
            or simulate(you, opp, runs, seed, you_tier, opp_tier, pool))
