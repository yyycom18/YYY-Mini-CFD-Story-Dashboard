import streamlit as st
import pandas as pd
import time
from pathlib import Path
from data.fetch import fetch_30m_data, fetch_1h_data, SYMBOL_MAP
from data.asset_groups import build_scanner_assets
from logic.analysis import (
    compute_season_4h,
    compute_bias,
    compute_alignment,
    compute_proximity,
    priority_from_alignment_proximity,
)
from logic.market_structure import detect_market_structure
from logic.trade_gate import trade_gate_mini
from ui.render import render_asset_row, render_scanner_header
from typing import List, Tuple, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent


def _read_doc(relative_path: str) -> Optional[str]:
    path = _PROJECT_ROOT / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _render_documentation_ui() -> None:
    """Sidebar quick reference + main expander (full doc). Lazy: read files once per run."""
    doc_main = _read_doc("docs/50_TRADING_LOGIC.md")
    doc_quick = _read_doc("docs/51_TRADING_LOGIC_QUICK_REFERENCE.md")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📖 Dashboard Guide")
    if doc_main:
        with st.sidebar.expander("Trading logic (50_TRADING_LOGIC.md)", expanded=False):
            st.markdown(doc_main)
    else:
        st.sidebar.warning("Documentation not available (50_TRADING_LOGIC.md).")

    st.sidebar.subheader("Quick Guide")
    if doc_quick:
        with st.sidebar.expander("Quick reference (51_…)", expanded=False):
            st.markdown(doc_quick)
    else:
        st.sidebar.warning("Quick reference not available (51_TRADING_LOGIC_QUICK_REFERENCE.md).")

    st.markdown("---")
    with st.expander("📖 How this dashboard works (full)", expanded=False):
        if doc_main:
            st.markdown(doc_main)
        else:
            st.warning("Documentation not available.")

GLOBAL_TIMEOUT = 15  # seconds

st.set_page_config(page_title="Mini CFD Story Dashboard", layout="wide")


def main():
    start_time = time.time()

    st.title("Mini CFD Story Dashboard (v2 — Multi-Timeframe)")
    st.write("Lightweight market radar — stable, fast, and simple. Trade Gate validation: Group A by default.")

    st.sidebar.header("Settings")
    include_group_b = st.sidebar.checkbox(
        "Include Group B (secondary / risk)",
        value=False,
        help="Optional extra symbols (e.g. XAUUSD). Default = Group A only.",
    )
    active_universe = build_scanner_assets(SYMBOL_MAP, include_group_b)
    n_univ = max(1, len(active_universe))
    default_scan = min(4, n_univ)
    max_assets = st.sidebar.slider(
        "Max assets to scan",
        min_value=1,
        max_value=n_univ,
        value=default_scan,
    )
    assets = active_universe[:max_assets]

    st.sidebar.write("Data: 30M (4H proxy) + 1H (real)")

    _render_documentation_ui()

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
                "trade_gate": "—",
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

            s4 = detect_market_structure(df_30m) if df_30m is not None else None
            s1 = detect_market_structure(df_1h) if df_1h is not None else None
            trade_gate = trade_gate_mini(s4, s1, alignment)
            
            row = {
                "trade_gate": trade_gate,
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
    st.caption(
        "Data sources: 30M (Season / Bias 4H) + 1H (Bias 1H — real when available). "
        "Trade Gate uses structure stages on 30M (season) and 1H (wind); see docs/60_TRADE_GATE_VALIDATION_PLAN.md."
    )

    render_scanner_header()
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


