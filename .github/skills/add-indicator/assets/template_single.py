"""
Template: Single-Column Indicator
Replace MYINDICATOR, myindicator, and {category} with your actual names.
This template produces a single Series output (e.g., RSI, ROC, SMA).
"""
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    v_drift,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series,
    v_talib,
)


def myindicator(
    close: Series,
    length: Int = None,
    scalar: IntFloat = None,
    # drift: Int = None,      # uncomment if indicator uses drift
    # mamode: str = None,     # uncomment if indicator accepts MA mode
    talib: bool = None,
    offset: Int = None,
    **kwargs: DictLike,
) -> Series:
    """MYINDICATOR (My Indicator Name)

    Brief one-line description.

    Longer description of what the indicator measures and its interpretation.

    Sources:
        https://example.com/reference-to-formula

    Parameters
    ----------
    close : Series
        'close' Series
    length : int, optional
        The period. Default: ``14``
    scalar : float, optional
        Scalar factor. Default: ``100``
    talib : bool, optional
        If ``True``, uses TA-Lib if installed. Default: ``True``
    offset : int, optional
        How many periods to offset the result. Default: ``0``

    Other Parameters
    ----------------
    fillna : value
        pd.DataFrame.fillna(value)

    Returns
    -------
    pd.Series
        1 column

    """
    # --- Validate Inputs ---
    length = v_pos_default(length, 14)
    # Minimum series length needed = length + 1 (for drift) or just length
    close = v_series(close, length + 1)
    if close is None:
        return

    scalar = v_scalar(scalar, 100)
    mode_tal = v_talib(talib)
    # drift = v_drift(drift)      # uncomment if needed
    offset = v_offset(offset)

    # --- Calculate ---
    if Imports["talib"] and mode_tal:
        # Optional: delegate to TA-Lib when available
        # from talib import MYINDICATOR as _tal_func
        # result = _tal_func(close, length)
        pass
    # else:  (always implement the pure-Python path)

    # ---- YOUR CALCULATION HERE ----
    # Example: simple momentum
    result = close.diff(length)
    # --------------------------------

    # --- Offset ---
    if offset != 0:
        result = result.shift(offset)

    # --- Fill NA (optional, driven by caller) ---
    if "fillna" in kwargs:
        result.fillna(kwargs["fillna"], inplace=True)

    # --- Name & Category ---
    result.name = f"MYINDICATOR_{length}"
    result.category = "{category}"  # e.g. "momentum"

    return result
