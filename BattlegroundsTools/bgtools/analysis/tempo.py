# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Is your tavern tier on a typical curve for this turn? A rough guide, not a rule.

The table is the usual range strong players sit in: not a fixed plan. Greedy
leveling and tempo-heavy play both leave the range on purpose, so read "behind" or
"ahead" as a prompt to think, not as a mistake.
"""

from __future__ import annotations

from typing import Optional

from bgtools.core.domain import Tempo

# turn -> (lowest, highest) typical tavern tier
PACE = {1: (1, 1), 2: (1, 2), 3: (2, 2), 4: (2, 3), 5: (3, 3), 6: (3, 4),
        7: (4, 4), 8: (4, 5), 9: (5, 5), 10: (5, 6)}
LATE = (6, 6)  # turn 11 and later


def tempo(turn: Optional[int], tier: Optional[int]) -> Optional[Tempo]:
    """None when the turn or tier is unknown."""
    if not turn or not tier or turn < 1:
        return None
    low, high = PACE.get(turn, LATE)
    if tier < low:
        verdict = "behind"
    elif tier > high:
        verdict = "ahead"
    else:
        verdict = "on pace"
    return Tempo(verdict=verdict, low=low, high=high)
