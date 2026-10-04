# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Filtering the minion list by tier, type and search text."""

from __future__ import annotations

from typing import List, Optional, Sequence

from bgtools.core.domain import Minion


def filter_minions(minions: Sequence[Minion], tier: Optional[int],
                   race: Optional[str], search: Optional[str]) -> List[Minion]:
    out = list(minions)
    if tier:
        out = [m for m in out if m.tier == tier]
    if race:
        r = race.lower().replace("_", " ")
        out = [m for m in out if any(r in x.lower() for x in m.races)]
    if search:
        s = search.lower()
        out = [m for m in out if s in m.name.lower() or s in m.text.lower()]
    return out
