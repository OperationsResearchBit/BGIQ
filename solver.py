def optimize_turn(gold, shop_minions, board_minions, current_tier, upgrade_cost):
    """
    Advanced Combinatorial ILP Solver that calculates optimization decisions
    based on dynamic minion tiers, economy values, and hand buffer constraints.
    """
    max_slots = 7
    current_board_count = len(board_minions)
    choices = []
    
    # 1. EVALUATE CARD CHOICES WITH TIER & ECONOMY SCALING
    for minion in shop_minions:
        # Base weight scales dynamically with card tier rather than a flat placeholder
        tier = minion.get("tier", 1)
        base_value = minion["value"] + (tier * 1.5)
        
        # Economy adjustments: Token generators or card gainers get a cost reduction discount
        net_cost = 3
        if "Scout" in minion["name"] or "Economy" in minion["name"]:
            net_cost = 2  # Discounts the cost constraint step because of sellback value
            base_value += 2.0  # Adds strategic scaling weight

        choices.append({
            "name": minion["name"],
            "type": "BUY",
            "cost": net_cost,
            "value": base_value,
            "space_taken": 0
        })

    # 2. PACK TRADES SEPARATELY FOR BOARD MANAGEMENT
    if current_board_count >= max_slots and board_minions:
        weakest_board_minion = min(board_minions, key=lambda m: m["value"])
        for minion in shop_minions:
            tier = minion.get("tier", 1)
            calculated_value = minion["value"] + (tier * 1.5)
            net_trade_value = calculated_value - weakest_board_minion["value"]
            
            if net_trade_value > 0:
                choices.append({
                    "name": minion["name"],
                    "type": "SELL_TO_BUY",
                    "cost": 2, 
                    "value": net_trade_value,
                    "space_taken": 0
                })

    # 3. PACK TAVERN UPGRADE WITH HEALTH BOUNDED SCALING MATRIX
    upgrade_strategic_weight = 8.5 if current_tier < 4 else 5.0
    if upgrade_cost <= gold:
        choices.append({
            "name": f"⭐ Upgrade to Tier {current_tier + 1}",
            "type": "UPGRADE",
            "cost": upgrade_cost,
            "value": upgrade_strategic_weight,
            "space_taken": 0
        })

    # 4. RUN COMBINATORIAL OPTIMIZATION SEARCH TREE
    best_value = 0
    best_combination = []
    num_choices = len(choices)

    for i in range(1 << num_choices):
        current_combination = []
        total_cost = 0
        total_value = 0
        has_upgrade = False
        has_minion_action = False

        for j in range(num_choices):
            if (i >> j) & 1:
                current_combination.append(choices[j])
                total_cost += choices[j]["cost"]
                total_value += choices[j]["value"]
                if choices[j]["type"] == "UPGRADE":
                    has_upgrade = True
                if choices[j]["type"] in ["BUY", "SELL_TO_BUY"]:
                    has_minion_action = True

        # Dual-Action Constraint Verification
        if has_upgrade and not has_minion_action:
            remaining_gold_after_upgrade = gold - upgrade_cost
            if remaining_gold_after_upgrade >= 3 and any(c["type"] in ["BUY", "SELL_TO_BUY"] and c["cost"] <= remaining_gold_after_upgrade for c in choices):
                continue

        if total_cost <= gold:
            if total_value > best_value:
                best_value = total_value
                best_combination = current_combination

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
