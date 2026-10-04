# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Finished games: save them once, and compare each with your earlier ones."""

from datetime import datetime
from typing import List, Optional

from bgtools.analysis.stats import compare_to_history
from bgtools.core.domain import HISTORY_KEEP, MatchPanel
from bgtools.core.game_state import State
from bgtools.core.ports import HistoryStore


def record_finished(state: State, history: List[dict], store: HistoryStore) -> None:
    """Save games the state has seen finish (skips ones already saved)."""
    keys = {h.get("key") for h in history}
    for rec in state.finished:
        if rec.key not in keys:
            row = rec.to_dict()
            row["saved"] = datetime.now().isoformat(timespec="seconds")
            history.append(row)
            keys.add(rec.key)
    state.finished.clear()
    del history[:-HISTORY_KEEP]
    store.save(history)


def build_match_panel(state: State, history: List[dict]) -> Optional[MatchPanel]:
    """The data behind the MATCH COMPLETE panel, or None while a game is running."""
    rec = state.complete
    if rec is None:
        return None
    return MatchPanel(record=rec, comparison=compare_to_history(rec, history))
