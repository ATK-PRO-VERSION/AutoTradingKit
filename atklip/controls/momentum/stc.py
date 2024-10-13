# -*- coding: utf-8 -*-
from numpy import nan
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.overlap import ema
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.pandas_ta.utils import (
    non_zero_range,
    v_offset,
    v_pos_default,
    v_series
)



def stc(
    close: Series, tclength: Int = None,
    fast: Int = None, slow: Int = None, mamode: str = "ema",factor: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Schaff Trend Cycle (STC)

    The Schaff Trend Cycle is an evolution of the popular MACD
    incorporating two cascaded stochastic calculations with additional
    smoothing.

    The STC returns also the beginning MACD result as well as the result
    after the first stochastic including its smoothing. This implementation
    has been extended for Pandas TA to also allow for separately feeding any
    other two moving Averages (as ma1 and ma2) or to skip this to feed an
    oscillator, based on which the Schaff Trend Cycle should be calculated.

    Feed external moving averages:
    Internally calculation..
        stc = ta.stc(close=df["close"], tclength=stc_tclen, fast=ma1_interval, slow=ma2_interval, factor=stc_factor)
    becomes..
        extMa1 = df.ta.zlma(close=df["close"], length=ma1_interval, append=True)
        extMa2 = df.ta.ema(close=df["close"], length=ma2_interval, append=True)
        stc = ta.stc(close=df["close"], tclength=stc_tclen, ma1=extMa1, ma2=extMa2, factor=stc_factor)

    The same goes for osc=, which allows the input of an externally
    calculated oscillator, overriding ma1 & ma2.

    Coded by rengel8

    Sources:
        https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle2/

    Args:
        close (pd.Series): Series of 'close's
        tclength (int): SchaffTC Signal-Line length.
            Default: 10 (adjust to the half of cycle)
        fast (int): The short period. Default: 12
        slow (int): The long period. Default: 26
        factor (float): smoothing factor for last stoch. calculation.
            Default: 0.5
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        ma1: External MA (mandatory in conjunction with ma2)
        ma2: External MA (mandatory in conjunction with ma1)
        osc: External oscillator
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: stc, macd, stoch
    """
    # Validate
    fast = v_pos_default(fast, 12)
    slow = v_pos_default(slow, 26)
    tclength = v_pos_default(tclength, 10)
    if slow < fast:
        fast, slow = slow, fast
    _length = max(tclength, fast, slow)
    close = v_series(close, _length)

    if close is None:
        return

    factor = v_pos_default(factor, 0.5)
    offset = v_offset(offset)

    # Calculate
    # kwargs allows for three more series (ma1, ma2 and osc) which can be passed
    # here ma1 and ma2 input negate internal ema calculations, osc substitutes
    # both ma's.
    ma1 = kwargs.pop("ma1", False)
    ma2 = kwargs.pop("ma2", False)
    osc = kwargs.pop("osc", False)

    # 3 different modes of calculation..
    if isinstance(ma1, Series) and isinstance(ma2, Series) and not osc:
        ma1 = v_series(ma1, _length)
        ma2 = v_series(ma2, _length)

        if ma1 is None or ma2 is None:
            return
        # According to external feed series
        xmacd = ma1 - ma2
        pff, pf = schaff_tc(close, xmacd, tclength, factor)
    elif isinstance(osc, Series):
        osc = v_series(osc, _length)
        if osc is None:
            return
        # According to feed oscillator (should be ranging around 0 x-axis)
        xmacd = osc
        pff, pf = schaff_tc(close, xmacd, tclength, factor)
    else:
        # MACD (traditional/full)
        # fastma = ema(close, length=fast)
        # slowma = ema(close, length=slow)
        fastma = ma(mamode, close, length=fast)
        slowma = ma(mamode, close, length=slow)
        xmacd = fastma - slowma
        pff, pf = schaff_tc(close, xmacd, tclength, factor)

    pf[:_length - 1] = nan

    stc = Series(pff, index=close.index)
    macd = Series(xmacd, index=close.index)
    stoch = Series(pf, index=close.index)

    stc.iloc[:_length - 1] = nan

    # Offset
    if offset != 0:
        stc = stc.shift(offset)
        macd = macd.shift(offset)
        stoch = stoch.shift(offset)

    # Fill
    if "fillna" in kwargs:
        stc.fillna(kwargs["fillna"], inplace=True)
        macd.fillna(kwargs["fillna"], inplace=True)
        stoch.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{tclength}_{fast}_{slow}_{factor}"
    stc.name = f"STC{_props}"
    macd.name = f"STCmacd{_props}"
    stoch.name = f"STCstoch{_props}"
    stc.category = macd.category = stoch.category = "momentum"

    data = {
        stc.name: stc,
        macd.name: macd,
        stoch.name: stoch
    }
    df = DataFrame(data, index=close.index)
    df.name = f"STC{_props}"
    df.category = stc.category

    return df


def schaff_tc(close, xmacd, tclength, factor):
    # ACTUAL Calculation part, which is shared between operation modes
    lowest_xmacd = xmacd.rolling(tclength).min()
    xmacd_range = non_zero_range(xmacd.rolling(tclength).max(), lowest_xmacd)
    m = len(xmacd)

    # Initialize lists
    stoch1, pf = [0] * m, [0] * m
    stoch2, pff = [0] * m, [0] * m

    for i in range(1, m):
        # %Fast K of MACD
        if lowest_xmacd.iloc[i] > 0:
            stoch1[i] = 100 * ((xmacd.iloc[i] - lowest_xmacd.iloc[i]) / xmacd_range.iloc[i])
        else:
            stoch1[i] = stoch1[i - 1]
        # Smoothed Calculation for % Fast D of MACD
        pf[i] = round(pf[i - 1] + (factor * (stoch1[i] - pf[i - 1])), 8)

        # find min and max so far
        if i < tclength:
            # If there are not enough elements for a full tclength window, use what is available
            lowest_pf = min(pf[:i+1])
            highest_pf = max(pf[:i+1])
        else:
            lowest_pf = min(pf[i-tclength+1:i+1])
            highest_pf = max(pf[i-tclength+1:i+1])

        # Ensure non-zero range
        pf_range = highest_pf - lowest_pf if highest_pf - lowest_pf > 0 else 1

        # % of Fast K of PF
        if pf_range > 0:
            stoch2[i] = 100 * ((pf[i] - lowest_pf) / pf_range)
        else:
            stoch2[i] = stoch2[i - 1]
        pff[i] = round(pff[i - 1] + (factor * (stoch2[i] - pff[i - 1])), 8)

    pf_series = Series(pf, index=close.index)
    pff_series = Series(pff, index=close.index)

    return pff_series, pf_series



import numpy as np
import pandas as pd
from typing import List
from psygnal import Signal
from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.app_api.workers import ApiThreadPool

class STC():
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal()
    def __init__(self,_candles,dict_ta_params) -> None:
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.source:str = dict_ta_params["source"]              
        self.tclength:int= dict_ta_params["tclength"]
        self.fast:int = dict_ta_params["fast"]
        self.slow:int = dict_ta_params["slow"]
        self.ma_type:str = dict_ta_params["ma_type"]
        self.factor  :float=dict_ta_params.get("factor",0.5)
        self.offset :int=dict_ta_params.get("offset",0)

        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self.name = f"STC {self.source} {self.slow} {self.fast} {self.tclength} {self.ma_type}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.stc_,self.macd,self.stoch = [],[],[],[]

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
            self.source:str = dict_ta_params["source"]              
            self.tclength:int= dict_ta_params["tclength"]
            self.fast:int = dict_ta_params["fast"]
            self.slow:int = dict_ta_params["slow"]
            self.ma_type:str = dict_ta_params["ma_type"]
            self.factor  :float=dict_ta_params.get("factor",0.5)
            self.offset :int=dict_ta_params.get("offset",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.ma_type}-{self.tclength}-{self.fast}-{self.slow}"

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
            return {"x_data":[],"stc_":[],"macd":[],"stoch":[]}
        if start == 0 and stop == 0:
            x_data = self.xdata
            stc_,macd,stoch=self.stc_,self.macd,self.stoch
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            stc_,macd,stoch=self.stc_[:stop],self.macd[:stop],self.stoch[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            stc_,macd,stoch=self.stc_[start:],self.macd[start:],self.stoch[start:]
        else:
            x_data = self.xdata[start:stop]
            stc_,macd,stoch=self.stc_[start:stop],self.macd[start:stop],self.stoch[start:stop]
        return {"x_data":x_data,"stc_":stc_,"macd":macd,"stoch":stoch}
    
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
    
    def paire_data(self,INDICATOR:pd.DataFrame|pd.Series):
        
        column_names = INDICATOR.columns.tolist()
        
        stc_name = ''
        stoch_name = ''
        macd_name = ''
        for name in column_names:
            if name.__contains__("STC") and stc_name == "":
                stc_name = name
            if name.__contains__("STCstoch") and stoch_name == "":
                stoch_name = name
            if name.__contains__("STCmacd") and macd_name == "":
                macd_name = name
        stc_ = INDICATOR[stc_name].dropna().round(4)
        macd = INDICATOR[macd_name].dropna().round(4)
        stoch = INDICATOR[stoch_name].dropna().round(4)
        return stc_,macd,stoch
    
    def caculate(self,df: pd.DataFrame):
        INDICATOR = stc(close= df[self.source],
                        tclength= self.tclength,
                        fast = self.fast,
                        slow = self.slow,
                        mamode= self.ma_type,
                        factor=self.factor,
                        offset=self.offset
                        ).dropna().round(4)
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        
        stc_,macd,stoch = self.caculate(df)
        
        _len = min([len(stc_),len(macd),len(stoch)])
        _index = df["index"].tail(_len)
        
        self.df = pd.DataFrame({
                            'index':_index,
                            "stc":stc_.tail(_len),
                            "macd":macd.tail(_len),
                            "stoch":stoch.tail(_len)
                            })
                
        self.xdata,self.stc_,self.macd,self.stoch = self.df["index"].to_list(),self.df["stc"].to_list(),self.df["macd"].to_list(),self.df["stoch"].to_list()
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
        stc_,macd,stoch = self.caculate(df)
        
        _len = min([len(stc_),len(macd),len(stoch)])
        _index = df["index"].tail(_len)
        
        _df = pd.DataFrame({
                            'index':_index,
                            "stc":stc_.tail(_len),
                            "macd":macd.tail(_len),
                            "stoch":stoch.tail(_len)
                            })
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        self.xdata = _df["index"].to_list() + self.xdata
        self.stc_ = _df["stc"].to_list() + self.stc_
        self.macd = _df["macd"].to_list() + self.macd
        self.stoch = _df["stoch"].to_list() + self.stoch
        
        # self.xdata,self.stc_,self.macd,self.stoch = self.df["index"].to_list(),self.df["stc"].to_list(),self.df["macd"].to_list(),self.df["stoch"].to_list()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit()
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow*5)
                    
            stc_,macd,stoch = self.caculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "stc":[stc_.iloc[-1]],
                                    "macd":[macd.iloc[-1]],
                                    "stoch":[stoch.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata,self.stc_,self.macd,self.stoch = self.df["index"].to_list(),self.df["stc"].to_list(),self.df["macd"].to_list(),self.df["stoch"].to_list()
                                            
            self.sig_add_candle.emit()
            self.is_current_update = True
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow*5)
                    
            stc_,macd,stoch = self.caculate(df)
                    
            self.df.iloc[-1] = [new_candle.index,stc_.iloc[-1],macd.iloc[-1],stoch.iloc[-1]]
                    
            self.xdata,self.stc_,self.macd,self.stoch = self.df["index"].to_list(),self.df["stc"].to_list(),self.df["macd"].to_list(),self.df["stoch"].to_list()
            
            self.sig_update_candle.emit()
            self.is_current_update = True
