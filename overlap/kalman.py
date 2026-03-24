from numpy import zeros
from pandas import Series
from numba import jit

@jit(nopython=True, fastmath=True)
def kalman_filter(data, process_noise=1e-4, measurement_noise=1e-2):
    """
    Optimized Kalman filter using Numba for speed
    """
    n = len(data)
    filtered = zeros(n)

    x = data[0]
    P = 1.0

    for i in range(n):
        # Prediction
        x_pred = x
        P_pred = P + process_noise

        # Update
        K = P_pred / (P_pred + measurement_noise)
        x = x_pred + K * (data[i] - x_pred)
        P = (1 - K) * P_pred

        filtered[i] = x

    return filtered


def _noise_from_tick_size(tick_size):
    """Derive Kalman noise parameters from a symbol's tick_size.

    The tick_size represents the minimum price increment for a given futures
    contract.  Larger tick sizes (e.g. 0.5 on BTCUSD) imply noisier
    measurement data, while smaller tick sizes (e.g. 0.001 on SOLUSD)
    require tighter filtering.

    Returns (process_noise, measurement_noise).
    """
    process_noise = tick_size ** 2
    measurement_noise = tick_size * 100
    return process_noise, measurement_noise


def kfma(close, process_noise=None, measurement_noise=None, tick_size=None, **kwargs):
    """Kalman Filtered Moving Average.

    When *tick_size* is supplied the noise parameters are derived
    automatically via ``_noise_from_tick_size``.  Explicit *process_noise*
    and *measurement_noise* values always take priority.
    """
    # Resolve noise parameters
    if tick_size is not None and (process_noise is None or measurement_noise is None):
        auto_pn, auto_mn = _noise_from_tick_size(tick_size)
        if process_noise is None:
            process_noise = auto_pn
        if measurement_noise is None:
            measurement_noise = auto_mn
    # Fallback to original defaults when nothing is provided
    if process_noise is None:
        process_noise = 1e-4
    if measurement_noise is None:
        measurement_noise = 1e-2

    input = close.values
    filtered = kalman_filter(input, process_noise, measurement_noise)
    result = Series(filtered, index=close.index)
    # Name & Category
    result.name = f"KFMA"
    result.category = "overlap"
    return result



kfma.__doc__ = \
"""Kalman Filtered Moving Average.

Optimized Kalman filter using Numba for speed.  Supports adaptive noise
via tick_size parameter for per-symbol auto-tuning."""
