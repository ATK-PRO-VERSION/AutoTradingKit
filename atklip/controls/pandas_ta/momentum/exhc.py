# -*- coding: utf-8 -*-
from math import isnan
from numpy import (
    clip,
    cumsum,
    diff,
    float64,
    int64,
    isnan,
    nan,
    nan_to_num,
    where,
    zeros_like
)
from numba import njit
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.utils import (
    nb_ffill,
    nb_idiff,
    nb_shift,
    v_bool,
    v_int,
    v_offset,
    v_pos_default,
    v_series
)
from atklip.controls.pandas_ta.utils._numba import nb_exhc



def exhc(
    close: Series, length: Int = None,
    cap: Int = None, asint: bool = None,
    show_all: bool = None, nozeros: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Exhaustion Count (EXHC)

    Inspired by Tom DeMark's Sequential indicator which attempts
    to identify where an uptrend or a downtrend exhausts and reverses.

    Sources:
        https://demark.com
        http://practicaltechnicalanalysis.blogspot.com/2013/01/tom-demark-sequential.html

    Args:
        close (pd.Series): Series of close's
        length (int): Difference for the sequences. Default: 4
        cap (int): Maximum sequence number to cap at. Set to zero for
            no max. Default: 13
        show_all (bool): Show 1 - 13. If set to False, show 6 - 9.
            Default: True
        asint (bool): If True, fillna's with 0 and change type to int.
            Default: False
        nozeros (bool): If True, replaces zeros with nan. Default: False
        offset (int): How many periods to offset the result. Default: 0

    Returns:
        pd.DataFrame: Down count, Up count
    """
    # Validate
    length = v_pos_default(length, 4)
    close = v_series(close, length + 1)

    if close is None:
        return

    cap = v_int(cap, 13, -1)
    show_all = v_bool(show_all, True)
    asint = v_bool(asint, False)
    nozeros = v_bool(nozeros, False)
    offset = v_offset(offset)

    # Calculate
    np_close = close.values
    dn, up = nb_exhc(np_close, length, cap, 6, 9, show_all)

    if asint:
        dn = dn.astype(int64)
        up = up.astype(int64)

    # Name and Category
    data = {
        "EXHC_DNa" if show_all else "EXHC_DN": dn,
        "EXHC_UPa" if show_all else "EXHC_UP": up
    }
    df = DataFrame(data, index=close.index)
    df.name = "EXHCa" if show_all else "EXHC"
    df.category = "momentum"

    if nozeros:
        df.replace({0: nan}, inplace=True)

     # Offset
    if offset != 0:
        df = df.shift(offset)

    return df
