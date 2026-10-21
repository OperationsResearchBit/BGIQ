# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""How the fight odds look: two aligned rows (labels, then numbers) and an honest note.

Pure text. With color=True the numbers are colored: win green, tie yellow, loss red, and any
zero (or "--") dim grey, so a number lights up only when it matters. Stdlib and bgui only.
"""

from typing import List, Optional

LABELS = ("my lethal", "win", "tie", "loss", "opp lethal")
_WIDTHS = (9, 4, 4, 4, 10)          # wide enough for "100%" and for the longest label
_GAP = "   "
_COLOR = {"win": "1;92", "tie": "1;93", "loss": "1;91"}
_LETHAL_COLOR = ("1;92", "1;91")      # my lethal is good news (green), the opponent's is bad (red)
_DIM = "90"


def _pct(p: Optional[float]) -> str:
    return "--" if p is None else f"{p:.0%}"


def _center(text: str, width: int) -> str:
    return " " * ((width - len(text)) // 2) + text


def odds_rows(win: Optional[float] = None, tie: Optional[float] = None,
              loss: Optional[float] = None, mine: str = "--", theirs: str = "--",
              color: bool = False) -> List[str]:
    """Two rows: the labels, then the numbers under them. None shows as "--"."""
    values = (mine, _pct(win), _pct(tie), _pct(loss), theirs)
    names = ("lethal", "win", "tie", "loss", "lethal")
    top, bottom = [], []
    for n, (label, value, name, width) in enumerate(zip(LABELS, values, names, _WIDTHS)):
        top.append(_dress(_center(label, width).ljust(width), _DIM, color))
        if value in ("--", "0%"):
            shade = _DIM
        else:
            shade = _LETHAL_COLOR[n // 4] if name == "lethal" else _COLOR[name]
        bottom.append(_dress(_center(value, width).ljust(width), shade, color))
    return [_GAP.join(top).rstrip(), _GAP.join(bottom).rstrip()]


def _dress(text: str, code: str, color: bool) -> str:
    if not color:
        return text
    from bgtools.ui import bgui          # only when drawing in color
    return bgui.c(text, code)


def damage_line(avg_deal: Optional[float], avg_take: Optional[float]) -> str:
    """'average hero damage: you deal 6, you take 3', or '' when neither can be worked out."""
    parts = []
    if avg_deal is not None:
        parts.append(f"you deal {avg_deal:.0f}")
    if avg_take is not None:
        parts.append(f"you take {avg_take:.0f}")
    return "average hero damage: " + ", ".join(parts) if parts else ""


def effects_note(unmodeled: int, total: int = 0) -> str:
    """Which part of the board the estimate cannot see. Counts minions, not effects."""
    if unmodeled <= 0:
        return ""
    if total <= 0:
        return (f"{unmodeled} minion has an effect not modeled" if unmodeled == 1
                else f"{unmodeled} minions have effects not modeled")
    if unmodeled == 1:
        return f"1 of {total} minions has an effect not modeled"
    return f"{unmodeled} of {total} minions have effects not modeled"


def confidence(unmodeled: int, total: int) -> str:
    """high: nothing skipped. medium: fewer than half the minions. low: half or more."""
    if unmodeled <= 0:
        return "high"
    return "medium" if total > 0 and unmodeled * 2 < total else "low"


def note_line(unmodeled: int, total: int = 0) -> str:
    """'<note> · <confidence> confidence' for a screen, or '' when nothing is skipped."""
    note = effects_note(unmodeled, total)
    if not note:
        return ""
    return f"{note} · {confidence(unmodeled, total)} confidence"
