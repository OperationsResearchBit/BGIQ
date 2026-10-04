# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Plain data types and tiny pure helpers shared by every layer.

Nothing here reads files, prints, or knows about the screen.
"""

from __future__ import annotations

import html
import re
from dataclasses import asdict, dataclass
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
