# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The MATCH COMPLETE panel shown after a game ends."""

from typing import List

from bgtools.core.domain import COMPARE_MIN, Snapshot
from bgtools.ui import bgui


def match_panel(snap: Snapshot) -> List[str]:
    if snap.match is None:
        return []
    rec, cmp = snap.match.record, snap.match.comparison
    st = bgui.STYLE
    lines = [bgui.header(bgui.MATCH_TITLE, None, st["match_header"]),
             bgui.c(f"Final board: {rec.total} ({rec.atk} atk + {rec.hp} hp)"
                    f"  ·  Placement: {rec.placement or '?'}", st["match_main"])]
    if cmp.average is not None:
        word = "above" if cmp.diff >= 0 else "below"
        lines.append(bgui.c(f"Average of your last {cmp.count} games: {cmp.average:.0f}  ·  "
                            f"{abs(cmp.diff):.0f} {word} average", st["match_compare"]))
    else:
        lines.append(bgui.c(f"Comparison starts after {COMPARE_MIN} earlier games "
                            f"({cmp.count} saved)", st["dim"]))
    return lines
