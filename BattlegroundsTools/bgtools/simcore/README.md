# simcore

Win / tie / loss odds for two Battlegrounds boards, keywords only (taunt, Divine Shield, venomous,
reborn, windfury). Standard library only: it imports nothing from the rest of the app.

**Put it here:** copy the `simcore` folder into `bgtools\bgtools\`, next to `file_adapters`, and put
`simpreview.bat` in the same place.

**Try it** (double-click `simpreview.bat`, or from a terminal):

    simpreview.bat --you "5/5 taunt, 3/2 shield" --opp "4/4, 2/2 venom"
    simpreview.bat                       asks for the two boards, blank line to quit

**Check it:** `python simcore\test_simcore.py` (10 tests, no app needed).

**From code:**

    from simcore import Fighter, estimate
    odds = estimate([Fighter(5, 5)], [Fighter(3, 3)])    # odds.win, .tie, .loss, .unmodeled, .method

Exact odds when the fight is small, otherwise simulated fights. Summon deathrattles are played (always
simulated, never solved exactly). Other card effects (damage or buff deathrattles, start of combat) are not
modeled; `unmodeled` counts the minions that have one.

Hero damage and lethal: give the heroes' tavern tiers and each minion's tier.

    from simcore import Fighter, Summon, estimate
    o = estimate([Fighter(5, 5, tier=3)], [Fighter(3, 3, tier=2)], you_tier=4, opp_tier=3)
    o.p_kill(7)          # chance the fight takes a 7-health hero to 0 (here 1.0)
    o.avg_deal()         # average damage you deal; o.deal / o.take hold the full tables

A summon deathrattle is `Fighter(1, 1, deathrattle=(Summon(1, 3, 3),))` (one 3/3 token) or
`Summon(1, tier=4)` (one random tier 4 minion, drawn from `pool=[Fighter, ...]`).
