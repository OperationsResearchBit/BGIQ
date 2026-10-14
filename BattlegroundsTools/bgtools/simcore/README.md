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

Exact odds when the fight is small, otherwise simulated fights. Card effects (deathrattles, start of
combat, buffs) are not modeled; `unmodeled` counts the minions that have one. No damage to the hero yet.
