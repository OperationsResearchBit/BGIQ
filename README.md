# 🧠 BGIQ: Hearthstone Battlegrounds Linear Programming Solver

**BGIQ (Battlegrounds Intelligence Quantum Engine)** is an advanced, real-time analytics companion tool built explicitly for competitive **Hearthstone Battlegrounds Solo and Duos** players. 

BGIQ turns **Hearthstone Battlegrounds** turn decisions into a pure mathematical optimization matrix. By applying **Integer Linear Programming (ILP)** rules via the Simplex/Branch-and-Bound algorithms, this utility tracks your gold and board state to calculate the absolute highest-value path of buying and selling minions on your machine.

Unlike traditional tracking tools that simply simulate random combat outcomes, BGIQ acts as a **local analytical solver engine** (similar to how chess engines operate). It intercepts real-time text data logs directly from your Hearthstone client, parses board state vectors, and executes custom **Integer Linear Programming (ILP)** algorithms to calculate absolute optimal turn trajectories within strict resource frontiers.

Choose between a casual, zero-install **Google Sheets interactive template** or a live, fully automated **Desktop HUD Game Overlay**.

---

## 📺 Watch Live Development & High-MMR Gameplay
I stream high-MMR gameplay lobbies and live engine optimization updates over on Twitch! 
👉 **Follow [kangaroo_jo on Twitch](https://twitch.tv/kangaroo_jo)** to ask questions about the algorithm, discuss math models, or hang out with the community!

---

## 📈 Option 1: The Interactive Google Sheets Solver (Zero-Install)

Perfect for players who want to simulate or test complex turn setups without running executable files locally. The mathematical engine runs entirely inside your browser sandbox for free.

### 🚀 Quick Start Setup Instructions
1. **Get the Template:** Open the [BGIQ Master Google Sheet Template](https://docs.google.com/spreadsheets/d/1bbX7_2kBLQcj3aORT6YQIjcCQ5Pq7RTUSiCFcRwmkyQ/copy).
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

---

## 🛠️ Quick Installation & Setup

### For General Users (Standalone Executable)
1. Head over to the [GitHub Releases](https://github.com) tab panel.
2. Download the standalone executable asset pack: **`BGIQ_Pro_Engine.exe`**.
3. Double-click the file to boot. BGIQ will launch a silent background web host thread and automatically open an interactive dashboard page directly inside your default web browser at `http://localhost:8501`.
4. *(Optional)* Paste your custom log path directly into the sidebar panel if you installed Hearthstone on an alternate hard drive location.

### For Developers (Running From Source Code)
Ensure you possess a Python 3.9+ environment configured, then run:

```bash
# 1. Clone the project tree folder paths
git clone https://github.com/OperationsResearchBit/
cd BGIQ

# 2. Install the necessary visualization dashboard libraries
pip install streamlit

# 3. Boot up the local tracker script server loop
python -m streamlit run desktop_overlay.py
```

---

## 🧪 Running Diagnostic Stress Tests
You can verify that your data parser channels, accuracy matrices, and Streamlit columns are fully synchronized without entering a live game lobby by executing our standalone diagnostic tool:

```bash
python test_reader.py
```
This script will bypass Windows caching blocks and manually stream mock minion packets directly down your active `Power.log` file, allowing you to observe your browser recommendations and performance metrics live instantly.

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

## 🚀 Key Engine Features

### 1. Multi-Column Real-Time Grid Layout
BGIQ splits your monitoring matrix into a sleek, three-column professional workspace designed for deep strategic focus:
* **🛒 Column 1: Tavern Scanner** — Automatically hooks into your client file stream, scans card registry metadata tokens, applies dynamic tribe scaling multipliers, and reveals estimated gold valuations.
* **🎯 Column 2: Optimal Strategy** — Calculates high-yield turn deployment paths, automatically combining Tavern Tier leveling and elite card purchases into synchronized combinations.
* **💰 Column 3: Risk Management** — Continuously monitors friendly board boundaries. If your layout hits a maximum `7/7` capacity, it invokes value-trading filters to explicitly calculate which minion to liquidate to unlock maximum power.

### 📈 2. Real-Time Performance Accuracy Grading
The second your recruitment buying turn transitions into combat phase, the engine computes an in-memory evaluation matrix comparing your actual turn layout choices against the engine's absolute perfect efficiency ceiling. It outputs a **Post-Turn Accuracy Percentage** (`👑 BGIQ ACCURACY: 98.7%`) right at the top header block to flag strategic blunders in real time.

### 📡 3. Zero-Lag Chunk Streaming Pipeline
Built using a low-latency 4096-byte chunk processing reader, the logging engine completely bypasses default Windows file lock bottlenecks. It streams active data frames at a **20ms refresh threshold**, giving you instantaneous dashboard results the exact millisecond you press the **Reroll** button.

### 🛡️ 4. 100% Blizzard TOS Compliant
BGIQ follows strict gaming security guidelines. It relies purely on text data lines already publicly generated on your hard drive. It **never** hooks into internal memory addresses, never modifies game process memory blocks, and never performs code injection, making it completely invisible and safe from anti-cheat system flags.

---

## 🗺️ Structural Architecture Layout
The codebase is re-architected across a strict, scalable modular block setup:
* **`app.py`** — The native environment launcher entry hook wrapper.
* **`desktop_overlay.py`** — The professional frontend client UI framework.
* **`log_parser.py`** — The unbuffered, real-time chunk data processing stream engine.
* **`solver.py`** — The core combinatorial ILP calculation matrix.
* **`style.css`** — The modular visual styling dashboard layout script.

---

## 🤝 Contributing & Support
Contributions, feature suggestions, or custom lookup dictionary definitions are always welcome! Feel free to open an issue patch or submit a pull request down our main development branch tree. 

If you appreciate the mathematical approach, don't forget to **Star the repository** and swing by the [Twitch stream](https://twitch.tv/kangaroo_jo) to give me feedback!

## 🤝 Roster Sync Updates
The active minion card values and keyword parameters are maintained by open-source repository contributions! If a balancing patch lands or a card stat value shifts:
1. Fork this repository.
2. Adjust the mapping definitions inside `solver.py` or submit improvements to the data parsing loops.
3. Open a **Pull Request** to merge your layout changes into the main production tree.

Distributed under the AGPL3 License. Feel free to fork, customize, or integrate into your own tracking companion projects!


