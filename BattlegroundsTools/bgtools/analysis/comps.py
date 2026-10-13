# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Matches your board, hand and tavern against the comps you listed in comps.txt."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

from bgtools.core.domain import Comp, CompMatch, Minion

SHOW_TOP = 2   # comps shown on screen
NEEDS_FROM = 2 # tavern marks come from this many best comps


def match_comps(comps: Sequence[Comp], board: Iterable[Minion], hand: Iterable[Minion],
                tavern: Iterable[Minion]) -> Tuple[CompMatch, ...]:
    """Comps you hold at least one core card of, closest first.

    Closest = most core cards held, then most missing cards sitting in the tavern, then
    the order in the file. Golden copies count like plain ones.
    """
    held = {m.name.lower() for m in list(board) + list(hand) if m.known}
    shop = {m.name.lower() for m in tavern if m.known}
    out: List[Tuple[Tuple[int, int, int], CompMatch]] = []
    for order, comp in enumerate(comps):
        have = tuple(c for c in comp.core if c.lower() in held)
        if not have:
            continue
        missing = tuple(c for c in comp.core if c.lower() not in held)
        in_tavern = tuple(c for c in missing if c.lower() in shop)
        out.append(((-len(have), -len(in_tavern), order),
                    CompMatch(comp=comp, have=have, missing=missing, in_tavern=in_tavern)))
    out.sort(key=lambda x: x[0])
    return tuple(m for _, m in out)


def needed_cards(matches: Sequence[CompMatch]) -> Dict[str, str]:
    """lowercase missing core card -> name of the closest comp that wants it."""
    needs: Dict[str, str] = {}
    for m in matches[:NEEDS_FROM]:
        for card in m.missing:
            needs.setdefault(card.lower(), m.comp.name)
    return needs
