from functools import lru_cache
import numpy as np
import time
import pandas as pd
from typing import Dict, List,Tuple
from dataclasses import dataclass
from PySide6.QtCore import Qt, Signal,QObject,QCoreApplication,QThreadPool,Slot

from atklip.controls import pandas_ta as ta
from atklip.controls.ma_type import  PD_MAType
from atklip.controls.ohlcv import   OHLCV

from .candle import JAPAN_CANDLE
from .heikinashi import HEIKINASHI
from atklip.appmanager import FastWorker,CandleWorker

class SMOOTH_CANDLE(QObject):
    """
    _candles: JAPAN_CANDLE|HEIKINASHI 
    lastcandle: signal(list)  - the list of 2 last candle of para "_candles: JAPAN_CANDLE|HEIKINASHI"
    ma_type: IndicatorType  - IndicatorType.SMA
    period: int - 20
    """
    sig_update_candle = Signal(list)
    sig_add_candle = Signal(list)
    sig_reset_all = Signal()
    sig_add_historic = Signal(int)
    candles : List[OHLCV] = []
    dict_index_time = {}
    signal_delete = Signal()
    sig_update_source = Signal()
    
    
    sig_reset_source = Signal(str)
    
    def __init__(self,precision,_candles,ma_type,period) -> None:
        super().__init__(parent=None)
        self.ma_type:str = ma_type
        self.period:int= period
        self._candles: JAPAN_CANDLE|HEIKINASHI|self =_candles
        
        self.signal_delete.connect(self.deleteLater)
        
        self._precision = precision
        self.first_gen = False
        self.is_genering = True
        self._source_name = f"{self.period}_SMOOTH_CANDLE"

        self.df = pd.DataFrame([])

        self._candles.sig_update_source.connect(self.sig_update_source,Qt.ConnectionType.AutoConnection)
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
    def source_name(self,_name):
        self._source_name = _name
    
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
    def threadpool_asyncworker(self):
        self.worker = None
        self.worker = CandleWorker(self.fisrt_gen_data)
        self.worker.start()
    @Slot()
    def update_historic_worker(self,n):
        self.worker = None
        self.worker = CandleWorker(self.gen_historic_data,n)
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
            return []
    #@lru_cache(maxsize=128)
    def get_ma_ohlc_at_index(self,df: pd.DataFrame|None,index):
        #print(index,)
        # _index = self.opens.iloc[index]
        if df is None:
            df = self.df
        _open, _high, _low, _close, _hl2, _hlc3, _ohlc4, _volume, _time = df["open"].iloc[index],\
            df["high"].iloc[index],df["low"].iloc[index],df["close"].iloc[index],\
            df["hl2"].iloc[index],df["hlc3"].iloc[index],df["ohlc4"].iloc[index],df["volume"].iloc[index],df["time"].iloc[index]
        if _open != None and  _high != None and _low != None and _close != None:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4 = round(_open,self._precision),round(_high,self._precision),round(_low,self._precision),round(_close,self._precision),\
                    round(_hl2,self._precision),round(_hlc3,self._precision),round(_ohlc4,self._precision)
            return [_open, _high, _low, _close, _hl2, _hlc3, _ohlc4,_volume, _time]
        return []
    
    
    def update_ma_ohlc(self,lastcandle:OHLCV):
        _new_time = lastcandle.time
        if self.candles != []:
            _last_time = self.candles[-1].time
            df:pd.DataFrame = self._candles.get_df(self.period*5)
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

            if _new_time == _last_time:
                
                self.df.iloc[-1] = [opens.iloc[-1],
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

                self.df = pd.concat([self.df,new_df],ignore_index=True)


    def compute(self,index, i:int):
        _index = index[i]
        ohlc = self.get_ma_ohlc_at_index(None,i)
        if ohlc != []:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4,_volume, _time = ohlc[0],ohlc[1],ohlc[2],ohlc[3],ohlc[4],ohlc[5],ohlc[6],ohlc[7],ohlc[8]
            ha_candle = OHLCV(_open,_high,_low,_close, _hl2, _hlc3, _ohlc4,_volume,_time,_index)
            self.dict_index_ohlcv[ha_candle.index] = ha_candle
            self.dict_time_ohlcv[ha_candle.time] = ha_candle
            self.candles.append(ha_candle)

    
    def compute_historic(self,df: pd.DataFrame,index:np.array, i:int):
        _index = index[i]
        if _index in list(self.dict_index_ohlcv.keys()):
            return
        ohlc = self.get_ma_ohlc_at_index(df,i)
        if ohlc != []:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4,_volume, _time = ohlc[0],ohlc[1],ohlc[2],ohlc[3],ohlc[4],ohlc[5],ohlc[6],ohlc[7],ohlc[8]
            ha_candle = OHLCV(_open,_high,_low,_close, _hl2, _hlc3, _ohlc4,_volume,_time,_index)
            self.dict_index_ohlcv[ha_candle.index] = ha_candle
            self.dict_time_ohlcv[ha_candle.time] = ha_candle
            self.candles.insert(i,ha_candle)
    
    
    def refresh_data(self,ma_type,ma_period,n_smooth_period):
        self.reset_parameters(ma_type,ma_period,n_smooth_period)
        self.fisrt_gen_data()
    
    def reset_parameters(self,ma_type,ma_period,n_smooth_period = None):
        self.ma_type = ma_type
        self.period = ma_period
        # self.n = n_smooth_period    
    
    @Slot()
    def gen_historic_data(self,n_len):
        self.is_genering = True
                
        _pre_len = len(self.df)

        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        self.highs = ta.ma(f"{self.ma_type}".lower(), df["high"],length=self.period).dropna()
        self.highs = self.highs.astype('float32')

        self.lows = ta.ma(f"{self.ma_type}".lower(), df["low"],length=self.period).dropna()
        self.lows = self.lows.astype('float32')

        self.closes = ta.ma(f"{self.ma_type}".lower(), df["close"],length=self.period).dropna()
        self.closes = self.closes.astype('float32')

        self.opens = ta.ma(f"{self.ma_type}".lower(), df["open"],length=self.period).dropna()
        self.opens = self.opens.astype('float32')

        self.hl2s = ta.ma(f"{self.ma_type}".lower(), df["hl2"],length=self.period).dropna()
        self.hl2s = self.hl2s.astype('float32')

        self.hlc3s = ta.ma(f"{self.ma_type}".lower(), df["hlc3"],length=self.period).dropna()
        self.hlc3s = self.hlc3s.astype('float32')

        self.ohlc4s = ta.ma(f"{self.ma_type}".lower(), df["ohlc4"],length=self.period).dropna()
        self.ohlc4s = self.ohlc4s.astype('float32')

        _len = len(self.ohlc4s)
        
        _df = pd.DataFrame({  "open": self.opens,
                                    "high": self.highs,
                                    "low": self.lows,
                                    "close": self.closes,
                                    "hl2": self.hl2s,
                                    "hlc3": self.hlc3s,
                                    "ohlc4": self.ohlc4s,
                                    "volume": df["volume"].tail(_len),
                                    "time": df["time"].tail(_len),
                                    "index": df["index"].tail(_len)
                                })
        
        _index = _df["index"].to_list()
        
        # print(_df["index"].iloc[-1],_df["index"].iloc[-2],_df["index"].iloc[-3])
        # print(self.df["index"].iloc[0])
        
        self.df = pd.concat([_df,self.df], ignore_index=True)
        
        [self.compute_historic(_df,_index,i) for i in range(len(_df))]
        
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
        
        df:pd.DataFrame = self._candles.get_df()
        self.highs = ta.ma(f"{self.ma_type}".lower(), df["high"],length=self.period).dropna()
        self.highs = self.highs.astype('float32')

        self.lows = ta.ma(f"{self.ma_type}".lower(), df["low"],length=self.period).dropna()
        self.lows = self.lows.astype('float32')

        self.closes = ta.ma(f"{self.ma_type}".lower(), df["close"],length=self.period).dropna()
        self.closes = self.closes.astype('float32')

        self.opens = ta.ma(f"{self.ma_type}".lower(), df["open"],length=self.period).dropna()
        self.opens = self.opens.astype('float32')

        self.hl2s = ta.ma(f"{self.ma_type}".lower(), df["hl2"],length=self.period).dropna()
        self.hl2s = self.hl2s.astype('float32')

        self.hlc3s = ta.ma(f"{self.ma_type}".lower(), df["hlc3"],length=self.period).dropna()
        self.hlc3s = self.hlc3s.astype('float32')

        self.ohlc4s = ta.ma(f"{self.ma_type}".lower(), df["ohlc4"],length=self.period).dropna()
        self.ohlc4s = self.ohlc4s.astype('float32')

        _len = len(self.ohlc4s)
        
        self.df = pd.DataFrame({  "open": self.opens,
                                    "high": self.highs,
                                    "low": self.lows,
                                    "close": self.closes,
                                    "hl2": self.hl2s,
                                    "hlc3": self.hlc3s,
                                    "ohlc4": self.ohlc4s,
                                    "volume": df["volume"].tail(_len),
                                    "time": df["time"].tail(_len),
                                    "index": df["index"].tail(_len)
                                })
        
        _index = self.df["index"].to_list()
        
        [self.compute(_index,i) for i in range(len(self.df))]

        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
        return self.candles
    @Slot()
    def update(self, _candle:List[OHLCV]):
        print("smoothcandle", _candle)
        if (self.first_gen == True) and (self.is_genering == False):
            if self._candles.candles != []:
                new_candle = _candle[-1]
                self.update_ma_ohlc(new_candle)
                ohlc = self.get_ma_ohlc_at_index(None,-1)
                _open, _high, _low, _close = ohlc[0],ohlc[1],ohlc[2],ohlc[3]
                hl2 = ohlc[4]
                hlc3 = ohlc[5]
                ohlc4 = ohlc[6]

                if new_candle.time == self.candles[-1].time:
                    _index = self.candles[-1].index
                    ha_candle = OHLCV(_open,_high,_low,_close,hl2,hlc3,ohlc4,new_candle.volume,new_candle.time,_index)
                    if ha_candle.close != self.candles[-1].close or\
                        ha_candle.high != self.candles[-1].high or\
                        ha_candle.low != self.candles[-1].low or\
                        ha_candle.open != self.candles[-1].open:
                        self.candles[-1] = ha_candle
                        
                        self.dict_index_ohlcv[ha_candle.index] = ha_candle
                        self.dict_time_ohlcv[ha_candle.time] = ha_candle
                        
                        self.df.iloc[-1] = [self.candles[-1].open,
                                        self.candles[-1].high,
                                        self.candles[-1].low,
                                        self.candles[-1].close,
                                        self.candles[-1].hl2,
                                        self.candles[-1].hlc3,
                                        self.candles[-1].ohlc4,
                                        self.candles[-1].volume,
                                        self.candles[-1].time,
                                        self.candles[-1].index
                                        ]
                        
                        self.sig_update_candle.emit(self.candles[-2:])
                        #QCoreApplication.processEvents()
                        return False
                else:
                    _index = self.candles[-1].index + 1
                    ha_candle = OHLCV(_open,_high,_low,_close,hl2,hlc3,ohlc4,new_candle.volume,new_candle.time,_index)
                    
                    self.dict_index_ohlcv[ha_candle.index] = ha_candle
                    self.dict_time_ohlcv[ha_candle.time] = ha_candle
                    
                    self.candles.append(ha_candle)
                    new_row = pd.DataFrame([data.__dict__ for data in self.candles[-1:]])
                    self.df = pd.concat([self.df, new_row], ignore_index=True)
                    self.sig_add_candle.emit(self.candles[-2:])
                    #QCoreApplication.processEvents()
                    return True
        return False
            