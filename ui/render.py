import streamlit as st

# Must match header and every data row — identical structure for alignment.
# Trade Gate column is wider for prominence (second column).
SCANNER_COLUMN_RATIOS = [2, 3, 2, 2, 2, 2, 1, 1, 1]


def _trade_gate_html(val: str) -> str:
    if val == "PASS":
        return '<span style="background:#22c55e;color:#fff;font-weight:700;padding:4px 10px;border-radius:4px;">PASS</span>'
    if val == "BLOCK":
        return '<span style="background:#dc2626;color:#fff;font-weight:700;padding:4px 10px;border-radius:4px;">BLOCK</span>'
    return '<span style="color:#6b7280;font-weight:600;">—</span>'


def render_scanner_header() -> None:
    """Table header using the same st.columns layout as rows."""
    cols = st.columns(SCANNER_COLUMN_RATIOS)
    cols[0].markdown("**Asset**")
    cols[1].markdown("**Trade Gate**")
    cols[2].markdown("**Season (4H)**")
    cols[3].markdown("**Wind (1H)**")
    cols[4].markdown("**Bias (4H)**")
    cols[5].markdown("**Bias (1H)**")
    cols[6].markdown("**Align**")
    cols[7].markdown("**Prox.**")
    cols[8].markdown("**Priority**")


def render_asset_row(asset: str, row: dict) -> None:
    """
    One scanner row — same column ratios as render_scanner_header().
    row keys: trade_gate, season, wind, bias4, bias1, alignment, proximity, priority
    """
    cols = st.columns(SCANNER_COLUMN_RATIOS)
    cols[0].write(asset)
    cols[1].markdown(_trade_gate_html(str(row.get("trade_gate", "—"))), unsafe_allow_html=True)
    cols[2].write(row.get("season", "N/A"))
    cols[3].write(row.get("wind", "N/A"))
    cols[4].write(row.get("bias4", "N/A"))
    cols[5].write(row.get("bias1", "N/A"))
    cols[6].write(row.get("alignment", "-"))
    cols[7].write(row.get("proximity", "-"))
    cols[8].write(row.get("priority", "-"))
