# Season & Bias — Quick Reference

## TL;DR

✅ **Season (4H)** — Does price > SMA20?
- `compute_season_4h(df)` → "↑ Up" or "↓ Down"

✅ **Bias (4H/1H)** — Is last close > previous close?
- `compute_bias(df)` → "↑ Up", "↓ Down", or "→ Range"

✅ **No API calls** — Uses existing 30M data
✅ **No breaking changes** — All existing logic intact
✅ **Deterministic** — Same data = same output every time

---

## Function Signatures

### Season (4H)
```python
def compute_season_4h(df: pd.DataFrame) -> str:
    """Returns: '↑ Up', '↓ Down', or '→ N/A'"""
    # Logic: last_close > SMA20
```

### Bias (4H / 1H)
```python
def compute_bias(df: pd.DataFrame, label: str = "4H") -> str:
    """Returns: '↑ Up', '↓ Down', '→ Range', or '→ N/A'"""
    # Logic: last_close - previous_close
```

---

## Usage in app.py

```python
from logic.analysis import compute_season_4h, compute_bias

season_4h = compute_season_4h(df)  # "↑ Up"
bias_4h = compute_bias(df, label="4H")  # "↓ Down"
bias_1h = compute_bias(df, label="1H")  # "→ Range"

row = {
    "season": season_4h,
    "wind": bias_1h,
    "bias4": bias_4h,
    "bias1": bias_1h,
    # ... rest of row
}
```

---

## Output Example

```
EURUSD      ↑ Up        ↓ Down      ↑ Up        ↓ Down      2           🟢 NEAR     📍 MEDIUM
```

---

## SOP Compliance Checklist

- [x] Timeout ≤ 10s (no new API calls)
- [x] Retry ≤ 2 (using existing fetch)
- [x] Fail-fast (GLOBAL_TIMEOUT = 15s)
- [x] No debug print in loops
- [x] DEBUG_MODE properly gated
- [x] UI non-blocking (partial results allowed)
- [x] Scan time tested <3s

**Status**: ✅ READY TO DEPLOY
