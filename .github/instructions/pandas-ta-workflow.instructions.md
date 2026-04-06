---
description: "Agent behavior when extending pandas-ta: adding indicators, models, or signals. Use when asked to add, implement, port, or create any new indicator or model in this package. Covers which files to touch, what to verify, and how to avoid breaking the existing API."
---

# pandas-ta — Extending the Package

## Always Load the Skill First

When adding any new indicator, load and follow the `add-indicator` skill. It contains templates, a step-by-step procedure, and a quality checklist specific to this codebase.

## Four Files Always Change

Adding an indicator always requires editing exactly these four locations. Never skip one:

1. `pandas_ta/{category}/{indicator_name}.py` — new module
2. `pandas_ta/{category}/__init__.py` — export the function
3. `pandas_ta/maps.py` — register in `Category` dict
4. `pandas_ta/core.py` — add wrapper method to `AnalysisIndicators`

If you only touch fewer than four, the indicator will not be discoverable via `df.ta.study()` or when running a category study.

## Category Selection

Pick the most specific category. When ambiguous:
- Uses price + volume → `volume`
- Measures variability/range → `volatility`  
- Detects direction → `trend`
- Rate of change, divergence, oscillator → `momentum`
- Smoothing or envelope → `overlap`

Do not create a new category. Use an existing one from `maps.py`.

## Verify Both Access Patterns Work

After implementing, always confirm:
```python
ta.indicator_name(series, **params)   # standalone — must work
df.ta.indicator_name(**params)        # DataFrame extension — must work
```

## Never Break Existing Signatures

- Existing function signatures are public API. Do not rename, reorder, or remove parameters.
- New parameters must have defaults and be added at the end before `**kwargs`.
- Do not change existing column name formats — downstream code may depend on them.

## Do Not Add Unnecessary Dependencies

- Do not add new `pip` dependencies. Use only what is already in `pyproject.toml` (`pandas`, `numpy`, `numba`, `tqdm`).
- Optional TA-Lib support is allowed, always behind the `Imports["talib"]` guard.

## Docstring Is Required

Every indicator function must have a docstring with at minimum:
- One-line summary
- `Sources:` section with a URL or citation for the formula
- `Parameters` section
- `Returns` section describing the column(s)
