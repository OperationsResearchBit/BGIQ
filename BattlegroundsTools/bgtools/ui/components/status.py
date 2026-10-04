# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The three summary lines under the title: status, board type, triple targets."""

from typing import List

from bgtools.core.domain import Snapshot
from bgtools.ui import bgui


def status_line(snap: Snapshot) -> List[str]:
    s = snap.status
    gold = f"{s.gold_now}/{s.gold_max}" if s.gold_max is not None else "?"
    text = f"Turn {s.turn or '?'}  ·  Tavern {s.tier or '?'}  ·  Gold {gold}"
    return [bgui.c(text, bgui.STYLE["status"])]


def board_line(snap: Snapshot) -> List[str]:
    p = snap.profile
    if p.counts or p.wild:
        parts = [f"{r} {n}" for r, n in p.counts]
        if p.wild:
            parts.append(f"All {p.wild}")
        text = "Board: " + " · ".join(parts) + "  →  " + p.label
    else:
        text = "Board: " + p.label
    return [bgui.c(text, bgui.STYLE["board_line"])]


def triple_line(snap: Snapshot) -> List[str]:
    tier = snap.status.tier
    if tier is None or snap.triple_here is None:
        return []
    if not snap.targets_listed:
        return [bgui.c(bgui.TRIPLE_NONE_LISTED, bgui.STYLE["dim"])]
    shown = snap.triple_here
    if not shown:
        return [bgui.c(f"Triple targets T{tier}: none listed", bgui.STYLE["dim"])]
    more = f" +{len(shown) - 8} more" if len(shown) > 8 else ""
    return [bgui.c(f"Triple targets T{tier}: ", bgui.STYLE["triple_label"])
            + ", ".join(shown[:8]) + more]
