# -*- coding: utf-8 -*-
from concurrent.futures import Future
from pandas import Series
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.overlap.dema import dema
from atklip.controls.pandas_ta.overlap.ema import ema
from atklip.controls.pandas_ta.overlap.fwma import fwma
from atklip.controls.pandas_ta.overlap.hma import hma
from atklip.controls.pandas_ta.overlap.linreg import linreg
from atklip.controls.pandas_ta.overlap.midpoint import midpoint
from atklip.controls.pandas_ta.overlap.pwma import pwma
from atklip.controls.pandas_ta.overlap.rma import rma
from atklip.controls.pandas_ta.overlap.sinwma import sinwma
from atklip.controls.pandas_ta.overlap.sma import sma
from atklip.controls.pandas_ta.overlap.smma import smma
from atklip.controls.pandas_ta.overlap.ssf import ssf
from atklip.controls.pandas_ta.overlap.ssf3 import ssf3

from atklip.controls.pandas_ta.overlap.swma import swma
from atklip.controls.pandas_ta.overlap.t3 import t3
from atklip.controls.pandas_ta.overlap.tema import tema
from atklip.controls.pandas_ta.overlap.trima import trima
from atklip.controls.pandas_ta.overlap.vidya import vidya
from atklip.controls.pandas_ta.overlap.wma import wma
from atklip.controls.pandas_ta.overlap.zlma import zlma



def ma(name: str = None, source: Series = None,length: Int = None,mamode: str="ema") -> Series:
    """Simple MA Utility for easier MA selection

    Available MAs:
        dema, ema, fwma, hma, linreg, midpoint, pwma, rma, sinwma, sma, ssf,
        swma, t3, tema, trima, vidya, wma

    Examples:
        ema8 = ta.ma("ema", df.close, length=8)
        sma50 = ta.ma("sma", df.close, length=50)
        pwma10 = ta.ma("pwma", df.close, length=10, asc=False)

    Args:
        name (str): One of the Available MAs. Default: "ema"
        source (pd.Series): The 'source' Series.

    Kwargs:
        Any additional kwargs the MA may require.

    Returns:
        pd.Series: New feature generated.
    """
    _mas = [
        "dema", "ema", "fwma", "hma", "linreg", "midpoint", "pwma", "rma","smma"
        "sinwma", "sma", "ssf", "swma", "t3", "tema", "trima", "vidya", "wma","zlma"
    ]
    if name is None and source is None:
        return _mas
    elif isinstance(name, str) and name.lower() in _mas:
        name = name.lower()
    else:  # "ema"
        name = "ema"
    
    if   name == "dema": return dema(source, length)
    elif name == "fwma": return fwma(source, length)
    elif name == "hma": return hma(source, length)
    elif name == "linreg": return linreg(source, length)
    elif name == "midpoint": return midpoint(source, length)
    elif name == "pwma": return pwma(source, length)
    elif name == "rma": return rma(source, length)
    elif name == "sinwma": return sinwma(source, length)
    elif name == "sma": return sma(source, length)
    elif name == "smma": return smma(source, length,mamode)
    elif name == "ssf": return ssf(source, length)
    elif name == "ssf3": return ssf3(source, length)
    elif name == "swma": return swma(source, length)
    elif name == "t3": return t3(source, length)
    elif name == "tema": return tema(source, length)
    elif name == "trima": return trima(source, length)
    elif name == "vidya": return vidya(source, length)
    elif name == "wma": return wma(source, length)
    elif name == "zlma": return zlma(source, length,mamode)
    else: return ema(source, length)
