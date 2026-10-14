# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Commands: what `python -m bgtools <name>` can do. Connects modes to adapters.

Built-in commands live in __main__.py. Extra ones are files named cmd_<name>.py here;
discover() imports them so they register themselves.
"""

from bgtools.commands.registry import COMMANDS, MENU_LABELS, command
from bgtools.core.discovery import import_matching


def discover():
    return import_matching(__name__, "cmd_")


__all__ = ["COMMANDS", "MENU_LABELS", "command", "discover"]
