# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Replays the made-up game through the log parser, the tracker data and the screen."""

import os
import tempfile
import unittest

import fake_game

from bgtools.core.game_state import State
from bgtools.file_adapters.cards_hsjson import parse_cards
from bgtools.file_adapters.log_replay import ReplayLog
from bgtools.file_adapters.stores_json import JsonHistoryStore
from bgtools.modes.game_review import record_finished
from bgtools.modes.live_tracker import build_snapshot
from bgtools.ui import bgui
from bgtools.ui.layout import render_screen

CARDS = {c.id: c for c in parse_cards(fake_game.RAW_CARDS)}
TARGETS = {"pack leader": ("Pack Leader", "scales when golden")}
TIERS = {"pack leader": 3}


def replay(lines):
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8") as f:
        f.writelines(line + "\n" for line in lines)
    try:
        state = State(CARDS)
        state.path = f.name
        for line in ReplayLog(f.name).lines():
            state.feed(line)
        return state
    finally:
        os.unlink(f.name)


class GameReplay(unittest.TestCase):
    def setUp(self):
        bgui.set_enabled(False)

    def test_status_board_and_tavern_are_read(self):
        state = replay(fake_game.game_lines())
        snap = build_snapshot(state, TARGETS, TIERS, [])
        self.assertEqual((snap.status.turn, snap.status.tier), (2, 3))
        self.assertEqual((snap.status.gold_now, snap.status.gold_max), (6, 9))
        self.assertEqual([m.name for m in snap.board], ["Mama Bear", "Alley Cat", "Pack Leader"])
        self.assertEqual([m.name for m in snap.tavern], ["Pack Leader", "Wrath Weaver", "Amalgam"])
        self.assertEqual(snap.profile.label, "Beast build")
        self.assertEqual(snap.strength.total, 20)  # the ATK/HEALTH tags override card stats
        self.assertEqual(snap.marks[0].kind, "triple")
        self.assertEqual(snap.marks[2].kind, "fit")
        self.assertIsNone(snap.match)

    def test_finished_game_is_recorded_once(self):
        state = replay(fake_game.finished_game_lines(placement=2))
        self.assertEqual(state.complete.placement, 2)
        with tempfile.TemporaryDirectory() as d:
            store = JsonHistoryStore(os.path.join(d, "history.json"))
            history = store.load()
            record_finished(state, history, store)
            self.assertEqual(len(store.load()), 1)
            state.finished.append(state.complete)  # same game seen again
            record_finished(state, history, store)
            self.assertEqual(len(store.load()), 1)

    def test_screen_fits_the_window_at_every_size(self):
        snap = build_snapshot(replay(fake_game.finished_game_lines()), TARGETS, TIERS, [], True)
        for rows in (40, 20, 14, 10):
            text = render_screen(snap, show_text=True, rows=rows)
            self.assertLessEqual(len(text.split("\n")), max(rows - 1, 8))

    def test_unknown_cards_do_not_break_the_screen(self):
        snap = build_snapshot(replay(fake_game.game_lines()), {}, {}, [])
        self.assertIn("Pack Leader", render_screen(snap, rows=40))


if __name__ == "__main__":
    unittest.main()
