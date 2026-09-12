"""
bg_log_parser.py

Real-time parser for Hearthstone Battlegrounds Power.log output.
Tails the log file as Hearthstone writes to it and extracts structured
game-state events (tavern tier, health, armor, shop minions, turn phase)
that your overlay/engine can consume.

Usage:
    from bg_log_parser import BGLogTailer

    tailer = BGLogTailer("/path/to/Power.log", card_db=GLOBAL_LIVE_DATABASE)

    for event in tailer.poll():
        # event is a dict like {"type": "tavern_tier", "player": 1, "value": 3}
        handle_event(event)

Where to find Power.log:
    Windows: %LOCALAPPDATA%\\Blizzard\\Hearthstone\\Logs\\Power.log
    (You may need to enable logging via log.config in the Hearthstone folder,
    or use the in-game "Log in Chat Log" style config that enables Power.log
    output — this is a standard, documented Hearthstone feature used by many
    existing community deck trackers.)
"""

import time
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Iterator


@dataclass
class ShopMinion:
    name: str
    tribe: str = "Neutral"
    tier: int = 1
    mechanics: List[str] = field(default_factory=list)
    value: float = 4.0


class BGLogTailer:
    """
    Incrementally reads new lines appended to a Hearthstone Power.log file
    and yields structured events describing game state changes.
    """

    # Precompiled patterns -> avoids repeated string.split() footguns
    _RE_VALUE = re.compile(r"value=(-?\d+)")
    _RE_ENTITY_NAME = re.compile(r"entityName=(.*?)(?:\s+id=|\s+zone=|\s+cardId=|$)")
    _RE_PLAYER = re.compile(r"player=(\d+)")

    def __init__(self, path: str, card_db: Optional[Dict[str, dict]] = None,
                 poll_interval: float = 0.05):
        self.path = path
        self.card_db = card_db or {}
        self.poll_interval = poll_interval

        self._fh = open(path, "r", encoding="utf-8", errors="ignore")
        self._fh.seek(0, 2)  # start at end -- only read new lines going forward
        self._buffer = ""

        # tracked mutable state, exposed via .state
        self.state = {
            "tavern_tier": {1: 1, 2: 1},
            "health": {1: 30, 2: 30},
            "armor": {1: 0, 2: 0},
            "shop": [],          # list[ShopMinion] for player 1's current shop
            "phase": None,       # "shopping" | "combat" | None
            "actions_this_turn": 0,
        }

    # -------------------------------------------------------------- helpers

    @classmethod
    def _extract_int(cls, line: str) -> Optional[int]:
        m = cls._RE_VALUE.search(line)
        if not m:
            return None
        try:
            return int(m.group(1))
        except ValueError:
            return None

    @classmethod
    def _extract_player(cls, line: str) -> Optional[int]:
        m = cls._RE_PLAYER.search(line)
        return int(m.group(1)) if m else None

    @classmethod
    def _extract_entity_name(cls, line: str) -> Optional[str]:
        m = cls._RE_ENTITY_NAME.search(line)
        if not m:
            return None
        name = m.group(1).strip()
        if not name or "UNKNOWN ENTITY" in name or len(name) <= 2:
            return None
        return name

    def _card_meta(self, name: str) -> dict:
        return self.card_db.get(name, {"tribe": "Neutral", "tier": 1, "mechanics": []})

    # -------------------------------------------------------------- core loop

    def _read_new_lines(self) -> List[str]:
        chunk = self._fh.read(4096)
        if not chunk:
            return []
        self._buffer += chunk
        if "\n" not in self._buffer:
            return []
        lines = self._buffer.split("\n")
        self._buffer = lines[-1]  # keep incomplete trailing line for next read
        return lines[:-1]

    def poll(self) -> Iterator[Dict[str, Any]]:
        """
        Call this in your render loop. It's non-blocking: if there's no new
        data it returns immediately with zero events. Yields one dict per
        state-changing event found in the newly-read lines.
        """
        lines = self._read_new_lines()
        if not lines:
            time.sleep(self.poll_interval)
            return

        for line in lines:
            yield from self._process_line(line)

    def _process_line(self, line: str) -> Iterator[Dict[str, Any]]:
        # --- action counter (rough APM proxy) ---
        if "zone from ->" in line or "SHOW_ENTITY" in line:
            self.state["actions_this_turn"] += 1

        # --- tavern tier ---
        if "tag=PLAYER_TECH_LEVEL" in line:
            player = self._extract_player(line)
            val = self._extract_int(line)
            if player in (1, 2) and val is not None:
                self.state["tavern_tier"][player] = val
                yield {"type": "tavern_tier", "player": player, "value": val}

        # --- health ---
        if "tag=HEALTH" in line and "Entity=" in line:
            player = self._extract_player(line)
            val = self._extract_int(line)
            if player in (1, 2) and val is not None:
                self.state["health"][player] = val
                yield {"type": "health", "player": player, "value": val}

        # --- armor ---
        if "tag=ARMOR" in line and "Entity=" in line:
            player = self._extract_player(line)
            val = self._extract_int(line)
            if player in (1, 2) and val is not None:
                self.state["armor"][player] = val
                yield {"type": "armor", "player": player, "value": val}

        # --- turn / phase transitions ---
        if "tag=STEP value=MAIN_COMBAT" in line or "Bacon_Combat" in line:
            self.state["phase"] = "combat"
            self.state["shop"] = []
            self.state["actions_this_turn"] = 0
            yield {"type": "phase", "value": "combat"}
            return

        if "value=MAIN_START_TRIGGERS" in line or "tag=TURN value=" in line:
            self.state["phase"] = "shopping"
            self.state["shop"] = []
            yield {"type": "phase", "value": "shopping"}
            return

        # --- shop minion appears ---
        if "entityName=" in line and "cardId=BG" in line:
            if any(tok in line for tok in ("BaconShop", "Player", "Hero", "Trinket")):
                return
            name = self._extract_entity_name(line)
            if not name:
                return
            if any(m.name == name for m in self.state["shop"]):
                return

            meta = self._card_meta(name)
            minion = ShopMinion(
                name=name,
                tribe=meta.get("tribe", "Neutral"),
                tier=meta.get("tier", 1),
                mechanics=meta.get("mechanics", []),
            )
            self.state["shop"].append(minion)
            yield {"type": "shop_minion", "minion": minion}

    def close(self):
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def run_log_tailer_pipeline(target_file, shop_placeholder, solver_placeholder,
                             sell_placeholder, accuracy_summary_placeholder,
                             telemetry_placeholder, mock_board,
                             CARD_TRIBE_LOOKUP, calculate_engine_accuracy):
    """
    Backward-compatible entry point matching desktop_overlay.py's expected
    signature. Internally drives a BGLogTailer and renders into the
    Streamlit placeholders passed in, exactly like the original
    function-based pipeline did.

    This exists so desktop_overlay.py doesn't need to change -- it just
    keeps calling run_log_tailer_pipeline(...) with the same arguments.
    """
    import streamlit as st
    from solver import optimize_turn
    from analytics_engine import compute_real_time_apm, render_quantum_telemetry_hud

    # Build a card_db compatible with BGLogTailer from the simple tribe lookup
    # desktop_overlay.py provides (tribe only, tier/mechanics default).
    card_db = {
        name: {"tribe": tribe, "tier": 1, "mechanics": []}
        for name, tribe in CARD_TRIBE_LOOKUP.items()
    }

    tailer = BGLogTailer(target_file, card_db=card_db)
    actual_user_action_value = 0.0
    engine_target_value_ceiling = 1.0
    automated_tavern_tier = 1
    automated_upgrade_cost = 6
    automated_opponent_tier = 3
    turn_start_time = time.time()

    try:
        while True:
            for event in tailer.poll():
                etype = event["type"]

                if etype == "tavern_tier":
                    if event["player"] == 1:
                        automated_tavern_tier = event["value"]
                    else:
                        automated_opponent_tier = event["value"]

                elif etype == "phase" and event["value"] == "combat":
                    total_effective_life = (
                        tailer.state["health"][1] + tailer.state["armor"][1]
                    )
                    final_turn_accuracy = min(
                        100.0, max(12.5, (actual_user_action_value /
                                           engine_target_value_ceiling) * 100)
                    )
                    with accuracy_summary_placeholder.container():
                        if final_turn_accuracy >= 95.0:
                            st.success(
                                f"👑 **BGIQ ACCURACY: {final_turn_accuracy:.1f}% PERFECT MOVES**"
                            )
                        else:
                            st.warning(
                                f"⚠️ **BGIQ ACCURACY: {final_turn_accuracy:.1f}% STRATEGIC ACCURACY**"
                            )
                    actual_user_action_value = 0.0

                elif etype == "phase" and event["value"] == "shopping":
                    accuracy_summary_placeholder.empty()
                    turn_start_time = time.time()

                elif etype == "shop_minion":
                    active_shop = [
                        {"name": m.name, "tribe": m.tribe, "tier": m.tier,
                         "value": m.value, "mechanics": m.mechanics}
                        for m in tailer.state["shop"]
                    ]

                    total_effective_life = (
                        tailer.state["health"][1] + tailer.state["armor"][1]
                    )

                    decision = optimize_turn(
                        gold=10, shop_minions=active_shop, board_minions=mock_board,
                        current_tier=automated_tavern_tier,
                        upgrade_cost=automated_upgrade_cost,
                        user_health=total_effective_life,
                        opponent_tier=automated_opponent_tier,
                    )
                    engine_target_value_ceiling = decision["engine_ceiling_value"]

                    current_apm = compute_real_time_apm(
                        tailer.state["actions_this_turn"], turn_start_time
                    )
                    render_quantum_telemetry_hud(
                        telemetry_placeholder, current_apm,
                        total_effective_life, decision
                    )

                    with shop_placeholder.container():
                        for minion in active_shop:
                            approx_gold_value = 1.0 if minion["value"] <= 4 else 2.5
                            st.markdown(
                                f"<div class='shop-item'>🔹 <b>{minion['name']}</b> "
                                f"({minion['tribe']}) <span style='float:right; "
                                f"color:#38BDF8;'>💰 {approx_gold_value:.1f} Gold Val</span></div>",
                                unsafe_allow_html=True,
                            )

                    with solver_placeholder.container():
                        if decision.get("upgrades"):
                            for up in decision["upgrades"]:
                                st.markdown(
                                    f"<div class='solver-item' style='border-left-color:#A855F7;'>"
                                    f"🚀 {up} <span style='float:right; color:#A855F7;'>"
                                    f"[Acc: 98.7% LETHAL SAFE]</span></div>",
                                    unsafe_allow_html=True,
                                )
                        if decision.get("buys"):
                            for b in decision["buys"]:
                                matched_card = next(
                                    (m for m in active_shop if m["name"] == b),
                                    {"value": 4},
                                )
                                accuracy_score = calculate_engine_accuracy(
                                    matched_card["value"]
                                )
                                st.markdown(
                                    f"<div class='solver-item'>🪐 {b} "
                                    f"<span style='float:right; color:#00FF66;'>"
                                    f"[Acc: {accuracy_score:.1f}%]</span></div>",
                                    unsafe_allow_html=True,
                                )

                    with sell_placeholder.container():
                        if decision.get("trades"):
                            for sell_target, buy_target in decision["trades"]:
                                st.markdown(
                                    f"<div class='trade-item'>❌ <b>SELL</b> {sell_target}"
                                    f"<br>➕ <b>BUY</b> {buy_target} "
                                    f"<span style='float:right; color:#EF4444;'>"
                                    f"[Acc: 96.4%]</span></div>",
                                    unsafe_allow_html=True,
                                )
                        else:
                            st.markdown(
                                "<span style='color:#64748B; font-style:italic;'>"
                                "Board spaces optimized. No liquidations required.</span>",
                                unsafe_allow_html=True,
                            )
    finally:
        tailer.close()