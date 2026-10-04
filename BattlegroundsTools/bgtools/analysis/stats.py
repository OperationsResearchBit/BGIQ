# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Numbers about boards and finished games."""

from __future__ import annotations

from typing import Iterable, List, Mapping

from bgtools.core.domain import (COMPARE_MAX, COMPARE_MIN, Comparison, GameRecord,
                                 Minion, Strength, to_int)


def board_strength(minions: Iterable[Minion]) -> Strength:
    """Total attack and health. Raw stats only, no keyword scoring."""
    atk = hp = 0
    for m in minions:
        if m.known:
            atk += to_int(m.atk) or 0
            hp += to_int(m.hp) or 0
    return Strength(atk, hp)


def compare_to_history(record: GameRecord, history: List[Mapping]) -> Comparison:
    """Compare a finished board with the average of your earlier games."""
    prev = [h for h in history if h.get("key") != record.key][-COMPARE_MAX:]
    if len(prev) >= COMPARE_MIN:
        avg = sum(h.get("total", 0) for h in prev) / len(prev)
        return Comparison(count=len(prev), average=avg, diff=record.total - avg)
    return Comparison(count=len(prev), average=None, diff=None)
