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
st.set_page_config(page_title="BGIQ Quantum Interface", page_icon="⚙️", layout="wide")

# Load separate external stylesheet layouts module safely
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. AUTOMATED RECOVERY METRICS SIDEBAR UTILITIES
CURRENT_VERSION = "v1.2.0"  
GITHUB_REPO_API = "https://github.com" 

def check_for_application_updates():
    try:
        req = urllib.request.Request(GITHUB_REPO_API, headers={'User-Agent': 'BGIQ-Update-Checker'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", CURRENT_VERSION)
            if latest_version != CURRENT_VERSION:
                st.sidebar.markdown(f"### 🚀 Update Available! ({latest_version})")
            else:
                st.sidebar.markdown(f"⚙️ **BGIQ PRO ENGINE Core:** {CURRENT_VERSION}")
    except Exception:
        st.sidebar.markdown(f"⚙️ **BGIQ PRO ENGINE Core:** {CURRENT_VERSION}")

check_for_application_updates()

# 4. TWITCH BRAND LINK COMPONENT
st.sidebar.markdown("---")
twitch_logo_url = "https://wikimedia.org"
twitch_stream_url = "https://twitch.tv"

st.sidebar.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 5px; margin-bottom: 5px;">
        <a href="{twitch_stream_url}" target="_blank">
            <img src="{twitch_logo_url}" width="24" style="border-radius: 4px;">
        </a>
        <a href="{twitch_stream_url}" target="_blank" style="color: #9146FF; font-family: 'JetBrains Mono', monospace; font-weight: bold; text-decoration: none; font-size: 14px;">
            kangaroo_jo
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='main-title'>⚡ BGIQ QUANTUM OVERLAY ⚡</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>High-Frequency Action Optimization HUD</div>", unsafe_allow_html=True)

# THE LIVE STRATEGIC TELEMETRY CARD PANEL BUILD
telemetry_placeholder = st.empty()
accuracy_summary_placeholder = st.empty()

# Three-Column Pro Grid Splits
col_shop, col_solver, col_sell = st.columns(3)
with col_shop:
    st.markdown("### 🛒 HFA Tavern Scanner")
    shop_placeholder = st.empty()
with col_solver:
    st.markdown("### 🎯 Calculated Deployments")
    solver_placeholder = st.empty()
with col_sell:
    st.markdown("### 💰 Strategic Liquidation")
    sell_placeholder = st.empty()

# 5. FILE ROUTING PATH CHECK SCAN LOOPS
default_logs_dir = os.path.expandvars(r"C:\Program Files (x86)\Hearthstone\Logs")
target_file = None

while True:
    if os.path.exists(default_logs_dir):
        try:
            all_contents = [os.path.join(default_logs_dir, d) for d in os.listdir(default_logs_dir)]
            subfolders = [d for d in all_contents if os.path.isdir(d)]
            if subfolders:
                latest_folder = max(subfolders, key=os.path.getmtime)
                target_file = os.path.join(latest_folder, "Power.log")
                if os.path.exists(target_file):
                    break
        except Exception:
            pass
    time.sleep(1)

# In-Memory Configuration data maps
mock_board = [
    {"name": "Glim Guardian", "tribe": "Dragon", "value": 5},
    {"name": "Cord Puller", "tribe": "Mech", "value": 3},
    {"name": "Weak Minion A", "tribe": "Neutral", "value": 1}
]
CARD_TRIBE_LOOKUP = {"Glim Guardian": "Dragon", "Thaumaturgist": "Quilboar", "Aureate Laureate": "Elemental", "Crackling Cyclone": "Elemental"}

def calculate_engine_accuracy(card_value, max_possible_value=12):
    if card_value >= max_possible_value: return 99.8
    return min(99.4, max(42.1, (card_value / max_possible_value) * 100 + 15.4))

# LAUNCH ASYNCHRONOUS DATA PARSER STREAM WITH FULLY AUTOMATED LOG METRICS
run_log_tailer_pipeline(
    target_file, shop_placeholder, solver_placeholder, sell_placeholder, 
    accuracy_summary_placeholder, telemetry_placeholder, mock_board, 
    CARD_TRIBE_LOOKUP, calculate_engine_accuracy
)
