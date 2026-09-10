import os
import time
import tkinter as tk
from threading import Thread
from solver import optimize_turn

class HearthstoneOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HS BG LP Solver Overlay")
        
        # Make the GUI canvas pass-through, transparent, and locked to the top layer
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.geometry("400x200+50+50") # Width x Height + X position + Y position
        self.root.overrideredirect(True)    # Removes standard OS borders/headers
        
        # HUD Text Panel Window
        self.label = tk.Label(self.root, text="Waiting for Bob's Turn...", 
                              font=("Arial", 16, "bold"), fg="#00FF00", bg="black", justify="left")
        self.label.pack(expand=True, fill="both")
        
        # Start looking at game file events on a parallel background worker thread
        Thread(target=self.watch_game_logs, daemon=True).start()
        self.root.mainloop()

    def watch_game_logs(self):
        """
        Monitors Hearthstone's log file path for active shop and board states.
        """
        # Standard local log file directory route on Windows installations
        log_path = os.path.expandvars(r"%PROGRAMFILES(X86)%\Hearthstone\Logs\Power.log")
        
        # Fallback placeholder defaults for prototyping visualization rules
        mock_shop = [
            {"name": "Aureate Laureate", "value": 6},
            {"name": "Buzzing Vermin", "value": 2},
            {"name": "Crackling Cyclone", "value": 5}
        ]
        mock_board = [{"name": "Weak Starter Minion", "value": 1}]
        
        while True:
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    # Jump directly to the end of the file to capture live turn events
                    f.seek(0, 2)
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(0.5)
                            continue
                            
                        # When the log registers a Battlegrounds setup choice event block
                        if "Tavern" in line or "BACON" in line:
                            # 1. Run optimization engine logic
                            decision = optimize_turn(gold=10, spaces=0, shop_minions=mock_shop, board_minions=mock_board)
                            
                            # 2. Refresh UI display metrics instantly on your game layout canvas
                            display_text = f"✨ OPTIMAL PLAYS:\n\n🛒 BUY: {', '.join(decision['buys'])}\n💰 SELL: {', '.join(decision['sells'])}"
                            self.label.config(text=display_text)
            else:
                # If game isn't active, show fallback mock data loop calculations for testing
                decision = optimize_turn(gold=10, spaces=0, shop_minions=mock_shop, board_minions=mock_board)
                self.label.config(text=f"📊 PROTOTYPE MODES:\n\n🛒 BUY: {', '.join(decision['buys'])}\n💰 SELL: {', '.join(decision['sells'])}")
                time.sleep(5)

if __name__ == "__main__":
    HearthstoneOverlay()
