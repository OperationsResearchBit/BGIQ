# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The command registry. A command is a function marked with @command.

To add one, create bgtools/commands/cmd_<name>.py, write a handler that takes the parsed
args, and decorate it:  @command("name", "help text", configure_fn, menu="Menu label").
`configure_fn(subparser)` adds options and may be left out. `menu` is optional; give it to
show the command in the numbered menu. Nothing else in the app changes.
"""

from typing import Callable, Dict, Optional, Tuple

COMMANDS: Dict[str, Tuple[str, Optional[Callable], Callable]] = {}
MENU_LABELS: Dict[str, str] = {}


def command(name: str, help: str, configure: Optional[Callable] = None,
            menu: Optional[str] = None):
    def register(handler):
        COMMANDS[name] = (help, configure, handler)
        if menu:
            MENU_LABELS[name] = menu
        return handler
    return register
