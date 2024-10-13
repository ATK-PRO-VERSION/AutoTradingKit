# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.overlap.ema import ema
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.pandas_ta.utils import (
    v_drift,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series
)



def trix(
    close: Series, length: Int = None, signal: Int = None,mamode: str = "ema",
    scalar: IntFloat = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Trix (TRIX)

    TRIX is a momentum oscillator to identify divergences.

    Sources:
        https://www.tradingview.com/wiki/TRIX

    Args:
        close (pd.Series): Series of 'close's
        length (int): It's period. Default: 18
        signal (int): It's period. Default: 9
        scalar (float): How much to magnify. Default: 100
        drift (int): The difference period. Default: 1
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.Series: New feature generated.
    """
    # Validate
    length = v_pos_default(length, 30)
    signal = v_pos_default(signal, 9)
    if length < signal:
        length, signal = signal, length
    _length = 3 * length - 1
    close = v_series(close, _length)

    if close is None:
        return

    scalar = v_scalar(scalar, 100)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    
    # ema1 = ema(close=close, length=length, **kwargs)
    ema1 = ma(mamode, source=close, length=length, **kwargs)
    if all(isnan(ema1)):
        return  # Emergency Break

    # ema2 = ema(close=ema1, length=length, **kwargs)
    ema2 = ma(mamode, source=ema1, length=length, **kwargs)
    if all(isnan(ema2)):
        return  # Emergency Break

    # ema3 = ema(close=ema2, length=length, **kwargs)
    ema3 = ma(mamode, source=ema2, length=length, **kwargs)
    if all(isnan(ema3)):
        return  # Emergency Break

    trix = scalar * ema3.pct_change(drift)
    trix_signal = trix.rolling(signal).mean()

    # Offset
    if offset != 0:
        trix = trix.shift(offset)
        trix_signal = trix_signal.shift(offset)

    # Fill
    if "fillna" in kwargs:
        trix.fillna(kwargs["fillna"], inplace=True)
        trix_signal.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    trix.name = f"TRIX_{length}_{signal}"
    trix_signal.name = f"TRIXs_{length}_{signal}"
    trix.category = trix_signal.category = "momentum"

    data = {trix.name: trix, trix_signal.name: trix_signal}
    df = DataFrame(data, index=close.index)
    df.name = f"TRIX_{length}_{signal}"
    df.category = "momentum"

    return df


import numpy as np
import pandas as pd
from typing import List
from psygnal import Signal
from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.app_api.workers import ApiThreadPool

class TRIX():
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()  
    sig_add_historic = Signal()    
    def __init__(self,_candles,dict_ta_params) -> None:
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.length_period :int = dict_ta_params["length_period"]
        self.signal_period:int = dict_ta_params["signal_period"]
        self.source:str = dict_ta_params["source"]
        self.ma_type:str = dict_ta_params["ma_type"]
        self.drift  :int=dict_ta_params.get("drift",1)
        self.offset :int=dict_ta_params.get("offset",0)

        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self.name = f"TRIX {self.source} {self.length_period} {self.signal_period} {self.ma_type.lower()}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.trix_ , self.signalma = [],[],[]

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
        
        if dict_ta_params != {}:
            self.length_period :int = dict_ta_params["length_period"]
            self.signal_period:int = dict_ta_params["signal_period"]
            self.source:str = dict_ta_params["source"]
            self.ma_type:str = dict_ta_params["ma_type"]
            self.drift  :int=dict_ta_params.get("drift",1)
            self.offset :int=dict_ta_params.get("offset",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.ma_type}-{self.signal_period}-{self.length_period}"

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
        self._candles.signal_delete.connect(self.signal_delete)
        self._candles.sig_add_historic.connect(self.add_historic_worker)
    
    
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
            return {"x_data":[],"trix_":[],"signalma":[]}
        if start == 0 and stop == 0:
            x_data = self.xdata
            trix_,signalma =self.trix_,self.signalma
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            trix_,signalma=self.trix_[:stop],self.signalma[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            trix_,signalma=self.trix_[start:],self.signalma[start:]
        else:
            x_data = self.xdata[start:stop]
            trix_,signalma=self.trix_[start:stop],self.signalma[start:stop]
        return {"x_data":x_data,"trix_":trix_,"signalma":signalma}
    
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
    
    def paire_data(self,INDICATOR:pd.DataFrame|pd.Series):
        column_names = INDICATOR.columns.tolist()
        
        trix_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("TRIX_"):
                trix_name = name
            elif name.__contains__("TRIXs_"):
                signalma_name = name

        trix_ = INDICATOR[trix_name].dropna().round(4)
        signalma = INDICATOR[signalma_name].dropna().round(4)
        
        return trix_,signalma
    
    def caculate(self,df: pd.DataFrame):
        INDICATOR = trix(close=df[self.source],
                            length=self.length_period,
                            signal = self.signal_period,
                            mamode=self.ma_type.lower(),
                            drift=self.drift,
                            offset=self.offset
                            ).dropna().round(4)
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        
        trix_, signalma = self.caculate(df)
        
        _len = min([len(trix_),len(signalma)])
        _index = df["index"].tail(_len)

        self.df = pd.DataFrame({
                            'index':_index,
                            "trix":trix_.tail(_len),
                            "signalma":signalma.tail(_len)
                            })
                
        self.xdata,self.trix_ , self.signalma = self.df["index"].to_list(),\
                                                self.df["trix"].to_list(),\
                                                self.df["signalma"].to_list()
        
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
        
        trix_, signalma = self.caculate(df)
        
        _len = min([len(trix_),len(signalma)])
        _index = df["index"].tail(_len)

        _df = pd.DataFrame({
                            'index':_index,
                            "trix":trix_.tail(_len),
                            "signalma":signalma.tail(_len)
                            })
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        
        self.xdata = _df["index"].to_list() + self.xdata
        self.trix_ = _df["trix"].to_list() + self.trix_
        self.signalma = _df["signalma"].to_list() + self.signalma
        
        # self.xdata,self.trix_ , self.signalma = self.df["index"].to_list(),\
        #                                         self.df["trix"].to_list(),\
        #                                         self.df["signalma"].to_list()
        
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
            df:pd.DataFrame = self._candles.get_df(self.length_period*5)
                    
            trix_, signalma = self.caculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "trix":[trix_.iloc[-1]],
                                    "signalma":[signalma.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata,self.trix_ , self.signalma  = self.df["index"].to_list(),\
                                                    self.df["trix"].to_list(),\
                                                    self.df["signalma"].to_list()
                                            
            self.sig_add_candle.emit()
            self.is_current_update = True
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length_period*5)
                    
            trix_, signalma = self.caculate(df)
                    
            self.df.iloc[-1] = [new_candle.index,trix_.iloc[-1],signalma.iloc[-1]]
                    
            self.xdata,self.trix_ , self.signalma  = self.df["index"].to_list(),\
                                                    self.df["trix"].to_list(),\
                                                    self.df["signalma"].to_list()
            self.sig_update_candle.emit()
            self.is_current_update = True

