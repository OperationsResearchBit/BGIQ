# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""buy_delta for every minion that could appear in the shop, worked out once per board state.

The numbers depend on your board and on which minions *can* show up, not on the three minions
in the shop right now. So a reroll costs nothing: the table is looked up by card id. It is rebuilt
only when your board, the turn, your tavern tier or the lobby's missing types change.
Pure: the card pool and the opponent field arrive as arguments (no card data is read here).
"""

import time
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from bgtools.adapter_buy_delta.delta import Result
from bgtools.adapter_buy_delta.field import buy_delta_vs_field, field_bases
from bgtools.analysis.combat_odds import RUNS

Table = Dict[str, Result]          # card_id -> (value, best_slot, state)
_FLAGS = ("golden", "taunt", "shield", "venomous", "reborn", "windfury")


def possible_minions(pool: Sequence, tier: int, out_types: Sequence[str] = ()) -> List:
    """Minions that can be offered at `tier`: tier at most `tier`, not golden, each card once, and
    neutral or with a type that is not in `out_types` (types the lobby does not use)."""
    seen, out = set(), []
    for m in pool:
        t = getattr(m, "tier", None)
        races = tuple(getattr(m, "races", ()) or ())
        if not isinstance(t, int) or t > tier or getattr(m, "golden", False) or m.card_id in seen:
            continue
        if races and all(r in out_types for r in races):
            continue
        seen.add(m.card_id)
        out.append(m)
    return out


def board_key(board: Sequence) -> Tuple:
    """What the numbers depend on for a board: stats and keywords of each minion, in order."""
    return tuple((m.card_id, str(m.atk), str(m.hp)) + tuple(bool(getattr(m, f, False)) for f in _FLAGS)
                 for m in board)


class ShopTable:
    """Keeps the table for the latest board state. `get` fills in what is missing, so a time budget can
    spread the work over several redraws: minions not done yet are simply absent from the table."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._key: Optional[Tuple] = None
        self._table: Table = {}
        self._bases: Optional[list] = None      # no-purchase scores, one per field board; same for every minion

    def get(self, board: Sequence, possible: Sequence, field: Sequence[Sequence], turn: int, tier: int,
            runs: int = RUNS, budget_s: Optional[float] = None, first: Sequence[str] = (),
            opp_tier: int = 0) -> Table:
        key = (board_key(board), turn, tier, opp_tier, tuple(m.card_id for m in possible))
        if key != self._key:
            self._key, self._table, self._bases = key, {}, None
        start = self._clock()
        seen = set(first)                      # the minions in the shop right now are priced before the rest
        for m in sorted(possible, key=lambda x: x.card_id not in seen):
            if m.card_id in self._table:
                continue
            if budget_s is not None and self._clock() - start >= budget_s:
                break
            if self._bases is None:
                self._bases = field_bases(board, field, runs, tier, opp_tier)
            got = buy_delta_vs_field(board, field, m, runs, self._bases, tier, opp_tier)
            self._table[m.card_id] = got if got is not None else Result(None, None, "none")
        return self._table

    def complete(self, possible: Sequence) -> bool:
        return all(m.card_id in self._table for m in possible)
