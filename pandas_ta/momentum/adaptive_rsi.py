# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta.utils import (
    verify_series,
)

import numpy as np

from pandas_ta.utils._core import non_zero_range

def _adaptive_ma(
    source: Series,
    sc: Series,
    length: int
) -> Series:
    """
    Adaptive EMA using dynamic smoothing constant
    """

    result = source.copy().astype(float)

    if len(result) == 0:
        return result

    result.iloc[:length - 1] = np.nan

    # initialize
    result.iloc[length - 1] = (
        source.iloc[:length].mean()
    )

    for i in range(length, len(source)):

        prev = result.iloc[i - 1]

        alpha = sc.iloc[i]

        result.iloc[i] = (
            prev
            + alpha * (source.iloc[i] - prev)
        )

    return result

def adaptive_rsi(
    close,
    length=14,
    fast=2,
    slow=30,
    **kwargs
):
    """
    Ultimate RSI [LuxAlgo] with optional
    KAMA adaptive smoothing.
    """

    # -----------------------------------
    # Validate Inputs
    # -----------------------------------
    close = verify_series(close, length)

    if close is None:
        return

    # -----------------------------------
    # Highest / Lowest
    # -----------------------------------
    highest = close.rolling(length).max()

    lowest = close.rolling(length).min()

    range_ = highest - lowest

    # -----------------------------------
    # Custom Momentum Logic
    # -----------------------------------
    delta = close.diff()

    cond1 = highest > highest.shift(1)

    cond2 = lowest < lowest.shift(1)

    diff = np.where(
        cond1,
        range_,
        np.where(
            cond2,
            -range_,
            delta
        )
    )

    diff = Series(diff, index=close.index)

    # ---------------------------------------------
    # KAMA Smoothing Constant
    # ---------------------------------------------
    def weight(length: int) -> float:
        return 2 / (length + 1)

    fr = weight(fast)
    sr = weight(slow)

    abs_diff = non_zero_range(close, close.shift(length)).abs()
    peer_diff = non_zero_range(close, close.shift(1)).abs()
    peer_diff_sum = peer_diff.rolling(length).sum()
    er = abs_diff / peer_diff_sum
    x = er * (fr - sr) + sr
    sc = x * x

    num = _adaptive_ma(
        source=diff,
        sc=sc,
        length=length
    )

    den = _adaptive_ma(
        source=diff.abs(),
        sc=sc,
        length=length
    )

    # -----------------------------------
    # Adaptive RSI
    # -----------------------------------
    arsi = (num / den) * 50 + 50

    # -----------------------------------
    # Fill
    # -----------------------------------
    if "fillna" in kwargs:

        arsi.fillna(
            kwargs["fillna"],
            inplace=True
        )

    if "fill_method" in kwargs:

        arsi.fillna(
            method=kwargs["fill_method"],
            inplace=True
        )

    # -----------------------------------
    # Naming
    # -----------------------------------
    arsi.name = f"ADAPTIVE_RSI_{length}"

    arsi.category = "momentum"

    return arsi