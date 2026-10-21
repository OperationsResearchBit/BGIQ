# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Draws the buy_delta number next to a tavern minion. Reads only what a Snapshot holds.

It reads only .value, .slot, .state and .unit, so it does not import `BuyDelta` (the hook-up adds that class to
`core/domain.py`). That keeps `lab.py check` working whether or not the hook-up is applied.
"""

from typing import Any, Optional

from bgtools.ui import bgui

GREEN, DIM, RED = "92", "90", "91"


def token(d: Optional[Any]) -> str:
    """One short colored token for a tavern row, or "" when there is nothing to say."""
    if d is None:
        return ""
    if d.value is None:
        return ""
    rough = {"rough": "~", "unmodeled": "?"}.get(d.state, "")   # ? = this card's effect is not counted
    if d.value == 0:
        return bgui.c("0%" + rough, DIM)
    where = (f" {d.slot}" if d.slot.startswith("swap") else f" at {d.slot}") if d.slot else ""
    unit = " dmg" if getattr(d, "unit", "%") == "dmg" else "%"     # hero damage when the win chance cannot move
    return bgui.c(f"{d.value:+d}{unit}{rough}{where}", GREEN if d.value > 0 else RED)


def label(note: str) -> str:
    """The dim text in the TAVERN header, such as "vs Millhouse's last board (turn 9)"."""
    return bgui.c(note, DIM) if note else ""
