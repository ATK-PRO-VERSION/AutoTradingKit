# -*- coding: utf-8 -*-
from pandas import concat, DataFrame, Series
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.utils import (
    signals,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def macd(
    close: Series, fast: Int = None, slow: Int = None,
    signal: Int = None,  mamode="ema", talib: bool = False,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Moving Average Convergence Divergence (MACD)

    The MACD is a popular indicator to that is used to identify a security's
    trend. While APO and MACD are the same calculation, MACD also returns
    two more series called Signal and Histogram. The Signal is an EMA of
    MACD and the Histogram is the difference of MACD and Signal.

    Sources:
        https://www.tradingview.com/wiki/MACD_(Moving_Average_Convergence/Divergence)
        AS Mode: https://tr.tradingview.com/script/YFlKXHnP/

    Args:
        close (pd.Series): Series of 'close's
        fast (int): The short period. Default: 12
        slow (int): The long period. Default: 26
        signal (int): The signal period. Default: 9
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        asmode (value, optional): When True, enables AS version of MACD.
            Default: False
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: macd, histogram, signal columns
    """
    # Validate
    fast = v_pos_default(fast, 12)
    slow = v_pos_default(slow, 26)
    signal = v_pos_default(signal, 9)
    if slow < fast:
        fast, slow = slow, fast
    _length = slow + signal - 1
    close = v_series(close, _length)

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)
    as_mode = kwargs.setdefault("asmode", False)

    # Calculate
    if Imports["talib"] and mode_tal:
        from atklip.controls.talib import MACD
        macd, signalma, histogram = MACD(close, fast, slow, signal)
    else:
        fastma = ma(mamode,close, length=fast)
        slowma = ma(mamode,close, length=slow)

        macd = fastma - slowma
        macd_fvi = macd.loc[macd.first_valid_index():, ]
        signalma = ma(mamode,macd_fvi, length=signal)
        histogram = macd - signalma

    if as_mode:
        macd = macd - signalma
        macd_fvi = macd.loc[macd.first_valid_index():, ]
        signalma = ma(mamode,macd_fvi, length=signal)
        histogram = macd - signalma

    # Offset
    if offset != 0:
        macd = macd.shift(offset)
        histogram = histogram.shift(offset)
        signalma = signalma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        macd.fillna(kwargs["fillna"], inplace=True)
        histogram.fillna(kwargs["fillna"], inplace=True)
        signalma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _asmode = "AS" if as_mode else ""
    _props = f"_{fast}_{slow}_{signal}"
    macd.name = f"MACD{_asmode}{_props}"
    histogram.name = f"HISTOGRAM{_asmode}h{_props}"
    signalma.name = f"SIGNAL{_asmode}s{_props}"
    macd.category = histogram.category = signalma.category = "momentum"

    data = {
        macd.name: macd,
        histogram.name: histogram,
        signalma.name: signalma
    }
    df = DataFrame(data, index=close.index)
    df.name = f"MACD{_asmode}{_props}"
    df.category = macd.category

    signal_indicators = kwargs.pop("signal_indicators", False)
    if signal_indicators:
        signalsdf = concat(
            [
                df,
                signals(
                    indicator=histogram,
                    xa=kwargs.pop("xa", 0),
                    xb=kwargs.pop("xb", None),
                    xserie=kwargs.pop("xserie", None),
                    xserie_a=kwargs.pop("xserie_a", None),
                    xserie_b=kwargs.pop("xserie_b", None),
                    cross_values=kwargs.pop("cross_values", True),
                    cross_series=kwargs.pop("cross_series", True),
                    offset=offset,
                ),
                signals(
                    indicator=macd,
                    xa=kwargs.pop("xa", 0),
                    xb=kwargs.pop("xb", None),
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
        return df

import numpy as np
import pandas as pd
from typing import List
from PySide6.QtCore import Qt, Signal,QObject

from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import CandleWorker

class MACD(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    def __init__(self,parent,_candles,source,fast_period,slow_period,signal_period,mamode) -> None:
        super().__init__(parent=parent)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.source:str = source      
        self.slow_period:int = slow_period
        self.fast_period:int = fast_period
        self.signal_period:int = signal_period
        self.mamode: PD_MAType = mamode

        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        
        self.name = f"MACD {self.source} {self.mamode.name.lower()} {self.slow_period} {self.fast_period} {self.signal_period}"

        self.df = pd.DataFrame([])
        
        self.xdata,self.macd_data,self.histogram,self.signalma = np.array([]),np.array([]),np.array([]),np.array([])

        self.connect_signals()
        
    def disconnect_signals(self):
        try:
            self._candles.sig_reset_all.disconnect(self.started_worker)
            self._candles.sig_update_candle.disconnect(self.update_worker)
            self._candles.sig_add_candle.disconnect(self.add_worker)
            self._candles.signal_delete.disconnect(self.signal_delete)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self._candles.sig_reset_all.connect(self.started_worker,Qt.ConnectionType.AutoConnection)
        self._candles.sig_update_candle.connect(self.update_worker,Qt.ConnectionType.AutoConnection)
        self._candles.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.AutoConnection)
        self._candles.signal_delete.connect(self.signal_delete)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
    
    def change_inputs(self,_input:str,_source:str|int|JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE|PD_MAType):
        is_update = False
        print(_input,_source)
        if _input == "source":
            self.change_source(_source)
            return
        elif _input == "fast_period":
            self.fast_period = _source
            is_update = True
        elif _input == "slow_period":
            self.slow_period = _source
            is_update = True
        elif _input == "signal_period":
            self.signal_period = _source
            is_update = True
        elif _input == "type":
            self.source = _source
            is_update = True
        elif _input == "mamode":
            self.mamode = _source
            is_update = True
        if is_update:
            self.started_worker()
    
    @property
    def name(self):
        return self.name
    @name.setter
    def name(self,_name):
        self.name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_data(self):
        return self.xdata,self.macd_data,self.signalma,self.histogram
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 

    def update_worker(self,candle):
        self.worker_ = None
        self.worker_ = CandleWorker(self.update,candle)
        self.worker_.start()
    
    def add_worker(self,candle):
        self.worker_ = None
        self.worker_ = CandleWorker(self.add,candle)
        self.worker_.start()
    
    def started_worker(self):
        self.worker = None
        self.worker = CandleWorker(self.fisrt_gen_data)
        self.worker.start()
    
    def paire_data(self,INDICATOR:DataFrame):
        column_names = INDICATOR.columns.tolist()
        
        macd_name = ''
        histogram_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("MACD"):
                macd_name = name
            elif name.__contains__("HISTOGRAM"):
                histogram_name = name
            elif name.__contains__("SIGNAL"):
                signalma_name = name

        macd = INDICATOR[macd_name]
        histogram = INDICATOR[histogram_name]
        signalma = INDICATOR[signalma_name]
        return macd,histogram,signalma
    def calculate(self,df: pd.DataFrame):
        INDICATOR = macd(close=df[self.source],
                        fast=self.fast_period,
                        slow=self.slow_period,
                        signal = self.signal_period,
                        mamode=self.mamode.name.lower())
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        
        _index = df["index"]
        macd_data,histogram,signalma = self.calculate(df)

        self.df = pd.DataFrame({
                            'index':_index,
                            "macd":macd_data,
                            "histogram":histogram,
                            "signalma":signalma
                            })
                
        self.xdata,self.macd_data,self.histogram,self.signalma = self.df["index"].to_numpy(),macd_data.to_numpy(),\
                                                histogram.to_numpy(),signalma.to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow_period*5)
                    
            macd_data,histogram,signalma = self.calculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "macd":[macd_data.iloc[-1]],
                                    "histogram":[histogram.iloc[-1]],
                                    "signalma":[signalma.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
                                
            self.xdata,self.macd_data,self.histogram,self.signalma = self.df["index"].to_numpy(),self.df["macd"].to_numpy(),\
                                                self.df["histogram"].to_numpy(),self.df["signalma"].to_numpy()
            
            self.sig_add_candle.emit()
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow_period*5)
                    
            macd_data,histogram,signalma = self.calculate(df)
                    
            self.df.iloc[-1] = [new_candle.index,macd_data.iloc[-1],histogram.iloc[-1],signalma.iloc[-1]]
                    
            self.xdata,self.macd_data,self.histogram,self.signalma = self.df["index"].to_numpy(),self.df["macd"].to_numpy(),\
                                                self.df["histogram"].to_numpy(),self.df["signalma"].to_numpy()
            
            self.sig_update_candle.emit()
            
