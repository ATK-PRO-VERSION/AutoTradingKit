# -*- coding: utf-8 -*-
from pandas import Series
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib
from .ema import ema



def t3(
    close: Series, length: Int = None, a: IntFloat = None, talib: bool = False,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Tim Tillson's T3 Moving Average (T3)

    Tim Tillson's T3 Moving Average is considered a smoother and more
    responsive moving average relative to other moving averages.

    Sources:
        http://www.binarytribune.com/forex-trading-indicators/t3-moving-average-indicator/

    Args:
        close (pd.Series): Series of 'close's
        length (int): It's period. Default: 10
        a (float): 0 < a < 1. Default: 0.7
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        adjust (bool): Default: True
        presma (bool, optional): If True, uses SMA for initial value.
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.Series: New feature generated.
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, 5 * (length + 1))

    if close is None:
        return

    a = float(a) if isinstance(a, float) and 0 < a < 1 else 0.7
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    c1 = -a * a**2
    c2 = 3 * a**2 + 3 * a**3
    c3 = -6 * a**2 - 3 * a - 3 * a**3
    c4 = a**3 + 3 * a**2 + 3 * a + 1

    e1 = ema(close=close, length=length, talib=mode_tal, **kwargs)
    e2 = ema(close=e1, length=length, talib=mode_tal, **kwargs)
    e3 = ema(close=e2, length=length, talib=mode_tal, **kwargs)
    e4 = ema(close=e3, length=length, talib=mode_tal, **kwargs)
    e5 = ema(close=e4, length=length, talib=mode_tal, **kwargs)
    e6 = ema(close=e5, length=length, talib=mode_tal, **kwargs)
    t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

    # Offset
    if offset != 0:
        t3 = t3.shift(offset)

    # Fill
    if "fillna" in kwargs:
        t3.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    t3.name = f"T3_{length}_{a}"
    t3.category = "overlap"

    return t3
