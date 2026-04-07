"""
Trade Gate for Mini dashboard — structure stages from detect_market_structure (see docs/60_TRADE_GATE_VALIDATION_PLAN.md).
"""

from typing import Optional


def trade_gate_mini(stage_4h: Optional[int], stage_1h: Optional[int], alignment: int) -> str:
    """
    PASS only if season and wind stages match strictly (both non-zero) and alignment >= 2.
    — only when neither timeframe produced a stage (no data).
    """
    if stage_4h is None and stage_1h is None:
        return "—"
    if stage_4h is None or stage_1h is None:
        return "BLOCK"
    if stage_4h == 0:
        return "BLOCK"
    if stage_1h != stage_4h or stage_1h == 0:
        return "BLOCK"
    if alignment < 2:
        return "BLOCK"
    return "PASS"
