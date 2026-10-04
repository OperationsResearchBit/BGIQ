# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Rebuilds a game from Hearthstone's Power.log, one line at a time.

Pure logic: feed it text lines, ask it questions. It never opens a file.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from bgtools.core.domain import (Card, GameRecord, Minion, Status, clean_text,
                                 to_int)

GAME_ID = -1  # internal key for the GameEntity
BOB_CARD = "TB_BaconShopBob"
PLAYER_CARD = "TB_BaconShop_8P_PlayerE"

RE_CREATE = re.compile(r"FULL_ENTITY - Creating ID=(\d+) CardID=(\S*)")
RE_SHOW = re.compile(r"SHOW_ENTITY - Updating Entity=(.+?) CardID=(\S*)\s*$")
RE_CHANGE = re.compile(r"TAG_CHANGE Entity=(.+?) tag=(\w+) value=(\S*)")
RE_TAG = re.compile(r"GameState\.DebugPrintPower\(\) -\s+tag=(\w+) value=(\S*)")
RE_BRACKET = re.compile(r"\[entityName=.+?\bplayer=\d+\]")
RE_GAMEENT = re.compile(r"GameEntity EntityID=(\d+)")
RE_PLAYER = re.compile(r"Player EntityID=(\d+) PlayerID=(\d+)")
RE_PNAME = re.compile(r"PlayerID=(\d+), PlayerName=(.+)$")


def describe(entity: dict, by_id: Dict[str, Card]) -> Minion:
    """Turn a tracked entity into a Minion (known=False if the card is unknown)."""
    card = by_id.get(entity["card"])
    if card is None:
        return Minion(card_id=entity["card"], name=entity["card"] or "unknown card",
                      atk="?", hp="?", tier="?", races=(), known=False)
    t = entity["tags"]
    return Minion(
        card_id=card.id,
        name=card.name or "?",
        atk=t.get("ATK", card.attack if card.attack is not None else "?"),
        hp=t.get("HEALTH", card.health if card.health is not None else "?"),
        tier=card.tier if card.tier is not None else "?",
        races=card.races,
        text=clean_text(card.text),
        golden=t.get("PREMIUM") == "1" or card.is_golden,
    )


class State:
    def __init__(self, by_id: Optional[Dict[str, Card]] = None):
        self.by_id = by_id or {}
        self.pname: Dict[str, int] = {}  # player name -> player id (set before CREATE_GAME)
        self.path = ""     # log file being read (used to key saved games)
        self.game_no = 0
        self.finished: List[GameRecord] = []  # finished games waiting to be saved
        self.reset()

    def reset(self) -> None:
        self.ents: Dict[int, dict] = {}
        self.pents: Dict[int, int] = {}  # player id -> player entity id
        self.cur: Optional[int] = None
        self.samples: List[tuple] = []   # (atk, hp, minions) of your board, once per turn change
        self.complete: Optional[GameRecord] = None  # summary of the finished game, once it ends

    def ent(self, i: int) -> dict:
        return self.ents.setdefault(i, {"card": "", "tags": {}})

    def learn(self, s: str) -> Optional[int]:
        """Turn an Entity=... field into an id, picking up card/controller hints."""
        s = s.strip()
        if s.isdigit():
            return int(s)
        if s == "GameEntity":
            return GAME_ID
        if not s.startswith("["):
            pid = self.pname.get(s)
            if pid is not None:
                return self.pents.get(pid)
            return None
        m = re.search(r"\bid=(\d+)", s)
        if not m:
            return None
        i = int(m.group(1))
        e = self.ent(i)
        c = re.search(r"cardId=([^\s\]]*)", s)
        if c and c.group(1) and not e["card"]:
            e["card"] = c.group(1)
        p = re.search(r"player=(\d+)", s)
        if p and "CONTROLLER" not in e["tags"]:
            e["tags"]["CONTROLLER"] = p.group(1)
        return i

    def feed(self, line: str) -> None:
        if "GameState.DebugPrintGame()" in line:
            if "BuildNumber=" in line:
                self.pname = {}
            m = RE_PNAME.search(line.rstrip())
            if m:
                self.pname[m.group(2).strip()] = int(m.group(1))
            return
        if "DebugPrintPower()" not in line:
            return
        if "GameState.DebugPrintPower()" not in line:
            # PowerTaskList lags behind GameState, so only use it for hints.
            b = RE_BRACKET.search(line)
            if b:
                self.learn(b.group(0))
            return
        if line.rstrip().endswith("CREATE_GAME"):
            self.reset()
            self.game_no += 1
            return
        m = RE_TAG.search(line)
        if m and self.cur is not None:
            self.ent(self.cur)["tags"][m.group(1)] = m.group(2)
            return
        m = RE_CREATE.search(line)
        if m:
            self.cur = int(m.group(1))
            self.ent(self.cur)["card"] = m.group(2)
            return
        m = RE_SHOW.search(line)
        if m:
            i = self.learn(m.group(1))
            if i is not None:
                self.ent(i)["card"] = m.group(2)
            self.cur = i
            return
        m = RE_CHANGE.search(line)
        if m:
            i = self.learn(m.group(1))
            if i == GAME_ID and m.group(2) == "TURN":
                self.sample_board()  # board as it stood before the turn changes
            if i is not None:
                self.ent(i)["tags"][m.group(2)] = m.group(3)
            if i == GAME_ID and m.group(2) == "STATE" and m.group(3) == "COMPLETE":
                self.finish()
            return
        if RE_GAMEENT.search(line):
            self.cur = GAME_ID
            return
        m = RE_PLAYER.search(line)
        if m:
            eid, pid = int(m.group(1)), int(m.group(2))
            self.pents[pid] = eid
            self.cur = eid
            return
        self.cur = None  # any other line ends an entity block

    def sample_board(self) -> None:
        """Remember your board's total attack/health (never breaks the tracker)."""
        try:
            me = self.controller_of(PLAYER_CARD)
            ents = self.minions(me, "PLAY")
            if not ents:
                return
            atk = hp = 0
            for e in ents:
                d = describe(e, self.by_id)
                if d.known:
                    atk += to_int(d.atk) or 0
                    hp += to_int(d.hp) or 0
            self.samples.append((atk, hp, len(ents)))
        except Exception:
            pass

    def placement(self, me: Optional[str]) -> Optional[int]:
        """Your final placement, read from your hero's leaderboard tag if present."""
        for e in self.ents.values():
            t = e["tags"]
            if (t.get("CARDTYPE") == "HERO" and t.get("CONTROLLER") == me
                    and t.get("ZONE") == "PLAY"):
                p = to_int(t.get("PLAYER_LEADERBOARD_PLACE"))
                if p:
                    return p
        return None

    def finish(self) -> None:
        """Called when the game reports COMPLETE: file the last board seen."""
        try:
            self.sample_board()
            if not self.samples or self.complete is not None:
                return
            atk, hp, n = self.samples[-1]
            me = self.controller_of(PLAYER_CARD)
            self.complete = GameRecord(key=f"{self.path}:{self.game_no}",
                                       total=atk + hp, atk=atk, hp=hp, minions=n,
                                       placement=self.placement(me),
                                       turns=len(self.samples))
            self.finished.append(self.complete)
        except Exception:
            pass

    def controller_of(self, card_prefix: str) -> Optional[str]:
        for e in self.ents.values():
            if e["card"].startswith(card_prefix) and "CONTROLLER" in e["tags"]:
                return e["tags"]["CONTROLLER"]
        return None

    def game_tags(self) -> dict:
        return self.ents.get(GAME_ID, {}).get("tags", {})

    def player_tags(self, ctrl: Optional[str]) -> dict:
        pid = to_int(ctrl)
        if pid is None:
            return {}
        return self.ents.get(self.pents.get(pid), {}).get("tags", {})

    def minions(self, ctrl: Optional[str], zone: str) -> List[dict]:
        out = []
        if ctrl is None:
            return []
        for e in self.ents.values():
            t = e["tags"]
            card = self.by_id.get(e["card"])
            if (t.get("ZONE") == zone and t.get("CONTROLLER") == ctrl
                    and card is not None and card.kind == "MINION"):
                out.append((int(t.get("ZONE_POSITION", 0) or 0), e))
        return [e for _, e in sorted(out, key=lambda x: x[0])]

    def minion_views(self, ctrl: Optional[str], zone: str) -> List[Minion]:
        return [describe(e, self.by_id) for e in self.minions(ctrl, zone)]

    def status(self, me: Optional[str]) -> Status:
        g, p = self.game_tags(), self.player_tags(me)
        turn_raw = to_int(g.get("TURN"))
        turn = (turn_raw + 1) // 2 if turn_raw else None
        res = to_int(p.get("RESOURCES"))
        used = to_int(p.get("RESOURCES_USED")) or 0
        temp = to_int(p.get("TEMP_RESOURCES")) or 0
        gold_now = res + temp - used if res is not None else None
        return Status(turn=turn, tier=to_int(p.get("PLAYER_TECH_LEVEL")),
                      gold_now=gold_now, gold_max=res)
