# -*- coding: utf-8 -*-
from concurrent.futures import Future
from atklip.appmanager.worker.return_worker import HeavyProcess
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
import numpy as np
from PySide6.QtCore import Signal,QObject
from atklip.controls.pandas_ta.volatility import donchian


class DONCHIAN(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int)    
    
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
            
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
                
        self.lower_length:int = dict_ta_params["lower_length"]
        self.upper_length:int = dict_ta_params["upper_length"]
        self.offset :int=dict_ta_params.get("offset",0)
        
        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"DC {self.lower_length} {self.upper_length}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.lb,self.cb,self.ub = np.array([]),np.array([]),np.array([]),np.array([])

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
            self.lower_length:int = dict_ta_params["lower_length"]
            self.upper_length:int = dict_ta_params["upper_length"]
            self.offset :int=dict_ta_params.get("offset",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.lower_length}-{self.upper_length}"

            self._name = ta_param
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        
        self.first_gen_data()
             
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
            return [],[],[],[]
        if start == 0 and stop == 0:
            x_data = self.xdata
            lb,cb,ub=self.lb,self.cb,self.ub
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            lb,cb,ub=self.lb[:stop],self.cb[:stop],self.ub[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            lb,cb,ub=self.lb[start:],self.cb[start:],self.ub[start:]
        else:
            x_data = self.xdata[start:stop]
            lb,cb,ub=self.lb[start:stop],self.cb[start:stop],self.ub[start:stop]
        return x_data,lb,cb,ub
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 
    
    def update_worker(self,candle):
        self.worker.submit(self.update,candle)

    def add_worker(self,candle):
        self.worker.submit(self.add,candle)
    
    def add_historic_worker(self,n):
        self.worker.submit(self.add_historic,n)

    def started_worker(self):
        self.worker.submit(self.first_gen_data)
    
    @staticmethod
    def calculate(df: pd.DataFrame,lower_length,upper_length,offset):
        df = df.copy()
        df = df.reset_index(drop=True)
        INDICATOR = donchian(high=df["high"],
                            low=df["low"],
                            lower_length=lower_length,
                            upper_length=upper_length,
                            offset=offset)
        
        column_names = INDICATOR.columns.tolist()
        lower_name = ''
        mid_name = ''
        upper_name = ''
        for name in column_names:
            if name.__contains__("DCL_"):
                lower_name = name
            elif name.__contains__("DCM_"):
                mid_name = name
            elif name.__contains__("DCU_"):
                upper_name = name

        df.loc[:, lower_name] = INDICATOR[lower_name].dropna().round(6)
        df.loc[:, mid_name] = INDICATOR[mid_name].dropna().round(6)
        df.loc[:, upper_name] = INDICATOR[upper_name].dropna().round(6)
        _len = min([len(df[lower_name]), len(df[mid_name]), len(df[upper_name])])
        _index = df["index"]
        return pd.DataFrame({
                            'index':_index.tail(_len),
                            "lb":df[lower_name].tail(_len),
                            "cb":df[mid_name].tail(_len),
                            "ub":df[upper_name].tail(_len)
                            })
    
    
    def first_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df,
                               self.lower_length,
                               self.upper_length,
                               self.offset)
        process.start()       
     
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        process = HeavyProcess(self.calculate,
                               self.callback_gen_historic_data,
                               df,
                               self.lower_length,
                               self.upper_length,
                               self.offset)
        process.start() 
        
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.upper_length+self.lower_length+5)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.lower_length,
                               self.upper_length,
                               self.offset)
            process.start() 
            
        else:
            pass
            #self.is_current_update = True
            
    
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.upper_length+self.lower_length+5)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.lower_length,
                               self.upper_length,
                               self.offset)
            process.start() 
        else:
            pass
            #self.is_current_update = True
            
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_numpy(),self.df["lb"].to_numpy(),self.df["cb"].to_numpy(),self.df["ub"].to_numpy()
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
        self.lb = np.concatenate((_df["lb"].to_numpy(), self.lb))   
        self.cb = np.concatenate((_df["cb"].to_numpy(), self.cb))
        self.ub = np.concatenate((_df["ub"].to_numpy(), self.ub))
                
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False 
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
    
    def callback_add(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_lb = df["lb"].iloc[-1]
        last_cb = df["cb"].iloc[-1]
        last_ub = df["ub"].iloc[-1]
         
        new_frame = pd.DataFrame({
                                'index':[last_index],
                                "lb":[last_lb],
                                "cb":[last_cb],
                                "ub":[last_ub]
                                })

        self.df = pd.concat([self.df,new_frame],ignore_index=True)                     
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.lb = np.concatenate((self.lb,np.array([last_lb])))
        self.cb = np.concatenate((self.cb,np.array([last_cb])))
        self.ub = np.concatenate((self.ub,np.array([last_ub])))
        self.sig_add_candle.emit()
        #self.is_current_update = True
    
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_lb = df["lb"].iloc[-1]
        last_cb = df["cb"].iloc[-1]
        last_ub = df["ub"].iloc[-1]      
        self.df.loc[-1] = [last_index, last_lb, last_cb, last_ub]
        self.xdata[-1],self.lb[-1],self.cb[-1],self.ub[-1] = last_index,last_lb,last_cb,last_ub
        self.sig_update_candle.emit()
        #self.is_current_update = True
