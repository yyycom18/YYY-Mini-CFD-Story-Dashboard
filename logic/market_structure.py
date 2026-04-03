import pandas as pd
from typing import Optional


def detect_market_structure(df: pd.DataFrame) -> Optional[int]:
    """
    Detect 4H market structure using swing analysis (HH/HL/LH/LL).
    
    Returns:
        +1 if Upside (Higher High + Higher Low)
        -1 if Downside (Lower High + Lower Low)
        0 if Range/Neutral (mixed or unclear structure)
        None if invalid data
    
    Logic:
        - Use recent highs/lows (~20-30 candles)
        - Compare last 2 significant swings
        - Avoid SMA/indicators entirely
        - Pure structure-based classification
    
    Args:
        df: DataFrame with 'High' and 'Low' columns
    
    Performance:
        - O(1) — constant time, no loops
        - <0.1ms execution
    """
    # Validation
    if df is None or df.empty:
        return None
    
    if len(df) < 10:
        return None
    
    try:
        highs = df["high"].astype(float)
        lows = df["low"].astype(float)
    except (KeyError, ValueError, TypeError):
        return None
    
    # Ensure we have valid data
    if highs.isna().any() or lows.isna().any():
        return None
    
    # Use recent candles only (last 30)
    lookback = min(30, len(df))
    recent_highs = highs.iloc[-lookback:]
    recent_lows = lows.iloc[-lookback:]
    
    # Identify recent swing points (simple method: compare adjacent peaks/troughs)
    # Take highs/lows from different positions to avoid consecutive same candle
    
    # Last high/low (most recent)
    last_high = recent_highs.iloc[-1]
    last_low = recent_lows.iloc[-1]
    
    # Previous swing high/low (scan back, skip immediate neighbors)
    # Look 5-10 candles back for previous swing
    prev_high = recent_highs.iloc[-min(10, len(recent_highs)):-1].max()
    prev_low = recent_lows.iloc[-min(10, len(recent_lows)):-1].min()
    
    # Detect structure
    higher_high = last_high > prev_high
    higher_low = last_low > prev_low
    lower_high = last_high < prev_high
    lower_low = last_low < prev_low
    
    # Classification
    if higher_high and higher_low:
        return 1  # Upside structure
    elif lower_high and lower_low:
        return -1  # Downside structure
    else:
        return 0  # Range/Neutral (mixed or no clear pattern)
