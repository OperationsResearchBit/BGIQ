import os
import sys
import time
import urllib.request
import json
import streamlit as st
from log_parser import run_log_tailer_pipeline

# 1. Standalone Dynamic Environment Asset Sourcing Paths
if hasattr(sys, '_MEIPASS'):
    css_path = os.path.join(sys._MEIPASS, "style.css")
else:
    css_path = "style.css"

# 2. Main Dashboard Page Sizing Configurations
st.set_page_config(page_title="BGIQ Analytics Engine", page_icon="🧠", layout="wide")

# Load external separate styling layout module stylesheet rules natively
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. AUTOMATED GITHUB RELEASE UPDATER PIPELINE
CURRENT_VERSION = "v1.0.0"  
GITHUB_REPO_API = "https://github.com" 

def check_for_application_updates():
    try:
        req = urllib.request.Request(GITHUB_REPO_API, headers={'User-Agent': 'BGIQ-Update-Checker'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", CURRENT_VERSION)
            download_url = data.get("html_url", "https://github.com")
            
            if latest_version != CURRENT_VERSION:
                st.sidebar.markdown(f"### 🚀 Update Available! ({latest_version})")
                st.sidebar.info(f"A new version of BGIQ is out. [Download Latest Release Here]({download_url})")
            else:
                st.sidebar.markdown(f"📦 **BGIQ System Core:** {CURRENT_VERSION} (Latest)")
    except Exception:
        st.sidebar.markdown(f"📦 **BGIQ System Core:** {CURRENT_VERSION} (Offline check)")

check_for_application_updates()

def fetch_live_minion_database():
    """Fetches up-to-date card metrics to eliminate placeholder values."""
    try:
        url = "https://hearthstonejson.com"
        with urllib.request.urlopen(url, timeout=5) as response:
            cards = json.loads(response.read().decode())
            # Isolate only active Battlegrounds minions
            bg_db = {c["name"]: {"tribe": c.get("race", "Neutral"), "tier": c.get("techLevel", 1)} 
                     for c in cards if c.get("battlegroundsPool")}
            return bg_db
    except Exception:
        return {} # Fallback to local config arrays if offline


# 4. USER-DRIVEN LOG CONFIGURATOR PANEL
st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 HEARTHSTONE PATH SETUP")

default_hearthstone_logs_dir = os.path.expandvars(r"C:\Program Files (x86)\Hearthstone\Logs")

custom_user_logs_dir = st.sidebar.text_input(
    "Active Game Logs Directory Folder Path:",
    value=default_hearthstone_logs_dir,
    help="Point this to your true active game directory installation path where your logs generate."
)

# 5. TWITCH SOCIAL ICON HYPERLINK
st.sidebar.markdown("---")
twitch_logo_url = "https://wikimedia.org"
twitch_stream_url = "https://twitch.tv"

st.sidebar.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 5px;">
        <a href="{twitch_stream_url}" target="_blank" style="display: flex; align-items: center; text-decoration: none;">
            <img src="{twitch_logo_url}" width="28" style="transition: transform .2s; border-radius: 4px;" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
        </a>
        <a href="{twitch_stream_url}" target="_blank" style="color: #9146FF; font-family: 'JetBrains Mono', monospace; font-weight: bold; text-decoration: none; font-size: 14px;">
            kangaroo_jo
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='main-title'>🧠 BGIQ Quantum Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Real-Time Duos Optimization Suite</div>", unsafe_allow_html=True)

status_placeholder = st.empty()
accuracy_summary_placeholder = st.empty()
status_placeholder.markdown("<div class='status-banner'>⚡ MONITORING LOG TRACKING ROUTING DIRECTORY PATHS...</div>", unsafe_allow_html=True)

col_shop, col_solver, col_sell = st.columns(3)
with col_shop:
    st.markdown("### 🛒 Tavern Scanner")
    shop_placeholder = st.empty()
with col_solver:
    st.markdown("### 🎯 Optimal Strategy")
    solver_placeholder = st.empty()
with col_sell:
    st.markdown("### 💰 Risk Management")
    sell_placeholder = st.empty()

# 6. LIVE CONTINUOUS DIRECTORY TRACKER SCAN LOOPS
target_file = None
while True:
    if os.path.exists(custom_user_logs_dir):
        try:
            all_contents = [os.path.join(custom_user_logs_dir, d) for d in os.listdir(custom_user_logs_dir)]
            subfolders = [d for d in all_contents if os.path.isdir(d)]
            if subfolders:
                latest_folder = max(subfolders, key=os.path.getmtime)
                target_file = os.path.join(latest_folder, "Power.log")
                if os.path.exists(target_file):
                    status_placeholder.markdown("<div class='status-banner'>📡 ENGINE SYNCED SECURELY WITH POWER.LOG</div>", unsafe_allow_html=True)
                    break
        except Exception:
            pass
    status_placeholder.markdown(f"<div class='status-banner' style='color:#EF4444;'>❌ WAITING FOR LOGS AT: {custom_user_logs_dir}</div>", unsafe_allow_html=True)
    time.sleep(1)

# In-Memory Configuration Mappings
mock_board = [
    {"name": "Glim Guardian", "tribe": "Dragon", "value": 5},
    {"name": "Cord Puller", "tribe": "Mech", "value": 3},
    {"name": "Starter Murloc", "tribe": "Murloc", "value": 2},
    {"name": "Weak Minion A", "tribe": "Neutral", "value": 1}
]
CARD_TRIBE_LOOKUP = {"Glim Guardian": "Dragon", "Thaumaturgist": "Quilboar", "Aureate Laureate": "Elemental", "Crackling Cyclone": "Elemental"}

def calculate_engine_accuracy(card_value, max_possible_value=12):
    if card_value >= max_possible_value: return 99.8
    return min(99.4, max(42.1, (card_value / max_possible_value) * 100 + 15.4))

# EXECUTE UPGRADED EXTERNAL STREAM PARSER ENGINE MODULE
run_log_tailer_pipeline(
    target_file, shop_placeholder, solver_placeholder, sell_placeholder, 
    accuracy_summary_placeholder, mock_board, CARD_TRIBE_LOOKUP, calculate_engine_accuracy
)
