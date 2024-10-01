from functools import lru_cache
import numpy as np
import time
import pandas as pd
from typing import Any, Dict, List,Tuple
from dataclasses import dataclass
from PySide6.QtCore import Qt, Signal,QObject,QCoreApplication,Slot

from atklip.controls import pandas_ta as ta
from atklip.controls.ma_type import  PD_MAType
from atklip.controls.ohlcv import   OHLCV

from .candle import JAPAN_CANDLE
from .heikinashi import HEIKINASHI

from atklip.appmanager import CandleWorker

class N_SMOOTH_CANDLE(QObject):
    """
    _candles: JAPAN_CANDLE|HEIKINASHI 
    lastcandle: signal(list)  - the list of 2 last candle of para "_candles: JAPAN_CANDLE|HEIKINASHI"
    ma_type: IndicatorType  - IndicatorType.SMA
    period: int - 20
    """
    sig_update_candle = Signal(list)
    sig_add_candle = Signal(list)
    sig_add_historic = Signal(int)
    sig_reset_all = Signal()
    candles : List[OHLCV] = []
    dict_index_time = {}
    dict_n_ma:Dict[str,pd.Series] = {}
    dict_n_frame:Dict[str,pd.DataFrame] = {}
    signal_delete = Signal()
    
    sig_reset_source = Signal(str)
    
    sig_update_source = Signal()
    def __init__(self,precision,_candles,n,ma_type,period) -> None:
        super().__init__(parent=None)
        self.ma_type:str = ma_type
        self.period:int= period
        self._candles:JAPAN_CANDLE|HEIKINASHI =_candles
        self.n:int = n
            
        self.signal_delete.connect(self.deleteLater)
        self._candles.sig_update_source.connect(self.sig_update_source,Qt.ConnectionType.AutoConnection)
        self._precision = precision
        self.first_gen = False
        self.is_genering = True
        self._source_name = f"N_SMOOTH_CANDLE_{self.period}_{self.n}"
        self.df = pd.DataFrame([])
        
        self._candles.sig_reset_all.connect(self.fisrt_gen_data,Qt.ConnectionType.AutoConnection)
        self._candles.sig_update_candle.connect(self.update,Qt.ConnectionType.QueuedConnection)
        self._candles.sig_add_candle.connect(self.update,Qt.ConnectionType.QueuedConnection)
        self._candles.sig_add_historic.connect(self.gen_historic_data,Qt.ConnectionType.QueuedConnection)

    
    def connect_signals(self):
        self._candles.sig_update_source.connect(self.sig_update_source,Qt.ConnectionType.AutoConnection)
        self._candles.sig_reset_all.connect(self.fisrt_gen_data,Qt.ConnectionType.AutoConnection)
        self._candles.sig_update_candle.connect(self.update,Qt.ConnectionType.QueuedConnection)
        self._candles.sig_add_candle.connect(self.update,Qt.ConnectionType.QueuedConnection)
        self._candles.sig_add_historic.connect(self.gen_historic_data,Qt.ConnectionType.QueuedConnection)
    
    def disconnect_signals(self):
        try:
            self._candles.sig_update_source.disconnect(self.sig_update_source)
            self._candles.sig_reset_all.disconnect(self.fisrt_gen_data)
            self._candles.sig_update_candle.disconnect(self.update)
            self._candles.sig_add_candle.disconnect(self.update)
            self._candles.sig_add_historic.disconnect(self.gen_historic_data)
        except:
            pass
    
    def update_source(self,candle:JAPAN_CANDLE|HEIKINASHI):
        self.disconnect_signals()
        self._candles = candle
        self.connect_signals()
    
    
    @property
    def source_name(self):
        return self._source_name
    @source_name.setter
    def source_name(self,_source_name):
        self._source_name = _source_name
        
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_last_row_df(self):
        return self.df.iloc[-1]
    @Slot()
    def update_worker(self,candle):
        self.worker_ = None
        self.worker_ = CandleWorker(self.update,candle)
        self.worker_.start()
    @Slot()
    def update_historic_worker(self,n):
        self.worker = None
        self.worker = CandleWorker(self.gen_historic_data,n)
        self.worker.start()

    @Slot()
    def threadpool_asyncworker(self):
        self.worker = None
        self.worker = CandleWorker(self.fisrt_gen_data)
        self.worker.start()
     
    #@lru_cache(maxsize=128)
    def get_times(self,start:int=0,stop:int=0) -> List[str]:
        if start == 0 and stop == 0:
            return [candle.time for candle in self.candles]
        elif start == 0 and stop != 0:
            return [candle.time for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [candle.time for candle in self.candles[start:]]
        else:
            return [candle.time for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_values(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [[candle.open, candle.high, candle.low, candle.close] for candle in self.candles]
        elif start == 0 and stop != 0:
            return [[candle.open, candle.high, candle.low, candle.close] for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [[candle.open, candle.high, candle.low, candle.close] for candle in self.candles[start:]]
        else:
            return [[candle.open, candle.high, candle.low, candle.close] for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_indexs(self,start:int=0,stop:int=0) -> List[str]:
        if start == 0 and stop == 0:
            return [candle.index for candle in self.candles]
        elif start == 0 and stop != 0:
            return [candle.index for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [candle.index for candle in self.candles[start:]]
        else:
            return [candle.index for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_candles(self,n:int=0) -> List[OHLCV]:
        if n == 0:
            return self.candles
        else:
            return self.candles[n:]
    #@lru_cache(maxsize=128)
    def get_n_first_candles(self,n:int=0) -> List[OHLCV]:
        if n == 0:
            return self.candles
        else:
            return self.candles[:n]
        
    def getspecialvalues(self,_type):
        if _type == 'open':
            return [candle.index for candle in self.candles], [candle.open for candle in self.candles]
        elif _type == 'high':
            return [candle.index for candle in self.candles], [candle.high for candle in self.candles]
        elif _type == 'low':
            return [candle.index for candle in self.candles], [candle.low for candle in self.candles]
        elif _type == 'close':
            return [candle.index for candle in self.candles], [candle.close for candle in self.candles]
        elif _type == 'volume':
            return [candle.index for candle in self.candles], [candle.volume for candle in self.candles]
        elif _type == 'hl2':
            return [candle.index for candle in self.candles], [candle.hl2 for candle in self.candles]
        elif _type == 'hlc3':
            return [candle.index for candle in self.candles], [candle.hlc3 for candle in self.candles]
        elif _type == 'ohlc4':
            return [candle.index for candle in self.candles], [candle.ohlc4 for candle in self.candles]
        else:
            return [], []
    
    #@lru_cache(maxsize=128)
    def get_data(self,start:int=0,stop:int=0):
        all_time = self.get_times(start,stop)
        all_data = self.get_values(start,stop)
        all_time_np = np.array(all_time)
        all_data_np = np.array(all_data)
        return all_time_np,all_data_np
    
    #@lru_cache(maxsize=128)
    def get_volumes(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [[candle.open, candle.close, candle.volume] for candle in self.candles]
        elif start == 0 and stop != 0:
            return [[candle.open, candle.close, candle.volume] for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [[candle.open, candle.close, candle.volume] for candle in self.candles[start:]]
        else:
            return [[candle.open, candle.close, candle.volume] for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_ohlc4(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [sum([candle.open, candle.close, candle.high, candle.low])/4 for candle in self.candles]
        elif start == 0 and stop != 0:
            return [sum([candle.open, candle.close, candle.high, candle.low])/4 for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [sum([candle.open, candle.close, candle.high, candle.low])/4 for candle in self.candles[start:]]
        else:
            return [sum([candle.open, candle.close, candle.high, candle.low])/4 for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_hlc3(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [sum([candle.close, candle.high, candle.low])/3 for candle in self.candles]
        elif start == 0 and stop != 0:
            return [sum([candle.close, candle.high, candle.low])/3 for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [sum([candle.close, candle.high, candle.low])/3 for candle in self.candles[start:]]
        else:
            return [sum([candle.close, candle.high, candle.low])/3 for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_hl2(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            return [sum([candle.high, candle.low])/2 for candle in self.candles]
        elif start == 0 and stop != 0:
            return [sum([candle.high, candle.low])/2 for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [sum([candle.high, candle.low])/2 for candle in self.candles[start:]]
        else:
            return [sum([candle.high, candle.low])/2 for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_index_hl2(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_hl2(start,stop)
        all_index_np = np.array(all_index)
        all_data_np = np.array(all_data)
        return all_index_np,all_data_np
    #@lru_cache(maxsize=128)
    def get_index_hlc3(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_hlc3(start,stop)
        all_index_np = np.array(all_index)
        all_data_np = np.array(all_data)
        return all_index_np,all_data_np
    #@lru_cache(maxsize=128)
    def get_index_ohlc4(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_ohlc4(start,stop)
        all_index_np = np.array(all_index)
        all_data_np = np.array(all_data)
        return all_index_np,all_data_np
    
    def get_index_data(self,start:int=0,stop:int=0):
        if start == 0 and stop == 0:
            all_index = self.df["index"].to_list()
            all_open = self.df["open"].to_list()
            all_high = self.df["high"].to_list()
            all_low = self.df["low"].to_list()
            all_close = self.df["close"].to_list()
        elif start == 0 and stop != 0:
            all_index = self.df["index"].iloc[:stop].to_list()
            all_open = self.df["open"].iloc[:stop].to_list()
            all_high = self.df["high"].iloc[:stop].to_list()
            all_low = self.df["low"].iloc[:stop].to_list()
            all_close = self.df["close"].iloc[:stop].to_list()
            
        elif start != 0 and stop == 0:
            all_index = self.df["index"].iloc[start:].to_list()
            all_open = self.df["open"].iloc[start:].to_list()
            all_high = self.df["high"].iloc[start:].to_list()
            all_low = self.df["low"].iloc[start:].to_list()
            all_close = self.df["close"].iloc[start:].to_list()
        else:
            all_index = self.df["index"].iloc[start:stop].to_list()
            all_open = self.df["open"].iloc[start:stop].to_list()
            all_high = self.df["high"].iloc[start:stop].to_list()
            all_low = self.df["low"].iloc[start:stop].to_list()
            all_close = self.df["close"].iloc[start:stop].to_list()
        
        return {"index":all_index,"data":[all_open,all_high,all_low,all_close]}
    
    def get_index_volumes(self,start:int=0,stop:int=0):
        if start == 0 and stop == 0:
            all_index = self.df["index"].to_list()
            all_open = self.df["open"].to_list()            
            all_close = self.df["close"].to_list()
            all_volume = self.df["volume"].to_list()
        elif start == 0 and stop != 0:
            all_index = self.df["index"].iloc[:stop].to_list()
            all_open = self.df["open"].iloc[:stop].to_list()
            all_volume = self.df["volume"].iloc[:stop].to_list()
            all_close = self.df["close"].iloc[:stop].to_list()
            
        elif start != 0 and stop == 0:
            all_index = self.df["index"].iloc[start:].to_list()
            all_open = self.df["open"].iloc[start:].to_list()
            all_volume = self.df["volume"].iloc[start:].to_list()
            all_close = self.df["close"].iloc[start:].to_list()
        else:
            all_index = self.df["index"].iloc[start:stop].to_list()
            all_open = self.df["open"].iloc[start:stop].to_list()
            all_volume = self.df["volume"].iloc[start:stop].to_list()
            all_close = self.df["close"].iloc[start:stop].to_list()
        return {"index":all_index,"data":[all_open,all_close,all_volume]}
    def get_last_candle(self):
        return self.df.iloc[-1].to_dict()
    #@lru_cache(maxsize=128)
    def last_data(self)->OHLCV:
        if self.candles != []:
            return self.candles[-1]
        else:
            self.dict_n_frame[f"{self.n}-candles"][-1]
    #@lru_cache(maxsize=128)
    def get_ma_ohlc_at_index(self,index:int,opens:pd.Series,highs:pd.Series,lows:pd.Series,closes:pd.Series,hl2s:pd.Series,hlc3s:pd.Series,ohlc4s:pd.Series):
        #_index = opens.output_times.get(index)
        ohlc = [opens._dict_time_value.get(index),highs._dict_time_value.get(index),lows._dict_time_value.get(index),closes._dict_time_value.get(index),\
            hl2s._dict_time_value.get(index),hlc3s._dict_time_value.get(index),ohlc4s._dict_time_value.get(index)]
        return index, ohlc
    
    def update_ma_ohlc(self,lastcandle:OHLCV):
        _new_time = lastcandle.time
        self.dict_n_frame[f"0-candles"] = self._candles.get_df()
        _last_time = self.df["time"].iloc[-1]
        _is_update = False

        if _new_time == _last_time:
            _is_update =  True
        
        for i in range(self.n):
            df = self.dict_n_frame[f"{i}-candles"].tail(self.period*self.n*5) #
            highs = ta.ma(f"{self.ma_type}".lower(), df["high"],length=self.period).dropna()
            highs = highs.astype('float32')
            lows = ta.ma(f"{self.ma_type}".lower(), df["low"],length=self.period).dropna()
            lows = lows.astype('float32')
            closes = ta.ma(f"{self.ma_type}".lower(), df["close"],length=self.period).dropna()
            closes = closes.astype('float32')
            opens = ta.ma(f"{self.ma_type}".lower(), df["open"],length=self.period).dropna()
            opens = opens.astype('float32')
            hl2s = ta.ma(f"{self.ma_type}".lower(), df["hl2"],length=self.period).dropna()
            hl2s = hl2s.astype('float32')
            hlc3s = ta.ma(f"{self.ma_type}".lower(), df["hlc3"],length=self.period).dropna()
            hlc3s = hlc3s.astype('float32')
            ohlc4s = ta.ma(f"{self.ma_type}".lower(), df["ohlc4"],length=self.period).dropna()
            ohlc4s = ohlc4s.astype('float32')
            
            if _is_update:
                self.dict_n_frame[f"{i+1}-candles"].iloc[-1] = [opens.iloc[-1],
                                                                highs.iloc[-1],
                                                                lows.iloc[-1],
                                                                closes.iloc[-1],
                                                                hl2s.iloc[-1],
                                                                hlc3s.iloc[-1],
                                                                ohlc4s.iloc[-1],
                                                                df["volume"].iloc[-1],
                                                                df["time"].iloc[-1],
                                                                df["index"].iloc[-1]]
            else:
                new_df = pd.DataFrame({ "open": [opens.iloc[-1]],
                                        "high": [highs.iloc[-1]],
                                        "low": [lows.iloc[-1]],
                                        "close": [closes.iloc[-1]],
                                        "hl2": [hl2s.iloc[-1]],
                                        "hlc3": [hlc3s.iloc[-1]],
                                        "ohlc4": [ohlc4s.iloc[-1]],
                                        "volume": [df["volume"].iloc[-1]],
                                        "time": [df["time"].iloc[-1]],
                                        "index": [df["index"].iloc[-1]]
                                    })

                self.dict_n_frame[f"{i+1}-candles"] = pd.concat([self.dict_n_frame[f"{i+1}-candles"],new_df],ignore_index=True)

        self.df = self.dict_n_frame[f"{self.n}-candles"]          
        
        return _is_update
    
    def compute(self,pre_frame: pd.DataFrame,opens,highs,lows,closes,hl2s,hlc3s,ohlc4s):
            
        new_frame = pd.DataFrame({  "open": opens,
                                    "high": highs,
                                    "low": lows,
                                    "close": closes,
                                    "hl2": hl2s,
                                    "hlc3": hlc3s,
                                    "ohlc4": ohlc4s,
                                    "volume": pre_frame["volume"],
                                    "time": pre_frame["time"],
                                    "index": pre_frame["index"]
                                })
        return new_frame
        
    def refresh_data(self,ma_type,ma_period,n_smooth_period):
        self.reset_parameters(ma_type,ma_period,n_smooth_period)
        self.fisrt_gen_data()
    
    def reset_parameters(self,ma_type,ma_period,n_smooth_period):
        self.ma_type = ma_type
        self.period = ma_period
        self.n = n_smooth_period
    
    def _gen_data(self):
        # len_old = len(self.candles)
        self.dict_n_frame[f"0-candles"] = self._candles.get_df()
        for i in range(self.n):
            self.dict_n_ma[f"{i+1}-highs"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"{i}-candles"]["high"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-highs"] = self.dict_n_ma[f"{i+1}-highs"].astype('float32')

            self.dict_n_ma[f"{i+1}-lows"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"{i}-candles"]["low"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-lows"] = self.dict_n_ma[f"{i+1}-lows"].astype('float32')

            self.dict_n_ma[f"{i+1}-closes"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"{i}-candles"]["close"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-closes"] = self.dict_n_ma[f"{i+1}-closes"].astype('float32')

            self.dict_n_ma[f"{i+1}-opens"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"{i}-candles"]["open"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-opens"] = self.dict_n_ma[f"{i+1}-opens"].astype('float32')

            self.dict_n_ma[f"{i+1}-hl2s"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"{i}-candles"]["hl2"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-hl2s"] = self.dict_n_ma[f"{i+1}-hl2s"].astype('float32')

            self.dict_n_ma[f"{i+1}-hlc3s"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"{i}-candles"]["hlc3"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-hlc3s"] = self.dict_n_ma[f"{i+1}-hlc3s"].astype('float32')

            self.dict_n_ma[f"{i+1}-ohlc4s"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"{i}-candles"]["ohlc4"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-ohlc4s"] = self.dict_n_ma[f"{i+1}-ohlc4s"].astype('float32')

            self.dict_n_frame[f"{i+1}-candles"] = self.compute(self.dict_n_frame[f"{i}-candles"],\
                                    self.dict_n_ma[f"{i+1}-opens"],\
                                    self.dict_n_ma[f"{i+1}-highs"],\
                                    self.dict_n_ma[f"{i+1}-lows"],\
                                    self.dict_n_ma[f"{i+1}-closes"],\
                                    self.dict_n_ma[f"{i+1}-hl2s"],\
                                    self.dict_n_ma[f"{i+1}-hlc3s"],\
                                    self.dict_n_ma[f"{i+1}-ohlc4s"])
        return self.dict_n_frame[f"{self.n}-candles"]   
    
    def _gen_historic_data(self):
        len_old = len(self.candles)
        self.dict_n_frame[f"old_0-candles"] = self._candles.get_df()
        for i in range(self.n):
            self.dict_n_ma[f"{i+1}-highs"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"old_{i}-candles"]["high"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-highs"] = self.dict_n_ma[f"{i+1}-highs"].astype('float32')

            self.dict_n_ma[f"{i+1}-lows"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"old_{i}-candles"]["low"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-lows"] = self.dict_n_ma[f"{i+1}-lows"].astype('float32')

            self.dict_n_ma[f"{i+1}-closes"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"old_{i}-candles"]["close"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-closes"] = self.dict_n_ma[f"{i+1}-closes"].astype('float32')

            self.dict_n_ma[f"{i+1}-opens"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"old_{i}-candles"]["open"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-opens"] = self.dict_n_ma[f"{i+1}-opens"].astype('float32')

            self.dict_n_ma[f"{i+1}-hl2s"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"old_{i}-candles"]["hl2"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-hl2s"] = self.dict_n_ma[f"{i+1}-hl2s"].astype('float32')

            self.dict_n_ma[f"{i+1}-hlc3s"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"old_{i}-candles"]["hlc3"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-hlc3s"] = self.dict_n_ma[f"{i+1}-hlc3s"].astype('float32')

            self.dict_n_ma[f"{i+1}-ohlc4s"] = ta.ma(f"{self.ma_type}".lower(), self.dict_n_frame[f"old_{i}-candles"]["ohlc4"],length=self.period).dropna()
            self.dict_n_ma[f"{i+1}-ohlc4s"] = self.dict_n_ma[f"{i+1}-ohlc4s"].astype('float32')

            self.dict_n_frame[f"old_{i+1}-candles"] = self.compute(self.dict_n_frame[f"old_{i}-candles"],\
                                    self.dict_n_ma[f"{i+1}-opens"],\
                                    self.dict_n_ma[f"{i+1}-highs"],\
                                    self.dict_n_ma[f"{i+1}-lows"],\
                                    self.dict_n_ma[f"{i+1}-closes"],\
                                    self.dict_n_ma[f"{i+1}-hl2s"],\
                                    self.dict_n_ma[f"{i+1}-hlc3s"],\
                                    self.dict_n_ma[f"{i+1}-ohlc4s"])
        return self.dict_n_frame[f"old_{self.n}-candles"]  

    def gen_candles(self):
        for i in range(len(self.df)):
            _open,_high,_low,_close,hl2,hlc3,ohlc4,_volume,_time,_index = self.df["open"].iloc[i],self.df["high"].iloc[i],self.df["low"].iloc[i],self.df["close"].iloc[i],\
                  self.df["hl2"].iloc[i], self.df["hlc3"].iloc[i], self.df["ohlc4"].iloc[i],self.df["volume"].iloc[i],\
                      self.df["time"].iloc[i],self.df["index"].iloc[i]
            variables = [_open,_high,_low,_close,hl2,hlc3,ohlc4,_volume,_time,_index]
            if _index not in list(self.dict_index_ohlcv.keys()):
                if not any(v is None for v in variables):
                    ohlcv = OHLCV(_open,_high,_low,_close,hl2,hlc3,ohlc4,_volume,_time,_index)
                    self.dict_index_ohlcv[ohlcv.index] = ohlcv
                    self.dict_time_ohlcv[ohlcv.time] = ohlcv
                    self.candles.append(ohlcv)
    
    @Slot()
    def gen_historic_data(self,n_len):
        self.is_genering = True
        self._gen_data()
        self.df = self.dict_n_frame[f"{self.n}-candles"]
        self.gen_candles()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_add_historic.emit(n_len)
        return self.candles
    
    @Slot()
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        self.candles:List[OHLCV] = []
        self.dict_index_ohlcv: Dict[int, OHLCV] = {}
        self.dict_time_ohlcv: Dict[int, OHLCV] = {}
        self.dict_n_frame.clear()
        self.dict_n_ma.clear()
        self._gen_data()
        self.df = self.dict_n_frame[f"{self.n}-candles"]
        self.gen_candles()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    @Slot()
    def update(self, _candle:List[OHLCV]):
        if (self.first_gen == True) and (self.is_genering == False):
            if self._candles.candles != []:
                new_candle = _candle[-1]
                is_update = self.update_ma_ohlc(new_candle)
                self.df = self.dict_n_frame[f"{self.n}-candles"]
                _open,_high,_low,_close,hl2,hlc3,ohlc4,_volume,_time,_index = self.df["open"].iloc[-1],self.df["high"].iloc[-1],self.df["low"].iloc[-1],self.df["close"].iloc[-1],\
                  self.df["hl2"].iloc[-1], self.df["hlc3"].iloc[-1], self.df["ohlc4"].iloc[-1],self.df["volume"].iloc[-1],\
                      self.df["time"].iloc[-1],self.df["index"].iloc[-1]
                
                ohlcv = OHLCV(_open,_high,_low,_close,hl2,hlc3,ohlc4,_volume,_time,_index)
                
                self.dict_index_ohlcv[ohlcv.index] = ohlcv
                self.dict_time_ohlcv[ohlcv.time] = ohlcv
                
                if is_update:
                    self.candles[-1] = ohlcv
                    self.sig_update_candle.emit(self.candles[-2:])
                    #QCoreApplication.processEvents()
                    return False
                else:
                    self.candles.append(ohlcv)
                    self.sig_add_candle.emit(self.candles[-2:])
                    #QCoreApplication.processEvents()
                    return True
                
        return False