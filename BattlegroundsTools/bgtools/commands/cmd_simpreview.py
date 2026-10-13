# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""python -m bgtools simpreview: only the fight odds, read from your real game.

Follows Power.log like `track`, but draws two lines and touches none of your saved files:

    waiting for a fight...   (Ctrl+C to stop)
    my lethal 0%   win 0%   tie 0%   loss 0%   opp lethal 0%

Lethal (damage to a hero) is not calculated yet, so a real fight shows `--` for both lethal values.
"""

import sys

from bgtools.commands.registry import command
from bgtools.core import paths
from bgtools.core.domain import Snapshot
from bgtools.file_adapters.cards_hsjson import HearthstoneJsonCards
from bgtools.file_adapters.log_replay import ReplayLog
from bgtools.file_adapters.log_tail import LogTail, default_logs_dir, newest_log
from bgtools.modes import live_tracker


class _NoHistory:
    """Saves nothing: simpreview only looks, so it never writes your game history."""

    def load(self):
        return []

    def save(self, history) -> None:
        pass


class _NoTargets:
    def load(self):
        return {}


def _numbers(win="0%", tie="0%", loss="0%", mine="0%", theirs="0%") -> str:
    return f"my lethal {mine}   win {win}   tie {tie}   loss {loss}   opp lethal {theirs}"


def render_odds(snap: Snapshot, _show_text: bool = False, _rows: int = 0) -> str:
    """The whole screen: a status line, then the numbers."""
    o = snap.odds
    if o is None:
        return "waiting for a fight...   (Ctrl+C to stop)\n" + _numbers()
    head = "fight in progress" if o.current else "last fight"
    if o.unmodeled:
        head += f"   ({o.unmodeled} effects not modeled)"
    return head + "   (Ctrl+C to stop)\n" + _numbers(f"{o.win:.0%}", f"{o.tie:.0%}",
                                                     f"{o.loss:.0%}", "--", "--")


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
