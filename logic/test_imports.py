#!/usr/bin/env python
"""Quick test to verify Season and Bias functions work."""

import pandas as pd
import numpy as np
from analysis import compute_season_4h, compute_bias

# Create sample data
df = pd.DataFrame({
    "close": np.linspace(100, 110, 50)
})

print("[TEST] compute_season_4h...")
season = compute_season_4h(df)
print(f"  Result: {season}")
assert season in ["↑ Up", "↓ Down", "→ N/A"], f"Invalid season: {season}"

print("[TEST] compute_bias (4H)...")
bias = compute_bias(df, label="4H")
print(f"  Result: {bias}")
assert bias in ["↑ Up", "↓ Down", "→ Range", "→ N/A"], f"Invalid bias: {bias}"

print("[TEST] compute_bias (1H)...")
bias = compute_bias(df, label="1H")
print(f"  Result: {bias}")
assert bias in ["↑ Up", "↓ Down", "→ Range", "→ N/A"], f"Invalid bias: {bias}"

print("\n✅ All tests passed!")
