# -*- coding: utf-8 -*-
from numpy import isnan, nan
from pandas import Series
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.utils import (
    v_bool,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)
from atklip.controls.pandas_ta.utils._numba import nb_ht_trendline


def ht_trendline(
    close: Series = None, talib: bool = None,
    prenan: Int = None, offset: Int = None,
    **kwargs: DictLike
) -> Series:
    """Hilbert Transform TrendLine (HT_TL)

    The Hilbert Transform TrendLine or Instantaneous TrendLine as described
    in Ehler's "Rocket Science for Traders" Book attempts to smooth the
    source by using a bespoke application of the Hilbert Transform.

    Sources:
        https://c.mql5.com/forextsd/forum/59/023inst.pdf
        https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_HT_TRENDLINE.c

    Args:
        close (pd.Series): Series of 'close's.
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        prenan (int): Prenans to apply. Ehler's 6 or 12, TALib 63
            Default: 63
        offset (int, optional): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: Hilbert Transformation Instantaneous Trend-line.
    """
    # Validate
    prenan = v_pos_default(prenan, 63)
    close = v_series(close, prenan)

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    np_close = close.to_numpy()
    np_tl = nb_ht_trendline(np_close)

    if prenan > 0:
        np_tl[:prenan] = nan
    tl = Series(np_tl, index=close.index)

    if all(isnan(tl)):
        return  # Emergency Break

    # Offset
    if offset != 0:
        trend_line = tl.shift(offset)

    # Fill
    if "fillna" in kwargs:
        tl.fillna(kwargs["fillna"], inplace=True)

    tl.name = f"HT_TL"
    tl.category = "trend"

    return tl
