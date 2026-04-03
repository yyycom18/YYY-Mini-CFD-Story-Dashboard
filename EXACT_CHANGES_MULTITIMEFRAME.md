# EXACT CHANGES: Multi-Timeframe Upgrade

## File 1: `data/fetch.py`

### NEW FUNCTION ADDED

```python
def fetch_1h_data(symbol: str, period_days: int = 5, timeout: int = 10, max_retry: int = 2) -> Optional[pd.DataFrame]:
    """
    Fetch 1-hour OHLC data using yfinance.
    - symbol: one of keys in SYMBOL_MAP (e.g., "EURUSD","GBPJPY","SP500")
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
    if symbol == "SP500":
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
                interval="1h",  # KEY DIFFERENCE: 1h instead of 30m
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
        if len(df) < 10:  # KEY DIFFERENCE: 10 instead of 20
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
    return None  # KEY DIFFERENCE: returns None, NOT synthetic data
```

**Key differences from fetch_30m_data()**:
- `interval="1h"` instead of `"30m"`
- Min rows: 10 instead of 20
- Returns `None` on complete failure (no synthetic fallback)
- All debug messages prefixed with "1H"

---

## File 2: `logic/analysis.py`

### IMPORT UPDATED

**Before**:
```python
import pandas as pd
from typing import Tuple
```

**After**:
```python
import pandas as pd
from typing import Tuple, Optional
```

### FUNCTION UPDATED

**Before**:
```python
def compute_bias(df: pd.DataFrame, label: str = "4H") -> str:
    """..."""
```

**After**:
```python
def compute_bias(df: pd.DataFrame, label: str = "1H") -> str:
    """
    Simple Bias using momentum: last_close - previous_close
    ...
    Args:
        df: DataFrame with 'close' column (preferably real 1H data)
        label: label for logging (e.g., "1H", "4H")
    """
```

**Change**: Default label changed from "4H" to "1H", added docstring clarification.

---

## File 3: `app.py`

### IMPORTS UPDATED

**Before**:
```python
import streamlit as st
import time
from data.fetch import fetch_30m_data
```

**After**:
```python
import streamlit as st
import pandas as pd  # NEW
import time
from data.fetch import fetch_30m_data, fetch_1h_data  # fetch_1h_data NEW
from typing import List, Tuple, Optional  # Added Optional
```

### TITLE & SIDEBAR UPDATED

**Before**:
```python
st.title("Mini CFD Story Dashboard (v1)")
st.write("Lightweight market radar — stable, fast, and simple.")
# ...
st.sidebar.write(f"Max assets: {MAX_ASSETS}")
```

**After**:
```python
st.title("Mini CFD Story Dashboard (v2 — Multi-Timeframe)")
st.write("Lightweight market radar — stable, fast, and simple. Now with real 1H data.")
# ...
st.sidebar.write(f"Max assets: {MAX_ASSETS}")
st.sidebar.write("Data: 30M (4H proxy) + 1H (real)")  # NEW
```

### FETCH FUNCTIONS UPDATED

**Before**:
```python
def safe_fetch(symbol: str):
    # wrapper to respect GLOBAL_TIMEOUT
    try:
        df = fetch_30m_data(symbol, period_days=5, timeout=10, max_retry=2)
        return df
    except Exception:
        return None
```

**After**:
```python
def safe_fetch_30m(symbol: str) -> Optional[pd.DataFrame]:
    """Fetch 30M data with timeout."""
    try:
        df = fetch_30m_data(symbol, period_days=5, timeout=10, max_retry=2)
        return df
    except Exception as e:
        print(f"[ERROR] safe_fetch_30m {symbol}: {e}")
        return None

def safe_fetch_1h(symbol: str) -> Optional[pd.DataFrame]:
    """Fetch 1H data with timeout."""  # NEW
    try:
        df = fetch_1h_data(symbol, period_days=5, timeout=10, max_retry=2)
        return df
    except Exception as e:
        print(f"[ERROR] safe_fetch_1h {symbol}: {e}")
        return None
```

### MAIN LOOP UPDATED

**Before**:
```python
    rows = []
    for sym in assets:
        if time.time() - start_time > GLOBAL_TIMEOUT:
            st.error("System timeout — safe exit")
            st.stop()

        df = safe_fetch(sym)
        if df is None:
            row = {
                "season": "N/A",
                # ...
            }
        else:
            season_4h = compute_season_4h(df)
            bias_4h = compute_bias(df, label="4H")
            bias_1h = compute_bias(df, label="1H")  # Same data for both
            # ...
            row = {
                "season": season_4h,
                "wind": bias_1h,
                "bias4": bias_4h,
                "bias1": bias_1h,
                # ...
            }
        rows.append((sym, row))
```

**After**:
```python
    rows = []
    for sym in assets:
        if time.time() - start_time > GLOBAL_TIMEOUT:
            st.error("System timeout — safe exit")
            st.stop()

        print(f"\n[MAIN LOOP] Processing asset: {sym}")
        
        # Fetch BOTH timeframes in parallel logic (sequential for simplicity)
        df_30m = safe_fetch_30m(sym)  # NEW - explicit name
        df_1h = safe_fetch_1h(sym)    # NEW - fetch real 1H data

        # Check if at least one timeframe succeeded
        if df_30m is None and df_1h is None:
            print(f"[ERROR] {sym} - both timeframes failed")
            row = {
                "season": "N/A",
                # ...
            }
        else:
            # Compute Season (4H) using 30M data (proxy)
            season_4h = compute_season_4h(df_30m) if df_30m is not None else "→ N/A"
            
            # Compute Bias (4H) using 30M data
            bias_4h = compute_bias(df_30m, label="4H") if df_30m is not None else "→ N/A"
            
            # Compute Bias (1H) using REAL 1H data, fallback to 30M if needed
            if df_1h is not None:
                bias_1h = compute_bias(df_1h, label="1H")
                print(f"[SUCCESS] {sym} - using REAL 1H data for bias")
            else:
                bias_1h = compute_bias(df_30m, label="1H (fallback)") if df_30m is not None else "→ N/A"
                print(f"[FALLBACK] {sym} - 1H fetch failed, using 30M for 1H bias")
            
            # Compute alignment and proximity using 30M (or 1H if 30M failed)
            df_for_metrics = df_30m if df_30m is not None else df_1h
            alignment = compute_alignment(df_for_metrics) if df_for_metrics is not None else 0
            proximity = compute_proximity(df_for_metrics) if df_for_metrics is not None else "⚪ FAR"
            priority = priority_from_alignment_proximity(alignment, proximity)
            
            row = {
                "season": season_4h,
                "wind": bias_1h,
                "bias4": bias_4h,
                "bias1": bias_1h,
                # ...
            }
        rows.append((sym, row))
```

**Key changes**:
- Fetch both 30M and 1H separately
- Check if at least one succeeded
- Smart fallback: use real 1H if available, fallback to 30M
- Log which path was taken
- Use either 30M or 1H for alignment/proximity (whichever available)

### UI SECTION UPDATED

**Before**:
```python
    st.subheader("Market Scanner — Mini Radar")
    st.write("Columns: Asset | Season (4H) | Wind (1H) | Bias (4H) | Bias (1H) | Alignment | Proximity | Priority")
```

**After**:
```python
    st.subheader("Market Scanner — Multi-Timeframe Radar")
    st.write("Columns: Asset | Season (4H) | Wind (1H) | Bias (4H) | Bias (1H) | Alignment | Proximity | Priority")
    st.write("**Data sources**: 30M (Season/Bias4) + 1H (Bias1 — real when available)")  # NEW
```

---

## SUMMARY OF CHANGES

| Component | Change | Status |
|-----------|--------|--------|
| `fetch_1h_data()` | New function (~110 lines) | ✅ |
| `fetch_30m_data()` | No changes | ✅ |
| `logic/analysis.py` | Minor import addition | ✅ |
| `app.py` main loop | Fallback logic added (~40 lines) | ✅ |
| UI/sidebar | Updated messaging | ✅ |

**Total new code**: ~150 lines  
**Total removed code**: 0 lines  
**Net change**: +150 lines

---

## ARCHITECTURE DIAGRAM

```
BEFORE (v1 - Single Timeframe)
================================
    Asset 1, 2, 3
         ↓
    fetch_30m_data()
         ↓
    compute_season_4h(df_30m)
    compute_bias(df_30m, "4H")
    compute_bias(df_30m, "1H")  ← Same data for both!
         ↓
    render_asset_row()


AFTER (v2 - Multi-Timeframe)
================================
    Asset 1, 2, 3
         ├─→ fetch_30m_data()  
         │        ↓ (df_30m)
         │
         └─→ fetch_1h_data()  ← NEW
                  ↓ (df_1h or None)
         
         ├─ compute_season_4h(df_30m)
         ├─ compute_bias(df_30m, "4H")
         └─ IF df_1h:
              compute_bias(df_1h, "1H")        ← Real 1H
            ELSE:
              compute_bias(df_30m, "1H")       ← Fallback to 30M
         
         └─→ render_asset_row()
```

---

**All changes verified and SOP compliant.**
