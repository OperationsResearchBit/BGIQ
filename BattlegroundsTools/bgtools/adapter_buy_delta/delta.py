# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""How much would adding one tavern minion change your next fight?

Pure: data in, plain values out. Boards are lists of Minion-like objects (the ones
`analysis/combat_odds.py` reads). Slots: "front" is the leftmost place (it attacks first), "back" the
rightmost, "middle" the one between. On a full board a minion must be sold: "swap N" puts the new one
where minion N (1 = leftmost) stood.

Two measures, one rule for choosing between them:

    win chance : score = win + tie / 2          shown as  +12%
    hero damage: damage = dealt - taken         shown as  +3 dmg   (needs both hero tiers)

The win chance is the honest headline, but it saturates: a board that already wins about 100% cannot
win more, so every buy would read 0%. When the win chance cannot move and the hero damage can, the
damage is shown instead, with its own unit, so the number never silently changes meaning.

The module has three layers, each using only the one below it:

    buy_delta / to_result   rounding, noise floor, choice of unit      (the public face)
    compare                 one buy against one opposing board, unrounded
    evaluate / estimate     one fight: exact when it is small, sampled when it is not
"""

import math
from dataclasses import dataclass
from typing import List, NamedTuple, Optional, Sequence, Tuple

from bgtools.analysis.combat_odds import RUNS, to_fighter
from bgtools.simcore import CombatOdds, Fighter, exact_odds, simulate

# --- Rules of the board -------------------------------------------------------------------------------
MAX_BOARD = 7        # a board holds seven minions

# --- Cost control: how hard we work per fight ---------------------------------------------------------
BUDGET = 5_000       # exact-solver states per fight before it gives up. Lower than simcore's default on
                     # purpose: 21 or so fights per shop must stay quick. A starting point; tune it.
EXACT_MAX = 11       # try the exact solver only when both boards together hold at most this many minions.
                     # Measured: it succeeds 81% or more up to 11, 41% at 12, 25% at 13, and a failed try
                     # wastes about 45 ms. Above this the fight is simulated straight away.
SWAP_TRIES = 3       # on a full board, only the weakest few minions (lowest attack + health) are tried as the
                     # one to sell; selling a strong minion is almost never the best buy.
BATCH = 100          # simulated fights per step when a fight is too big to solve exactly
MIN_RUNS = 200       # never stop sampling before this many
TARGET_SE = 0.02     # stop once the score is known to about 2 percent points (one standard error). A
                     # lopsided fight (95 / 5) gets there in a few hundred runs; an even one needs ~1000.

# --- What counts as a real change ---------------------------------------------------------------------
NOISE_FLOOR = 3      # percent points. A sampled change smaller than this may be sampling noise, so it reads 0.
DAMAGE_NOISE_FLOOR = 1.0   # the same idea for hero damage (points of damage, sampled fights only)
SATURATED = 0.98     # above this win score extra win chance is not worth chasing: options are compared by
                     # hero damage instead (see `_better`)

PERCENT, DAMAGE = "%", "dmg"     # the two units a Result can be in


class Result(NamedTuple):
    """The answer shown to the player. `value` is whole percent points of win chance, or whole points of
    hero damage when `unit` is "dmg". `state` is "ok", "rough" (a minion on either board has an effect the
    sim skips) or "unmodeled" (the tavern minion itself has one: the number counts its stats and keywords
    only). A NamedTuple, so `result[0]` and `Result(...) == (v, s, st, u)` keep working."""
    value: Optional[int]
    slot: Optional[str]
    state: str
    unit: str = PERCENT


@dataclass(frozen=True)
class Outcome:
    """One fight, summarized: what the rest of the module compares."""
    score: float                 # win + tie / 2, between 0 and 1
    damage: Optional[float]      # average damage dealt minus taken; None when a hero tier is not known
    sampled: bool                # True when simulated (noisy), False when solved exactly


@dataclass(frozen=True)
class Change:
    """One buy against one opposing board, before any rounding. Averaged over a field of boards."""
    points: float                # change in score, as a fraction (0.12 = 12 percent points)
    damage: Optional[float]      # change in average damage; None when unknown
    slot: str
    state: str
    sampled: bool


# --- One fight ----------------------------------------------------------------------------------------

def _damage(o: CombatOdds, known: bool) -> Optional[float]:
    """Average hero damage dealt minus taken. None when the hero tiers were not given (the sim then leaves
    its damage tables empty, so zero would be a lie); a missing table with tiers means no such outcome."""
    return (o.avg_deal() or 0.0) - (o.avg_take() or 0.0) if known else None


def estimate(you: List[Fighter], opp: List[Fighter], runs: int, seed: int, budget: int,
             you_tier: int = 0, opp_tier: int = 0) -> Outcome:
    """Exact when the fight fits `budget` states, else simulated in batches of BATCH (seeds count up from
    `seed`, so the same boards give the same answer). Sampling stops early once the score is steady: the
    less even the fight, the fewer runs it needs, up to `runs`."""
    known = you_tier > 0 and opp_tier > 0
    exact = exact_odds(you, opp, budget, you_tier, opp_tier) if budget > 0 else None
    if exact is not None:
        return Outcome(exact.win + exact.tie / 2, _damage(exact, known), False)
    wins = ties = damage = 0.0
    n = 0
    while n < runs:
        o = simulate(you, opp, BATCH, seed + n // BATCH, you_tier, opp_tier)
        wins += o.win * BATCH
        ties += o.tie * BATCH
        damage += (_damage(o, known) or 0.0) * BATCH
        n += BATCH
        if n >= MIN_RUNS:
            score = (wins + ties / 2) / n
            var = (wins + ties / 4) / n - score * score      # variance of one fight's 1 / 0.5 / 0 result
            if max(var, 0.0) / n <= TARGET_SE ** 2:
                break
    return Outcome((wins + ties / 2) / n, damage / n if known else None, True)


def evaluate(you: List[Fighter], opp: List[Fighter], runs: int, you_tier: int = 0,
             opp_tier: int = 0) -> Outcome:
    """One board against one board. An empty board loses to any board with a minion."""
    if not you:
        return Outcome(0.0, None, False)
    budget = BUDGET if len(you) + len(opp) <= EXACT_MAX else 0
    return estimate(you, opp, runs, 0, budget, you_tier, opp_tier)


def _better(a: Outcome, b: Outcome) -> bool:
    """Is `a` a better board than `b`? By win score, but scores above SATURATED count as equal, and equal
    scores are separated by hero damage. A strict test: when all else ties, the earlier option wins."""
    sa, sb = min(a.score, SATURATED), min(b.score, SATURATED)
    if abs(sa - sb) > 1e-9:
        return sa > sb
    return (a.damage or 0.0) > (b.damage or 0.0) + 1e-9


# --- Where the new minion can go ----------------------------------------------------------------------

def _slots(n: int) -> List[Tuple[str, int]]:
    """(name, list index) for each place a new minion can go on a board of n, in preference order: when
    two slots score the same, the first one listed wins."""
    out = [("back", n)]
    if 0 < n // 2 < n:           # with 0 or 1 minions the middle is the front or the back
        out.append(("middle", n // 2))
    if n > 0:
        out.append(("front", 0))
    return out


def _options(mine: List[Fighter], new: Fighter) -> List[Tuple[str, List[Fighter]]]:
    """(slot name, board after buying) for each way to add `new`. With room: back, middle, front. On a
    full board something must be sold: "swap N" puts `new` where minion N (1 = leftmost) was."""
    n = len(mine)
    if n < MAX_BOARD:
        return [(name, mine[:i] + [new] + mine[i:]) for name, i in _slots(n)]
    weakest = sorted(range(n), key=lambda i: (mine[i].atk + mine[i].hp, i))[:SWAP_TRIES]
    return [(f"swap {i + 1}", mine[:i] + [new] + mine[i + 1:]) for i in weakest]


# --- One buy against one opposing board ---------------------------------------------------------------

def _fighters(board: Sequence, opp: Sequence, minion=None):
    """(mine, theirs, new) as Fighters, or None when the opposing board is empty or any minion's attack or
    health cannot be read."""
    mine, theirs = [to_fighter(m) for m in board], [to_fighter(m) for m in opp]
    new = to_fighter(minion) if minion is not None else None
    if not theirs or any(f is None for f in mine + theirs) or (minion is not None and new is None):
        return None
    return mine, theirs, new


def base_score(board: Sequence, opp: Sequence, runs: int = RUNS, you_tier: int = 0,
               opp_tier: int = 0) -> Optional[Outcome]:
    """The fight as it stands, before any purchase. It does not depend on the minion, so work it out once
    per opposing board and pass it to `compare` / `buy_delta` as `base`. None when a board cannot be read."""
    got = _fighters(board, opp)
    return None if got is None else evaluate(got[0], got[1], runs, you_tier, opp_tier)


def compare(board: Sequence, opp: Sequence, minion, runs: int = RUNS, base: Optional[Outcome] = None,
            you_tier: int = 0, opp_tier: int = 0) -> Optional[Change]:
    """The best way to add `minion` to `board` against `opp`, unrounded; None when a board cannot be read.
    The gold from selling a minion on a full board is not counted."""
    got = _fighters(board, opp, minion)
    if got is None:
        return None
    mine, theirs, new = got
    before = base if base is not None else evaluate(mine, theirs, runs, you_tier, opp_tier)
    best_slot, best, sampled = "", None, before.sampled
    for slot, after in _options(mine, new):
        o = evaluate(after, theirs, runs, you_tier, opp_tier)
        sampled = sampled or o.sampled
        if best is None or _better(o, best):
            best_slot, best = slot, o
    rough = any(f.has_effect for f in mine + theirs)
    state = "unmodeled" if new.has_effect else "rough" if rough else "ok"
    gain = None if best.damage is None or before.damage is None else best.damage - before.damage
    return Change(best.score - before.score, gain, best_slot, state, sampled)


# --- What the player sees -----------------------------------------------------------------------------

def to_result(c: Change, boards: int = 1) -> Result:
    """Round a Change into a Result. `boards` is how many opposing boards were averaged into it: noise
    shrinks with the square root of that, so the floors shrink too (a mean of 12 small changes is far
    steadier than any one of them). The unit is percent unless that reads 0 and hero damage does not."""
    shrink = math.sqrt(max(boards, 1))
    points = round(c.points * 100)
    if c.sampled and abs(points) < NOISE_FLOOR / shrink:
        points = 0
    damage = 0 if c.damage is None else round(c.damage)
    if c.sampled and c.damage is not None and abs(c.damage) < DAMAGE_NOISE_FLOOR / shrink:
        damage = 0
    if points == 0 and damage != 0:
        return Result(damage, c.slot, c.state, DAMAGE)
    return Result(points, c.slot, c.state)


def buy_delta(board: Sequence, opp: Sequence, minion, runs: int = RUNS, base: Optional[Outcome] = None,
              you_tier: int = 0, opp_tier: int = 0) -> Optional[Result]:
    """(value, best_slot, state, unit) for adding `minion` to `board` against `opp`, or None when the
    opposing board is empty or any minion's attack or health cannot be read. Give both hero tiers to let
    the answer fall back to hero damage when the win chance cannot move."""
    change = compare(board, opp, minion, runs, base, you_tier, opp_tier)
    return None if change is None else to_result(change)
