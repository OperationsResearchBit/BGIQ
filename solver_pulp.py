import pulp

def solve_hearthstone_turn(shop_minions, current_gold, board_spaces_free):
    # 1. Initialize the Integer Linear Programming Problem
    prob = pulp.LpProblem("Hearthstone_Turn_Optimization", pulp.LpMaximize)
    
    # 2. Decision Variables (1 if buy, 0 if skip)
    buy_vars = pulp.LpVariable.dicts("Buy", shop_minions.keys(), cat='Binary')
    
    # 3. Objective Function: Maximize expected stat value
    prob += pulp.lpSum([shop_minions[m]['stats'] * buy_vars[m] for m in shop_minions])
    
    # 4. Constraints
    prob += pulp.lpSum([3 * buy_vars[m] for m in shop_minions]) <= current_gold, "Gold_Constraint"
    prob += pulp.lpSum([buy_vars[m] for m in shop_minions]) <= board_spaces_free, "Board_Space_Constraint"
    
    # 5. Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    # Return actions where the decision variable equals 1
    return [m for m in shop_minions if buy_vars[m].varValue == 1]
