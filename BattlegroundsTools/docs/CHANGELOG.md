# Changelog

All notable changes to Battlegrounds Tools (v2). The baseline is the original `bgtools` folder, which v2 was copied from.

## Unreleased

Developer changes only. The screens and results are the same as v2.1.0 (checked with the golden-screen tests against the old code).

### Added

- Rule registry: advice rules are functions marked `@rule`; `pick_marks` runs them in order. Files named `rule_*.py` in `analysis\recommender\` are imported automatically.
- Command registry (`bgtools\commands\`): commands register with `@command`, and the parser is built from them. Files named `cmd_*.py` are imported automatically, and `menu="Label"` adds a numbered menu item.
- `docs\MAP.md`, a generated map of the code for AI assistants, made by `build_and_test\tools\make_map.py` and checked by a test.
- Golden-screen tests (`build_and_test\tests\golden\`) and registry tests.
- `.gitignore` and `.gitattributes`.
- The lab (`build_and_test\lab\`): create, check and promote new ideas with `lab.bat`. Includes a worked example, `pairs`.

### Changed

- Docs now say the log parsing was checked against real games. The automated tests still use a made-up log, because real logs contain battletags and are not committed.
- The lab now rejects a copy of an app file (its tests would have run the app's version instead) and finds `rule_*.py` and `cmd_*.py` files in an idea.
- `build_exe.bat` collects the `commands` and `recommender` folders so automatically imported files are included in the `.exe`.
- `CLAUDE.md` now lives at the repo root (it pointed to a missing `dev\` folder) and describes how to add features.
- `build_exe.bat` creates a starter `triple_targets.txt` when `data\` has none.

### Ideas for later (not built)

- **`Snapshot.extras`, for when there is an art-heavy UI.** Today every screen piece is drawn by the terminal, and a piece that needs derived data may call `analysis` directly (the plan is to let `ui` import `analysis`). If a second, graphical UI is built, derived data should move out of the UI: `Snapshot` gets `extras: Dict[str, object]`, filled once in `modes\live_tracker.build_snapshot` by small functions in `analysis\` (one per key, for example `extras["pairs"]`), and every UI reads the same values. The terminal and the art UI then cannot disagree, the same reason the board type is computed once.
- **Keep the move cheap.** When a piece in `ui\components\` needs derived data, put that one analysis call in a single small helper at the top of its file. Moving it into an extras entry later is then a cut and paste, not a rewrite. Lab ideas that add a component follow the same habit, so the data they need accumulates in one findable place per piece.
- **Not decided:** whether extras stay a plain dictionary (easy to add to, typos not caught) or become typed fields. Decide when the second UI exists.

## v2.1.0 - 2026-10-03

Code reorganization. The screens, options and results are the same as v2.0.0; what you will notice is how you start the tools and where your own files live.

### Changed

- Docs now say the log parsing was checked against real games. The automated tests still use a made-up log, because real logs contain battletags and are not committed.
- The lab now rejects a copy of an app file (its tests would have run the app's version instead) and finds `rule_*.py` and `cmd_*.py` files in an idea.
- `build_exe.bat` collects the `commands` and `recommender` folders so automatically imported files are included in the `.exe`.
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

- Docs now say the log parsing was checked against real games. The automated tests still use a made-up log, because real logs contain battletags and are not committed.
- The lab now rejects a copy of an app file (its tests would have run the app's version instead) and finds `rule_*.py` and `cmd_*.py` files in an idea.
- `build_exe.bat` collects the `commands` and `recommender` folders so automatically imported files are included in the `.exe`.
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

These were first written against a made-up log. They have since been checked against real games and read correctly (confirmed by the maintainer, 2026-10-04). How each is worked out (`--debug` shows the raw values):

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
