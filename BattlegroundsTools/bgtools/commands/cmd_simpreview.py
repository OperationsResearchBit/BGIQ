# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""python -m bgtools simpreview: only the fight odds, read from your real game.

Follows Power.log like `track`, but draws two lines and touches none of your saved files:

    waiting for a fight...   (Ctrl+C to stop)
    my lethal 0%   win 0%   tie 0%   loss 0%   opp lethal 0%

Lethal is the chance the fight takes a hero to 0. It shows `--` when the hero's health or tavern tier is not in the log.
"""

import sys

from bgtools.commands.registry import command
from bgtools.core import paths
from bgtools.core.domain import Snapshot
from bgtools.file_adapters.cards_hsjson import HearthstoneJsonCards
from bgtools.file_adapters.log_replay import ReplayLog
from bgtools.file_adapters.log_tail import LogTail, default_logs_dir, newest_log
from bgtools.modes import live_tracker
from bgtools.ui import odds_view


class _NoHistory:
    """Saves nothing: simpreview only looks, so it never writes your game history."""

    def load(self):
        return []

    def save(self, history) -> None:
        pass


class _NoTargets:
    def load(self):
        return {}


def render_odds(snap: Snapshot, _show_text: bool = False, _rows: int = 0) -> str:
    """The whole screen: a status line, the labels, the numbers, and an honest note."""
    o = snap.odds
    if o is None:
        return "\n".join(["waiting for a fight...   (Ctrl+C to stop)"]
                          + odds_view.odds_rows(color=True))
    head = "fight in progress" if o.current else "last fight"
    lines = [head + "   (Ctrl+C to stop)"]
    lines += odds_view.odds_rows(o.win, o.tie, o.loss, odds_view._pct(o.my_lethal),
                                 odds_view._pct(o.opp_lethal), color=True)
    damage = odds_view.damage_line(o.avg_deal, o.avg_take)
    if damage:
        lines.append(damage)
    note = odds_view.note_line(o.unmodeled, o.total)
    if note:
        lines.append(note)
    return "\n".join(lines)


def _configure(p) -> None:
    p.add_argument("--log", help="path to Power.log (default: newest one found)")
    p.add_argument("--replay", help="show the last fight of a saved Power.log, then exit")
    p.add_argument("--cards-file", help="read a local cards.json instead of the downloaded one")
    p.add_argument("--debug", action="store_true",
                   help="also write data/combat_odds_log.txt (one line each time a fight's odds change)")
    p.add_argument("--logs-dir", default=default_logs_dir(), help="Hearthstone Logs folder")


@command("simpreview", "only the fight odds from your real game", _configure)
def cmd_simpreview(args) -> None:
    cards = HearthstoneJsonCards(paths.cards_cache_file(), args.cards_file)
    try:
        cards.minions()
    except Exception as e:
        sys.exit(f"Could not load card data: {e}")
    path = args.replay or args.log or newest_log(args.logs_dir)
    if not path:
        sys.exit("Couldn't find Power.log. Use --log PATH or --logs-dir PATH.")
    if args.replay:
        log = ReplayLog(path)
    elif args.log:
        log = LogTail(path)
    else:
        log = LogTail(path, follow_dir=args.logs_dir)
    live_tracker.run(cards, _NoTargets(), _NoHistory(), log, debug=args.debug,
                     follow=not args.replay, render=render_odds)
