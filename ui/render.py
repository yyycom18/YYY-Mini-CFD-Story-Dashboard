import streamlit as st

# Must match header and every data row — identical structure for alignment.
SCANNER_COLUMN_RATIOS = [2, 2, 2, 2, 2, 1, 1, 1]


def render_scanner_header() -> None:
    """Table header using the same st.columns layout as rows."""
    cols = st.columns(SCANNER_COLUMN_RATIOS)
    cols[0].markdown("**Asset**")
    cols[1].markdown("**Season (4H)**")
    cols[2].markdown("**Wind (1H)**")
    cols[3].markdown("**Bias (4H)**")
    cols[4].markdown("**Bias (1H)**")
    cols[5].markdown("**Align**")
    cols[6].markdown("**Prox.**")
    cols[7].markdown("**Priority**")


def render_asset_row(asset: str, row: dict) -> None:
    """
    One scanner row — same column ratios as render_scanner_header().
    row keys: season, wind, bias4, bias1, alignment, proximity, priority
    """
    cols = st.columns(SCANNER_COLUMN_RATIOS)
    cols[0].write(asset)
    cols[1].write(row.get("season", "N/A"))
    cols[2].write(row.get("wind", "N/A"))
    cols[3].write(row.get("bias4", "N/A"))
    cols[4].write(row.get("bias1", "N/A"))
    cols[5].write(row.get("alignment", "-"))
    cols[6].write(row.get("proximity", "-"))
    cols[7].write(row.get("priority", "-"))
