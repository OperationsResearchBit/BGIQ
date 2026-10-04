# Architecture

bgtools uses a **ports and adapters** design (also called hexagonal architecture) with a thin UI layer.
The rules of the tool sit in the middle and know nothing about files, the network, or the screen.
Everything that touches the outside world plugs in around them.

```
                 ┌─────────────────────────────────────────┐
                 │  __main__.py  (connects the pieces)      │
                 │  menu.py                                 │
                 │                                          │
                 │   modes ──────────► ui                   │
                 │     │                │                   │
                 │     ▼                ▼                   │
   file_adapters ──► analysis ──► core ◄─────────────        │
   (files, network)              (data, contracts, rules)    │
                 └─────────────────────────────────────────┘
```

## The dependency rule

Imports point inward only. `core` imports nothing from the rest of the package.

| Folder | May import from | What it holds |
|---|---|---|
| `core` | standard library only | data types, the contracts (`ports.py`), the log-driven game state, file locations |
| `analysis` | `core` | board strength, board type, advice rules, minion search |
| `file_adapters` | `core` | reading the game log, card data, saving your history and triple targets |
| `ui` | `core` | styling (`bgui.py`), screen pieces (`components\`), window fitting (`layout.py`), experiments (`sandbox\`) |
| `modes` | `core`, `analysis`, `ui` | what the tool does: live tracker, game review, minion browser, triple-target editor |
| `__main__.py`, `menu.py` | everything | the entry point; the only place adapters are connected to modes |

`build_and_test\tests\test_architecture.py` checks this on every test run, so the rule cannot drift.

## How a frame gets on screen

1. `file_adapters\log_tail.py` yields new lines of `Power.log` (any `LogSource`).
2. `core\game_state.py` turns lines into game state: your board, the tavern, your hand.
3. `modes\live_tracker.py` builds one `Snapshot` (defined in `core\domain.py`) from that state:
   - `analysis\board_type.py` computes the board **Profile** once.
   - The screen label and `analysis\recommender\rules.py` both read that Profile, so "Leaning Murloc" on screen and "fits Murloc" in the advice cannot disagree.
4. `ui\layout.py` picks the fullest layout that fits the window and asks each piece in `ui\components\` for its lines. Every piece is a function from a `Snapshot` to a list of lines.

## The original plan, mapped to today's folders

The first design had four boxes: UI adapters on top, a middle layer holding the session, analysis and domain, then ports, then adapters. The folder structure moved things around, but the idea is the same. This diagram shows where each part of that plan lives now.

```
 UI (terminal now, art-heavy UI later)
 ui/  bgui.py · layout.py · components/           draws a Snapshot
 modes/  live_tracker · game_review ·             what the tool does
         minion_browser · triple_targets
        │  receive a Snapshot, send favorites (triple targets)
 ┌──────┴──────────────────────────────────────────┐
 │ modes/live_tracker.py   the "Session": builds a │
 │                         Snapshot from game state│
 │ analysis/  stats · board_type ·                 │
 │            recommender/rules   (pure functions) │
 │ core/domain.py   Minion · Card · Profile ·      │
 │                  Snapshot · Mark · GameRecord   │
 │ core/game_state.py   log lines -> game state    │
 └──────┬──────────────────────────────────────────┘
 ports (core/ports.py):
   LogSource · CardSource · TargetsStore · HistoryStore
        │
 adapters (file_adapters/):
   log_tail.py (follow Power.log)   log_replay.py (read a saved file)
   cards_hsjson.py (HearthstoneJSON)
   stores_json.py (history.json)    targets_txt.py (triple_targets.txt)

 __main__.py and menu.py connect the adapters to the modes.
```

| Original plan | Today |
|---|---|
| UI adapters | `ui\` (drawing) and `modes\` (what runs). A future art-heavy UI would replace `ui\` and reuse `modes\`. |
| `app/` Session | `modes\live_tracker.py` (`build_snapshot` and the run loop). There is no separate Session class yet. |
| `analysis/` | `analysis\`, unchanged: stats, board type, recommender rules. |
| `domain/` (Minion, Board, Snapshot, Recommendation, Profile) | `core\domain.py`. `Board` is a tuple of `Minion`, and `Recommendation` became `Mark`. |
| Port `LogSource` | `LogSource` |
| Port `CardCatalog` | `CardSource` |
| Port `ProfileStore` | `TargetsStore` (your triple targets) |
| Port `HistoryStore` | `HistoryStore` |
| Adapters: tail, replay, HearthstoneJSON, JSON files | `log_tail`, `log_replay`, `cards_hsjson`, `stores_json` and `targets_txt` |

Differences from the plan:

- `core\game_state.py` is new. It turns log lines into game state, which the plan did not list. It is pure logic, so it sits in `core`.
- The plan had the UI receive pushed updates. Today the tracker loop pulls: it reads new log lines, builds one `Snapshot` and redraws. A second UI would need that loop moved behind a Session.

## Why things are named the way they are

- **`domain.py`, not `types.py`.** A file called `types.py` can shadow Python's standard `types` module when scripts run from its folder, which causes confusing import errors.
- **`core` and `modes` instead of one `app` folder.** `domain.py` and `ports.py` are the innermost layer; the things the tool does sit above them and use `analysis`. Two folders keep the rule readable from the names.
- **`file_adapters`.** Each file implements a contract from `core\ports.py` and touches files, folders or the network.
- **`modes`.** Each file is something you can run: track a live game, review finished games, browse minions, edit triple targets.
- **`ui\sandbox`.** A staging area for new screen pieces, not a plugin system. Build a piece there, preview it with `python -m bgtools demo`, then move its file to `ui\components\` when it is ready.
- **`bgui.py` stays low-level.** Colors, banner, header, badges, wrapping, and the named style tokens. Screen pieces live in `components\` so this file does not grow into a 600-line catch-all.
- **No `src\` folder.** The program is run with `python -m bgtools` or shipped as an `.exe`, not installed with pip, so the extra folder adds nothing.

## Adding things

- **A new screen piece:** write `def my_piece(snap: Snapshot) -> list[str]` in `ui\sandbox\`, preview it with the demo runner, then move it to `ui\components\` and add it to `REGISTRY`.
- **A new advice rule:** add a function in `analysis\recommender\` that reads the `Profile` and returns plain data (`Mark`). The UI decides how to color it.
- **A new data source** (for example a local server): add a class in `file_adapters\` that satisfies the matching contract in `core\ports.py`, and connect it in `__main__.py`. No other file changes.
- **A new mode:** add a file in `modes\` that takes its adapters as arguments, then add a command in `__main__.py`.

## Known gaps

- `modes\game_review.py` saves finished games and compares each with your earlier ones. A screen that ranks your past boards is not built yet (see the changelog's "Not yet built" list).
- The log parsing in `core\game_state.py` was written against a log format as understood and tested on a made-up log only (see "Known limits" in the changelog).
