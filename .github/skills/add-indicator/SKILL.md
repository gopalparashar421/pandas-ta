---
name: add-indicator
description: "Add a new technical analysis indicator or model to the pandas-ta Python package. Use when: implementing a new indicator, adding a new signal, creating a new model, extending pandas-ta with custom calculations. Produces a fully-integrated indicator accessible via both ta.indicator() and df.ta.indicator()."
argument-hint: "Describe the indicator to add (name, category, inputs, outputs)"
---

# Add Indicator to pandas-ta

## When to Use
- Adding a new technical indicator (e.g., a custom RSI variant, a new oscillator)
- Implementing a financial model or signal generator
- Porting an indicator from another library or paper

## Decision Points Before You Start

### 1. Choose a Category
| Category | Use for |
|---|---|
| `momentum` | Oscillators, divergence signals, rate-of-change |
| `overlap` | Moving averages, smoothing, envelope bands |
| `volatility` | ATR-based, Bollinger-type, standard deviation measures |
| `volume` | On-balance, accumulation/distribution, volume-weighted |
| `trend` | Trend detection, direction, ADX-type |
| `statistics` | Pure statistical: skew, kurtosis, z-score |
| `performance` | Return-based: log return, drawdown |
| `cycle` | Cycle analysis, dominant cycle |
| `candle` | Candlestick patterns |

### 2. Choose Return Type
- **`Series`** — single output column (e.g., RSI, ROC, SMA)
- **`DataFrame`** — multiple output columns (e.g., MACD → signal + histogram, Supertrend → trend + direction + long + short)

---

## Step-by-Step Procedure

### Step 1 — Create the Indicator Module

Create `pandas_ta/{category}/{indicator_name}.py`.

Follow the **Single-Column Template** or **Multi-Column Template** in `./assets/`.

**Mandatory elements:**
1. Import only from `pandas`, `pandas_ta._typing`, `pandas_ta.maps`, `pandas_ta.ma`, and `pandas_ta.utils`
2. Validate ALL inputs with `v_*` helpers before any calculation
3. Return `None` (not raise) when validation fails (insufficient data)
4. Assign `.name` as `f"INDICATOR_{param1}_{param2}"` (uppercase indicator name)
5. Assign `.category` as the string category name

**Validation helpers** (import from `pandas_ta.utils`):

| Helper | Purpose | Default |
|---|---|---|
| `v_series(series, min_length)` | Validate Series has enough rows | returns `None` |
| `v_pos_default(var, default)` | Validate positive int/float param | positive int |
| `v_int(var, default, ne)` | Validate int, not equal to `ne` | int |
| `v_drift(var)` | Validate drift param | `1` |
| `v_offset(var)` | Validate offset param | `0` |
| `v_scalar(var, default)` | Validate scalar (float) | `float` |
| `v_mamode(var, default)` | Validate MA mode string | string |
| `v_talib(var)` | Validate talib bool flag | `True` |
| `v_bool(var, default)` | Validate boolean | bool |

**Optional talib integration pattern:**
```python
from pandas_ta.maps import Imports
mode_tal = v_talib(talib)
if Imports["talib"] and mode_tal:
    from talib import INDICATOR_FUNC
    result = INDICATOR_FUNC(close, length)
else:
    # custom calculation
```

**Offset and fill pattern (apply at the end, always):**
```python
if offset != 0:
    result = result.shift(offset)
if "fillna" in kwargs:
    result.fillna(kwargs["fillna"], inplace=True)
```

---

### Step 2 — Export from Category Package

Edit `pandas_ta/{category}/__init__.py`:

```python
# Add to imports (alphabetical order)
from .{indicator_name} import {indicator_name}

# Add to __all__ list (alphabetical order)
__all__ = [
    ...,
    "{indicator_name}",
    ...
]
```

---

### Step 3 — Register in Category Map

Edit `pandas_ta/maps.py` — add to the `Category` dict under the correct key (keep alphabetical order within the list):

```python
Category: Dict[str, ListStr] = {
    "{category}": [
        ...,
        "{indicator_name}",   # ← insert alphabetically
        ...
    ],
    ...
}
```

---

### Step 4 — Add Wrapper in core.py

Edit `pandas_ta/core.py` — find the section for the category (search for `# Section: {Category}` or look for neighboring indicators). Add a method to the `AnalysisIndicators` class:

**Single-series input (e.g., close-only):**
```python
def {indicator_name}(self, length=None, offset=None, **kwargs):
    close = self._get_column(kwargs.pop("close", "close"))
    from pandas_ta.{category} import {indicator_name}
    result = {indicator_name}(close=close, length=length, offset=offset, **kwargs)
    return self._post_process(result, **kwargs)
```

**Multi-series input (e.g., high/low/close):**
```python
def {indicator_name}(self, length=None, offset=None, **kwargs):
    high = self._get_column(kwargs.pop("high", "high"))
    low = self._get_column(kwargs.pop("low", "low"))
    close = self._get_column(kwargs.pop("close", "close"))
    from pandas_ta.{category} import {indicator_name}
    result = {indicator_name}(high=high, low=low, close=close, length=length, offset=offset, **kwargs)
    return self._post_process(result, **kwargs)
```

**Rules:**
- Use `self._get_column(kwargs.pop("column_name", "column_name"))` for each OHLCV input
- Mirror the standalone function's parameters exactly (excluding series inputs)
- Always end with `return self._post_process(result, **kwargs)`

---

## Checklist — Quality Criteria

Before considering the indicator complete, verify:

- [ ] Module file exists at `pandas_ta/{category}/{indicator_name}.py`
- [ ] Function signature uses `**kwargs: DictLike` as last parameter
- [ ] All inputs validated with `v_*` helpers; returns `None` on failure
- [ ] Calculation is correct (cross-check formula with source)
- [ ] `result.name` is set (format: `INDICATOR_params`)
- [ ] `result.category` is set
- [ ] Offset applied: `result.shift(offset)` when `offset != 0`
- [ ] `fillna` handled from kwargs
- [ ] Exported in `{category}/__init__.py` (import + `__all__`)
- [ ] Registered in `maps.py` `Category` dict
- [ ] Wrapper method added to `AnalysisIndicators` in `core.py`
- [ ] Both access patterns work: `ta.{name}(series)` and `df.ta.{name}()`

---

## Reference Files

- [Single-column indicator template](./assets/template_single.py)
- [Multi-column indicator template](./assets/template_multi.py)
- [Registration reference](./references/registration.md)
