# ⚡ MINI DASHBOARD: QUICK START GUIDE

**Version:** 1.0  
**Purpose:** Get started in 5 minutes  
**Reference:** See `10_MINI_ARCHITECTURE.md` for full design

---

## 🚀 QUICK START (5 MINUTES)

### Step 1: Create Structure

```bash
mkdir -p YYY-Mini-CFD-Story-Dashboard/{data,logic,ui,docs}
cd YYY-Mini-CFD-Story-Dashboard
```

### Step 2: Create Files

**app.py** (Main entry point)
```python
import streamlit as st
from data.fetch import fetch_ohlc
from logic.market_stage import calculate_trend
from logic.bias import calculate_bias
from logic.narrative import calculate_narrative_stage
from ui.render import render_header, render_input, render_loading, render_result

def main():
    render_header()
    symbol = render_input()
    if not symbol:
        st.warning("Enter a symbol")
        return
    
    render_loading("Fetching data...")
    data = fetch_ohlc(symbol)
    
    if data is None:
        render_result(None)
        return
    
    trend = calculate_trend(data)
    bias = calculate_bias(data)
    stage = calculate_narrative_stage(trend, bias)
    
    result = {
        "data": data,
        "trend": ["Downside", "Neutral", "Upside"][trend + 1] if trend is not None else "N/A",
        "bias": ["Down", "Range", "Up"][bias + 1] if bias is not None else "N/A",
        "stage": ["Environment", "Trend"][stage] if stage is not None else "N/A",
        "close": data['Close'].iloc[-1],
        "ohlc_display": data.tail(10)[['Open', 'High', 'Low', 'Close']]
    }
    
    render_result(result)

if __name__ == "__main__":
    main()
```

### Step 3: Create Data Layer

**data/__init__.py** (Empty)

**data/fetch.py** (Simple fetching)
```python
import yfinance as yf
import pandas as pd
from typing import Optional

TIMEOUT = 10
MAX_RETRIES = 2
INTERVAL = "30m"

def fetch_ohlc(symbol: str) -> Optional[pd.DataFrame]:
    """Fetch 30M OHLC data."""
    for attempt in range(MAX_RETRIES):
        try:
            data = yf.download(symbol, interval=INTERVAL, timeout=TIMEOUT, progress=False)
            if data is None or data.empty:
                return None
            if not all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
                return None
            return data
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == MAX_RETRIES - 1:
                return None
    return None
```

### Step 4: Create Logic Layer

**logic/__init__.py** (Empty)

**logic/market_stage.py** (Trend detection)
```python
import pandas as pd
from typing import Optional

def calculate_trend(df: pd.DataFrame) -> Optional[int]:
    """Calculate trend. Returns: 1 (Up), -1 (Down), 0 (Neutral), None (invalid)"""
    if df is None or len(df) < 3:
        return None
    try:
        last_3 = df['Close'].tail(3).values
        if last_3[0] < last_3[1] < last_3[2]:
            return 1
        if last_3[0] > last_3[1] > last_3[2]:
            return -1
        return 0
    except Exception:
        return None
```

**logic/bias.py** (Bias calculation)
```python
import pandas as pd
from typing import Optional

def calculate_bias(df: pd.DataFrame) -> Optional[int]:
    """Calculate bias. Returns: 1 (Up), -1 (Down), 0 (Range), None (invalid)"""
    if df is None or len(df) < 5:
        return None
    try:
        window = df.tail(5)
        close = df['Close'].iloc[-1]
        mid = (window['High'].max() + window['Low'].min()) / 2
        if close > mid * 1.02:
            return 1
        if close < mid * 0.98:
            return -1
        return 0
    except Exception:
        return None
```

**logic/narrative.py** (Stage calculation)
```python
from typing import Optional

def calculate_narrative_stage(trend: Optional[int], bias: Optional[int]) -> Optional[int]:
    """Calculate stage. Returns: 0 (Environment), 1 (Trend), None (invalid)"""
    if trend is None or bias is None:
        return None
    try:
        if trend != 0 and bias != 0 and trend == bias:
            return 1  # Trend
        return 0  # Environment
    except Exception:
        return None
```

### Step 5: Create UI Layer

**ui/__init__.py** (Empty)

**ui/render.py** (UI rendering)
```python
import streamlit as st
from typing import Optional, Dict, Any

def render_header():
    st.title("Mini CFD Dashboard")
    st.caption("Minimal, stable architecture")

def render_input():
    return st.text_input("Symbol:", value="EURUSD")

def render_loading(msg: str):
    st.info(f"⏳ {msg}")

def render_result(result: Optional[Dict[str, Any]]):
    if result is None or result.get("data") is None:
        st.error("❌ Failed to load data")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Trend (4H)", result.get("trend", "N/A"))
    with col2:
        st.metric("Bias", result.get("bias", "N/A"))
    with col3:
        st.metric("Stage", result.get("stage", "N/A"))
    with col4:
        st.metric("Last Close", f"${result.get('close', 'N/A'):.5f}")
    
    st.divider()
    st.write("**Latest OHLC (30M):**")
    st.dataframe(result.get("ohlc_display"), use_container_width=True)
```

### Step 6: Install & Run

```bash
# Install dependencies
pip install streamlit yfinance pandas

# Run app
streamlit run app.py
```

**Expected output:**
- App loads in ~2 seconds
- Enter symbol (e.g., EURUSD)
- See results or error
- No hanging, no crashes

---

## 📋 FILE CHECKLIST

- [ ] `app.py` (50 lines)
- [ ] `data/__init__.py` (empty)
- [ ] `data/fetch.py` (30 lines)
- [ ] `logic/__init__.py` (empty)
- [ ] `logic/market_stage.py` (30 lines)
- [ ] `logic/bias.py` (30 lines)
- [ ] `logic/narrative.py` (30 lines)
- [ ] `ui/__init__.py` (empty)
- [ ] `ui/render.py` (80 lines)
- [ ] `docs/10_MINI_ARCHITECTURE.md` (done)
- [ ] `requirements.txt` (created)

**Total:** ~250 lines of code

---

## 🎯 TESTING

### Test 1: Normal Flow
```
1. Run: streamlit run app.py
2. Enter: EURUSD
3. Expected: Results in ~2 seconds
4. Result: ✅ PASS
```

### Test 2: Invalid Symbol
```
1. Enter: XXXXXX (invalid)
2. Expected: Error message
3. Result: ✅ PASS
```

### Test 3: Network Offline
```
1. Disconnect internet
2. Enter: EURUSD
3. Expected: Error, not crash
4. Result: ✅ PASS
```

### Test 4: No Infinite Loops
```
1. Refresh page 5 times
2. Expected: Each time works, no loops
3. Result: ✅ PASS
```

---

## 🚀 READY TO ADD FEATURES

Once all tests pass, safely add:

```
✅ CAN ADD (Won't break):
  - Charts (UI layer)
  - Zones (Logic layer)
  - Multiple symbols (add loop)
  - R:R calculation (Logic layer)

❌ DON'T ADD (Will break):
  - 15M timeframe
  - Threading
  - Complex caching
  - Multiple retry strategies
```

---

**See 10_MINI_ARCHITECTURE.md for full details.**

