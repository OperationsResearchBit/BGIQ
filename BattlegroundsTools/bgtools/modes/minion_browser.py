# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Browse every Battlegrounds minion, grouped by tavern tier."""

import argparse
import shlex
from collections import Counter
from typing import Sequence

from bgtools.analysis.minion_search import filter_minions
from bgtools.core.domain import Minion
from bgtools.ui import bgui


def print_minions(minions: Sequence[Minion], use_color: bool) -> None:
    bgui.set_enabled(use_color)
    if not minions:
        print("No minions matched.")
        return
    counts = Counter(m.tier for m in minions)
    current = None
    for m in minions:
        if m.tier != current:
            current = m.tier
            print()
            print(bgui.header(f"TAVERN TIER {current}", counts[current],
                              bgui.TIER_FG.get(current, "1;37")))
        for line in bgui.minion_lines(m.name, m.atk, m.hp, m.tier, list(m.races), m.text):
            print(line)
    print("\n" + bgui.c(f"{len(minions)} minion(s).", "90"))


def query_parser() -> argparse.ArgumentParser:
    q = argparse.ArgumentParser(prog="", add_help=False)
    q.add_argument("-t", "--tier", type=int, choices=range(1, 8))
    q.add_argument("-r", "--race")
    q.add_argument("-s", "--search")
    return q


def interactive(minions: Sequence[Minion], use_color: bool) -> None:
    """Keep running and answer queries until the user quits."""
    q = query_parser()
    print(f"Loaded {len(minions)} minions.")
    print("Type filters like:  -t 3   |   -r beast   |   -t 4 -r mech -s taunt")
    print("Or just type a word to search name/text. 'q' to quit.\n")
    while True:
        try:
            line = input("bg> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in ("q", "quit", "exit"):
            break
        if not line:
            continue
        if not line.startswith("-"):
            line = "-s " + shlex.quote(line)
        try:
            a = q.parse_args(shlex.split(line))
        except (SystemExit, ValueError):
            print("Couldn't read that. Example: -t 3 -r beast")
            continue
        print_minions(filter_minions(minions, a.tier, a.race, a.search), use_color)
        print()


def run(minions: Sequence[Minion], tier=None, race=None, search=None,
        hide_timewarped=False, interactive_mode=False, use_color=True) -> None:
    if hide_timewarped:
        minions = [m for m in minions if not m.name.startswith("Timewarped ")]
    if interactive_mode:
        interactive(minions, use_color)
        return
    print_minions(filter_minions(minions, tier, race, search), use_color)
