"""
Template: Multi-Column Indicator
Replace MYINDICATOR, myindicator, and {category} with your actual names.
This template produces a DataFrame output (e.g., MACD, Supertrend, Bollinger Bands).
"""
from pandas import DataFrame, Series, concat
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    v_offset,
    v_pos_default,
    v_scalar,
    v_series,
    v_talib,
)


def myindicator(
    high: Series,
    low: Series,
    close: Series,
    length: Int = None,
    multiplier: IntFloat = None,
    talib: bool = None,
    offset: Int = None,
    **kwargs: DictLike,
) -> DataFrame:
    """MYINDICATOR (My Indicator Name)

    Brief one-line description.

    Longer description: what each output column represents.

    Sources:
        https://example.com/reference-to-formula

    Parameters
    ----------
    high : Series
        'high' Series
    low : Series
        'low' Series
    close : Series
        'close' Series
    length : int, optional
        The period. Default: ``14``
    multiplier : float, optional
        Multiplier factor. Default: ``3.0``
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
    pd.DataFrame
        3 columns: MYINDICATOR_line1, MYINDICATOR_line2, MYINDICATOR_signal

    """
    # --- Validate Inputs ---
    length = v_pos_default(length, 14)
    multiplier = v_scalar(multiplier, 3.0)

    high = v_series(high, length)
    low = v_series(low, length)
    close = v_series(close, length)

    # Return None if ANY required series fails validation
    if high is None or low is None or close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # --- Calculate ---
    if Imports["talib"] and mode_tal:
        # Optional: delegate to TA-Lib when available
        pass

    # ---- YOUR CALCULATION HERE ----
    # Example: trivial placeholder calculations
    line1 = (high + low) / 2           # midpoint
    line2 = close.rolling(length).mean()  # SMA
    signal = line1 - line2             # difference
    # --------------------------------

    # --- Build result string (used in column names) ---
    _props = f"_{length}_{multiplier}"

    # --- Offset ---
    if offset != 0:
        line1 = line1.shift(offset)
        line2 = line2.shift(offset)
        signal = signal.shift(offset)

    # --- Assemble DataFrame ---
    data = {
        f"MYINDICATORl1{_props}": line1,
        f"MYINDICATORl2{_props}": line2,
        f"MYINDICATORs{_props}": signal,
    }
    df = DataFrame(data, index=close.index)

    # --- Fill NA (optional, driven by caller) ---
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    # --- Name & Category ---
    df.name = f"MYINDICATOR{_props}"
    df.category = "{category}"  # e.g. "volatility"

    return df
