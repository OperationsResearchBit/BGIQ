# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Pick your favorite minions for triple_targets.txt.

Search or filter the minion list, then add what you like by number.
The live tracker reloads triple_targets.txt automatically, so changes show
up in a running game.

At the prompt:
    beast            search names and card text
    -t 3 -r mech     filter by tier / type (same as the minion browser)
    a 1 4 7          add results 1, 4 and 7 to your list
    a 2 | why        add result 2 with your own reason
    l                show your list
    r 3              remove item 3 of your list
    q                quit
"""

import shlex
from typing import Dict, List, Sequence, Tuple

from bgtools.analysis.minion_search import filter_minions
from bgtools.core.domain import Minion
from bgtools.core.ports import TargetsStore
from bgtools.modes.minion_browser import query_parser
from bgtools.ui import bgui


def show_list(entries: List[Tuple[str, str]], tiers: Dict[str, int]) -> None:
    if not entries:
        print("Your list is empty. Search for a minion and use:  a <number>")
        return
    print(bgui.header("MY TRIPLE TARGETS", len(entries)))
    for i, (n, w) in enumerate(entries, 1):
        t = tiers.get(n.lower())
        badge = bgui.tier_badge(t) if t else bgui.c(" ?? ", "90")
        extra = f"  {bgui.c(w, '90')}" if w else ""
        warn = "" if t else bgui.c("  (not a known minion)", "91")
        print(f"{i:>2}  {badge} {n}{extra}{warn}")


def run(minions: Sequence[Minion], store: TargetsStore) -> None:
    minions = [m for m in minions if not m.name.startswith("Timewarped ")]
    tiers = {m.name.lower(): m.tier for m in minions}
    q = query_parser()

    header, entries = store.read_entries()
    results: List[Minion] = []
    print(f"Loaded {len(minions)} minions. Your list has {len(entries)}.")
    print("Search a word or use -t 3 -r beast. Then:  a 1 4  (add)  l (list)  r 2 (remove)  q (quit)\n")
    while True:
        try:
            line = input("fav> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        cmd, _, rest = line.partition(" ")
        low = cmd.lower()
        if low in ("q", "quit", "exit"):
            break
        if low in ("l", "list"):
            show_list(entries, tiers)
            continue
        if low in ("a", "add", "r", "remove"):
            nums, _, why = rest.partition("|")
            try:
                picks = [int(x) for x in nums.replace(",", " ").split()]
            except ValueError:
                picks = []
            if not picks:
                print("Give numbers, e.g.  a 1 4   or   r 2")
                continue
            if low in ("a", "add"):
                have = {n.lower() for n, _ in entries}
                for p in picks:
                    if not 1 <= p <= len(results):
                        print(f"  {p}: not in the last results")
                        continue
                    name = results[p - 1].name
                    if name.lower() in have:
                        print(f"  {name}: already in your list")
                        continue
                    entries.append((name, why.strip()))
                    have.add(name.lower())
                    print(f"  added {name}")
            else:
                for p in sorted(set(picks), reverse=True):
                    if 1 <= p <= len(entries):
                        print(f"  removed {entries.pop(p - 1)[0]}")
                    else:
                        print(f"  {p}: not in your list")
            store.write_entries(header, entries)
            continue
        if not line.startswith("-"):
            line = "-s " + shlex.quote(line)
        try:
            a = q.parse_args(shlex.split(line))
        except (SystemExit, ValueError):
            print("Couldn't read that. Example: -t 3 -r beast")
            continue
        found = filter_minions(minions, a.tier, a.race, a.search)
        seen, results = set(), []
        for m in found:
            if m.name not in seen:
                seen.add(m.name)
                results.append(m)
        if not results:
            print("No minions matched.")
            continue
        listed = {n.lower() for n, _ in entries}
        for i, m in enumerate(results[:60], 1):
            mark = bgui.c("★ in list", "1;93") if m.name.lower() in listed else ""
            for ln in bgui.minion_lines(m.name, m.atk, m.hp, m.tier, list(m.races), m.text,
                                        num=i, mark=mark):
                print(ln)
        if len(results) > 60:
            print(f"...{len(results) - 60} more. Narrow your search.")
            results = results[:60]
        print()
