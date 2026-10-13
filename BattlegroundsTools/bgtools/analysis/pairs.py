# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Finds minions you hold more than one copy of (a pair is one step from a triple)."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Tuple

from bgtools.core.domain import Minion


def find_pairs(minions: Iterable[Minion]) -> Tuple[Tuple[str, int], ...]:
    """(name, copies) for every card you hold 2 or more of, most copies first.

    Golden minions are skipped: a golden card is already a finished triple.
    """
    counts = Counter(m.name for m in minions if m.known and not m.golden)
    pairs = [(name, n) for name, n in counts.items() if n >= 2]
    return tuple(sorted(pairs, key=lambda p: (-p[1], p[0])))
