# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""simcore: win / tie / loss odds for two Battlegrounds boards (keywords only). Standard library only."""

from .boards import parse_board
from .combat_estimate import estimate
from .combat_exact import DEFAULT_BUDGET, exact_odds
from .combat_sim import CombatOdds, Fighter, simulate

__all__ = ["parse_board", "estimate", "exact_odds", "simulate", "Fighter", "CombatOdds", "DEFAULT_BUDGET"]
