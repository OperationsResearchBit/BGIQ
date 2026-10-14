# Battlegrounds Tools (v2.1)

Terminal tools for Hearthstone Battlegrounds. Everything uses only the Python standard library, so there is nothing to install besides Python.

| Command | What it does |
|---|---|
| `python -m bgtools` | Opens the menu (the same menu `run_bgtools.bat` shows). |
| `python -m bgtools track` | Live tracker. Reads Hearthstone's log while you play and shows your status, board type, the tavern, your board and your hand. Summarizes each finished game. |
| `python -m bgtools simpreview` | Only the fight odds from your real game: `my lethal / win / tie / loss / opp lethal` in two rows, with colored numbers. Double-click `simpreview.bat`. See [Fight odds](#fight-odds). |
| `python -m bgtools combatsim` | Type two boards and get win / tie / loss, no game needed. |
| `python -m bgtools comps` | Checks your `data\comps.txt` against the game's card names. |
| `python -m bgtools stats` | Your results from saved games: average placement, top-4 rate, recent form, placements by build, cold-streak warning. |
| `python -m bgtools minions` | Browse every Battlegrounds minion (name, tier, stats, type, card text). Filter and search. |
| `python -m bgtools targets` | Search minions and add them to your triple-target list. |
| `python -m bgtools demo` | Draw the tracker screen from made-up data (for working on the UI). |

The tools use colors, box lines and a colored badge for each tavern tier (T1 to T7). They look best in **Windows Terminal** or any modern terminal. If colors look wrong or you prefer plain text, add `--no-color` or set the `NO_COLOR` environment variable.

## Folder layout

```
bgtools\
  README.md   run_bgtools.bat   simpreview.bat
  pyproject.toml   .gitignore
  docs\          LICENSE   CHANGELOG.md   ARCHITECTURE.md
  data\          triple_targets.txt (yours)   history.json (created by the tracker)
  bgtools\       the program (see docs\ARCHITECTURE.md); bgtools\simcore is the fight calculator
```

Your own files live in `data\`. If you run the `.exe`, `data\` sits next to it. Set the `BGTOOLS_DATA_DIR` environment variable to keep them somewhere else.

License: [AGPL-3.0](docs/LICENSE). Changes by version: [CHANGELOG](docs/CHANGELOG.md). How the code is organized: [ARCHITECTURE](docs/ARCHITECTURE.md).

## Easiest way: the launcher

Double-click `run_bgtools.bat`. A menu opens:

1. Live tracker (start a Battlegrounds game first)
2. Browse minions (interactive prompt)
3. Show the minions for one tier
4. Refresh card data (do this after a game patch)
5. My triple targets (search minions, add favorites)
6. Edit `triple_targets.txt` in Notepad
7. Open this README

Press **Ctrl+C** in the tracker to come back to the menu.

## Requirements

- Python 3.8 or newer (check with `python --version`). Tested on 3.12 only so far.
- Internet connection the first time you run either tool (it downloads card data once and caches it)
- For the live tracker: Hearthstone installed on the same computer, with logging turned on (see below)

## Quick start (Windows PowerShell)

```powershell
cd C:\path\to\bgtools
python -m bgtools minions -i   # browse minions
python -m bgtools track        # live tracker (start a Battlegrounds game first)
```

On macOS/Linux use `python3` instead of `python`.

## Browse minions: `python -m bgtools minions`

```powershell
python -m bgtools minions                  # everything, grouped by tavern tier
python -m bgtools minions -t 3             # only tier 3
python -m bgtools minions -r beast         # only beasts
python -m bgtools minions -s deathrattle   # search name and card text
python -m bgtools minions -t 4 -r mech     # filters can be combined
python -m bgtools minions -x               # hide Timewarped variants
python -m bgtools minions -i               # interactive mode (keeps running)
python -m bgtools minions --refresh        # re-download card data (after a patch)
python -m bgtools minions --no-color       # plain output
```

| Option | Meaning |
|---|---|
| `-t`, `--tier` | Tavern tier, 1 to 7 |
| `-r`, `--race` | Minion type, e.g. beast, mech, murloc, demon, dragon, elemental, pirate, undead, naga, quilboar |
| `-s`, `--search` | Text to look for in the name or card text (quote multiple words) |
| `-x`, `--no-timewarped` | Hide the "Timewarped ..." variants |
| `-i`, `--interactive` | Stay open and keep answering queries |
| `--refresh` | Download fresh card data |
| `--file PATH` | Use a local `cards.json` instead of downloading |
| `--no-color` | Turn off colored output |

### Interactive mode

```
python -m bgtools minions -i
bg> -t 3
bg> -t 4 -r mech
bg> taunt
bg> q
```

Typing a plain word searches names and card text. Type `q` to quit.

## Live tracker: `python -m bgtools track`

### 1. Turn on Hearthstone logging (one time)

Create a file named `log.config` in:

- Windows: `%LOCALAPPDATA%\Blizzard\Hearthstone\`
- macOS: `~/Library/Preferences/Blizzard/Hearthstone/`

with this content:

```
[Power]
LogLevel=1
FilePrinting=True
ConsolePrinting=False
ScreenPrinting=False
Verbose=True
```

Restart Hearthstone after creating it.

### 2. Run it

Start a Battlegrounds game, then in a terminal:

```powershell
python -m bgtools track
```

The screen redraws as the game changes. Press **Ctrl+C** to stop. You do not need to restart it between games. It switches to the newest log automatically.

### data\comps.txt

Builds you want to play, one per line: `Comp name | Tribe | Core card, Core card, Core card | note`. The tracker shows your two closest comps and marks tavern minions that are a missing core card. A file with example lines in comments is created the first time you run the tracker. Card names must match the game's names (run `python -m bgtools comps` to check). Keep it current after each patch; the tool does not know which comps are strong.

### What the screen shows (new in this version)

- `You: 27 hp · place 3/8   Next: <hero> (19 hp)` appears when your health can be read. Yellow at 20 or less, red at 10 or less.
- `Lobby: ...` lists the minion types in this game. It is certain after five types have shown up in a tavern; before that, `Lobby so far (n/5)` and `Probably out`.
- `Comp: <name> 2/3  in tavern now: ...` shows how close you are to a comp from `comps.txt`.

- The status line draws your tavern tier and gold as bars. `(behind)`, `(on pace)` or `(ahead)` compares your tier with a typical range for the turn. It is a guide, not a rule.
- `Pairs (one more = golden)` lists cards you hold two copies of. A tavern minion that completes one is marked `completes a triple`.

### What the screen shows

```
Turn 7  ·  Tavern 4  ·  Gold 6/9
Board: Beast 3 · Mech 1  →  Beast build
Triple targets T4: Card A, Card B

══ TAVERN (4) ══
 1  T3  Minion A     4/4   Beast   ✓ fits Beast
 2  T4  Minion B     3/6   Mech    ★ triple target: scales when golden
 ...
══ YOUR BOARD (5)  42 atk + 38 hp = 80 ══
 ...
══ YOUR HAND (1) ══
 ...
```

- **Status line:** turn, tavern tier and gold. A value that cannot be read shows `?`.
- **Board line:** how many minions of each type you have, and a label: `Beast build` (a clear majority of one type), `Leaning Murloc` (two or more of a type), `Mixed types` (three or more types with no more than two of any), or `No clear type yet`. Minions that count as every type are shown as `All`.
- **Triple targets line:** the minions from `triple_targets.txt` that are in your current tavern tier.
- **Tavern (Bob):** one line per minion. At most two get a mark:
  - `★ triple target` : the minion is in `triple_targets.txt`, with your reason if you wrote one.
  - `✓ fits <type>` : the minion matches your board's main type, or counts as every type.
  - Triple-target marks take priority over type-fit marks.
- **Your board:** your minions, with total attack + total health in the header. This is raw stats only.
- **Your hand:** minions you are holding.
- Golden minions are marked `GOLD`.

### When a game ends

A **MATCH COMPLETE** panel appears with:

- your final board strength (total attack + health)
- your final placement
- how that board compares with the average of your last 3 to 10 games

The comparison starts once 3 earlier games are saved. Before that the panel says how many are saved. Finished games are stored in `data\history.json`. Delete that file to reset your history. A game replayed from the same log is not saved twice.

"Final board" means the last non-empty board the tracker saw before the game ended, sampled once per turn change.

### data\triple_targets.txt

List minions worth tripling, one per line as `Card name | short reason`. Lines starting with `#` are ignored, and upper/lower case does not matter.

```
# Card name | reason
Example Minion | scales when golden
```

The file starts empty, so no triple targets show until you add some. The tracker reloads the file when it changes. Card names must match the game's names. Names that do not match a Battlegrounds minion are ignored.

### Options

```powershell
python -m bgtools track --text
python -m bgtools track --debug
python -m bgtools track --log "C:\Program Files (x86)\Hearthstone\Logs\Hearthstone_2026_10_02_20_23_59\Power.log"
python -m bgtools track --logs-dir "D:\Games\Hearthstone\Logs"
```

| Option | Meaning |
|---|---|
| `--text` | Show card text under each minion (falls back to one line each if the window is too short) |
| `--debug` | Show the debug footer |
| `--log PATH` | Read one specific `Power.log` (no automatic switching) |
| `--replay PATH` | Read a saved `Power.log` from the top, draw its final screen once, then exit (no waiting for a game) |
| `--logs-dir PATH` | Hearthstone's `Logs` folder, if it is not in the default location |
| `--no-color` | Turn off colors |

Default log folders: `C:\Program Files (x86)\Hearthstone\Logs` on Windows, `/Applications/Hearthstone/Logs` on macOS.

### Fitting the window

The tracker never prints more lines than your window has rows, so the screen does not scroll. If the window is short, it drops detail in steps: card text, then the boxed title, then blank lines, then the hand list. Long lines are cut off at the window edge instead of wrapping. Making the window taller or wider shows more.

### Reading the debug footer

With `--debug`, the last lines show:

- `bob_ctrl` and `you_ctrl`: the player IDs the tracker found for the shop and for you, and how many minions are in play per player ID. If a section is empty when it shouldn't be, these help show why.
- the raw `TURN`, `TECH`, `RES`, `USED` and `TEMP` values behind the status line, and the player entity found.
- how many games are saved, how many turn samples this game has, and whether the game has been marked complete.
- `combat odds:` the game step and what the fight estimate has seen so far (see [Fight odds](#fight-odds)).

## Fight odds

During combat the tracker shows `Estimate: win % tie % loss %` under your hero line, and `Last fight: ...` through the next shop phase. It plays the two boards against each other with the keywords `taunt`, Divine Shield, venomous, reborn and windfury. Small fights are calculated exactly; bigger ones are simulated.

- **`python -m bgtools simpreview`** (or double-click `simpreview.bat`) follows the game like `track` but draws only the odds, and saves nothing of yours:

  ```
  fight in progress   (Ctrl+C to stop)
  my lethal   win    tie    loss   opp lethal
     --       62%     5%    33%        --
  2 of 13 minions have effects not modeled · medium confidence
  ```

  The labels sit on top and each number is centered under its label. Win is green, tie yellow and loss red; a `0%` or `--` is dim grey, so only real chances light up. Before a fight every number is `--`, and after it the top line says `last fight`. Lethal (damage to a hero) is not calculated yet, so it shows `--`. The last line appears only when the estimate skips something: it counts minions, not effects, and says how far to trust the numbers (high, medium or low confidence). Options: `--log`, `--logs-dir`, `--replay`, `--cards-file`, `--debug`. `simpreview.bat PATH\Power.log` (or dragging a log onto the file) shows the last fight of that log.
- **`python -m bgtools combatsim --you "5/5 taunt, 3/2 shield" --opp "4/4, 2/2 venom"`** works out a fight between two boards you type in. Keywords: `taunt`, `shield` (`ds`), `venom`, `reborn`, `windfury` (`wf`), `effect`. Add `--brief` for just the likeliest result.
- **`--debug`** on `track` or `simpreview` also writes `data\combat_odds_log.txt`: one line each time a fight's game steps, board sizes or estimate change. It is there to find out why a fight got no estimate.
- The calculator is the `bgtools\simcore` folder. It uses only the standard library and imports nothing from the rest of the app.

Limits: card effects (deathrattles, start of combat, buffs) are not modeled; the screen says how many minions have one. The estimate is only made at the log's `MAIN_START` step, and that timing has not been confirmed on a real game yet.

## Known limits

The v2 additions read tags from `Power.log`. They have been checked against real games and read correctly. How each value is worked out, and how to compare it with the game (use `--debug`):

- **Turn number:** shown as the game's turn counter divided by two (rounded up). Compare it with the in-game turn using `--debug`.
- **Gold:** shown as current/total from the resource tags.
- **Placement:** read from your hero's leaderboard tag. If the tag is missing, the panel shows `Placement: ?`.
- **Board totals:** buffs may not all appear in the attack and health tags.
- **Type labels:** the labels are simple rules on the types on your board. They are not the game's own definition of a build.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognized | Install Python from python.org and tick "Add Python to PATH", or try `py` or `python3` |
| `Could not load card data` | Check your internet connection, or download `https://api.hearthstonejson.com/v1/latest/enUS/cards.json` in a browser and run `python -m bgtools minions --file cards.json` |
| `Couldn't find Power.log` | Logging is off or the game is installed elsewhere. Check `log.config`, then use `--logs-dir` or `--log` |
| Tracker stays on "Reading ..." | It is catching up on a big log. Progress lines appear every 200,000 lines. Wait a little |
| Tracker shows empty sections | No game with a shop is running yet, or the newest log is from a finished game. Start a game |
| New minions show as `? CardID` | Card data is out of date. Run `python -m bgtools minions --refresh` |
| Tavern section empty during a game | Run with `--debug`. It may be combat, or the shop may be under a different player ID |
| Status line shows `?` | A tag could not be read. Run with `--debug` to see the raw values |
| Screen repeats or scrolls | Make the window taller. If it still happens, run with `--debug` and note your window size |
| No MATCH COMPLETE panel | The game may not have reported completion. Check the last footer line with `--debug` |
| Triple targets line says "none listed" | Add cards to `triple_targets.txt`, using names that match the game's |

## How it works

- Card data comes from [HearthstoneJSON](https://hearthstonejson.com) and is cached at `~/.cache/bgminions/cards.json`.
- `file_adapters/cards_hsjson.py` keeps cards that are minions with a tavern tier, drops golden duplicates, and cleans up the card text.
- `file_adapters/log_tail.py` follows Hearthstone's `Power.log` as it grows, and `core/game_state.py` tracks each game entity's card, zone and owner and looks the cards up in the card data.
- None of the tools modify the game or sends anything anywhere. They only read files. The tracker writes only `data\history.json`.
