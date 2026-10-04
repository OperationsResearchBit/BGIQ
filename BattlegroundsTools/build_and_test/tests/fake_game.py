# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""A small made-up game: card data and a Power.log that uses it.

Real logs are huge and change with game patches, so tests use this instead.
"""

PREFIX = "D 12:00:00.0000000 GameState.DebugPrintPower() - "


def _raw(cid, name, tier, atk, hp, races, text=""):
    c = {"id": cid, "name": name, "type": "MINION", "techLevel": tier, "attack": atk,
         "health": hp, "battlegroundsPremiumDbfId": 1, "text": text}
    if races:
        c["races"] = races
    return c


RAW_CARDS = [
    _raw("T_CAT", "Alley Cat", 1, 1, 1, ["BEAST"]),
    _raw("T_BEAR", "Mama Bear", 5, 4, 4, ["BEAST"], "Give <b>+4/+4</b> to Beasts."),
    _raw("T_LEADER", "Pack Leader", 3, 3, 3, ["BEAST"]),
    _raw("T_WEAVER", "Wrath Weaver", 1, 1, 3, ["DEMON"]),
    _raw("T_MECH", "Micro Machine", 1, 1, 2, ["MECHANICAL"]),
    _raw("T_ALL", "Amalgam", 1, 1, 2, ["ALL"]),
    _raw("T_PLAIN", "Plain Guy", 2, 2, 2, []),
    {"id": "T_GOLD", "name": "Golden Alley Cat", "type": "MINION", "techLevel": 1,
     "attack": 2, "health": 2, "races": ["BEAST"], "battlegroundsNormalDbfId": 1,
     "battlegroundsPremiumDbfId": 1},
    {"id": "T_SPELL", "name": "Not A Minion", "type": "SPELL"},
    {"id": "T_TEMPLATE", "name": "[BGTEMPLATE] Dummy", "type": "MINION", "techLevel": 1,
     "attack": 1, "health": 1, "battlegroundsPremiumDbfId": 1},
]


def _entity(eid, card, **tags):
    out = [PREFIX + f"FULL_ENTITY - Creating ID={eid} CardID={card}"]
    for k, v in tags.items():
        out.append(PREFIX + f"    tag={k} value={v}")
    return out


def game_lines(placement=3):
    """One full game: you have 3 beasts, the tavern has 3 minions, then it ends."""
    L = ["D 12:00:00.0000000 GameState.DebugPrintGame() - BuildNumber=1",
         "D 12:00:00.0000000 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Tester",
         PREFIX + "CREATE_GAME",
         PREFIX + "    GameEntity EntityID=1",
         PREFIX + "        tag=TURN value=1",
         PREFIX + "    Player EntityID=2 PlayerID=1",
         PREFIX + "        tag=PLAYER_TECH_LEVEL value=3",
         PREFIX + "        tag=RESOURCES value=9",
         PREFIX + "        tag=RESOURCES_USED value=3",
         PREFIX + "        tag=TEMP_RESOURCES value=0"]
    L += _entity(10, "TB_BaconShop_8P_PlayerE", CONTROLLER=1)
    L += _entity(11, "TB_BaconShopBob", CONTROLLER=2)
    L += _entity(12, "HERO_X", CARDTYPE="HERO", CONTROLLER=1, ZONE="PLAY",
                 PLAYER_LEADERBOARD_PLACE=placement)
    # your board (controller 1): Mama Bear (golden-looking buff via ATK tag), Alley Cat, Pack Leader
    L += _entity(20, "T_BEAR", CONTROLLER=1, ZONE="PLAY", ZONE_POSITION=1, ATK=6, HEALTH=6)
    L += _entity(21, "T_CAT", CONTROLLER=1, ZONE="PLAY", ZONE_POSITION=2)
    L += _entity(22, "T_LEADER", CONTROLLER=1, ZONE="PLAY", ZONE_POSITION=3)
    # your hand
    L += _entity(23, "T_MECH", CONTROLLER=1, ZONE="HAND", ZONE_POSITION=1)
    # the tavern (controller 2)
    L += _entity(30, "T_LEADER", CONTROLLER=2, ZONE="PLAY", ZONE_POSITION=1)
    L += _entity(31, "T_WEAVER", CONTROLLER=2, ZONE="PLAY", ZONE_POSITION=2)
    L += _entity(32, "T_ALL", CONTROLLER=2, ZONE="PLAY", ZONE_POSITION=3)
    L += _entity(33, "T_UNKNOWN_CARD", CONTROLLER=2, ZONE="PLAY", ZONE_POSITION=4)
    L += [PREFIX + "TAG_CHANGE Entity=GameEntity tag=TURN value=2",
          PREFIX + "TAG_CHANGE Entity=GameEntity tag=TURN value=3"]
    return L


def finished_game_lines(placement=3):
    return game_lines(placement) + [PREFIX + "TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE"]
