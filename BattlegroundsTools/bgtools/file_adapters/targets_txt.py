# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""triple_targets.txt: one 'Card name | short reason' per line."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

HEADER = [
    "# Triple targets: minions worth tripling. One per line, as:  Card name | short reason",
    "# Lines starting with # are ignored. Matching ignores upper/lower case.",
    "# The tracker marks a tavern minion with a star when its name is listed here.",
    "# Tip: run run_bgtools.bat and pick \"My triple targets\" to add cards by search.",
]


class TextTargetsStore:
    def __init__(self, path: Path):
        self._path = Path(path)
        self._mtime: Optional[float] = None
        self._data: Dict[str, Tuple[str, str]] = {}

    def load(self) -> Dict[str, Tuple[str, str]]:
        """lowercase name -> (name, reason). Re-read only when the file changes."""
        try:
            mtime = self._path.stat().st_mtime
        except OSError:
            return {}
        if self._mtime != mtime:
            data = {}
            try:
                for raw in self._path.read_text(encoding="utf-8").splitlines():
                    raw = raw.strip()
                    if not raw or raw.startswith("#"):
                        continue
                    name, _, why = raw.partition("|")
                    data[name.strip().lower()] = (name.strip(), why.strip())
            except OSError:
                data = {}
            self._mtime, self._data = mtime, data
        return self._data

    def read_entries(self) -> Tuple[List[str], List[Tuple[str, str]]]:
        header, entries = [], []
        if self._path.exists():
            for raw in self._path.read_text(encoding="utf-8").splitlines():
                s = raw.strip()
                if s.startswith("#") or not s:
                    if not entries and s:
                        header.append(raw)
                    continue
                name, _, why = s.partition("|")
                entries.append((name.strip(), why.strip()))
        return (header or list(HEADER)), entries

    def write_entries(self, header: List[str], entries: List[Tuple[str, str]]) -> None:
        lines = list(header) + [f"{n} | {w}" if w else n for n, w in entries]
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text("\n".join(lines) + "\n", encoding="utf-8")
