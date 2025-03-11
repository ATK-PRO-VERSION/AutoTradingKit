import numpy as np
import pandas as pd
from atklip.controls import atr,bbands,kc,donchian
from atklip.app_utils.helpers import crossover

def utsignal(data,a,c):
    # ATR Calculation
    src = data["close"]
    high = data["high"]
    low = data["low"]
    
    xATR = atr(high, low, src, length=c)
    nLoss = a * xATR
    
    # ATR Trailing Stop
    xATRTrailingStop = np.zeros(len(data))
    for i in range(1, len(data)):
        if src[i] > xATRTrailingStop[i - 1] and src[i - 1] > xATRTrailingStop[i - 1]:
            xATRTrailingStop[i] = max(xATRTrailingStop[i - 1], src[i] - nLoss[i])
        elif src[i] < xATRTrailingStop[i - 1] and src[i - 1] < xATRTrailingStop[i - 1]:
            xATRTrailingStop[i] = min(xATRTrailingStop[i - 1], src[i] + nLoss[i])
        else:
            xATRTrailingStop[i] = src[i] - nLoss[i] if src[i] > xATRTrailingStop[i - 1] else src[i] + nLoss[i]
    # EMA for crossover logic
    above_ema = ema(high, length=1)
    below_ema = ema(low, length=1)
    # above_ema = ema(src, length=1)
    # below_ema = ema(src, length=1)
    above = crossover(below_ema, xATRTrailingStop)
    below = crossover(xATRTrailingStop, above_ema)
    return src, xATRTrailingStop, above, below

# Bands Calculation
def calculate_bands(data, band_type, length, std_dev):
    if band_type == "Bollinger Bands":
        bb = bbands(data["close"], length=length, std=std_dev)
        _props = f"_{length}_{std_dev}"
        lower_name = f"BBL{_props}"
        mid_name = f"BBM{_props}"
        upper_name = f"BBU{_props}"
        return bb[lower_name], bb[mid_name], bb[upper_name]
    elif band_type == "Keltner Channel":
        _kc = kc(data["high"],data["low"],data["close"], length=length)
        _props = f"_{length}_2"
        lower_name = f"KCL{_props}"
        basis_name = f"KCB{_props}"
        upper_name = f"KCU{_props}"
        return _kc[lower_name], _kc[basis_name], _kc[upper_name]
    elif band_type == "Donchian Channel":
        lower_length = length
        upper_length = length
        dc = donchian(data["high"],data["low"],lower_length,upper_length)
        lower_name = f"DCL_{lower_length}_{upper_length}"
        mid_name = f"DCM_{lower_length}_{upper_length}"
        upper_name = f"DCU_{lower_length}_{upper_length}"
        return dc[lower_name], dc[mid_name], dc[upper_name]
    else:
        return None, None, None

# Trailing Stop Calculation
def calculate_trailing_stop(data:pd.DataFrame, lower:pd.Series, upper:pd.Series, atr_length:int, mult: float, wicks: bool):
    if lower is None or upper is None:
        raise ValueError("Invalid band type or parameters resulting in None values for bands.")
    
    _atr = atr(data["high"], data["low"], data["close"], length=atr_length)
    
    _dir = np.ones(len(data))
    dir = pd.Series(_dir)
    
    if wicks:
        longtarget = data["low"]
        shorttarget = data["high"]
    else:
        shorttarget = data["close"]
        longtarget = data["close"]
    long_stop = lower - _atr * mult
    short_stop = upper + _atr * mult
    
    short_stop_pre = short_stop.shift(1)
    long_stop_pre = long_stop.shift(1)
    
    for i in range(1, len(data)):
        if dir.iloc[i - 1] == 1 and longtarget[i] <= long_stop_pre[i]:
            dir.iloc[i] = -1
        elif dir.iloc[i - 1] == -1 and shorttarget[i] >= short_stop_pre[i]:
            dir.iloc[i] = 1
        else:
            dir.iloc[i] = dir.iloc[i - 1]
    return dir, long_stop, short_stop

def utbot_with_bb(data,key_value = 1,atr_utbot_length=10, mult = 1, wicks=False,band_type = "Bollinger Bands",atr_length=22, channel_length = 20, StdDev = 1):
    """_summary_
    Args:
        data (_type_): _description_
        a (int, optional): Key Value, this changes sensitivity. Defaults to 1.
        c (int, optional): ATR Period. Defaults to 10.
        mult (int, optional): ATR Multiplier. Defaults to 1.
        wicks (bool, optional): _description_. Defaults to False.
        band_type (str, optional): Channel Type. Defaults to "Bollinger Bands".
        channel_length (int, optional): _description_. Defaults to 20.
        StdDev (int, optional): _description_. Defaults to 1.
    Returns:
        _type_: _description_
    """
    data = data.copy()
    data = data.reset_index(drop=True)
    src, xATRTrailingStop, above, below = utsignal(data,key_value,atr_utbot_length)
    # print("src--------------")
    # print(src)
    lower_band, middle_band, upper_band = calculate_bands(data, band_type, channel_length, StdDev)
    # print("lower_band--------------")
    # print(lower_band)
    barState, buyStop, sellStop = calculate_trailing_stop(data, lower_band, upper_band, atr_length, mult, wicks)
    # print("barState--------------")
    # print(barState)
    # Trade Conditions
    buy_condition = (src > xATRTrailingStop) & above & (barState == 1)
    sell_condition = (src < xATRTrailingStop) & below & (barState == -1)
    # Output Results
    data["BuySignal"] = buy_condition
    data["SellSignal"] = sell_condition
    
    return data[["BuySignal", "SellSignal"]]

import numpy as np
import pandas as pd

from atklip.controls import atr
from atklip.controls.ma_overload import ema, ma

import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject


class UTBOT_ALERT_WITH_BB(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int) 
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.atr_length:int=dict_ta_params.get("atr_length",22)
        self.channel_length:int=dict_ta_params.get("channel_length",20)
        self.key_value:float=dict_ta_params.get("key_value",1)
        self.atr_utbot_length:int=dict_ta_params.get("atr_utbot_length",10)
        self.mult:float=dict_ta_params.get("mult",1)
        self.wicks:bool=dict_ta_params.get("wicks",True)
        self.band_type:str=dict_ta_params.get("band_type","Bollinger Bands")
 
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"ATKPRO Ver_1.0"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.long,self.short= np.array([]),np.array([]),np.array([])

        self.connect_signals()

    
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
            self.atr_length:int=dict_ta_params.get("atr_length",22)
            self.channel_length:int=dict_ta_params.get("channel_length",20)
            self.key_value:float=dict_ta_params.get("key_value",1)
            self.atr_utbot_length:int=dict_ta_params.get("atr_utbot_length",10)
            self.mult:float=dict_ta_params.get("mult",1)
            self.wicks:bool=dict_ta_params.get("wicks",True)
            self.band_type:str=dict_ta_params.get("band_type","Bollinger Bands")
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name} {self.atr_length} {self.channel_length}"

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
            return [],[]
        if start == 0 and stop == 0:
            x_data = self.xdata
            _long =self.long
            _short =self.short
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            _long =self.long[:stop]
            _short =self.short[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            _long =self.long[start:]
            _short =self.short[start:]
        else:
            x_data = self.xdata[start:stop]
            _long =self.long[start:stop]
            _short =self.short[start:stop]
        return np.array(x_data),np.array(_long),np.array(_short)
    
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
        _long,_short = INDICATOR["BuySignal"],INDICATOR["SellSignal"]
        return _long,_short
    
    def calculate(self,df: pd.DataFrame):
        INDICATOR = utbot_with_bb(data=df,
                                    key_value = self.key_value,
                                    atr_utbot_length = self.atr_utbot_length,
                                    mult = self.mult,
                                    wicks = self.wicks,
                                    band_type = self.band_type,
                                    atr_length=self.atr_length,
                                    channel_length=self.channel_length)
        _long,_short = self.paire_data(INDICATOR)
        return _long,_short
    
    
    def fisrt_gen_data(self):
                
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        
        self.xdata,self.long,self.short = np.array([]),np.array([]),np.array([])
        
        _long,_short = self.calculate(df)
        
        
        _index = df["index"]
        

        _df = pd.DataFrame({
                            'index':_index,
                            "long":_long,
                            "short":_short
                            })
        
        
        self.df = _df.iloc[self.atr_length+self.channel_length+self.atr_utbot_length:]
        
        self.xdata,self.long,self.short = self.df["index"],self.df["long"],self.df["short"]
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        
        #self.is_current_update = True
        self.sig_reset_all.emit()
          
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        _len = len(df)
        
        _long,_short = self.calculate(df)
                                
        _index = df["index"]
        
        _df = pd.DataFrame({
                            'index':_index,
                            "long":_long,
                            "short":_short
                            })
        
        _df = _df.iloc[self.atr_length+self.channel_length+self.atr_utbot_length:]
        
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        self.xdata,self.long,self.short = self.df["index"].to_numpy(),self.df["long"].to_numpy(),self.df["short"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            self.is_current_update = False
            df:pd.DataFrame = self._candles.df.iloc[-int(self.atr_length+self.channel_length+self.atr_utbot_length+10):]
            
            # print(df)
            _long,_short = self.calculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "long":[_long.iloc[-1]],
                                    "short":[_short.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata = np.concatenate((self.xdata,np.array([new_candle.index])))
            self.long = np.concatenate((self.long,np.array([_long.iloc[-1]])))
            self.short = np.concatenate((self.short,np.array([_short.iloc[-1]])))
            
            self.sig_add_candle.emit()
            
        #self.is_current_update = True
            
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        
        if (self.first_gen == True) and (self.is_genering == False):
            self.is_current_update = False
            df:pd.DataFrame = self._candles.df.iloc[-int(self.atr_length+self.channel_length+self.atr_utbot_length+10):]
            _long,_short = self.calculate(df)
            
            self.df.iloc[-1] = [new_candle.index,_long.iloc[-1],_short.iloc[-1]]
            
            self.xdata[-1],self.long[-1],self.short[-1] = new_candle.index,_long.iloc[-1],_short.iloc[-1]
            
            self.sig_update_candle.emit()
        #self.is_current_update = True
            

    