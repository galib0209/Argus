# dashboard.py
# Day 9: ULTRA DASHBOARD
# Features: Altair Charts, Danger Lines, Neon UI

import streamlit as st
import sqlite3
import pandas as pd
import time
import altair as alt

st.set_page_config(page_title="Argus Mission Control", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# --- NEON CSS ---
st.markdown("""
<style>
    .stApp { background-color: #000000; }
    div[data-testid="metric-container"] {
        background-color: #111;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 5px;
        color: #0f0;
    }
    /* Log Text Area Style */
    .stTextArea textarea {
        font-family: 'Consolas', monospace;
        background-color: #0a0a0a;
        color: #00ff41;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ ARGUS: SRE MISSION CONTROL")

def load_data():
    try:
        conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
        df_metrics = pd.read_sql("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 50", conn)
        df_alerts = pd.read_sql("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 5", conn)
        df_cmds = pd.read_sql("SELECT * FROM commands WHERE executed=1 ORDER BY id DESC LIMIT 5", conn)
        conn.close()
        
        if not df_alerts.empty: df_alerts['timestamp'] = pd.to_datetime(df_alerts['timestamp'])
        if not df_metrics.empty: df_metrics['timestamp'] = pd.to_datetime(df_metrics['timestamp'])
        return df_metrics, df_alerts, df_cmds
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- CUSTOM ALTAIR CHART FUNCTION ---
def create_cyber_chart(data, y_col, color_hex, title, threshold=None):
    if data.empty: return st.info("No Data")
    
    # Base Chart
    base = alt.Chart(data).encode(
        x=alt.X('timestamp:T', axis=alt.Axis(title="", labels=False, grid=False)),
        y=alt.Y(f'{y_col}:Q', axis=alt.Axis(title=""), scale=alt.Scale(domain=[0, 100])),
        tooltip=['timestamp', y_col]
    )

    # The Area (Gradient look)
    area = base.mark_area(
        line={'color': color_hex},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(offset=0, color=color_hex), alt.GradientStop(offset=1, color='black')],
            x1=1, x2=1, y1=1, y2=0
        ),
        opacity=0.5
    )
    
    final_chart = area

    # Add Danger Line if needed
    if threshold:
        rule = alt.Chart(pd.DataFrame({'y': [threshold]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='y')
        final_chart = area + rule

    st.altair_chart(final_chart, use_container_width=True, theme=None)

# --- MAIN LOOP ---
# No while loop, using rerun()
time.sleep(0.5)
df, df_alerts, df_cmds = load_data()

if not df.empty:
    latest = df.iloc[0]
    
    # TOP METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CPU LOAD", f"{latest['cpu']:.1f}%", delta_color="off")
    c2.metric("RAM USAGE", f"{latest['ram']:.1f}%", delta_color="off")
    c3.metric("TEMP (EST)", f"{latest['temp']:.1f}°C", delta_color="off")
    c4.metric("NET SPEED", f"{latest['network']:.2f} MB/s", delta_color="off")

    col_main, col_logs = st.columns([2, 1])

    with col_main:
        st.subheader("🔥 CPU Telemetry (Red Line = 90%)")
        # RED chart with DANGER LINE at 90
        create_cyber_chart(df, 'cpu', '#FF4B4B', 'CPU', threshold=90)
        
        c_a, c_b = st.columns(2)
        with c_a:
            st.caption("RAM Usage")
            create_cyber_chart(df, 'ram', '#00FFAA', 'RAM')
        with c_b:
            st.caption("Network Activity")
            create_cyber_chart(df, 'network', '#FFAA00', 'NET')

    with col_logs:
        st.subheader("🤖 AI Actions")
        if not df_cmds.empty:
            for i, row in df_cmds.iterrows():
                st.error(f"⚡ KILL COMMAND EXECUTED\nTarget: {row['machine_id']}")
        else:
            st.success("System Stable. AI Standby.")
            
        st.subheader("🧠 Gemini Logs")
        if not df_alerts.empty:
            for i, row in df_alerts.iterrows():
                ts = row['timestamp'].strftime('%H:%M:%S')
                st.text_area(f"[{ts}] Analysis", row['analysis'], height=100, key=f"log_{row['id']}")

st.rerun()