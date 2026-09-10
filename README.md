# 🧠 BGIQ: Hearthstone Battlegrounds Linear Programming Solver

BGIQ turns **Hearthstone Battlegrounds** turn decisions into a pure mathematical optimization matrix. By applying **Integer Linear Programming (ILP)** rules via the Simplex/Branch-and-Bound algorithms, this utility tracks your gold and board state to calculate the absolute highest-value path of buying and selling minions on your machine.

Choose between a casual, zero-install **Google Sheets interactive template** or a live, fully automated **Desktop HUD Game Overlay**.

---

## 📈 Option 1: The Interactive Google Sheets Solver (Zero-Install)

Perfect for players who want to simulate or test complex turn setups without running executable files locally. The mathematical engine runs entirely inside your browser sandbox for free.

### 🚀 Quick Start Setup Instructions
1. **Get the Template:** Open the [BGIQ Master Google Sheet Template](https://google.com) (Replace this with your spreadsheet sharing link, ensuring it ends with `/copy`).
2. **Authorize the Automation Script:** 
   * Click **BG Solver** ➔ **Optimize Current Turn** in the top menu bar.
   * Google will prompt an authorization alert box. Click *Advanced* ➔ *Go to Untitled project (unsafe)* ➔ *Allow*. This step is safe; it enables the spreadsheet to calculate the matrix locally.
3. **Sync Latest Card Data:** Click **BG Solver** ➔ **🔄 Sync Latest Card Data** to connect to the active card database and download the current season's minion roster automatically.
4. **Input & Play:** Select your shop cards from the dropdown menus in Column A. Change your `Current Gold` or `Free Board Spaces` values to watch the engine write optimized plays into Column E instantly!

---

## 🖥️ Option 2: The Automated Desktop HUD Game Overlay (Python)

Supercharge your game by running a lightweight overlay that sits on top of your live match window. It monitors your local game logs in real-time, extracts active shop options, and flashes the optimal choices directly onto your screen automatically.

### 🔧 Step 1: Force Hearthstone to Stream Game Logs
To allow the overlay to read your board actions, you must enable logging in the game engine settings:
1. Press `Windows Key + R` to open the Windows Run box, paste this path, and hit Enter:
   ```text
   %localappdata%\Blizzard\Hearthstone
   ```
2. Right-click an empty space inside that directory, select **New** ➔ **Text Document**, and name it exactly:
   ```text
   log.config
   ```
   *(Ensure you delete the hidden `.txt` file extension at the very end so it saves cleanly as a configuration type!)*
3. Double-click your new `log.config` file to open it in Notepad, paste the tracking rules below, and **Save**:
   ```ini
   [Power]
   LogLevel=1
   ConsolePrinting=True
   ScreenPrinting=False

   [Zone]
   LogLevel=1
   ConsolePrinting=True
   ScreenPrinting=False
   ```

### 🕹️ Step 2: Boot Up the Automated Application Overlay
Ensure you have Python installed on your computer. Open your terminal or command prompt inside this repository directory and execute these commands:

```bash
# 1. Download the optimization matrix dependencies
pip install -r requirements.txt

# 2. Launch the transparent pass-through HUD over your desktop
python desktop_overlay.py
```

A transparent, green-text canvas tracker will float directly over your screen, feeding active match sequences cleanly into `solver.py` and updating your optimal pathways live as you play!

---

## 🧮 How the Mathematical Matrix Model Works

The underlying core engine uses the `PuLP` optimization library to treat a tavern turn as a constrained resource allocation problem:

```text
Maximize:   Z = ∑ (Shop_Minion_Value_i × Buy_i) - ∑ (Board_Minion_Value_j × Sell_j)

Subject To: 
  1. Gold Limit:   ∑ (3 × Buy_i) ≤ Current_Gold + ∑ (1 × Sell_j)
  2. Board Space:  ∑ (1 × Buy_i) ≤ Free_Spaces + ∑ (1 × Sell_j)
  3. Integrality:  Buy_i, Sell_j ∈ {0, 1}  (Binary choices)
```

The mathematical formulas also apply complex custom value weights to mechanical keyword variables (such as multiplying card coefficients dynamically by `1.5x` for **Divine Shield** properties), allowing numbers to accurately reflect real in-game combat strength.

---

## 🤝 Contributing & Roster Sync Updates
The active minion card values and keyword parameters are maintained by open-source repository contributions! If a balancing patch lands or a card stat value shifts:
1. Fork this repository.
2. Adjust the mapping definitions inside `solver.py` or submit improvements to the data parsing loops.
3. Open a **Pull Request** to merge your layout changes into the main production tree.

Distributed under the MIT License. Feel free to fork, customize, or integrate into your own tracking companion projects!
