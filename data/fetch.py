import yfinance as yf
import pandas as pd
from typing import Optional

# SYMBOL_MAP: input symbol -> yfinance symbol
SYMBOL_MAP = {
    "EURUSD": "EURUSD=X",
    "GBPJPY": "GBPJPY=X",
    "SP500": "^GSPC",
}


def fetch_30m_data(symbol: str, period_days: int = 7, timeout: int = 10, max_retry: int = 2) -> Optional[pd.DataFrame]:
    """
    Fetch 30-minute OHLC data using yfinance.
    - symbol: one of keys in SYMBOL_MAP (e.g., "EURUSD","GBPJPY","SP500")
    - timeout: per-call timeout (<=10)
    - max_retry: <=2

    Returns a DataFrame with lowercase columns ['open','high','low','close'] or None on failure.
    """
    if symbol is None:
        print(f"[FAIL] {symbol}")
        return None

    mapped = SYMBOL_MAP.get(symbol)
    if mapped is None:
        print(f"[FAIL] {symbol} (no mapping)")
        return None

    # For SP500 allow a single fallback to SPY
    candidates = [mapped]
    if symbol == "SP500":
        # primary ^GSPC then fallback SPY (ETF)
        if mapped != "SPY":
            candidates = [mapped, "SPY"]

    period_arg = f"{max(1, min(period_days, 60))}d"

    attempts = 0
    for cand in candidates:
        if attempts >= max_retry:
            break
        attempts += 1
        print(f"[FETCH] {symbol} → {cand}")
        try:
            df = yf.download(cand, interval="30m", period=period_arg, auto_adjust=False, progress=False, timeout=timeout)
        except Exception as e:
            print(f"[FAIL] {symbol} ({cand}) exception: {e}")
            df = None

        # Validation checks
        if df is None:
            print(f"[FAIL] {symbol} ({cand}) - no data")
            continue
        if df.empty:
            print(f"[FAIL] {symbol} ({cand}) - empty")
            continue
        if len(df) < 20:
            print(f"[FAIL] {symbol} ({cand}) - insufficient rows ({len(df)})")
            continue

        # Normalize and ensure OHLC exist
        try:
            df = df.copy()
            df.columns = [str(c).strip().lower() for c in df.columns]
            expected = ["open", "high", "low", "close"]
            if not all(c in df.columns for c in expected):
                print(f"[FAIL] {symbol} ({cand}) - missing cols {list(df.columns)}")
                continue
            df = df[expected].dropna()
            if df.empty or len(df) < 20:
                print(f"[FAIL] {symbol} ({cand}) - post-clean insufficient rows")
                continue
        except Exception as e:
            print(f"[FAIL] {symbol} ({cand}) - validation error: {e}")
            continue

        print(f"[OK] {symbol} ({cand})")
        return df

    # all attempts failed
    print(f"[FAIL] {symbol} - all candidates tried")
    return None

 

