import pulp

def optimize_turn(gold, spaces, shop_minions, board_minions):
    """
    Solves the optimal combination of buys and sells using an LP Matrix.
    """
    prob = pulp.LpProblem("Hearthstone_Turn", pulp.LpMaximize)
    
    # Define Binary Choice Actions (1 = Execute, 0 = Skip)
    buy_vars = pulp.LpVariable.dicts("Buy", range(len(shop_minions)), cat='Binary')
    sell_vars = pulp.LpVariable.dicts("Sell", range(len(board_minions)), cat='Binary')
    
    # Objective Function: Maximize expected net value 
    # (Shop Card Value minus sacrificed Board Card Value)
    prob += (
        pulp.lpSum([shop_minions[i]['value'] * buy_vars[i] for i in range(len(shop_minions))]) -
        pulp.lpSum([board_minions[j]['value'] * sell_vars[j] for j in range(len(board_minions))])
    )
    
    # Constraints
    # 1. Gold Limit: Total gold spent cannot exceed current bank + sold card returns
    prob += (pulp.lpSum([3 * buy_vars[i] for i in range(len(shop_minions))]) <= 
             gold + pulp.lpSum([1 * sell_vars[j] for j in range(len(board_minions))]))
             
    # 2. Board Space Limit: Initial space + freed slots must fit your buys
    prob += (pulp.lpSum([buy_vars[i] for i in range(len(shop_minions))]) <= 
             spaces + pulp.lpSum([1 * sell_vars[j] for j in range(len(board_minions))]))
             
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    # Format Results
    buys = [shop_minions[i]['name'] for i in range(len(shop_minions)) if buy_vars[i].varValue == 1]
    sells = [board_minions[j]['name'] for j in range(len(board_minions)) if sell_vars[j].varValue == 1]
    
    return {"buys": buys, "sells": sells}
