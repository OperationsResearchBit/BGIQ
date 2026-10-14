# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""python -m bgtools comps: lists comps.txt and flags card names the game does not know."""

import sys

from bgtools.commands.registry import command
from bgtools.core import paths
from bgtools.file_adapters.cards_hsjson import HearthstoneJsonCards
from bgtools.file_adapters.comps_txt import TextCompsStore


@command("comps", "check your comps.txt against the card data", None, menu="My comps")
def cmd_comps(args) -> None:
    store = TextCompsStore(paths.comps_file())
    if store.create_template():
        print(f"Created {paths.comps_file()}. Add one comp per line, then run this again.")
        return
    comps = store.load()
    if not comps:
        print(f"No comps in {paths.comps_file()} yet. Add lines like:\n"
              "  Comp name | Tribe | Core card, Core card | note")
        return
    try:
        tiers = HearthstoneJsonCards(paths.cards_cache_file()).tier_by_name()
    except Exception as e:
        sys.exit(f"Could not load card data: {e}")
    bad = 0
    for c in comps:
        print(f"{c.name}  ({c.tribe})")
        for card in c.core:
            tier = tiers.get(card.lower())
            if tier is None:
                bad += 1
            print(f"   {'T' + str(tier) if tier else '??'}  {card}")
    print(f"\n{len(comps)} comps." + (f" {bad} card names are not Battlegrounds minions "
                                      "and will never match." if bad else " All names found."))
