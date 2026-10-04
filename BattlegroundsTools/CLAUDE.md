# bgtools: notes for AI assistants (read this first)

Python 3.8+ stdlib-only terminal tools for Hearthstone Battlegrounds (v2.1). Windows first. Run with `python -m bgtools` from the repo root. Paths below are relative to the repo root.

## Rules for working cheaply

- Start with `docs/MAP.md` (generated; one line per module, public names only). Open only the file you are changing. Use search, not whole-file reads.
- Do NOT read `README.md`, `docs/CHANGELOG.md`, `docs/ARCHITECTURE.md` or `bgtools/ui/README.md` unless asked. They are for people. This file has what you need.
- Never paste or print a full `Power.log` (huge, contains battletags). Use `track --replay PATH --debug` and read only the footer.
- Keep answers and diffs small. Change one thing at a time.

## Starting a new idea? Use the lab

All new features start in `build_and_test/lab/`. Read `build_and_test/lab/CLAUDE.md` before you write anything; it has the work order and the current limits. Small fixes to existing files can be made in place.

## What to open, by task

| Task | Open | Also touches today |
|---|---|---|
| Advice rule | new file `analysis/recommender/rule_<name>.py` with `@rule` (see `rules.py`) | nothing: `rule_*.py` files are imported automatically, in name order, after `rules.py` |
| Board type / stats | `analysis/board_type.py`, `analysis/stats.py` | `Profile` in `core/domain.py` |
| New screen piece | `ui/components/`, start in `ui/sandbox/` | `Snapshot` in `core/domain.py`, `build_snapshot` in `modes/live_tracker.py`, `REGISTRY` in `ui/components/__init__.py`, `_build` in `ui/layout.py`, golden files |
| New command / mode | the mode in `bgtools/modes/`, plus new file `commands/cmd_<name>.py` with `@command(name, help, configure, menu="Label")` (see `commands/registry.py`) | nothing: `cmd_*.py` files are imported automatically; `menu=` adds a numbered menu item |
| What to work on next | `build_and_test/lab/BACKLOG.md` (only when asked) | |
| Log parsing | `core/game_state.py` (fed by `file_adapters/log_tail.py`) | see "Log parsing" |
| Card data | `file_adapters/cards_hsjson.py` | |
| Saved data | `file_adapters/stores_json.py`, `targets_txt.py` | contracts in `core/ports.py` |

## Architecture rule (enforced by `build_and_test/tests/test_architecture.py`)

Imports point inward only. `core` imports only the standard library.

| Folder | May import |
|---|---|
| `core` | stdlib only |
| `analysis`, `file_adapters`, `ui` | `core` |
| `modes` | `core`, `analysis`, `ui` |
| `commands` | `core`, `analysis`, `file_adapters`, `ui`, `modes` |
| `__main__.py`, `menu.py` | everything |

Adapters are connected to modes only in `__main__.py` and `commands/`.

## Conventions

- Analysis code is pure functions: data in, plain data out (for example `Mark`). The UI decides colors.
- Board type is computed once (`build_profile`) and read by both the on-screen label and the tavern marks. Do not recompute it elsewhere.
- Name the domain module `domain.py`, never `types.py`.
- Every new `.py` file starts with the two license lines (AGPL-3.0) used by existing files.
- Update `docs/CHANGELOG.md` for any user-visible change.

## Log parsing: verified by hand, tested on a made-up log

Turn number (counter / 2), gold, placement and game-end detection were checked against real games by the maintainer and work. The automated tests only use `fake_game.py`, so they cannot catch a parsing regression on real logs. After any change to `core/game_state.py`, ask the maintainer to run `track --replay REAL_LOG --debug`. Never paste or commit a real log.

## Before saying a change is done

1. `python -m unittest discover -s build_and_test/tests`. If a golden-screen test fails, read the diff. If the change is intended, regenerate with `UPDATE_GOLDEN=1` (see `test_golden_screens.py`) and review the changed `golden/*.txt`. Never regenerate just to make a test pass.
2. If you touched parsing or the screen, run `python -m bgtools demo` and a replay of a sample log.
3. Confirm nothing in `core` imports from another layer (the test does this).
4. If a public function or class changed, run `python build_and_test/tools/make_map.py` (a test fails when `docs/MAP.md` is stale).
