# -*- coding: utf-8 -*-
from numpy import floor, isnan, nan, zeros, zeros_like
from numba import njit
from pandas import Series, DataFrame
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.utils import (
    v_bool,
    v_offset,
    v_pos_default,
    v_series,
)

from atklip.app_utils import percent_caculator
from functools import lru_cache

@njit(cache=True)
def nb_rolling_hl(np_high, np_low, window_size):
    m = np_high.size
    idx = zeros(m)
    swing = zeros(m)  # where a high = 1 and low = -1
    value = zeros(m)

    extremums = 0
    left = int(floor(window_size / 2))
    right = left + 1
    # sample_array = [*[left-window], *[center], *[right-window]]
    for i in range(left, m - right):
        low_center = np_low[i]
        high_center = np_high[i]
        low_window = np_low[i - left: i + right]
        high_window = np_high[i - left: i + right]

        if (low_center <= low_window).all():
            idx[extremums] = i
            swing[extremums] = -1
            value[extremums] = low_center
            extremums += 1

        if (high_center >= high_window).all():
            idx[extremums] = i
            swing[extremums] = 1
            value[extremums] = high_center
            extremums += 1

    return idx[:extremums], swing[:extremums], value[:extremums]


@njit(cache=True)
def nb_find_zigzags(idx, swing, value, deviation):
    zz_idx = zeros_like(idx)
    zz_swing = zeros_like(swing)
    zz_value = zeros_like(value)
    zz_dev = zeros_like(idx)

    zigzags = 0
    zz_idx[zigzags] = idx[-1]
    zz_swing[zigzags] = swing[-1]
    zz_value[zigzags] = value[-1]
    zz_dev[zigzags] = 0

    m = idx.size
    for i in range(m - 2, -1, -1):
        # last point in zigzag is bottom
        if zz_swing[zigzags] == -1:
            if swing[i] == -1:
                if zz_value[zigzags] > value[i] and zigzags > 1:
                    current_dev = (zz_value[zigzags - 1] - value[i]) / value[i]
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev
            else:
                current_dev = (value[i] - zz_value[zigzags]) / value[i]
                if current_dev > 0.01 * deviation:
                    if zz_idx[zigzags] == idx[i]:
                        continue
                    zigzags += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev

        # last point in zigzag is peak
        else:
            if swing[i] == 1:
                if zz_value[zigzags] < value[i] and zigzags > 1:
                    current_dev = (value[i] - zz_value[zigzags - 1]) / value[i]
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev
            else:
                current_dev = (zz_value[zigzags] - value[i]) / value[i]
                if current_dev > 0.01 * deviation:
                    if zz_idx[zigzags] == idx[i]:
                        continue
                    zigzags += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev

    _n = zigzags + 1
    return zz_idx[:_n], zz_swing[:_n], zz_value[:_n], zz_dev[:_n]


@njit(cache=True)
def nb_map_zigzag(idx, swing, value, deviation, n):
    swing_map = zeros(n)
    value_map = zeros(n)
    dev_map = zeros(n)

    for j, i in enumerate(idx):
        i = int(i)
        swing_map[i] = swing[j]
        value_map[i] = value[j]
        dev_map[i] = deviation[j]

    for i in range(n):
        if swing_map[i] == 0:
            swing_map[i] = nan
            value_map[i] = nan
            dev_map[i] = nan

    return swing_map, value_map, dev_map



def zigzag(
    high: Series, low: Series, close: Series = None,
    legs: int = None, deviation: IntFloat = None,
    retrace: bool = None, last_extreme: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """ Zigzag (ZIGZAG)

    Zigzag attempts to filter out smaller price movments while highlighting
    trend direction. It does not predict future trends, but it does identify
    swing highs and lows. When 'deviation' is set to 10, it will ignore
    all price movements less than 10%; only price movements greater than 10%
    would be shown.

    Note: Zigzag lines are not permanent and a price reversal will create a
        new line.

    Sources:
        https://www.tradingview.com/support/solutions/43000591664-zig-zag/#:~:text=Definition,trader%20visual%20the%20price%20action.
        https://school.stockcharts.com/doku.php?id=technical_indicators:zigzag

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's. Default: None
        legs (int): Number of legs > 2. Default: 10
        deviation (float): Price Deviation Percentage for a reversal.
            Default: 5
        retrace (bool): Default: False
        last_extreme (bool): Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
        fill_method (value, optional): Type of fill method

    Returns:
        pd.DataFrame: swing, and swing_type (high or low).
    """
    # Validate
    legs = v_pos_default(legs, 10)
    _length = legs + 1
    high = v_series(high, _length)
    low = v_series(low, _length)

    if high is None or low is None:
        return

    if close is not None:
        close = v_series(close,_length)
        np_close = close.values
        if close is None:
            return

    deviation = v_pos_default(deviation, 5.0)
    retrace = v_bool(retrace, False)
    last_extreme = v_bool(last_extreme, True)
    offset = v_offset(offset)

    # Calculation
    np_high, np_low = high.to_numpy(), low.to_numpy()
    hli, hls, hlv = nb_rolling_hl(np_high, np_low, legs)
    zzi, zzs, zzv, zzd = nb_find_zigzags(hli, hls, hlv, deviation)
    zz_swing, zz_value, zz_dev = nb_map_zigzag(zzi, zzs, zzv, zzd, np_high.size)

    # Offset
    if offset != 0:
        zz_swing = zz_swing.shift(offset)
        zz_value = zz_value.shift(offset)
        zz_dev = zz_dev.shift(offset)

    # Fill
    if "fillna" in kwargs:
        zz_swing.fillna(kwargs["fillna"], inplace=True)
        zz_value.fillna(kwargs["fillna"], inplace=True)
        zz_dev.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        zz_swing.fillna(method=kwargs["fill_method"], inplace=True)
        zz_value.fillna(method=kwargs["fill_method"], inplace=True)
        zz_dev.fillna(method=kwargs["fill_method"], inplace=True)

    _props = f"_{deviation}%_{legs}"
    data = {
        f"ZIGZAGs{_props}": zz_swing,
        f"ZIGZAGv{_props}": zz_value,
        f"ZIGZAGd{_props}": zz_dev,
    }
    df = DataFrame(data, index=high.index)
    df.name = f"ZIGZAG{_props}"
    df.category = "trend"

    return df

import numpy as np
import pandas as pd
from typing import List
from PySide6.QtCore import Qt, Signal,QObject

from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import CandleWorker



class OLD_ZIGZAG(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal() 
    def __init__(self,parent,_candles,legs,deviation,retrace=False,last_extreme=False) -> None:
        super().__init__(parent=parent)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles

        self.legs :Int = legs
        self.deviation: IntFloat = deviation
        self.retrace: bool = retrace
        self.last_extreme: bool = last_extreme
        
        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        
        self.name = f"ZIGZAG {self.legs} {self.deviation}"

        self.df = pd.DataFrame([])
        
        self.xdata,self.zz_swing, self.zz_value, self.zz_dev  = np.array([]),np.array([]),np.array([]),np.array([])

        self.connect_signals()
        
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
        self._candles.sig_reset_all.connect(self.started_worker,Qt.ConnectionType.AutoConnection)
        self._candles.sig_update_candle.connect(self.update_worker,Qt.ConnectionType.QueuedConnection)
        self._candles.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.QueuedConnection)
        self._candles.signal_delete.connect(self.signal_delete)
        self._candles.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.QueuedConnection)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
    
    def change_inputs(self,_input:str,_source:str|int|JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE|PD_MAType):
        is_update = False
        print(_input,_source)
        
        if _input == "source":
            self.change_source(_source)
            return
        elif _input == "deviation":
            self.deviation = _source
            is_update = True
        elif _input == "legs":
            self.legs = _source
            is_update = True
        elif _input == "retrace":
            self.retrace = _source
            is_update = True
        elif _input == "last_extreme":
            self.last_extreme = _source
            is_update = True
        if is_update:
            self.started_worker()
    
    @property
    def indicator_name(self):
        return self.name
    @indicator_name.setter
    def indicator_name(self,_name):
        self.name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_data(self):
        return self.xdata,self.zz_swing, self.zz_value, self.zz_dev
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 

    def update_worker(self,candle):
        self.worker_ = None
        self.worker_ = CandleWorker(self.update,candle)
        self.worker_.start()
    
    def add_worker(self,candle):
        self.worker_ = None
        self.worker_ = CandleWorker(self.add,candle)
        self.worker_.start()
    
    def add_historic_worker(self,n):
        self.worker_ = None
        self.worker_ = CandleWorker(self.add_historic,n)
        self.worker_.start()
    
    def started_worker(self):
        self.worker = None
        self.worker = CandleWorker(self.fisrt_gen_data)
        self.worker.start()
    
    def paire_data(self,INDICATOR:pd.DataFrame|pd.Series):
        column_names = INDICATOR.columns.tolist()
        
        zz_swing_name = ''
        zz_value_name = ''
        zz_dev_name = '' 
        
        for name in column_names:
            if name.__contains__("ZIGZAGs"):
                zz_swing_name = name
            elif name.__contains__("ZIGZAGv"):
                zz_value_name = name
            elif name.__contains__("ZIGZAGd"):
                zz_dev_name = name

        zz_swing = INDICATOR[zz_swing_name]#.dropna()
        zz_value = INDICATOR[zz_value_name]#.dropna()
        zz_dev = INDICATOR[zz_dev_name]#.dropna()
        zz_index = INDICATOR["index"]#.dropna()
        return zz_index,zz_swing,zz_value,zz_dev
    
    def caculate(self,df: pd.DataFrame,_index: pd.Series):
        
        INDICATOR = zigzag(high=df["high"],
                            low=df["low"],
                            close=df["close"],
                            legs = self.legs,
                            deviation = self.deviation,
                            retrace = self.retrace,
                            last_extreme = self.last_extreme
                            )#.dropna()
        INDICATOR["index"] = _index
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        
        _index = df["index"]
        zz_index,zz_swing,zz_value,zz_dev = self.caculate(df,_index)

        self.df = pd.DataFrame({
                            'index':zz_index,
                            "zz_swing":zz_swing,
                            "zz_value":zz_value,
                            "zz_dev":zz_dev
                            })
        INDICATOR = self.df[self.df['zz_value'].notna()]
        self.xdata,self.zz_swing, self.zz_value, self.zz_dev = INDICATOR["index"].to_numpy(),\
                                                                INDICATOR["zz_swing"].to_numpy(),\
                                                                INDICATOR["zz_value"].to_numpy(),\
                                                                INDICATOR["zz_dev"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add_historic(self,n:int):
        self.is_genering = True
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df()
        
        
        _index = df["index"]
        zz_index,zz_swing,zz_value,zz_dev = self.caculate(df,_index)
        
        self.df = pd.DataFrame({
                            'index':zz_index,
                            "zz_swing":zz_swing,
                            "zz_value":zz_value,
                            "zz_dev":zz_dev
                            })
        INDICATOR = self.df[self.df['zz_value'].notna()]
        self.xdata,self.zz_swing, self.zz_value, self.zz_dev = INDICATOR["index"].to_numpy(),\
                                                                INDICATOR["zz_swing"].to_numpy(),\
                                                                INDICATOR["zz_value"].to_numpy(),\
                                                                INDICATOR["zz_dev"].to_numpy()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        
        self.sig_add_historic.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df()
            
            _index = df["index"]
            zz_index,zz_swing,zz_value,zz_dev = self.caculate(df,_index)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "zz_swing":[zz_swing.iloc[-1]],
                                    "zz_value":[zz_value.iloc[-1]],
                                    "zz_dev":[zz_dev.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            INDICATOR = self.df[self.df['zz_value'].notna()]
            self.xdata,self.zz_swing, self.zz_value, self.zz_dev = INDICATOR["index"].to_numpy(),\
                                                                INDICATOR["zz_swing"].to_numpy(),\
                                                                INDICATOR["zz_value"].to_numpy(),\
                                                                INDICATOR["zz_dev"].to_numpy()
            
            self.sig_add_candle.emit()
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df()
            _index = df["index"]
            zz_index,zz_swing,zz_value,zz_dev = self.caculate(df,_index)
            
            self.df.iloc[-1] = [new_candle.index,zz_swing.iloc[-1],zz_value.iloc[-1],zz_dev.iloc[-1]]
            
            INDICATOR = self.df[self.df['zz_value'].notna()]
            self.xdata,self.zz_swing, self.zz_value, self.zz_dev = INDICATOR["index"].to_numpy(),\
                                                                INDICATOR["zz_swing"].to_numpy(),\
                                                                INDICATOR["zz_value"].to_numpy(),\
                                                                INDICATOR["zz_dev"].to_numpy()
            self.sig_update_candle.emit()



def caculate_zz(list_zizgzag:list,ohlcv:OHLCV,percent: float):
    if percent_caculator(list_zizgzag[0][1],list_zizgzag[1][1]) < percent:
        if list_zizgzag[0][2] == 'low':
            if list_zizgzag[0][1] > ohlcv.low:
                list_zizgzag.pop(0)
                list_zizgzag.append([ohlcv.index,ohlcv.low,'low'])
            elif list_zizgzag[1][1] < ohlcv.high:
                list_zizgzag[-1]=[ohlcv.index,ohlcv.high,'high']
        elif list_zizgzag[0][2] == 'high':
            if list_zizgzag[0][1] < ohlcv.high:
                list_zizgzag.pop(0)
                list_zizgzag.append([ohlcv.index,ohlcv.high,'high'])
            elif list_zizgzag[1][1] > ohlcv.low:
                list_zizgzag[-1]=[ohlcv.index,ohlcv.low,'low']
    else:
        if list_zizgzag[-1][2] == 'low':
            if percent_caculator(list_zizgzag[-1][1],ohlcv.high) > percent:
                list_zizgzag.append([ohlcv.index,ohlcv.high,'high'])
            elif list_zizgzag[-1][1] > ohlcv.low:
                if list_zizgzag[-1][0] == ohlcv.index:
                    list_zizgzag[-1]=[ohlcv.index,ohlcv.low,'low']
                else:
                    list_zizgzag.append([ohlcv.index,ohlcv.low,'low'])
        elif list_zizgzag[-1][2] == 'high':
            if percent_caculator(list_zizgzag[-1][1],ohlcv.low) > percent:
                list_zizgzag.append([ohlcv.index,ohlcv.low,'low'])
            elif list_zizgzag[-1][1] < ohlcv.high:
                if list_zizgzag[-1][0] == ohlcv.index:
                    list_zizgzag[-1]=[ohlcv.index,ohlcv.high,'high']
                else:
                    list_zizgzag.append([ohlcv.index,ohlcv.high,'high'])
    return list_zizgzag


def update_zz(list_zizgzag:list,ohlcv:OHLCV,percent: float):
    if list_zizgzag[-1][2] == 'low':
        if percent_caculator(list_zizgzag[-1][1],ohlcv.high) > percent:
            list_zizgzag.append([ohlcv.index,ohlcv.high,'high'])
        elif list_zizgzag[-1][1] > ohlcv.low:
            list_zizgzag[-1]=[ohlcv.index,ohlcv.low,'low']
    elif list_zizgzag[-1][2] == 'high':
        if percent_caculator(list_zizgzag[-1][1],ohlcv.low) > percent:
            list_zizgzag.append([ohlcv.index,ohlcv.low,'low'])
        elif list_zizgzag[-1][1] < ohlcv.high:
            list_zizgzag[-1]=[ohlcv.index,ohlcv.high,'high']
    return list_zizgzag


def load_zz(list_zizgzag:list,candles: List[OHLCV],percent: float):
    last_point = list_zizgzag[0]
    last_time = last_point[0]

    _new_zz = [[candles[0].index,candles[0].low,'low'],[candles[0].index,candles[0].high,'high']]
    
    for i in range(len(candles)):
        if candles[i].index > last_time:
            _new_zz.pop(0)
            if _new_zz[-1][0] == last_time:
                _new_zz.pop(-1)
            list_zizgzag = _new_zz + list_zizgzag
            return list_zizgzag

        _new_zz = caculate_zz(_new_zz,candles[i],percent)
    
    _new_zz.pop(0)
    if _new_zz[-1][0] == last_time:
        _new_zz.pop(-1)
    list_zizgzag = _new_zz + list_zizgzag
    return list_zizgzag


def my_zigzag(list_zizgzag:list=[],candles: List[OHLCV]=None,percent: float=0.5):
    if list_zizgzag == []:
        list_zizgzag = [[candles[0].index,candles[0].low,'low'],[candles[0].index,candles[0].high,'high']]
    for i in range(len(candles)):
        list_zizgzag = caculate_zz(list_zizgzag,candles[i],percent)
    
    list_zizgzag.pop(0)
    return list_zizgzag


class ZIGZAG(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal() 
    def __init__(self,parent=None,_candles=None,dict_ta_params: dict={}) -> None:
        super().__init__(parent=parent)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles

        self._dict_ta_params = dict_ta_params
        
        self.legs :Int = self.dict_ta_params.get("legs") 
        self.deviation: IntFloat = self.dict_ta_params.get("deviation")
        self.retrace: bool = self.dict_ta_params.get("retrace",False) 
        self.last_extreme: bool = self.dict_ta_params.get("last_extreme",False) 
        
        # self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.list_zizgzag:list = []
        
        self.indicator_name = f"ZIGZAG {self.legs} {self.deviation}"
        
        self.df = pd.DataFrame([])
        
        self.x_data,self.y_data  = [],[]

        self.connect_signals()
    
    @property
    def dict_ta_params(self)-> dict:
        return self._dict_ta_params
    @dict_ta_params.setter
    def dict_ta_params(self,dict_ta_params):
        self._dict_ta_params = dict_ta_params
    
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
        self._candles.sig_reset_all.connect(self.started_worker,Qt.ConnectionType.AutoConnection)
        self._candles.sig_update_candle.connect(self.update_worker,Qt.ConnectionType.QueuedConnection)
        self._candles.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.QueuedConnection)
        self._candles.signal_delete.connect(self.signal_delete)
        self._candles.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.QueuedConnection)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
    
    def change_inputs(self,_input:str,_source:str|int|JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE|PD_MAType):
        is_update = False
        print(_input,_source)
        
        if _input == "source":
            self.change_source(_source)
            return
        elif _input == "deviation":
            self.deviation = _source
            is_update = True
        elif _input == "legs":
            self.legs = _source
            is_update = True
        elif _input == "retrace":
            self.retrace = _source
            is_update = True
        elif _input == "last_extreme":
            self.last_extreme = _source
            is_update = True
        if is_update:
            self.started_worker()
    
    @property
    def indicator_name(self):
        return self.name
    @indicator_name.setter
    def indicator_name(self,_name):
        self.name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_data(self,start:int,stop:int):
        if start == 0 and stop == 0:
            x_data = self.x_data
            y_data = self.y_data
        elif start == 0 and stop != 0:
            x_data = self.x_data[:stop]
            y_data = self.y_data[:stop]
        elif start != 0 and stop == 0:
            x_data = self.x_data[start:]
            y_data = self.y_data[start:]
        else:
            x_data = self.x_data[start:stop]
            y_data = self.y_data[start:stop]
        return {"x_data":x_data,"y_data":y_data} 
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 

    def update_worker(self,candle):
        self.worker_ = None
        self.worker_ = CandleWorker(self.update,candle)
        self.worker_.start()
    
    def add_worker(self,candle):
        self.worker_ = None
        self.worker_ = CandleWorker(self.add,candle)
        self.worker_.start()
    
    def add_historic_worker(self,n):
        self.worker_ = None
        self.worker_ = CandleWorker(self.add_historic,n)
        self.worker_.start()
    
    def started_worker(self):
        self.worker = None
        self.worker = CandleWorker(self.fisrt_gen_data)
        self.worker.start()
    
    def paire_data(self,list_zizgzag:list):
        if len(list_zizgzag) == 2:
            if percent_caculator(list_zizgzag[0][1],list_zizgzag[1][1]) >= self.deviation:
                x_data = [x[0] for x in list_zizgzag]
                y_data = [x[1] for x in list_zizgzag]   
            else:
                x_data,y_data = [],[]
        else:
            x_data = [x[0] for x in list_zizgzag]
            y_data = [x[1] for x in list_zizgzag]  
        return x_data,y_data
    
    def caculate(self,list_zizgzag, candles: List[OHLCV],process:str=""):
        
        if process == "add" or process == "update":
            self.list_zizgzag = update_zz(list_zizgzag=list_zizgzag,
                                ohlcv=candles[-1],
                                percent= self.deviation
                                )
        elif process == "load":
            self.list_zizgzag = load_zz(list_zizgzag=list_zizgzag,
                                candles=candles,
                                percent= self.deviation
                                )
        else:
            self.list_zizgzag = my_zigzag(list_zizgzag=list_zizgzag,
                                candles=candles,
                                percent= self.deviation
                                )

        return self.paire_data(self.list_zizgzag)
    
    def fisrt_gen_data(self):
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        self.x_data,self.y_data = self.caculate([],self._candles.candles)

        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.x_data,self.y_data = self.caculate(self.list_zizgzag,self._candles.candles,"load")
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_add_historic.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            self.x_data,self.y_data = self.caculate(self.list_zizgzag,self._candles.candles,"add")
            self.sig_add_candle.emit()
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            self.x_data,self.y_data = self.caculate(self.list_zizgzag,self._candles.candles,"update")
            self.sig_update_candle.emit()

