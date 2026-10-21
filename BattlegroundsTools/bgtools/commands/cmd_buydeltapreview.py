# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""python -m bgtools buydeltapreview: try buy_delta on boards you type in. No game needed.

    buydeltapreview.bat                                          the example cases
    buydeltapreview.bat --you "3/3" --opp "4/4" --shop "2/2, 5/5"
    buydeltapreview.bat --you "3/3" --turn 5 --shop "2/2, 5/5"    against typical turn-5 boards
"""

import sys

from bgtools.adapter_buy_delta import preview
from bgtools.adapter_buy_delta.field import field_boards
from bgtools.commands.registry import command
from bgtools.core import paths
from bgtools.file_adapters.cards_hsjson import HearthstoneJsonCards

USAGE = ('\nYour own boards:  buydeltapreview.bat --you "3/3" --opp "4/4" --shop "2/2, 5/5"\n'
         'Typical boards:   buydeltapreview.bat --you "3/3" --turn 5 --shop "2/2, 5/5"')


def _configure(p) -> None:
    p.add_argument("--you", default="", help='your board, e.g. "3/3, 2/4 taunt" (default: empty)')
    p.add_argument("--opp", default=None, help="the opponent's board, same format")
    p.add_argument("--turn", type=int, default=None, help="use typical boards for this game turn instead of --opp")
    p.add_argument("--shop", default=None, help='tavern minions to price, e.g. "2/2, 5/5 taunt"')
    p.add_argument("--cards-file", help="read a local cards.json (only used with --turn)")


@command("buydeltapreview", "try buy_delta on boards you type in (no game needed)", _configure)
def cmd_buydeltapreview(args) -> None:
    if args.shop is None or (args.opp is None and args.turn is None):
        print(preview.examples())
        print(USAGE)
        return
    try:
        field = None
        if args.opp is None:
            cards = HearthstoneJsonCards(paths.cards_cache_file(), args.cards_file)
            try:
                field = field_boards(cards.minions(), args.turn)
            except Exception as e:
                sys.exit(f"Could not load card data: {e}")
            if not field:
                sys.exit(f"No typical boards for turn {args.turn}.")
        print(preview.show(args.you, args.opp, args.shop, field))
    except ValueError as e:
        sys.exit(f"Bad board: {e}")
