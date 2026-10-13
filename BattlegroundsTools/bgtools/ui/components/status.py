# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The three summary lines under the title: status, board type, triple targets."""

from typing import List

from bgtools.core.domain import Snapshot
from bgtools.ui import bgui


TIER_MAX = 6      # the tier bar has one pip per tier up to here (T7 is a rare extra pip)
TEMPO_STYLE = {"behind": "91", "on pace": "90", "ahead": "92"}


def _pips(now: int, top: int, full: str, empty: str) -> str:
    now = max(0, min(now, top))
    return full * now + empty * (top - now)


def status_line(snap: Snapshot) -> List[str]:
    s = snap.status
    st = bgui.STYLE
    gold = f"{s.gold_now}/{s.gold_max}" if s.gold_max is not None else "?"
    parts = [bgui.c(f"Turn {s.turn or '?'}", st["status"])]
    tier = bgui.c(f"Tavern {s.tier or '?'}", st["status"])
    if s.tier:
        tier += " " + bgui.c(_pips(s.tier, max(TIER_MAX, s.tier), "▰", "▱"),
                             bgui.TIER_FG.get(s.tier, "37"))
    if snap.tempo is not None:
        t = snap.tempo
        tier += " " + bgui.c(f"({t.verdict})", TEMPO_STYLE.get(t.verdict, "90"))
    parts.append(tier)
    coins = ""
    if s.gold_now is not None and s.gold_max is not None:
        coins = " " + bgui.c(_pips(s.gold_now, max(s.gold_max, s.gold_now, 1), "●", "○"), "1;93")
    parts.append(bgui.c(f"Gold {gold}", st["status"]) + coins)
    return [bgui.c("  ·  ", st["dim"]).join(parts)]


def board_line(snap: Snapshot) -> List[str]:
    p = snap.profile
    if p.counts or p.wild:
        parts = [f"{r} {n}" for r, n in p.counts]
        if p.wild:
            parts.append(f"All {p.wild}")
        text = "Board: " + " · ".join(parts) + "  →  " + p.label
    else:
        text = "Board: " + p.label
    return [bgui.c(text, bgui.STYLE["board_line"])]


def triple_line(snap: Snapshot) -> List[str]:
    tier = snap.status.tier
    if tier is None or snap.triple_here is None:
        return []
    if not snap.targets_listed:
        return [bgui.c(bgui.TRIPLE_NONE_LISTED, bgui.STYLE["dim"])]
    shown = snap.triple_here
    if not shown:
        return [bgui.c(f"Triple targets T{tier}: none listed", bgui.STYLE["dim"])]
    more = f" +{len(shown) - 8} more" if len(shown) > 8 else ""
    return [bgui.c(f"Triple targets T{tier}: ", bgui.STYLE["triple_label"])
            + ", ".join(shown[:8]) + more]


def pairs_line(snap: Snapshot) -> List[str]:
    """Cards you hold two or more of: the next copy makes a golden."""
    if not snap.pairs:
        return []
    shown = ", ".join(f"{name} x{n}" for name, n in snap.pairs[:6])
    more = f" +{len(snap.pairs) - 6} more" if len(snap.pairs) > 6 else ""
    return [bgui.c("Pairs (one more = golden): ", bgui.STYLE["triple_label"]) + shown + more]


HERO_WARN = 20     # health at or below this is shown yellow
HERO_DANGER = 10   # ...and at or below this red


def _hp_style(health):
    if health is None:
        return bgui.STYLE["dim"]
    if health <= HERO_DANGER:
        return bgui.STYLE["hero_danger"]
    return bgui.STYLE["hero_warn"] if health <= HERO_WARN else bgui.STYLE["hero_ok"]


def hero_line(snap: Snapshot) -> List[str]:
    """Your health and place, and who you fight next. Shown only when health can be read."""
    h, n = snap.hero, snap.next_opponent
    if h is None or h.health is None:
        return []
    place = f"  ·  place {h.place}/8" if h.place else ""
    text = (bgui.c("You: ", bgui.STYLE["dim"]) + bgui.c(f"{h.health} hp", _hp_style(h.health))
            + bgui.c(place, bgui.STYLE["status"]))
    if n is not None:
        hp = f" ({n.health} hp)" if n.health is not None else ""
        text += bgui.c("   Next: ", bgui.STYLE["dim"]) + bgui.c(n.name + hp, bgui.STYLE["status"])
    lines = [text]
    o = snap.odds
    if o is not None:   # own line: a long hero line gets clipped by narrow windows
        est = (bgui.c("Estimate: " if o.current else "Last fight: ", bgui.STYLE["dim"])
               + bgui.c(f"win {o.win:.0%}  tie {o.tie:.0%}  loss {o.loss:.0%}", bgui.STYLE["status"]))
        if o.unmodeled:
            est += bgui.c(f"  ({o.unmodeled} effects not modeled)", bgui.STYLE["dim"])
        lines.append(est)
    return lines


def lobby_line(snap: Snapshot) -> List[str]:
    """Which minion types are in this lobby (certain once five have been seen)."""
    lb = snap.lobby
    if lb is None:
        return []
    st = bgui.STYLE
    seen = " · ".join(bgui.c(r, bgui.RACE_FG.get(r, "37")) for r in lb.seen)
    if lb.complete:
        out = bgui.c("   Out: " + ", ".join(lb.out), st["dim"]) if lb.out else ""
        return [bgui.c("Lobby: ", st["board_line"]) + seen + out]
    out = bgui.c("   Probably out: " + ", ".join(lb.out), st["dim"]) if lb.out else ""
    return [bgui.c(f"Lobby so far ({len(lb.seen)}/5): ", st["board_line"]) + seen + out]


def comps_line(snap: Snapshot) -> List[str]:
    """Your closest comps from comps.txt: how many core cards you hold and what is missing."""
    lines = []
    for m in snap.comps:
        total = len(m.have) + len(m.missing)
        head = bgui.c(f"Comp: {m.comp.name}", bgui.STYLE["mark_comp"]) + f" {len(m.have)}/{total}"
        if m.in_tavern:
            head += bgui.c("  in tavern now: " + ", ".join(m.in_tavern), bgui.STYLE["mark_fit"])
        elif m.missing:
            more = f" +{len(m.missing) - 3}" if len(m.missing) > 3 else ""
            head += bgui.c("  need: " + ", ".join(m.missing[:3]) + more, bgui.STYLE["dim"])
        lines.append(head)
    return lines
