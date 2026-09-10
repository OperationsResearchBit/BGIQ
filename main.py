from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pulp

app = FastAPI()

# Define the exact JSON structure coming from your Google Sheet
class Minion(BaseModel):
    name: str
    stats: int
    synergy_buff: int
    cost: int

class TurnData(BaseModel):
    current_gold: int
    free_spaces: int
    shop: List[Minion]

@app.post("/optimize")
def optimize_turn(data: TurnData):
    gold = data.current_gold
    spaces = data.free_spaces
    shop = data.shop
    
    # Initialize optimization model
    prob = pulp.LpProblem("Hearthstone_Turn", pulp.LpMaximize)
    buy_choices = pulp.LpVariable.dicts("Buy", range(len(shop)), cat='Binary')
    
    # Objective function (Maximize total combined stats)
    prob += pulp.lpSum([
        (shop[i].stats + shop[i].synergy_buff) * buy_choices[i] 
        for i in range(len(shop))
    ])
    
    # Mathematical constraints
    prob += pulp.lpSum([shop[i].cost * buy_choices[i] for i in range(len(shop))]) <= gold
    prob += pulp.lpSum([buy_choices[i] for i in range(len(shop))]) <= spaces
    
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    # Gather winning recommendations
    recommendations = []
    for i in range(len(shop)):
        if buy_choices[i].varValue == 1:
            recommendations.append(shop[i].name)
            
    return {"buy_list": recommendations}
