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
        # normalize names to lowercase
        d = df.copy()
        d.columns = [c.lower() for c in d.columns]
        if "open" not in d.columns or "close" not in d.columns:
            return None
        recent = d[["open", "close"]].tail(5)
        if len(recent) < 5:
            return None
        opens = recent["open"].astype(float).values
        closes = recent["close"].astype(float).values

        # count bullish/bearish candles
        bullish = sum(1 for i in range(len(closes)) if closes[i] > opens[i])
        bearish = sum(1 for i in range(len(closes)) if closes[i] < opens[i])

        # body strength
        bodies = [abs(closes[i] - opens[i]) for i in range(len(closes))]
        avg_body = sum(bodies) / len(bodies) if len(bodies) else 0.0
        strong_count = sum(1 for b in bodies if b > avg_body)

        if bullish >= 3 and strong_count >= 2:
            return 1
        if bearish >= 3 and strong_count >= 2:
            return -1
        return 0
    except Exception:
        return None

