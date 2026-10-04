# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Card data from HearthstoneJSON (https://hearthstonejson.com), cached on disk."""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

from bgtools.core.domain import Card, Minion, clean_text, normalize_races

URL = "https://api.hearthstonejson.com/v1/latest/enUS/cards.json"


def parse_cards(raw: List[dict]) -> List[Card]:
    cards = []
    for c in raw:
        races = c.get("races") or ([c["race"]] if c.get("race") else [])
        cards.append(Card(
            id=c.get("id", ""),
            name=c.get("name", "?"),
            kind=c.get("type", ""),
            tier=c.get("techLevel"),
            attack=c.get("attack"),
            health=c.get("health"),
            races=tuple(normalize_races(races)),
            text=c.get("text") or "",
            is_golden="battlegroundsNormalDbfId" in c,
            has_golden="battlegroundsPremiumDbfId" in c,
        ))
    return cards


def is_bg_minion(card: Card) -> bool:
    """Normal (non-golden) Battlegrounds minions only."""
    return (card.kind == "MINION" and card.tier is not None
            and not card.is_golden            # golden versions point back to the normal card
            and card.has_golden               # real BG minions have a golden counterpart
            and not card.name.startswith("["))  # internal cards such as "[BGTEMPLATE] VFX Dummy"


class HearthstoneJsonCards:
    """CardSource backed by HearthstoneJSON. Downloads once, then reads the cache."""

    def __init__(self, cache: Path, file: Optional[str] = None):
        self._cache = Path(cache)
        self._file = file
        self._cards: Optional[List[Card]] = None

    def _load(self, refresh: bool = False) -> List[Card]:
        if self._cards is not None and not refresh:
            return self._cards
        if self._file:
            raw = json.loads(Path(self._file).read_text(encoding="utf-8"))
        else:
            if refresh or not self._cache.exists():
                print("Downloading card data...", file=sys.stderr)
                req = urllib.request.Request(URL, headers={"User-Agent": "bgminions/1.0"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read()
                self._cache.parent.mkdir(parents=True, exist_ok=True)
                self._cache.write_bytes(data)
            raw = json.loads(self._cache.read_text(encoding="utf-8"))
        self._cards = parse_cards(raw)
        return self._cards

    def refresh(self) -> None:
        self._load(refresh=True)

    def by_id(self) -> Dict[str, Card]:
        return {c.id: c for c in self._load()}

    def minions(self) -> List[Minion]:
        out = []
        for c in self._load():
            if not is_bg_minion(c):
                continue
            out.append(Minion(
                card_id=c.id, name=c.name, atk=c.attack if c.attack is not None else 0,
                hp=c.health if c.health is not None else 0, tier=c.tier,
                races=c.races or ("Neutral",), text=clean_text(c.text)))
        out.sort(key=lambda m: (m.tier, m.name))
        return out

    def tier_by_name(self) -> Dict[str, int]:
        """Lowercase minion name -> tavern tier, for Battlegrounds minions."""
        idx: Dict[str, int] = {}
        for c in self._load():
            if is_bg_minion(c):
                idx.setdefault(c.name.lower(), c.tier)
        return idx
