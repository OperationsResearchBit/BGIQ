# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Exact win / tie / loss odds for the combat rules in combat_sim.py (no sampling error).

Every random choice (who attacks first when both boards are the same size, which foe is hit) is
walked with its probability. States already solved are remembered, so equal positions are worked
once. When a fight needs more than `budget` distinct states, `exact_odds` gives up (None) and the
caller falls back to sampling. The rules mirror `combat_sim._fight` line for line; keep them in step.
"""

from typing import Dict, Iterator, List, Optional, Sequence, Tuple

from .combat_sim import CombatOdds, Fighter

DEFAULT_BUDGET = 50_000    # keeps the worst case near a second; bigger fights fall back to sampling

# A living minion is (attack, health, flags); a dead one is always DEAD, so equal positions match.
_TAUNT, _SHIELD, _VENOM, _REBORN, _WIND = 1, 2, 4, 8, 16
DEAD = (0, 0, 0)

Minion = Tuple[int, int, int]
Side = Tuple[Minion, ...]
Result = Tuple[float, float, float]          # win, tie, loss


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
    (aa, ah, af), (da, dh, df) = a, d
    dh, df, landed = _hurt(dh, df, aa)
    if landed and af & _VENOM:
        dh, af = 0, af & ~_VENOM
    ah, af, landed = _hurt(ah, af, da)
    if landed and df & _VENOM:
        ah, df = 0, df & ~_VENOM
    out = []
    for atk, hp, fl in ((aa, ah, af), (da, dh, df)):
        if hp <= 0 and fl & _REBORN:           # back with 1 health, no shield
            hp, fl = 1, fl & ~(_REBORN | _SHIELD)
        out.append((atk, hp, fl) if hp > 0 else DEAD)
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


def exact_odds(you: Sequence[Fighter], opp: Sequence[Fighter],
               budget: int = DEFAULT_BUDGET) -> Optional[CombatOdds]:
    """Exact odds (runs=0, method="exact"), or None if the fight is too big or too deep to solve."""
    mine: Side = tuple((f.atk, f.hp, _flags(f)) if f.hp > 0 else DEAD for f in you)
    theirs: Side = tuple((f.atk, f.hp, _flags(f)) if f.hp > 0 else DEAD for f in opp)
    memo: Dict[tuple, Result] = {}

    def solve(state: tuple) -> Result:
        got = memo.get(state)
        if got is not None:
            return got
        if len(memo) >= budget:
            raise _TooBig
        sides, ptr, turn = (state[0], state[1]), [state[2], state[3]], state[4]
        a, b = _alive(sides[0]), _alive(sides[1])
        if not (a and b):
            res = (1.0, 0.0, 0.0) if a else (0.0, 0.0, 1.0) if b else (0.0, 1.0, 0.0)
        elif not _can_hurt(sides[0]) and not _can_hurt(sides[1]):
            res = (0.0, 1.0, 0.0)               # nobody can ever deal damage: a tie
        else:
            att_side, foe_side = sides[turn], sides[1 - turn]
            n = len(att_side)
            i = next((ptr[turn] + k) % n for k in range(n) if att_side[(ptr[turn] + k) % n][1] > 0)
            ptr[turn] = (i + 1) % n
            w = t = l = 0.0
            for p, m2, f2 in _swings(att_side, foe_side, i, 2 if att_side[i][2] & _WIND else 1, 1.0):
                new = (m2, f2) if turn == 0 else (f2, m2)
                sw, st, sl = solve((new[0], new[1], ptr[0], ptr[1], 1 - turn))
                w, t, l = w + p * sw, t + p * st, l + p * sl
            res = (w, t, l)
        memo[state] = res
        return res

    def start(turn: int) -> Result:
        return solve((mine, theirs, 0, 0, turn))

    try:
        if len(mine) != len(theirs):                       # the side with more minions goes first
            w, t, l = start(0 if len(mine) > len(theirs) else 1)
        else:                                              # same size: a coin flip
            (w1, t1, l1), (w2, t2, l2) = start(0), start(1)
            w, t, l = (w1 + w2) / 2, (t1 + t2) / 2, (l1 + l2) / 2
    except (_TooBig, RecursionError):
        return None
    unmodeled = sum(1 for f in tuple(you) + tuple(opp) if f.has_effect)
    return CombatOdds(round(w, 12), round(t, 12), round(l, 12), unmodeled, 0, "exact")
