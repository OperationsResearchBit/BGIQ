# Changelog

All notable changes to Battlegrounds Tools (v2). The baseline is the original `bgtools` folder, which v2 was copied from.

## v2.1.0 - 2026-10-03

Code reorganization. The screens, options and results are the same as v2.0.0; what you will notice is how you start the tools and where your own files live.

### Changed

- The code is now a Python package, `bgtools\`, split into layers: `core`, `analysis`, `file_adapters`, `modes` and `ui`. See `docs\ARCHITECTURE.md`.
- Start with `run_bgtools.bat` or `python -m bgtools`. The menu is now part of the program (`menu.py`), so Ctrl+C in the tracker returns to the menu without the "Terminate batch job" question.
- The old scripts map to commands: `bgtrack.py` is `python -m bgtools track`, `bgminions.py` is `python -m bgtools minions`, `bgfavs.py` is `python -m bgtools targets`.
- Your files moved to `data\` (`triple_targets.txt`, `history.json`). Copy your existing ones there.
- `bgui.py` now also holds the named style tokens and the less-used screen elements (tracker title, hints, terminal control codes), so no other file hard-codes colors.
- Board type is computed once (`board_type.py`) and read by both the on-screen label and the tavern marks.
- Tests, sample data, `build_exe.bat` and build output moved into `build_and_test\`.
- `README.md` is at the repo root; `LICENSE`, `CHANGELOG.md` and `ARCHITECTURE.md` are in `docs\`.

### Added

- `python -m bgtools demo`: draws the tracker screen, or one UI piece, from made-up data.
- `python -m bgtools track --replay PATH`: draw the final screen of a saved `Power.log`, then exit.
- Tests, including one that checks the dependency rule between layers.
- `pyproject.toml`, a GitHub Actions test workflow, and AGPL-3.0 license lines in each source file.

### Checked

- The new code was compared against the v2.0.0 scripts on a made-up game (120 combinations of window height, `--text`, `--debug` and saved history): the screens and saved game records were identical, and the minion browser output matched. This is not the same as a check against a real game; the "Known limits" below still apply.

## v2.0.0 - 2026-10-03

### Added

- **Status line** in the live tracker: turn, tavern tier and gold.
- **Board type line**: counts of each minion type on your board plus a label (`Beast build`, `Leaning <type>`, `Mixed types`, `No clear type yet`, `No board yet`). Minions that count as every type are shown as `All`.
- **Board strength**: total attack + total health in the YOUR BOARD header (raw stats only, no keyword scoring).
- **Tavern marks**: at most two tavern minions are marked, each with a short reason.
  - `✓ fits <type>` for a minion matching your board's main type.
  - `★ triple target` for a minion listed in `triple_targets.txt`. Triple-target marks take priority.
- **`triple_targets.txt`**: your own list of minions worth tripling (`Card name | reason`). Reloaded automatically when it changes. Ships empty.
- **Triple targets line** under the board line: the cards from that list that are in your current tavern tier.
- **MATCH COMPLETE panel** when a game ends: final board strength, placement, and a comparison with the average of your last 3 to 10 games. The comparison starts after 3 earlier games are saved.
- **`history.json`**: finished games are saved here, with duplicate protection when a log is read again.
- **`--text` option**: show card text under each minion.
- **`--debug` option**: show the debug footer, now including the raw turn, tier and gold tags and the saved-game count.
- **`CHANGELOG.md`**.

### Changed

- The live tracker shows one line per minion by default. Card text is hidden unless `--text` is used.
- The debug footer is hidden unless `--debug` is used.
- `bgui.py`: `minion_lines` takes optional `mark` and `show_text` arguments, and `header` takes an optional `note`. `bgminions.py` output is unchanged.
- The tracker also reads the game entity and your player entity from the log (needed for the status line and game completion). Existing shop, board and hand detection is unchanged.
- `run_bgtools.bat` now starts from the `bgtools_v2` folder.
- `README.md` rewritten for v2: new folder layout, screen guide, `triple_targets.txt`, match summary, options, known limits and troubleshooting.

### Fixed

- Repeating banner and scrolling screen: the tracker now picks the fullest layout that fits the window height, turns off line wrapping while it runs, and redraws cleanly when the window is resized.
- README said golden minions are marked "Golden"; the tracker shows `GOLD`.

### Known limits

These were written against the log format as understood and tested only on a made-up log. They need checking against a real game (use `--debug`):

- The turn number is the game's turn counter divided by two, rounded up.
- Final placement is read from your hero's leaderboard tag. If it is not there, the panel shows `Placement: ?`.
- Game end is detected from the game's `COMPLETE` state.
- "Final board" is the last non-empty board seen before the game ended, sampled at turn changes.
- Buffs may not all appear in the attack and health tags, so board totals can be low.
- `triple_targets.txt` is empty. No automatic check of whether a minion is worth tripling exists yet.

### Not yet built

- Review screen ranking your strongest boards across games.
- Economy review (unspent gold, rolls, leveling turns).
- Opponent board comparison.
- Shop scoring from `solver.py`.
- Automatic card-data update check.
