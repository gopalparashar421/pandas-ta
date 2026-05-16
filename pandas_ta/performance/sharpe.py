# -*- coding: utf-8 -*-
from numpy import sqrt
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import v_bool, v_offset, v_pos_default, v_scalar, v_series


def sharpe(
    close: Series,
    length: Int = None,
    risk_free: IntFloat = None,
    annualize: bool = None,
    periods: Int = None,
    offset: Int = None,
    **kwargs: DictLike,
) -> Series:
    """Sharpe Ratio

    The Sharpe Ratio measures the risk-adjusted return of an asset. It is
    calculated as the rolling mean excess return (above the risk-free rate)
    divided by the rolling standard deviation of returns, optionally
    annualized.

    Sources:
        * [Wikipedia](https://en.wikipedia.org/wiki/Sharpe_ratio)
        * Sharpe, W. F. (1966). Mutual Fund Performance. Journal of Business.

    Parameters:
        close (Series): ``close`` Series
        length (int): Rolling window size. Default: ``30``
        risk_free (float): Annualized risk-free rate as a decimal (e.g.
            ``0.04`` for 4%). Converted to a per-period rate internally.
            Default: ``0.0``
        annualize (bool): If ``True``, multiply the result by
            ``sqrt(periods)`` to annualize. Default: ``True``
        periods (int): Number of trading periods per year used for
            annualization and risk-free rate conversion. Default: ``252``
        offset (int): Post shift. Default: ``0``

    Other Parameters:
        fillna (value): ``pd.DataFrame.fillna(value)``

    Returns:
        (Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 30)
    close = v_series(close, length + 1)

    if close is None:
        return

    risk_free = v_scalar(risk_free, 0.0)
    annualize = v_bool(annualize, True)
    periods = v_pos_default(periods, 252)
    offset = v_offset(offset)

    # Calculate
    returns = close.pct_change()

    # Convert annualized risk-free rate to per-period rate
    rf_per_period = risk_free / periods

    excess_returns = returns - rf_per_period

    rolling_mean = excess_returns.rolling(length).mean()
    rolling_std = returns.rolling(length).std()

    result = rolling_mean / rolling_std

    if annualize:
        result = result * sqrt(periods)

    # Offset
    if offset != 0:
        result = result.shift(offset)

    # Fill
    if "fillna" in kwargs:
        result.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    result.name = f"SHARPE_{length}_{periods}"
    result.category = "performance"

    return result
