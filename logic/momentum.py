import pandas as pd
from typing import Optional


def detect_momentum(df: pd.DataFrame) -> Optional[int]:
    """
    Detect simple momentum using last 5 candles (30m data).
    Returns:
      1  -> strong up momentum
     -1  -> strong down momentum
      0  -> weak / range
     None -> invalid input

    Rules (v1):
    - Use last 5 candles.
    - Direction: strictly increasing closes -> up, strictly decreasing -> down.
    - Strength: at least 3 of 5 candles have body > avg_body.
    """
    if df is None:
        return None
    # Ensure OHLC present (accept lowercase or uppercase)
    cols = {c.lower() for c in df.columns}
    if not {"open", "close"}.issubset(cols):
        return None
    if len(df) < 5:
        return None
    try:
        # normalize names
        d = df.copy()
        d.columns = [c.lower() for c in d.columns]
        recent = d[["open", "close"]].tail(5)
        closes = recent["close"].astype(float).values
        opens = recent["open"].astype(float).values
        # direction checks
        up = all(closes[i] < closes[i + 1] for i in range(len(closes) - 1))
        down = all(closes[i] > closes[i + 1] for i in range(len(closes) - 1))
        # body sizes
        bodies = [abs(closes[i] - opens[i]) for i in range(len(closes))]
        avg_body = sum(bodies) / len(bodies) if len(bodies) else 0.0
        strong_count = sum(1 for b in bodies if b > avg_body)
        strong = strong_count >= 3
        if up and strong:
            return 1
        if down and strong:
            return -1
        return 0
    except Exception:
        return None

