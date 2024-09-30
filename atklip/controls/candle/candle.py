from functools import lru_cache
from typing import Dict, List,Tuple
from dataclasses import dataclass
from atklip.controls.ohlcv import OHLCV
import pandas as pd
import numpy as np,array

from PySide6.QtCore import Qt, Signal,QObject,QCoreApplication
from atklip.appmanager import CandleWorker

#@dataclass
class JAPAN_CANDLE(QObject):
    """
    lastcandle: chính là lastcandle signal của chartview, hiện tại chưa dùng"
    """
    candles: List[OHLCV] = []
    dict_index_ohlcv: Dict[int, OHLCV] = {}
    dict_time_ohlcv: Dict[int, OHLCV] = {}
    sig_update_candle = Signal(list)
    sig_add_candle = Signal(list)
    sig_add_historic = Signal(int)
    sig_reset_all = Signal()
    signal_delete = Signal()
    sig_update_source = Signal()
    
    sig_reset_source = Signal(str)
    
    def __init__(self) -> None:
        super().__init__(parent=None)
        self.first_gen = False
        self._source_name = "JAPAN_CANDLE"
        self.signal_delete.connect(self.deleteLater)
        self.df = pd.DataFrame([])

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

    #@lru_cache(maxsize=128)
    def get_times(self,start:int=0,stop:int=0) -> List[int]:
        if start == 0 and stop == 0:
            return [candle.time for candle in self.candles]
        elif start == 0 and stop != 0:
            return [candle.time for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [candle.time for candle in self.candles[start:]]
        else:
            return [candle.time for candle in self.candles[start:stop]]
    #@lru_cache(maxsize=128)
    def get_indexs(self,start:int=0,stop:int=0) -> List[int]:
        if start == 0 and stop == 0:
            return [candle.index for candle in self.candles]
        elif start == 0 and stop != 0:
            return [candle.index for candle in self.candles[:stop]]
        elif start != 0 and stop == 0:
            return [candle.index for candle in self.candles[start:]]
        else:
            return [candle.index for candle in self.candles[start:stop]]
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
    def get_list_index_data(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_values(start,stop)
        return all_index,all_data

    def last_data(self)->OHLCV:
        if self.candles != []:
            return self.candles[-1]
        else:
            return []
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
    
    def fisrt_gen_data(self,ohlcv,_precision):
        self.first_gen = False
        self.df = pd.DataFrame([])
        self.dict_index_ohlcv: Dict[int, OHLCV] = {}
        self.dict_time_ohlcv: Dict[int, OHLCV] = {}
        self.candles = []
        [self.gen_update(OHLCV(ohlcv[i][1],ohlcv[i][2],ohlcv[i][3],ohlcv[i][4],round((ohlcv[i][2]+ohlcv[i][3])/2,_precision), round((ohlcv[i][2]+ohlcv[i][3]+ohlcv[i][4])/3,_precision), round((ohlcv[i][1]+ohlcv[i][2]+ohlcv[i][3]+ohlcv[i][4])/4,_precision),ohlcv[i][5],ohlcv[i][0]/1000,i)) for i in range(len(ohlcv))]
        self.first_gen = True
        self.df = pd.DataFrame([data.__dict__ for data in self.candles])
        self.sig_reset_all.emit()
        #QCoreApplication.processEvents()
        return self.candles
    
    def load_historic_data(self,ohlcv,_precision):
        ohlcv = ohlcv[::-1]
        self.first_gen = False
        # self.df = pd.DataFrame([])
        candles:List[OHLCV] = []
        [self.update_historic(candles,OHLCV(ohlcv[i][1],ohlcv[i][2],ohlcv[i][3],ohlcv[i][4],round((ohlcv[i][2]+ohlcv[i][3])/2,_precision), round((ohlcv[i][2]+ohlcv[i][3]+ohlcv[i][4])/3,_precision), round((ohlcv[i][1]+ohlcv[i][2]+ohlcv[i][3]+ohlcv[i][4])/4,_precision),ohlcv[i][5],ohlcv[i][0]/1000,i)) for i in range(len(ohlcv))]
        
        if candles != []:
            df = pd.DataFrame([data.__dict__ for data in candles])
            self.df = pd.concat([df, self.df], ignore_index=True)
            
        self.first_gen = True
        self.sig_add_historic.emit(len(ohlcv))
        return self.candles

    def update_historic(self,candles:List[OHLCV],new_candle:OHLCV):
        if len(self.candles) == 0:
            "lấy mốc thời gian 2018 thời điểm data bắt đầu"
            new_candle.index = 1514754000
            self.candles.append(new_candle)
            self.dict_index_ohlcv[new_candle.index] = new_candle
            self.dict_time_ohlcv[new_candle.time] = new_candle
            return
        last_candle = self.candles[0]
        _time = last_candle.time
        if _time == new_candle.time:
            last_candle.open = new_candle.open
            last_candle.high = new_candle.high
            last_candle.low = new_candle.low
            last_candle.close = new_candle.close
            
            last_candle.hl2 = new_candle.hl2
            last_candle.hlc3 = new_candle.hlc3
            last_candle.ohlc4 = new_candle.ohlc4
            
            last_candle.volume = new_candle.volume
            last_candle.time = new_candle.time
            
            self.dict_index_ohlcv[new_candle.index] = new_candle
            self.dict_time_ohlcv[new_candle.time] = new_candle
        else:
            _index = last_candle.index - 1
            _new_candle = OHLCV(new_candle.open,new_candle.high,new_candle.low,new_candle.close,new_candle.hl2,new_candle.hlc3,new_candle.ohlc4,new_candle.volume,new_candle.time,_index)
            self.candles.insert(0,_new_candle)
            candles.insert(0,_new_candle)
            self.dict_index_ohlcv[_new_candle.index] = _new_candle
            self.dict_time_ohlcv[_new_candle.time] = _new_candle
    
    
    def gen_update(self,new_candle:OHLCV):
        if len(self.candles) == 0:
            "lấy mốc thời gian 2018 thời điểm data bắt đầu"
            new_candle.index = 1514754000
            self.candles.append(new_candle)
            self.dict_index_ohlcv[new_candle.index] = new_candle
            self.dict_time_ohlcv[new_candle.time] = new_candle
            return
        last_candle = self.candles[-1]
        _time = last_candle.time
        if _time == new_candle.time:
            last_candle.open = new_candle.open
            last_candle.high = new_candle.high
            last_candle.low = new_candle.low
            last_candle.close = new_candle.close
            
            last_candle.hl2 = new_candle.hl2
            last_candle.hlc3 = new_candle.hlc3
            last_candle.ohlc4 = new_candle.ohlc4
            
            last_candle.volume = new_candle.volume
            last_candle.time = new_candle.time
            
            self.dict_index_ohlcv[new_candle.index] = new_candle
            self.dict_time_ohlcv[new_candle.time] = new_candle
 
        else:
            _index = last_candle.index + 1
            _new_candle = OHLCV(new_candle.open,new_candle.high,new_candle.low,new_candle.close,new_candle.hl2,new_candle.hlc3,new_candle.ohlc4,new_candle.volume,new_candle.time,_index)
            self.candles.append(_new_candle)
            self.dict_index_ohlcv[_new_candle.index] = _new_candle
            self.dict_time_ohlcv[_new_candle.time] = _new_candle

    def update(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if self.first_gen:
            if len(self.candles) == 0:
                "lấy mốc thời gian 1.1.2000 thời điểm data bắt đầu"
                new_candle.index = 946684800
                self.candles.append(new_candle)
                self.dict_index_ohlcv[new_candle.index] = new_candle
                self.dict_time_ohlcv[new_candle.time] = new_candle
                return None
            last_candle = self.candles[-1]
            _time = last_candle.time
            if _time == new_candle.time:
                if new_candle.close != last_candle.close or\
                                        new_candle.high != last_candle.high or\
                                        new_candle.low != last_candle.low or\
                                        new_candle.open != last_candle.open:
                    last_candle.open = new_candle.open
                    last_candle.high = new_candle.high
                    last_candle.low = new_candle.low
                    last_candle.close = new_candle.close
                    
                    last_candle.hl2 = new_candle.hl2
                    last_candle.hlc3 = new_candle.hlc3
                    last_candle.ohlc4 = new_candle.ohlc4
                    
                    last_candle.volume = new_candle.volume
                    last_candle.time = new_candle.time
                    self.dict_index_ohlcv[last_candle.index] = last_candle
                    self.dict_time_ohlcv[last_candle.time] = last_candle
                    
                    self.df.iloc[-1] = [last_candle.open,
                                        last_candle.high,
                                        last_candle.low,
                                        last_candle.close,
                                        last_candle.hl2,
                                        last_candle.hlc3,
                                        last_candle.ohlc4,
                                        last_candle.volume,
                                        last_candle.time,
                                        last_candle.index
                                        ]
                    self.sig_update_candle.emit(self.candles[-2:])
                    return False
                return None
            else:
                pre_candle:OHLCV = new_candles[-2]
                
                last_candle.open = pre_candle.open
                last_candle.high = pre_candle.high
                last_candle.low = pre_candle.low
                last_candle.close = pre_candle.close
                
                last_candle.hl2 = pre_candle.hl2
                last_candle.hlc3 = pre_candle.hlc3
                last_candle.ohlc4 = pre_candle.ohlc4
                
                last_candle.volume = pre_candle.volume
                last_candle.time = pre_candle.time
                _index = last_candle.index + 1
                _new_candle = OHLCV(new_candle.open,new_candle.high,new_candle.low,new_candle.close,new_candle.hl2,new_candle.hlc3,new_candle.ohlc4,new_candle.volume,new_candle.time,_index)
                self.candles.append(_new_candle)
                self.dict_index_ohlcv[_new_candle.index] = _new_candle
                self.dict_time_ohlcv[_new_candle.time] = _new_candle
                
                new_row = pd.DataFrame([data.__dict__ for data in self.candles[-1:]])
                self.df = pd.concat([self.df, new_row], ignore_index=True)
                self.sig_add_candle.emit(self.candles[-2:])
                return True
        return None
            
