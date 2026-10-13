# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Type two boards, see win / tie / loss. Nothing from the rest of the app is used.

    python bgtools\\simcore\\preview.py --you "5/5 taunt, 3/2 shield" --opp "4/4, 2/2 venom"
    python bgtools\\simcore\\preview.py          (no options: it asks for the boards, blank line to quit)

Keywords: taunt, shield (ds), venom, reborn, windfury (wf), effect. Order is left to right.
"""
import argparse
import sys
from pathlib import Path

try:
    from .boards import parse_board
    from .combat_estimate import estimate
except ImportError:                       # run as a script: python bgtools\simcore\preview.py
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from simcore.boards import parse_board
    from simcore.combat_estimate import estimate


def show(you: str, opp: str, runs: int, seed: int) -> None:
    odds = estimate(parse_board(you), parse_board(opp), runs, seed)
    print(f"win {odds.win:.0%}   tie {odds.tie:.0%}   loss {odds.loss:.0%}")
    how = "exact" if odds.method == "exact" else f"estimate from {odds.runs} simulated fights"
    print(f"({how}; {odds.unmodeled} minion effect(s) not modeled)")


def ask(runs: int, seed: int) -> None:
    print("Boards are minions left to right: 5/5 taunt, 3/2 shield   (blank line to quit)")
    while True:
        you = input("Your board:  ").strip()
        if not you:
            return
        opp = input("Their board: ").strip()
        if not opp:
            return
        try:
            show(you, opp, runs, seed)
        except ValueError as e:
            print(f"  {e}")
        print()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="preview", description=__doc__.split("\n")[1])
    p.add_argument("--you", help='your board, e.g. "5/5 taunt, 3/2 shield"')
    p.add_argument("--opp", help="their board, same format")
    p.add_argument("--runs", type=int, default=2000, help="fights to simulate if it cannot calculate (2000)")
    p.add_argument("--seed", type=int, default=0, help="same seed gives the same answer")
    args = p.parse_args(argv)
    if args.you is None and args.opp is None:
        ask(args.runs, args.seed)
        return 0
    if not args.you or not args.opp:
        p.error("give both --you and --opp, or neither to be asked")
    try:
        show(args.you, args.opp, args.runs, args.seed)
    except ValueError as e:
        sys.exit(f"preview: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
