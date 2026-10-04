# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Rules that mark tavern minions worth a look.

Each rule is a function ``rule(minion, main, targets) -> Optional[Mark]`` that looks at
one tavern minion and returns a Mark, or None when it has nothing to say.
RULES lists them in priority order: a minion gets the mark of the first rule that
fires, and earlier rules win when there are more candidates than MAX_MARKS.

To add a rule, write the function and decorate it with ``@rule`` (see
docs/ARCHITECTURE.md). Nothing else in the app needs to change.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence

from bgtools.core.domain import Mark, Minion, to_int
from bgtools.core.ports import TargetMap

MAX_MARKS = 2

Rule = Callable[[Minion, Optional[str], TargetMap], Optional[Mark]]
RULES: List[Rule] = []


def rule(fn: Rule) -> Rule:
    """Register a rule. Rules run in the order they are registered."""
    RULES.append(fn)
    return fn


@rule
def triple_target(m: Minion, main: Optional[str], targets: TargetMap) -> Optional[Mark]:
    name = m.name.lower()
    if name not in targets:
        return None
    why = targets[name][1]
    return Mark("triple", "★ triple target" + (f": {why}" if why else ""))


@rule
def fits_board(m: Minion, main: Optional[str], targets: TargetMap) -> Optional[Mark]:
    if main and (main in m.races or "All" in m.races):
        return Mark("fit", f"✓ fits {main}")
    return None


def pick_marks(tavern: Sequence[Minion], main: Optional[str],
               targets: TargetMap) -> Dict[int, Mark]:
    """Choose at most MAX_MARKS tavern minions to mark, each with a short reason.

    Earlier rules come first. Within a rule, higher tavern tier first, then leftmost.
    Returns {tavern position (0-based): Mark}.
    """
    cands = []
    for i, m in enumerate(tavern):
        if not m.known:
            continue
        for rank, fn in enumerate(RULES):
            mark = fn(m, main, targets)
            if mark is not None:
                cands.append((rank, -(to_int(m.tier) or 0), i, mark))
                break
    cands.sort(key=lambda x: x[:3])
    return {c[2]: c[3] for c in cands[:MAX_MARKS]}
