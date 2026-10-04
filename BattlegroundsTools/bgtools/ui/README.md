# UI adapters and how to build an overlay_adapter

The terminal screen is one way to show a game. An overlay is another: a small, polished window that sits on top of Hearthstone and shows the same information. This file explains how to add one without touching the rules of the tool.

## What an overlay_adapter is

A UI adapter takes a `Snapshot` (defined in `core/domain.py`) and draws it. It may send simple commands back (for example "add this minion to my triple targets"). It never reads the game log, never reads card data, and never decides advice. Those stay in `file_adapters`, `analysis` and `modes`.

Put it in `bgtools/ui/overlay_adapter/`.

## Rules

- It may import from `core` only, like the rest of `ui`. It must not import `analysis`, `file_adapters` or `modes`.
- Standard library only. `tkinter` ships with Python, so a first overlay needs nothing to install. PyInstaller bundles it into the `.exe`.
- It receives finished Snapshots. If the loop that builds them is still inside `modes/live_tracker.py`, move that loop into a `TrackerSession` (no screen code) first, so the terminal and the overlay share it.
- Colors come from named style tokens, not hard-coded values. The terminal tokens are ANSI codes, so add an overlay palette next to them with the same names.

## Steps

1. **Preview first.** Create a function that draws a Snapshot, and run it with `python -m bgtools demo` (made-up data). No log or game needed.
2. **Make a borderless, always-on-top window.** With tkinter: `overrideredirect(True)` and `attributes("-topmost", True)`. A fixed transparent color (`-transparentcolor`) or `-alpha` gives the see-through look. These options are Windows behavior; test them on your machine.
3. **Draw from the Snapshot.** One row per tavern minion, with tier badge, stats, type and the mark text. Reuse the same marks the terminal shows, so the two never disagree.
4. **Update without flicker.** Receive new Snapshots on a queue and apply them from the UI thread (`after()` polling). Redraw only rows that changed.
5. **Make it movable and remembered.** Drag to move, save the position in `data\`, and add a hotkey or tray-free way to hide and show it.
6. **Click-through when idle (optional).** Needs a Windows call through `ctypes` to set the window as transparent to mouse clicks. Verify it before relying on it.
7. **Connect it in `__main__.py`.** Add a command such as `python -m bgtools overlay`. Nothing else in the project should change.
8. **Test.** Unit-test any layout and formatting code that doesn't need a window. Check by hand with `demo` and with a replay of a real log.

## Making it feel polished

- Keep it small. Show only what changes a decision: tavern marks, your board's type, triple hints.
- Readable at a glance: large stats, short reason text, consistent column widths.
- Respect screen space: never cover the shop or the hero power area, and let the user choose the corner.
- No flashing. Fade or highlight a row briefly when it changes.
- Fail quietly: if a value is missing, show `?` like the terminal does.

## Things to check before shipping

- **Display mode.** Overlays like this generally need Hearthstone in windowed or borderless mode, not exclusive fullscreen. Confirm on your setup.
- **Blizzard's rules.** An overlay that only reads the log file and draws a separate window doesn't modify the game, but read Blizzard's current policy on third-party tools before you promote it.
- **Antivirus.** Always-on-top windows built with PyInstaller are sometimes flagged. Mention it in the README.
