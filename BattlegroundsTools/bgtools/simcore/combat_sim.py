# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Estimates a combat: your chance to win, tie or lose against a board, and the damage that follows.

Keywords (taunt, divine shield, venomous, reborn, windfury) and summon deathrattles are played out.
Damage to a hero is the winner's tavern tier plus the tiers of its minions left standing.
"""

import random
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

MAX_ATTACKS = 500   # a fight nobody can win (for example all 0 attack) is called a tie
MAX_BOARD = 7       # living minions one side can hold; a summon that does not fit is lost
TOKEN_TIER = 1      # tavern tier counted for a summoned token when damage is worked out
FLAG_NAMES = ("taunt", "shield", "venomous", "reborn", "windfury")


@dataclass(frozen=True)
class Summon:
    """A deathrattle that puts minions on the dead minion's side, to the right of where it stood.

    A fixed token has tier 0 and the given atk / hp / flags. With tier > 0 it is `count` random
    minions of that tavern tier taken from the pool given to `simulate` (atk, hp and flags unused).
    """
    count: int = 1
    atk: int = 0
    hp: int = 0
    tier: int = 0
    flags: Tuple[str, ...] = ()


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
    tier: int = 0               # tavern tier, for hero damage (0 = not known)
    deathrattle: Tuple[Summon, ...] = ()


@dataclass(frozen=True)
class CombatOdds:
    win: float
    tie: float
    loss: float
    unmodeled: int              # minions, on both sides, whose effect is ignored
    runs: int                   # simulated fights; 0 when the odds are exact
    method: str = "sampled"    # "exact" (calculated) or "sampled" (simulated)
    deal: Tuple[Tuple[int, float], ...] = ()   # (damage to their hero, chance) per way you can win
    take: Tuple[Tuple[int, float], ...] = ()   # (damage to your hero, chance) per way you can lose

    def p_kill(self, their_health: Optional[int]) -> Optional[float]:
        """Chance this fight takes their hero to 0 or less. None when it cannot be worked out."""
        if their_health is None or not self.deal:
            return None
        return sum(p for d, p in self.deal if d >= their_health)

    def p_die(self, your_health: Optional[int]) -> Optional[float]:
        """Chance this fight takes your hero to 0 or less. None when it cannot be worked out."""
        if your_health is None or not self.take:
            return None
        return sum(p for d, p in self.take if d >= your_health)

    def avg_deal(self) -> Optional[float]:
        """Damage you deal to their hero, averaged over every outcome (a loss or tie counts 0)."""
        return sum(d * p for d, p in self.deal) if self.deal else None

    def avg_take(self) -> Optional[float]:
        return sum(d * p for d, p in self.take) if self.take else None


Dist = Dict[Tuple[int, int], float]    # (outcome, damage) -> chance. outcome: 1 win, 0 tie, -1 loss


def make_odds(dist: Dist, unmodeled: int, runs: int, method: str,
              you_tier: int = 0, opp_tier: int = 0) -> CombatOdds:
    """Fold a distribution of (outcome, damage) into win / tie / loss and the two damage tables.
    A damage table is left empty when that side's hero tier is not known."""
    win = sum((p for (o, _), p in dist.items() if o == 1), 0.0)
    tie = sum((p for (o, _), p in dist.items() if o == 0), 0.0)
    loss = sum((p for (o, _), p in dist.items() if o == -1), 0.0)
    deal: Dict[int, float] = {}
    take: Dict[int, float] = {}
    for (o, d), p in dist.items():
        if o == 1 and you_tier > 0:
            deal[d] = deal.get(d, 0.0) + p
        elif o == -1 and opp_tier > 0:
            take[d] = take.get(d, 0.0) + p
    return CombatOdds(win, tie, loss, unmodeled, runs, method,
                      tuple(sorted(deal.items())), tuple(sorted(take.items())))


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
    tier: int = 0
    dr: Tuple[Summon, ...] = ()
    died: bool = False          # died since deathrattles were last played


def _live(f: Fighter) -> _Live:
    return _Live(f.atk, f.hp, f.taunt, f.shield, f.venomous, f.reborn, f.windfury, f.tier,
                 f.deathrattle)


def _token(s: Summon) -> _Live:
    flags = set(s.flags)
    return _Live(s.atk, s.hp, "taunt" in flags, "shield" in flags, "venomous" in flags,
                 "reborn" in flags, "windfury" in flags, TOKEN_TIER)


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
        if m.hp <= 0:
            m.died = True                    # its deathrattle (if any) plays after this attack
            if m.reborn:                     # back with 1 health, no shield
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


def _play_deathrattles(sides, ptr, first: int, rng: random.Random, by_tier) -> None:
    """Play the deathrattles of every minion that died since the last call.

    Order: the side that just attacked first, then the other; each side left to right. A summon
    lands to the right of the dead minion if the board has room (7 living). An attack order that
    was already past the dead minion stays past it, so the new minions do not attack out of turn.
    """
    for si in (first, 1 - first):
        side = sides[si]
        i = 0
        while i < len(side):
            m = side[i]
            if m.died:
                m.died = False
                at = i + 1
                for eff in m.dr:
                    for _ in range(eff.count):
                        if sum(1 for x in side if x.hp > 0) >= MAX_BOARD:
                            break
                        if eff.tier:
                            pool = by_tier.get(eff.tier)
                            if not pool:
                                continue
                            born = _live(rng.choice(pool))
                        else:
                            born = _token(eff)
                        side.insert(at, born)
                        if ptr[si] >= at:
                            ptr[si] += 1
                        at += 1
            i += 1


def _stand(side: List[_Live], hero_tier: int) -> int:
    """Damage the side's hero deals by winning: its tavern tier plus every minion left standing."""
    return hero_tier + sum(m.tier for m in side if m.hp > 0)


def _fight(you: List[_Live], opp: List[_Live], rng: random.Random,
           by_tier=None, you_tier: int = 0, opp_tier: int = 0) -> Tuple[int, int]:
    """(outcome, damage): outcome +1 you win, 0 tie, -1 you lose; damage is the hit the loser's hero takes."""
    by_tier = by_tier or {}
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
            _play_deathrattles(sides, ptr, turn, rng, by_tier)
        turn = 1 - turn
    a, b = _alive(you), _alive(opp)
    if a and not b:
        return 1, _stand(you, you_tier)
    if b and not a:
        return -1, _stand(opp, opp_tier)
    return 0, 0


def pool_by_tier(pool: Sequence[Fighter]) -> Dict[int, List[Fighter]]:
    out: Dict[int, List[Fighter]] = {}
    for f in pool:
        if f.tier > 0:
            out.setdefault(f.tier, []).append(f)
    return out


def simulate(you: Sequence[Fighter], opponent: Sequence[Fighter],
             n: int = 1000, seed: int = 0, you_tier: int = 0, opp_tier: int = 0,
             pool: Sequence[Fighter] = ()) -> CombatOdds:
    """Play `n` fights and return the share of wins, ties and losses (and the damage of each win or
    loss when the hero tiers are given). `pool` is where "summon a random tier N minion" draws
    from. Same seed, same answer."""
    if n < 1:
        raise ValueError("n must be at least 1")
    rng = random.Random(seed)
    by_tier = pool_by_tier(pool)
    tally: Counter = Counter()
    for _ in range(n):
        tally[_fight([_live(f) for f in you], [_live(f) for f in opponent], rng,
                     by_tier, you_tier, opp_tier)] += 1
    unmodeled = sum(1 for f in tuple(you) + tuple(opponent) if f.has_effect)
    dist = {k: v / n for k, v in tally.items()}
    return make_odds(dist, unmodeled, n, "sampled", you_tier, opp_tier)
