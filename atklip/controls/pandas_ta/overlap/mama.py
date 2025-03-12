# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib
from atklip.controls.pandas_ta.utils._numba import nb_mama

def mama(
    close: Series, fastlimit: IntFloat = None, slowlimit: IntFloat = None,
    prenan: Int = None, talib: bool = False,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Ehler's MESA Adaptive Moving Average (MAMA)

    Ehler's MESA Adaptive Moving Average (MAMA) aka the Mother of All Moving
    Averages attempts to adapt to the source's dynamic nature. The adapation
    is based on the rate change of phase as measured by the Hilbert
    Transform Discriminator. The advantage of this method of adaptation is
    that it features a fast attack average and a slow decay average so that
    the composite average rapidly adjusts to price changes and holds
    the average value until the next change occurs. This indicator also
    includes FAMA.

    Sources:
        Ehler's Mother of Adaptive Moving Averages:
            http://traders.com/documentation/feedbk_docs/2014/01/traderstips.html
        https://www.tradingview.com/script/foQxLbU3-Ehlers-MESA-Adaptive-Moving-Average-LazyBear/

    Args:
        close (pd.Series): Series of 'close's
        fastlimit (float): Fast limit. Default: 0.5
        slowlimit (float): Slow limit. Default: 0.05
        prenan (int): Prenans to apply. TV-LB 3, Ehler's 6, TALib 32
            Default: 3
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: MAMA and FAMA columns.
    """
    # Validate
    close = v_series(close, 1)

    if close is None:
        return

    fastlimit = v_pos_default(fastlimit, 0.5)
    slowlimit = v_pos_default(slowlimit, 0.05)
    prenan = v_pos_default(prenan, 3)
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    np_close = close.to_numpy()

    mama, fama = nb_mama(np_close, fastlimit, slowlimit, prenan)

    if all(isnan(mama)) or all(isnan(fama)):
        return  # Emergency Break

    # Name and Category
    _props = f"_{fastlimit}_{slowlimit}"
    data = {f"MAMA{_props}": mama, f"FAMA{_props}": fama}
    df = DataFrame(data, index=close.index)

    df.name = f"MAMA{_props}"
    df.category = "overlap"

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Fill
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    return df
