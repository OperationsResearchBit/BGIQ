# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""comps.txt: the builds you want to play, one per line.

    Comp name | Tribe | Core card, Core card, Core card | optional note
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from bgtools.core.domain import Comp

TEMPLATE = [
    "# Comps: builds you want to play. One per line, as:",
    "#   Comp name | Tribe | Core card, Core card, Core card | optional note",
    "# Lines starting with # are ignored. Card names must match the game's names",
    "# (run  python -m bgtools comps  to check them). Update this after every patch.",
    "# Example (replace with comps from the current patch):",
    "# Beast tempo | Beast | Card A, Card B, Card C | keep two beasts for the buff",
]


def parse_line(raw: str) -> Optional[Comp]:
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        return None
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 3 or not parts[0]:
        return None
    core = tuple(c for c in (x.strip() for x in parts[2].split(",")) if c)
    if not core:
        return None
    return Comp(name=parts[0], tribe=parts[1], core=core, note=parts[3] if len(parts) > 3 else "")


class TextCompsStore:
    def __init__(self, path: Path):
        self._path = Path(path)
        self._mtime: Optional[float] = None
        self._data: List[Comp] = []

    def load(self) -> List[Comp]:
        """Re-read only when the file changes. A missing file means no comps."""
        try:
            mtime = self._path.stat().st_mtime
        except OSError:
            return []
        if self._mtime != mtime:
            try:
                lines = self._path.read_text(encoding="utf-8").splitlines()
            except OSError:
                lines = []
            self._data = [c for c in map(parse_line, lines) if c]
            self._mtime = mtime
        return self._data

    def create_template(self) -> bool:
        """Write a starter file if there is none. True when it created one."""
        if self._path.exists():
            return False
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text("\n".join(TEMPLATE) + "\n", encoding="utf-8")
        return True
