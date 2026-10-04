# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Enforces the dependency rule from docs/ARCHITECTURE.md: imports point inward only."""

import ast
import sys
import unittest
from pathlib import Path

PKG = Path(__file__).resolve().parents[2] / "bgtools"

# folder -> the bgtools folders it is allowed to import from (besides itself)
ALLOWED = {
    "core": set(),
    "analysis": {"core"},
    "file_adapters": {"core"},
    "ui": {"core"},
    "modes": {"core", "analysis", "ui"},
}


def bgtools_imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names = [node.module]
        else:
            continue
        for n in names:
            parts = n.split(".")
            if parts[0] == "bgtools" and len(parts) > 1:
                found.add(parts[1])
    return found


class DependencyRule(unittest.TestCase):
    def test_imports_point_inward(self):
        problems = []
        for folder, allowed in ALLOWED.items():
            for py in (PKG / folder).rglob("*.py"):
                for target in bgtools_imports(py):
                    if target != folder and target not in allowed:
                        problems.append(f"{py.relative_to(PKG)} imports bgtools.{target}")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_core_uses_only_standard_library(self):
        stdlib = getattr(sys, "stdlib_module_names", None)  # Python 3.10+
        if stdlib is None:
            self.skipTest("needs Python 3.10+ to list standard library modules")
        bad = []
        for py in (PKG / "core").rglob("*.py"):
            tree = ast.parse(py.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    mods = [node.module]
                else:
                    continue
                for m in mods:
                    top = m.split(".")[0]
                    if top not in stdlib and top != "bgtools":
                        bad.append(f"{py.name}: {m}")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
