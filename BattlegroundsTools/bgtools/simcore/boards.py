# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Typed boards: '5/5 taunt, 3/2 shield venom' -> Fighters. Standard library only."""

import re
from typing import List

from .combat_sim import Fighter

FLAGS = {"taunt": "taunt", "shield": "shield", "ds": "shield", "venom": "venomous",
         "venomous": "venomous", "reborn": "reborn", "windfury": "windfury",
         "wf": "windfury", "effect": "has_effect"}


def parse_board(text: str) -> List[Fighter]:
    """Minions left to right, separated by commas. Raises ValueError on a bad minion."""
    out = []
    for part in text.split(","):
        words = part.split()
        if not words:
            continue
        stats = re.fullmatch(r"(\d+)/(\d+)", words[0])
        if not stats:
            raise ValueError(f"expected attack/health like 5/5, got '{words[0]}'")
        flags = {}
        for w in words[1:]:
            if w.lower() not in FLAGS:
                raise ValueError(f"unknown keyword '{w}' (use: {', '.join(sorted(FLAGS))})")
            flags[FLAGS[w.lower()]] = True
        out.append(Fighter(int(stats.group(1)), int(stats.group(2)), **flags))
    return out
