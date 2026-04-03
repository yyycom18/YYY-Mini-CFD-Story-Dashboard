# Trading Logic — Quick Reference

**For**: End users of the dashboard  
**Purpose**: Quick understanding of Season + Momentum

---

## Season (4H Proxy)

### What It Is
Direction of market structure (trend vs range)

### Calculation
Compares recent highs/lows to previous highs/lows

### Interpretation

| Signal | Meaning | Use For |
|--------|---------|---------|
| ↑ Up | Uptrend (HH + HL) | Buying bias |
| ↓ Down | Downtrend (LH + LL) | Selling bias |
| → Range | Mixed structure | Wait for clarity |
| → N/A | No data | Check connection |

---

## Momentum (1H Proxy)

### What It Is
Strength of recent price movement (conviction)

### Calculation
Counts bullish/bearish candles in last 5 bars + body sizes

### Interpretation

| Signal | Meaning | Use For |
|--------|---------|---------|
| ↑ Strong Up | Bullish candles, strong bodies | Confirm upside |
| ↓ Strong Down | Bearish candles, strong bodies | Confirm downside |
| → Weak / Range | Mixed candles, small bodies | Wait for conviction |
| → N/A | No data | Check connection |

---

## Reading Both Together

### Strong Signals (Aligned)
- **Season ↑ + Momentum ↑**: Strong upside → favorable for longs
- **Season ↓ + Momentum ↓**: Strong downside → favorable for shorts

### Caution Signals (Mismatch)
- **Season ↑ + Momentum Weak**: Uptrend losing steam → use caution
- **Season ↓ + Momentum Weak**: Downtrend losing steam → use caution

### Weak Signals
- **Season Range + Momentum Weak**: Indecision → avoid directional trades

---

## Other Metrics

| Metric | What It Shows |
|--------|---------------|
| Alignment | Agreement across timeframes (0-3, higher = better) |
| Proximity | Price distance from moving average (Near/Far) |
| Priority | Overall signal quality badge (HOT/WARM/MEDIUM/LOW) |

---

## Key Principles

### Pure Structure, Not Indicators
- Uses only highs, lows, opens, closes
- NO moving averages, NO oscillators
- Shows what market is doing now

### 30M Data Simulates Structure
- Faster and simpler than multi-timeframe
- Approximation, not perfection
- Verify on real chart before trading

### For Decision Support Only
- Not automatic trade signals
- Requires your own analysis
- Always manage risk

---

## Quick Decision Framework

**When to look for Longs**:
- Season ↑ Up + Momentum ↑ Strong Up
- Alignment is 3
- Price pulls back to support

**When to look for Shorts**:
- Season ↓ Down + Momentum ↓ Strong Down
- Alignment is 3
- Price bounces to resistance

**When to Wait**:
- Season → Range
- Momentum → Weak / Range
- Alignment is 0-1

**Always**:
- Check real chart for confirmation
- Identify support/resistance
- Plan entry and stop loss
- Risk only what you can afford to lose

---

## Limitations

- Uses 30M data (not perfect 4H/1H)
- Shows current structure, not future
- Cannot predict reversals
- No guarantee of accuracy
- Use with your own analysis

---

**For detailed explanation, see docs/50_TRADING_LOGIC.md**
