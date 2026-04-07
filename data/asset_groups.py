"""
Trade Gate validation — scanner asset groups (see docs/60_TRADE_GATE_VALIDATION_PLAN.md).

No fetch logic: only ordered symbol keys that exist in SYMBOL_MAP.
"""

from typing import Dict, List

GROUP_A_PRIMARY = ("EURUSD", "GBPJPY", "SPX500", "BTCUSD")

GROUP_B_SECONDARY = (
    "XAUUSD",
    "EURJPY",
    "EURGBP",
    "AUDUSD",
    "GBPUSD",
    "USDCAD",
    "NZDUSD",
    "USDCHF",
    "USDJPY",
    "HK50",
)


def build_scanner_assets(symbol_map: Dict[str, str], include_group_b: bool) -> List[str]:
    out: List[str] = []
    seen = set()
    for s in GROUP_A_PRIMARY:
        if s in symbol_map and s not in seen:
            out.append(s)
            seen.add(s)
    if include_group_b:
        for s in GROUP_B_SECONDARY:
            if s in symbol_map and s not in seen:
                out.append(s)
                seen.add(s)
    return out
