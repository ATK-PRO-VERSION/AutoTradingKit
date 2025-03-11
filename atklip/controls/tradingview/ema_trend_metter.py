from concurrent.futures import Future
import numpy as np
import pandas as pd
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.ma_overload import ema, ma

def ema_trend_metter(df: pd.DataFrame, base_ema_length: int=13, ema_length_1: int=21, ema_length_2: int=34, ema_length_3: int=55) -> pd.DataFrame:
    df = df.copy()
    df = df.reset_index(drop=True)
    
    max_len = max([base_ema_length, ema_length_1, ema_length_2, ema_length_3])
    df['EMA0'] = ema(df['close'], length=base_ema_length)
    df['EMA1'] = ema(df['close'], length=ema_length_1)
    df['EMA2'] = ema(df['close'], length=ema_length_2)
    df['EMA3'] = ema(df['close'], length=ema_length_3)
    # Determine Bullish conditions
    # df['EMA1_Color'] = np.where(df['Bull1'], 'green', 'red')
    # df['EMA2_Color'] = np.where(df['Bull2'], 'green', 'red')
    # df['EMA3_Color'] = np.where(df['Bull3'], 'green', 'red')
    
    df['up'] = (df['EMA1'] < df['EMA0']) & (df['EMA2'] < df['EMA0']) & (df['EMA3'] < df['EMA0'])
    df['down'] = (df['EMA1'] > df['EMA0']) & (df['EMA2'] > df['EMA0']) & (df['EMA3'] > df['EMA0'])
    df = df.iloc[max_len+1:]
    return df[['up','down']]


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject

class EMA_TREND_METTER(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()   
    sig_add_historic = Signal(int)  
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.base_ema_length  :int=dict_ta_params.get("base_ema_length",13)
        self.ema_length_1  :int=dict_ta_params.get("ema_length_1",21)
        self.ema_length_2  :int=dict_ta_params.get("ema_length_2",34)
        self.ema_length_3  :int=dict_ta_params.get("ema_length_3",55)
        

        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"EMA TREND METTER-{self.base_ema_length}-{self.ema_length_1}-{self.ema_length_2}-{self.ema_length_3}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.uptrend , self.downtrend = np.array([]),np.array([]),np.array([])

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
            self.base_ema_length  :int=dict_ta_params.get("base_ema_length",13)
            self.ema_length_1  :int=dict_ta_params.get("ema_length_1",21)
            self.ema_length_2  :int=dict_ta_params.get("ema_length_2",34)
            self.ema_length_3  :int=dict_ta_params.get("ema_length_3",55)
            
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.base_ema_length}-{self.ema_length_1}-{self.ema_length_2}-{self.ema_length_3}"

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
            return self.xdata,self.uptrend,self.downtrend
        if start == 0 and stop == 0:
            x_data = self.xdata
            uptrend,downtrend =self.uptrend,self.downtrend
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            uptrend,downtrend=self.uptrend[:stop],self.downtrend[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            uptrend,downtrend=self.uptrend[start:],self.downtrend[start:]
        else:
            x_data = self.xdata[start:stop]
            uptrend,downtrend=self.uptrend[start:stop],self.downtrend[start:stop]
        return x_data,uptrend,downtrend
    
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
        uptrend_name = 'up'
        downtrend_name = 'down'
        uptrend = INDICATOR[uptrend_name].dropna().round(6)
        downtrend = INDICATOR[downtrend_name].dropna().round(6)
        return uptrend,downtrend
    
    @staticmethod
    def calculate(df: pd.DataFrame,base_ema_length,ema_length_1,ema_length_2,ema_length_3):
        df = df.copy()
        df = df.reset_index(drop=True)
        
        INDICATOR = ema_trend_metter(df=df,
                                    base_ema_length = base_ema_length,
                                    ema_length_1 = ema_length_1,
                                    ema_length_2 = ema_length_2,
                                    ema_length_3 = ema_length_3).dropna()
        
        uptrend_name = 'up'
        downtrend_name = 'down'
        uptrend = INDICATOR[uptrend_name].dropna().round(6)
        downtrend = INDICATOR[downtrend_name].dropna().round(6)
 
        _len = min([len(uptrend),len(downtrend)])
        _index = df["index"].tail(_len)

        return pd.DataFrame({
                            'index':_index,
                            "uptrend":uptrend.tail(_len),
                            "downtrend":downtrend.tail(_len)
                            })
        
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df,
                               self.base_ema_length,self.ema_length_1,self.ema_length_2,self.ema_length_3)
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
                               self.base_ema_length,self.ema_length_1,self.ema_length_2,self.ema_length_3)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.base_ema_length+
                                                   self.ema_length_1+
                                                   self.ema_length_2+
                                                   self.ema_length_3+5)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.base_ema_length,self.ema_length_1,self.ema_length_2,self.ema_length_3)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.base_ema_length+
                                                   self.ema_length_1+
                                                   self.ema_length_2+
                                                   self.ema_length_3+5)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.base_ema_length,self.ema_length_1,self.ema_length_2,self.ema_length_3)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.xdata,self.uptrend, self.downtrend = self.df["index"].to_numpy(),\
                                                self.df["uptrend"].to_numpy(),\
                                                self.df["downtrend"].to_numpy()
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
        self.uptrend = np.concatenate((_df["uptrend"].to_numpy(), self.uptrend))   
        self.downtrend = np.concatenate((_df["downtrend"].to_numpy(), self.downtrend))  
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
        
    def callback_add(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_uptrend = df["uptrend"].iloc[-1]
        last_downtrend = df["downtrend"].iloc[-1]
        new_frame = pd.DataFrame({
                                    'index':[last_index],
                                    "uptrend":[last_uptrend],
                                    "downtrend":[last_downtrend]
                                    })
        self.df = pd.concat([self.df,new_frame],ignore_index=True)
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.uptrend = np.concatenate((self.uptrend,np.array([last_uptrend])))
        self.downtrend = np.concatenate((self.downtrend,np.array([last_downtrend])))                            
        self.sig_add_candle.emit()
        #self.is_current_update = True
        
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_uptrend = df["uptrend"].iloc[-1]
        last_downtrend = df["downtrend"].iloc[-1]
        self.df.iloc[-1] = [last_index,last_uptrend,last_downtrend]
        self.xdata[-1],self.uptrend[-1], self.downtrend[-1]  = last_index,last_uptrend,last_downtrend
        self.sig_update_candle.emit()
        #self.is_current_update = True
        