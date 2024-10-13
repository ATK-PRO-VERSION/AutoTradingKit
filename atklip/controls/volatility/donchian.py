# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int
from atklip.controls.pandas_ta.utils import v_offset, v_pos_default, v_series



def donchian(
    high: Series, low: Series,
    lower_length: Int = None, upper_length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Donchian Channels (DC)

    Donchian Channels are used to measure volatility, similar to
    Bollinger Bands and Keltner Channels.

    Sources:
        https://www.tradingview.com/wiki/Donchian_Channels_(DC)

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        lower_length (int): The short period. Default: 20
        upper_length (int): The short period. Default: 20
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: lower, mid, upper columns.
    """
    # Validate
    lower_length = v_pos_default(lower_length, 20)
    upper_length = v_pos_default(upper_length, 20)
    lmin_periods = int(kwargs.pop("lmin_periods", lower_length))
    umin_periods = int(kwargs.pop("umin_periods", upper_length))

    _length = max(lower_length, lmin_periods, upper_length, umin_periods)
    high = v_series(high, _length)
    low = v_series(low, _length)

    if high is None or low is None:
        return

    offset = v_offset(offset)

    # Calculate
    lower = low.rolling(lower_length, min_periods=lmin_periods).min()
    upper = high.rolling(upper_length, min_periods=umin_periods).max()
    mid = 0.5 * (lower + upper)

    # Fill
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        mid.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        mid = mid.shift(offset)
        upper = upper.shift(offset)

    # Name and Category
    lower.name = f"DCL_{lower_length}_{upper_length}"
    mid.name = f"DCM_{lower_length}_{upper_length}"
    upper.name = f"DCU_{lower_length}_{upper_length}"
    mid.category = upper.category = lower.category = "volatility"

    data = {lower.name: lower, mid.name: mid, upper.name: upper}
    df = DataFrame(data, index=high.index)
    df.name = f"DC_{lower_length}_{upper_length}"
    df.category = mid.category

    return df

import numpy as np
import pandas as pd
from typing import List

from psygnal import Signal
from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.app_api.workers import ApiThreadPool

class DONCHIAN():
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal()    
    def __init__(self,_candles,dict_ta_params) -> None:
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
                
        self.lower_length:int = dict_ta_params["lower_length"]
        self.upper_length:int = dict_ta_params["upper_length"]
        self.offset :int=dict_ta_params.get("offset",0)
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self.name = f"DC {self.lower_length} {self.upper_length}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.lb,self.cb,self.ub = [],[],[],[]

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
            self.lower_length:int = dict_ta_params["lower_length"]
            self.upper_length:int = dict_ta_params["upper_length"]
            self.offset :int=dict_ta_params.get("offset",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.lower_length}-{self.upper_length}"

            self.indicator_name = ta_param
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        
        self.started_worker()
             
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
    def indicator_name(self):
        return self.name
    @indicator_name.setter
    def indicator_name(self,_name):
        self.name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_data(self,start:int=0,stop:int=0):
        if self.xdata == []:
            return {"x_data":[],"lb":[],"cb":[],"ub":[]}
        if start == 0 and stop == 0:
            x_data = self.xdata
            lb,cb,ub=self.lb,self.cb,self.ub
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            lb,cb,ub=self.lb[:stop],self.cb[:stop],self.ub[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            lb,cb,ub=self.lb[start:],self.cb[start:],self.ub[start:]
        else:
            x_data = self.xdata[start:stop]
            lb,cb,ub=self.lb[start:stop],self.cb[start:stop],self.ub[start:stop]
        return {"x_data":x_data,"lb":lb,"cb":cb,"ub":ub}
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 
    
    def update_worker(self,candle):
        self.worker.submit(self.update(candle))

    def add_worker(self,candle):
        self.worker.submit(self.add(candle))
    
    def add_historic_worker(self,n):
        self.worker.submit(self.add_historic(n))

    def started_worker(self):
        self.worker.submit(self.fisrt_gen_data())
    
    def paire_data(self,INDICATOR:DataFrame):
        column_names = INDICATOR.columns.tolist()
        lower_name = ''
        mid_name = ''
        upper_name = ''
        for name in column_names:
            if name.__contains__("DCL_"):
                lower_name = name
            elif name.__contains__("DCM_"):
                mid_name = name
            elif name.__contains__("DCU_"):
                upper_name = name

        lb = INDICATOR[lower_name].dropna().round(4)
        cb = INDICATOR[mid_name].dropna().round(4)
        ub = INDICATOR[upper_name].dropna().round(4)
        return lb,cb,ub
    def caculate(self,df: pd.DataFrame):
        INDICATOR = donchian(high=df["high"],
                            low=df["low"],
                            lower_length=self.lower_length,
                            upper_length=self.upper_length,
                            offset=self.offset)
        return self.paire_data(INDICATOR)
        return None,None,None
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        lb,cb,ub = self.caculate(df)

        _len = min([len(lb),len(cb),len(ub)])
        _index = df["index"].tail(_len)
        
        self.df = pd.DataFrame({
                            'index':_index,
                            "lb":lb.tail(_len),
                            "cb":cb.tail(_len),
                            "ub":ub.tail(_len)
                            })
                
        self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_list(),self.df["lb"].to_list(),self.df["cb"].to_list(),self.df["ub"].to_list()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.sig_reset_all.emit()
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        lb,cb,ub = self.caculate(df)

        _len = min([len(lb),len(cb),len(ub)])
        _index = df["index"].tail(_len)
        
        _df = pd.DataFrame({
                            'index':_index,
                            "lb":lb.tail(_len),
                            "cb":cb.tail(_len),
                            "ub":ub.tail(_len)
                            })
        
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        
        self.xdata = _df["index"].to_list() + self.xdata
        self.lb = _df["lb"].to_list() + self.lb
        self.cb = _df["cb"].to_list() + self.cb
        self.ub = _df["ub"].to_list() + self.ub
        
        # self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_list(),self.df["lb"].to_list(),self.df["cb"].to_list(),self.df["ub"].to_list()
        
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False 
        self.is_histocric_load = True
        self.sig_add_historic.emit()
    
    def add(self,new_candles:List[OHLCV]):
        self.is_current_update = False
        new_candle:OHLCV = new_candles[-1]
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.upper_length*5)
                    
            lb,cb,ub = self.caculate(df)
 
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "lb":[lb.iloc[-1]],
                                    "cb":[cb.iloc[-1]],
                                    "ub":[ub.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
                                
            self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_list(),self.df["lb"].to_list(),\
                                                self.df["cb"].to_list(),self.df["ub"].to_list()
            
           
            self.sig_add_candle.emit()
            self.is_current_update = True
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.upper_length*5)
                    
            lb,cb,ub = self.caculate(df)

            self.df.iloc[-1] = [new_candle.index,lb.iloc[-1],cb.iloc[-1],ub.iloc[-1]]
                    
            self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_list(),self.df["lb"].to_list(),\
                                                self.df["cb"].to_list(),self.df["ub"].to_list()
            
            self.sig_update_candle.emit()
            self.is_current_update = True
            
