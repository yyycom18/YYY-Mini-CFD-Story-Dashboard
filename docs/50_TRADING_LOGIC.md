Whenever logic changes, this document MUST be updated.

# Trading Logic (v1)

## Overview

This document describes the simple trading logic used in the Mini CFD Dashboard. The app is a decision-support radar that combines structure (Season / 4H proxy) and momentum (1H proxy derived from 30m candles) to surface market context quickly.

## Season (4H proxy)

- Purpose: Provide a structural view (Upside / Downside / Range) using recent highs/lows.
- Implementation: `detect_market_structure` examines recent highs and lows (small lookback). It returns:
  - `1` → Upside (higher-highs + higher-lows)
  - `-1` → Downside (lower-highs + lower-lows)
  - `0` → Range / Neutral
  - `None` → invalid / insufficient data
- Interpretation:
  - `↑ Up` → structural bias higher; align with momentum for stronger signals.
  - `↓ Down` → structural bias lower.
  - `→ Range` → no clear structure; prefer to avoid directional conviction.

## Momentum (1H proxy)

- Purpose: Capture short-term directional strength using only recent 30m candles (fast, indicator-free).
- Implementation: `detect_momentum(df)` (last 5 candles) returns:
  - `1` → strong up momentum
  - `-1` → strong down momentum
  - `0` → weak / range
  - `None` → invalid input
- Logic (v2):
  1. Take last 5 candles (open, close).
  2. Count bullish vs bearish candles (close > open).
  3. Compute candle body sizes and average body.
  4. Require:
     - Majority direction (≥3 bullish or ≥3 bearish)
     - At least 2 candles with body > average (strength)
  5. If both satisfied → return direction ±1; else 0.
- Interpretation:
  - `↑ Strong Up` = momentum aligns with buyers; higher priority if structure also up.
  - `↓ Strong Down` = momentum aligns with sellers.
  - `→ Weak / Range` = avoid or lower priority.

## Design Principles

- Use only 30m data (no external indicators) — fast and deterministic.
- Pure functions in `logic/` — no state, no caching.
- Fail-safe: functions return `None` or safe default when input invalid.
- Fast: analysis operates on last 5–20 rows only.

## Limitations

- Simplified heuristics — not a substitute for full technical analysis.
- Sensitive to candlestick noise in low-liquidity instruments.
- Recommended: treat outputs as decision support, not trade signals.

# Trading Logic: Season + Momentum

**Version**: 1.0  
**Date**: January 21, 2026  
**Audience**: Dashboard users (non-technical)

---

## 1. Overview

### What This Dashboard Is

This is a **Decision Support Tool**, not an automatic trading system.

The dashboard shows you:
- Market structure and direction (Season)
- Short-term momentum and strength (Wind/Momentum)
- Alignment of these signals (Priority)

You decide whether to trade or not.

### Design Philosophy

The dashboard is built on **Price Action** thinking:
- What the market is doing (structure)
- How strong the movement is (momentum)
- What the combination suggests

It does **NOT** use:
- Moving averages (SMA, EMA)
- Oscillators (RSI, MACD)
- Bollinger Bands
- Any other technical indicators

This means you're seeing pure market structure, not indicator interpretation.

### Why This Approach?

Technical indicators can lag the market because they are based on past data. Structure-based analysis (highs/lows, candle bodies) reflects what is happening **now**, not what happened last week.

---

## 2. Season (4H Proxy)

### What It Means

**Season** represents the higher timeframe directional bias.

Think of Season like asking: "What trend am I in?"

- If the market is making **higher highs and higher lows** → Uptrend (Season Up)
- If the market is making **lower highs and lower lows** → Downtrend (Season Down)
- If the market is **mixed** (one higher, one lower) → No clear trend (Season Range)

### How It's Calculated

The dashboard uses 30-minute candlestick data to approximate a 4-hour structure.

**The Logic:**

1. Look at the most recent high and low
2. Compare them to the previous swing high and low (from the last 5-10 candles back)
3. Determine if it's a higher high + higher low (uptrend), lower high + lower low (downtrend), or mixed (range)

**Example:**

```
Recent High: 1.0960
Previous High: 1.0955

Recent Low: 1.0940
Previous Low: 1.0935

Result:
- Recent High (1.0960) > Previous High (1.0955) ✓ Higher High
- Recent Low (1.0940) > Previous Low (1.0935) ✓ Higher Low
- Conclusion: UPTREND → Season = "↑ Up"
```

### What Each Season Means

#### ↑ Up (Upside Season)

**Market Structure**: Higher High + Higher Low

**What it means**:
- The market is in an uptrend
- Each swing is higher than the previous one
- Buyers are in control
- Trend is intact

**How to use it**:
- Bias toward looking for buying opportunities
- Watch for pullbacks to support levels
- Be cautious of short positions (against the trend)

#### ↓ Down (Downside Season)

**Market Structure**: Lower High + Lower Low

**What it means**:
- The market is in a downtrend
- Each swing is lower than the previous one
- Sellers are in control
- Trend is intact

**How to use it**:
- Bias toward looking for selling opportunities
- Watch for bounces to resistance levels
- Be cautious of long positions (against the trend)

#### → Range (Neutral Season)

**Market Structure**: Mixed (e.g., higher high but lower low, or vice versa)

**What it means**:
- No clear directional trend
- Market is consolidating or choppy
- Could be a reversal pattern forming
- No strong bias to either buyers or sellers

**How to use it**:
- Be cautious with directional trades
- Look for breakout patterns
- Consider waiting for clarity
- Trade the range boundaries if applicable

#### → N/A (No Data)

**What it means**:
- Insufficient data or error loading data
- Season cannot be determined

**How to use it**:
- Check your internet connection
- Wait for fresh data
- Do not trade with incomplete information

### Important: Season is NOT Timeframe Perfection

Season uses 30-minute data to approximate 4-hour structure. This is a simplification.

Why?
- **Stability**: Faster calculation, no multi-timeframe complexity
- **Speed**: Dashboard loads instantly
- **Reliability**: Fewer potential issues

What this means:
- Season is approximately 4H structure, not perfect 4H analysis
- For precise 4H analysis, check a real 4H chart
- Use Season as a reference, not the only source of truth

---

## 3. Wind / Momentum (1H Proxy)

### What It Means

**Momentum** (shown as "Wind") represents short-term strength and direction.

Think of Momentum like asking: "Is this move strong or weak right now?"

- Strong bullish candles with conviction → Strong Up momentum
- Strong bearish candles with conviction → Strong Down momentum
- No clear pattern → Weak or Range

### How It's Calculated

The dashboard analyzes the last 5 candles to detect momentum.

**The Logic:**

1. Count bullish candles (close > open) vs bearish candles (close < open)
2. Measure candle body sizes
3. If mostly bullish AND bodies are strong → Strong Up
4. If mostly bearish AND bodies are strong → Strong Down
5. Otherwise → Weak or Range

**What is a "Strong Body"?**

A candle has a strong body if it is **larger than average** compared to the last 5 candles.

**Example:**

```
Last 5 candles (30m data):
1. Close > Open (bullish), body = 10 pips
2. Close > Open (bullish), body = 15 pips
3. Close > Open (bullish), body = 12 pips
4. Close > Open (bullish), body = 18 pips
5. Close > Open (bullish), body = 14 pips

Bullish count: 5 (all bullish) ✓
Average body: (10+15+12+18+14) / 5 = 13.8 pips
Strong bodies: 4 out of 5 are > 13.8 pips ✓

Result: STRONG UP MOMENTUM
```

### What Each Momentum Means

#### ↑ Strong Up

**What it means**:
- Majority of recent candles are bullish (closes above opens)
- Candle bodies are large and decisive
- Buying pressure is strong
- Momentum is upward

**How to use it**:
- Confirms upside bias
- Look for pullback buying opportunities
- Trend likely to continue
- Good environment for long positions

**Caution**:
- Strong momentum can exhaust
- Watch for reversals after strong moves
- Don't blindly chase momentum

#### ↓ Strong Down

**What it means**:
- Majority of recent candles are bearish (closes below opens)
- Candle bodies are large and decisive
- Selling pressure is strong
- Momentum is downward

**How to use it**:
- Confirms downside bias
- Look for bounce selling opportunities
- Trend likely to continue
- Good environment for short positions

**Caution**:
- Strong momentum can exhaust
- Watch for reversals after strong moves
- Don't blindly chase momentum

#### → Weak / Range

**What it means**:
- Mixed candle direction (mix of bullish and bearish)
- Candle bodies are small or inconsistent
- No strong conviction in either direction
- Market is indecisive or consolidating

**How to use it**:
- No clear directional momentum
- Look for breakout patterns
- Consider waiting for momentum to strengthen
- Trade smaller positions if you trade at all

#### → N/A (No Data)

**What it means**:
- Insufficient data or error loading data
- Momentum cannot be determined

**How to use it**:
- Check your internet connection
- Wait for fresh data

### Important: Momentum is NOT Perfection

Momentum is calculated from 30-minute candle data, so it reflects 30-minute momentum, not perfectly 1-hour momentum.

Why?
- **Stability**: Simpler logic, fewer calculation points
- **Speed**: Instant execution
- **Stability**: Works with existing data

What this means:
- Momentum is approximately 1H strength, not perfect 1H momentum
- For precise 1H momentum, check a real 1H chart
- Use Momentum as a reference

---

## 4. Season + Momentum Combined

### How to Read Both Together

The dashboard shows both Season and Momentum to give you a complete picture.

#### Strong Signal: Season + Momentum Aligned

**Scenario 1: Both Up**
```
Season: ↑ Up (higher highs/lows, uptrend)
Momentum: ↑ Strong Up (bullish candles, strong bodies)

Interpretation: STRONG UPSIDE
- Market structure is up
- Recent strength is up
- Conviction is high
- Good environment for longs
```

**Scenario 2: Both Down**
```
Season: ↓ Down (lower highs/lows, downtrend)
Momentum: ↓ Strong Down (bearish candles, strong bodies)

Interpretation: STRONG DOWNSIDE
- Market structure is down
- Recent strength is down
- Conviction is high
- Good environment for shorts
```

#### Caution Signal: Season vs Momentum Mismatch

**Scenario 3: Season Up, Momentum Weak**
```
Season: ↑ Up (uptrend)
Momentum: → Weak / Range (mixed candles, small bodies)

Interpretation: UPTREND WITH LOSS OF MOMENTUM
- Structure is still up
- But momentum is fading
- Possible consolidation or reversal coming
- Use caution before longing
- Watch for break of structure
```

**Scenario 4: Season Down, Momentum Weak**
```
Season: ↓ Down (downtrend)
Momentum: → Weak / Range (mixed candles, small bodies)

Interpretation: DOWNTREND WITH LOSS OF MOMENTUM
- Structure is still down
- But momentum is fading
- Possible consolidation or reversal coming
- Use caution before shorting
- Watch for break of structure
```

#### Neutral Scenario: No Clear Signal

**Scenario 5: Both Neutral**
```
Season: → Range (mixed structure)
Momentum: → Weak / Range (mixed candles)

Interpretation: NO CLEAR DIRECTION
- No strong directional bias
- Market is indecisive
- Wait for breakout or momentum
- Avoid directional trades
- Consider sitting out
```

### Decision-Making Framework

Use Season and Momentum together to assess market bias:

| Season | Momentum | Signal Strength | Suggested Action |
|--------|----------|-----------------|------------------|
| ↑ Up | ↑ Strong Up | Very Strong | Favorable for longs |
| ↑ Up | → Weak / Range | Moderate | Use caution on longs |
| → Range | ↑ Strong Up | Moderate | Watch for breakout up |
| ↓ Down | ↓ Strong Down | Very Strong | Favorable for shorts |
| ↓ Down | → Weak / Range | Moderate | Use caution on shorts |
| → Range | → Weak / Range | Weak | Avoid directional trades |

---

## 5. Other Metrics (Reference)

The dashboard also shows additional information to help you understand the market:

### Alignment (0-3 Score)

**What it means**: How many timeframes are in agreement about direction.

- Score 3: Strong agreement (short-term, medium-term, longer-term all agree)
- Score 2: Moderate agreement
- Score 1-0: Weak agreement

**How to use it**: Higher alignment scores suggest more reliable signals.

### Proximity (Near / Far)

**What it means**: How close price is to moving average.

- 🟢 NEAR: Price is close to moving average (potential reversal zone)
- ⚪ FAR: Price is far from moving average (strong trend move)

**How to use it**: Can help identify pullback opportunities.

### Priority (HOT / WARM / MEDIUM / LOW)

**What it means**: Overall signal quality combining alignment and proximity.

- 🔥 HOT: Strong signal with alignment and proximity
- 📌 WARM: Strong signal but price is extended
- 📍 MEDIUM: Moderate signal
- ❄️ LOW: Weak signal

**How to use it**: Use as a quick filter for signal quality.

---

## 6. Key Design Principles

### Why 30-Minute Data for 4H Season?

The dashboard uses 30-minute OHLC data to calculate 4-hour structure.

**Rationale**:
- 30M is a reasonable proxy for 4H structure (8 x 30M = 4H)
- No need to fetch real 4H data (faster)
- Simpler system design (fewer complexity points)
- Still captures major structural changes

**Limitation**:
- Not perfectly 4-hour structure
- Use as approximation, not replacement for real 4H chart

### Why No Multi-Timeframe Fetching?

The dashboard deliberately avoids fetching multiple timeframes (30M + 1H + 4H).

**Rationale**:
- Simplicity: fewer moving parts
- Speed: dashboard loads in <15 seconds
- Stability: fewer potential data issues
- Focus on structure, not timeframe perfection

**How we work around it**:
- 30M data simulates 4H structure (Season)
- 1H data provides momentum (Wind)
- Combined view gives a reasonable approximation

### Pure Structure, Not Indicators

The dashboard uses only:
- Highs and lows (swing detection)
- Opens and closes (candle bodies)

No use of:
- Moving averages
- Oscillators
- Bands or channels
- Any other calculated indicators

**Why**:
- Structure is immediate (current market action)
- Indicators lag (based on past price)
- Structure aligns with how traders think

---

## 7. What This Dashboard Cannot Do

Important limitations to understand:

### Not Predictive

Season and Momentum show **what is happening now**, not what will happen next.

Just because the market is in an uptrend doesn't mean it will stay up forever.

### Not Entry/Exit Signals

The dashboard shows context, not trade execution signals.

You still need to:
- Identify support/resistance
- Plan entry price
- Plan stop loss
- Plan profit target
- Manage risk

### Not Perfect Structure Detection

Season is calculated from 30-minute data, which is a simplification of true 4-hour structure.

For precise structure analysis, check a real 4H chart.

### Not Replacement for Chart Analysis

The dashboard is a reference tool, not a replacement for looking at the actual chart.

Always verify any signal with visual chart analysis.

---

## 8. How to Use This Dashboard

### Step 1: Check Season

Ask yourself: **What trend am I in?**

- ↑ Up → Uptrend
- ↓ Down → Downtrend
- → Range → No clear trend

### Step 2: Check Momentum

Ask yourself: **How strong is current momentum?**

- ↑ Strong Up → Strong buying
- ↓ Strong Down → Strong selling
- → Weak / Range → Indecision

### Step 3: Assess Alignment

Ask yourself: **Are short-term and medium-term in agreement?**

- 3: Strong agreement → Reliable
- 2: Moderate agreement → Okay
- 1-0: Weak agreement → Use caution

### Step 4: Make Decision

Combine Season, Momentum, and Alignment to decide:
- **BUY bias**: Season Up + Momentum Up + High Alignment
- **SELL bias**: Season Down + Momentum Down + High Alignment
- **CAUTION**: Season doesn't match Momentum, or Alignment is weak
- **WAIT**: Season Range + Momentum Weak

### Step 5: Verify on Chart

Before any trade:
1. Look at the actual price chart
2. Identify support/resistance
3. Plan entry and exit
4. Manage risk

---

## 9. Limitations & Disclaimers

### Simplified System

This dashboard is intentionally simplified for speed and stability.

It does NOT account for:
- Volatility patterns
- Time of day effects
- News and events
- Macroeconomic factors
- Market sentiment
- Order flow
- Volume analysis

### Data Approximations

- Season is calculated from 30M data (not real 4H)
- Momentum is calculated from 30M data (not real 1H)
- Both are approximations for simplicity

### No Guarantee

This tool is for **decision support only**.

Past structure and momentum do not guarantee future performance.

**Your responsibility**:
- Never trade without proper risk management
- Never risk more than you can afford to lose
- Always verify signals with chart analysis
- Use this as one input among many
- Do your own due diligence

---

## 10. Future Updates

This documentation and the underlying logic may evolve as the dashboard improves.

Possible future enhancements:
- Improved momentum detection
- Zone support/resistance detection
- Liquidity level identification
- Multi-asset comparison

When logic changes, this documentation will be updated to reflect the new behavior.

---

## 11. Questions & Support

### Common Questions

**Q: Why doesn't Season change faster?**
A: Season uses the last 30 candles to avoid false signals. Quick changes would be noise, not structure.

**Q: Why do Season and Momentum sometimes disagree?**
A: They measure different things. Season is structure (macro), Momentum is recent strength (micro). Disagreement can signal reversal.

**Q: Can I trade just on this dashboard?**
A: Not recommended. Use it as one input. Always do your own analysis and risk management.

**Q: How often should I check the dashboard?**
A: Depends on your trading style. Scalpers might check every minute, swing traders every 4 hours.

---

## 12. Glossary

**Season**: Higher timeframe directional bias based on structure (HH/HL vs LH/LL)

**Momentum**: Short-term strength of price movement based on candle direction and body size

**Higher High (HH)**: Most recent swing high is above the previous swing high

**Higher Low (HL)**: Most recent swing low is above the previous swing low

**Lower High (LH)**: Most recent swing high is below the previous swing high

**Lower Low (LL)**: Most recent swing low is below the previous swing low

**Candle Body**: Distance between open and close price

**Bullish Candle**: Close above open (buyers win the session)

**Bearish Candle**: Close below open (sellers win the session)

**Trend**: Series of higher highs/lows (uptrend) or lower highs/lows (downtrend)

**Range**: Sideways movement with no clear directional trend

**Structure Break**: Price breaking the previous swing high or low

**Alignment**: Agreement between multiple timeframes or measures

---

**End of Documentation**

**Version**: 1.0  
**Last Updated**: January 21, 2026  
**Dashboard Version**: Mini CFD Dashboard v2
