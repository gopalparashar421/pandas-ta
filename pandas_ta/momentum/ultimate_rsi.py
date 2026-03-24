# -*- coding: utf-8 -*-
from pandas import Series, DataFrame, concat
from pandas_ta.ma import ma
from pandas_ta.utils import get_offset, verify_series, signals
import numpy as np


def ultimate_rsi(close, length=14, ma_type1="wma", offset=0, **kwargs):
    """Ultimate RSI [LuxAlgo] based on dynamic momentum smoothing.

    Args:
        close (pd.Series): Series of close prices.
        length (int): Lookback period. Default: 14
        smooth (int): Smoothing period for the signal line. Default: 14
        ma_type1 (str): MA type for ARSI calc (rma, sma, ema, tma). Default: 'rma'
        ma_type2 (str): MA type for signal line. Default: 'ema'
        offset (int): Shift the result by 'offset'. Default: 0

    Kwargs:
        fillna (value): value to fill missing data
        fill_method (method): method to fill missing data

    Returns:
        pd.DataFrame: Ultimate RSI and Signal columns
    """

    # Validate and clean inputs
    close = verify_series(close, length)
    offset = get_offset(offset)
    if close is None: return

    # Step 1: Highest and Lowest over the period
    highest = close.rolling(length).max()
    lowest = close.rolling(length).min()
    range_ = highest - lowest

    # Step 2: Custom momentum logic
    delta = close.diff()
    # Conditions for diff
    cond1 = highest > highest.shift(1)
    cond2 = lowest < lowest.shift(1)

    # Apply conditions with correct precedence
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

    # Calculate num and den with correct MA
    num = ma(name=ma_type1, source=diff, length=length)
    den = ma(name=ma_type1, source=diff.abs(), length=length)

    # Compute ARSI
    ursi = (num / den) * 50 + 50

    # Offset
    if offset != 0:
        ursi = ursi.shift(offset)
        
    # Fill
    if "fillna" in kwargs:
        ursi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ursi.fillna(method=kwargs["fill_method"], inplace=True)

    # Naming
    ursi.name = f"ULT_RSI_{length}"
    ursi.category = "momentum"

    signal_indicators = kwargs.pop("signal_indicators", False)
    if signal_indicators:
        signalsdf = concat(
            [
                DataFrame({ursi.name: ursi}),
                signals(
                    indicator=ursi,
                    xa=kwargs.pop("xa", 70),
                    xb=kwargs.pop("xb", 30),
                    xserie=kwargs.pop("xserie", None),
                    xserie_a=kwargs.pop("xserie_a", None),
                    xserie_b=kwargs.pop("xserie_b", None),
                    cross_values=kwargs.pop("cross_values", False),
                    cross_series=kwargs.pop("cross_series", True),
                    offset=offset,
                ),
            ],
            axis=1,
        )

        return signalsdf
    else:
        return ursi
