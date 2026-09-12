import os
import time

def inject_mock_match_data():
    """
    Simulates high-precision, raw Blizzard Power.log packets to feed 
    the updated Event-Driven 4-Module BGIQ Engine.
    """
    base_logs_dir = os.path.expandvars(r"%PROGRAMFILES(X86)%\Hearthstone\Logs")
    print("⏳ Scanning for active session folder path...")
    
    if not os.path.exists(base_logs_dir):
        print("❌ System Error: Could not locate Hearthstone Logs directory tree.")
        return
        
    all_contents = [os.path.join(base_logs_dir, d) for d in os.listdir(base_logs_dir)]
    subfolders = [d for d in all_contents if os.path.isdir(d)]
    
    if not subfolders:
        print("❌ Error: No timestamped match folders exist yet. Please launch Hearthstone once.")
        return
        
    latest_folder = max(subfolders, key=os.path.getmtime)
    target_file = os.path.join(latest_folder, "Power.log")
    
    print(f"📡 Found active target file: {target_file}")
    print("🚀 Commencing real-time automated packet injection in 2 seconds...")
    time.sleep(2)
    
    # ADVANCED EVENT-DRIVEN PACKETS MATCHING YOUR GAME_FILTERS REGEX
    mock_log_lines = [
        # Step 1: Initialize a brand-new turn shopping phase boundary
        "D 18:00:00.000 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STEP value=MAIN_START_TRIGGERS",
        
        # Step 2: Inject dynamic automated health & armor tags under player=1 (Scraped Hands-Free!)
        "D 18:00:01.000 GameState.DebugPrintPower() - TAG_CHANGE Entity=MossDew#1919 tag=HEALTH value=35 player=1",
        "D 18:00:01.200 GameState.DebugPrintPower() - TAG_CHANGE Entity=MossDew#1919 tag=ARMOR value=5 player=1",
        
        # Step 3: Inject enemy tavern tier under player=2 to fuel Lethal Risk Models
        "D 18:00:01.400 GameState.DebugPrintPower() - TAG_CHANGE Entity=Enemy#2026 tag=PLAYER_TECH_LEVEL value=4 player=2",
        
        # Step 4: Stream collectible minions to player=14 (Bob's Tavern) in valid slots (zonePos 1-6)
        "D 18:00:02.000 GameState.DebugPrintPower() - FULL_ENTITY - Creating ID=2107 CardID=BG29_888 [entityName=Glim Guardian id=2107 zone=PLAY zonePos=1 cardId=BG29_888 player=14]",
        "D 18:00:03.500 GameState.DebugPrintPower() - FULL_ENTITY - Creating ID=2108 CardID=BG29_800 [entityName=Cord Puller id=2108 zone=PLAY zonePos=2 cardId=BG29_800 player=14]",
        "D 18:00:05.000 GameState.DebugPrintPower() - FULL_ENTITY - Creating ID=2109 CardID=BG29_999 [entityName=Patient Scout id=2109 zone=PLAY zonePos=3 cardId=BG29_999 player=14]",
        
        # Step 5: Simulate an APM action change -- pick up a minion into your hand!
        "D 18:00:06.000 GameState.DebugPrintPower() - ACTION_START zone=HAND zone from -> PLAY [entityName=Glim Guardian id=2107 player=1]",
        
        # Step 6: Transition turn cleanly into combat round to trigger your move accuracy scorecards
        "D 18:00:08.000 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STEP value=MAIN_COMBAT"
    ]
    
    # CRUCIAL: Using share-compliant open structures to append safely while terminal tailers look at it
    with open(target_file, "a", encoding="utf-8") as f:
        for line in mock_log_lines:
            f.write(line + "\n")
            f.flush() # Force write bypasses Windows caching delays completely
            print(f"📥 Successfully injected text: {line[:80]}...")
            time.sleep(1.5) # Space out actions so you can watch your dashboard calculate live!
            
    print("\n✅ Simulation Test complete! Check your Streamlit browser window dashboard.")

if __name__ == "__main__":
    inject_mock_match_data()
