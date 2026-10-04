# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Your finished games, saved as history.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


class JsonHistoryStore:
    def __init__(self, path: Path):
        self._path = Path(path)

    def load(self) -> List[dict]:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, ValueError):
            return []

    def save(self, history: List[dict]) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(history, indent=1), encoding="utf-8")
        except OSError:
            pass
