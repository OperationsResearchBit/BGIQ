# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Advice rules. Each rule reads the board Profile and returns plain data."""

from bgtools.analysis.recommender.rules import RULES, pick_marks, rule
from bgtools.core.discovery import import_matching


def discover():
    """Import every rule_<name>.py in this folder; each registers its rules with @rule."""
    return import_matching(__name__, "rule_")


discover()

__all__ = ["RULES", "discover", "pick_marks", "rule"]
