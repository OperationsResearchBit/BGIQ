# bgtools: notes for AI assistants

Python 3.8+ stdlib-only terminal tools for Hearthstone Battlegrounds (v2.1). Windows first. Run with `python -m bgtools` from the repo root. All paths below are relative to the repo root.

## Read this before editing

- Do not read whole files. Open only the file you are changing, and use search to find it. See "Where things are".
- Never paste or print a full `Power.log`. It is huge and contains battletags. Use `track --replay PATH --debug` and read only the footer.
- Keep answers and diffs small. Change one thing at a time.

## Architecture rule (enforced by a test)

Imports point inward only. `core` imports only the standard library.

| Folder | May import |
|---|---|
| `core` | stdlib only |
| `analysis` | `core` |
| `file_adapters` | `core` |
| `ui` | `core` |
| `modes` | `core`, `analysis`, `ui` |
| `__main__.py`, `menu.py` | everything (the only place adapters are connected) |

Full detail: `docs/ARCHITECTURE.md`. Layering test: `build_and_test/tests/test_architecture.py`.

## Where things are

- Log lines to game state: `bgtools/core/game_state.py` (fed by `bgtools/file_adapters/log_tail.py`).
- Snapshot type and data types: `bgtools/core/domain.py`. Contracts: `bgtools/core/ports.py`.
- Board type (the Profile): `bgtools/analysis/board_type.py`. Advice rules: `bgtools/analysis/recommender/rules.py`.
- Card data (HearthstoneJSON): `bgtools/file_adapters/cards_hsjson.py`.
- Screen pieces: `bgtools/ui/components/`. New ones start in `bgtools/ui/sandbox/`. Layout fitting: `bgtools/ui/layout.py`.
- Modes (live tracker, review, minions, targets): `bgtools/modes/`.
- User data: `data/` (`history.json`, `triple_targets.txt`).
- Developer scripts and notes: `dev/` (this file lives here).

## Conventions

- Analysis code is pure functions: data in, plain data out (for example `Mark`). The UI decides colors.
- Board type is computed once and read by both the on-screen label and the tavern marks. Do not recompute it elsewhere.
- Name the domain module `domain.py`, never `types.py`.
- Add source-file license lines (AGPL-3.0) to new files, like the existing ones.
- Update `docs/CHANGELOG.md` for any user-visible change.

## Known unverified areas

Turn number (counter / 2), gold, placement and game-end detection were tested only on a made-up log, not a real game. Do not assume they are right. Check with `track --replay REAL_LOG --debug` and compare with notes from the real game.

## Before saying a change is done

1. Run the test suite (command in `build_and_test/README.md`).
2. If you touched parsing or the screen, run `python -m bgtools demo` and a replay of a sample log.
3. Check that no file in `core` imports from another layer.
