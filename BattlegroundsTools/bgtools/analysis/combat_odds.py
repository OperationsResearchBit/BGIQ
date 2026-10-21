# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Turn the minions on screen into a combat estimate (used by the live tracker).

Pure: data in, a plain tuple out. Keyword flags are read with getattr, so this also works on
minions that do not have them (they count as having none).
"""

import re
from functools import lru_cache
from typing import Dict, List, Optional, Sequence, Tuple

from bgtools.core.domain import to_int
from bgtools.simcore import Fighter, Summon, estimate
from bgtools.simcore.combat_sim import FLAG_NAMES
from bgtools.simcore.combat_sim import CombatOdds

RUNS = 1000   # fights per estimate; the seed is fixed, so the same boards give the same numbers

# Card text with the keywords and punctuation removed; anything left is an effect the sim skips.
_KEYWORDS = re.compile(r"mega-windfury|windfury|divine shield|venomous|poisonous|reborn|taunt|[^a-z]",
                       re.I)

_COUNT = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3}
_FIXED = re.compile(r"^deathrattle:\s*summon\s+(a|an|one|two|three|\d+)\s+(\d+)\s*/\s*(\d+)\b(.*)$")
_RANDOM = re.compile(r"^deathrattle:\s*summon\s+(a|an|one|two|three|\d+)\s+random\s+tier[ -]?(\d)"
                     r"\s+minions?$")
_FLAG_WORDS = {"taunt": "taunt", "divine shield": "shield", "venomous": "venomous",
               "poisonous": "venomous", "reborn": "reborn", "windfury": "windfury"}
_NOT_A_NAME = re.compile(r"\b(give|deal|gain|get|summon|random|add|destroy|your|all|other|friendly|"
                         r"enemy|then|each|for|of)\b|\d")


def _sentences(text: Optional[str]) -> List[str]:
    text = re.sub(r"<[^>]*>", "", text or "").replace("[x]", "")          # card text carries <b>..</b> tags
    text = re.sub(r"\s+", " ", text.replace("\n", " "))
    return [x.strip().lower() for x in re.split(r"\.\s*|\.$", text) if x.strip()]


def _fixed_summon(m) -> Optional[Summon]:
    count = _COUNT.get(m.group(1)) or int(m.group(1))
    rest = m.group(4)
    flags = tuple(sorted({v for k, v in _FLAG_WORDS.items() if k in rest}))
    left = re.sub("|".join(map(re.escape, _FLAG_WORDS)), " ", rest)
    left = re.sub(r"\b(with|and)\b|,", " ", left)
    if _NOT_A_NAME.search(left) or not re.fullmatch(r"[a-z' -]*", left.strip()):
        return None                         # more than a plain token name: not understood
    return Summon(count, int(m.group(2)), int(m.group(3)), 0, flags)


@lru_cache(maxsize=4096)       # card text in, immutable tuple out: safe to cache; saves re-parsing every board minion
def parse_effects(text: Optional[str]) -> Tuple[Tuple[Summon, ...], bool]:
    """(summon deathrattles the sim plays, whether some part of the text is still not understood)."""
    found, unknown = [], False
    for sentence in _sentences(text):
        if not _KEYWORDS.sub("", sentence):
            continue                        # only keywords: taunt, reborn, ...
        got = None
        if (m := _FIXED.match(sentence)):
            got = _fixed_summon(m)
        elif (m := _RANDOM.match(sentence)):
            got = Summon(_COUNT.get(m.group(1)) or int(m.group(1)), tier=int(m.group(2)))
        if got is None:
            unknown = True
        else:
            found.append(got)
    return tuple(found), unknown


def has_effect(text: Optional[str]) -> bool:
    """True when the card has an effect the sim cannot play. A summon deathrattle it can play is not one
    (a random one needs a card pool, see `to_fighter`)."""
    effects, unknown = parse_effects(text)
    return unknown or any(e.tier for e in effects)


def to_fighter(m, pool_ok: bool = False) -> Optional[Fighter]:
    """A Minion -> a Fighter, or None when its attack or health cannot be read.
    `pool_ok`: a card pool will be given to the sim, so "summon a random tier N minion" counts as played."""
    atk, hp = to_int(getattr(m, "atk", None)), to_int(getattr(m, "hp", None))
    if atk is None or hp is None:
        return None
    effects, unknown = parse_effects(getattr(m, "text", ""))
    if not pool_ok:
        unknown = unknown or any(e.tier for e in effects)
    tier = getattr(m, "tier", None)
    return Fighter(atk, hp,
                   taunt=bool(getattr(m, "taunt", False)),
                   shield=bool(getattr(m, "shield", False)),
                   venomous=bool(getattr(m, "venomous", False)),
                   reborn=bool(getattr(m, "reborn", False)),
                   windfury=bool(getattr(m, "windfury", False)),
                   has_effect=unknown,
                   tier=tier if isinstance(tier, int) and not isinstance(tier, bool) else 0,
                   deathrattle=effects)


_pool_cache: Dict[Tuple[int, int], List[Fighter]] = {}


def _pool_fighters(pool: Sequence) -> List[Fighter]:
    """The minions a random summon can pick: not golden, each card once, with a tier."""
    key = (id(pool), len(pool))
    if key not in _pool_cache:
        seen, out = set(), []
        for m in pool:
            f = to_fighter(m, pool_ok=True)
            cid = getattr(m, "card_id", None)
            if f is None or f.tier <= 0 or getattr(m, "golden", False) or cid in seen:
                continue
            seen.add(cid)
            out.append(f)
        _pool_cache.clear()
        _pool_cache[key] = out
    return _pool_cache[key]


def fight_for(you: Sequence, opp: Sequence, runs: int = RUNS, you_tier: int = 0, opp_tier: int = 0,
              pool: Optional[Sequence] = None) -> Optional[CombatOdds]:
    """The full estimate (odds and hero damage) for your board against theirs, or None if either board
    is empty or a minion cannot be read. `you_tier` / `opp_tier` are the heroes' tavern tiers (0 = not
    known, then no damage is given for that side); `pool` lets "summon a random tier N minion" be played."""
    mine = [to_fighter(m, pool is not None) for m in you]
    theirs = [to_fighter(m, pool is not None) for m in opp]
    if not mine or not theirs or any(f is None for f in mine + theirs):
        return None
    cards = _pool_fighters(pool) if pool is not None and any(
        e.tier for f in mine + theirs for e in f.deathrattle) else ()
    return estimate(mine, theirs, runs, 0, you_tier=you_tier, opp_tier=opp_tier, pool=cards)


def odds_for(you: Sequence, opp: Sequence, runs: int = RUNS) -> Optional[Tuple[float, float, float, int]]:
    """(win, tie, lose, unmodeled) for your board against theirs, or None if either board is
    empty or a minion cannot be read."""
    o = fight_for(you, opp, runs)
    return None if o is None else (o.win, o.tie, o.loss, o.unmodeled)
