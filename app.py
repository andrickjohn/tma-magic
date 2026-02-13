#!/usr/bin/env python3
# TMA Magic Black Box - Streamlit Frontend
"""
Premium financial extraction interface.
Non-blocking design using subprocess workers.
"""

import html
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
from datetime import datetime
import tempfile
import os
import streamlit.components.v1 as components

import streamlit as st
import pandas as pd

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config, get_temp_dir

# Page configuration
st.set_page_config(
    page_title="TMA Magic Black Box",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Dark Theme CSS
# ... (imports remain the same)
CUSTOM_CSS = """
<style>
/* Import premium font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styles */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    font-family: 'Inter', sans-serif;
    color: #ffffff !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Text Visibility Improvements */
p, h1, h2, h3, h4, h5, h6, span, div, label, .stMarkdown {
    color: #e2e8f0 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

/* Radio Button Improvements for Readability */
.stRadio > label {
    font-size: 1.1rem;
    font-weight: 600;
    color: #a5b4fc !important;
}
.stRadio div[role='radiogroup'] > label {
    background: rgba(255, 255, 255, 0.05);
    padding: 10px;
    border-radius: 8px;
    margin-right: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Main container glassmorphism */
.main-container {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* Blinking Dots Animation */
@keyframes blink {
    0% { opacity: 0.2; }
    20% { opacity: 1; }
    100% { opacity: 0.2; }
}

.blink-dot {
    animation-name: blink;
    animation-duration: 1.4s;
    animation-iteration-count: infinite;
    animation-fill-mode: both;
    font-size: 1.5rem;
    font-weight: 900;
}

.blink-dot:nth-child(2) { animation-delay: 0.2s; }
.blink-dot:nth-child(3) { animation-delay: 0.4s; }

/* Status Bar */
.status-bar {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.cost-display {
    font-family: 'Courier New', monospace;
    font-weight: 700;
    color: #fca5a5 !important;
    background: rgba(0,0,0,0.3);
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Code block styling - READABLE */
code, pre, .stCode, [data-testid="stCode"] {
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    background: #1a1a2e !important;
}
[data-testid="stCode"] pre {
    color: #e0e0e0 !important;
    font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace !important;
}

/* File uploader styling - BRIGHT & READABLE */
[data-testid="stFileUploader"] {
    border: 2px solid rgba(255,255,255,0.5) !important;
    border-radius: 12px !important;
    padding: 10px !important;
    background: rgba(0,0,0,0.3) !important;
}
[data-testid="stFileUploader"] section {
    background: transparent !important;
}
[data-testid="stFileUploader"] section > div {
    color: #ffffff !important;
}
[data-testid="stFileUploader"] small {
    color: #a5b4fc !important;
}
[data-testid="stFileUploader"] button {
    background: rgba(255,255,255,0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}
/* Animation Keyframes */
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

@keyframes pump-iron {
    0% { transform: scale(1) rotate(0deg); }
    50% { transform: scale(1.15) rotate(-10deg); }
    100% { transform: scale(1) rotate(0deg); }
}

.animate-bounce {
    animation: bounce 0.6s infinite ease-in-out;
    display: inline-block;
}

.animate-pump {
    animation: pump-iron 0.8s infinite ease-in-out;
    display: inline-block;
    font-size: 3rem; 
    margin-bottom: 0.5rem;
}
</style>
"""


def inject_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #a5b4fc 0%, #c084fc 50%, #f0abfc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 30px rgba(167, 139, 250, 0.5);
        ">✨ TMA Magic Black Box</h1>
        <p style="font-size: 1.2rem; opacity: 0.8; color: #e2e8f0;">
            Premium Financial Data Extraction
        </p>
    </div>
    """, unsafe_allow_html=True)


def check_job_status(job_id: str) -> dict:
    """Poll for job status."""
    status_file = get_temp_dir() / f"tma_status_{job_id}.json"
    
    if status_file.exists():
        try:
            data = json.loads(status_file.read_text())
            # Ensure "message" is always present
            if "message" not in data:
                data["message"] = "Processing..."
            return data
        except json.JSONDecodeError:
            return {"state": "processing", "progress": 0, "message": "Reading status..."}
    
    return {"state": "pending", "progress": 0, "message": "Initializing..."}


def submit_job(file_path: Path, mode: str, api_key: str = "") -> str:
    """Submit extraction job to subprocess."""
    job_id = str(uuid.uuid4())[:8]
    job_file = get_temp_dir() / f"tma_job_{job_id}.json"
    
    job_data = {
        "job_id": job_id,
        "file_path": str(file_path),
        "mode": mode,
        "api_key": api_key
    }
    
    job_file.write_text(json.dumps(job_data))
    
    
    # Spawn detached subprocess with logging
    backend_script = Path(__file__).parent / "backend_processor.py"
    log_file = get_temp_dir() / f"tma_log_{job_id}.txt"
    
    with open(log_file, "w") as log:
        subprocess.Popen(
            [sys.executable, str(backend_script), str(job_file)],
            start_new_session=True,
            stdout=log,
            stderr=subprocess.STDOUT
        )
    
    return job_id


def format_excel_value(val):
    """Format matching Excel requirements: blank if None/Empty, $0 if 0."""
    if val is None or val == "":
        return ""
    try:
        f = float(val)
        if f == 0:
            return "$0"
        return f"${f:,.0f}"
    except (ValueError, TypeError):
        return ""


def generate_excel_string(years_data, pad=False):
    """Generate the exact tab-separated string for Excel pasting.
    pad=True: adds spaces for visual alignment (st.code)
    pad=False: clean TSV for Excel
    """
    lines = []
    
    # ALWAYS show these 3 years (matching Excel format)
    target_years = [2024, 2023, 2022]
    
    # Build a lookup by year
    year_lookup = {y.get("year"): y for y in years_data}
    
    # Helper to format row
    def row(c1, c2, c3, c4=None):
        if pad:
            if c4 is not None:
                return f"{c1:<24}\t{c2:<18}\t{c3:<18}\t{c4:<18}"
            return f"{c1:<24}\t{c2:<18}\t{c3:<18}"
        else:
            if c4 is not None:
                return f"{c1}\t{c2}\t{c3}\t{c4}"
            return f"{c1}\t{c2}\t{c3}"

    # 1. Income Statement
    lines.append(row("Income Statement", "Revenue", "Net Income", "Depreciation"))
    for yr in target_years:
        y = year_lookup.get(yr, {})
        rev = format_excel_value(y.get("revenue"))
        net = format_excel_value(y.get("net_income"))
        dep = format_excel_value(y.get("depreciation"))
        lines.append(row(str(yr), rev, net, dep))
    
    lines.append("")  # Blank line
    
    # 2. Balance Sheet
    lines.append(row("Balance Sheet", "Assets", "Liabilities"))
    for yr in target_years:
        y = year_lookup.get(yr, {})
        asset = format_excel_value(y.get("assets"))
        liab = format_excel_value(y.get("liabilities"))
        lines.append(row(str(yr), asset, liab))
        
    lines.append("")  # Blank line
    
    # 3. Cash Flow
    lines.append(row("Cash Flow", "TOTAL CPLTD", "")) # Empty 3rd col for alignment logic
    for yr in target_years:
        y = year_lookup.get(yr, {})
        cpltd = format_excel_value(y.get("total_cpltd"))
        lines.append(row(str(yr), cpltd, ""))
        
    return "\n".join(lines)


def render_results(data: dict, unique_key: str):
    """Display extraction results - simple and clean."""
    if not data or not data.get("years"):
        st.warning("No data extracted.")
        return
        
    years_data = data.get("years", [])
    if not years_data:
        return

    # Generate the Excel-ready string
    excel_text = generate_excel_string(years_data)
    
    st.success("✅ Extraction Complete")
    
    st.markdown("**📋 Ready for Excel** - Click copy button in top right:")
    
    # Display as code block for easy copying
    st.code(excel_text, language="text")

def get_funny_status(progress: float):
    """Return a funny status message based on progress."""
    if progress < 0.1: return "Reading pixels..."
    if progress < 0.3: return "Combobulating data..."
    if progress < 0.5: return "Consulting the oracle..."
    if progress < 0.7: return "Crunching numbers..."
    if progress < 0.9: return "Polishing results..."
    return "Almost there..."


def format_currency(value) -> str:
    """Format number as currency."""
    if value is None:
        return "—"
    try:
        v = float(value)
        if v < 0:
            return f"(${abs(v):,.0f})"
        return f"${v:,.0f}"
    except (ValueError, TypeError):
        return "—"


def render_settings():
    """Render mode and model selectors (always visible, side-by-side)."""
    config = get_config()
    
    # API Key in a compact input at the top
    api_key = st.text_input(
        "🔑 OpenAI API Key",
        value=config.openai_api_key,
        type="password",
        help="Required for AI extraction mode"
    )
    if api_key != config.openai_api_key:
        config.openai_api_key = api_key
        st.success("API key saved!")
    
    st.markdown("")
    
    # Two columns for Mode and Model
    mode_col, model_col = st.columns(2)
    
    # --- LEFT: Extraction Mode ---
    with mode_col:
        st.markdown("##### ⚡ Mode")
        
        mode_options = ["hybrid", "regex_only", "ai_only"]
        mode_labels = [
            "✨ Hybrid",
            "⚡ Regex Only",
            "🧠 AI Only"
        ]
        
        current_index = mode_options.index(config.extraction_mode) if config.extraction_mode in mode_options else 0
        
        selected_mode_label = st.radio(
            "Mode",
            options=mode_labels,
            index=current_index,
            label_visibility="collapsed"
        )
        
        mode = mode_options[mode_labels.index(selected_mode_label)]
        if mode != config.extraction_mode:
            config.set("extraction_mode", mode)
    
    # --- RIGHT: AI Model ---
    with model_col:
        st.markdown("##### 🧠 Model")
        
        model_options = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        model_labels = [
            "🚀 GPT-4o",
            "🐢 GPT-4 Turbo",
            "🐇 GPT-3.5"
        ]
        
        current_model = config.get("ai_model", "gpt-4o")
        curr_model_idx = model_options.index(current_model) if current_model in model_options else 0
        
        selected_model_label = st.radio(
            "Model",
            options=model_labels,
            index=curr_model_idx,
            label_visibility="collapsed"
        )
        
        sel_model = model_options[model_labels.index(selected_model_label)]
        if sel_model != current_model:
            config.set("ai_model", sel_model)
    
    return mode, api_key


def render_worker_panel():
    """Render TMA BossMan Overlord and 4 Minion workers status panel."""
    
    # Initialize minion state if not exists
    if "minions" not in st.session_state:
        st.session_state.minions = {
            i: {"status": "idle", "file": None, "progress": 0, "eta": 0, "cost": 0.0, "job_id": None}
            for i in range(4)
        }
    
    minions = st.session_state.minions
    jobs = st.session_state.get("jobs", {})
    
    # Calculate overall stats - use PROGRESS to detect activity, not status field
    working_minions = [m for m in minions.values() if m["progress"] > 0 and m["progress"] < 1.0]
    completed_minions = [m for m in minions.values() if m["progress"] >= 1.0]
    assigned_minions = [m for m in minions.values() if m.get("file")]
    
    total_progress = sum(m["progress"] for m in minions.values()) / max(len(assigned_minions), 1) if assigned_minions else 0
    total_eta = max((m["eta"] for m in minions.values()), default=0)
    total_cost = sum(m["cost"] for m in minions.values())
    
    # Fun boss status messages - based on ACTUAL progress
    import random
    if not assigned_minions:
        boss_status = "😎 Chillin'"
    elif len(completed_minions) == len(assigned_minions) and len(assigned_minions) > 0:
        boss_status = "✅ All Done!"
    elif total_progress < 0.25:
        boss_status = random.choice(["🏃 Cracking Whip!", "👀 Supervising...", "📋 Checking Work"])
    elif total_progress < 0.5:
        boss_status = random.choice(["💪 Keep It Moving!", "🔥 On Fire!", "⚡ Full Steam!"])
    elif total_progress < 0.75:
        boss_status = random.choice(["🎯 Almost There!", "👊 Push Through!", "🚀 Turbo Mode!"])
    else:
        boss_status = random.choice(["🏁 Final Stretch!", "🎉 Wrapping Up!", "✨ Polishing!"])
    
    pct = int(total_progress * 100)
    
    # === BOSSMAN BOX (centered, with progress bar) ===
    # Animate "Pump Iron" if any minions are assigned and not all done
    boss_anim_class = "animate-pump" if assigned_minions and len(completed_minions) < len(assigned_minions) else ""
    
    # Build Boss HTML string
    boss_html = f'<div style="background: linear-gradient(135deg, rgba(167,139,250,0.2), rgba(139,92,246,0.1)); border: 2px solid rgba(167,139,250,0.5); border-radius: 12px; padding: 1rem 1.5rem; margin: 1rem 0; text-align: center;"> <div style="font-size: 1.8rem; font-weight: 900; color: #a78bfa; margin-bottom: 0.5rem;"> 👔 TMA BossMan Overlord </div> <!-- PUMPING IRON GRAPHIC --> <div class="{boss_anim_class}">💪</div> <div style="font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-bottom: 0.75rem;"> {boss_status} </div> <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap; margin-bottom: 0.75rem;"> <div style="text-align: center;"> <div style="font-size: 1rem; color: rgba(255,255,255,0.6);">Progress</div> <div style="font-size: 1.3rem; font-weight: 600; color: #10b981;">{pct}%</div> </div> <div style="text-align: center;"> <div style="font-size: 1rem; color: rgba(255,255,255,0.6);">ETA</div> <div style="font-size: 1.3rem; font-weight: 600; color: #60a5fa;">{int(total_eta)}s</div> </div> <div style="text-align: center;"> <div style="font-size: 1rem; color: rgba(255,255,255,0.6);">Cost</div> <div style="font-size: 1.3rem; font-weight: 600; color: #fca5a5;">${total_cost:.5f}</div> </div> </div> <!-- Overall Progress Bar --> <div style="background: rgba(255,255,255,0.1); border-radius: 8px; height: 12px; width: 100%; overflow: hidden;"> <div style="background: linear-gradient(90deg, #a78bfa, #c4b5fd); height: 100%; width: {pct}%; transition: width 0.3s;"></div> </div> </div>'
    st.markdown(boss_html, unsafe_allow_html=True)
    
    # === MINIONS SECTION ===
    st.markdown('<div style="font-size: 1.3rem; font-weight: 700; color: #94a3b8; margin-bottom: 0.75rem; text-align: center;">🤖 Minions</div>', unsafe_allow_html=True)
    
    # Minion names and emojis
    minion_names = ["🔧 Minion 1", "⚡ Minion 2", "🔥 Minion 3", "💎 Minion 4"]
    status_emojis = {
        "idle": "💤",
        "reading": "📖",
        "chewing": "🍔", 
        "processing": "⚙️",
        "thinking": "🧠",
        "done": "✅",
        "error": "❌"
    }
    
    # Minion rows with larger fonts
    for i, name in enumerate(minion_names):
        m = minions[i]
        progress = m["progress"]
        pct = int(progress * 100)  # Calculate pct first for display
        
        # Derive status from PROGRESS percentage, not stale status field
        if not m.get("file"):
            status = "idle"
        elif pct >= 100:  # Use pct for cleaner comparisons
            status = "done"
        elif pct < 15:
            status = "reading"
        elif pct < 35:
            status = "chewing"
        elif pct < 85:
            status = "processing"
        else:
            status = "thinking"
        
        emoji = status_emojis.get(status, "💤")
        
        # Apply BOUNCE animation if active (working states only)
        # Excludes 'done' and 'idle' and 'error'
        anim_class = ""
        if status in ["reading", "chewing", "processing", "thinking"]:
            anim_class = "animate-bounce"
            
        eta = int(m["eta"])
        cost = m["cost"]
        file_display = m.get("file", "—")[:18] + "..." if m.get("file") and len(m.get("file", "")) > 18 else (m.get("file") or "—")
        
        # Blinking dots for active (not idle, not done)
        dots = '<span class="blink-dot">.</span><span class="blink-dot">.</span><span class="blink-dot">.</span>' if status in ["reading", "chewing", "processing", "thinking"] else ""
        
        
        # Build Minion HTML string
        # UPDATED: Applied {anim_class} to the Name, removed from Emoji
        minion_html = f'<div style="display: flex; align-items: center; justify-content: space-between; padding: 0.7rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 1.1rem;"> <div style="flex: 2; min-width: 120px;"> <div style="font-weight: 700; font-size: 1.1rem; color: #e2e8f0; display: inline-block;" class="{anim_class}">{name}</div> <div style="font-size: 0.85rem; color: rgba(255,255,255,0.5);">{file_display}</div> </div> <div style="flex: 1; color: #94a3b8; font-weight: 500;"> <span>{emoji}</span> {status.title()}{dots} </div> <div style="flex: 1; text-align: center;"> <div style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; width: 100%; overflow: hidden;"> <div style="background: linear-gradient(90deg, #10b981, #34d399); height: 100%; width: {pct}%; transition: width 0.3s;"></div> </div> </div> <div style="flex: 0.8; text-align: right; color: #94a3b8; font-size: 1rem;"> {pct}% • {eta}s </div> <div style="flex: 0.5; text-align: right; color: #fca5a5; font-weight: 600;"> ${cost:.5f} </div> </div>'
        st.markdown(minion_html, unsafe_allow_html=True)


def render_first_launch_setup():
    """Show first-launch setup wizard if API key not configured."""
    config = get_config()
    
    if config.has_api_key:
        return True  # Already configured
    
    st.markdown("""
    <div class="main-container" style="max-width: 600px; margin: 2rem auto;">
        <h2 style="color: white; text-align: center;">🔑 First-Time Setup</h2>
        <p style="color: rgba(255,255,255,0.7); text-align: center;">
            Enter your OpenAI API key to enable AI-powered extraction for scanned documents.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Get your key from platform.openai.com"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Save & Continue", use_container_width=True):
            if api_key:
                config.openai_api_key = api_key
                st.success("API key saved!")
                st.rerun()
            else:
                st.warning("Please enter an API key")
    
    with col2:
        if st.button("Skip for Now", use_container_width=True):
            config.set("skip_api_setup", True)
            st.rerun()
    
    st.markdown("""
    <p style="color: rgba(255,255,255,0.4); font-size: 0.85rem; text-align: center; margin-top: 2rem;">
        Without an API key, only Regex extraction will work (for digital PDFs only).
    </p>
    """, unsafe_allow_html=True)
    
    return False  # Not configured, show setup


def main():
    inject_css()
    render_header()
    
    
    # --- AUTHENTICATION ---
    import yaml
    from yaml.loader import SafeLoader
    import streamlit_authenticator as stauth

    # Load Config
    config_path = Path(__file__).parent / "auth_config.yaml"
    with open(config_path) as file:
        auth_config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        auth_config['credentials'],
        auth_config['cookie']['name'],
        auth_config['cookie']['key'],
        auth_config['cookie']['expiry_days'],
        None
    )

    # Render Login
    name, authentication_status, username = authenticator.login("main")

    if authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')
        
        # Sign Up Widget (Only show if not logged in)
        try:
            if authenticator.register_user('Register User', preauthorization=False):
                st.success('User registered successfully')
                # Save to file
                with open(config_path, 'w') as file:
                    yaml.dump(auth_config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)
            
    if authentication_status:
        # LOGGED IN SUCCESSFULLY
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.write(f'Welcome *{name}*')
        
        # --- EXISTING APP LOGIC ---
        # Session State Init
        if "jobs" not in st.session_state:
            st.session_state.jobs = {}
        if "last_uploaded_files" not in st.session_state:
            st.session_state.last_uploaded_files = []
        if "total_cost" not in st.session_state:
            st.session_state.total_cost = 0.0
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0
        if "active_file_list" not in st.session_state:
            st.session_state.active_file_list = []

        # Main Layout - STABLE GRID
        # Row 1: Settings (Left) | File Uploader (Right - Fixed Height)
        col_top_left, col_top_right = st.columns([1, 1], gap="large")
        
        # --- TOP LEFT: Settings ---
        with col_top_left:
            # Match height of right side to ensure perfect grid alignment
            with st.container(height=380, border=True):
                mode, api_key = render_settings()

        # --- TOP RIGHT: File Upload (Fixed Height Container) ---
        with col_top_right:
            # STRICT FIXED HEIGHT CONTAINER for the entire block
            # This ensures the bottom section NEVER moves up or down
            with st.container(height=380, border=True):
                col_u1, col_u2 = st.columns([3, 1])
                with col_u1:
                    st.markdown("### 📂 Drop Files")
                with col_u2:
                    if st.button("🔄 Clear All", key="clear_btn", type="primary", use_container_width=True):
                        st.session_state.jobs = {}
                        st.session_state.minions = {
                            i: {"status": "idle", "file": None, "progress": 0, "eta": 0, "cost": 0.0, "job_id": None}
                            for i in range(4)
                        }
                        st.session_state.total_cost = 0.0
                        st.session_state.last_uploaded_files = [] # Deprecated but kept just in case
                        st.session_state.last_upload_signature = [] # Reset signature!
                        
                        # Force a hard reset of the uploader widget by incrementing its key
                        st.session_state.uploader_key += 1
                        st.rerun()

                uploaded_files = st.file_uploader(
                    "Drag & drop files here",
                    type=["pdf", "xlsx", "xls"],
                    accept_multiple_files=True,
                    label_visibility="collapsed",
                    key=f"uploader_{st.session_state.uploader_key}"
                )
                
                if uploaded_files:
                    st.caption(f"📝 {len(uploaded_files)} files selected")

                # --- DISPLAY ACTIVE BATCH (Inside Fixed Container) ---
                if st.session_state.active_file_list:
                    st.markdown("---")
                    st.caption(f"📂 **Active Batch ({len(st.session_state.active_file_list)} files)**")
                    # Use a scrollable container if list is long, but here simple list is fine
                    # Limit to 3 items to save space, with "+X more" if needed
                    display_list = st.session_state.active_file_list[:3]
                    for fname in display_list:
                        st.text(f"• {fname}")
                    if len(st.session_state.active_file_list) > 3:
                        st.caption(f"...and {len(st.session_state.active_file_list) - 3} more")

        # --- ONE-SHOT INGESTION LOGIC ---
        # The uploader is now an "Input Gate". 
        # If files are present, we ingest them, clear the gate, and start a fresh batch.
        

        if uploaded_files:
            # 1. NEW BATCH RECEIVED -> NUCLEAR RESET
            st.session_state.jobs = {}
            st.session_state.total_cost = 0.0
            st.session_state.minions = {
                i: {"status": "idle", "file": None, "progress": 0, "eta": 0, "cost": 0.0, "job_id": None}
                for i in range(4)
            }
            
            # 2. INGEST FILES & START JOBS
            temp_dir = get_temp_dir()
            new_batch_names = []
            
            for idx, up_file in enumerate(uploaded_files):
                file_path = temp_dir / up_file.name
                file_path.write_bytes(up_file.read())
                new_batch_names.append(up_file.name)
                
                # Auto-submit
                job_id = submit_job(file_path, mode, api_key)
                st.session_state.jobs[job_id] = {
                    "file_name": up_file.name,
                    "status": "pending",
                    "results": None,
                    "start_time": datetime.now(),
                    "message": "Queued...",
                    "minion_id": idx % 4
                }
                
                # Update minion state
                minion_id = idx % 4
                st.session_state.minions[minion_id] = {
                    "status": minion_status,
                    "file": job["file_name"],
                    "progress": progress,
                    "eta": eta,
                    "cost": cost,
                    "job_id": jid
                }
                
                # Force rerun if status changed to complete to show results immediately
                if status["state"] == "complete":
                    job["results"] = status.get("data")
                    st.rerun()
        
        # 3. RENDER RESULTS (Most recent complete job)
        # Find most recent complete job
        completed_jobs = [j for j in st.session_state.jobs.values() if j["status"] == "complete"]
        if completed_jobs:
            # Sort by start time desc
            latest_job = sorted(completed_jobs, key=lambda x: x["start_time"], reverse=True)[0]
            render_results(latest_job["results"], unique_key=latest_job["file_name"])
        else:
            # Placeholder
            st.markdown("""
            <div style="
                border: 2px dashed rgba(255,255,255,0.1); 
                border-radius: 12px; 
                padding: 4rem 2rem; 
                text-align: center;
                color: rgba(255,255,255,0.3);
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                Results will appear here
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
