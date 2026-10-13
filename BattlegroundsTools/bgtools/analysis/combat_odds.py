# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Turn the minions on screen into a combat estimate (used by the live tracker).

Pure: data in, a plain tuple out. Keyword flags are read with getattr, so this also works on
minions that do not have them (they count as having none).
"""

import re
from typing import Optional, Sequence, Tuple

from bgtools.core.domain import to_int
from bgtools.simcore import Fighter, estimate

RUNS = 1000   # fights per estimate; the seed is fixed, so the same boards give the same numbers

# Card text with the keywords and punctuation removed; anything left is an effect the sim skips.
_KEYWORDS = re.compile(r"mega-windfury|windfury|divine shield|venomous|poisonous|reborn|taunt|[^a-z]",
                       re.I)


def has_effect(text: Optional[str]) -> bool:
    text = re.sub(r"<[^>]*>", "", text or "")   # card text carries <b>..</b> tags
    return bool(_KEYWORDS.sub("", text))


def to_fighter(m) -> Optional[Fighter]:
    """A Minion -> a Fighter, or None when its attack or health cannot be read."""
    atk, hp = to_int(getattr(m, "atk", None)), to_int(getattr(m, "hp", None))
    if atk is None or hp is None:
        return None
    return Fighter(atk, hp,
                   taunt=bool(getattr(m, "taunt", False)),
                   shield=bool(getattr(m, "shield", False)),
                   venomous=bool(getattr(m, "venomous", False)),
                   reborn=bool(getattr(m, "reborn", False)),
                   windfury=bool(getattr(m, "windfury", False)),
                   has_effect=has_effect(getattr(m, "text", "")))


def odds_for(you: Sequence, opp: Sequence, runs: int = RUNS) -> Optional[Tuple[float, float, float, int]]:
    """(win, tie, lose, unmodeled) for your board against theirs, or None if either board is
    empty or a minion cannot be read."""
    mine = [to_fighter(m) for m in you]
    theirs = [to_fighter(m) for m in opp]
    if not mine or not theirs or any(f is None for f in mine + theirs):
        return None
    o = estimate(mine, theirs, runs, 0)   # exact when it fits, else sampled
    return (o.win, o.tie, o.loss, o.unmodeled)
