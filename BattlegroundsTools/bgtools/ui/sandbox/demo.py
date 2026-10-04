# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Draws UI pieces from made-up data so you can build one without playing a game."""

from typing import Optional

from bgtools.core.domain import (Comparison, GameRecord, Mark, MatchPanel, Minion,
                                 Profile, Snapshot, Status, Strength)
from bgtools.ui.components import REGISTRY
from bgtools.ui.layout import render_screen


def fake_snapshot() -> Snapshot:
    def m(name, atk, hp, tier, races, text="", golden=False):
        return Minion(name.lower().replace(" ", "_"), name, atk, hp, tier, tuple(races), text, golden)

    tavern = (m("Alley Cat", 3, 2, 3, ["Beast"]), m("Wrath Weaver", 1, 3, 1, ["Demon"]),
              m("Pack Leader", 3, 3, 3, ["Beast"]))
    board = (m("Rat Pack", 2, 2, 2, ["Beast"]), m("Mama Bear", 4, 4, 5, ["Beast"], golden=True),
             m("Zesty Shaker", 3, 3, 2, ["Elemental"]))
    hand = (m("Tabbycat", 2, 2, 1, ["Beast"]),)
    # Hand-made values: the UI layer never imports the analysis layer.
    profile = Profile(counts=(("Beast", 2), ("Elemental", 1)), wild=0, size=3,
                      main="Beast", label="Leaning Beast")
    marks = {2: Mark("triple", "★ triple target: scales when golden"),
             0: Mark("fit", "✓ fits Beast")}
    rec = GameRecord("demo:1", 42, 22, 20, 3, 4, 12)
    return Snapshot(
        status=Status(7, 4, 6, 9), profile=profile, tavern=tavern, board=board, hand=hand,
        marks=marks, strength=Strength(9, 9),
        targets_listed=True, triple_here=("Pack Leader",),
        match=MatchPanel(rec, Comparison(count=0, average=None, diff=None)),
        debug=("demo data, not a real game",))


def run(name: Optional[str] = None, rows: int = 40) -> int:
    snap = fake_snapshot()
    if name is None:
        print(render_screen(snap, show_text=True, rows=rows))
        print("\nPieces you can preview:", ", ".join(sorted(REGISTRY)))
        return 0
    piece = REGISTRY.get(name)
    if piece is None:
        print(f"No piece named '{name}'. Available: {', '.join(sorted(REGISTRY))}")
        return 2
    print("\n".join(piece(snap)))
    return 0
