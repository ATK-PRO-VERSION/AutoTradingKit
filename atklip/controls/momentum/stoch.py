# -*- coding: utf-8 -*-
from concurrent.futures import Future
from pandas import DataFrame, Series
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.utils import (
    non_zero_range,
    tal_ma,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def stoch(
    high: Series, low: Series, close: Series,
    k: Int = None, d: Int = None, smooth_k: Int = None,
    mamode: str = None, talib: bool = False,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Stochastic (STOCH)

    The Stochastic Oscillator (STOCH) was developed by George Lane in the
    1950's. He believed this indicator was a good way to measure momentum
    because changes in momentum precede changes in price.

    It is a range-bound oscillator with two lines moving between 0 and 100.
    The first line (%K) displays the current close in relation to the
    period's high/low range. The second line (%D) is a Simple Moving Average
    of the %K line. The most common choices are a 14 period %K and a 3 period
    SMA for %D.

    Sources:
        https://www.tradingview.com/wiki/Stochastic_(STOCH)
        https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=332&Name=KD_-_Slow

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        k (int): The Fast %K period. Default: 14
        d (int): The Slow %D period. Default: 3
        smooth_k (int): The Slow %K period. Default: 3
        mamode (str): See ``help(ta.ma)``. Default: 'sma'
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: %K, %D, Histogram columns.
    """
    # Validate
    k = v_pos_default(k, 14)
    d = v_pos_default(d, 3)
    smooth_k = v_pos_default(smooth_k, 3)
    _length = k + d + smooth_k
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    mode_tal = v_talib(talib)
    mamode = v_mamode(mamode, "sma")
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal and smooth_k > 2:
        from atklip.controls.talib import STOCH
        stoch_ = STOCH(
            high, low, close, k, d, tal_ma(mamode), d, tal_ma(mamode)
        )
        stoch_k, stoch_d = stoch_[0], stoch_[1]
    else:
        ll = low.rolling(k).min()
        hh = high.rolling(k).max()

        stoch = 100 * (close - ll) / non_zero_range(hh, ll)

        if stoch is None: return

        stoch_fvi = stoch.loc[stoch.first_valid_index():, ]
        if smooth_k == 1:
            stoch_k = stoch
        else:
            stoch_k = ma(mamode, stoch_fvi, length=smooth_k)

        stochk_fvi = stoch_k.loc[stoch_k.first_valid_index():, ]
        stoch_d = ma(mamode, stochk_fvi, length=d)

    stoch_h = stoch_k - stoch_d  # Histogram

    # Offset
    if offset != 0:
        stoch_k = stoch_k.shift(offset)
        stoch_d = stoch_d.shift(offset)
        stoch_h = stoch_h.shift(offset)

    # Fill
    if "fillna" in kwargs:
        stoch_k.fillna(kwargs["fillna"], inplace=True)
        stoch_d.fillna(kwargs["fillna"], inplace=True)
        stoch_h.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _name = "STOCH"
    _props = f"_{k}_{d}_{smooth_k}"
    stoch_k.name = f"{_name}k{_props}"
    stoch_d.name = f"{_name}d{_props}"
    stoch_h.name = f"{_name}h{_props}"
    stoch_k.category = stoch_d.category = stoch_h.category = "momentum"

    data = {
        stoch_k.name: stoch_k,
        stoch_d.name: stoch_d,
        stoch_h.name: stoch_h
    }
    df = DataFrame(data, index=close.index)
    df.name = f"{_name}{_props}"
    df.category = stoch_k.category

    return df

import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool

from PySide6.QtCore import Signal,QObject

class STOCH(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()   
    sig_add_historic = Signal(int) 
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
                 
        self.smooth_k_period:int = dict_ta_params["smooth_k_period"]
        self.k_period:int = dict_ta_params["k_period"]
        self.d_period:int = dict_ta_params["d_period"]
        self.mamode:str = dict_ta_params["mamode"]
        self.offset :int=dict_ta_params.get("offset",0)

        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"STOCH {self.smooth_k_period} {self.k_period} {self.d_period} {self.mamode}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.stoch_,self.signalma = np.array([]),np.array([]),np.array([])

        self.connect_signals()
    
    @property
    def is_current_update(self)-> bool:
        return self._is_current_update
    @is_current_update.setter
    def is_current_update(self,_is_current_update):
        self._is_current_update = _is_current_update
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
        
        if dict_ta_params != {}:
            self.smooth_k_period:int = dict_ta_params["smooth_k_period"]
            self.k_period:int = dict_ta_params["k_period"]
            self.d_period:int = dict_ta_params["d_period"]
            self.mamode:str = dict_ta_params["mamode"]
            self.offset :int=dict_ta_params.get("offset",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.mamode}-{self.smooth_k_period}-{self.k_period}-{self.d_period}"

            self._name = ta_param
            
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
        if len(self.xdata) == 0:
            return {"x_data":[],"stoch_":[],"signalma":[]}
        if start == 0 and stop == 0:
            x_data = self.xdata
            stoch_,signalma =self.stoch_,self.signalma
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            stoch_,signalma=self.stoch_[:stop],self.signalma[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            stoch_,signalma=self.stoch_[start:],self.signalma[start:]
        else:
            x_data = self.xdata[start:stop]
            stoch_,signalma=self.stoch_[start:stop],self.signalma[start:stop]
        return x_data,stoch_,signalma
    
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
        column_names = INDICATOR.columns.tolist()
        stoch_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("STOCHk"):
                stoch_name = name
            elif name.__contains__("STOCHd"):
                signalma_name = name

        stoch_ = INDICATOR[stoch_name].dropna().round(6)
        signalma = INDICATOR[signalma_name].dropna().round(6)
        return stoch_,signalma
    
    @staticmethod
    def calculate(df: pd.DataFrame,smooth_k_period,k_period,d_period,mamode,offset):
        df = df.copy()
        df = df.reset_index(drop=True)
        
        INDICATOR = stoch(high=df["high"],
                        low=df["low"],
                        close=df["close"],
                        smooth_k=smooth_k_period,
                        k = k_period,
                        d = d_period,
                        mamode=mamode,
                        offset=offset).dropna()
        
        column_names = INDICATOR.columns.tolist()
        stoch_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("STOCHk"):
                stoch_name = name
            elif name.__contains__("STOCHd"):
                signalma_name = name

        stoch_ = INDICATOR[stoch_name].dropna().round(6)
        signalma = INDICATOR[signalma_name].dropna().round(6)
        
        _len = min([len(stoch_),len(signalma)])
        _index = df["index"]
        
        return pd.DataFrame({
                            'index':_index.tail(_len),
                            "stoch":stoch_.tail(_len),
                            "signalma":signalma.tail(_len)
                            })
        
        
        

    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df,
                               self.smooth_k_period,self.k_period,
                               self.d_period,self.mamode,self.offset)
        process.start()
        
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        candle_df = self._candles.get_df()
        df:pd.DataFrame = candle_df.head(-_pre_len)
        
        process = HeavyProcess(self.calculate,
                               self.callback_gen_historic_data,
                               df,
                               self.smooth_k_period,self.k_period,
                               self.d_period,self.mamode,self.offset)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.k_period*5)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.smooth_k_period,self.k_period,
                               self.d_period,self.mamode,self.offset)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.k_period*5)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.smooth_k_period,self.k_period,
                               self.d_period,self.mamode,self.offset)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.xdata,self.stoch_,self.signalma = self.df["index"].to_numpy(),\
                                                self.df["stoch"].to_numpy(),\
                                                self.df["signalma"].to_numpy()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        #self.is_current_update = True
        self.sig_reset_all.emit()
        
    def callback_gen_historic_data(self, future: Future):
        _df = future.result()
        _len = len(_df)
        self.df = pd.concat([_df,self.df],ignore_index=True)
        self.xdata = np.concatenate((_df["index"].to_numpy(), self.xdata))
        self.stoch_ = np.concatenate((_df["stoch"].to_numpy(), self.stoch_))
        self.signalma = np.concatenate((_df["signalma"].to_numpy(), self.signalma))
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
        
    def callback_add(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_signalma = df["signalma"].iloc[-1]
        last_stoch = df["stoch"].iloc[-1]
        new_frame = pd.DataFrame({
                                    'index':[last_index],
                                    "stoch":[last_stoch],
                                    "signalma":[last_signalma]
                                    })
        self.df = pd.concat([self.df,new_frame],ignore_index=True)
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.stoch_ = np.concatenate((self.stoch_,np.array([last_stoch])))
        self.signalma = np.concatenate((self.signalma,np.array([last_signalma])))             
        self.sig_add_candle.emit()
        #self.is_current_update = True
        
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_signalma = df["signalma"].iloc[-1]
        last_stoch = df["stoch"].iloc[-1]
        self.df.iloc[-1] = [last_index,last_stoch,last_signalma]       
        self.xdata[-1],self.stoch_[-1],self.signalma[-1]  = last_index,last_stoch,last_signalma
        self.sig_update_candle.emit()
        #self.is_current_update = True
        