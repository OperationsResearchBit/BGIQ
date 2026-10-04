# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Where bgtools keeps its files."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def app_root() -> Path:
    """Repo root when run from source, the folder holding the .exe when frozen."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    """Your own files (triple targets, finished games). Override with BGTOOLS_DATA_DIR."""
    env = os.environ.get("BGTOOLS_DATA_DIR")
    return Path(env) if env else app_root() / "data"


def targets_file() -> Path:
    return data_dir() / "triple_targets.txt"


def history_file() -> Path:
    return data_dir() / "history.json"


def cards_cache_file() -> Path:
    return Path.home() / ".cache" / "bgminions" / "cards.json"


def readme_file() -> Path:
    return app_root() / "README.md"
