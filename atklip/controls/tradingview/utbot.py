from concurrent.futures import Future
import numpy as np
import pandas as pd
from atklip.app_utils.helpers import crossover
from atklip.appmanager.worker.return_worker import HeavyProcess

from atklip.controls import atr
from atklip.controls.ma_overload import ema, ma

import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject


def xATRTrailingStop_func(close, prev_close, prev_atr, nloss):
    if close > prev_atr and prev_close > prev_atr:
        return max(prev_atr, close - nloss)
    elif close < prev_atr and prev_close < prev_atr:
        return min(prev_atr, close + nloss)
    elif close > prev_atr:
        return close - nloss
    else:
        return close + nloss


def utbot(dataframe:pd.DataFrame, key_value=1, atr_period=10, ema_period=1, ma_atr_mode="rma", ma_mode="ema"):
    # ATR Calculation
    data = dataframe.copy()
    
    data = data.reset_index(drop=True)
    
    src = data["close"]
    high = data["high"]
    low = data["low"]
    
    data["xATR"] = atr(high, low, src, length=atr_period,mamode=ma_atr_mode)
    data["nLoss"] = key_value * data["xATR"]

    data["ATRTrailingStop"] = [0.0] + [np.nan for i in range(len(data) - 1)]
 
    for i in range(1, len(data)):
        data.loc[i, "ATRTrailingStop"] = xATRTrailingStop_func(
            data.loc[i, "close"],
            data.loc[i - 1, "close"],
            data.loc[i - 1, "ATRTrailingStop"],
            data.loc[i, "nLoss"],
        )
    # EMA for crossover logic
    _ema = ema(src, length=ema_period)
    data["Above"] = crossover(_ema,data["ATRTrailingStop"])  
    data["Below"] = crossover(data["ATRTrailingStop"],_ema)  
    
    data["long"] = (src > data["ATRTrailingStop"]) & (data["Above"]==1)
    data["short"] = (src < data["ATRTrailingStop"]) & (data["Below"]==1)
    kq = data.iloc[max([ema_period,atr_period])-1:]
    return kq[["long", "short"]]


class UTBOT_ALERT(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int) 
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles

        self.key_value_long:int=dict_ta_params.get("key_value_long",1)
        self.key_value_short:int=dict_ta_params.get("key_value_short",1)
        
        self.atr_long_period:float=dict_ta_params.get("atr_long_period",10)
        self.ema_long_period:int=dict_ta_params.get("ema_long_period",1) 
        
        self.atr_short_period:float=dict_ta_params.get("atr_short_period",10)
        self.ema_short_period:int=dict_ta_params.get("ema_short_period",1) 

        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"ATKPRO Ver_1.0"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.long,self.short= np.array([]),np.array([]),np.array([])

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
            self.key_value_long:int=dict_ta_params.get("key_value_long",1)
            self.key_value_short:int=dict_ta_params.get("key_value_short",1)
            
            self.atr_long_period:float=dict_ta_params.get("atr_long_period",3)
            self.ema_long_period:int=dict_ta_params.get("ema_long_period",500) 
            
            self.atr_short_period:float=dict_ta_params.get("atr_short_period",3)
            self.ema_short_period:int=dict_ta_params.get("ema_short_period",20) 
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name} L {self.atr_long_period} {self.ema_long_period} S {self.atr_short_period} {self.ema_short_period}"

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
            return self.xdata,self.long,self.short
        if start == 0 and stop == 0:
            x_data = self.xdata
            _long =self.long
            _short =self.short
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            _long =self.long[:stop]
            _short =self.short[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            _long =self.long[start:]
            _short =self.short[start:]
        else:
            x_data = self.xdata[start:stop]
            _long =self.long[start:stop]
            _short =self.short[start:stop]
        return np.array(x_data),np.array(_long),np.array(_short)
    
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
    
    @staticmethod
    def paire_data(INDICATOR:pd.DataFrame|pd.Series):
        _long,_short = INDICATOR["long"],INDICATOR["short"]
        return _long,_short
    
    @staticmethod
    def calculate(df: pd.DataFrame,key_value_long,atr_long_period,ema_long_period,
                                    key_value_short,atr_short_period,ema_short_period):
        df = df.copy()
        df = df.reset_index(drop=True)
        
        LONG = utbot(dataframe=df,
                            key_value=key_value_long,
                            atr_period=atr_long_period,
                            ema_period=ema_long_period
                            )
        
        SHORT = utbot(dataframe=df,
                            key_value=key_value_short,
                            atr_period=atr_short_period,
                            ema_period=ema_short_period
                            )
        _long = LONG["long"]
        _short = SHORT["short"]
        
        _len = min([len(_long),len(_short)])
        
        _index = df["index"].tail(_len)
        _long = _long.tail(_len)
        _short = _short.tail(_len)
        
        return pd.DataFrame({
                            'index':_index,
                            "long":_long,
                            "short":_short
                            })
        
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        self.xdata,self.long,self.short = np.array([]),np.array([]),np.array([])
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df,
                               self.key_value_long,self.atr_long_period,self.ema_long_period,
                                self.key_value_short,self.atr_short_period,self.ema_short_period)
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
                               self.key_value_long,self.atr_long_period,self.ema_long_period,
                                self.key_value_short,self.atr_short_period,self.ema_short_period)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(int(self.atr_short_period+self.ema_short_period+10))
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.key_value_long,self.atr_long_period,self.ema_long_period,
                                self.key_value_short,self.atr_short_period,self.ema_short_period)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(int(self.atr_short_period+self.ema_short_period+10))
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.key_value_long,self.atr_long_period,self.ema_long_period,
                                self.key_value_short,self.atr_short_period,self.ema_short_period)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        
        self.xdata,self.long,self.short = self.df["index"].to_numpy(),self.df["long"].to_numpy(),self.df["short"].to_numpy()
        
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
        self.long = np.concatenate((_df["long"].to_numpy(), self.long))   
        self.short = np.concatenate((_df["short"].to_numpy(), self.short))
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
        
    def callback_add(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_long = df["long"].iloc[-1]
        last_short = df["short"].iloc[-1]
        new_frame = pd.DataFrame({
                                    'index':[last_index],
                                    "long":[last_long],
                                    "short":[last_short]
                                    })
        self.df = pd.concat([self.df,new_frame],ignore_index=True)
        self.xdata = np.append(self.xdata,last_index)
        self.long = np.append(self.long,last_long)
        self.short = np.append(self.short,last_short)
        self.sig_add_candle.emit()
        #self.is_current_update = True
        
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_long = df["long"].iloc[-1]
        last_short = df["short"].iloc[-1]
        self.df.iloc[-1] = [last_index,last_long,last_short]
        self.xdata[-1],self.long[-1],self.short[-1] = last_index,last_long,last_short
        self.sig_update_candle.emit()
        #self.is_current_update = True
          