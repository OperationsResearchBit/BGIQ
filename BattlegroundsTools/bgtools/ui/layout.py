# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Chooses the fullest tracker layout that fits the window, so the screen never scrolls."""

from typing import List

from bgtools.core.domain import Snapshot
from bgtools.ui import bgui
from bgtools.ui.components import (board_line, debug_footer, match_panel, section,
                                   status_line, triple_line)

TIERS_OF_DETAIL = ((False, 0), (False, 1), (False, 2), (False, 3))


def _build(snap: Snapshot, show_text: bool, level: int) -> List[str]:
    """level 0 = full, 1 = small title, 2 = no blank lines, 3 = hand collapsed."""
    sec = bgui.SECTION_COLOR
    gap = [""] if level < 2 else []
    if level == 0:
        lines = [bgui.tracker_banner(), ""]
    else:
        lines = [bgui.c(bgui.TRACKER_TITLE, bgui.STYLE["title"])]
    lines += status_line(snap) + board_line(snap)
    match = match_panel(snap)
    lines += triple_line(snap) + gap + (match + gap if match else [])
    lines += section("TAVERN", snap.tavern, sec["TAVERN"], snap.marks, show_text)
    s = snap.strength
    note = f"{s.atk} atk + {s.hp} hp = {s.total}"
    lines += gap + section("YOUR BOARD", snap.board, sec["YOUR BOARD"], None, show_text, note)
    if level < 3:
        lines += gap + section("YOUR HAND", snap.hand, sec["YOUR HAND"], None, show_text)
    else:
        lines += [bgui.header("YOUR HAND", len(snap.hand), sec["YOUR HAND"])]
    footer = debug_footer(snap)
    if level < 2 and footer:
        lines += [""] + footer
    lines += gap + [bgui.c(bgui.QUIT_HINT, bgui.STYLE["dim"])]
    return lines


def render_screen(snap: Snapshot, show_text: bool = False, rows: int = 40) -> str:
    limit = max(rows - 1, 8)
    tries = ([(True, 0)] if show_text else []) + list(TIERS_OF_DETAIL)
    for show, level in tries:
        lines = _build(snap, show, level)
        if len(lines) <= limit:
            break
    else:
        lines = lines[:limit - 1] + [bgui.c(bgui.TOO_SMALL_HINT, bgui.STYLE["dim"])]
    return "\n".join(lines)
