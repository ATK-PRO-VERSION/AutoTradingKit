from concurrent.futures import Future
import numpy as np
import pandas as pd

from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.momentum import macd
from atklip.controls.tradingview.atr_stoploss import atr_stoploss
from atklip.controls.overlap.supertrend import supertrend

def paire_data(INDICATOR:pd.DataFrame):
    try:
        column_names = INDICATOR.columns.tolist()
        SUPERT_name = ''
        SUPERTd_name = ''
        SUPERTl_name = ''
        SUPERTs_name = ''
        for name in column_names:
            if name.__contains__("SUPERTt"):
                SUPERT_name = name
            elif name.__contains__("SUPERTd"):
                SUPERTd_name = name
            elif name.__contains__("SUPERTl"):
                SUPERTl_name = name
            elif name.__contains__("SUPERTs"):
                SUPERTs_name = name
                
        SUPERTt = INDICATOR[SUPERT_name].dropna().round(6)
        SUPERTd = INDICATOR[SUPERTd_name].dropna().round(6)
        SUPERTl = INDICATOR[SUPERTl_name].round(6)
        SUPERTs = INDICATOR[SUPERTs_name].round(6)
        return SUPERTt,SUPERTd
    except:
        return pd.Series([]),pd.Series([])
    

def supertrend_with_stoploss(data:pd.DataFrame,
                             supertrend_length,
                             supertrend_atr_length,
                             supertrend_multiplier,
                             supertrend_atr_mamode,
                             atr_length=14,atr_mamode="rma",atr_multiplier=1):
    """
    Tính toán Positive Cloud Uptrend và Negative Cloud Uptrend.
    Parameters:
        supertrend_length=self.length,
        supertrend_atr_length=self.supertrend_atr_length,
        supertrend_multiplier=self.supertrend_multiplier,
        supertrend_atr_mamode=self.supertrend_atr_mamode,
        atr_length=self.atr_length,
        atr_mamode=self.atr_mamode,
        atr_multiplier=self.atr_multiplier,

    Returns:
        pd.DataFrame: DataFrame với các cột 'Positive_Cloud_Uptrend' và 'Negative_Cloud_Uptrend'.
    """
    # data = data.copy()
    # Kiểm tra các cột bắt buộc
    required_columns = ['open', 'high', 'low', 'close']
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"DataFrame phải chứa cột '{col}'.")

    # Tính toán EMA của high và low
    atr_stoploss(data,atr_length,atr_mamode,atr_multiplier)
    
    # Tính toán MACD
    INDICATOR = supertrend(high=data["high"], 
                            low=data["low"], 
                            close=data["close"],
                            length = supertrend_length, 
                            atr_length = supertrend_atr_length,
                            multiplier = supertrend_multiplier,
                            atr_mamode = supertrend_atr_mamode,
                            )

    
    SUPERTt,SUPERTd = paire_data(INDICATOR)
    
    long_stoploss = data["long_stoploss"].dropna()
    short_stoploss = data["short_stoploss"].dropna()
    
    lendth = min([len(SUPERTt),len(SUPERTd),len(long_stoploss),len(short_stoploss)])
    
    data["long_stoploss"] = long_stoploss.tail(lendth)
    data["short_stoploss"] = short_stoploss.tail(lendth)
    # data["SUPERTt"] = SUPERTt.tail(lendth)
    data["SUPERTd"] = SUPERTd.tail(lendth)
    
    return data[["long_stoploss","short_stoploss","SUPERTd"]]


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool

from PySide6.QtCore import Signal,QObject

class SuperTrendWithStopLoss(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int)
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)

        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        

        self.supertrend_length = dict_ta_params.get("supertrend_length",14) 
        self.supertrend_atr_length = dict_ta_params.get("supertrend_atr_length",14)
        self.supertrend_multiplier = dict_ta_params.get("supertrend_multiplier",3) 
        self.supertrend_atr_mamode = dict_ta_params.get("supertrend_atr_mamode","rma")
        
        self.atr_length = dict_ta_params.get("atr_length",14) 
        self.atr_mamode = dict_ta_params.get("atr_mamode","rma") 
        self.atr_multiplier = dict_ta_params.get("atr_multiplier",1.5) 
        
        
        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"SuperTrendWithStopLoss"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.long_stoploss,self.short_stoploss,self.SUPERTd = np.array([]),np.array([]),np.array([]),np.array([])

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
    
    def change_input(self,candles=None,dict_ta_params:dict={}):
        if candles != None:
            self.disconnect_signals()
            self._candles : JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE= candles
            self.connect_signals()
        
        if dict_ta_params != {}:
            self.supertrend_length = dict_ta_params.get("supertrend_length",7) 
            self.supertrend_atr_length = dict_ta_params.get("supertrend_atr_length",7)
            self.supertrend_multiplier = dict_ta_params.get("supertrend_multiplier",3) 
            self.supertrend_atr_mamode = dict_ta_params.get("supertrend_atr_mamode","rma")
            
            self.atr_length = dict_ta_params.get("atr_length",14) 
            self.atr_mamode = dict_ta_params.get("atr_mamode","rma") 
            self.atr_multiplier = dict_ta_params.get("atr_multiplier",1) 
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.atr_length}-{self.atr_mamode}-{self.atr_multiplier}"

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
        self._candles.sig_add_historic.connect(self.add_historic_worker)
        self._candles.signal_delete.connect(self.signal_delete)
    
    
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
            long_stoploss,short_stoploss,SUPERTd=self.long_stoploss,self.short_stoploss,self.SUPERTd
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            long_stoploss,short_stoploss,SUPERTd=self.long_stoploss[:stop],self.short_stoploss[:stop],self.SUPERTd[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            long_stoploss,short_stoploss,SUPERTd=self.long_stoploss[start:],self.short_stoploss[start:],self.SUPERTd[start:]
        else:
            x_data = self.xdata[start:stop]
            long_stoploss,short_stoploss,SUPERTd=self.long_stoploss[start:stop],self.short_stoploss[start:stop],self.SUPERTd[start:stop]
        return x_data,long_stoploss,short_stoploss,SUPERTd
    
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
    
    def paire_data(self,INDICATOR:pd.DataFrame):
        try:
            long_stoploss = INDICATOR["long_stoploss"].dropna().round(6)
            short_stoploss = INDICATOR["short_stoploss"].dropna().round(6)
            SUPERTd = INDICATOR["SUPERTd"].dropna()
            return long_stoploss,short_stoploss,SUPERTd
        except:
            return pd.Series([]),pd.Series([]),pd.Series([])
    
    @staticmethod
    def calculate(df: pd.DataFrame,supertrend_length,supertrend_atr_length,
                                    supertrend_multiplier,supertrend_atr_mamode,
                                    atr_length,atr_mamode,atr_multiplier):
        
        df = df.copy()
        df = df.reset_index(drop=True)
        
        INDICATOR = supertrend_with_stoploss(df,
                                            supertrend_length=supertrend_length,
                                            supertrend_atr_length=supertrend_atr_length,
                                            supertrend_multiplier=supertrend_multiplier,
                                            supertrend_atr_mamode=supertrend_atr_mamode,
                                            atr_length=atr_length,
                                            atr_mamode=atr_mamode,
                                            atr_multiplier=atr_multiplier,
                                             )
        
        long_stoploss = INDICATOR["long_stoploss"].dropna().round(6)
        short_stoploss = INDICATOR["short_stoploss"].dropna().round(6)
        SUPERTd = INDICATOR["SUPERTd"].dropna()
        
        _len = min([len(long_stoploss),len(short_stoploss),len(SUPERTd)])
        
        _index = df["index"]
        return pd.DataFrame({
                            'index':_index.tail(_len),
                            "long_stoploss":long_stoploss.tail(_len),
                            "short_stoploss":short_stoploss.tail(_len),
                            "SUPERTd":SUPERTd.tail(_len)
                            })
        
    

    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df,
                               self.supertrend_length,self.supertrend_atr_length,
                                self.supertrend_multiplier,self.supertrend_atr_mamode,
                                self.atr_length,self.atr_mamode,self.atr_multiplier)
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
                               self.supertrend_length,self.supertrend_atr_length,
                                self.supertrend_multiplier,self.supertrend_atr_mamode,
                                self.atr_length,self.atr_mamode,self.atr_multiplier)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.supertrend_length+self.atr_length+self.supertrend_atr_length+10)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.supertrend_length,self.supertrend_atr_length,
                                self.supertrend_multiplier,self.supertrend_atr_mamode,
                                self.atr_length,self.atr_mamode,self.atr_multiplier)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.supertrend_length+self.atr_length+self.supertrend_atr_length+10)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.supertrend_length,self.supertrend_atr_length,
                                self.supertrend_multiplier,self.supertrend_atr_mamode,
                                self.atr_length,self.atr_mamode,self.atr_multiplier)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        
        self.xdata,self.long_stoploss,self.short_stoploss,self.SUPERTd = self.df["index"].to_numpy(),\
                                                                        self.df["long_stoploss"].to_numpy(),\
                                                                        self.df["short_stoploss"].to_numpy(),\
                                                                        self.df["SUPERTd"].to_numpy()                                                                      
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
        self.long_stoploss = np.concatenate((_df["long_stoploss"].to_numpy(), self.long_stoploss)) 
        self.short_stoploss = np.concatenate((_df["short_stoploss"].to_numpy(), self.short_stoploss)) 
        self.SUPERTd = np.concatenate((_df["SUPERTd"].to_numpy(), self.SUPERTd)) 

        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
        
    
    def callback_add(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_long_stoploss = df["long_stoploss"].iloc[-1]
        last_short_stoploss = df["short_stoploss"].iloc[-1]
        last_SUPERTd = df["SUPERTd"].iloc[-1]
        
        
        new_frame = pd.DataFrame({
                                'index':[last_index],
                                "long_stoploss":[last_long_stoploss],
                                "short_stoploss":[last_short_stoploss],
                                "SUPERTd":[last_SUPERTd]
                                })
            
        self.df = pd.concat([self.df,new_frame],ignore_index=True)
        
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.long_stoploss = np.concatenate((self.long_stoploss,np.array([last_long_stoploss])))
        self.short_stoploss = np.concatenate((self.short_stoploss,np.array([last_short_stoploss])))
        self.SUPERTd = np.concatenate((self.SUPERTd,np.array([last_SUPERTd])))

        self.sig_add_candle.emit()
        #self.is_current_update = True
        
    
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_long_stoploss = df["long_stoploss"].iloc[-1]
        last_short_stoploss = df["short_stoploss"].iloc[-1]
        last_SUPERTd = df["SUPERTd"].iloc[-1]
        
        self.df.iloc[-1] = [last_index,last_long_stoploss,last_short_stoploss,last_SUPERTd]
        self.xdata[-1],self.long_stoploss[-1],self.short_stoploss[-1],self.SUPERTd[-1]  = last_index,last_long_stoploss,last_short_stoploss,last_SUPERTd
        self.sig_update_candle.emit()
        #self.is_current_update = True
        