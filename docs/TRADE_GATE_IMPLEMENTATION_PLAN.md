# Trade Gate — Implementation plan & review

**Date:** 2026-04-06  
**Last updated:** 2026-04-06  
**Status:** Implemented — see `docs/60_TRADE_GATE_VALIDATION_PLAN.md` (SSOT)

### Note (relationship to validation program)

This document covers **Trade Gate logic, UI, and docs** (PASS / BLOCK filter, strict conditions, column prominence).

**Filter validation across markets** (which assets load by default, Group A vs Group B, performance budget) is defined in:

- `docs/60_TRADE_GATE_VALIDATION_PLAN.md` (**single source of truth**)

**Do not** mix “more trades” goals with this phase—the product goal is a **reliable control filter**, not feature breadth.

**Principle:** Simplicity over flexibility; default load = **Group A only** (EURUSD, GBPJPY, SPX500, BTCUSD); Group B optional and off by default.

---

## Context

The main scanner lives in `YYY-Project-99-CFD-Story-Dashboard` (`app.py` builds rows from cached engine output: `stage_4h`, `stage_1h`, `bias_4h`, alignment). `YYY-Mini-CFD-Story-Dashboard` uses `ui/render.py` with fixed column ratios.

---

## [DADA] — Implementation plan (no code)

### Scope

- **Primary target:** `YYY-Project-99-CFD-Story-Dashboard` (Streamlit scanner table is the full “analysis” surface).
- **Secondary (if PM wants parity):** `YYY-Mini-CFD-Story-Dashboard` — same gate rule, add column + fix ratio alignment in `ui/render.py`.

### Trade Gate rule (derived from existing fields, no new fetch)

Compute **after** `run_engine_cached` / cached row is available, using last scalars already in cache:

- **Season not Range:** `int(stage_4h) != 0` (matches `market_stage.py`: UP=1, DOWN=-1, Range=0).
- **Momentum aligns with Season:** `int(stage_1h) == int(stage_4h)` and both non-zero (Wind same sign as Season; rejects neutral wind when season is directional, or any mismatch).
- **Alignment ≥ 2:** reuse the same **alignment** integer already computed (max of up-count vs down-count on `stage_4h`, `stage_1h`, `bias_4h`).

`trade_gate = "PASS"` iff all three; else `"BLOCK"`.

**Fail-fast:** if any required scalar missing / engine error / cache not `"ok"` → `"BLOCK"` (or a single explicit `"—"` only for loading rows if you want to distinguish “not yet computed” from “blocked”—PM can choose).

### Performance

- **O(1) per asset:** boolean checks on existing integers; no extra loops over OHLC.
- **No new dependencies.**
- Stays **<3s** if current scanner stays <3s (gate adds negligible CPU).

### UI

1. **Column:** `"Trade Gate"` with values **PASS** / **BLOCK** (and optional loading placeholder consistent with other columns).
2. **Prominence:** put **`Trade Gate` as the first data column** (after `Asset`), or first column overall—so it’s seen first; apply **strong styling** (e.g. green/red background via `Styler.apply` on that column only, bold text). Streamlit `dataframe` styling is enough; no new widgets.
3. **Header/row misalignment:**
   - **Project 99:** build `DataFrame` with **explicit column order** including `Trade Gate`; avoid duplicate partial/final tables fighting layout; verify `use_container_width` and **no extra index column** mismatch (consider `hide_index=True` if supported by your Streamlit version).
   - **Mini:** extend `SCANNER_COLUMN_RATIOS` and add **Trade Gate** in **both** `render_scanner_header` and `render_asset_row` in the **same** slot (same order as Project 99 for consistency).

### Documentation (same repo docs PM referenced)

- **`docs/00_DASHBOARD_GUIDE.md`:** new section “Trade Gate”; PASS vs BLOCK; **not** a signal; workflow PASS → TradingView, BLOCK → no action; warning banner that **this is not an entry signal**.
- **`docs/50_TRADING_LOGIC.md` (or quick reference):** formal definition of the three conditions; clarify difference from **Signal** column (narrative/alignment display) vs **qualified filter**.

### Testing (manual, fast)

- Spot-check: Season Range → BLOCK; Season Up + Wind Down → BLOCK; alignment 1 → BLOCK; aligned Up + alignment ≥ 2 → PASS.
- Confirm table columns line up header/body after change.

---

## [CHRIS] — Review

| Area | Verdict |
|------|--------|
| **Strategy alignment** | **Strong.** Gate is explicitly **filter-only** (PASS/BLOCK), uses **structure (Season/Wind)** and existing **alignment** score—matches “filter, not find” and no new indicators. |
| **Logic clarity** | **Confirm with PM:** “Momentum aligns with Season” is implemented as **`stage_1h == stage_4h`** (both non-zero). If PM intended **bias** or **only** directional agreement while allowing wind=0, rule must be adjusted—current spec reads as **wind must match season direction**. |
| **Edge cases** | **Loading vs BLOCK:** Loading rows should not show PASS; either `"—"` or spinner text—good UX. **Errors:** default BLOCK is fail-safe and matches PM. |
| **UI clarity** | **First column + color** satisfies “instant” PASS/BLOCK. Renaming or demoting **Signal** in copy/docs avoids implying Trade Gate is another signal—**docs requirement is critical.** |
| **Performance** | **Low risk**—pure reuse of cached integers. Watch only **styler** cost on large tables (usually negligible vs fetch). |
| **Header misalignment** | Plan correctly targets **explicit column order** and **Mini’s shared ratios**. For Streamlit, also verify **index column** and **styled vs unstyled** partial table use the same schema. |

**Recommendation:** Approve plan after PM confirms **Wind vs Season** equality is the intended momentum-alignment definition. **Do not implement** until PM approval.
