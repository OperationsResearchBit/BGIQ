# simcore

Win / tie / loss odds for two Battlegrounds boards, keywords only (taunt, Divine Shield, venomous,
reborn, windfury). Standard library only: it imports nothing from the rest of bgtools.

    from bgtools.simcore import Fighter, estimate
    odds = estimate([Fighter(5, 5)], [Fighter(3, 3)])    # .win .tie .loss .unmodeled .method .runs

Exact odds when the fight is small, otherwise simulated fights (fixed seed, so the same boards give the
same numbers). Card effects (deathrattles, start of combat, buffs) are not modeled; `unmodeled` counts
the minions that have one. No damage to the hero yet.

Try it without the rest of the app:

    python bgtools\simcore\preview.py --you "5/5 taunt, 3/2 shield" --opp "4/4, 2/2 venom"
    python bgtools\simcore\preview.py                 asks for the two boards
    python bgtools\simcore\test_simcore.py            10 checks
