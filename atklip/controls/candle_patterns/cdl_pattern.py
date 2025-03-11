# -*- coding: utf-8 -*-
from pandas import Series, DataFrame
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat, List, Union
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.utils import v_offset, v_scalar, v_series
from atklip.controls.candle_patterns import cdl_doji, cdl_inside



ALL_PATTERNS = [
    "2crows", "3blackcrows", "3inside", "3linestrike", "3outside",
    "3starsinsouth", "3whitesoldiers", "abandonedbaby", "advanceblock",
    "belthold", "breakaway", "closingmarubozu", "concealbabyswall",
    "counterattack", "darkcloudcover", "doji", "dojistar", "dragonflydoji",
    "engulfing", "eveningdojistar", "eveningstar", "gapsidesidewhite",
    "gravestonedoji", "hammer", "hangingman", "harami", "haramicross",
    "highwave", "hikkake", "hikkakemod", "homingpigeon", "identical3crows",
    "inneck", "inside", "invertedhammer", "kicking", "kickingbylength",
    "ladderbottom", "longleggeddoji", "longline", "marubozu", "matchinglow",
    "mathold", "morningdojistar", "morningstar", "onneck", "piercing",
    "rickshawman", "risefall3methods", "separatinglines", "shootingstar",
    "shortline", "spinningtop", "stalledpattern", "sticksandwich", "takuri",
    "tasukigap", "thrusting", "tristar", "unique3river", "upsidegap2crows",
    "xsidegap3methods"
]

list_cdl_patterns = ["dojistar",                   
                "eveningdojistar",
                "engulfing",
                "eveningstar",
                "morningdojistar",
                "morningstar",
                "shootingstar",
                "harami",
                "haramicross",
                "kicking",
                "kickingbylength",
                "marubozu"]

def cdl_pattern(
    open_: Series, high: Series, low: Series, close: Series,
    name: Union[str, List[str]] = "all", scalar: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """TA Lib Candle Patterns

    A wrapper around all TA Lib's candle patterns.

    Examples:

        Get all candle patterns (This is the default behaviour)::

            df = df.ta.cdl_pattern(name="all")

        Get only one pattern::

            df = df.ta.cdl_pattern(name="doji")

        Get some patterns::

            df = df.ta.cdl_pattern(name=["doji", "inside"])

    Args:
        open_ (pd.Series): Series of 'open's
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        name: (Union[str, Sequence[str]]): name of the patterns
        scalar (float): How much to magnify. Default: 100
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
    Returns:
        pd.DataFrame: one column for each pattern.
    """
    # Validate Arguments
    open_ = v_series(open_, 1)
    high = v_series(high, 1)
    low = v_series(low, 1)
    close = v_series(close, 1)
    offset = v_offset(offset)
    scalar = v_scalar(scalar, 100)

    if open_ is None or high is None or low is None or close is None:
        return

    # Patterns implemented in Pandas TA
    pta_patterns = {"doji": cdl_doji, "inside": cdl_inside}

    if name == "all":
        name = ALL_PATTERNS
    if isinstance(name, str):
        name = [name]

    if Imports["talib"]:
        import talib.abstract as tala

    result = {}
    for n in name:
        if n not in ALL_PATTERNS:
            print(f"[X] There is no candle pattern named {n} available!")
            continue

        if n in pta_patterns:
            pattern_result = pta_patterns[n](
                open_, high, low, close, offset=offset, scalar=scalar, **kwargs
            )
            if not isinstance(pattern_result, Series):
                continue
            result[pattern_result.name] = pattern_result

        else:
            if not Imports["talib"]:
                print(f"[X] Install TA-Lib to use {n}. (pip install TA-Lib)")
                continue

            pf = tala.Function(f"CDL{n.upper()}")
            pattern_result = Series(
                0.01 * scalar * pf(open_, high, low, close, **kwargs)
            )
            pattern_result.index = close.index

            # Offset
            if offset != 0:
                pattern_result = pattern_result.shift(offset)

            # Fill
            if "fillna" in kwargs:
                pattern_result.fillna(kwargs["fillna"], inplace=True)
            result[f"CDL_{n.upper()}"] = pattern_result

    if len(result) == 0:
        return

    # Name and Category
    df = DataFrame(result)
    df.name = "CDL_PATTERN"
    df.category = "candles"
    return df

cdl = cdl_pattern  # Alias




import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject

class AllCandlePattern(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int) 
    def __init__(self,_candles,dict_ta_params:dict={}) -> None:
        super().__init__(parent=None)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"ALL CDL PATTERN"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool

        self.connect_signals()
    
    @property
    def source_name(self)-> str:
        return self._source_name
    @source_name.setter
    def source_name(self,source_name):
        self._source_name = source_name
    
    def change_input(self,candles=None,dict_ta_params: dict={}):
        if candles != None:
            self.disconnect_signals()
            self._candles : JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE= candles
            self.connect_signals()
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        
        self.fisrt_gen_data()
    
    def disconnect_signals(self):
        try:
            self._candles.sig_reset_all.disconnect(self.started_worker)
            self._candles.sig_update_candle.disconnect(self.update_worker)
            self._candles.sig_add_candle.disconnect(self.add_worker)
            self._candles.signal_delete.disconnect(self.signal_delete)
            self._candles.sig_add_historic.disconnect(self.add_historic_worker)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self._candles.sig_reset_all.connect(self.started_worker)
        self._candles.sig_update_candle.connect(self.update_worker)
        self._candles.sig_add_candle.connect(self.add_worker)
        self._candles.signal_delete.connect(self.signal_delete)
        self._candles.sig_add_historic.connect(self.add_historic_worker)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self,_name):
        self._name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    
    def get_data(self,start:int=0,stop:int=0):
        if len(self.df) == 0:
            return []
        if start == 0 and stop == 0:
            df=self.df
        elif start == 0 and stop != 0:
            df=self.df.iloc[:stop]
        elif start != 0 and stop == 0:
            df=self.df.iloc[start:]
        else:
            df=self.df.iloc[start:stop]
        return df
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 

    def update_worker(self,candle):
        self.worker.submit(self.update,candle)

    def add_worker(self,candle):
        self.worker.submit(self.add,candle)
    
    def add_historic_worker(self,n):
        self.worker.submit(self.add_historic,n)

    def started_worker(self):
        self.worker.submit(self.fisrt_gen_data)
    
    def paire_data(self,INDICATOR:pd.DataFrame|pd.Series):
        return
    
    def calculate(self,df: pd.DataFrame):
        INDICATOR = cdl_pattern(open_=df["open"],
                                high=df["high"],
                                low=df["low"],
                                close=df["close"],
                                name=list_cdl_patterns)
        return INDICATOR
    
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        
        self.df = self.calculate(df)
        
        
        print(self.df)
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        
        #self.is_current_update = True
        self.sig_reset_all.emit()
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        _df= self.calculate(df)
        _len = len(_df)
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(10)
            _df:pd.DataFrame  = self.calculate(df)
            
            _new_df = _df.iloc[[-1]]
            
            # print(type(_new_df),_new_df)
            
            self.df = pd.concat([self.df,_new_df],ignore_index=True)
            self.sig_add_candle.emit()
        #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(10)
            _df = self.calculate(df)
            self.df.iloc[-1] = _df.iloc[-1]
            self.sig_update_candle.emit()
        #self.is_current_update = True
           