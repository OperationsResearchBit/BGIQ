# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Try buy_delta on boards you type in. Pure: text in, text out (no game, no card data).

Boards are "atk/hp" separated by commas; add keywords after a size: taunt, shield, venom, reborn,
wind. Text after a "#" is card text, so `5/5 # Deathrattle: x` shows the "?" case.
"""

from typing import List, Optional, Sequence

from bgtools.adapter_buy_delta.delta import buy_delta
from bgtools.adapter_buy_delta.field import buy_delta_vs_field
from bgtools.core.domain import Minion

FLAGS = {"taunt": "taunt", "shield": "shield", "venom": "venomous", "reborn": "reborn",
         "wind": "windfury"}
EXAMPLE = [("3/3", "4/4", "2/2, 5/5"), ("3/3", "2/2, 2/2", "2/2"), ("3/3", "4/4", "5/5 # Deathrattle: x"),
           ("1/1, 1/1, 1/1, 1/1, 1/1, 1/1, 1/1", "4/4", "5/5"), ("", "4/4", "5/5")]


def parse_board(text: str) -> List[Minion]:
    """"3/3, 2/4 taunt, 5/5 # Deathrattle: x" -> minions. Raises ValueError on a bad size."""
    out = []
    for part in filter(None, (p.strip() for p in (text or "").split(","))):
        part, _, card_text = part.partition("#")
        size, *words = part.split()
        atk, _, hp = size.partition("/")
        if not (atk.isdigit() and hp.isdigit()):
            raise ValueError(f'"{size}" is not atk/hp, for example 3/3')
        flags = {FLAGS[w]: True for w in words if w in FLAGS}
        out.append(Minion("T_001", "Test", int(atk), int(hp), 1, (), card_text.strip(), **flags))
    return out


def describe(got) -> str:
    """One result as text: "+12% at back", "-3%~ at front", "?", "+12% swap 3" (full board), "nothing shown"."""
    if got is None:
        return "nothing shown"
    value, slot, state, unit = got
    if state == "unmodeled":
        return "?"
    where = f" {slot}" if slot.startswith("swap") else f" at {slot}"
    return f"{value:+d}{' dmg' if unit == 'dmg' else '%'}" + ("~" if state == "rough" else "") + where


def show(you: str, opp: Optional[str], shop: str, field: Optional[Sequence[Sequence]] = None) -> str:
    """The lines for one board pair. With `field` (typical boards) `opp` is ignored."""
    board = parse_board(you)
    head = f"you: [{you}]   " + (f"opp: typical boards ({len(field)})" if field is not None else f"opp: [{opp}]")
    lines = ["", head]
    for text in filter(None, (p.strip() for p in shop.split(","))):
        minion = parse_board(text)[0]
        if field is not None:
            got = buy_delta_vs_field(board, field, minion)
        else:
            got = buy_delta(board, parse_board(opp or ""), minion)
        lines.append(f"  shop {text:<22} -> {describe(got)}")
    return "\n".join(lines)


def examples() -> str:
    return "\n".join(show(*case) for case in EXAMPLE)
