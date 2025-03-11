# -*- coding: utf-8 -*-
from concurrent.futures import Future
from atklip.controls.ma_overload import ma

import numpy as np
import pandas as pd
from typing import List
from .ohlcv import   OHLCV
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from atklip.appmanager.worker import HeavyProcess
from PySide6.QtCore import Qt, Signal,QObject

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
class MA(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()
    sig_add_historic = Signal(int)    
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        
        self.mamode:str = dict_ta_params.get("mamode")
        self.source:str = dict_ta_params.get("source")
        self.length:int= dict_ta_params.get("length") 
        self.zl_mode:str= dict_ta_params.get("zl_mode","ema") 
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"{self.mamode} {self.source} {self.length}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata = np.array([])
        self.ydata = np.array([])

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
            self.mamode:str = dict_ta_params.get("mamode")
            self.source:str = dict_ta_params.get("source")
            self.length:int= dict_ta_params.get("length") 
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.mamode}-{self.length}"

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
    
    def change_source(self,_candles):
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
    
    def callback_first_gen(self,future:Future):
        _index,data = future.result()
        
        self.df = pd.DataFrame({
                            'index':_index,
                            "data":data
                            })
        
        self.xdata,self.ydata = self.df["index"].to_numpy(),self.df["data"].to_numpy()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        #self.is_current_update = True
        self.sig_reset_all.emit()
        
    @staticmethod
    def _gen_data(df,mamode,source,length,zl_mode):
        data = ma(mamode,source=df[source],length=length,mamode=zl_mode).dropna().round(6)
        _len = len(data)
        _index = df["index"].tail(_len)
        
        return _index,data

    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self._gen_data,self.callback_first_gen,df,self.mamode,self.source,self.length,self.zl_mode)
        process.start()
    
    def call_back_add_historic(self,future:Future):
        _index,data = future.result()
        _df = pd.DataFrame({
                            'index':_index,
                            "data":data
                            })
        
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        self.xdata = np.concatenate((_df["index"].to_numpy(), self.xdata)) 
        self.ydata = np.concatenate((_df["data"].to_numpy(), self.ydata))  
           
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False        
        self.is_histocric_load = True
        _len = len(data)
        self.sig_add_historic.emit(_len)
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        process = HeavyProcess(self._gen_data,self.call_back_add_historic,df,self.mamode,self.source,self.length,self.zl_mode)
        process.start()

    def add(self,new_candles:List[OHLCV]):
        self.is_current_update = False
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*10)
                        
            process = HeavyProcess(self._gen_data,self.callback_add,df,self.mamode,self.source,self.length,self.zl_mode)
            process.start()
            
    def callback_add(self,future:Future):
        index,data = future.result()
        _data = data.iloc[-1]
        _index = index.iloc[-1]
            
        new_frame = pd.DataFrame({
                            'index':[_index],
                            "data":[_data]
                            })
        self.df = pd.concat([self.df,new_frame],ignore_index=True)            
        self.xdata = np.concatenate((self.xdata,np.array([_index])))
        self.ydata = np.concatenate((self.ydata,np.array([_data])))
        self.sig_add_candle.emit()
        #self.is_current_update = True
            
    def callback_update(self,future:Future):
        index,data = future.result()
        _data = data.iloc[-1]
        _index = index.iloc[-1]

        self.df.iloc[-1] = [_index,data.iloc[-1]]
        self.xdata[-1] = _index
        self.ydata[-1] = _data
        self.sig_update_candle.emit()
        #self.is_current_update = True
    
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*10)
            process = HeavyProcess(self._gen_data,self.callback_update,df,self.mamode,self.source,self.length,self.zl_mode)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
            
            
            
            
            