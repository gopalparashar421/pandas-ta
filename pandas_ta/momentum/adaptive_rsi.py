# -*- coding: utf-8 -*-
import numpy as np
from numba import njit
from pandas import Series
from pandas_ta.utils import (
    verify_series,
)

import numpy as np

from pandas_ta.utils._core import non_zero_range

@njit
def _adaptive_ma_numba(
    source,
    sc,
    length
):

    n = len(source)

    result = np.empty(n)

    result[:] = np.nan

    # ---------------------------------
    # Find valid initialization window
    # ---------------------------------
    init_sum = 0.0
    init_count = 0

    for i in range(length):

        val = source[i]

        if not np.isnan(val):

            init_sum += val
            init_count += 1

    if init_count == 0:
        return result

    result[length - 1] = (
        init_sum / init_count
    )

    # ---------------------------------
    # Recursive adaptive EMA
    # ---------------------------------
    for i in range(length, n):

        alpha = sc[i]

        if np.isnan(alpha):
            alpha = sc[i - 1]

        if np.isnan(alpha):
            alpha = 0.0

        prev = result[i - 1]

        x = source[i]

        # Handle source NaNs
        if np.isnan(x):

            result[i] = prev

        else:

            result[i] = (
                prev
                + alpha * (x - prev)
            )

    return result


def _adaptive_ma(source, sc, length=1):

    source_np = source.to_numpy(np.float64)

    # IMPORTANT FIX
    sc_np = (
        sc.bfill()
        .fillna(0.0)
        .to_numpy(np.float64)
    )

    result = _adaptive_ma_numba(
        source_np,
        sc_np,
        length
    )

    return Series(result, index=source.index)

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