# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Which minion types are in this lobby? Worked out from the taverns you have seen.

A Battlegrounds lobby uses LOBBY_TYPES of the game's types, so once you have seen that many
the rest are certainly out. Before that, a type that has not shown up after MIN_SIGHTINGS
typed tavern minions is probably out (a type in the lobby would almost surely have appeared).
Change LOBBY_TYPES if the game changes how many types a lobby uses.
"""

from __future__ import annotations

from typing import Mapping, Optional, Sequence

from bgtools.core.domain import Lobby

LOBBY_TYPES = 5
MIN_SIGHTINGS = 20


def infer_lobby(counts: Mapping[str, int], all_types: Sequence[str]) -> Optional[Lobby]:
    """None until at least one typed minion has been seen."""
    seen = tuple(sorted(r for r, n in counts.items() if n > 0 and r != "Neutral"))
    sightings = sum(counts[r] for r in seen)
    if not seen:
        return None
    rest = tuple(t for t in sorted(all_types) if t not in seen)
    if len(seen) >= LOBBY_TYPES:
        return Lobby(seen=seen, out=rest, complete=True, sightings=sightings)
    out = rest if sightings >= MIN_SIGHTINGS else ()
    return Lobby(seen=seen, out=out, complete=False, sightings=sightings)
