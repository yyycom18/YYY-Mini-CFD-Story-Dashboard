import streamlit as st
import pandas as pd
import time
from data.fetch import fetch_30m_data, fetch_1h_data
from logic.analysis import (
    compute_season_4h,
    compute_bias,
    compute_alignment,
    compute_proximity,
    priority_from_alignment_proximity,
)
from ui.render import render_asset_row
from typing import List, Tuple, Optional

MAX_ASSETS = 3
DEFAULT_ASSETS = ["EURUSD", "GBPJPY", "SP500"]
GLOBAL_TIMEOUT = 15  # seconds

st.set_page_config(page_title="Mini CFD Story Dashboard", layout="wide")


def main():
    start_time = time.time()

    st.title("Mini CFD Story Dashboard (v2 — Multi-Timeframe)")
    st.write("Lightweight market radar — stable, fast, and simple. Now with real 1H data.")

    # selected assets (limit)
    assets = DEFAULT_ASSETS[:MAX_ASSETS]

    st.sidebar.header("Settings")
    st.sidebar.write(f"Max assets: {MAX_ASSETS}")
    st.sidebar.write("Data: 30M (4H proxy) + 1H (real)")

    def safe_fetch_30m(symbol: str) -> Optional[pd.DataFrame]:
        """Fetch 30M data with timeout."""
        try:
            df = fetch_30m_data(symbol, period_days=5, timeout=10, max_retry=2)
            return df
        except Exception as e:
            print(f"[ERROR] safe_fetch_30m {symbol}: {e}")
            return None

    def safe_fetch_1h(symbol: str) -> Optional[pd.DataFrame]:
        """Fetch 1H data with timeout."""
        try:
            df = fetch_1h_data(symbol, period_days=5, timeout=10, max_retry=2)
            return df
        except Exception as e:
            print(f"[ERROR] safe_fetch_1h {symbol}: {e}")
            return None

    rows = []
    for sym in assets:
        # global timeout check
        if time.time() - start_time > GLOBAL_TIMEOUT:
            st.error("System timeout — safe exit")
            st.stop()

        print(f"\n[MAIN LOOP] Processing asset: {sym}")
        
        # Fetch both timeframes in parallel logic (sequential for simplicity)
        df_30m = safe_fetch_30m(sym)
        df_1h = safe_fetch_1h(sym)

        # Check if at least one timeframe succeeded
        if df_30m is None and df_1h is None:
            print(f"[ERROR] {sym} - both timeframes failed")
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
            # Compute Season (4H) using 30M data (proxy)
            season_4h = compute_season_4h(df_30m) if df_30m is not None else "→ N/A"
            
            # Compute Bias (4H) using 30M data
            bias_4h = compute_bias(df_30m, label="4H") if df_30m is not None else "→ N/A"
            
            # Compute Bias (1H) using REAL 1H data, fallback to 30M if needed
            if df_1h is not None:
                bias_1h = compute_bias(df_1h, label="1H")
                print(f"[SUCCESS] {sym} - using REAL 1H data for bias")
            else:
                bias_1h = compute_bias(df_30m, label="1H (fallback)") if df_30m is not None else "→ N/A"
                print(f"[FALLBACK] {sym} - 1H fetch failed, using 30M for 1H bias")
            
            # Compute alignment and proximity using 30M (or 1H if 30M failed)
            df_for_metrics = df_30m if df_30m is not None else df_1h
            alignment = compute_alignment(df_for_metrics) if df_for_metrics is not None else 0
            proximity = compute_proximity(df_for_metrics) if df_for_metrics is not None else "⚪ FAR"
            priority = priority_from_alignment_proximity(alignment, proximity)
            
            row = {
                "season": season_4h,
                "wind": bias_1h,
                "bias4": bias_4h,
                "bias1": bias_1h,
                "alignment": alignment,
                "proximity": proximity,
                "priority": priority,
                "signal": "See priority",
            }
        rows.append((sym, row))

    st.subheader("Market Scanner — Multi-Timeframe Radar")
    st.write("Columns: Asset | Season (4H) | Wind (1H) | Bias (4H) | Bias (1H) | Alignment | Proximity | Priority")
    st.write("**Data sources**: 30M (Season/Bias4) + 1H (Bias1 — real when available)")

    for sym, row in rows:
        render_asset_row(sym, row)
        # small guard to keep UI responsive
        if time.time() - start_time > GLOBAL_TIMEOUT:
            st.error("System timeout — safe exit")
            st.stop()

    elapsed = time.time() - start_time
    st.write(f"Done. Completed in {elapsed:.2f}s")


if __name__ == "__main__":
    main()


