# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Contracts the inner layers need. The adapters in file_adapters/ fulfil them."""

from __future__ import annotations

from typing import Dict, Iterator, List, Mapping, Optional, Protocol, Tuple

from bgtools.core.domain import Card, Minion

# lowercase card name -> (card name as written, your reason)
TargetMap = Mapping[str, Tuple[str, str]]


class CardSource(Protocol):
    def by_id(self) -> Dict[str, Card]: ...
    def minions(self) -> List[Minion]: ...
    def tier_by_name(self) -> Dict[str, int]: ...
    def refresh(self) -> None: ...


class LogSource(Protocol):
    path: str

    def lines(self) -> Iterator[str]:
        """Yield every complete line not read yet, then stop."""

    def switch_if_newer(self) -> bool:
        """Move to a newer game log if one appeared. True when it switched."""


class HistoryStore(Protocol):
    def load(self) -> List[dict]: ...
    def save(self, history: List[dict]) -> None: ...


class TargetsStore(Protocol):
    def load(self) -> TargetMap: ...
    def read_entries(self) -> Tuple[List[str], List[Tuple[str, str]]]: ...
    def write_entries(self, header: List[str], entries: List[Tuple[str, str]]) -> None: ...
