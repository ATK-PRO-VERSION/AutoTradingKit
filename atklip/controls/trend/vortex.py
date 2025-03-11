# -*- coding: utf-8 -*-
from concurrent.futures import Future
from pandas import DataFrame, Series
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.utils import v_drift, v_offset, v_pos_default, v_series
from atklip.controls.volatility import true_range



def vortex(
    high: Series, low: Series, close: Series,
    length: Int = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Vortex

    Two oscillators that capture positive and negative trend movement.

    Sources:
        https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:vortex_indicator

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        length (int): ROC 1 period. Default: 14
        drift (int): The difference period. Default: 1
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: vip and vim columns
    """
    # Validate
    length = v_pos_default(length, 14)
    if "min_periods" in kwargs and kwargs["min_periods"] is not None:
        min_periods = int(kwargs["min_periods"])
    else:
        min_periods = length
    _length = max(length, min_periods)
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    tr = true_range(high=high, low=low, close=close)
    tr_sum = tr.rolling(length, min_periods=min_periods).sum()

    vmp = (high - low.shift(drift)).abs()
    vmm = (low - high.shift(drift)).abs()

    vip = vmp.rolling(length, min_periods=min_periods).sum() / tr_sum
    vim = vmm.rolling(length, min_periods=min_periods).sum() / tr_sum

    # Offset
    if offset != 0:
        vip = vip.shift(offset)
        vim = vim.shift(offset)

    # Fill
    if "fillna" in kwargs:
        vip.fillna(kwargs["fillna"], inplace=True)
        vim.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    vip.name = f"VTXP_{length}"
    vim.name = f"VTXM_{length}"
    vip.category = vim.category = "trend"

    data = {vip.name: vip, vim.name: vim}
    df = DataFrame(data, index=close.index)
    df.name = f"VTX_{length}"
    df.category = "trend"

    return df


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject

class VORTEX(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int) 
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.period :int=dict_ta_params["period"]
        self.drift  :int=dict_ta_params.get("drift",1)
        self.offset :int=dict_ta_params.get("offset",0)
        
        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"VORTEX {self.period}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.vortex_, self.signalma = np.array([]),np.array([]),np.array([])

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
            self.period :int=dict_ta_params["period"]
            self.drift  :int=dict_ta_params.get("drift",1)
            self.offset :int=dict_ta_params.get("offset",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.period}-{self.drift}"

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
            vortex_,signalma =self.vortex_,self.signalma
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            vortex_,signalma=self.vortex_[:stop],self.signalma[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            vortex_,signalma=self.vortex_[start:],self.signalma[start:]
        else:
            x_data = self.xdata[start:stop]
            vortex_,signalma=self.vortex_[start:stop],self.signalma[start:stop]
        return x_data,vortex_,signalma
    
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
        
        vortex_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("VTXP_"):
                vortex_name = name
            elif name.__contains__("VTXM_"):
                signalma_name = name

        vortex_ = INDICATOR[vortex_name].dropna().round(6)
        signalma = INDICATOR[signalma_name].dropna().round(6)
        
        return vortex_,signalma
    
    @staticmethod
    def calculate(df: pd.DataFrame,period,drift,offset):
        df = df.copy()
        df = df.reset_index(drop=True)
        INDICATOR = vortex(high=df["high"],
                            low=df["low"],
                            close=df["close"],
                            length=period,
                            drift=drift,
                            offset=offset
                            ).dropna()
        column_names = INDICATOR.columns.tolist()
        
        vortex_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("VTXP_"):
                vortex_name = name
            elif name.__contains__("VTXM_"):
                signalma_name = name
        vortex_ = INDICATOR[vortex_name].dropna().round(6)
        signalma = INDICATOR[signalma_name].dropna().round(6)
        _len = min([len(vortex_),len(signalma)])
        _index = df["index"].tail(_len)
        return pd.DataFrame({
                            'index':_index,
                            "vortex":vortex_.tail(_len),
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
                               self.period,self.drift,self.offset)
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
                               self.period,self.drift,self.offset)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.period*5)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.period,self.drift,self.offset)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.period*5)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.period,self.drift,self.offset)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.xdata,self.vortex_, self.signalma = self.df["index"].to_numpy(),self.df["vortex"].to_numpy(),self.df["signalma"].to_numpy()
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
        self.vortex_ = np.concatenate((_df["vortex"].to_numpy(), self.vortex_))
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
        last_vortex = df["vortex"].iloc[-1]
        last_signalma = df["signalma"].iloc[-1]
        new_frame = pd.DataFrame({
                                    'index':[last_index],
                                    "vortex":[last_vortex],
                                    "signalma":[last_signalma]
                                    })
        self.df = pd.concat([self.df,new_frame],ignore_index=True)
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.vortex_ = np.concatenate((self.vortex_,np.array([last_vortex])))
        self.signalma = np.concatenate((self.signalma,np.array([last_signalma])))      
        self.sig_add_candle.emit()
        #self.is_current_update = True
        
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_vortex = df["vortex"].iloc[-1]
        last_signalma = df["signalma"].iloc[-1]
        self.df.iloc[-1] = [last_index,last_vortex,last_signalma]
        self.xdata[-1],self.vortex_[-1], self.signalma[-1]  = last_index,last_vortex,last_signalma
        self.sig_update_candle.emit()
        #self.is_current_update = True
    
    