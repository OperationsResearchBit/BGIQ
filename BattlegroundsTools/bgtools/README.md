# Battlegrounds Tools

Two small terminal tools for Hearthstone Battlegrounds. Both use only the Python standard library, so there is nothing to install besides Python.

| File | What it does |
|---|---|
| `bgminions.py` | Browse every Battlegrounds minion (name, tier, stats, type, card text). Filter and search. |
| `bgtrack.py` | Live tracker. Reads Hearthstone's log while you play and shows the tavern, your board and your hand. |
| `bgui.py` | Shared colors and layout used by both tools. Nothing to run. |

Keep all the files in the same folder. `bgtrack.py` uses the card loading code in `bgminions.py`, and both use `bgui.py` for colors.

The tools use colors, box lines and a colored badge for each tavern tier (T1 to T7). They look best in **Windows Terminal** or any modern terminal. If colors look wrong or you prefer plain text, add `--no-color` or set the `NO_COLOR` environment variable.

## Folder layout

```
BattlegroundsTools\
  run_bgtools.bat          <- double-click this to launch
  bgtools\
    bgminions.py           minion browser and card data loading
    bgtrack.py             live tracker (reads Power.log)
    bgui.py                shared colors and layout
    README.md              this file
```

## Easiest way: the launcher

Double-click `run_bgtools.bat`. A menu opens:

1. Live tracker (start a Battlegrounds game first)
2. Browse minions (interactive prompt)
3. Show the minions for one tier
4. Refresh card data (do this after a game patch)
5. Open this README

The launcher runs everything from inside the `bgtools` folder, so you can also open a terminal there and run the commands below directly.

## Requirements

- Python 3.8 or newer (check with `python --version`)
- Internet connection the first time you run either tool (it downloads card data once and caches it)
- For the live tracker: Hearthstone installed on the same computer, with logging turned on (see below)

## Quick start (Windows PowerShell)

```powershell
cd C:\path\to\bgtools
python bgminions.py -i      # browse minions
python bgtrack.py           # live tracker (start a Battlegrounds game first)
```

On macOS/Linux use `python3` instead of `python`.

## bgminions.py: browse minions

```powershell
python bgminions.py                  # everything, grouped by tavern tier
python bgminions.py -t 3             # only tier 3
python bgminions.py -r beast         # only beasts
python bgminions.py -s deathrattle   # search name and card text
python bgminions.py -t 4 -r mech     # filters can be combined
python bgminions.py -x               # hide Timewarped variants
python bgminions.py -i               # interactive mode (keeps running)
python bgminions.py --refresh        # re-download card data (after a patch)
python bgminions.py --no-color       # plain output
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
python bgminions.py -i
bg> -t 3
bg> -t 4 -r mech
bg> taunt
bg> q
```

Typing a plain word searches names and card text. Type `q` to quit.

## bgtrack.py: live tracker

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
python bgtrack.py
```

The screen redraws as the game changes and shows:

- **Tavern (Bob)**: the minions in the shop
- **Your board**: your minions with current stats
- **Your hand**: minions you are holding

Golden minions are marked "Golden". Press **Ctrl+C** to stop.

You do not need to restart it between games. It switches to the newest log automatically.

### Options

```powershell
python bgtrack.py --log "C:\Program Files (x86)\Hearthstone\Logs\Hearthstone_2026_10_02_20_23_59\Power.log"
python bgtrack.py --logs-dir "D:\Games\Hearthstone\Logs"
```

| Option | Meaning |
|---|---|
| `--log PATH` | Read one specific `Power.log` (no automatic switching) |
| `--logs-dir PATH` | Hearthstone's `Logs` folder, if it is not in the default location |
| `--no-color` | Turn off colors |

Default log folders: `C:\Program Files (x86)\Hearthstone\Logs` on Windows, `/Applications/Hearthstone/Logs` on macOS.

### Reading the debug footer

The last lines show `bob_ctrl`, `you_ctrl` and how many minions are in play per player ID. If a section is empty when it shouldn't be, those numbers help show why.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Terminate batch job (Y/N)?" after pressing Ctrl+C in the launcher | Answer `N` to go back to the menu, or `Y` to close it |
| `python` is not recognized | Install Python from python.org and tick "Add Python to PATH", or try `py` or `python3` |
| `Could not load card data` | Check your internet connection, or download `https://api.hearthstonejson.com/v1/latest/enUS/cards.json` in a browser and run `python bgminions.py --file cards.json` |
| `Couldn't find Power.log` | Logging is off or the game is installed elsewhere. Check `log.config`, then use `--logs-dir` or `--log` |
| Tracker stays on "Reading ..." | It is catching up on a big log. Progress lines appear every 200,000 lines. Wait a little |
| Tracker shows empty sections | No game with a shop is running yet, or the newest log is from a finished game. Start a game |
| New minions show as `? CardID` | Card data is out of date. Run `python bgminions.py --refresh` |
| Tavern section empty during a game | Check the debug footer. It may be combat, or the shop may be under a different player ID |

## How it works

- Card data comes from [HearthstoneJSON](https://hearthstonejson.com) and is cached at `~/.cache/bgminions/cards.json`.
- `bgminions.py` keeps cards that are minions with a tavern tier, drops golden duplicates, and cleans up the card text.
- `bgtrack.py` reads Hearthstone's `Power.log` as it grows, tracks each game entity's card, zone and owner, and looks the cards up in the card data.
- Neither tool modifies the game or sends anything anywhere. They only read files.
