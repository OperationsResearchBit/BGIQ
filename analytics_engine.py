import time
import streamlit as st

def compute_real_time_apm(actions_count, turn_start_time):
    """
    Tracks and compiles the current live Actions Per Minute (APM) vector metrics.
    """
    elapsed_time = time.time() - turn_start_time
    if elapsed_time > 1.0:
        return int((actions_count / elapsed_time) * 60)
    return 0

def render_quantum_telemetry_hud(telemetry_placeholder, current_apm, total_effective_life, decision):
    """
    Renders the re-engineered esports dark-grid telemetry card panel layout 
    featuring live APM tracking, survival bounds, and team strategy pivot alerts.
    """
    # 1. COMBO STRATEGY PIVOT MESSAGE COMPILATION
    if decision.get("trigger_pivot"):
        pivot_status = f"🔥 STRATEGIC PIVOT RECOMMENDATION: FORCE DETECTED -> TRANSITION TO {decision['pivot_target_tribe'].upper()}"
    else:
        pivot_status = "🟢 BOARD BALANCED // MAINTAINING TRIBE ALLOCATION STATE"
        
    # 2. LETHAL SAFETY MARGIN COLOR OVERRIDES
    safety_color = "#00FF66" if decision.get("lethal_safety_status") == "100% SAFE" else "#EF4444"
    
    # 3. STREAM THE HTML CARD LAYOUT TO STREAMLIT
    with telemetry_placeholder.container():
        st.markdown(
            f"""
            <div class='metric-card' style='border: 1px solid #1E293B;'>
                <div style='display: flex; justify-content: space-between; font-weight: bold; font-size: 14px;'>
                    <span style='color: #38BDF8;'>🚀 RATE: <span style='color:#FFF;'>{current_apm} APM</span> | ❤️ HP+ARMOR: <span style='color:#FFF;'>{total_effective_life}</span></span>
                    <span style='color: {safety_color};'>🎯 SURVIVAL RISK MODEL: {decision.get("lethal_safety_status", "UNKNOWN")}</span>
                </div>
                <div style='margin-top: 10px; font-size: 12px; color: #A855F7; font-weight: bold;'>
                    {pivot_status}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
