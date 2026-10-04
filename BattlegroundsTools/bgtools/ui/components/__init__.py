# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Stable UI pieces. Each is a function from a Snapshot to a list of lines.

REGISTRY lets the demo runner (and anything else) pick a piece by name.
New pieces start in ui/sandbox/ and move here when they are ready.
"""

from bgtools.ui.components.debug_footer import debug_footer
from bgtools.ui.components.match_panel import match_panel
from bgtools.ui.components.minion_list import section
from bgtools.ui.components.status import board_line, status_line, triple_line

REGISTRY = {
    "status_line": status_line,
    "board_line": board_line,
    "triple_line": triple_line,
    "match_panel": match_panel,
    "debug_footer": debug_footer,
}

__all__ = ["REGISTRY", "board_line", "debug_footer", "match_panel", "section",
           "status_line", "triple_line"]
