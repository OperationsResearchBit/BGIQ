# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""simpreview: type two boards, see win / tie / loss. Nothing from the rest of the app is used.

    simpreview.bat --you "5/5 taunt, 3/2 shield" --opp "4/4, 2/2 venom"
    simpreview.bat                      (no options: it asks for the boards, blank line to quit)

Keywords: taunt, shield (ds), venom, reborn, windfury (wf), effect. Order is left to right.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import List

try:
    from .combat_estimate import estimate
    from .combat_sim import Fighter
except ImportError:                       # run as a script: python simcore\preview.py
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from simcore.combat_estimate import estimate
    from simcore.combat_sim import Fighter

_FLAGS = {"taunt": "taunt", "shield": "shield", "ds": "shield", "venom": "venomous",
          "venomous": "venomous", "reborn": "reborn", "windfury": "windfury",
          "wf": "windfury", "effect": "has_effect"}


def parse_board(text: str) -> List[Fighter]:
    """'5/5 taunt, 3/2 shield venom' -> two Fighters. Raises ValueError on a bad minion."""
    out = []
    for part in text.split(","):
        words = part.split()
        if not words:
            continue
        stats = re.fullmatch(r"(\d+)/(\d+)", words[0])
        if not stats:
            raise ValueError(f"expected attack/health like 5/5, got '{words[0]}'")
        flags = {}
        for w in words[1:]:
            if w.lower() not in _FLAGS:
                raise ValueError(f"unknown keyword '{w}' (use: {', '.join(sorted(_FLAGS))})")
            flags[_FLAGS[w.lower()]] = True
        out.append(Fighter(int(stats.group(1)), int(stats.group(2)), **flags))
    return out


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
    p = argparse.ArgumentParser(prog="simpreview", description=__doc__.split("\n")[1])
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
        sys.exit(f"simpreview: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
