import os
import time
import json
import urllib.request  # Built-in: Bypasses pip download blocks
import tkinter as tk
from threading import Thread
from solver import optimize_turn

# CURRENT APPLICATION VERSION STRING
__version__ = "v1.0.0" 

class HearthstoneOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BGIQ Overlay HUD")
        
        # Transparent pass-through HUD styling constraints
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.geometry("450x250+50+50") 
        self.root.overrideredirect(True)    
        
        # Main UI label panel text element
        self.label = tk.Label(self.root, text="Checking for data updates...", 
                              font=("Arial", 14, "bold"), fg="#00FF00", bg="black", justify="left")
        self.label.pack(expand=True, fill="both")
        
        # Trigger the update checker immediately before starting the logging loop
        Thread(target=self.check_for_updates, daemon=True).start()
        self.root.mainloop()

    def check_for_updates(self):
        """
        Queries the GitHub API to check for balance changes or tool software updates.
        """
        # REPLACE 'yourusername' WITH YOUR ACTUAL GITHUB ACCOUNT USERNAME STRING!
        api_url = "https://github.com"
        
        # Simulate clean header parameters to safeguard API calls
        request = urllib.request.Request(
            api_url, 
            headers={"User-Agent": "BGIQ-Overlay-Update-Checker", "Accept": "application/vnd.github+json"}
        )
        
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", __version__)
                
                if latest_version != __version__:
                    update_msg = f"⚠️ UPDATE AVAILABLE!\n\nCurrent: {__version__} ➔ Latest: {latest_version}\n\nDownload fresh build at:\://ngithub.com\n\nBooting HUD anyway in 5s..."
                    self.label.config(text=update_msg, fg="#FFCC00")
                    time.sleep(5)  # Pause to let the gamer read the balance notification
                    
        except Exception as e:
            # Silent fallback: If offline or API fails, don't crash, just log and continue
            print(f"Update check skipped: {str(e)}")
            
        # Transition back into the standard game monitoring function loops
        self.label.config(text="Waiting for Bob's Turn...", fg="#00FF00")
        self.watch_game_logs()

    def watch_game_logs(self):
        """
        Monitors Hearthstone's log file path for active shop and board states.
        """
        log_path = os.path.expandvars(r"%PROGRAMFILES(X86)%\Hearthstone\Logs\Power.log")
        mock_shop = [
            {"name": "Aureate Laureate", "value": 6},
            {"name": "Buzzing Vermin", "value": 2},
            {"name": "Crackling Cyclone", "value": 5}
        ]
        mock_board = [{"name": "Weak Starter Minion", "value": 1}]
        
        while True:
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    f.seek(0, 2)
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(0.5)
                            continue
                        if "Tavern" in line or "BACON" in line:
                            decision = optimize_turn(gold=10, spaces=0, shop_minions=mock_shop, board_minions=mock_board)
                            display_text = f"✨ OPTIMAL PLAYS:\n\n🛒 BUY: {', '.join(decision['buys'])}\n💰 SELL: {', '.join(decision['sells'])}"
                            self.label.config(text=display_text, fg="#00FF00")
            else:
                decision = optimize_turn(gold=10, spaces=0, shop_minions=mock_shop, board_minions=mock_board)
                self.label.config(text=f"📊 PROTOTYPE MODES:\n\n🛒 BUY: {', '.join(decision['buys'])}\n💰 SELL: {', '.join(decision['sells'])}")
                time.sleep(5)

if __name__ == "__main__":
    HearthstoneOverlay()
