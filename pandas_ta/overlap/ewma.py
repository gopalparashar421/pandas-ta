# -*- coding: utf-8 -*-
from numpy import log, sqrt
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import (
    v_bool,
    v_offset,
    v_pos_default,
    v_series,
)


def ewma(
    close: Series, length: Int = None,
    alpha: float = None, adjust: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Exponentially Weighted Moving Average (EWMA)

    EWMA applies a smoothing factor (alpha) to weight recent observations
    more heavily than older ones. Unlike EMA which derives alpha from a
    span period via alpha = 2 / (span + 1), EWMA accepts alpha directly,
    giving you precise control over the decay rate.

    When ``length`` is provided instead of ``alpha``, the smoothing factor
    is derived as ``alpha = 2 / (length + 1)``, matching the standard EMA
    formula.

    Sources:
        * [Pandas ewm](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html)
        * [Investopedia EMA](https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp)

    Parameters:
        close (Series): ``close`` Series
        length (int): The period used to derive alpha as 2/(length+1).
            Ignored when ``alpha`` is provided explicitly. Default: ``10``
        alpha (float): Direct smoothing factor in the range (0, 1].
            Overrides ``length`` when provided. Default: ``None``
        adjust (bool): Use adjusted EWMA (divide by decaying weights).
            Default: ``False``
        offset (int): Post shift. Default: ``0``

    Other Parameters:
        fillna (value): ``pd.DataFrame.fillna(value)``

    Returns:
        (Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)

    if close is None:
        return

    adjust = v_bool(adjust, False)
    offset = v_offset(offset)

    # Resolve alpha: explicit alpha takes precedence over length
    if alpha is not None:
        alpha = float(alpha)
        if not (0 < alpha <= 1):
            raise ValueError(
                f"[EWMA] alpha must be in the range (0, 1], got {alpha}"
            )
        label_param = f"a{alpha}"
    else:
        alpha = 2 / (length + 1)
        label_param = str(length)

    # Calculate
    result = close.ewm(alpha=alpha, adjust=adjust).mean()

    # Offset
    if offset != 0:
        result = result.shift(offset)

    # Fill
    if "fillna" in kwargs:
        result.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    result.name = f"EWMA_{label_param}"
    result.category = "overlap"

    return result


def ewma_vol(
    close: Series, lam: float = None,
    scalar: float = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """EWMA Volatility Estimator (RiskMetrics)

    Estimates time-varying volatility using the Exponentially Weighted Moving
    Average method from the RiskMetrics model (J.P. Morgan). The decay factor
    lambda controls how quickly older observations are discounted.

    Formula::

        ret      = log(close / close[1])
        ewma_var = EWM(ret^2, alpha=1-lambda)
        ewma_vol = sqrt(ewma_var) * scalar

    Sources:
        * RiskMetrics Technical Document (J.P. Morgan, 1996)
        * TradingView "EWMA Volatility Estimator" by piirsalu

    Parameters:
        close (Series): ``close`` Series
        lam (float): Decay factor lambda in the range (0, 1). Higher values
            weight history more heavily. Default: ``0.94`` (RiskMetrics daily)
        scalar (float): Multiplier applied to the volatility output.
            Default: ``100`` (converts to percentage)
        offset (int): Post shift. Default: ``0``

    Other Parameters:
        fillna (value): ``pd.DataFrame.fillna(value)``

    Returns:
        (Series): 1 column — EWMA volatility as a percentage
    """
    # Defaults and validation
    lam = float(lam) if lam is not None else 0.94
    if not (0 < lam < 1):
        raise ValueError(f"[EWMA_VOL] lam must be in the range (0, 1), got {lam}")
    scalar = float(scalar) if scalar is not None else 100.0
    offset = v_offset(offset)

    # Need at least 2 bars to compute a return
    close = v_series(close, 2)
    if close is None:
        return

    # Log returns → squared (variance proxy)
    ret = log(close / close.shift(1))
    sq_ret = ret ** 2

    # EWM variance using alpha = 1 - lambda (RiskMetrics formulation)
    alpha = 1.0 - lam
    ewma_var = sq_ret.ewm(alpha=alpha, adjust=False).mean()

    # Volatility estimate
    result = sqrt(ewma_var) * scalar

    # Offset
    if offset != 0:
        result = result.shift(offset)

    # Fill
    if "fillna" in kwargs:
        result.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    result.name = f"EWMA_VOL_{lam}"
    result.category = "volatility"

    return result
