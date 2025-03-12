from concurrent.futures import Future
import numpy as np
import pandas as pd
from typing import Dict, List
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.ma_type import  PD_MAType
from atklip.controls.ohlcv import   OHLCV
from .candle import JAPAN_CANDLE
from .heikinashi import HEIKINASHI
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject



class SMOOTH_CANDLE(QObject):
    """
    _candles: JAPAN_CANDLE|HEIKINASHI 
    lastcandle: signal(list)  - the list of 2 last candle of para "_candles: JAPAN_CANDLE|HEIKINASHI"
    mamode: IndicatorType  - IndicatorType.SMA
    ma_leng: int - 20
    """
    sig_update_candle = Signal(list)
    sig_add_candle = Signal(list)
    sig_reset_all = Signal()
    sig_add_historic = Signal(int)
    candles : List[OHLCV] = []
    dict_index_time = {}
    signal_delete = Signal()
    sig_update_source = Signal()
    def __init__(self,chart,_candles,mamode,ma_leng,dict_candle_params:dict={}) -> None:
        super().__init__(parent=None)
        self.chart = chart
        if dict_candle_params !={}:
            self.id_exchange:str = dict_candle_params["id_exchange"]
            self.symbol:str = dict_candle_params["symbol"]
            self.interval:str = dict_candle_params["interval"]
            self.mamode:PD_MAType = dict_candle_params["mamode"]
            self.ma_leng:int= dict_candle_params["ma_leng"]
            self.source:str = dict_candle_params["source"]
            self.precision = dict_candle_params["precision"]
            self.canlde_id = dict_candle_params["canlde_id"]
            self.chart_id = dict_candle_params["chart_id"]
            self.name:str=dict_candle_params.get("name")
        else:
            self.mamode:PD_MAType = mamode
            self.ma_leng:int= ma_leng
            self.precision = self.chart.get_precision()
        self.start_index:int = 0
        self.stop_index:int = 0
        self._candles: JAPAN_CANDLE|HEIKINASHI =_candles
                
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self.n_len:int = 0
        self._source_name = f"{self.ma_leng}_SMOOTH_CANDLE"
        self.worker = ApiThreadPool
        self.df = pd.DataFrame([])
        self.connect_signals()
    @property
    def is_current_update(self)-> bool:
        return self._is_current_update
    @is_current_update.setter
    def is_current_update(self,_is_current_update):
        self._is_current_update = _is_current_update 
    @property
    def precision(self):
        return self.chart.get_precision()
    
    @precision.setter
    def precision(self,precision):
        self._precision = precision
    
    def change_input(self,candles=None,dict_candle_params: dict={}):
        if candles != None:
            self.disconnect_signals()
            self._candles : JAPAN_CANDLE|HEIKINASHI= candles
            self.connect_signals()
        
        if dict_candle_params != {}:
            self.id_exchange:str = dict_candle_params["id_exchange"]
            self.symbol:str = dict_candle_params["symbol"]
            self.interval:str = dict_candle_params["interval"]
            self.mamode:PD_MAType = dict_candle_params["mamode"]
            self.ma_leng:int= dict_candle_params["ma_leng"]
            self.source:str = dict_candle_params["source"]
            self.precision = dict_candle_params["precision"]
            self.canlde_id = dict_candle_params["canlde_id"]
            self.chart_id = dict_candle_params["chart_id"]
            self.name:str=dict_candle_params.get("name")
            source_name = f"{self.chart_id}-{self.canlde_id}-{self.id_exchange}-{self.source}-{self.name}-{self.symbol}-{self.interval}-{self.mamode.name}-{self.ma_leng}".encode("utf-8").decode("utf-8")
            self.source_name = source_name
        
        self.first_gen = False
        self.is_genering = True
        self.fisrt_gen_data()
            

    def set_candle_infor(self,id_exchange,symbol,interval):
        self.id_exchange = id_exchange
        self.symbol = symbol
        self.interval = interval
            
    def get_candle_infor(self):
        return self.id_exchange, self.symbol, self.interval
    
    # def delete(self):
    #     self.deleteLater()

    def connect_signals(self):
        self._candles.sig_update_source.connect(self.sig_update_source)
        self._candles.sig_reset_all.connect(self.fisrt_gen_data)
        self._candles.sig_update_candle.connect(self.update_worker)
        self._candles.sig_add_candle.connect(self.update_worker)
        self._candles.sig_add_historic.connect(self.update_historic_worker)
    
    def disconnect_signals(self):
        try:
            self._candles.sig_update_source.disconnect(self.sig_update_source)
            self._candles.sig_reset_all.disconnect(self.fisrt_gen_data)
            self._candles.sig_update_candle.disconnect(self.update_worker)
            self._candles.sig_add_candle.disconnect(self.update_worker)
            self._candles.sig_add_historic.disconnect(self.update_historic_worker)
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
        if n > len(self.df):
            return self.df
        return self.df.tail(n)
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 
    
    def update_worker(self,candle):
        self.worker.submit(self.update,candle)
    
    def threadpool_asyncworker(self):
        self.worker.submit(self.fisrt_gen_data)
    
    def update_historic_worker(self,n):
        self.worker.submit(self.gen_historic_data,n)

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
        """_summary_

        Returns:
            OHLCV: open: float | None,
                high: float | None,
                low: float | None,
                close: float | None,
                hl2: float | None,
                hlc3: float | None,
                ohlc4: float | None,
                volume: float | None,
                time: int | None,
                index: int | None
        """
        last_df = self.get_last_candle()
        return OHLCV(last_df["open"],last_df["high"],last_df["low"],last_df["close"],last_df["hl2"],last_df["hlc3"],last_df["ohlc4"],last_df["volume"],last_df["time"],last_df["index"])

    #@lru_cache(maxsize=128)
    def get_ma_ohlc_at_index(self,df: pd.DataFrame|None,index):
        if df is None:
            df = self.df
        _open, _high, _low, _close, _hl2, _hlc3, _ohlc4, _volume, _time, _index = df["open"].iloc[index],\
            df["high"].iloc[index],df["low"].iloc[index],df["close"].iloc[index],\
            df["hl2"].iloc[index],df["hlc3"].iloc[index],df["ohlc4"].iloc[index],\
            df["volume"].iloc[index],df["time"].iloc[index],df["index"].iloc[index]
        if _open != None and  _high != None and _low != None and _close != None:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4 = round(_open,self.precision),round(_high,self.precision),round(_low,self.precision),round(_close,self.precision),\
                    round(_hl2,self.precision),round(_hlc3,self.precision),round(_ohlc4,self.precision)
            return _open, _high, _low, _close, _hl2, _hlc3, _ohlc4,_volume, _time,_index
        return None,None,None,None,None,None,None,None,None,None
    
    
    def compute(self,index, i:int):
        _index = index[i]
        ohlc = self.get_ma_ohlc_at_index(None,i)
        if ohlc != []:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4,_volume, _time = ohlc[0],ohlc[1],ohlc[2],ohlc[3],ohlc[4],ohlc[5],ohlc[6],ohlc[7],ohlc[8]
            ha_candle = OHLCV(_open,_high,_low,_close, _hl2, _hlc3, _ohlc4,_volume,_time,_index)
            self.map_index_ohlcv[ha_candle.index] = ha_candle
            self.map_time_ohlcv[ha_candle.time] = ha_candle
            self.candles.append(ha_candle)

    
    def compute_historic(self,df: pd.DataFrame,index:np.array, i:int):
        _index = index[i]
        if _index in list(self.map_index_ohlcv.keys()):
            return
        ohlc = self.get_ma_ohlc_at_index(df,i)
        if ohlc != []:
            _open, _high, _low, _close, _hl2, _hlc3, _ohlc4,_volume, _time = ohlc[0],ohlc[1],ohlc[2],ohlc[3],ohlc[4],ohlc[5],ohlc[6],ohlc[7],ohlc[8]
            ha_candle = OHLCV(_open,_high,_low,_close, _hl2, _hlc3, _ohlc4,_volume,_time,_index)
            self.map_index_ohlcv[ha_candle.index] = ha_candle
            self.map_time_ohlcv[ha_candle.time] = ha_candle
            self.candles.insert(i,ha_candle)
    
    
    def refresh_data(self,mamode,ma_ma_leng,n_smooth_ma_leng):
        self.reset_parameters(mamode,ma_ma_leng,n_smooth_ma_leng)
        self.fisrt_gen_data()
    
    def reset_parameters(self,mamode,ma_ma_leng,n_smooth_ma_leng = None):
        self.mamode = mamode
        self.ma_leng = ma_ma_leng
    
    def callback_gen_historic_data(self, future: Future):
        _df = future.result()
        self.df = pd.concat([_df,self.df], ignore_index=True)
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(self.n_len)
    
    def gen_historic_data(self,n_len):
        self.n_len = n_len
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        process = HeavyProcess(self.pro_gen_data,self.callback_gen_historic_data,df,self.mamode.name,self.ma_leng,self.precision)
        process.start()
    
    @staticmethod
    def pro_gen_data(df:pd.DataFrame,mamode,ma_leng,precision):
        highs = ma(mamode, df["high"],length=ma_leng).dropna().round(precision)
        lows = ma(mamode, df["low"],length=ma_leng).dropna().round(precision)
        closes = ma(mamode, df["close"],length=ma_leng).dropna().round(precision)
        opens = ma(mamode, df["open"],length=ma_leng).dropna().round(precision)
        hl2s = ma(mamode, df["hl2"],length=ma_leng).dropna().round(precision)
        hlc3s = ma(mamode, df["hlc3"],length=ma_leng).dropna().round(precision)
        ohlc4s = ma(mamode, df["ohlc4"],length=ma_leng).dropna().round(precision)
        _len = len(ohlc4s)
        
        return pd.DataFrame({  "open": opens,
                                    "high": highs,
                                    "low": lows,
                                    "close": closes,
                                    "hl2": hl2s,
                                    "hlc3": hlc3s,
                                    "ohlc4": ohlc4s,
                                    "volume": df["volume"].tail(_len),
                                    "time": df["time"].tail(_len),
                                    "index": df["index"].tail(_len)
                                })  
        
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        # self.start_index:int = self.df["index"].iloc[0]
        # self.stop_index:int = self.df["index"].iloc[-1]
        #self.is_current_update = True
        self.sig_reset_all.emit()
    
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        self.candles:List[OHLCV] = []
        self.map_index_ohlcv: Dict[int, OHLCV] = {}
        self.map_time_ohlcv: Dict[int, OHLCV] = {}
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.pro_gen_data,self.callback_first_gen,df,self.mamode.name,self.ma_leng,self.precision)
        process.start()

    
    def callback_update_ma_ohlc(self,future: Future):
        update_df = future.result()
        
        if self._is_update:
            self.df.iloc[-1] = update_df.iloc[-1]
        else:            
            self.df = pd.concat([self.df,update_df.iloc[[-1]]],ignore_index=True)
        
        _open, _high, _low, _close, hl2, hlc3, ohlc4,_volume, _time,_index = self.get_ma_ohlc_at_index(None,-1)
        ha_candle = OHLCV(_open,_high,_low,_close,hl2,hlc3,ohlc4,_volume,_time,_index)
        if self._is_update:
            # self.start_index:int = self.df["index"].iloc[0]
            # self.stop_index:int = self.df["index"].iloc[-1]
            #self.is_current_update = True
            self.sig_update_candle.emit([ha_candle])
            return False
        else:
            # self.start_index:int = self.df["index"].iloc[0]
            # self.stop_index:int = self.df["index"].iloc[-1]
            #self.is_current_update = True
            self.sig_add_candle.emit([ha_candle])
            return True
        
    def update(self, _candle:List[OHLCV]):
        # print(_candle)
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            new_candle = _candle[-1]

            _new_time = new_candle.time
            _last_time = self.df["time"].iloc[-1]
            self._is_update = False
            if _new_time == _last_time:
                self._is_update =  True
                
            df:pd.DataFrame = self._candles.get_df(self.ma_leng*5)
            
            process = HeavyProcess(self.pro_gen_data,self.callback_update_ma_ohlc,df,self.mamode.name,self.ma_leng,self.precision)
            process.start()
        else:
            pass
            #self.is_current_update = True
            return False


