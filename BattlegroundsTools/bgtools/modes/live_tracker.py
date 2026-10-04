# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The live tracker: follow Power.log while you play and redraw the screen."""

import shutil
import sys
import time
from typing import List, Optional

from bgtools.analysis.board_type import build_profile
from bgtools.analysis.recommender import pick_marks
from bgtools.analysis.stats import board_strength
from bgtools.core.domain import Snapshot, to_int
from bgtools.core.game_state import BOB_CARD, PLAYER_CARD, State
from bgtools.core.ports import CardSource, HistoryStore, LogSource, TargetMap, TargetsStore
from bgtools.modes.game_review import build_match_panel, record_finished
from bgtools.ui import bgui
from bgtools.ui.layout import render_screen


def _debug_lines(state: State, bob, me, history: List[dict]) -> tuple:
    counts = {}
    for e in state.ents.values():
        tg = e["tags"]
        card = state.by_id.get(e["card"])
        if tg.get("ZONE") == "PLAY" and card is not None and card.kind == "MINION":
            k = tg.get("CONTROLLER", "?")
            counts[k] = counts.get(k, 0) + 1
    play = " ".join(f"{k}:{v}" for k, v in sorted(counts.items()))
    p = state.player_tags(me)
    return (f"entities={len(state.ents)} bob_ctrl={bob} you_ctrl={me}",
            f"minions in play by controller -> {play or 'none'}",
            f"raw TURN={state.game_tags().get('TURN')} "
            f"TECH={p.get('PLAYER_TECH_LEVEL')} RES={p.get('RESOURCES')} "
            f"USED={p.get('RESOURCES_USED')} TEMP={p.get('TEMP_RESOURCES')} "
            f"player_entity={state.pents.get(to_int(me))}",
            f"history={len(history)} games, samples={len(state.samples)}, "
            f"complete={'yes' if state.complete else 'no'}")


def build_snapshot(state: State, targets: TargetMap, tiers: dict,
                   history: List[dict], debug: bool = False) -> Snapshot:
    """Turn the current game state into one frame of data for the screen."""
    bob = state.controller_of(BOB_CARD)
    me = state.controller_of(PLAYER_CARD)
    tavern = state.minion_views(bob, "PLAY")
    board = state.minion_views(me, "PLAY")
    hand = state.minion_views(me, "HAND")
    status = state.status(me)

    profile = build_profile([m.races for m in board if m.known], len(board))
    marks = pick_marks(tavern, profile.main, targets)
    triple_here = None
    if status.tier is not None:
        triple_here = tuple(v[0] for k, v in targets.items() if tiers.get(k) == status.tier)
    return Snapshot(
        status=status, profile=profile, tavern=tuple(tavern), board=tuple(board),
        hand=tuple(hand), marks=marks, strength=board_strength(board),
        targets_listed=bool(targets), triple_here=triple_here,
        match=build_match_panel(state, history),
        debug=_debug_lines(state, bob, me, history) if debug else ())


def run(cards: CardSource, targets: TargetsStore, history_store: HistoryStore,
        log: LogSource, show_text: bool = False, debug: bool = False,
        follow: bool = True, out=None) -> None:
    out = out or sys.stdout
    by_id = cards.by_id()
    tiers = cards.tier_by_name()
    state = State(by_id)
    state.path = log.path
    history = history_store.load()

    out.write(bgui.CLEAR_ALL + bgui.HOME + bgui.WRAP_OFF)  # clear; stop long lines wrapping
    print(f"Reading {log.path} (catching up, big logs can take a few seconds)...")
    last_shown: Optional[str] = None
    last_check, count, last_rows = time.time(), 0, None
    try:
        while True:
            for line in log.lines():
                state.feed(line)
                if state.finished:
                    record_finished(state, history, history_store)
                count += 1
                if count % 200000 == 0:
                    print(f"  ...{count:,} lines", flush=True)
            rows = shutil.get_terminal_size((100, 40)).lines
            if rows != last_rows:
                last_rows, last_shown = rows, None
                out.write(bgui.CLEAR_ALL)
            snap = build_snapshot(state, targets.load(), tiers, history, debug)
            text = render_screen(snap, show_text, rows)
            if text != last_shown:
                out.write(bgui.frame(text))
                out.flush()
                last_shown = text
            if not follow:
                return
            if time.time() - last_check > 3:
                last_check = time.time()
                if log.switch_if_newer():
                    state.reset()
                    state.path = log.path
            time.sleep(0.3)
    except KeyboardInterrupt:
        print()
    finally:
        out.write(bgui.WRAP_ON)  # turn line wrapping back on
        out.flush()
