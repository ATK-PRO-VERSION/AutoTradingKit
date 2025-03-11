from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
import pandas as pd
from typing import List,Dict
from PySide6.QtCore import QObject,Signal
from atklip.controls.ohlcv import OHLCV
from .candle import JAPAN_CANDLE



class HEIKINASHI(QObject):
    """
    lastcandle: signal(list)  - the list of 2 last candle of para "_candles: JAPAN_CANDLE|HEIKINASHI"
    """
    map_index_ohlcv: Dict[int, OHLCV] = {}
    map_time_ohlcv: Dict[int, OHLCV] = {}
    sig_update_candle = Signal(list)
    sig_add_candle = Signal(list)
    sig_add_historic = Signal(int)
    sig_reset_all = Signal()
    candles : List[OHLCV] = []
    dict_index_time = {}
    signal_delete = Signal()
    sig_update_source = Signal()
    
    def __init__(self,Chart,_candle) -> None:
        super().__init__(parent=None)
        self._candles:JAPAN_CANDLE = _candle
        self.chart = Chart
        self.exchange_id:str
        self.symbol:str
        self.interval:str
        self.start_index:int = 0
        self.stop_index:int = 0
        self.first_gen = False
        self._source_name = "HEIKINASHI"
        self.precision = self.chart.get_precision()
        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        self.is_current_update = False
        # self.signal_delete.connect(self.delete)
    @property
    def is_current_update(self)-> bool:
        return self._is_current_update
    @is_current_update.setter
    def is_current_update(self,_is_current_update):
        self._is_current_update = _is_current_update
    def set_candle_infor(self,exchange_id,symbol,interval):
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.interval = interval
    
    def get_candle_infor(self):
        return self.exchange_id, self.symbol, self.interval
    
    # def delete(self):
    #     self.deleteLater()
    
    def connect_signals(self):
        if not isinstance(self._candles,JAPAN_CANDLE):
            self._candles.setParent(self)
            self.signal_delete.connect(self._candles.signal_delete)
        self._candles.sig_update_source.connect(self.sig_update_source)
    
    def disconnect_signals(self):
        try:
            if not isinstance(self._candles,JAPAN_CANDLE):
                self.signal_delete.disconnect(self._candles.signal_delete)
            self._candles.sig_update_source.disconnect(self.sig_update_source)
        except:
            pass
    
    def update_source(self,candle:JAPAN_CANDLE):
        self.disconnect_signals()
        self._candles = candle
        self.precision = self.chart.get_precision()
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
        if n > len(self.df):
            return self.df
        return self.df.tail(n)
    
    def get_last_row_df(self):
        return self.df.iloc[-1]
    
    def threadpool_asyncworker(self,candle:any=None):
        self.worker.submit(self.update,candle)

    #@lru_cache(maxsize=128)
    def get_times(self,start:int=0,stop:int=0) -> List[int]:
        if start == 0 and stop == 0:
            avg = self.df["time"].to_numpy()
        elif start == 0 and stop != 0:
            avg = self.df["time"].iloc[:stop].to_numpy()
        elif start != 0 and stop == 0:
            avg = self.df["time"].iloc[start:].to_numpy()
        else:
            avg = self.df["time"].iloc[start:stop].to_numpy()
        return avg
        
    #@lru_cache(maxsize=128)
    def get_indexs(self,start:int=0,stop:int=0) -> List[int]:
        if start == 0 and stop == 0:
            avg = self.df["index"].to_numpy()
        elif start == 0 and stop != 0:
            avg = self.df["index"].iloc[:stop].to_numpy()
        elif start != 0 and stop == 0:
            avg = self.df["index"].iloc[start:].to_numpy()
        else:
            avg = self.df["index"].iloc[start:stop].to_numpy()
        return avg
        
    #@lru_cache(maxsize=128)
    def get_values(self,start:int=0,stop:int=0) -> List[List[float]]:
        
        if start == 0 and stop == 0:
            avg = [self.df["open"].to_numpy(),self.df["high"].to_numpy(),self.df["low"].to_numpy(),self.df["close"].to_numpy()]
        elif start == 0 and stop != 0:
            avg = [self.df["open"].iloc[:stop].to_numpy(),self.df["high"].iloc[:stop].to_numpy(),self.df["low"].iloc[:stop].to_numpy(),self.df["close"].iloc[:stop].to_numpy()]
        elif start != 0 and stop == 0:
            avg = [self.df["open"].iloc[start:].to_numpy(),self.df["high"].iloc[start:].to_numpy(),self.df["low"].iloc[start:].to_numpy(),self.df["close"].iloc[start:].to_numpy()]
        else:
            avg = [self.df["open"].iloc[start:stop].to_numpy(),self.df["high"].iloc[start:stop].to_numpy(),self.df["low"].iloc[start:stop].to_numpy(),self.df["close"].iloc[start:stop].to_numpy()]
        return avg
    #@lru_cache(maxsize=128)
    def get_volumes(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            avg = [self.df["open"].to_numpy(),self.df["close"].to_numpy(),self.df["volume"].to_numpy()]
        elif start == 0 and stop != 0:
            avg = [self.df["open"].iloc[:stop].to_numpy(),self.df["close"].iloc[:stop].to_numpy(),self.df["volume"].iloc[:stop].to_numpy()]
        elif start != 0 and stop == 0:
            avg = [self.df["open"].iloc[start:].to_numpy(),self.df["close"].iloc[start:].to_numpy(),self.df["volume"].iloc[start:].to_numpy()]
        else:
            avg = [self.df["open"].iloc[start:stop].to_numpy(),self.df["close"].iloc[start:stop].to_numpy(),self.df["volume"].iloc[start:stop].to_numpy()]
        return avg

    #@lru_cache(maxsize=128)
    def get_n_last_candles(self,n:int=0) -> List[OHLCV]:
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

    def get_data(self,start:int=0,stop:int=0):
        all_time = self.get_times(start,stop)
        all_data = self.get_values(start,stop)
        return all_time,all_data

    #@lru_cache(maxsize=128)
    def get_index_data(self,start:int=0,stop:int=0):
        if start == 0 and stop == 0:
            all_index = self.df["index"].to_numpy()
            all_open = self.df["open"].to_numpy()
            all_high = self.df["high"].to_numpy()
            all_low = self.df["low"].to_numpy()
            all_close = self.df["close"].to_numpy()
        elif start == 0 and stop != 0:
            all_index = self.df["index"].iloc[:stop].to_numpy()
            all_open = self.df["open"].iloc[:stop].to_numpy()
            all_high = self.df["high"].iloc[:stop].to_numpy()
            all_low = self.df["low"].iloc[:stop].to_numpy()
            all_close = self.df["close"].iloc[:stop].to_numpy()
            
        elif start != 0 and stop == 0:
            all_index = self.df["index"].iloc[start:].to_numpy()
            all_open = self.df["open"].iloc[start:].to_numpy()
            all_high = self.df["high"].iloc[start:].to_numpy()
            all_low = self.df["low"].iloc[start:].to_numpy()
            all_close = self.df["close"].iloc[start:].to_numpy()
        else:
            all_index = self.df["index"].iloc[start:stop].to_numpy()
            all_open = self.df["open"].iloc[start:stop].to_numpy()
            all_high = self.df["high"].iloc[start:stop].to_numpy()
            all_low = self.df["low"].iloc[start:stop].to_numpy()
            all_close = self.df["close"].iloc[start:stop].to_numpy()
        
        return all_index,[all_open,all_high,all_low,all_close]
    
    def get_index_volumes(self,start:int=0,stop:int=0):
        if start == 0 and stop == 0:
            all_index = self.df["index"].to_numpy()
            all_open = self.df["open"].to_numpy()            
            all_close = self.df["close"].to_numpy()
            all_volume = self.df["volume"].to_numpy()
        elif start == 0 and stop != 0:
            all_index = self.df["index"].iloc[:stop].to_numpy()
            all_open = self.df["open"].iloc[:stop].to_numpy()
            all_volume = self.df["volume"].iloc[:stop].to_numpy()
            all_close = self.df["close"].iloc[:stop].to_numpy()
            
        elif start != 0 and stop == 0:
            all_index = self.df["index"].iloc[start:].to_numpy()
            all_open = self.df["open"].iloc[start:].to_numpy()
            all_volume = self.df["volume"].iloc[start:].to_numpy()
            all_close = self.df["close"].iloc[start:].to_numpy()
        else:
            all_index = self.df["index"].iloc[start:stop].to_numpy()
            all_open = self.df["open"].iloc[start:stop].to_numpy()
            all_volume = self.df["volume"].iloc[start:stop].to_numpy()
            all_close = self.df["close"].iloc[start:stop].to_numpy()
        return all_index,[all_open,all_close,all_volume]
    
    #@lru_cache(maxsize=128)
    def get_ohlc4(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            avg = (self.df["open"].to_numpy() + self.df["high"].to_numpy() + self.df["low"].to_numpy() + self.df["close"].to_numpy()) / 4
        elif start == 0 and stop != 0:
            avg = (self.df["open"].to_numpy() + self.df["high"].iloc[:stop].to_numpy() + self.df["low"].iloc[:stop].to_numpy() + self.df["close"].to_numpy()) / 4
        elif start != 0 and stop == 0:
            avg = (self.df["open"].to_numpy() + self.df["high"].iloc[start:].to_numpy() + self.df["low"].iloc[start:].to_numpy() + self.df["close"].to_numpy()) / 4
        else:
            avg = (self.df["open"].to_numpy() + self.df["high"].iloc[start:stop].to_numpy() + self.df["low"].iloc[start:stop].to_numpy() + self.df["close"].to_numpy()) / 4
        return avg
    
    #@lru_cache(maxsize=128)
    def get_hlc3(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            avg = (self.df["high"].to_numpy() + self.df["low"].to_numpy() + self.df["close"].to_numpy()) / 3
        elif start == 0 and stop != 0:
            avg = (self.df["high"].iloc[:stop].to_numpy() + self.df["low"].iloc[:stop].to_numpy() + self.df["close"].to_numpy()) / 3
        elif start != 0 and stop == 0:
            avg = (self.df["high"].iloc[start:].to_numpy() + self.df["low"].iloc[start:].to_numpy() + self.df["close"].to_numpy()) / 3
        else:
            avg = (self.df["high"].iloc[start:stop].to_numpy() + self.df["low"].iloc[start:stop].to_numpy() + self.df["close"].to_numpy()) / 3
        return avg
    
    #@lru_cache(maxsize=128)
    def get_hl2(self,start:int=0,stop:int=0) -> List[List[float]]:
        if start == 0 and stop == 0:
            avg = (self.df["high"].to_numpy() + self.df["low"].to_numpy()) / 2
        elif start == 0 and stop != 0:
            avg = (self.df["high"].iloc[:stop].to_numpy() + self.df["low"].iloc[:stop].to_numpy()) / 2
        elif start != 0 and stop == 0:
            avg = (self.df["high"].iloc[start:].to_numpy() + self.df["low"].iloc[start:].to_numpy()) / 2
        else:
            avg = (self.df["high"].iloc[start:stop].to_numpy() + self.df["low"].iloc[start:stop].to_numpy()) / 2
        return avg
    #@lru_cache(maxsize=128)
    def get_index_hl2(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_hl2(start,stop)
        return all_index,all_data
    #@lru_cache(maxsize=128)
    def get_index_hlc3(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_hlc3(start,stop)
        return all_index,all_data
    #@lru_cache(maxsize=128)
    def get_index_ohlc4(self,start:int=0,stop:int=0):
        all_index = self.get_indexs(start,stop)
        all_data = self.get_ohlc4(start,stop)
        return all_index,all_data
    
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
    

    def compute(self, candle:OHLCV):
        if len(self.candles) == 0:
            ha_open = candle.open
            ha_close = round((candle.open+candle.high+candle.low+candle.close)/4,self.precision)
            # ha_close = (candle.open+candle.high+candle.low+candle.close)/4
            ha_high = candle.high
            ha_low = candle.low
            
            hl2 = round((ha_high+ha_low)/2,self.precision)
            hlc3 = round((ha_high+ha_low+ha_close)/3,self.precision)
            ohlc4 = round((ha_open+ha_high+ha_low+ha_close)/4,self.precision)
            

        else:
            ha_open = round((self.candles[-1].open+self.candles[-1].close)/2,self.precision)
            ha_close = round((candle.open+candle.high+candle.low+candle.close)/4,self.precision)
            # ha_open = (self.candles[-1].open+self.candles[-1].close)/2
            # ha_close = (candle.open+candle.high+candle.low+candle.close)/4
            ha_high = max(ha_open, ha_close, candle.high)
            ha_low = min(ha_open, ha_close, candle.low)
            
            
            hl2 = round((ha_high+ha_low)/2,self.precision)
            hlc3 = round((ha_high+ha_low+ha_close)/3,self.precision)
            ohlc4 = round((ha_open+ha_high+ha_low+ha_close)/4,self.precision)
        
        ha_candle = OHLCV(ha_open,ha_high,ha_low,ha_close,hl2,hlc3,ohlc4,candle.volume,candle.time,candle.index)
        
        self.map_index_ohlcv[ha_candle.index] = ha_candle
        self.map_time_ohlcv[ha_candle.time] = ha_candle
            
        self.candles.append(ha_candle)

    def reset(self):
        self.candles = []
    
    
    def fisrt_gen_data(self,_precision):
        self.precision = _precision
        self.is_current_update = False
        self.first_gen = False
        self.candles = []
        self.map_index_ohlcv: Dict[int, OHLCV] = {}
        self.map_time_ohlcv: Dict[int, OHLCV] = {}
        self.df = pd.DataFrame([])
        [self.compute(candle) for candle in self._candles.candles]
        
        self.df = pd.DataFrame([data.__dict__ for data in self.candles])
        self.first_gen = True
        # self.start_index:int = self.candles[0].index
        # self.stop_index:int = self.candles[-1].index
        #self.is_current_update = True
        self.sig_reset_all.emit()
        return self.candles
    
    def load_historic_data(self,n):
        self.first_gen = False
        # self.df = pd.DataFrame([])
        update_candles = self._candles.candles[:n+3]
        
        new_candle:List[OHLCV] = []
        
        [self.update_historic(new_candle,update_candles[i],i) for i in range(len(update_candles))]
        
        if new_candle != []:
            df = pd.DataFrame([data.__dict__ for data in new_candle])
            self.df = pd.concat([df, self.df], ignore_index=True)

        self.first_gen = True
        self.sig_add_historic.emit(n)
        return self.candles
    
    def update_historic(self,new_candle:List[OHLCV], candle:OHLCV,i:int):
        if i == 0:
            ha_open = candle.open
            ha_close = round((candle.open+candle.high+candle.low+candle.close)/4,self.precision)
            # ha_close = (candle.open+candle.high+candle.low+candle.close)/4
            ha_high = candle.high
            ha_low = candle.low
            
            hl2 = round((ha_high+ha_low)/2,self.precision)
            hlc3 = round((ha_high+ha_low+ha_close)/3,self.precision)
            ohlc4 = round((ha_open+ha_high+ha_low+ha_close)/4,self.precision)
            
        else:
            ha_open = round((self.candles[i-1].open+self.candles[i-1].close)/2,self.precision)
            ha_close = round((candle.open+candle.high+candle.low+candle.close)/4,self.precision)
            ha_high = max(ha_open, ha_close, candle.high)
            ha_low = min(ha_open, ha_close, candle.low)
            hl2 = round((ha_high+ha_low)/2,self.precision)
            hlc3 = round((ha_high+ha_low+ha_close)/3,self.precision)
            ohlc4 = round((ha_open+ha_high+ha_low+ha_close)/4,self.precision)
        
        ha_candle = OHLCV(ha_open,ha_high,ha_low,ha_close,hl2,hlc3,ohlc4,candle.volume,candle.time,candle.index)
        
        self.map_index_ohlcv[ha_candle.index] = ha_candle
        self.map_time_ohlcv[ha_candle.time] = ha_candle
        if self.candles[i].time == ha_candle.time:
            self.candles[i] = ha_candle
        else:
            self.candles.insert(i,ha_candle)
            new_candle.insert(i,ha_candle)
            
    def update(self, _candles:List[OHLCV],_is_add_candle):
        self.is_current_update = False
        if self.first_gen:
            new_candle = _candles[-1] #    _candle[-1]
            if len(self.candles) < 2:
                return False
            else:
                _index = new_candle.index
                if _is_add_candle==True:
                    # _index = new_candle.index
                    ha_open = round((self.candles[-1].open+self.candles[-1].close)/2,self.precision)
                    ha_close = round((new_candle.open+new_candle.high+new_candle.low+new_candle.close)/4,self.precision)
                    # ha_open = (self.candles[-1].open+self.candles[-1].close)/2
                    # ha_close = (new_candle.open+new_candle.high+new_candle.low+new_candle.close)/4
                    ha_high = max(ha_open, ha_close, new_candle.high)
                    ha_low = min(ha_open, ha_close, new_candle.low)
                    
                    hl2 = round((ha_high+ha_low)/2,self.precision)
                    hlc3 = round((ha_high+ha_low+ha_close)/3,self.precision)
                    ohlc4 = round((ha_open+ha_high+ha_low+ha_close)/4,self.precision)
                    
                    ha_candle = OHLCV(ha_open,ha_high,ha_low,ha_close,hl2,hlc3,ohlc4,new_candle.volume,new_candle.time,_index)
                    self.candles.append(ha_candle)
                    
                    self.map_index_ohlcv[ha_candle.index] = ha_candle
                    self.map_time_ohlcv[ha_candle.time] = ha_candle
                    
                    new_row = pd.DataFrame([data.__dict__ for data in self.candles[-1:]])
                    # concatenate the existing DataFrame and the new row
                    self.df = pd.concat([self.df, new_row], ignore_index=True)
                    # self.start_index:int = self.candles[0].index
                    # self.stop_index:int = self.candles[-1].index
                    #self.is_current_update = True
                    self.sig_add_candle.emit(self.candles[-2:])
                    #QCoreApplication.processEvents()
                    return True
                elif _is_add_candle==False:
                    ha_open = round((self.candles[-2].open+self.candles[-2].close)/2,self.precision)
                    ha_close =  round((new_candle.open+new_candle.high+new_candle.low+new_candle.close)/4,self.precision)
                    # ha_open = (self.candles[-2].open+self.candles[-2].close)/2
                    # ha_close =  (new_candle.open+new_candle.high+new_candle.low+new_candle.close)/4
                    ha_high = max(ha_open, ha_close, new_candle.high)
                    ha_low = min(ha_open, ha_close, new_candle.low)
                    
                    hl2 = round((ha_high+ha_low)/2,self.precision)
                    hlc3 = round((ha_high+ha_low+ha_close)/3,self.precision)
                    ohlc4 = round((ha_open+ha_high+ha_low+ha_close)/4,self.precision)
                    
                    ha_candle = OHLCV(ha_open,ha_high,ha_low,ha_close,hl2,hlc3,ohlc4,new_candle.volume,new_candle.time,_index)
                    
                    if ha_candle.close != self.candles[-1].close or\
                        ha_candle.high != self.candles[-1].high or\
                        ha_candle.low != self.candles[-1].low or\
                        ha_candle.open != self.candles[-1].open:
                        self.candles[-1] = ha_candle
                        
                        self.map_index_ohlcv[ha_candle.index] = ha_candle
                        self.map_time_ohlcv[ha_candle.time] = ha_candle
                        
                        
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
                        
                        # self.start_index:int = self.candles[0].index
                        # self.stop_index:int = self.candles[-1].index
                        #self.is_current_update = True
                        self.sig_update_candle.emit(self.candles[-2:])
                        #QCoreApplication.processEvents()
                        return False
        #self.is_current_update = True
                    
                    
