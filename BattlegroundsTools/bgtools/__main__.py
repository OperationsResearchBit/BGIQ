# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Entry point: python -m bgtools  (and the one the .exe is built from).

This is the only place that connects the adapters (files, network) to the
modes that use them.
"""

import argparse
import os
import subprocess
import sys
from typing import List, Optional

from bgtools import __version__
from bgtools.core import paths
from bgtools.file_adapters.cards_hsjson import HearthstoneJsonCards
from bgtools.file_adapters.log_replay import ReplayLog
from bgtools.file_adapters.log_tail import LogTail, default_logs_dir, newest_log
from bgtools.file_adapters.stores_json import JsonHistoryStore
from bgtools.file_adapters.targets_txt import TextTargetsStore
from bgtools.menu import run_menu
from bgtools.modes import live_tracker, minion_browser, triple_targets
from bgtools.ui import bgui
from bgtools.ui.sandbox import demo


def _make_cards(file: Optional[str] = None) -> HearthstoneJsonCards:
    return HearthstoneJsonCards(paths.cards_cache_file(), file)


def _load_or_exit(cards: HearthstoneJsonCards):
    try:
        return cards.minions()
    except Exception as e:
        sys.exit(f"Could not load card data: {e}")


def _open_file(path) -> None:
    if not path.exists():
        print(f"Could not find {path}")
        return
    if os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(path)])


def cmd_track(args) -> None:
    bgui.set_enabled(not args.no_color)
    cards = _make_cards(args.cards_file)
    _load_or_exit(cards)
    path = args.replay or args.log or newest_log(args.logs_dir)
    if not path:
        sys.exit("Couldn't find Power.log. Use --log PATH or --logs-dir PATH.")
    if args.replay:
        log = ReplayLog(path)
    elif args.log:
        log = LogTail(path)
    else:
        log = LogTail(path, follow_dir=args.logs_dir)
    live_tracker.run(cards, TextTargetsStore(paths.targets_file()),
                     JsonHistoryStore(paths.history_file()), log,
                     show_text=args.text, debug=args.debug, follow=not args.replay)


def cmd_minions(args) -> None:
    cards = _make_cards(args.file)
    if args.refresh:
        cards.refresh()
    minions = _load_or_exit(cards)
    use_color = sys.stdout.isatty() and not args.no_color
    minion_browser.run(minions, args.tier, args.race, args.search,
                       hide_timewarped=args.no_timewarped,
                       interactive_mode=args.interactive, use_color=use_color)


def cmd_targets(_args=None) -> None:
    bgui.set_enabled(sys.stdout.isatty())
    minions = _load_or_exit(_make_cards())
    triple_targets.run(minions, TextTargetsStore(paths.targets_file()))


def cmd_demo(args) -> None:
    sys.exit(demo.run(args.piece))


def cmd_menu(_args=None) -> None:
    def tracker():
        args = build_parser().parse_args(["track"])
        cmd_track(args)

    def browse():
        cmd_minions(build_parser().parse_args(["minions", "-i"]))

    def tier():
        raw = input("Tier number (1-7): ").strip()
        if not raw:
            return
        if raw not in list("1234567"):
            print("Please enter a number from 1 to 7.")
            return
        cmd_minions(build_parser().parse_args(["minions", "-t", raw]))

    def refresh():
        _make_cards().refresh()
        print("\nCard data updated.")

    def edit_targets():
        store = TextTargetsStore(paths.targets_file())
        if not paths.targets_file().exists():
            header, entries = store.read_entries()
            store.write_entries(header, entries)
        if os.name == "nt":
            subprocess.Popen(["notepad", str(paths.targets_file())])
        else:
            _open_file(paths.targets_file())

    bgui.set_enabled(sys.stdout.isatty())
    run_menu({"tracker": tracker, "browse": browse, "tier": tier, "refresh": refresh,
              "targets": cmd_targets, "edit_targets": edit_targets,
              "readme": lambda: _open_file(paths.readme_file())})


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bgtools", description="Hearthstone Battlegrounds tools.")
    p.add_argument("--version", action="version", version=f"bgtools {__version__}")
    sub = p.add_subparsers(dest="command")

    sub.add_parser("menu", help="open the menu (default)")

    t = sub.add_parser("track", help="live tracker")
    t.add_argument("--log", help="path to Power.log (default: newest one found)")
    t.add_argument("--replay", help="draw the final screen of a saved Power.log, then exit")
    t.add_argument("--cards-file", help="read a local cards.json instead of the downloaded one")
    t.add_argument("--no-color", action="store_true", help="turn off colors")
    t.add_argument("--text", action="store_true", help="show card text under each minion")
    t.add_argument("--debug", action="store_true", help="show the debug footer")
    t.add_argument("--logs-dir", default=default_logs_dir(), help="Hearthstone Logs folder")

    m = sub.add_parser("minions", help="browse minions")
    m.add_argument("-t", "--tier", type=int, choices=range(1, 8), help="tavern tier (1-7)")
    m.add_argument("-r", "--race", help="minion type, e.g. beast, mech, murloc")
    m.add_argument("-s", "--search", help="text to search in name or card text")
    m.add_argument("-x", "--no-timewarped", action="store_true", help="hide Timewarped variants")
    m.add_argument("-i", "--interactive", action="store_true", help="keep answering queries")
    m.add_argument("--file", help="read a local cards.json instead of downloading")
    m.add_argument("--refresh", action="store_true", help="re-download card data")
    m.add_argument("--no-color", action="store_true", help="disable ANSI colors")

    sub.add_parser("targets", help="search minions and edit your triple targets")

    d = sub.add_parser("demo", help="draw a UI piece from made-up data")
    d.add_argument("piece", nargs="?", help="piece name (omit to draw the whole screen)")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = build_parser().parse_args(argv)
    handlers = {None: cmd_menu, "menu": cmd_menu, "track": cmd_track,
                "minions": cmd_minions, "targets": cmd_targets, "demo": cmd_demo}
    try:
        handlers[args.command](args)
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
