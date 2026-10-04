# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Import every module in a package whose name starts with a prefix.

This is how a new advice rule or command becomes part of the app by adding one file:
drop `rule_<name>.py` or `cmd_<name>.py` in the right folder and nothing else changes.
Modules load in name order. Standard library only.
"""

import importlib
import pkgutil
from typing import List


def import_matching(package: str, prefix: str) -> List[str]:
    """Import `package.<name>` for each submodule starting with prefix; return the names."""
    pkg = importlib.import_module(package)
    found = sorted(i.name for i in pkgutil.iter_modules(pkg.__path__) if i.name.startswith(prefix))
    for name in found:
        importlib.import_module(f"{package}.{name}")
    return found
