---
description: "Coding conventions for the pandas-ta package. Use when writing, editing, or reviewing any indicator module, category __init__.py, maps.py, or core.py. Covers imports, validation, naming, return types, and error handling."
---

# pandas-ta Coding Conventions

## Imports — Required Order

```python
# 1. stdlib (none in most indicators)
# 2. pandas
from pandas import DataFrame, Series

# 3. internal typing
from pandas_ta._typing import DictLike, Int, IntFloat

# 4. internal maps (only when using Imports or Category)
from pandas_ta.maps import Imports

# 5. internal MA helper (only when indicator uses moving averages)
from pandas_ta.ma import ma

# 6. internal utils — only import what you use
from pandas_ta.utils import v_drift, v_offset, v_pos_default, v_series, v_talib
```

Never import from outside pandas-ta unless it is inside an `if Imports["talib"] and mode_tal:` guard.

## Function Signatures

- Last parameter is always `**kwargs: DictLike`
- Series inputs come first, then numeric params, then flags, then `offset`, then `**kwargs`
- Use type hints from `pandas_ta._typing` for all non-Series parameters

```python
def myindicator(
    close: Series,
    length: Int = None,
    scalar: IntFloat = None,
    talib: bool = None,
    offset: Int = None,
    **kwargs: DictLike,
) -> Series:          # or DataFrame for multi-output
```

## Input Validation — Rules

- Always validate with `v_*` helpers. Never write manual `if isinstance(...)` guards inline.
- Call `v_series(series, min_length)` for every Series input. Pass the minimum number of rows needed.
- **Return `None` (not `raise`) when validation fails.** All callers expect `None` on bad input.
- Validate all numeric params before the series so defaults are set before `v_series` uses them.

```python
length = v_pos_default(length, 14)       # set default first
close = v_series(close, length + 1)      # then validate series
if close is None:                         # guard after every v_series call
    return
```

For multi-series indicators, check all series before any calculation:
```python
if high is None or low is None or close is None:
    return
```

## Calculation

- Use `pandas_ta.ma` for moving averages instead of calling `.rolling().mean()` directly when the mode is user-configurable (`mamode`).
- Wrap TA-Lib calls in `if Imports["talib"] and mode_tal:`. Always provide a pure-Python fallback.

## Offset and Fill — Apply at the End, Always

```python
if offset != 0:
    result = result.shift(offset)          # Series
    # or: df = df.shift(offset)            # DataFrame

if "fillna" in kwargs:
    result.fillna(kwargs["fillna"], inplace=True)
```

## Naming and Category Attributes

Every result **must** have these two attributes set before returning:

```python
result.name = f"INDICATOR_{param1}_{param2}"   # UPPERCASE indicator name
result.category = "momentum"                    # lowercase category string
```

Column name format for DataFrame returns: `f"INDICATORabbrev{_props}"` where `_props = f"_{p1}_{p2}"`.

## Return Type

| Outputs | Return type |
|---|---|
| 1 column | `Series` |
| 2+ columns | `DataFrame` — build with a `dict` keyed by column names, then `DataFrame(data, index=close.index)` |

## Registration — Keep Alphabetical Order

When updating `category/__init__.py` or `maps.py`, insert new entries in alphabetical order within their existing sorted list. Do not sort the whole list — only find the correct insertion point.

## core.py Wrappers

- Use `self._get_column(kwargs.pop("col", "col"))` — use `pop`, not `get`, so the kwarg is not forwarded twice.
- Mirror the standalone function's parameters exactly (minus Series inputs, which come from `_get_column`).
- Always end with `return self._post_process(result, **kwargs)`.
