def optimize_turn(gold, shop_minions, board_minions, current_tier, upgrade_cost):
    """
    Stockfish-Tier Multi-Resource ILP Solver with an internal
    evaluation matrix for tracking absolute turn perfection ceilings.
    """
    max_slots = 7
    current_board_count = len(board_minions)
    choices = []
    
    # 1. GENERATE GAME SELECTION ARRAY
    for minion in shop_minions:
        choices.append({
            "name": minion["name"],
            "type": "BUY",
            "cost": 3,
            "value": minion["value"],
            "space_taken": 0
        })

    if current_board_count >= max_slots and board_minions:
        weakest_board_minion = min(board_minions, key=lambda m: m["value"])
        for minion in shop_minions:
            net_trade_value = minion["value"] - weakest_board_minion["value"]
            if net_trade_value > 0:
                choices.append({
                    "name": minion["name"],
                    "type": "SELL_TO_BUY",
                    "cost": 2, 
                    "value": net_trade_value,
                    "space_taken": 0
                })

    upgrade_strategic_weight = 7.5 if current_tier < 4 else 5.0
    if upgrade_cost <= gold:
        choices.append({
            "name": f"⭐ Upgrade to Tier {current_tier + 1}",
            "type": "UPGRADE",
            "cost": upgrade_cost,
            "value": upgrade_strategic_weight,
            "space_taken": 0
        })

    # 2. CALCULATE ABSOLUTE ENGINE CEILING (THE PERFECT PATHWAY VALUE)
    best_value = 0
    best_combination = []
    num_choices = len(choices)

    for i in range(1 << num_choices):
        current_combination = []
        total_cost = 0
        total_value = 0

        for j in range(num_choices):
            if (i >> j) & 1:
                current_combination.append(choices[j])
                total_cost += choices[j]["cost"]
                total_value += choices[j]["value"]

        if total_cost <= gold:
            if total_value > best_value:
                best_value = total_value
                best_combination = current_combination

    # 3. PACK AND RETURN DECISIONS WITH THE TRUTH CEILING SCORE
    buys = [item["name"] for item in best_combination if item["type"] == "BUY"]
    upgrades = [item["name"] for item in best_combination if item["type"] == "UPGRADE"]
    trades = [(item["associated_sell"], item["name"]) for item in best_combination if item["type"] == "SELL_TO_BUY"]

    return {
        "buys": buys,
        "upgrades": upgrades,
        "trades": trades,
        "engine_ceiling_value": best_value if best_value > 0 else 1.0,
        "remaining_gold": gold - sum(item["cost"] for item in best_combination)
    }
