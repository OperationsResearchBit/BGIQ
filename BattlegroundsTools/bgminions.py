#!/usr/bin/env python3
"""
bgminions.py - browse Hearthstone Battlegrounds minions in your terminal.

Data comes from HearthstoneJSON (https://hearthstonejson.com) and is cached
locally after the first download. No third-party packages needed.

Examples:
    python bgminions.py                    # all minions, grouped by tavern tier
    python bgminions.py -t 3               # only tier 3
    python bgminions.py -r beast           # only beasts
    python bgminions.py -s "deathrattle"   # search name/text
    python bgminions.py -t 4 -r mech -s    # (see --help)
    python bgminions.py --refresh          # re-download card data
    python bgminions.py --file cards.json  # use a local JSON file
"""

import argparse
import html
import json
import re
import shlex
import sys
import urllib.request
from collections import Counter
from pathlib import Path

import bgui

URL = "https://api.hearthstonejson.com/v1/latest/enUS/cards.json"
CACHE = Path.home() / ".cache" / "bgminions" / "cards.json"



def load_cards(file=None, refresh=False):
    if file:
        return json.loads(Path(file).read_text(encoding="utf-8"))
    if refresh or not CACHE.exists():
        print("Downloading card data...", file=sys.stderr)
        req = urllib.request.Request(URL, headers={"User-Agent": "bgminions/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_bytes(data)
    return json.loads(CACHE.read_text(encoding="utf-8"))


def clean_text(text):
    """Strip HTML tags and HearthstoneJSON placeholders from card text."""
    if not text:
        return ""
    text = text.replace("\n", " ").replace("[x]", "")
    text = re.sub(r"</?[^>]+>", "", text)          # <b>, <i>, ...
    text = re.sub(r"[$#](\d+)", r"\1", text)       # $3 / #3 -> 3
    text = text.replace("_", " ")
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def parse_minions(cards):
    """Return normal (non-golden) Battlegrounds minions as simple dicts."""
    minions = []
    for c in cards:
        if c.get("type") != "MINION" or "techLevel" not in c:
            continue
        # Golden versions point back to their normal card; skip them.
        if "battlegroundsNormalDbfId" in c:
            continue
        # Real BG minions have a golden counterpart.
        if "battlegroundsPremiumDbfId" not in c:
            continue
        # Skip internal placeholder cards such as "[BGTEMPLATE] VFX Dummy".
        if c.get("name", "").startswith("["):
            continue
        races = c.get("races") or ([c["race"]] if c.get("race") else [])
        minions.append({
            "id": c.get("id", ""),
            "name": c.get("name", "?"),
            "tier": c["techLevel"],
            "attack": c.get("attack", 0),
            "health": c.get("health", 0),
            "races": [r.title().replace("_", " ") for r in races] or ["Neutral"],
            "text": clean_text(c.get("text")),
        })
    minions.sort(key=lambda m: (m["tier"], m["name"]))
    return minions


def filter_minions(minions, tier, race, search):
    out = minions
    if tier:
        out = [m for m in out if m["tier"] == tier]
    if race:
        r = race.lower().replace("_", " ")
        out = [m for m in out if any(r in x.lower() for x in m["races"])]
    if search:
        s = search.lower()
        out = [m for m in out if s in m["name"].lower() or s in m["text"].lower()]
    return out


def print_minions(minions, use_color):
    bgui.set_enabled(use_color)
    if not minions:
        print("No minions matched.")
        return
    counts = Counter(m["tier"] for m in minions)
    current = None
    for m in minions:
        if m["tier"] != current:
            current = m["tier"]
            print()
            print(bgui.header(f"TAVERN TIER {current}", counts[current],
                              bgui.TIER_FG.get(current, "1;37")))
        for line in bgui.minion_lines(m["name"], m["attack"], m["health"],
                                      m["tier"], m["races"], m["text"]):
            print(line)
    print("\n" + bgui.c(f"{len(minions)} minion(s).", "90"))


def interactive(minions, use_color):
    """Keep running and answer queries until the user quits."""
    q = argparse.ArgumentParser(prog="", add_help=False)
    q.add_argument("-t", "--tier", type=int, choices=range(1, 7))
    q.add_argument("-r", "--race")
    q.add_argument("-s", "--search")

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


def main():
    p = argparse.ArgumentParser(description="Browse Hearthstone Battlegrounds minions.")
    p.add_argument("-t", "--tier", type=int, choices=range(1, 7), help="tavern tier (1-6)")
    p.add_argument("-r", "--race", help="minion type, e.g. beast, mech, murloc")
    p.add_argument("-s", "--search", help="text to search in name or card text")
    p.add_argument("-x", "--no-timewarped", action="store_true",
                   help="hide Timewarped minion variants")
    p.add_argument("-i", "--interactive", action="store_true",
                   help="stay open and keep answering queries")
    p.add_argument("--file", help="read a local cards.json instead of downloading")
    p.add_argument("--refresh", action="store_true", help="re-download card data")
    p.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    args = p.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    try:
        cards = load_cards(args.file, args.refresh)
    except Exception as e:
        sys.exit(f"Could not load card data: {e}")

    minions = parse_minions(cards)
    if args.no_timewarped:
        minions = [m for m in minions if not m["name"].startswith("Timewarped ")]
    use_color = sys.stdout.isatty() and not args.no_color
    if args.interactive:
        interactive(minions, use_color)
        return
    minions = filter_minions(minions, args.tier, args.race, args.search)
    print_minions(minions, use_color=sys.stdout.isatty() and not args.no_color)


if __name__ == "__main__":
    main()
