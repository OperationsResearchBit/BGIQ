# Changelog

All notable changes to Battlegrounds Tools (v2). The baseline is the original `bgtools` folder, which v2 was copied from.

## Unreleased

### Added: simpreview screen, v1

- **`simpreview` shows the odds in two rows.** The labels (`my lethal`, `win`, `tie`, `loss`, `opp lethal`) sit on top and each number is centered under its label. Win is green, tie yellow, loss red; a `0%` or `--` is dim grey, so only real chances light up. Lethal stays `--` until lethal chances are calculated.
- **Honest note under the numbers.** It counts minions, not effects, and says how far to trust the estimate: `2 of 13 minions have effects not modeled · medium confidence`. Nothing skipped means no note (high confidence); fewer than half the minions is medium; half or more is low. The tracker's Estimate line uses the same wording.
- **`simpreview.bat`** follows your newest `Power.log` live, as before. New: `simpreview.bat PATH\Power.log` (or dragging a log onto the file) shows the last fight of that log and waits, and any other `simpreview` option can be passed through.
- `Odds` has a new field `total` (minions on both boards). `Odds(*got)` still works.

### Needs a real-log check (simpreview v1)

- The screen was checked on made-up odds in a real terminal (colors and alignment). Watch a real fight with `simpreview.bat` and confirm the numbers and the note.
- Known, not part of v1: the estimate can still be made while the boards are half read, and a high loss percent is red like any other loss.

### Added: fight odds

- **Estimate line in the tracker.** During combat: `Estimate: win % tie % loss %`. Through the next shop phase: `Last fight: ...`. Card effects are not modeled and the screen says how many minions have one.
- **`python -m bgtools simpreview`** and `simpreview.bat`: only the odds, from your real game, as `my lethal / win / tie / loss / opp lethal`. Lethal (damage to a hero) is not calculated yet and shows `--`. It saves nothing of yours.
- **`python -m bgtools combatsim`**: win / tie / loss for two boards you type in.
- **`bgtools\simcore`**: the fight calculator (exact for small fights, simulated otherwise). Standard library only; `analysis` and `commands` may import it (see ARCHITECTURE).
- `--debug` also writes `data\combat_odds_log.txt` when a fight's steps, board sizes or estimate change.
- The status label is `loss` everywhere (it was `lose` in the first version of the estimate line).

### Needs a real-log check (fight odds)

- The estimate is made only at the log step `MAIN_START`. A replay of a finished game showed no combat, so this has not been confirmed on a real fight. Use `track --debug` or `simpreview --debug` in a game and read `data\combat_odds_log.txt`.

### Added: scouting (second batch)

- **Lobby line.** Shows which minion types are in this game, worked out from the shop minions you have seen. After five types it is certain and the rest are listed as `Out`; before that, types still unseen after 20 typed minions are shown as `Probably out`.
- **Hero line.** Your health (with armor) and place, and the hero you fight next with its health. It only appears when your health can be read.
- **Comps.** `data\comps.txt` holds the builds you want to play (`Comp name | Tribe | Core, Core, Core | note`). The tracker shows your two closest comps (core cards held, what is missing, what is in the tavern now) and marks missing core cards in the tavern with `core for <comp>`. `python -m bgtools comps` checks the card names against the game.
- Advice rules take a fifth argument, `needs`: `rule(minion, main, targets, pairs, needs)`.

### Needs a real-log check (second batch)

- Lobby: assumes shop minions stay in the log after a reroll and that a lobby has five types (`LOBBY_TYPES`).
- Hero line: reads the tags `HEALTH`, `DAMAGE`, `ARMOR`, `NEXT_OPPONENT_PLAYER_ID` and the opponent hero's `PLAYER_ID`. Run `track --debug` in a game and compare the `hero=` and `next_opp=` footer lines with the screen.

### Added (player-facing)

- **`python -m bgtools stats`** (also menu item "My stats"): average placement, top-4 / win / 7th-8th rates, recent form, a placement chart, results by the main type of your final board, and a short read-out. It warns about a cold streak (last 5 games well below your average).
- **Pair and triple alerts in the tracker.** A "Pairs (one more = golden)" line lists cards you hold two copies of (board and hand). A tavern minion that completes one is marked `completes a triple` and ranks above every other mark.
- **Tavern pace.** The status line now shows tier and gold as bars, and `(behind)`, `(on pace)` or `(ahead)` against a typical tier-by-turn range (`analysis\tempo.py`). It is a rough guide: greedy and tempo plays leave the range on purpose.
- Finished games now save the main type of the final board (`build` in `history.json`). Older games have no build and are left out of the by-build table.

### Changed

- Advice rules now take a fourth argument, `pairs`: `rule(minion, main, targets, pairs)`.
- The `pairs` lab idea was promoted to `analysis\pairs.py`.
- Golden screens were regenerated for the new status line and pairs line.

### Needs a real-log check

The new `build` value reads the types of your board in `core\game_state.py` (`sample_board`). It uses the same entities the board total already uses, but the tests only use the made-up log. Run `track --replay REAL_LOG --debug` once and play a game to confirm `history.json` gets a sensible `build`.

### Developer changes

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
- **Decided: typed fields, not a loose dictionary.** Each new value is a named field on `Snapshot` with a default (for example `pairs: Tuple[Tuple[str, int], ...] = ()`), so existing code and tests keep working and a typo is caught. The name `extras` above only describes the idea.
- **Archive instead of delete.** A component or lab idea that is built but not used moves to `build_and_test\\lab\\_archive\\<name>\\`, in the same folder shape as a lab idea, with an index line saying what it was and why it was shelved. It stays out of `bgtools\\`, so it is not shipped, not in `docs\\MAP.md` and not run by the app tests. A `restore` command would copy it back into the lab to be checked again.

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
