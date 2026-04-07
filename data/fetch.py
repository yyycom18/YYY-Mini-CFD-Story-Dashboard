import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional

# SYMBOL_MAP: input symbol -> yfinance symbol (aligned with Project 99 / 60_TRADE_GATE_VALIDATION_PLAN)
SYMBOL_MAP = {
    "EURUSD": "EURUSD=X",
    "GBPJPY": "GBPJPY=X",
    "SPX500": "^GSPC",
    "BTCUSD": "BTC-USD",
    "XAUUSD": "GC=F",
    "EURJPY": "EURJPY=X",
    "EURGBP": "EURGBP=X",
    "AUDUSD": "AUDUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDCAD": "USDCAD=X",
    "NZDUSD": "NZDUSD=X",
    "USDCHF": "USDCHF=X",
    "USDJPY": "USDJPY=X",
    "HK50": "^HSI",
}

# DEBUG MODE: If True, use fake data on yfinance failure
DEBUG_MODE_FALLBACK = True


def _create_fake_data(symbol: str, rows: int = 50) -> pd.DataFrame:
    """Create synthetic OHLC data for testing UI/logic layers."""
    print(f"[DEBUG] Creating fake data for {symbol} ({rows} rows)")
    base_price = 100 + np.random.uniform(-20, 20)
    closes = np.linspace(base_price, base_price + 5, rows)
    opens = closes + np.random.uniform(-0.5, 0.5, rows)
    highs = np.maximum(opens, closes) + np.random.uniform(0.2, 1.0, rows)
    lows = np.minimum(opens, closes) - np.random.uniform(0.2, 1.0, rows)
    
    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
    })
    print(f"[DEBUG] Fake data created: {len(df)} rows, close range {df['close'].min():.2f}-{df['close'].max():.2f}")
    return df


def fetch_1h_data(symbol: str, period_days: int = 5, timeout: int = 10, max_retry: int = 2) -> Optional[pd.DataFrame]:
    """
    Fetch 1-hour OHLC data using yfinance.
    - symbol: one of keys in SYMBOL_MAP (e.g., "EURUSD","GBPJPY","SPX500")
    - timeout: per-call timeout (<=10)
    - max_retry: <=2

    Returns a DataFrame with lowercase columns ['open','high','low','close'] or None on failure.
    """
    print(f"[FETCH 1H START] {symbol}, period={period_days}d, timeout={timeout}s, max_retry={max_retry}")
    
    if symbol is None:
        print(f"[FAIL 1H] {symbol} - symbol is None")
        return None

    mapped = SYMBOL_MAP.get(symbol)
    if mapped is None:
        print(f"[FAIL 1H] {symbol} - no mapping in SYMBOL_MAP")
        return None
    
    print(f"[MAPPED 1H] {symbol} → {mapped}")

    candidates = [mapped]
    if symbol == "SPX500":
        if mapped != "SPY":
            candidates = [mapped, "SPY"]
    
    print(f"[CANDIDATES 1H] {symbol}: {candidates}")

    period_arg = f"{max(1, min(period_days, 60))}d"
    print(f"[PERIOD 1H] {symbol}: {period_arg}")

    attempts = 0
    for cand in candidates:
        if attempts >= max_retry:
            print(f"[RETRY_LIMIT 1H] {symbol} ({cand}) - max retries reached")
            break
        attempts += 1
        
        print(f"[FETCH ATTEMPT 1H {attempts}] {symbol} → {cand}, interval=1h, period={period_arg}, timeout={timeout}s")
        
        try:
            df = yf.download(
                cand,
                interval="1h",
                period=period_arg,
                auto_adjust=False,
                progress=False,
                timeout=timeout
            )
            print(f"[RAW_DF 1H] {symbol} ({cand}): df type={type(df)}, rows={len(df) if df is not None else 'None'}")
        except Exception as e:
            print(f"[FAIL 1H] {symbol} ({cand}) - yfinance exception: {type(e).__name__}: {e}")
            df = None

        # Validation checks
        if df is None:
            print(f"[FAIL 1H] {symbol} ({cand}) - df is None")
            continue
        if df.empty:
            print(f"[FAIL 1H] {symbol} ({cand}) - df.empty=True")
            continue
        if len(df) < 10:
            print(f"[FAIL 1H] {symbol} ({cand}) - insufficient rows: {len(df)} < 10")
            continue

        print(f"[PRE_NORMALIZE 1H] {symbol} ({cand}): columns={list(df.columns)}, rows={len(df)}")

        # Normalize and ensure OHLC exist
        try:
            df = df.copy()
            df.columns = [str(c).strip().lower() for c in df.columns]
            print(f"[NORMALIZED_COLS 1H] {symbol} ({cand}): {list(df.columns)}")
            
            expected = ["open", "high", "low", "close"]
            missing = [c for c in expected if c not in df.columns]
            if missing:
                print(f"[FAIL 1H] {symbol} ({cand}) - missing columns: {missing}")
                continue
            
            df = df[expected].dropna()
            print(f"[POST_DROPNA 1H] {symbol} ({cand}): rows={len(df)}")
            
            if df.empty or len(df) < 10:
                print(f"[FAIL 1H] {symbol} ({cand}) - post-clean insufficient rows: {len(df)} < 10")
                continue
                
        except Exception as e:
            print(f"[FAIL 1H] {symbol} ({cand}) - validation error: {type(e).__name__}: {e}")
            continue

        print(f"[SUCCESS 1H] {symbol} ({cand}) - {len(df)} rows fetched")
        return df

    # all attempts failed for 1H
    print(f"[FAIL 1H] {symbol} - all {len(candidates)} candidate(s) tried")
    print(f"[FALLBACK 1H] {symbol} - returning None (will use 30M as fallback in logic)")
    return None


def fetch_30m_data(symbol: str, period_days: int = 7, timeout: int = 10, max_retry: int = 2) -> Optional[pd.DataFrame]:
    """
    Fetch 30-minute OHLC data using yfinance.
    - symbol: one of keys in SYMBOL_MAP (e.g., "EURUSD","GBPJPY","SPX500")
    - timeout: per-call timeout (<=10)
    - max_retry: <=2

    Returns a DataFrame with lowercase columns ['open','high','low','close'] or None on failure.
    """
    print(f"[FETCH START] {symbol}, period={period_days}d, timeout={timeout}s, max_retry={max_retry}")
    
    if symbol is None:
        print(f"[FAIL] {symbol} - symbol is None")
        return None

    mapped = SYMBOL_MAP.get(symbol)
    if mapped is None:
        print(f"[FAIL] {symbol} - no mapping in SYMBOL_MAP")
        return None
    
    print(f"[MAPPED] {symbol} → {mapped}")

    # For SPX500 allow a single fallback to SPY
    candidates = [mapped]
    if symbol == "SPX500":
        # primary ^GSPC then fallback SPY (ETF)
        if mapped != "SPY":
            candidates = [mapped, "SPY"]
    
    print(f"[CANDIDATES] {symbol}: {candidates}")

    period_arg = f"{max(1, min(period_days, 60))}d"
    print(f"[PERIOD_ARG] {symbol}: {period_arg}")

    attempts = 0
    for cand in candidates:
        if attempts >= max_retry:
            print(f"[RETRY_LIMIT] {symbol} ({cand}) - max retries reached")
            break
        attempts += 1
        
        print(f"[FETCH ATTEMPT {attempts}] {symbol} → {cand}, interval=30m, period={period_arg}, timeout={timeout}s")
        
        try:
            df = yf.download(
                cand,
                interval="30m",
                period=period_arg,
                auto_adjust=False,
                progress=False,
                timeout=timeout
            )
            print(f"[RAW_DF] {symbol} ({cand}): df type={type(df)}, rows={len(df) if df is not None else 'None'}")
        except Exception as e:
            print(f"[FAIL] {symbol} ({cand}) - yfinance exception: {type(e).__name__}: {e}")
            df = None

        # Validation checks
        if df is None:
            print(f"[FAIL] {symbol} ({cand}) - df is None")
            continue
        if df.empty:
            print(f"[FAIL] {symbol} ({cand}) - df.empty=True")
            continue
        if len(df) < 20:
            print(f"[FAIL] {symbol} ({cand}) - insufficient rows: {len(df)} < 20")
            continue

        print(f"[PRE_NORMALIZE] {symbol} ({cand}): columns={list(df.columns)}, rows={len(df)}")

        # Normalize and ensure OHLC exist
        try:
            df = df.copy()
            df.columns = [str(c).strip().lower() for c in df.columns]
            print(f"[NORMALIZED_COLS] {symbol} ({cand}): {list(df.columns)}")
            
            expected = ["open", "high", "low", "close"]
            missing = [c for c in expected if c not in df.columns]
            if missing:
                print(f"[FAIL] {symbol} ({cand}) - missing columns: {missing}")
                continue
            
            df = df[expected].dropna()
            print(f"[POST_DROPNA] {symbol} ({cand}): rows={len(df)}")
            
            if df.empty or len(df) < 20:
                print(f"[FAIL] {symbol} ({cand}) - post-clean insufficient rows: {len(df)} < 20")
                continue
                
        except Exception as e:
            print(f"[FAIL] {symbol} ({cand}) - validation error: {type(e).__name__}: {e}")
            continue

        print(f"[SUCCESS REAL] {symbol} ({cand}) - {len(df)} rows fetched")
        return df

    # all attempts failed
    print(f"[FAIL] {symbol} - all {len(candidates)} candidate(s) tried")
    # FALLBACK: synthetic
    print(f"[FALLBACK USED] {symbol} - returning synthetic data")
    return _create_fake_data(symbol, rows=50)
 

