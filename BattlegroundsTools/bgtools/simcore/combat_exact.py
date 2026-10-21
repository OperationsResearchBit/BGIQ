# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Exact win / tie / loss odds (and hero damage) for the combat rules in combat_sim.py (no sampling error).

Every random choice (who attacks first when both boards are the same size, which foe is hit) is
walked with its probability. States already solved are remembered, so equal positions are worked
once. When a fight needs more than `budget` distinct states, `exact_odds` gives up (None) and the
caller falls back to sampling. The rules mirror `combat_sim._fight` line for line; keep them in step.
Deathrattles are not walked here (a summon changes the board size mid-fight): a fight with one
gets None, so the caller samples it.
"""

from typing import Dict, Iterator, List, Optional, Sequence, Tuple

from .combat_sim import CombatOdds, Dist, Fighter, make_odds

DEFAULT_BUDGET = 50_000    # keeps the worst case near a second; bigger fights fall back to sampling

# A living minion is (attack, health, flags, tier); a dead one is always DEAD, so equal positions
# match. The tier is 0 unless that side's hero tier is known (it only matters for hero damage).
_TAUNT, _SHIELD, _VENOM, _REBORN, _WIND = 1, 2, 4, 8, 16
DEAD = (0, 0, 0, 0)

Minion = Tuple[int, int, int, int]
Side = Tuple[Minion, ...]
Result = Dist                                # (outcome, damage) -> chance


class _TooBig(Exception):
    pass


def _flags(f: Fighter) -> int:
    return (_TAUNT * f.taunt + _SHIELD * f.shield + _VENOM * f.venomous
            + _REBORN * f.reborn + _WIND * f.windfury)


def _alive(side: Side) -> bool:
    return any(m[1] > 0 for m in side)


def _can_hurt(side: Side) -> bool:
    return any(m[1] > 0 and m[0] > 0 for m in side)


def _hurt(hp: int, flags: int, dmg: int) -> Tuple[int, int, bool]:
    """Deal damage. The bool is True if it landed (a Divine Shield absorbs it instead)."""
    if dmg <= 0:
        return hp, flags, False
    if flags & _SHIELD:
        return hp, flags & ~_SHIELD, False
    return hp - dmg, flags, True


def _hit(a: Minion, d: Minion) -> Tuple[Minion, Minion]:
    """a attacks d; both take damage at the same time (same order as combat_sim._hit)."""
    (aa, ah, af, at), (da, dh, df, dt) = a, d
    dh, df, landed = _hurt(dh, df, aa)
    if landed and af & _VENOM:
        dh, af = 0, af & ~_VENOM
    ah, af, landed = _hurt(ah, af, da)
    if landed and df & _VENOM:
        ah, df = 0, df & ~_VENOM
    out = []
    for atk, hp, fl, tr in ((aa, ah, af, at), (da, dh, df, dt)):
        if hp <= 0 and fl & _REBORN:           # back with 1 health, no shield
            hp, fl = 1, fl & ~(_REBORN | _SHIELD)
        out.append((atk, hp, fl, tr) if hp > 0 else DEAD)
    return out[0], out[1]


def _swings(mine: Side, foes: Side, i: int, left: int, p: float) -> Iterator[Tuple[float, Side, Side]]:
    """Every way minion i's attack can go: (probability, your side, their side)."""
    a = mine[i]
    if left == 0 or a[1] <= 0 or not _alive(foes):
        yield p, mine, foes
        return
    alive = [j for j, m in enumerate(foes) if m[1] > 0]
    pool = [j for j in alive if foes[j][2] & _TAUNT] or alive
    for j in pool:
        na, nd = _hit(a, foes[j])
        m2 = mine[:i] + (na,) + mine[i + 1:]
        f2 = foes[:j] + (nd,) + foes[j + 1:]
        yield from _swings(m2, f2, i, left - 1, p / len(pool))


def _stand(side: Side, hero_tier: int) -> int:
    return hero_tier + sum(m[3] for m in side if m[1] > 0)


def exact_odds(you: Sequence[Fighter], opp: Sequence[Fighter], budget: int = DEFAULT_BUDGET,
               you_tier: int = 0, opp_tier: int = 0) -> Optional[CombatOdds]:
    """Exact odds (runs=0, method="exact"), or None if the fight is too big or too deep to solve,
    or has a deathrattle. With a hero tier the damage of each win (yours) or loss (theirs) is exact too."""
    if any(f.deathrattle for f in tuple(you) + tuple(opp)):
        return None
    mine: Side = tuple((f.atk, f.hp, _flags(f), f.tier if you_tier > 0 else 0) if f.hp > 0 else DEAD
                       for f in you)
    theirs: Side = tuple((f.atk, f.hp, _flags(f), f.tier if opp_tier > 0 else 0) if f.hp > 0 else DEAD
                         for f in opp)
    memo: Dict[tuple, Result] = {}

    def solve(state: tuple) -> Result:
        got = memo.get(state)
        if got is not None:
            return got
        if len(memo) >= budget:
            raise _TooBig
        sides, ptr, turn = (state[0], state[1]), [state[2], state[3]], state[4]
        a, b = _alive(sides[0]), _alive(sides[1])
        if a and not b:
            res: Result = {(1, _stand(sides[0], you_tier)): 1.0}
        elif b and not a:
            res = {(-1, _stand(sides[1], opp_tier)): 1.0}
        elif not (a or b) or (not _can_hurt(sides[0]) and not _can_hurt(sides[1])):
            res = {(0, 0): 1.0}                 # nobody left, or nobody can ever deal damage: a tie
        else:
            att_side, foe_side = sides[turn], sides[1 - turn]
            n = len(att_side)
            i = next((ptr[turn] + k) % n for k in range(n) if att_side[(ptr[turn] + k) % n][1] > 0)
            ptr[turn] = (i + 1) % n
            res = {}
            for p, m2, f2 in _swings(att_side, foe_side, i, 2 if att_side[i][2] & _WIND else 1, 1.0):
                new = (m2, f2) if turn == 0 else (f2, m2)
                for key, q in solve((new[0], new[1], ptr[0], ptr[1], 1 - turn)).items():
                    res[key] = res.get(key, 0.0) + p * q
        memo[state] = res
        return res

    def start(turn: int) -> Result:
        return solve((mine, theirs, 0, 0, turn))

    try:
        if len(mine) != len(theirs):                       # the side with more minions goes first
            dist = start(0 if len(mine) > len(theirs) else 1)
        else:                                              # same size: a coin flip
            dist = {}
            for half in (start(0), start(1)):
                for key, q in half.items():
                    dist[key] = dist.get(key, 0.0) + q / 2
    except (_TooBig, RecursionError):
        return None
    unmodeled = sum(1 for f in tuple(you) + tuple(opp) if f.has_effect)
    dist = {k: round(v, 12) for k, v in dist.items()}
    return make_odds(dist, unmodeled, 0, "exact", you_tier, opp_tier)
