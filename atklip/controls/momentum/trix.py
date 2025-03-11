# -*- coding: utf-8 -*-
from concurrent.futures import Future
from numpy import isnan
from pandas import DataFrame, Series
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
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
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool

from PySide6.QtCore import Signal,QObject

class TRIX(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()  
    sig_add_historic = Signal(int)    
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.length_period :int = dict_ta_params["length_period"]
        self.signal_period:int = dict_ta_params["signal_period"]
        self.source:str = dict_ta_params["source"]
        self.mamode:str = dict_ta_params["mamode"]
        self.drift  :int=dict_ta_params.get("drift",1)
        self.offset :int=dict_ta_params.get("offset",0)

        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"TRIX {self.source} {self.length_period} {self.signal_period} {self.mamode.lower()}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.trix_ , self.signalma = np.array([]),np.array([]),np.array([])

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
            self.length_period :int = dict_ta_params["length_period"]
            self.signal_period:int = dict_ta_params["signal_period"]
            self.source:str = dict_ta_params["source"]
            self.mamode:str = dict_ta_params["mamode"]
            self.drift  :int=dict_ta_params.get("drift",1)
            self.offset :int=dict_ta_params.get("offset",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.mamode}-{self.signal_period}-{self.length_period}"

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
            return [],[],[]
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
        return x_data,trix_,signalma
    
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
        
        trix_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("TRIX_"):
                trix_name = name
            elif name.__contains__("TRIXs_"):
                signalma_name = name

        trix_ = INDICATOR[trix_name].dropna().round(6)
        signalma = INDICATOR[signalma_name].dropna().round(6)
        
        return trix_,signalma
    
    @staticmethod
    def calculate(df: pd.DataFrame,source,length_period,signal_period,mamode,drift,offset):
        df = df.copy()
        df = df.reset_index(drop=True)
        
        INDICATOR = trix(close=df[source],
                            length=length_period,
                            signal = signal_period,
                            mamode=mamode.lower(),
                            drift=drift,
                            offset=offset
                            ).dropna()
        column_names = INDICATOR.columns.tolist()
        trix_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("TRIX_"):
                trix_name = name
            elif name.__contains__("TRIXs_"):
                signalma_name = name
        trix_ = INDICATOR[trix_name].dropna().round(6)
        signalma = INDICATOR[signalma_name].dropna().round(6)
        _len = min([len(trix_),len(signalma)])
        _index = df["index"].tail(_len)

        return pd.DataFrame({
                            'index':_index,
                            "trix":trix_.tail(_len),
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
                               self.source,self.length_period,self.signal_period,self.mamode,self.drift,self.offset)
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
                               self.source,self.length_period,self.signal_period,self.mamode,self.drift,self.offset)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length_period*5)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.source,self.length_period,self.signal_period,self.mamode,self.drift,self.offset)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length_period*5)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.source,self.length_period,self.signal_period,self.mamode,self.drift,self.offset)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.xdata,self.trix_ , self.signalma = self.df["index"].to_numpy(),\
                                                self.df["trix"].to_numpy(),\
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
        self.trix_ = np.concatenate((_df["trix"].to_numpy(), self.trix_))   
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
        last_trix = df["trix"].iloc[-1]
        last_signalma = df["signalma"].iloc[-1]
        new_frame = pd.DataFrame({
                                    'index':[last_index],
                                    "trix":[last_trix],
                                    "signalma":[last_signalma]
                                    })
            
        self.df = pd.concat([self.df,new_frame],ignore_index=True)       
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.trix_ = np.concatenate((self.trix_,np.array([last_trix])))
        self.signalma = np.concatenate((self.signalma,np.array([last_signalma]))) 
        self.sig_add_candle.emit()
        #self.is_current_update = True
        
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_trix = df["trix"].iloc[-1]
        last_signalma = df["signalma"].iloc[-1]
        self.df.iloc[-1] = [last_index,last_trix,last_signalma]
        self.xdata[-1],self.trix_[-1], self.signalma[-1]  = last_index,last_trix,last_signalma
        self.sig_update_candle.emit()
        #self.is_current_update = True
