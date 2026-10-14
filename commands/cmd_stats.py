# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""python -m bgtools stats: your saved games as a performance screen."""

from bgtools.analysis.performance import summarize
from bgtools.commands.registry import command
from bgtools.core import paths
from bgtools.file_adapters.stores_json import JsonHistoryStore
from bgtools.modes.performance_report import render_report


def _configure(p) -> None:
    p.add_argument("--no-color", action="store_true", help="turn off colors")


@command("stats", "your results: placements, form, builds", _configure, menu="My stats")
def cmd_stats(args) -> None:
    from bgtools.ui import bgui
    bgui.set_enabled(not getattr(args, "no_color", False))
    history = JsonHistoryStore(paths.history_file()).load()
    print(render_report(summarize(history)))
