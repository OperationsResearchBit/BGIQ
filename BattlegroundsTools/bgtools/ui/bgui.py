# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""bgui.py - low-level terminal styling (colors, banner, header, badges, wrapping).

Also holds the named style tokens and the less-used screen elements (tracker
title, hints, cursor control) so components never hard-code colors or strings.
Stdlib only; knows nothing about game logic.
"""

import os
import re
import shutil
import textwrap

ENABLED = True

if os.name == "nt":
    os.system("")  # switches on ANSI escape codes in the Windows console

# (text color, background color) per tavern tier
TIER_BADGE = {
    1: ("30", "47"), 2: ("30", "42"), 3: ("30", "46"), 4: ("97", "44"),
    5: ("97", "45"), 6: ("30", "43"), 7: ("97", "41"),
}
TIER_FG = {1: "1;37", 2: "1;32", 3: "1;36", 4: "1;94", 5: "1;35", 6: "1;33", 7: "1;31"}

RACE_FG = {
    "Beast": "33", "Mechanical": "36", "Murloc": "96", "Demon": "35",
    "Dragon": "31", "Elemental": "94", "Pirate": "93", "Undead": "37",
    "Naga": "92", "Quilboar": "91", "Aberration": "95", "Neutral": "90",
    "All": "1;97",
}

KEYWORDS = [
    "Mega-Windfury", "Windfury", "Divine Shield", "Taunt", "Reborn", "Venomous",
    "Poisonous", "Stealth", "Magnetic", "Immune", "Deathrattle", "Battlecry",
    "Rally", "Avenge", "Start of Combat", "Spellcraft", "Activate", "Overkill",
    "Choose One",
]
_KW = "|".join(re.escape(k) for k in sorted(KEYWORDS, key=len, reverse=True))
_BOOST = r"\+\d+/\+\d+|\+\d+(?: Attack| Health)?"
HIGHLIGHT = re.compile(rf"((?:{_KW})|(?:{_BOOST}))")


def set_enabled(on):
    global ENABLED
    ENABLED = bool(on) and "NO_COLOR" not in os.environ


def c(text, *codes):
    """Wrap text in ANSI color codes (no-op when colors are off)."""
    if not ENABLED or not codes:
        return str(text)
    return f"\033[{';'.join(codes)}m{text}\033[0m"


def term_width():
    return min(max(shutil.get_terminal_size((100, 24)).columns, 60), 110)


def banner(text, color="1;93"):
    inner = f"  {text}  "
    return "\n".join([
        c("╔" + "═" * len(inner) + "╗", color),
        c("║", color) + c(inner, "1;97") + c("║", color),
        c("╚" + "═" * len(inner) + "╝", color),
    ])


def header(title, count=None, color="1;93", note=""):
    label = (f" {title}" + (f"  ({count})" if count is not None else "")
             + (f"  {note}" if note else "") + " ")
    return c("══" + label + "═" * max(2, term_width() - len(label) - 2), color)


def tier_badge(tier):
    fg, bg = TIER_BADGE.get(tier, ("97", "100"))
    return c(f" T{tier} ", fg, bg)


def highlight(line):
    parts = HIGHLIGHT.split(line)
    out = []
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2 == 1:
            out.append(c(part, "92") if part.startswith("+") else c(part, "1;96"))
        else:
            out.append(c(part, "37"))
    return "".join(out)


def minion_lines(name, atk, hp, tier, races, text="", golden=False, num=None,
                 mark="", show_text=True):
    """Return the printable lines for one minion."""
    prefix = f"{num:>2}  " if num is not None else ""
    gold = c("GOLD ", "1;93") if golden else ""
    nm = c(name, "1;93" if golden else "1;97")
    name_pad = " " * max(2, 32 - (len(name) + (5 if golden else 0)))
    stat_txt = f"{atk}/{hp}"
    stats = c(str(atk), "1;93") + c("/", "90") + c(str(hp), "1;91")
    stat_pad = " " * max(2, 9 - len(stat_txt))
    rc = c("/", "90").join(c(r, RACE_FG.get(r, "37")) for r in (races or ["Neutral"]))
    mk = ("  " + mark) if mark else ""
    lines = [f"{prefix}{tier_badge(tier)} {gold}{nm}{name_pad}{stats}{stat_pad}{rc}{mk}"]
    if text and show_text:
        indent = " " * (len(prefix) + 5)
        for part in textwrap.wrap(text, max(30, term_width() - len(indent))):
            lines.append(indent + highlight(part))
    return lines


# --- Named style tokens (ANSI codes) -----------------------------------------
# Components use these names instead of raw codes, so the look changes in one place.
STYLE = {
    "title": "1;93",       # small tracker title when the banner is dropped
    "status": "1;97",      # turn / tavern / gold line
    "board_line": "1;96",  # board type line
    "triple_label": "1;93",
    "dim": "90",           # hints, empty sections, debug footer
    "error": "91",         # unknown card
    "match_header": "1;95",
    "match_main": "1;97",
    "match_compare": "96",
    "mark_triple": "1;93",
    "mark_fit": "92",
}

# Section header colors on the tracker screen.
SECTION_COLOR = {"TAVERN": "1;93", "YOUR BOARD": "1;92", "YOUR HAND": "1;96"}

# --- Less frequently used screen elements -----------------------------------
TRACKER_TITLE = "BATTLEGROUNDS TRACKER"
MATCH_TITLE = "MATCH COMPLETE"
QUIT_HINT = "Ctrl+C to quit"
TOO_SMALL_HINT = "... window too small, make it taller"
EMPTY_SECTION = "  (empty)"
TRIPLE_NONE_LISTED = "Triple targets: none listed (edit triple_targets.txt)"

# --- Terminal control (used by the live screen) -----------------------------
CLEAR_ALL = "\033[2J"
HOME = "\033[H"
WRAP_OFF = "\033[?7l"
WRAP_ON = "\033[?7h"
ERASE_LINE = "\033[K"
ERASE_BELOW = "\033[J"


def tracker_banner():
    """The boxed title shown at the top of the full tracker layout."""
    return banner(TRACKER_TITLE)


def frame(text):
    """Wrap a finished screen so redrawing it leaves no leftovers."""
    return HOME + text.replace("\n", ERASE_LINE + "\n") + ERASE_LINE + "\n" + ERASE_BELOW
