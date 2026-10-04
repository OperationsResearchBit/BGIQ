# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Works out what kind of board you have.

Computed once as a Profile. The on-screen label and the recommender rules both
read it, so "Leaning Murloc" on screen and "fits Murloc" in the advice agree.
"""

from __future__ import annotations

from collections import Counter
from typing import Optional, Sequence, Tuple

from bgtools.core.domain import Profile


def build_label(counts: Counter, wild: int, size: int) -> Tuple[Optional[str], str]:
    """Return (main_type_or_None, label) describing the board's lean."""
    if size == 0:
        return None, "No board yet"
    top, topn = counts.most_common(1)[0] if counts else (None, 0)
    if top and topn + wild >= 3 and (topn + wild) * 2 >= size:
        return top, f"{top} build"
    if len(counts) >= 3 and topn <= 2:
        return None, "Mixed types"
    if top and topn + wild >= 2:
        return top, f"Leaning {top}"
    return None, "No clear type yet"


def build_profile(races_per_minion: Sequence[Sequence[str]], size: int) -> Profile:
    """races_per_minion: the types of each minion whose card is known.
    size: how many minions are on the board (including unknown cards).
    Minions that count as every type ("All") are kept apart as `wild`."""
    counts, wild = Counter(), 0
    for races in races_per_minion:
        if "All" in races:
            wild += 1
            continue
        for r in races:
            counts[r] += 1
    main, label = build_label(counts, wild, size)
    return Profile(counts=tuple(counts.most_common()), wild=wild, size=size,
                   main=main, label=label)
