# Registration Reference

This document shows exactly which lines to edit across the three registration files when adding a new indicator.

---

## File 1: `pandas_ta/{category}/__init__.py`

Add two things — an import at the top and an entry in `__all__`. Keep alphabetical order.

```python
# existing imports ...
from .ema import ema
from .myindicator import myindicator   # ← ADD (alphabetical position)
from .sma import sma
# ...

__all__ = [
    "ema",
    "myindicator",                     # ← ADD (alphabetical position)
    "sma",
    # ...
]
```

---

## File 2: `pandas_ta/maps.py`

Find the `Category` dict. Add the indicator name string to the correct category list. Keep alphabetical order within the list.

```python
Category: Dict[str, ListStr] = {
    "momentum": [
        "ao", "apo", "bias",
        "myindicator",                 # ← ADD (alphabetical position)
        "rsi", "roc",
        # ...
    ],
    # other categories ...
}
```

---

## File 3: `pandas_ta/core.py`

Find the section of `AnalysisIndicators` for the category. Add a wrapper method. Keep related indicators grouped together.

### Wrapper patterns

**close-only indicator:**
```python
def myindicator(self, length=None, offset=None, **kwargs):
    close = self._get_column(kwargs.pop("close", "close"))
    from pandas_ta.{category} import myindicator
    result = myindicator(close=close, length=length, offset=offset, **kwargs)
    return self._post_process(result, **kwargs)
```

**open + close indicator:**
```python
def myindicator(self, length=None, offset=None, **kwargs):
    open_ = self._get_column(kwargs.pop("open", "open"))
    close = self._get_column(kwargs.pop("close", "close"))
    from pandas_ta.{category} import myindicator
    result = myindicator(open_=open_, close=close, length=length, offset=offset, **kwargs)
    return self._post_process(result, **kwargs)
```

**high + low + close indicator:**
```python
def myindicator(self, length=None, multiplier=None, offset=None, **kwargs):
    high = self._get_column(kwargs.pop("high", "high"))
    low = self._get_column(kwargs.pop("low", "low"))
    close = self._get_column(kwargs.pop("close", "close"))
    from pandas_ta.{category} import myindicator
    result = myindicator(high=high, low=low, close=close, length=length, multiplier=multiplier, offset=offset, **kwargs)
    return self._post_process(result, **kwargs)
```

**volume indicator (close + volume):**
```python
def myindicator(self, length=None, offset=None, **kwargs):
    close = self._get_column(kwargs.pop("close", "close"))
    volume = self._get_column(kwargs.pop("volume", "volume"))
    from pandas_ta.{category} import myindicator
    result = myindicator(close=close, volume=volume, length=length, offset=offset, **kwargs)
    return self._post_process(result, **kwargs)
```

---

## How to Find the Right Location in core.py

Search for a neighboring indicator in the same category to find where to insert the new method. For example, to add near RSI:

```
grep -n "def rsi" pandas_ta/core.py
```

Insert the new `def myindicator(...)` method adjacent to similar indicators.

---

## Verification

After completing all four steps, verify both access patterns work:

```python
import pandas as pd
import pandas_ta as ta

# Access pattern 1 — standalone function
result = ta.myindicator(df["close"], length=14)
print(result)

# Access pattern 2 — DataFrame extension
df.ta.myindicator(length=14, append=True)
print(df.columns)
```
