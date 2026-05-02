# -*- coding: utf-8 -*-
import numpy as np
from numba import njit
from pandas import DataFrame, Series

from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import (
    v_pos_default,
    v_series,
    non_zero_range,
    zero
)
from pandas_ta.volatility import atr

@njit
def _adaptive_ma_numba(
    source,
    sc,
    length
):

    n = len(source)

    result = np.empty(n)

    result[:] = np.nan

    init = 0.0

    for i in range(length):
        init += source[i]

    result[length - 1] = init / length

    for i in range(length, n):

        alpha = sc[i]

        prev = result[i - 1]

        result[i] = (
            prev
            + alpha * (source[i] - prev)
        )

    return result

def _adaptive_ma(source, sc, length=1):

    result = _adaptive_ma_numba(
        source.to_numpy(np.float64),
        sc.to_numpy(np.float64),
        length
    )

    return Series(result, index=source.index)


def adaptive_adx(
    high: Series,
    low: Series,
    close: Series,
    length: Int = None,
    fast: Int = None,
    slow: Int = None,
    **kwargs: DictLike
) -> DataFrame:
    """Average Directional Movement (Adaptive KAMA Version)

    Adaptive mode replaces fixed smoothing with
    Kaufman Efficiency Ratio adaptive smoothing.

    Parameters:
        adaptive (bool): Enable adaptive smoothing.
            Default: False

        er_length (int): Efficiency Ratio lookback.
            Default: 10

        fast (int): Fast smoothing bound.
            Default: 2

        slow (int): Slow smoothing bound.
            Default: 30
    """

    # -------------------------------------------------
    # Validate
    # -------------------------------------------------
    length = v_pos_default(length, 10)
    fast = v_pos_default(fast, 2)
    slow = v_pos_default(slow, 10)
    high = v_series(high, length)
    low = v_series(low, length)
    close = v_series(close, length)
    drift = 1
    scalar = 100

    if high is None or low is None or close is None:
        return

    # -------------------------------------------------
    # ATR
    # -------------------------------------------------
    
    atr_ = atr(
        high=high,
        low=low,
        close=close,
        length=length,
        prenan=kwargs.pop("prenan", True)
    )

    if atr_ is None or all(np.isnan(atr_)):
        return

    k = scalar / atr_

    # -------------------------------------------------
    # Directional Movement
    # -------------------------------------------------
    up = high - high.shift(drift)
    dn = low.shift(drift) - low

    pos = ((up > dn) & (up > 0)) * up
    neg = ((dn > up) & (dn > 0)) * dn

    pos = pos.apply(zero)
    neg = neg.apply(zero)

    # ---------------------------------------------
    # KAMA Smoothing Constant
    # ---------------------------------------------
    def weight(length: int) -> float:
        return 2 / (length + 1)

    fr = weight(fast)
    sr = weight(slow)

    abs_diff = non_zero_range(close, close.shift(length)).abs()
    peer_diff = non_zero_range(close, close.shift(drift)).abs()
    peer_diff_sum = peer_diff.rolling(length).sum()
    er = abs_diff / peer_diff_sum
    x = er * (fr - sr) + sr
    sc = x * x

    # ---------------------------------------------
    # Adaptive Smoothing
    # ---------------------------------------------
    dmp_raw = pos
    dmn_raw = neg

    dmp_smoothed = _adaptive_ma(
        dmp_raw,
        sc,
        length
    )

    dmn_smoothed = _adaptive_ma(
        dmn_raw,
        sc,
        length
    )

    dmp = k * dmp_smoothed
    dmn = k * dmn_smoothed

    dx = (
        scalar
        * (dmp - dmn).abs()
        / (dmp + dmn)
    )

    adx = _adaptive_ma(
        dx,
        sc,
        length
    )

    # -------------------------------------------------
    # Fill
    # -------------------------------------------------
    if "fillna" in kwargs:

        adx.fillna(kwargs["fillna"], inplace=True)

        dmp.fillna(kwargs["fillna"], inplace=True)

        dmn.fillna(kwargs["fillna"], inplace=True)

    # -------------------------------------------------
    # Name and Category
    # -------------------------------------------------

    adx.name = f"ADAPTIVE_ADX_{length}"

    dmp.name = f"ADAPTIVE_DMP_{length}"

    dmn.name = f"ADAPTIVE_DMN_{length}"

    adx.category = dmp.category = dmn.category = "trend"

    # -------------------------------------------------
    # DataFrame
    # -------------------------------------------------
    data = {
        adx.name: adx,
        dmp.name: dmp,
        dmn.name: dmn
    }

    df = DataFrame(data, index=close.index)

    df.name = f"ADAPTIVE_ADX_{length}"

    df.category = "trend"

    return df