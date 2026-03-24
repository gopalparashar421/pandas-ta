from pandas import Series, DataFrame, concat
from pandas_ta.ma import ma
from pandas_ta.utils import get_offset, verify_series, signals

def tdfi(close, length=13, mma_type="wma", smma_type="wma", mma_length=13, smma_length=13, n_length=3, offset=0, **kwargs):
    close = verify_series(close, length)
    offset = get_offset(offset)
    
    if close is None: return
    close = close * 1000

    # Calculate MMAs
    mma = ma(kind=mma_type, source=close, length=mma_length)
    smma = ma(kind=smma_type, source=mma, length=smma_length)

    # Calculate Momentum
    impet_mma = mma.diff()
    impet_smma = smma.diff()
    divma = (mma - smma).abs()
    averimpet = (impet_mma + impet_smma) / 2
    
    # Calculate Force Index
    tdf = divma * (averimpet ** n_length)
    tdf_norm = tdf / tdf.abs().rolling(length*n_length).max()
    tdf_norm = Series(tdf_norm, index=close.index)

    if "fillna" in kwargs:
        tdf_norm.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        tdf_norm.fillna(method=kwargs["fill_method"], inplace=True)

    # Naming
    tdf_norm.name = f"TDFI_{length}"
    tdf_norm.category = "momentum"

    signal_indicators = kwargs.pop("signal_indicators", False)
    if signal_indicators:
        signalsdf = concat(
            [
                DataFrame({tdf_norm.name: tdf_norm}),
                signals(
                    indicator=tdf_norm,
                    xa=kwargs.pop("xa", 0.05),
                    xb=kwargs.pop("xb", -0.05),
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
        return tdf_norm
