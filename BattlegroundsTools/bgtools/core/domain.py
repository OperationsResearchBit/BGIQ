# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Plain data types and tiny pure helpers shared by every layer.

Nothing here reads files, prints, or knows about the screen.
"""

from __future__ import annotations

import html
import re
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple, Union

Number = Union[int, str]  # a stat from the log, or "?" when it can't be read

HISTORY_KEEP = 200  # games kept in history.json
COMPARE_MAX = 10    # compare against at most this many earlier games
COMPARE_MIN = 3     # ...and only once there are at least this many


def to_int(value) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_races(raw: Sequence[str]) -> List[str]:
    """'MECHANICAL' -> 'Mechanical', 'MURLOC' -> 'Murloc'."""
    return [r.title().replace("_", " ") for r in raw]


def clean_text(text: Optional[str]) -> str:
    """Strip HTML tags and HearthstoneJSON placeholders from card text."""
    if not text:
        return ""
    text = text.replace("\n", " ").replace("[x]", "")
    text = re.sub(r"</?[^>]+>", "", text)          # <b>, <i>, ...
    text = re.sub(r"[$#](\d+)", r"\1", text)      # $3 / #3 -> 3
    text = text.replace("_", " ")
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


@dataclass(frozen=True)
class Card:
    """One card from the card database, already in bgtools' own terms."""
    id: str
    name: str
    kind: str                     # "MINION", "HERO", ...
    tier: Optional[int]           # tavern tier, None if the card has none
    attack: Optional[int]
    health: Optional[int]
    races: Tuple[str, ...]        # normalized, may be empty
    text: str                     # raw card text (see clean_text)
    is_golden: bool               # the golden version of another card
    has_golden: bool              # a real Battlegrounds minion has a golden version


@dataclass(frozen=True)
class Minion:
    """A minion as shown on screen."""
    card_id: str
    name: str
    atk: Number
    hp: Number
    tier: Number
    races: Tuple[str, ...]        # empty means Neutral
    text: str = ""
    golden: bool = False
    known: bool = True            # False when the card id is not in the card data
    taunt: bool = False           # keyword flags, read from the log's entity tags
    shield: bool = False          # Divine Shield
    venomous: bool = False
    reborn: bool = False
    windfury: bool = False


@dataclass(frozen=True)
class Profile:
    """What kind of board you have. One source for the label and the advice."""
    counts: Tuple[Tuple[str, int], ...]   # (type, how many), biggest first
    wild: int                              # minions that count as every type
    size: int
    main: Optional[str]
    label: str


@dataclass(frozen=True)
class Strength:
    atk: int
    hp: int

    @property
    def total(self) -> int:
        return self.atk + self.hp


@dataclass(frozen=True)
class Mark:
    kind: str   # "triple" or "fit"
    text: str


@dataclass(frozen=True)
class Status:
    turn: Optional[int]
    tier: Optional[int]
    gold_now: Optional[int]
    gold_max: Optional[int]


@dataclass(frozen=True)
class GameRecord:
    key: str
    total: int
    atk: int
    hp: int
    minions: int
    placement: Optional[int]
    turns: int
    races: Tuple[Tuple[str, int], ...] = ()   # types on your final board (type, count)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class Comparison:
    count: int                    # earlier games considered
    average: Optional[float]      # None until COMPARE_MIN games are saved
    diff: Optional[float]


@dataclass(frozen=True)
class MatchPanel:
    record: GameRecord
    comparison: Comparison


@dataclass(frozen=True)
class Tempo:
    """How your tavern tier compares with a typical curve for this turn."""
    verdict: str      # "behind", "on pace" or "ahead"
    low: int          # typical tier range for this turn
    high: int


@dataclass(frozen=True)
class Performance:
    """Your results over the saved games. Placement 1 is best."""
    games: int                                # games with a known placement
    average: float
    top4: float                               # share of games, 0..1
    wins: float
    blowups: float                            # share of 7th and 8th places
    distribution: Tuple[int, ...]             # games per placement, index 0 = 1st
    trend: Tuple[int, ...]                    # placements, oldest first (recent games)
    recent_n: int
    recent_average: Optional[float]           # None until there are enough games
    cold_streak: bool                         # recent games clearly worse than usual
    by_build: Tuple[Tuple[str, int, float], ...]   # (build, games, average), best first


@dataclass(frozen=True)
class Lobby:
    """Which minion types are in this lobby, worked out from the taverns you have seen."""
    seen: Tuple[str, ...]        # types seen in a tavern
    out: Tuple[str, ...]         # types that are out (certain) or probably out
    complete: bool               # True when every lobby type has been seen, so `out` is certain
    sightings: int               # tavern minions with a type that were counted


@dataclass(frozen=True)
class Hero:
    name: str
    health: Optional[int]        # health + armor, None if it cannot be read
    place: Optional[int]


@dataclass(frozen=True)
class Odds:
    """Estimated result of the fight under way (see analysis/combat_odds.py)."""
    win: float
    tie: float
    loss: float
    unmodeled: int               # minions with a card effect the estimate does not model
    current: bool = True         # False once that fight is over and the shop is open
    total: int = 0               # minions on both boards (how many the estimate covers)
    my_lethal: Optional[float] = None    # chance this fight takes the opponent's hero to 0; None if unknown
    opp_lethal: Optional[float] = None   # chance it takes yours to 0; None if unknown
    avg_deal: Optional[float] = None     # hero damage you deal / take, averaged over every outcome
    avg_take: Optional[float] = None


@dataclass(frozen=True)
class Comp:
    """A build you want to play, from comps.txt."""
    name: str
    tribe: str
    core: Tuple[str, ...]        # card names, as written
    note: str = ""


@dataclass(frozen=True)
class CompMatch:
    comp: Comp
    have: Tuple[str, ...]        # core cards on your board or in your hand
    missing: Tuple[str, ...]
    in_tavern: Tuple[str, ...]   # missing cards that are in the tavern right now


@dataclass(frozen=True)
class BuyDelta:
    """What adding one tavern minion would do to your next fight (see adapter_buy_delta/delta.py)."""
    value: Optional[int]         # whole percent points of win chance (a tie counts half), or of hero damage; None if no number
    slot: Optional[str]          # "front", "middle", "back", or "swap N" on a full board
    state: str                   # "ok", "rough" or "unmodeled"
    unit: str = "%"              # "%" win chance; "dmg" hero damage (shown when the win chance cannot move)


@dataclass(frozen=True)
class Snapshot:
    """Everything the screen needs for one frame. UI pieces are functions of this."""
    status: Status
    profile: Profile
    tavern: Tuple[Minion, ...]
    board: Tuple[Minion, ...]
    hand: Tuple[Minion, ...]
    marks: Dict[int, Mark]                 # tavern position (0-based) -> mark
    strength: Strength
    targets_listed: bool                   # does triple_targets.txt have any cards?
    triple_here: Optional[Tuple[str, ...]]  # your targets at this tier; None if tier unknown
    match: Optional[MatchPanel] = None
    debug: Tuple[str, ...] = ()
    tempo: Optional[Tempo] = None
    pairs: Tuple[Tuple[str, int], ...] = ()   # cards you hold 2+ copies of
    lobby: Optional[Lobby] = None
    hero: Optional[Hero] = None
    next_opponent: Optional[Hero] = None
    odds: Optional[Odds] = None
    comps: Tuple[CompMatch, ...] = ()
    buy_deltas: Dict[int, BuyDelta] = field(default_factory=dict)   # tavern position (0-based)
    buy_note: str = ""                                              # "vs <hero>'s last board"
