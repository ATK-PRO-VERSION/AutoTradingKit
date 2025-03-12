# -*- coding: utf-8 -*-
from concurrent.futures import Future
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta.momentum import stc
import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool

from PySide6.QtCore import Signal,QObject

class STC(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int)
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.source:str = dict_ta_params["source"]              
        self.tclength:int= dict_ta_params["tclength"]
        self.fast:int = dict_ta_params["fast"]
        self.slow:int = dict_ta_params["slow"]
        self.mamode:str = dict_ta_params["mamode"]
        self.factor  :float=dict_ta_params.get("factor",0.5)
        self.offset :int=dict_ta_params.get("offset",0)

        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"STC {self.source} {self.slow} {self.fast} {self.tclength} {self.mamode}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.stc_,self.macd,self.stoch = np.array([]),np.array([]),np.array([]),np.array([])

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
            self.tclength:int= dict_ta_params["tclength"]
            self.fast:int = dict_ta_params["fast"]
            self.slow:int = dict_ta_params["slow"]
            self.mamode:str = dict_ta_params["mamode"]
            self.factor  :float=dict_ta_params.get("factor",0.5)
            self.offset :int=dict_ta_params.get("offset",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.mamode}-{self.tclength}-{self.fast}-{self.slow}"

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
            return {"x_data":[],"stc_":[],"macd":[],"stoch":[]}
        if start == 0 and stop == 0:
            x_data = self.xdata
            stc_,macd,stoch=self.stc_,self.macd,self.stoch
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            stc_,macd,stoch=self.stc_[:stop],self.macd[:stop],self.stoch[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            stc_,macd,stoch=self.stc_[start:],self.macd[start:],self.stoch[start:]
        else:
            x_data = self.xdata[start:stop]
            stc_,macd,stoch=self.stc_[start:stop],self.macd[start:stop],self.stoch[start:stop]
        return x_data,stc_,macd,stoch
    
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
        
        stc_name = ''
        stoch_name = ''
        macd_name = ''
        for name in column_names:
            if name.__contains__("STC") and stc_name == "":
                stc_name = name
            if name.__contains__("STCstoch") and stoch_name == "":
                stoch_name = name
            if name.__contains__("STCmacd") and macd_name == "":
                macd_name = name
        stc_ = INDICATOR[stc_name].dropna().round(6)
        macd = INDICATOR[macd_name].dropna().round(6)
        stoch = INDICATOR[stoch_name].dropna().round(6)
        return stc_,macd,stoch
    
    @staticmethod
    def calculate(df: pd.DataFrame,source,tclength,fast,slow,mamode,factor,offset):
        df = df.copy()
        df = df.reset_index(drop=True)
        
        INDICATOR = stc(close= df[source],
                        tclength= tclength,
                        fast = fast,
                        slow = slow,
                        mamode= mamode,
                        factor=factor,
                        offset=offset
                        ).dropna()
        
        column_names = INDICATOR.columns.tolist()
        
        stc_name = ''
        stoch_name = ''
        macd_name = ''
        for name in column_names:
            if name.__contains__("STC") and stc_name == "":
                stc_name = name
            if name.__contains__("STCstoch") and stoch_name == "":
                stoch_name = name
            if name.__contains__("STCmacd") and macd_name == "":
                macd_name = name
        stc_ = INDICATOR[stc_name].dropna().round(6)
        macd = INDICATOR[macd_name].dropna().round(6)
        stoch = INDICATOR[stoch_name].dropna().round(6)
        
        _len = min([len(stc_),len(macd),len(stoch)])
        _index = df["index"].tail(_len)
        
        return pd.DataFrame({
                            'index':_index,
                            "stc":stc_.tail(_len),
                            "macd":macd.tail(_len),
                            "stoch":stoch.tail(_len)
                            })
        
        
        

    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df,
                               self.source,self.tclength,
                               self.fast,self.slow,
                               self.mamode,self.factor,self.offset)
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
                               self.source,self.tclength,
                               self.fast,self.slow,
                               self.mamode,self.factor,self.offset)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow*5)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.source,self.tclength,
                               self.fast,self.slow,
                               self.mamode,self.factor,self.offset)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow*5)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.source,self.tclength,
                               self.fast,self.slow,
                               self.mamode,self.factor,self.offset)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.xdata,self.stc_,self.macd,self.stoch = self.df["index"].to_numpy(),self.df["stc"].to_numpy(),self.df["macd"].to_numpy(),self.df["stoch"].to_numpy()
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
        self.stc_ = np.concatenate((_df["stc"].to_numpy(), self.stc_))
        self.macd = np.concatenate((_df["macd"].to_numpy(), self.macd))
        self.stoch = np.concatenate((_df["stoch"].to_numpy(), self.stoch))
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
        
         
    def callback_add(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_stc = df["stc"].iloc[-1]
        last_macd = df["macd"].iloc[-1]
        last_stoch = df["stoch"].iloc[-1]
        
        new_frame = pd.DataFrame({
                                    'index':[last_index],
                                    "stc":[last_stc],
                                    "macd":[last_macd],
                                    "stoch":[last_stoch]
                                    })
            
        self.df = pd.concat([self.df,new_frame],ignore_index=True)     
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.stc_ = np.concatenate((self.stc_,np.array([last_stc])))
        self.macd = np.concatenate((self.macd,np.array([last_macd])))             
        self.stoch = np.concatenate((self.stoch,np.array([last_stoch])))             
        self.sig_add_candle.emit()
        #self.is_current_update = True
        
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_stc = df["stc"].iloc[-1]
        last_macd = df["macd"].iloc[-1]
        last_stoch = df["stoch"].iloc[-1]
        self.df.iloc[-1] = [last_index,last_stc,last_macd,last_stoch]
        self.xdata[-1],self.stc_[-1],self.macd[-1],self.stoch[-1] = last_index,last_stc,last_macd,last_stoch
        self.sig_update_candle.emit()
        #self.is_current_update = True
        