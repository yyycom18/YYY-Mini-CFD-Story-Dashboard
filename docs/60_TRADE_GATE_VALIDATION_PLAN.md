# Trade Gate — Validation plan (single source of truth)

**Version:** 1.0  
**Last updated:** 2026-04-06  
**Status:** Active — all Trade Gate and scanner loading changes must follow this document.

---

## Purpose

This phase is **not** about increasing trades or optimizing raw performance. It is about **validating whether the Trade Gate filter behaves reliably** across different liquid markets before expanding scope.

The dashboard is a **control system**: it **filters** whether context is qualified (PASS / BLOCK), not whether to enter a trade.

---

## What is Trade Gate?

Trade Gate is a **strict qualified-trade filter** (not a signal):

| State   | Meaning |
|--------|---------|
| **PASS** | All predefined conditions met — context is *qualified* for manual review elsewhere (e.g. TradingView). |
| **BLOCK** | Conditions not met — **not** qualified; do **not** treat as an entry trigger. |
| **—** | Data not ready / loading — **not** evaluated; **never** shown as BLOCK. |

**Strict momentum rule:** `stage_1h == stage_4h` and **both non-zero** (no neutral / weak wind for PASS).

**BLOCK must not** subsume loading: loading rows show **—**, not BLOCK.

---

## Qualified trade vs signal

| Concept | Provided? |
|--------|-----------|
| **Qualified trade (PASS)** | Yes — means the **filter** passed; still **not** an automated entry. |
| **Trade signal / entry signal** | **No** — the system does not provide entry timing, size, or execution. |

---

## User workflow

1. **PASS** → optional next step: open **TradingView** (or your chart) and apply **your** execution rules.  
2. **BLOCK** → **do nothing** with respect to this gate (no “trade because dashboard said so”).  
3. **—** → wait until the row finishes loading; do not interpret as PASS or BLOCK.

---

## Yahoo Finance symbol map (stable)

These mappings are the canonical user key → Yahoo symbol pairs:

| Key    | Yahoo symbol |
|--------|----------------|
| EURUSD | EURUSD=X |
| GBPJPY | GBPJPY=X |
| SPX500 | ^GSPC |
| BTCUSD | BTC-USD |

`SYMBOL_MAP` in each project must stay **consistent** with these keys (no duplicate tickers for the same instrument under different names).

---

## Asset grouping

### Group A — Primary validation set (default load)

| Asset  | Role |
|--------|------|
| EURUSD | Major FX |
| GBPJPY | Cross FX |
| SPX500 | Equity index (^GSPC) |
| BTCUSD | Crypto |

**Purpose:** Compare Trade Gate outcomes across **FX / index / crypto** with a **small, fixed** set.

### Group B — Secondary / risk control (optional)

- **XAUUSD** (known volatility / data quirks)  
- **Other** mapped symbols not in Group A (e.g. additional FX, HK50), as listed in code.

**Purpose:** Optional expansion and risk monitoring — **not** loaded by default so the system stays fast and stable.

---

## Rules

1. **Only Group A** is in the default scanner universe.  
2. **Group B** is **not** loaded unless the user **explicitly enables** it (e.g. sidebar toggle).  
3. **No additional fetch logic** — grouping only **selects which symbols** are iterated; each symbol is still fetched **once** per run/session rules as today.  
4. **Target:** remain responsive (design goal **&lt; ~3s** typical load for the default four assets; no deliberate heavy computation added).  
5. **Fail-fast:** bad or missing data → do not pretend PASS; use **BLOCK** or **—** per rules above.

---

## Why we limit default assets

- **Validation focus:** A small basket makes it possible to see whether PASS/BLOCK is **consistent** across regimes without noise from dozens of symbols.  
- **Stability:** Fewer default fetches means fewer failure modes and easier manual verification.  
- **Simplicity:** One default universe + one optional expansion keeps the **control** story clear.

---

## Performance considerations

- Grouping is **O(1)** selection over a fixed list — no extra market data pulls.  
- Caching remains **per symbol**; no duplicate fetch for the same key.  
- Trade Gate evaluation uses **already computed** engine outputs (or existing structure/metrics in Mini) — **no** new indicator stacks or heavy loops.

---

## Related documents

- `TRADE_GATE_IMPLEMENTATION_PLAN.md` — implementation notes for the Trade Gate column and UI (same repo).  
- Project 99: `docs/00_DASHBOARD_GUIDE.md` — user-facing dashboard copy (update when UX changes).

---

## Change control

Any future change to default universes, Yahoo symbols, or Trade Gate rules must:

1. Update **this file** first (or in the same PR).  
2. Keep **Group A / Group B** semantics or explicitly document a version bump and migration.
