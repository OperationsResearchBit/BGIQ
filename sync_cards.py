import json
import urllib.request

def update_local_card_database():
    """
    Queries the live hsbg.cards REST API, filters for active minions,
    and updates your local 'cards_data.json' reference engine cleanly.
    """
    url = "https://hsbg.cards"
    print("🔄 Connecting to live Battlegrounds API database index...")
    
    try:
        # Request data stream using web request headers to prevent scraping firewalls
        req = urllib.request.Request(url, headers={'User-Agent': 'BGIQ-Data-Sync-Manager'})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = json.loads(response.read().decode())
            
            # Navigate nested JSON mapping styles safely
            cards_list = raw_data.get("cards", raw_data.get("data", raw_data))
            if isinstance(cards_list, dict):
                cards_list = list(cards_list.values())
                
            synchronized_cards = {}
            
            for card in cards_list:
                # CRUCIAL FILTERS: Drop legacy cards, tokens, spells, and removed minions
                if (card.get("name") and 
                    card.get("tier") and 
                    not card.get("isLegacy") and 
                    not card.get("removed") and 
                    card.get("type") == "MINION"):
                    
                    name = card["name"]
                    attack = int(card.get("attack", 0))
                    health = int(card.get("health", 0))
                    
                    # Store data mapped by name for immediate dictionary lookups
                    synchronized_cards[name] = {
                        "value": attack + health,  # Flat baseline stats sum for LP optimization matrix
                        "tier": card["tier"],
                        "tribe": card.get("tribe", card.get("race", "Neutral"))
                    }
            
            # Save the clean current-patch dataset to a local JSON file
            with open("cards_data.json", "w", encoding="utf-8") as f:
                json.dump(synchronized_cards, f, indent=4, ensure_ascii=False)
                
            print(f"✅ Success! {len(synchronized_cards)} current-season minions synced to cards_data.json.")
            
    except Exception as e:
        print(f"❌ Failed to reach update server: {str(e)}")

if __name__ == "__main__":
    update_local_card_database()
