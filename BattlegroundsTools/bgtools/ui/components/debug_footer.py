# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The --debug footer: raw values behind the screen."""

from typing import List

from bgtools.core.domain import Snapshot
from bgtools.ui import bgui


def debug_footer(snap: Snapshot) -> List[str]:
    return [bgui.c(line, bgui.STYLE["dim"]) for line in snap.debug]
