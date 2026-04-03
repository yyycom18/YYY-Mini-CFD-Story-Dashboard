import pandas as pd
from typing import Tuple, Optional
from market_structure import detect_market_structure
from logic.momentum import detect_momentum


def compute_season_4h(df: pd.DataFrame) -> str:
    """
    Detect 4H Season (structure-based, NOT SMA).
    
    Uses pure swing analysis:
    - HH + HL → "↑ Up" (Upside structure)
    - LH + LL → "↓ Down" (Downside structure)
    - Mixed → "→ Range" (Neutral/No clear structure)
    
    Returns:
        "↑ Up": Upside structure
        "↓ Down": Downside structure
        "→ Range": Neutral/Range structure
        "→ N/A": Invalid data
    """
    if df is None or df.empty:
        return "→ N/A"
    
    try:
        structure = detect_market_structure(df)
        
        if structure is None:
            return "→ N/A"
        elif structure == 1:
            return "↑ Up"
        elif structure == -1:
            return "↓ Down"
        else:  # structure == 0
            return "→ Range"
    except Exception as e:
        print(f"[LOGIC ERROR] compute_season_4h: {e}")
        return "→ N/A"



def compute_bias(df: pd.DataFrame, label: str = "1H") -> str:
    """
    Simple Bias using momentum: last_close - previous_close
    If bias > 0 → "↑ Up"
    If bias < 0 → "↓ Down"
    Else → "→ Range"
    
    Args:
        df: DataFrame with 'close' column (preferably real 1H data)
        label: label for logging (e.g., "1H", "4H")
    """
    # Use momentum detector on recent candles
    try:
        m = detect_momentum(df)
        if m is None:
            return "→ N/A"
        if m == 1:
            return "↑ Strong Up"
        if m == -1:
            return "↓ Strong Down"
        return "→ Weak / Range"
    except Exception as e:
        print(f"[LOGIC ERROR] compute_bias ({label}): {e}")
        return "→ N/A"


def compute_alignment(df: pd.DataFrame) -> int:
    """
    Simple alignment score 0-3 using short/med/long returns:
    - Compare last close vs close N bars ago for N in [1,3,6]
    - Count how many are trending in same direction (up or down).
    """
    if df is None or df.empty:
        return 0
    try:
        closes = df["close"].astype(float)
        last = closes.iloc[-1]
        scores = []
        for n in (1, 3, 6):
            if len(closes) > n:
                prev = closes.iloc[-(n + 1)]
                scores.append(1 if last > prev else (-1 if last < prev else 0))
            else:
                scores.append(0)
        # determine dominant direction
        up_count = sum(1 for v in scores if v == 1)
        down_count = sum(1 for v in scores if v == -1)
        return max(up_count, down_count)
    except Exception:
        return 0


def compute_proximity(df: pd.DataFrame) -> str:
    """
    Proximity heuristic: compute 20-period simple moving average.
    If last price within 1% of SMA -> NEAR, else FAR.
    """
    if df is None or df.empty:
        return "⚪ FAR"
    try:
        closes = df["close"].astype(float)
        if len(closes) < 5:
            return "⚪ FAR"
        sma_period = min(20, len(closes))
        sma = closes.rolling(window=sma_period).mean().iloc[-1]
        last = closes.iloc[-1]
        if sma is None or pd.isna(sma):
            return "⚪ FAR"
        rel = abs(last - sma) / max(abs(sma), 1e-8)
        return "🟢 NEAR" if rel <= 0.01 else "⚪ FAR"
    except Exception:
        return "⚪ FAR"


def priority_from_alignment_proximity(alignment: int, proximity: str) -> str:
    """
    Priority mapping:
    - alignment == 3 and NEAR -> HOT
    - alignment == 3 and FAR -> WARM
    - alignment == 2 -> MEDIUM
    - else LOW
    """
    try:
        if alignment == 3 and proximity.startswith("🟢"):
            return "🔥 HOT"
        if alignment == 3 and proximity.startswith("⚪"):
            return "📌 WARM"
        if alignment == 2:
            return "📍 MEDIUM"
    except Exception:
        pass
    return "❄️ LOW"

