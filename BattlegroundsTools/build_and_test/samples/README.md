# samples

Made-up data for trying the tools without Hearthstone. It is not real game data.

- `fake_cards.json`: a few invented cards in HearthstoneJSON format.
- `sample_power.log`: a short invented game that uses those cards (an unfinished game, so it does not touch your saved history).

Draw its screen from the repo root:

```powershell
python -m bgtools track --replay build_and_test\samples\sample_power.log --cards-file build_and_test\samples\fake_cards.json
```
