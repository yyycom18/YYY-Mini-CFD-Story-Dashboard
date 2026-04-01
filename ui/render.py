import streamlit as st


def render_asset_row(asset: str, row: dict):
    """
    Render a simple row for asset using st.metric / st.write.
    row is expected to contain keys: Season (4H), Wind (1H), Bias (4H), Bias (1H),
    Alignment, Proximity, Priority, Signal
    """
    cols = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
    cols[0].write(asset)
    cols[1].write(row.get("season", "N/A"))
    cols[2].write(row.get("wind", "N/A"))
    cols[3].write(row.get("bias4", "N/A"))
    cols[4].write(row.get("bias1", "N/A"))
    cols[5].metric("Align", row.get("alignment", "-"))
    cols[6].write(row.get("proximity", "-"))
    cols[7].write(row.get("priority", "-"))

import streamlit as st


def render_asset_row(asset: str, row: dict):
    """
    Render a simple row for asset using st.metric / st.write.
    row is expected to contain keys: Season (4H), Wind (1H), Bias (4H), Bias (1H),
    Alignment, Proximity, Priority, Signal
    """
    cols = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
    cols[0].write(asset)
    cols[1].write(row.get("season", "N/A"))
    cols[2].write(row.get("wind", "N/A"))
    cols[3].write(row.get("bias4", "N/A"))
    cols[4].write(row.get("bias1", "N/A"))
    cols[5].metric("Align", row.get("alignment", "-"))
    cols[6].write(row.get("proximity", "-"))
    cols[7].write(row.get("priority", "-"))

