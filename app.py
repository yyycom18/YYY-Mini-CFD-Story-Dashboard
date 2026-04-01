import streamlit as st
import time
from data.fetch import fetch_30m_data
from logic.analysis import compute_alignment, compute_proximity, priority_from_alignment_proximity
from ui.render import render_asset_row
from typing import List

MAX_ASSETS = 3
DEFAULT_ASSETS = ["EURUSD", "GBPJPY", "SP500"]
GLOBAL_TIMEOUT = 15  # seconds

st.set_page_config(page_title="Mini CFD Story Dashboard", layout="wide")

start_time = time.time()

st.title("Mini CFD Story Dashboard (v1)")
st.write("Lightweight market radar — stable, fast, and simple.")

# selected assets (limit)
assets = DEFAULT_ASSETS[:MAX_ASSETS]

st.sidebar.header("Settings")
st.sidebar.write(f"Max assets: {MAX_ASSETS}")

def safe_fetch(symbol: str):
    # wrapper to respect GLOBAL_TIMEOUT
    try:
        df = fetch_30m_data(symbol, period_days=5, timeout=10, max_retry=2)
        return df
    except Exception:
        return None

rows = []
for sym in assets:
    # global timeout check
    if time.time() - start_time > GLOBAL_TIMEOUT:
        st.error("System timeout — safe exit")
        st.stop()

    df = safe_fetch(sym)
    if df is None:
        row = {
            "season": "N/A",
            "wind": "N/A",
            "bias4": "N/A",
            "bias1": "N/A",
            "alignment": 0,
            "proximity": "Data unavailable",
            "priority": "N/A",
            "signal": "Data unavailable",
        }
    else:
        alignment = compute_alignment(df)
        proximity = compute_proximity(df)
        priority = priority_from_alignment_proximity(alignment, proximity)
        row = {
            "season": "N/A",
            "wind": "N/A",
            "bias4": "N/A",
            "bias1": "N/A",
            "alignment": alignment,
            "proximity": proximity,
            "priority": priority,
            "signal": "See priority",
        }
    rows.append((sym, row))

st.subheader("Market Scanner — Mini Radar")
st.write("Columns: Asset | Season (4H) | Wind (1H) | Bias (4H) | Bias (1H) | Alignment | Proximity | Priority")

for sym, row in rows:
    render_asset_row(sym, row)
    # small guard to keep UI responsive
    if time.time() - start_time > GLOBAL_TIMEOUT:
        st.error("System timeout — safe exit")
        st.stop()

st.write("Done.")

