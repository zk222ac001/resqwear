import asyncio
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import plotly.express as px
import streamlit as st
import pydeck as pdk
import websockets
from db import DB
from models import EventType, AlertType
from sim_manager import SimulatorManager
from scenarios import SCENARIOS
from rbac import login ,require_role

# --------------------------------------------------------
# CONFIG
# --------------------------------------------------------
st.set_page_config(page_title="ResQWear — Emergency Monitoring", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "resqwear_logo.jpg"

# --------------------------------------------------------
# LOGO LOADER
# --------------------------------------------------------
@st.cache_data
def load_logo_bytes():
    if LOGO_PATH.exists():
        return LOGO_PATH.read_bytes()
    else:
        st.warning(f"Logo not found: {LOGO_PATH}")
        return None

logo_bytes = load_logo_bytes()
# --------------------------------------------------------
# LOGIN
# --------------------------------------------------------
user = login()

# STOP THE APP UNTIL USER IS LOGGED IN
if not user:
    st.stop()

# Only runs after successful login
st.title("Dashboard")

if user["role"] == "operator":
    st.write("Operator tools: tracking, alerts, sensors...")

if user["role"] == "dispatcher":
    require_role("dispatcher")
    st.write("Dispatcher tools: emergency overview, incident map...")

# --------------------------------------------------------
# DB connection
# --------------------------------------------------------
@st.cache_resource
def get_db():
    db = DB()
    asyncio.run(db.init())
    return db

db = get_db()
# --------------------------------------------------------
# Simulator manager (only started once)
# --------------------------------------------------------
if "sim_manager" not in st.session_state:
    st.session_state.sim_manager = SimulatorManager()

# --------------------------------------------------------
# WebSocket Listener (background thread)
# --------------------------------------------------------

SIM_WS = "ws://simulator:8765"   # For Docker
# SIM_WS = "ws://127.0.0.1:8765" # For local debug

def ensure_ws_listener():
    if "ws_thread_started" in st.session_state:
        return

    st.session_state["ws_events"] = []

    async def listen():
        try:
            async with websockets.connect(SIM_WS) as ws:
                while True:
                    raw = await ws.recv()
                    evt = json.loads(raw)
                    st.session_state["ws_events"].append(evt)
                    st.session_state["ws_events"] = st.session_state["ws_events"][-200:]
        except Exception:
            return

    def runner():
        asyncio.run(listen())

    threading.Thread(target=runner, daemon=True).start()
    st.session_state["ws_thread_started"] = True

ensure_ws_listener()
# --------------------------------------------------------
# HEADER
# --------------------------------------------------------
col_logo, col_title = st.columns([1, 6])

with col_logo:
    if logo_bytes:
        st.image(logo_bytes, width=90)
    else:
        st.error("Logo missing!")

with col_title:
    st.title("ResQWear — Emergency Monitoring Dashboard")
    st.caption(f"Logged in as {user['role'].upper()} — {user['username']}")

# --------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------
st.sidebar.markdown(f"### User: {user['role'].upper()}")
# Dispatcher-only controls
if user["role"] == "dispatcher":
    st.sidebar.markdown("## Simulation Control")
    scenario = st.sidebar.selectbox("Scenario", list(SCENARIOS.keys()))
    n_dev = st.sidebar.slider("Devices", 1, 6, 3)

    colA, colB = st.sidebar.columns(2)
    if colA.button("Start"):
        st.session_state.sim_manager.start_simulator(scenario, n_dev)

    if colB.button("Stop"):
        st.session_state.sim_manager.stop_simulator(scenario)

    st.sidebar.write("Simulator:", st.session_state.sim_manager.status())

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Manual Emergency Trigger")

    devices = asyncio.run(db.list_devices())
    device_opts = {f"{d['name']} ({d['device_id']})": d["device_id"] for d in devices} or {"(none)": None}
    selected = st.sidebar.selectbox("Device", list(device_opts.keys()))
    selected_id = device_opts[selected]

    alert_type = st.sidebar.selectbox("Alert type", [a.value for a in AlertType])
    alert_msg = st.sidebar.text_input("Message", "Manual SOS triggered by operator")

    if st.sidebar.button("Trigger SOS") and selected_id:
        alert_id = "MANUAL-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        ts = datetime.now(timezone.utc)

        asyncio.run(db.upsert_alert(alert_id, selected_id, alert_type, alert_msg, 5, ts, False))
        st.sidebar.success("SOS sent.")
# --------------------------------------------------------
# TABS
# --------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Overview", 
                                  "Live Map",
                                  "Temperature",
                                  "Alerts"])
# ========================================================
# TAB 1 — OVERVIEW
# ========================================================
with tab1:
    st.subheader("Active Devices")
    devices = asyncio.run(db.list_devices())
    df_dev = pd.DataFrame(devices)
    if not df_dev.empty:
        df_dev["last_seen"] = pd.to_datetime(df_dev["last_seen"])
        df_dev["fresh"] = (datetime.now(timezone.utc) - df_dev["last_seen"]).dt.total_seconds() < 90 # type: ignore

        st.dataframe(df_dev, use_container_width=True)
    else:
        st.info("No devices connected.")
    st.subheader("Recent WebSocket Events")

    events = pd.DataFrame(st.session_state.get("ws_events", [])[-40:])
    if not events.empty:
        st.dataframe(events, use_container_width=True)
    else:
        st.info("Waiting for simulator events...")
# ========================================================
# TAB 2 — LIVE MAP
# ========================================================
with tab2:
    st.subheader("Real-Time Device Location Map")

    if not devices:
        st.info("No devices available.")
    else:
        selected = st.selectbox("Device", [f"{d['name']} ({d['device_id']})" for d in devices], key="map_device")
        dev_id = next(d["device_id"] for d in devices if f"{d['name']} ({d['device_id']})" == selected)

        last = asyncio.run(db.last_known(dev_id))
        traj = asyncio.run(db.hourly_positions(dev_id, hours=24))

        if last:
            points = pd.DataFrame(traj if traj else [last])
            view = pdk.ViewState(latitude=last["lat"], longitude=last["lon"], zoom=12)
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=points,
                get_position="[lon, lat]",
                get_fill_color="[255, 50, 0, 200]",
                get_radius=90,
            )
            st.pydeck_chart(
                pdk.Deck(
                    layers=[layer],
                    initial_view_state=view,
                    tooltip={"text": "{device_id}\n{ts}"} # type: ignore
                )
            )
            st.markdown(f"**Last seen:** {last['lat']:.5f}, {last['lon']:.5f} — {last['ts']}")
        else:
            st.info("No location data yet.")

# ========================================================
# TAB 3 — TEMPERATURE
# ========================================================
with tab3:
    st.subheader("Temperature Time-Series")

    if not devices:
        st.info("No devices for temperature data.")
    else:
        selected = st.selectbox("Device", [f"{d['name']} ({d['device_id']})" for d in devices], key="temp_device")
        dev_id = next(d["device_id"] for d in devices if f"{d['name']} ({d['device_id']})" == selected)
        series = asyncio.run(db.temps_series(dev_id, minutes=240))

        if series:
            df = pd.DataFrame(series)
            df["ts"] = pd.to_datetime(df["ts"])

            fig = px.line(df, x="ts", y="temp_c", title="Temperature (°C)", markers=True)
            fig.add_hline(y=5, line_dash="dash", annotation_text="Hypothermia threshold")

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No temperature data.")

# ========================================================
# TAB 4 — ALERTS
# ========================================================
with tab4:
    st.subheader("Active Alerts")

    alerts = asyncio.run(db.active_alerts())

    if alerts:
        df = pd.DataFrame(alerts)
        df["ts"] = pd.to_datetime(df["ts"])
        st.dataframe(df, use_container_width=True)

        if user["role"] == "operator":
            sel = st.selectbox("Resolve alert", ["(choose)"] + df["alert_id"].tolist())
            if sel != "(choose)" and st.button("Mark Resolved"):
                asyncio.run(db.resolve_alert(sel))
                st.success("Alert resolved.")
    else:
        st.success("No active alerts.")
