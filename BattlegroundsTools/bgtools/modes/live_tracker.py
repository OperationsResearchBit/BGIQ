# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The live tracker: follow Power.log while you play and redraw the screen."""

import shutil
import sys
import time
from dataclasses import replace
from typing import List, Optional, Sequence

from bgtools.analysis.board_type import build_profile
from bgtools.adapter_buy_delta.delta import buy_delta
from bgtools.analysis.combat_odds import fight_for
from bgtools.adapter_buy_delta.field import field_boards, field_note, field_tier
from bgtools.adapter_buy_delta.shop import ShopTable, possible_minions
from bgtools.analysis.comps import match_comps, needed_cards, SHOW_TOP
from bgtools.analysis.lobby import infer_lobby
from bgtools.analysis.pairs import find_pairs
from bgtools.analysis.recommender import pick_marks
from bgtools.analysis.stats import board_strength
from bgtools.analysis.tempo import tempo
from bgtools.core.domain import BuyDelta, Comp, Odds, Snapshot, to_int
from bgtools.core.game_state import BOB_CARD, PLAYER_CARD, State
from bgtools.core.paths import data_dir
from bgtools.core.ports import (CardSource, CompsStore, HistoryStore, LogSource, TargetMap,
                                TargetsStore)
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
            f"hero={state.hero(me)} next_opp_id={p.get('NEXT_OPPONENT_PLAYER_ID')} "
            f"next_opp={state.next_opponent(me)}",
            f"shop types seen -> {state.seen_races(bob) or 'none'}",
            f"combat odds: STEP={state.game_tags().get('STEP')} memo={_odds_memo}",
            _buy_debug(state, me),
            f"history={len(history)} games, samples={len(state.samples)}, "
            f"complete={'yes' if state.complete else 'no'}")


_odds_memo = {"key": None, "size": 0, "odds": None}

# buy_delta: the board each hero last fielded against you, and who you meet next.
_seen = {"game": None, "next": None, "shop_key": None, "boards": {}}   # boards: hero -> (turn, board)
_buy_memo = {"key": None, "out": {}}
_pool = {"minions": None}                          # every card, set in run()
_shop = ShopTable()                                # values for each possible shop minion, per board state
_field = {"turn": None, "boards": []}              # typical opponent boards for this game turn
SHOP_BUDGET_S = 0.5                                # seconds of simulation per redraw; the rest follows


def _fresh(state: State) -> None:
    if _seen["game"] != state.game_no:
        _seen.update(game=state.game_no, next=None, shop_key=None, boards={})


def _note_next_opponent(state: State, turn: int, step) -> None:
    """Shop phase: remember who you fight next. Once per (turn, step), so replaying a log is cheap."""
    _fresh(state)
    if _seen["shop_key"] == (turn, step):
        return
    _seen["shop_key"] = (turn, step)
    hero = state.next_opponent(state.controller_of(PLAYER_CARD))
    if hero is not None:
        _seen["next"] = hero.name


def _file_opponent_board(state: State, turn: int, opp) -> None:
    """Combat start: file the opponent's board under the hero noted in the shop phase. Boards fill in
    over a few log lines, so keep the biggest one seen this turn."""
    _fresh(state)
    name = _seen["next"]
    if not name or not opp:
        return
    old = _seen["boards"].get(name)
    if old is None or old[0] != turn or len(opp) > len(old[1]):
        _seen["boards"][name] = (turn, list(opp))


def _field_deltas(state: State, me, board, tavern, turn: int):
    """Before any board is known: your board against typical boards for this turn (see PRECOMBAT.md).
    Done once per board state for every minion that could appear, so a reroll only looks values up."""
    pool, status = _pool["minions"], state.status(me)
    if not pool or status.tier is None:
        return {}, ""
    lobby = infer_lobby(state.seen_races(state.controller_of(BOB_CARD)), state.all_tribes())
    possible = possible_minions(pool, status.tier, lobby.out if lobby else ())
    if _field["turn"] != turn:
        _field.update(turn=turn, boards=field_boards(pool, turn))
    table = _shop.get(board, possible, _field["boards"], turn, status.tier, budget_s=SHOP_BUDGET_S,
                     first=[m.card_id for m in tavern], opp_tier=field_tier(turn))
    out = {n: BuyDelta(*table[m.card_id]) for n, m in enumerate(tavern)
           if m.card_id in table and table[m.card_id][2] != "none"}
    return out, field_note(turn)


def _buy_deltas(state: State, me, board, tavern):
    """({tavern position: BuyDelta}, label) in the shop phase; ({}, "") otherwise."""
    turn = to_int(state.game_tags().get("TURN"))
    if not turn or turn % 2 == 0 or not tavern:
        return {}, ""
    hero = state.next_opponent(me)
    seen = _seen["boards"].get(hero.name) if hero is not None and _seen["game"] == state.game_no else None
    if seen is None:
        return _field_deltas(state, me, board, tavern, (turn + 1) // 2)
    you_tier = state.status(me).tier or 0
    opp_tier = max((to_int(getattr(m, "tier", 0)) or 0 for m in seen[1]), default=0)   # a guess: its best minion
    key = (state.game_no, turn, hero.name, tuple(board), tuple(seen[1]), tuple(tavern), you_tier)
    if _buy_memo["key"] != key:
        out = {}
        for n, m in enumerate(tavern):
            got = buy_delta(board, seen[1], m, you_tier=you_tier, opp_tier=opp_tier)
            if got is not None:
                out[n] = BuyDelta(*got)
        _buy_memo.update(key=key, out=out)
    return _buy_memo["out"], f"vs {hero.name}'s last board (turn {(seen[0] + 1) // 2})"


def _buy_debug(state: State, me) -> str:
    """Debug footer: your board and the boards filed per hero, as (attack, health)."""
    boards = {k: (v[0], [(m.atk, m.hp) for m in v[1]]) for k, v in _seen["boards"].items()}
    mine = [(m.atk, m.hp) for m in state.minion_views(me, "PLAY")]
    return f"buy_delta: next={_seen['next']} you={mine} filed={boards}"


_log_started = []   # empty until this run writes its first line, which starts the file fresh


def _odds_log(key, memo) -> None:
    """Debug: one line when this combat's steps or estimate change (not on every board-size change).
    The file starts fresh each run. While there is no estimate, the boards read are logged too."""
    o = memo["odds"]
    got = "none" if o is None else f"win {o.win:.0%} tie {o.tie:.0%} lose {o.loss:.0%}"
    sig = (key, tuple(memo["steps"]), got, memo["seen"] if o is None else None)
    if memo.get("logged") == sig:
        return
    memo["logged"] = sig
    try:
        path = data_dir() / "combat_odds_log.txt"     # the .exe's folder when frozen, else the repo root
        with open(path, "a" if _log_started else "w", encoding="utf-8") as f:
            _log_started.append(1)
            f.write(f"{time.strftime('%H:%M:%S')} game,turn={key} steps={memo['steps']} "
                    f"seen(you,opp)={memo['seen']} odds={got}\n")
    except OSError:
        pass


def _opp_tier(state: State, me) -> int:
    """The tavern tier of the hero you are fighting, or 0 when the log does not show it."""
    pid = state.player_tags(me).get("NEXT_OPPONENT_PLAYER_ID")
    if not pid or pid == "0":
        return 0
    return to_int(state.player_tags(pid).get("PLAYER_TECH_LEVEL")) or 0


def _combat_odds(state: State, board, opp_board) -> Optional[Odds]:
    """Win/tie/lose estimate for the fight under way, or None during the shop phase.

    Even TURN values are combat (seen in a real log: the shop controller holds the opponent's
    board from MAIN_START to MAIN_END). The boards fill in over a few log lines and shrink as
    minions die, so the estimate is redone only while the two boards are still growing, then
    kept until the turn ends.
    """
    turn = to_int(state.game_tags().get("TURN"))
    if not turn or turn % 2:          # shop phase: keep showing the fight just played
        got, k = _odds_memo["odds"], _odds_memo["key"]
        return replace(got, current=False) if got and k and k[0] == state.game_no else None
    key, memo = (state.game_no, turn), _odds_memo
    if memo["key"] != key:
        memo.update(key=key, size=0, odds=None, steps=[], seen=(0, 0))
    size = len(board) + len(opp_board)
    step = state.game_tags().get("STEP")      # debug trail: why was no estimate made?
    if step not in memo["steps"]:
        memo["steps"].append(step)
    memo["seen"] = (len(board), len(opp_board))
    if state.game_tags().get("STEP") == "MAIN_START" and size > memo["size"]:
        me = state.controller_of(PLAYER_CARD)
        mine, theirs = state.hero(me), state.next_opponent(me)
        opp_tier = _opp_tier(state, me)
        got = fight_for(board, opp_board, you_tier=state.status(me).tier or 0, opp_tier=opp_tier,
                        pool=_pool["minions"])
        if got is not None:
            memo.update(size=size, odds=Odds(
                got.win, got.tie, got.loss, got.unmodeled, total=size,
                my_lethal=got.p_kill(theirs.health if theirs else None),
                opp_lethal=got.p_die(mine.health if mine else None),
                avg_deal=got.avg_deal(), avg_take=got.avg_take()))
    _odds_log(key, memo)
    return memo["odds"]


def build_snapshot(state: State, targets: TargetMap, tiers: dict,
                   history: List[dict], debug: bool = False,
                   comps: Sequence[Comp] = ()) -> Snapshot:
    """Turn the current game state into one frame of data for the screen."""
    bob = state.controller_of(BOB_CARD)
    me = state.controller_of(PLAYER_CARD)
    tavern = state.minion_views(bob, "PLAY")
    board = state.minion_views(me, "PLAY")
    hand = state.minion_views(me, "HAND")
    status = state.status(me)

    profile = build_profile([m.races for m in board if m.known], len(board))
    pairs = find_pairs(list(board) + list(hand))
    matches = match_comps(comps, board, hand, tavern)
    marks = pick_marks(tavern, profile.main, targets, pairs, needed_cards(matches))
    lobby = infer_lobby(state.seen_races(bob), state.all_tribes())
    deltas, buy_note = _buy_deltas(state, me, board, tavern)
    triple_here = None
    if status.tier is not None:
        triple_here = tuple(v[0] for k, v in targets.items() if tiers.get(k) == status.tier)
    return Snapshot(
        status=status, profile=profile, tavern=tuple(tavern), board=tuple(board),
        hand=tuple(hand), marks=marks, strength=board_strength(board),
        targets_listed=bool(targets), triple_here=triple_here,
        match=build_match_panel(state, history),
        tempo=tempo(status.turn, status.tier), pairs=pairs, lobby=lobby,
        hero=state.hero(me), next_opponent=state.next_opponent(me), comps=matches[:SHOW_TOP],
        odds=_combat_odds(state, board, tavern), buy_deltas=deltas, buy_note=buy_note,
        debug=_debug_lines(state, bob, me, history) if debug else ())


def _observe_combat(state: State) -> None:
    """Work out the combat estimate from the boards as they stand after this log line."""
    g = state.game_tags()
    turn = to_int(g.get("TURN"))
    if turn and turn % 2:
        _note_next_opponent(state, turn, g.get("STEP"))
    if not turn or turn % 2 or g.get("STEP") != "MAIN_START":
        return                       # cheap exit: only the start of a combat turn matters
    bob, me = state.controller_of(BOB_CARD), state.controller_of(PLAYER_CARD)
    board, opp = state.minion_views(me, "PLAY"), state.minion_views(bob, "PLAY")
    _file_opponent_board(state, turn, opp)
    _combat_odds(state, board, opp)


def run(cards: CardSource, targets: TargetsStore, history_store: HistoryStore,
        log: LogSource, show_text: bool = False, debug: bool = False,
        follow: bool = True, out=None, comps_store: Optional[CompsStore] = None,
        render=render_screen) -> None:
    out = out or sys.stdout
    by_id = cards.by_id()
    try:
        _pool["minions"] = cards.minions()
    except Exception:
        pass                      # no card pool: buy_delta stays off
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
                if "ZONE" in line or "STEP" in line:
                    _observe_combat(state)
                if state.finished:
                    record_finished(state, history, history_store)
                count += 1
                if count % 200000 == 0:
                    print(f"  ...{count:,} lines", flush=True)
            rows = shutil.get_terminal_size((100, 40)).lines
            if rows != last_rows:
                last_rows, last_shown = rows, None
                out.write(bgui.CLEAR_ALL)
            snap = build_snapshot(state, targets.load(), tiers, history, debug,
                                  comps_store.load() if comps_store else ())
            text = render(snap, show_text, rows)
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
