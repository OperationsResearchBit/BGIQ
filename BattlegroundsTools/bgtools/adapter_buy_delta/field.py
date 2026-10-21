# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""buy_delta before combat: your board now against a typical field of opponent boards.

Before the fight nobody knows who you meet or what they field. So the opponent is a seeded sample of
typical boards for this turn, and the answer is the average of `buy_delta` over that sample.
Pure: data in, a plain tuple out. The card pool arrives as an argument (the app reads it from the
card data; tests write it inline).

The boards are a guess, labelled as one: stats are the printed ones (no buffs, no triples), the size
per turn is a rough curve, and the tier range is the pace table in `analysis/tempo.py`.
"""

import math
import random
from collections import Counter
from typing import List, Optional, Sequence, Tuple

from bgtools.adapter_buy_delta.delta import Change, Outcome, Result, base_score, compare, to_result
from bgtools.analysis.combat_odds import RUNS
from bgtools.analysis.tempo import LATE, PACE

FIELD = 12            # opponent boards per shop. More is steadier and slower (see IDEA.md, Cost).
SEED = 0              # same turn and pool in, same boards out
MAX_BOARD = 7
# turn -> usual number of minions on an opponent's board (a rough curve, not measured)
SIZE = {1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 5, 9: 6, 10: 6}
_ORDER = {"ok": 0, "rough": 1, "unmodeled": 2}      # worst state wins when boards are averaged


def field_boards(pool: Sequence, turn: int, count: int = FIELD, seed: int = SEED) -> List[list]:
    """`count` opponent boards of minions from `pool`, sized and tiered for `turn`. [] if `pool`
    has no minion in the tier range."""
    low, high = PACE.get(turn, LATE)
    usable = [m for m in pool if isinstance(getattr(m, "tier", None), int) and low <= m.tier <= high]
    if not usable:
        return []
    size = min(MAX_BOARD, SIZE.get(turn, MAX_BOARD))
    rng = random.Random(seed * 1000 + turn)
    return [[rng.choice(usable) for _ in range(size)] for _ in range(count)]


def field_tier(turn: int) -> int:
    """A typical hero tavern tier on `turn`: the middle of the pace range (a guess, like the boards)."""
    low, high = PACE.get(turn, LATE)
    return (low + high + 1) // 2


def field_bases(board: Sequence, field: Sequence[Sequence], runs: int = RUNS, you_tier: int = 0,
                opp_tier: int = 0) -> List[Optional[Outcome]]:
    """The no-purchase score against each board in `field`, to pass to `buy_delta_vs_field` as `bases`
    (it is the same for every minion, so work it out once per board state, not once per minion)."""
    return [base_score(board, opp, runs, you_tier, opp_tier) for opp in field]


def buy_delta_vs_field(board: Sequence, field: Sequence[Sequence], minion, runs: int = RUNS,
                       bases: Optional[Sequence[Optional[Outcome]]] = None, you_tier: int = 0,
                       opp_tier: int = 0) -> Optional[Result]:
    """(value, best_slot, state, unit): the mean change over `field`, the slot most boards preferred
    (ties: the first one seen), and the worst state seen. None when no board in `field` gives a number.
    The boards are averaged *before* rounding and before the noise floor, so many small real gains add up
    instead of each being cut to 0 on its own. On a full board the slots read "swap N" (sell minion N)."""
    got = (compare(board, opp, minion, runs, bases[i] if bases is not None else None, you_tier, opp_tier)
           for i, opp in enumerate(field))
    changes = [c for c in got if c is not None]
    if not changes:
        return None
    slots = Counter(c.slot for c in changes)
    top = max(slots.values())
    mean_damage = (None if any(c.damage is None for c in changes)
                   else math.fsum(c.damage for c in changes) / len(changes))
    mean = Change(math.fsum(c.points for c in changes) / len(changes), mean_damage,
                  next(c.slot for c in changes if slots[c.slot] == top),
                  max((c.state for c in changes), key=lambda st: _ORDER.get(st, 0)),
                  any(c.sampled for c in changes))
    return to_result(mean, boards=len(changes))


def field_note(turn: int) -> str:
    """The dim label for the tavern header."""
    return f"vs typical turn {turn} boards (estimate)"
