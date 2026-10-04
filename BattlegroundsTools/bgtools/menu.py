# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The numbered menu. It only shows choices and calls the functions it is given."""

import os
from typing import Callable, Dict, List, Tuple

Action = Callable[[], None]

TITLE = [
    "==========================================",
    "       BATTLEGROUNDS TOOLS",
    "==========================================",
]

# (key, label, action name)
ITEMS: List[Tuple[str, str, str]] = [
    ("1", "Live tracker  (start a Battlegrounds game first)", "tracker"),
    ("2", "Browse minions  (interactive)", "browse"),
    ("3", "Show minions for one tier", "tier"),
    ("4", "Refresh card data  (after a game patch)", "refresh"),
    ("5", "My triple targets  (search minions, add favorites)", "targets"),
    ("6", "Edit triple_targets.txt in Notepad", "edit_targets"),
    ("7", "Open README", "readme"),
]


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _run_guarded(action: Action) -> None:
    """Run one menu action. Ctrl+C or an error message returns to the menu."""
    try:
        action()
    except KeyboardInterrupt:
        print()
    except SystemExit as e:
        if e.code not in (None, 0):
            print(e.code)


def run_menu(actions: Dict[str, Action]) -> None:
    while True:
        _clear()
        print("\n".join(TITLE) + "\n")
        for key, label, _ in ITEMS:
            print(f"  {key}. {label}")
        print("  Q. Quit\n")
        print("  Tip: Ctrl+C stops the tracker and brings you back to this menu.\n")
        try:
            choice = input("Choose an option: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if choice == "q":
            return
        for key, _, name in ITEMS:
            if choice == key and name in actions:
                _clear()
                _run_guarded(actions[name])
                if name not in ("edit_targets", "readme"):
                    print()
                    try:
                        input("Press Enter to go back to the menu...")
                    except (EOFError, KeyboardInterrupt):
                        print()
                break
