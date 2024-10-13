# -*- coding: utf-8 -*-
from pandas import Series
from atklip.controls.pandas_ta._typing import DictLike
from atklip.controls.overlap.dema import dema
from atklip.controls.overlap.ema import ema
from atklip.controls.overlap.fwma import fwma
from atklip.controls.overlap.hma import hma
from atklip.controls.overlap.linreg import linreg
from atklip.controls.overlap.midpoint import midpoint
from atklip.controls.overlap.pwma import pwma
from atklip.controls.overlap.rma import rma
from atklip.controls.overlap.sinwma import sinwma
from atklip.controls.overlap.sma import sma
from atklip.controls.overlap.smma import smma
from atklip.controls.overlap.ssf import ssf
from atklip.controls.overlap.swma import swma
from atklip.controls.overlap.t3 import t3
from atklip.controls.overlap.tema import tema
from atklip.controls.overlap.trima import trima
from atklip.controls.overlap.vidya import vidya
from atklip.controls.overlap.wma import wma



def ma(name: str = None, source: Series = None, **kwargs: DictLike) -> Series:
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
        "dema", "ema", "fwma", "hma", "linreg", "midpoint", "pwma", "rma",
        "sinwma", "sma", "ssf", "swma", "t3", "tema", "trima", "vidya", "wma"
    ]
    if name is None and source is None:
        return _mas
    elif isinstance(name, str) and name.lower() in _mas:
        name = name.lower()
    else:  # "ema"
        name = _mas[1]

    if   name == "dema": return dema(source, **kwargs)
    elif name == "fwma": return fwma(source, **kwargs)
    elif name == "hma": return hma(source, **kwargs)
    elif name == "linreg": return linreg(source, **kwargs)
    elif name == "midpoint": return midpoint(source, **kwargs)
    elif name == "pwma": return pwma(source, **kwargs)
    elif name == "rma": return rma(source, **kwargs)
    elif name == "sinwma": return sinwma(source, **kwargs)
    elif name == "sma": return sma(source, **kwargs)
    elif name == "smma": return smma(source, **kwargs)
    elif name == "ssf": return ssf(source, **kwargs)
    elif name == "swma": return swma(source, **kwargs)
    elif name == "t3": return t3(source, **kwargs)
    elif name == "tema": return tema(source, **kwargs)
    elif name == "trima": return trima(source, **kwargs)
    elif name == "vidya": return vidya(source, **kwargs)
    elif name == "wma": return wma(source, **kwargs)
    else: return ema(source, **kwargs)


import numpy as np
import pandas as pd
from typing import List

from psygnal import Signal
from .ma_type import PD_MAType
from .ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.app_api.workers import ApiThreadPool

class MA():
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()
    sig_add_historic = Signal()    
    def __init__(self,_candles,dict_ta_params) -> None:        
        
        self.ma_type:str = dict_ta_params.get("ma_type")
        self.source:str = dict_ta_params.get("source")
        self.length:int= dict_ta_params.get("length") 
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self.name = f"{self.ma_type} {self.source} {self.length}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata = []
        self.ydata = []

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
            self.ma_type:str = dict_ta_params.get("ma_type")
            self.source:str = dict_ta_params.get("source")
            self.length:int= dict_ta_params.get("length") 
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.ma_type}-{self.length}"

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
            return {"x_data":[],"y_data":[]}
        if start == 0 and stop == 0:
            x_data = self.xdata
            y_data = self.ydata
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            y_data = self.ydata[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            y_data = self.ydata[start:]
        else:
            x_data = self.xdata[start:stop]
            y_data = self.ydata[start:stop]
        return {"x_data":x_data,"y_data":y_data} 
    
    
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
        
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        
        data = ma(self.ma_type,source=df[self.source],length=self.length).dropna().round(4)
        
        _len = len(data)
        _index = df["index"].tail(_len)
            
        self.df = pd.DataFrame({
                            'index':_index,
                            "data":data
                            })
        
        self.xdata,self.ydata = _index.to_list(),data.to_list()
        
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
        
        data = ma(self.ma_type,source=df[self.source],length=self.length).dropna().round(4)
        
        
        _len = len(data)
        _index = df["index"].tail(_len)
            
        _df = pd.DataFrame({
                            'index':_index,
                            "data":data
                            })
        
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        
        self.xdata = _df["index"].to_list() + self.xdata
        self.ydata = _df["data"].to_list() + self.ydata
        
        # self.xdata,self.ydata = self.df["index"].to_list(),self.df["data"].to_list()
           
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False        
        self.is_histocric_load = True
        self.sig_add_historic.emit()
    
    def add(self,new_candles:List[OHLCV]):
        self.is_current_update = False
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*10)
                        
            data = ma(self.ma_type,source=df[self.source],length=self.length).round(4)
            
            _data = data.iloc[-1]
            
            new_frame = pd.DataFrame({
                                'index':[new_candle.index],
                                "data":[_data]
                                })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata,self.ydata = self.df["index"].to_list(),self.df["data"].to_list()
            
            self.sig_add_candle.emit()
            self.is_current_update = True
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*10)
                        
            data = ma(self.ma_type,source=df[self.source],length=self.length).round(4)
            
            self.df.iloc[-1] = [new_candle.index,data.iloc[-1]]
            
            self.xdata,self.ydata = self.df["index"].to_list(),self.df["data"].to_list()
            
            self.sig_update_candle.emit()
            self.is_current_update = True
            
            