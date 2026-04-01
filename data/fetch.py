import yfinance as yf
import pandas as pd
from typing import Optional


def fetch_30m_data(symbol: str, period_days: int = 7, timeout: int = 10, max_retry: int = 2) -> Optional[pd.DataFrame]:
    """
    Fetch 30-minute OHLC data using yfinance.
    Returns a DataFrame with lowercase columns ['open','high','low','close'] or None on failure.
    Retries up to max_retry times. Each yf.download uses timeout seconds.
    """
    if symbol is None:
        return None
    period_arg = f"{max(1, min(period_days, 60))}d"
    attempts = 0
    last_err = None
    while attempts < max_retry:
        attempts += 1
        try:
            df = yf.download(symbol, interval="30m", period=period_arg, auto_adjust=False, progress=False, timeout=timeout)
            if df is None or df.empty:
                last_err = RuntimeError("empty dataframe")
                continue
            # Normalize column names
            df = df.copy()
            df.columns = [str(c).strip().lower() for c in df.columns]
            expected = ["open", "high", "low", "close"]
            if not all(c in df.columns for c in expected):
                last_err = RuntimeError(f"missing ohlc cols: {list(df.columns)}")
                continue
            df = df[expected].dropna()
            if df.empty:
                last_err = RuntimeError("empty after dropna")
                continue
            return df
        except Exception as e:
            last_err = e
            continue
    return None

import yfinance as yf
import pandas as pd
from typing import Optional


def fetch_30m_data(symbol: str, period_days: int = 7, timeout: int = 10, max_retry: int = 2) -> Optional[pd.DataFrame]:
    """
    Fetch 30-minute OHLC data using yfinance.
    Returns a DataFrame with lowercase columns ['open','high','low','close'] or None on failure.
    Retries up to max_retry times. Each yf.download uses timeout seconds.
    """
    if symbol is None:
        return None
    period_arg = f"{max(1, min(period_days, 60))}d"
    attempts = 0
    last_err = None
    while attempts < max_retry:
        attempts += 1
        try:
            df = yf.download(symbol, interval="30m", period=period_arg, auto_adjust=False, progress=False, timeout=timeout)
            if df is None or df.empty:
                last_err = RuntimeError("empty dataframe")
                continue
            # Normalize column names
            df = df.copy()
            df.columns = [str(c).strip().lower() for c in df.columns]
            expected = ["open", "high", "low", "close"]
            if not all(c in df.columns for c in expected):
                last_err = RuntimeError(f"missing ohlc cols: {list(df.columns)}")
                continue
            df = df[expected].dropna()
            if df.empty:
                last_err = RuntimeError("empty after dropna")
                continue
            return df
        except Exception as e:
            last_err = e
            continue
    return None

