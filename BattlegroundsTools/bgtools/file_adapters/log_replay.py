# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Reads a finished Power.log from the top, once. Used for tests and for --replay."""

from __future__ import annotations

from typing import Iterator


class ReplayLog:
    """LogSource over a saved log file. Never switches logs."""

    def __init__(self, path: str):
        self.path = path
        self._done = False

    def lines(self) -> Iterator[str]:
        if self._done:
            return
        self._done = True
        with open(self.path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                yield line

    def switch_if_newer(self) -> bool:
        return False
