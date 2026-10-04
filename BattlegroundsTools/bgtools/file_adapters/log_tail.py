# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Reads Hearthstone's Power.log while the game is still writing it."""

from __future__ import annotations

import glob
import os
import sys
from typing import Iterator, Optional


def default_logs_dir() -> str:
    if os.name == "nt":
        return r"C:\Program Files (x86)\Hearthstone\Logs"
    if sys.platform == "darwin":
        return "/Applications/Hearthstone/Logs"
    return ""


def newest_log(logs_dir: str) -> Optional[str]:
    files = glob.glob(os.path.join(logs_dir, "*", "Power.log"))
    return max(files, key=os.path.getmtime) if files else None


class LogTail:
    """LogSource that follows a growing log file.

    Pass follow_dir to switch automatically to the newest game log; leave it
    None to stay on one file.
    """

    def __init__(self, path: str, follow_dir: Optional[str] = None):
        self.path = path
        self._follow_dir = follow_dir
        self._f = open(path, "rb")

    def lines(self) -> Iterator[str]:
        while True:
            pos = self._f.tell()
            line = self._f.readline()
            if not line:
                return
            if not line.endswith(b"\n"):
                self._f.seek(pos)  # half-written line, try again shortly
                return
            yield line.decode("utf-8", "replace")

    def switch_if_newer(self) -> bool:
        if not self._follow_dir:
            return False
        new = newest_log(self._follow_dir)
        if new and new != self.path:
            self._f.close()
            self.path = new
            self._f = open(new, "rb")
            return True
        return False

    def close(self) -> None:
        self._f.close()
