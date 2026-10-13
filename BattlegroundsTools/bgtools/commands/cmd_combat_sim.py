# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""python -m bgtools combatsim: estimate a fight between two boards you type in."""

import sys

from bgtools.commands.registry import command
from bgtools.simcore import CombatOdds, estimate, parse_board


def brief(odds: CombatOdds) -> str:
    """The single likeliest result, e.g. 'win 62%' (a draw in size prefers win, then tie)."""
    name, value = max((("win", odds.win), ("tie", odds.tie), ("loss", odds.loss)),
                      key=lambda kv: kv[1])
    return f"{name} {value:.0%}"


def _configure(p) -> None:
    p.add_argument("--you", help='your board, left to right, e.g. "5/5 taunt, 3/2 shield"')
    p.add_argument("--opp", help="their board, same format")
    p.add_argument("--runs", type=int, default=2000, help="fights to simulate (default 2000)")
    p.add_argument("--seed", type=int, default=0, help="same seed gives the same answer")
    p.add_argument("--brief", action="store_true", help="print only the likeliest result, e.g. 'win 62%%'")


@command("combatsim", "estimate a fight between two boards you type in", _configure)
def cmd_combatsim(args) -> None:
    if not args.you or not args.opp:
        print('Usage: combatsim --you "5/5 taunt, 3/2 shield" --opp "4/4, 2/2 venom"')
        print("Keywords: taunt, shield (ds), venom, reborn, windfury (wf), effect")
        return
    try:
        odds = estimate(parse_board(args.you), parse_board(args.opp), args.runs, args.seed)
    except ValueError as e:
        sys.exit(f"combatsim: {e}")
    if args.brief:
        print(brief(odds))
        return
    if odds.method == "exact":
        print("Exact odds (calculated, no sampling error):")
    else:
        print(f"Estimate from {odds.runs} simulated fights:")
    print(f"  win {odds.win:.0%}   tie {odds.tie:.0%}   loss {odds.loss:.0%}")
    print(f"  Card effects are not modeled ({odds.unmodeled} minion(s) here have one).")
