# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""python -m bgtools buydelta: only the tavern, with the buy_delta number next to each minion.

Follows Power.log like `track`, but draws just the TAVERN block and touches none of your saved files.
"""

import sys

from bgtools.commands.registry import command
from bgtools.core import paths
from bgtools.core.domain import Snapshot
from bgtools.file_adapters.cards_hsjson import HearthstoneJsonCards
from bgtools.file_adapters.log_replay import ReplayLog
from bgtools.file_adapters.log_tail import LogTail, default_logs_dir, newest_log
from bgtools.modes import live_tracker
from bgtools.ui import bgui, buy_delta_view
from bgtools.ui.components import section


class _NoHistory:
    """Saves nothing: this screen only looks, so it never writes your game history."""

    def load(self):
        return []

    def save(self, history) -> None:
        pass


class _NoTargets:
    def load(self):
        return {}


def render_buydelta(snap: Snapshot, _show_text: bool = False, _rows: int = 0) -> str:
    """The whole screen: the TAVERN block and nothing else (plus the debug lines with --debug)."""
    lines = section("TAVERN", snap.tavern, bgui.SECTION_COLOR["TAVERN"], snap.marks, False,
                    note=buy_delta_view.label(snap.buy_note), deltas=snap.buy_deltas)
    return "\n".join(lines + list(snap.debug))


def _configure(p) -> None:
    p.add_argument("--log", help="path to Power.log (default: newest one found)")
    p.add_argument("--replay", help="show the last tavern of a saved Power.log, then exit")
    p.add_argument("--cards-file", help="read a local cards.json instead of the downloaded one")
    p.add_argument("--debug", action="store_true", help="also show the boards buy_delta is using")
    p.add_argument("--logs-dir", default=default_logs_dir(), help="Hearthstone Logs folder")


@command("buydelta", "only the tavern, with the win-chance change of buying each minion", _configure)
def cmd_buydelta(args) -> None:
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
                     follow=not args.replay, render=render_buydelta)
