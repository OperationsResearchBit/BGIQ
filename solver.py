import pulp

def optimize_turn(payload):
    # Extract variables from Google Sheet JSON
    gold = payload['current_gold']
    spaces = payload['free_spaces']
    shop = payload['shop']
    
    # Initialize the Optimization Problem
    prob = pulp.LpProblem("Hearthstone_Turn", pulp.LpMaximize)
    
    # Create Binary Decision Variables (1 = Buy, 0 = Do Not Buy)
    # Using index as key to handle duplicate minion names in the shop
    buy_choices = pulp.LpVariable.dicts("Buy", range(len(shop)), cat='Binary')
    
    # Objective Function: Maximize Total Net Value (Raw Stats + Synergy Buffs)
    prob += pulp.lpSum([
        (shop[i]['stats'] + shop[i]['synergy_buff']) * buy_choices[i] 
        for i in range(len(shop))
    ])
    
    # Constraint 1: Gold Limit
    prob += pulp.lpSum([shop[i]['cost'] * buy_choices[i] for i in range(len(shop))]) <= gold
    
    # Constraint 2: Board Space Limit
    prob += pulp.lpSum([buy_choices[i] for i in range(len(shop))]) <= spaces
    
    # Solve the system
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    # Extract Results
    recommendations = []
    for i in range(len(shop)):
        if buy_choices[i].varValue == 1:
            recommendations.append(shop[i]['name'])
            
    return {"buy_list": recommendations}
