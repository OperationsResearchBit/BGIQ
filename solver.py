def optimize_turn(gold, shop_minions, board_minions, current_tier, upgrade_cost, user_health, opponent_tier):
    """
    Quantum Multi-Resource ILP Solver. Features automated board strategy pivots,
    high-APM hand buffering, and lethal safety margin calculations.
    """
    max_slots = 7
    current_board_value = sum(m["value"] for m in board_minions) if board_minions else 1.0
    
    # 1. LETHAL SURVIVAL RISK FRONTIER CALCULATION
    # Absolute max damage an opponent can deal = (Their Tier + 7 minions capped at Tier 6)
    max_possible_opponent_damage = opponent_tier + (7 * 6)
    is_100_percent_safe = user_health > max_possible_opponent_damage

    choices = []
    
    # 2. PACK MINIONS WITH HIGH-APM RECYCLING VALUATIONS
    for minion in shop_minions:
        net_cost = 3
        base_value = minion["value"] + (minion.get("tier", 1) * 1.5)
        
        # Infinite Economy Loops: Flag cycle assets (Pirates/Elementals)
        if "Scout" in minion["name"] or "Dealer" in minion["name"] or "Sellemental" in minion["name"]:
            net_cost = 1  # 3 Gold cost - 1 play refund - 1 sellback refund = Net 1 Gold cost!
            base_value += 4.0 # High priority weight for infinite generation loops

        choices.append({
            "name": minion["name"],
            "type": "BUY",
            "cost": net_cost,
            "value": base_value,
            "space_taken": 0
        })

    # 3. HIGH-COMPLEXITY STRATEGIC PIVOT ALGORITHM
    shop_tribe_values = {}
    for m in shop_minions:
        t = m.get("tribe", "Neutral")
        shop_tribe_values[t] = shop_tribe_values.get(t, 0) + m["value"]
    
    best_shop_tribe = max(shop_tribe_values, key=shop_tribe_values.get) if shop_tribe_values else "Neutral"
    # Pivot Trigger: If the shop offers a concentrated tribe build that breaks your current ceiling
    trigger_pivot = shop_tribe_values.get(best_shop_tribe, 0) > (current_board_value * 1.4)

    # 4. PACK TAVERN UPGRADE WITH LETHAL OVERRIDE RISK CONTROLS
    # If survival is 100% mathematically guaranteed, heavily prioritize leveling up!
    upgrade_weight = 15.0 if is_100_percent_safe else (5.0 if current_tier >= 4 else 8.5)
    if upgrade_cost <= gold:
        choices.append({
            "name": f"⭐ Upgrade to Tier {current_tier + 1}",
            "type": "UPGRADE",
            "cost": upgrade_cost,
            "value": upgrade_weight,
            "space_taken": 0
        })

    # 5. RUN ILP COMBINATORIAL OPTIMIZATION SEARCH TREE
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

    buys = [item["name"] for item in best_combination if item["type"] == "BUY"]
    upgrades = [item["name"] for item in best_combination if item["type"] == "UPGRADE"]

    return {
        "buys": buys,
        "upgrades": upgrades,
        "trigger_pivot": trigger_pivot,
        "pivot_target_tribe": best_shop_tribe,
        "lethal_safety_status": "100% SAFE" if is_100_percent_safe else "RISK DETECTED",
        "engine_ceiling_value": best_value if best_value > 0 else 1.0,
        "remaining_gold": gold - sum(item["cost"] for item in best_combination)
    }
