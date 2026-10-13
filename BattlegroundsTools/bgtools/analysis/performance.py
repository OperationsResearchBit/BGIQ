# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Turns your saved games into the numbers behind the stats screen."""

from __future__ import annotations

from typing import List, Mapping, Optional, Sequence

from bgtools.core.domain import Performance

RECENT = 10          # games in the "recent form" window
RECENT_MIN = 5       # recent form needs at least this many games
COLD_MIN_GAMES = 15  # cold-streak check needs this much history
COLD_WINDOW = 5
COLD_GAP = 1.0       # last COLD_WINDOW games this much worse than your average
BUILD_MIN = 3        # a build needs this many games to be listed


def _mean(xs: Sequence[int]) -> float:
    return sum(xs) / len(xs)


def summarize(history: Sequence[Mapping]) -> Optional[Performance]:
    """None when no saved game has a placement yet."""
    ps: List[int] = []
    builds = {}
    for h in history:
        p = h.get("placement")
        if isinstance(p, int) and 1 <= p <= 8:
            ps.append(p)
            b = h.get("build")
            if b:
                builds.setdefault(b, []).append(p)
    if not ps:
        return None
    n = len(ps)
    recent = ps[-RECENT:]
    recent_avg = _mean(recent) if len(recent) >= RECENT_MIN else None
    avg = _mean(ps)
    cold = n >= COLD_MIN_GAMES and _mean(ps[-COLD_WINDOW:]) >= avg + COLD_GAP
    by_build = sorted(((b, len(v), _mean(v)) for b, v in builds.items() if len(v) >= BUILD_MIN),
                      key=lambda x: (x[2], -x[1]))
    return Performance(
        games=n, average=avg, top4=sum(p <= 4 for p in ps) / n, wins=ps.count(1) / n,
        blowups=sum(p >= 7 for p in ps) / n,
        distribution=tuple(ps.count(i) for i in range(1, 9)),
        trend=tuple(ps[-20:]), recent_n=len(recent), recent_average=recent_avg,
        cold_streak=cold, by_build=tuple(by_build))
