# -*- coding: utf-8 -*-
from pandas import concat, DataFrame, Series
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.overlap import ema
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
from psygnal import Signal
from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.app_api.workers import ApiThreadPool

class MACD():
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal()
    def __init__(self,_candles,dict_ta_params) -> None:

        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
                
        self.source:str = dict_ta_params.get("source")       
        self.slow_period:int = dict_ta_params.get("slow_period") 
        self.fast_period:int = dict_ta_params.get("fast_period") 
        self.signal_period:int = dict_ta_params.get("signal_period") 
        self.ma_type: str = dict_ta_params.get("ma_type") 
        self.offset :int=dict_ta_params.get("drift",0)

        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self.name = f"MACD {self.source} {self.ma_type} {self.slow_period} {self.fast_period} {self.signal_period}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.macd_data,self.histogram,self.signalma = [],[],[],[]

        self.connect_signals()
    
    @property
    def source_name(self)-> str:
        return self._source_name
    @source_name.setter
    def source_name(self,source_name):
        self._source_name = source_name
    
    def change_input(self,candles=None,dict_ta_params:dict={}):
        if candles != None:
            self.disconnect_signals()
            self._candles : JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE= candles
            self.connect_signals()
        
        if dict_ta_params != {}:
            self.source:str = dict_ta_params.get("source")       
            self.slow_period:int = dict_ta_params.get("slow_period") 
            self.fast_period:int = dict_ta_params.get("fast_period") 
            self.signal_period:int = dict_ta_params.get("signal_period") 
            self.ma_type: str = dict_ta_params.get("ma_type") 
            self.offset :int=dict_ta_params.get("drift",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.ma_type}-{self.slow_period}-{self.fast_period}-{self.signal_period}"

            self.indicator_name = ta_param
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        
        self.started_worker()
    
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
        self._candles.sig_add_historic.connect(self.add_historic_worker)
        self._candles.signal_delete.connect(self.signal_delete)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
    
    
    @property
    def indicator_name(self):
        return self.name
    @indicator_name.setter
    def indicator_name(self,_name):
        self.name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_data(self,start:int=0,stop:int=0):
        if self.xdata == []:
            return {"x_data":[],"macd_data":[],"signalma":[],"histogram":[]}
        if start == 0 and stop == 0:
            x_data = self.xdata
            macd_data,signalma,histogram=self.macd_data,self.signalma,self.histogram
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            macd_data,signalma,histogram=self.macd_data[:stop],self.signalma[:stop],self.histogram[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            macd_data,signalma,histogram=self.macd_data[start:],self.signalma[start:],self.histogram[start:]
        else:
            x_data = self.xdata[start:stop]
            macd_data,signalma,histogram=self.macd_data[start:stop],self.signalma[start:stop],self.histogram[start:stop]
        return {"x_data":x_data,"macd_data":macd_data,"signalma":signalma,"histogram":histogram}
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 

    
    def update_worker(self,candle):
        self.worker.submit(self.update(candle))

    def add_worker(self,candle):
        self.worker.submit(self.add(candle))

    
    def add_historic_worker(self,n):
        self.worker.submit(self.add_historic(n))

    def started_worker(self):
        self.worker.submit(self.fisrt_gen_data())
    
    
    def paire_data(self,INDICATOR:DataFrame):
        try:
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

            macd = INDICATOR[macd_name].dropna().round(4)
            histogram = INDICATOR[histogram_name].dropna().round(4)
            signalma = INDICATOR[signalma_name].dropna().round(4)
            return macd,histogram,signalma
        except:
            return Series([]),Series([]),Series([])
    def caculate(self,df: pd.DataFrame):
        INDICATOR = macd(close=df[self.source],
                        fast=self.fast_period,
                        slow=self.slow_period,
                        signal = self.signal_period,
                        mamode=self.ma_type,
                        offset=self.offset)
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        
        macd_data,histogram,signalma = self.caculate(df)
        _len = min([len(histogram),len(macd_data),len(signalma)])
        _index = df["index"]
        self.df = pd.DataFrame({
                            'index':_index.tail(_len),
                            "macd":macd_data.tail(_len),
                            "histogram":histogram.tail(_len),
                            "signalma":signalma.tail(_len)
                            })
        
        self.xdata,self.macd_data,self.histogram,self.signalma = self.df["index"].to_list(),macd_data.to_list(),\
                                                histogram.to_list(),signalma.to_list()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        macd_data,histogram,signalma = self.caculate(df)

        _len = min([len(histogram),len(macd_data),len(signalma)])
        
        _index = df["index"]
        _df = pd.DataFrame({
                            'index':_index.tail(_len),
                            "macd":macd_data.tail(_len),
                            "histogram":histogram.tail(_len),
                            "signalma":signalma.tail(_len)
                            })
                
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        self.xdata = _df["index"].to_list() + self.xdata
        self.macd_data = _df["macd"].to_list() + self.macd_data
        self.histogram = _df["histogram"].to_list() + self.histogram
        self.signalma = _df["signalma"].to_list() + self.signalma
        
        # self.xdata,self.macd_data,self.histogram,self.signalma = self.df["index"].to_list(),self.df["macd"].to_list(),\
        #                                         self.df["histogram"].to_list(),self.df["signalma"].to_list()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit()
    
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow_period*5)
                    
            macd_data,histogram,signalma = self.caculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "macd":[macd_data.iloc[-1]],
                                    "histogram":[histogram.iloc[-1]],
                                    "signalma":[signalma.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
                                
            self.xdata,self.macd_data,self.histogram,self.signalma = self.df["index"].to_list(),self.df["macd"].to_list(),\
                                                self.df["histogram"].to_list(),self.df["signalma"].to_list()
            
            self.sig_add_candle.emit()
            self.is_current_update = True
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow_period*5)
                    
            macd_data,histogram,signalma = self.caculate(df)
                    
            self.df.iloc[-1] = [new_candle.index,macd_data.iloc[-1],histogram.iloc[-1],signalma.iloc[-1]]
                    
            self.xdata,self.macd_data,self.histogram,self.signalma = self.df["index"].to_list(),self.df["macd"].to_list(),\
                                                self.df["histogram"].to_list(),self.df["signalma"].to_list()
            
            self.sig_update_candle.emit()
            self.is_current_update = True
            
