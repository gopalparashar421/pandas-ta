# -*- coding: utf-8 -*-
from numpy import isnan, log
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_scalar, v_series


def garman_klass(
    open_: Series, high: Series, low: Series, close: Series,
    co_factor: float = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Garman-Klass Volatility

    A volatility estimator that uses open, high, low, and close prices.
    More efficient than close-to-close estimators.

    Sources:
        * Garman, M.B. and Klass, M.J. (1980). On the Estimation of Security
          Price Volatilities from Historical Data. Journal of Business, 53(1), 67-78.

    Parameters:
        open_ (Series): ``open`` Series
        high (Series): ``high`` Series
        low (Series): ``low`` Series
        close (Series): ``close`` Series
        co_factor (float): Close-Open scaling factor. Default: ``0.3863``
        offset (int): Post shift. Default: ``0``

    Other Parameters:
        fillna (value): ``pd.DataFrame.fillna(value)``

    Returns:
        (Series): 1 column
    """
    # Validate
    open_ = v_series(open_)
    high = v_series(high)
    low = v_series(low)
    close = v_series(close)

    if open_ is None or high is None or low is None or close is None:
        return

    co_factor = v_scalar(co_factor, 0.3863)
    offset = v_offset(offset)

    # Calculate
    valid = (high > low) & (open_ > 0) & (high > 0) & (low > 0) & (close > 0)

    hl = (high / low.where(valid, other=1.0)).apply(log).where(valid, other=0.0)
    co = (close / open_.where(valid, other=1.0)).apply(log).where(
        valid & (close != open_), other=0.0
    )
    gk = (0.5 * hl ** 2 - co_factor * co ** 2).clip(lower=0.0)

    if all(isnan(gk)):
        return  # Emergency Break

    # Offset
    if offset != 0:
        gk = gk.shift(offset)

    # Fill
    if "fillna" in kwargs:
        gk.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    gk.name = f"GK_{co_factor}"
    gk.category = "volatility"

    return gk