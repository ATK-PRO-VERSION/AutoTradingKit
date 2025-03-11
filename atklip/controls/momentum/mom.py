# -*- coding: utf-8 -*-
from concurrent.futures import Future
from numba import njit
from pandas import Series
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta._typing import Array, DictLike, Int
from atklip.controls.pandas_ta.maps import Imports
from atklip.controls.pandas_ta.utils import (
    nb_idiff,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



@njit(cache=True)
def nb_mom(x, n):
    return nb_idiff(x, n)


def mom(
    close: Series, length: Int = None, talib: bool = False,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Momentum (MOM)

    Momentum is an indicator used to measure a security's speed
    (or strength) of movement or simply the change in price.

    Sources:
        http://www.onlinetradingconcepts.com/TechnicalAnalysis/Momentum.html

    Args:
        close (pd.Series): Series of 'close's
        length (int): It's period. Default: 1
        talib (bool): If TA Lib is installed and talib is True, Returns
            the TA Lib version. Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.Series: New feature generated.
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length + 1)

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from atklip.controls.talib import MOM
        mom = MOM(close, length)
    else:
        np_close = close.values
        _mom = nb_mom(np_close, length)
        mom = Series(_mom, index=close.index)

    # Offset
    if offset != 0:
        mom = mom.shift(offset)

    # Fill
    if "fillna" in kwargs:
        mom.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    mom.name = f"MOM_{length}"
    mom.category = "momentum"

    return mom


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool

from PySide6.QtCore import Signal,QObject

class MOM(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()  
    sig_add_historic = Signal(int)   
    def __init__(self,_candles,dict_ta_params) -> None:   
        super().__init__(parent=None)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.source:str = dict_ta_params["source"]      
        self.length:int = dict_ta_params["length"]
        self.offset :int=dict_ta_params.get("drift",0)
        
        #self.signal_delete.connect(self.deleteLater)

        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"MOM {self.source} {self.length}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.data = np.array([]),np.array([])

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
            self.source:str = dict_ta_params["source"]      
            self.length:int = dict_ta_params["length"]
            self.offset :int=dict_ta_params.get("drift",0)

            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.length}"

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
            return [],[]
        if start == 0 and stop == 0:
            x_data = self.xdata
            y_data = self.data
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            y_data = self.data[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            y_data = self.data[start:]
        else:
            x_data = self.xdata[start:stop]
            y_data = self.data[start:stop]
        return x_data,y_data
    
    
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
        
        if isinstance(INDICATOR,pd.Series):
            y_data = INDICATOR
        else:
            column_names = INDICATOR.columns.tolist()
            roc_name = ''
            for name in column_names:
                if name.__contains__("MOM_"):
                    roc_name = name
            y_data = INDICATOR[roc_name]
        return y_data

    @staticmethod
    def calculate(df: pd.DataFrame,source,length,offset):
        df = df.copy()
        df = df.reset_index(drop=True)
        
        INDICATOR = mom(close=df[source],
                        length=length,
                        offset=offset).dropna().round(6)
        
        if isinstance(INDICATOR,pd.Series):
            y_data = INDICATOR
        else:
            column_names = INDICATOR.columns.tolist()
            roc_name = ''
            for name in column_names:
                if name.__contains__("MOM_"):
                    roc_name = name
            y_data = INDICATOR[roc_name]
 
        _len = len(y_data)
        
        _index = df["index"].tail(_len)
        return pd.DataFrame({
                            'index':_index,
                            "data":y_data,
                            })
        
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df,
                               self.source,self.length,self.offset)
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
                               self.source,self.length,self.offset)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*5)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.source,self.length,self.offset)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*5)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.source,self.length,self.offset)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.xdata,self.data = self.df["index"].to_numpy(),self.df["data"].to_numpy()
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
        self.data = np.concatenate((_df["data"].to_numpy(), self.data))   
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
        
    def callback_add(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_data = df["data"].iloc[-1]
        new_frame = pd.DataFrame({
                                    'index':[last_index],
                                    "data":[last_data]
                                    })
            
        self.df = pd.concat([self.df,new_frame],ignore_index=True)
                            
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.data = np.concatenate((self.data,np.array([last_data])))
        self.sig_add_candle.emit()
        #self.is_current_update = True
        
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_data = df["data"].iloc[-1]
        
        self.df.iloc[-1] = [last_index,last_data]
        self.xdata[-1],self.data[-1] = last_index,last_data
        self.sig_update_candle.emit()
        #self.is_current_update = True