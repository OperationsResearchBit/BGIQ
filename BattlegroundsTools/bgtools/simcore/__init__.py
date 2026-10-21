# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""simcore: win / tie / loss odds and hero damage for two Battlegrounds boards (keywords and summon
deathrattles). Standard library only."""

from .combat_estimate import estimate
from .combat_exact import DEFAULT_BUDGET, exact_odds
from .combat_sim import CombatOdds, Fighter, Summon, simulate

__all__ = ["estimate", "exact_odds", "simulate", "Fighter", "Summon", "CombatOdds", "DEFAULT_BUDGET"]
