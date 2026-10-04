# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Rules that mark tavern minions worth a look."""

from __future__ import annotations

from typing import Dict, Optional, Sequence

from bgtools.core.domain import Mark, Minion, to_int
from bgtools.core.ports import TargetMap

MAX_MARKS = 2


def pick_marks(tavern: Sequence[Minion], main: Optional[str],
               targets: TargetMap) -> Dict[int, Mark]:
    """Choose at most two tavern minions to mark, each with a short reason.

    Triple targets come first, then minions that fit your board's main type.
    Within a rule, higher tavern tier first, then leftmost.
    Returns {tavern position (0-based): Mark}.
    """
    cands = []
    for i, m in enumerate(tavern):
        if not m.known:
            continue
        name = m.name.lower()
        tier = to_int(m.tier) or 0
        if name in targets:
            why = targets[name][1]
            text = "★ triple target" + (f": {why}" if why else "")
            cands.append((0, -tier, i, Mark("triple", text)))
        elif main and (main in m.races or "All" in m.races):
            cands.append((1, -tier, i, Mark("fit", f"✓ fits {main}")))
    cands.sort(key=lambda x: x[:3])
    return {c[2]: c[3] for c in cands[:MAX_MARKS]}
