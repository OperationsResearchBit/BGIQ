# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""A titled list of minions: the tavern, your board, your hand."""

from typing import Dict, List, Sequence

from bgtools.core.domain import Mark, Minion
from bgtools.ui import bgui


def _mark_text(mark: Mark) -> str:
    return bgui.c(mark.text, bgui.STYLE["mark_triple" if mark.kind == "triple" else "mark_fit"])


def section(title: str, minions: Sequence[Minion], color: str,
            marks: Dict[int, Mark] = None, show_text: bool = False,
            note: str = "") -> List[str]:
    marks = marks or {}
    lines = [bgui.header(title, len(minions), color, note)]
    if not minions:
        lines.append(bgui.c(bgui.EMPTY_SECTION, bgui.STYLE["dim"]))
    for n, m in enumerate(minions, 1):
        if not m.known:
            lines.append(f"{n:>2}  " + bgui.c(f"? {m.name}", bgui.STYLE["error"]))
            continue
        mark = marks.get(n - 1)
        lines += bgui.minion_lines(
            m.name, m.atk, m.hp, m.tier, list(m.races), m.text, golden=m.golden,
            num=n, mark=_mark_text(mark) if mark else "", show_text=show_text)
    return lines
