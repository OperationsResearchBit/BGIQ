# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Estimates a combat: your chance to win, tie or lose against a board (v0: keywords only)."""

import random
from dataclasses import dataclass
from typing import List, Sequence

MAX_ATTACKS = 500   # a fight nobody can win (for example all 0 attack) is called a tie


@dataclass(frozen=True)
class Fighter:
    """One minion in a fight. Keywords are plain flags."""
    atk: int
    hp: int
    taunt: bool = False
    shield: bool = False        # Divine Shield
    venomous: bool = False
    reborn: bool = False
    windfury: bool = False
    has_effect: bool = False    # the card has an effect this sim does not model


@dataclass(frozen=True)
class CombatOdds:
    win: float
    tie: float
    loss: float
    unmodeled: int              # minions, on both sides, whose effect is ignored
    runs: int                   # simulated fights; 0 when the odds are exact
    method: str = "sampled"    # "exact" (calculated) or "sampled" (simulated)


@dataclass
class _Live:
    """A minion while the fight is running (the Fighter itself never changes)."""
    atk: int
    hp: int
    taunt: bool
    shield: bool
    venom: bool
    reborn: bool
    wind: bool


def _live(f: Fighter) -> _Live:
    return _Live(f.atk, f.hp, f.taunt, f.shield, f.venomous, f.reborn, f.windfury)


def _hurt(m: _Live, dmg: int) -> bool:
    """Deal damage. True if it landed (a Divine Shield absorbs it instead)."""
    if dmg <= 0:
        return False
    if m.shield:
        m.shield = False
        return False
    m.hp -= dmg
    return True


def _hit(a: _Live, d: _Live) -> None:
    """a attacks d. Both take damage at the same time."""
    if _hurt(d, a.atk) and a.venom:
        d.hp, a.venom = 0, False
    if _hurt(a, d.atk) and d.venom:
        a.hp, d.venom = 0, False
    for m in (a, d):
        if m.hp <= 0 and m.reborn:          # v0: back with 1 health, no shield
            m.hp, m.reborn, m.shield = 1, False, False


def _alive(side: List[_Live]) -> bool:
    return any(m.hp > 0 for m in side)


def _target(foes: List[_Live], rng: random.Random) -> _Live:
    alive = [m for m in foes if m.hp > 0]
    return rng.choice([m for m in alive if m.taunt] or alive)


def _next(side: List[_Live], start: int) -> int:
    """Index of the next living minion at or after `start`, wrapping around."""
    n = len(side)
    return next((start + k) % n for k in range(n) if side[(start + k) % n].hp > 0)


def _fight(you: List[_Live], opp: List[_Live], rng: random.Random) -> int:
    """+1 you win, 0 tie, -1 you lose."""
    sides, ptr = (you, opp), [0, 0]
    turn = 0 if len(you) > len(opp) else 1 if len(opp) > len(you) else rng.randrange(2)
    for _ in range(MAX_ATTACKS):
        if not (_alive(you) and _alive(opp)):
            break
        mine, foes = sides[turn], sides[1 - turn]
        i = _next(mine, ptr[turn])
        ptr[turn] = i + 1
        att = mine[i]
        for _swing in range(2 if att.wind else 1):
            if att.hp <= 0 or not _alive(foes):
                break
            _hit(att, _target(foes, rng))
        turn = 1 - turn
    a, b = _alive(you), _alive(opp)
    return 1 if a and not b else -1 if b and not a else 0


def simulate(you: Sequence[Fighter], opponent: Sequence[Fighter],
             n: int = 1000, seed: int = 0) -> CombatOdds:
    """Play `n` fights and return the share of wins, ties and losses. Same seed, same answer."""
    if n < 1:
        raise ValueError("n must be at least 1")
    rng = random.Random(seed)
    tally = {1: 0, 0: 0, -1: 0}
    for _ in range(n):
        tally[_fight([_live(f) for f in you], [_live(f) for f in opponent], rng)] += 1
    unmodeled = sum(1 for f in tuple(you) + tuple(opponent) if f.has_effect)
    return CombatOdds(tally[1] / n, tally[0] / n, tally[-1] / n, unmodeled, n, "sampled")
