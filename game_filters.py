import re
import time
import streamlit as st
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Iterator
from solver import optimize_turn

@dataclass
class ShopMinion:
    name: str
    tribe: str = "Neutral"
    tier: int = 1
    mechanics: List[str] = field(default_factory=list)
    value: float = 4.0

# PRECOMPILED REGEX OBJECT PATTERNS
RE_VALUE = re.compile(r"value=(-?\d+)")
RE_ENTITY_NAME = re.compile(r"entityName=(.*?)(?:\s+id=|\s+zone=|\s+cardId=|$)")
RE_PLAYER = re.compile(r"player=(\d+)")
RE_ZONEPOS = re.compile(r"zonePos=(\d+)")
RE_CARDID = re.compile(r"cardId=(\S*)")
RE_ZONE = re.compile(r"\bzone=(\S+)")

# GLOBAL COLLECTIBLE MINION DEFINITIONS DATABASE
GLOBAL_LIVE_DATABASE = {
    "Mechagnome Interpreter": {"tribe": "Mech", "tier": 1, "mechanics": []},
    "Cord Puller": {"tribe": "Mech", "tier": 1, "mechanics": ["DEATHRATTLE"]},
    "Patient Scout": {"tribe": "Neutral", "tier": 2, "mechanics": []},
    "Lurking Lionfish": {"tribe": "Naga", "tier": 2, "mechanics": []},
    "Titus Rivendare": {"tribe": "Neutral", "tier": 5, "mechanics": ["ENROLLER_DEATHRATTLE"]}
}

class GameStateFilter:
    """
    Centralized extraction engine tracking live health, armor, APM, 
    and tavern tier metrics completely out of the background log stream.
    """
    
    @staticmethod
    def extract_telemetry_metric(line: str, pattern: re.Pattern) -> Optional[int]:
        m = pattern.search(line)
        if not m: return None
        try: return int(m.group(1))
        except ValueError: return None

    @staticmethod
    def extract_player(line: str) -> Optional[int]:
        m = RE_PLAYER.search(line)
        return int(m.group(1)) if m else None

    @staticmethod
    def extract_entity_name(line: str) -> Optional[str]:
        m = RE_ENTITY_NAME.search(line)
        if not m: return None
        name = m.group(1).strip()
        if not name or "UNKNOWN ENTITY" in name or len(name) <= 2: return None
        return name

    @staticmethod
    def is_valid_collectible_shop_minion(line: str, zonepos_match: Any, cardid_match: Any, current_shop_list: list) -> bool:
        if not zonepos_match or not cardid_match: return False
        zonepos = int(zonepos_match.group(1))
        card_id = cardid_match.group(1)
        if zonepos == 0 or not card_id or card_id.startswith("TB_BaconShop"): return False
        if len(current_shop_list) >= 7: return False
        return True

    @staticmethod
    def process_raw_line_state(line: str, state: dict) -> Iterator[Dict[str, Any]]:
        """
        Processes text structures and applies game state rule variations natively.
        """
        if "zone from ->" in line or "SHOW_ENTITY" in line:
            state["actions_this_turn"] += 1

        if "tag=PLAYER_TECH_LEVEL" in line:
            player = GameStateFilter.extract_player(line)
            val = GameStateFilter.extract_telemetry_metric(line, RE_VALUE)
            if player == 1 and val is not None:
                state["tavern_tier"] = val
                yield {"type": "tavern_tier", "player": 1, "value": val}
            elif player == 2 and val is not None:
                state["opponent_tier"] = val
                yield {"type": "tavern_tier", "player": 2, "value": val}

        if "tag=HEALTH" in line and "Entity=" in line:
            player = GameStateFilter.extract_player(line)
            val = GameStateFilter.extract_telemetry_metric(line, RE_VALUE)
            if player == 1 and val is not None:
                state["health"] = val
                yield {"type": "health", "player": 1, "value": val}

        if "tag=ARMOR" in line and "Entity=" in line:
            player = GameStateFilter.extract_player(line)
            val = GameStateFilter.extract_telemetry_metric(line, RE_VALUE)
            if player == 1 and val is not None:
                state["armor"] = val
                yield {"type": "armor", "player": 1, "value": val}

        if "zone=HAND" in line and "zone from ->" in line:
            name = GameStateFilter.extract_entity_name(line)
            if name:
                yield {"type": "user_purchase", "name": name}

        if "tag=STEP value=MAIN_COMBAT" in line or "Bacon_Combat" in line:
            state["phase"] = "combat"
            state["shop"] = []
            state["actions_this_turn"] = 0
            yield {"type": "phase", "value": "combat"}
            return

        if "value=MAIN_START_TRIGGERS" in line or "tag=TURN value=" in line:
            state["phase"] = "shopping"
            state["shop"] = []
            yield {"type": "phase", "value": "shopping"}
            return

        if "FULL_ENTITY" in line and "zone=PLAY" in line and "player=14" in line:
            zonepos_match = RE_ZONEPOS.search(line)
            cardid_match = RE_CARDID.search(line)
            
            if not GameStateFilter.is_valid_collectible_shop_minion(line, zonepos_match, cardid_match, state["shop"]):
                return

            name = GameStateFilter.extract_entity_name(line)
            if not name or any(m.name == name for m in state["shop"]): return

            card_db = state.get("card_db", GLOBAL_LIVE_DATABASE)
            meta = card_db.get(name, {"tribe": "Neutral", "tier": 1, "mechanics": []})
            
            minion = ShopMinion(
                name=name,
                tribe=meta.get("tribe", "Neutral"),
                tier=meta.get("tier", 1),
                mechanics=meta.get("mechanics", []),
            )
            state["shop"].append(minion)
            yield {"type": "shop_minion", "minion": minion}
