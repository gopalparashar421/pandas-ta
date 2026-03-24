# -*- coding: utf-8 -*-
from pandas_ta import Imports
from pandas_ta.utils import get_offset, verify_series


def hlcc4(high, low, close, talib=None, offset=None, **kwargs):
    """Indicator: HLC3"""
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = 2*(verify_series(close))
    offset = get_offset(offset)

    hlcc4 = (high + low + close) / 4.0

    # Offset
    if offset != 0:
        hlcc4 = hlcc4.shift(offset)

    # Name & Category
    hlcc4.name = "hlcc4"
    hlcc4.category = "overlap"

    return hlcc4
