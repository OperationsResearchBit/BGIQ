# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The stats screen: how your saved games went, and what stands out."""

from typing import List, Optional

from bgtools.analysis.performance import RECENT_MIN
from bgtools.core.domain import Performance
from bgtools.ui import bgui

ORDINAL = ("1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th")
SPARK = "█▇▆▅▄▃▂▁"   # placement 1 .. 8: taller is better
BAR_WIDTH = 28
BREAK_EVEN = 4.5     # the average placement of an even 8-player lobby
SMALL_SAMPLE = 20


def _place_color(p: int) -> str:
    return "1;92" if p <= 4 else "91"


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def _read_out(p: Performance) -> List[str]:
    notes = []
    gap = BREAK_EVEN - p.average
    if gap > 0.05:
        notes.append(f"Averaging {p.average:.2f}, {gap:.2f} better than the even-lobby "
                     f"{BREAK_EVEN}: that usually means your rating is going up.")
    elif gap < -0.05:
        notes.append(f"Averaging {p.average:.2f}, {-gap:.2f} worse than the even-lobby "
                     f"{BREAK_EVEN}: that usually means your rating is going down.")
    else:
        notes.append(f"Averaging {p.average:.2f}, right at the even-lobby {BREAK_EVEN}: "
                     "rating should be roughly flat.")
    if p.blowups >= 0.25:
        notes.append(f"{_pct(p.blowups)} of your games end 7th-8th. Those cost the most, "
                     "so review them first: what did you do on the turns before dying?")
    if p.cold_streak:
        notes.append("Cold streak: your last 5 games are well below your usual. "
                     "A break costs less than queueing on tilt.")
    if len(p.by_build) >= 2:
        best, worst = p.by_build[0], p.by_build[-1]
        notes.append(f"Best build: {best[0]} (avg {best[2]:.1f} over {best[1]} games). "
                     f"Worst: {worst[0]} (avg {worst[2]:.1f} over {worst[1]}).")
    if p.games < SMALL_SAMPLE:
        notes.append(f"Only {p.games} games saved, so treat all of this as rough.")
    return notes


def render_report(p: Optional[Performance]) -> str:
    st = bgui.STYLE
    out = [bgui.banner("YOUR PERFORMANCE"), ""]
    if p is None:
        out.append("No finished games saved yet. Play a game with the live tracker "
                   "running and its result shows up here.")
        return "\n".join(out)
    out.append(bgui.c(f"Games {p.games}  ·  Avg placement {p.average:.2f}  ·  "
                      f"Top 4 {_pct(p.top4)}  ·  Wins {_pct(p.wins)}  ·  "
                      f"7th-8th {_pct(p.blowups)}", st["status"]))
    if p.recent_average is not None:
        diff = p.average - p.recent_average
        arrow = ("▲ better than" if diff > 0.05 else "▼ worse than" if diff < -0.05
                 else "≈ same as")
        out.append(bgui.c(f"Recent form (last {p.recent_n}): {p.recent_average:.2f}  "
                          f"{arrow} your average", st["board_line"]))
    else:
        out.append(bgui.c(f"Recent form shows after {RECENT_MIN} games", st["dim"]))
    spark = "".join(bgui.c(SPARK[x - 1], _place_color(x)) for x in p.trend)
    out += [bgui.c("Trend  ", st["dim"]) + spark
            + bgui.c("   oldest → newest, taller is better", st["dim"]), ""]

    out.append(bgui.header("PLACEMENTS", None, "1;96"))
    top = max(p.distribution) or 1
    for i, n in enumerate(p.distribution):
        width = round(BAR_WIDTH * n / top)
        bar = bgui.c("█" * width, _place_color(i + 1)) + " " * (BAR_WIDTH - width)
        out.append(f" {ORDINAL[i]}  {bar}  {n:>3}  {_pct(n / p.games):>4}")
    if p.by_build:
        out += ["", bgui.header("BY BUILD", None, "1;92", "best first, 3+ games")]
        for name, n, avg in p.by_build:
            col = _place_color(round(avg))
            out.append(f" {name:<14}{n:>3} games   avg " + bgui.c(f"{avg:.2f}", col))
    out += ["", bgui.header("READ-OUT", None, "1;93")]
    out += [" • " + line for line in _read_out(p)]
    return "\n".join(out)
