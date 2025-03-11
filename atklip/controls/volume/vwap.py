# -*- coding: utf-8 -*-
from warnings import simplefilter
from pandas import DataFrame, Series
from atklip.controls.pandas_ta._typing import DictLike, Int, List
from atklip.controls.pandas_ta.overlap import hlc3
from atklip.controls.pandas_ta.utils import v_datetime_ordered, v_list, v_offset, v_series



def vwap(
    high: Series, low: Series, close: Series, volume: Series,
    anchor: str = None, bands: List = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Volume Weighted Average Price (VWAP)

    The Volume Weighted Average Price that measures the average typical price
    by volume.  It is typically used with intraday charts to identify general
    direction.

    Sources:
        https://www.tradingview.com/wiki/Volume_Weighted_Average_Price_(VWAP)
        https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/volume-weighted-average-price-vwap/
        https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:vwap_intraday
        https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=108&Name=Volume_Weighted_Average_Price_-_VWAP_-_with_Standard_Deviation_Lines

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        volume (pd.Series): Series of 'volume's
        anchor (str): How to anchor VWAP. Depending on the index values,
            it will implement various Timeseries Offset Aliases
            as listed here:
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
            Default: "D".
        bands (list): List of deviations to be calculated. Calculates upper
            and lower values given a positive list of ints or floats.
            Default: []
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.Series: New feature generated.
        Or
        pd.DataFrame: New feature generated.
    """
    # Validate
    _length = 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)
    volume = v_series(volume, _length)

    if high is None or low is None or close is None or volume is None:
        return

    bands = v_list(bands)
    offset = v_offset(offset)

    if anchor and isinstance(anchor, str) and len(anchor) >= 1:
        anchor = anchor.upper()
    else:
        anchor = "D"

    typical_price = hlc3(high=high, low=low, close=close)
    if not v_datetime_ordered(volume) or \
        not v_datetime_ordered(typical_price):
        print("[!] VWAP requires an ordered DatetimeIndex.")
        return

    # Calculate
    _props = f"VWAP_{anchor}"
    wp = typical_price * volume
    simplefilter(action="ignore", category=UserWarning)
    vwap = wp.groupby(wp.index.to_period(anchor)).cumsum() \
        / volume.groupby(volume.index.to_period(anchor)).cumsum()

    if bands and len(bands):
        # Calculate vwap stdev bands
        vwap_var = volume * (typical_price - vwap) ** 2
        vwap_var_sum = vwap_var \
            .groupby(vwap_var.index.to_period(anchor)).cumsum()
        vwap_volume_sum = volume \
            .groupby(volume.index.to_period(anchor)).cumsum()
        std_volume_weighted = (vwap_var_sum / vwap_volume_sum) ** 0.5

    # Name and Category
    vwap.name = _props
    vwap.category = "overlap"

    if bands:
        df = DataFrame({vwap.name: vwap}, index=close.index)
        for i in bands:
            df[f"{_props}_L_{i}"] = vwap - i * std_volume_weighted
            df[f"{_props}_U_{i}"] = vwap + i * std_volume_weighted
            df[f"{_props}_L_{i}"].name = df[f"{_props}_U_{i}"].name = _props
            df[f"{_props}_L_{i}"].category = "overlap"
            df[f"{_props}_U_{i}"].category = "overlap"
        df.name = _props
        df.category = "overlap"

    # Offset
    if offset != 0:
        if bands and not df.empty:
            df = df.shift(offset)
        vwap = vwap.shift(offset)

    # Fill
    if "fillna" in kwargs:
        if bands and not df.empty:
            df.fillna(kwargs["fillna"], inplace=True)
        else:
            vwap.fillna(kwargs["fillna"], inplace=True)

    if bands and not df.empty:
        return df
    return vwap


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool

from PySide6.QtCore import Signal,QObject

class VWAP(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int)    
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.mamode:str = dict_ta_params["mamode"]
        self.source:str = dict_ta_params["source"]
        self.length:int = dict_ta_params["length"]
        self.std_dev_mult:float = dict_ta_params["std_dev_mult"]
        self.ddof  :int=dict_ta_params.get("ddof",0)
        self.offset :int=dict_ta_params.get("offset",0)

        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"{self.mamode.lower()} {self.source} {self.length} {self.std_dev_mult}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.lb,self.cb,self.ub = np.array([]),np.array([]),np.array([]),np.array([])

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
            self.mamode:str = dict_ta_params["mamode"]
            self.source:str = dict_ta_params["source"]
            self.length:int = dict_ta_params["length"]
            self.std_dev_mult:float = dict_ta_params["std_dev_mult"]
            self.ddof  :int=dict_ta_params.get("ddof",0)
            self.offset :int=dict_ta_params.get("offset",0)
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.source}-{self.mamode}-{self.length}-{self.std_dev_mult}"

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
            return [],[],[],[]
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
        return x_data,lb,cb,ub
    
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
    
    def paire_data(self,INDICATOR:DataFrame):
        column_names = INDICATOR.columns.tolist()
        
        lower_name = ''
        mid_name = ''
        upper_name = ''
        for name in column_names:
            if name.__contains__("BBL_"):
                lower_name = name
            elif name.__contains__("BBM_"):
                mid_name = name
            elif name.__contains__("BBU_"):
                upper_name = name

        lb = INDICATOR[lower_name].dropna().round(6)
        cb = INDICATOR[mid_name].dropna().round(6)
        ub = INDICATOR[upper_name].dropna().round(6)
        return lb,cb,ub
    def calculate(self,df: pd.DataFrame):
        INDICATOR = vwap(high=df["high"],
                         low=df["low"],
                         close=df["close"],
                         volume=df["volume"]
                          )
        return self.paire_data(INDICATOR)
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
                     
        lb,cb,ub = self.calculate(df)
        
        _len = min([len(lb),len(cb),len(ub)])
        _index = df["index"].tail(_len)
        
        self.df = pd.DataFrame({
                            'index':_index,
                            "lb":lb.tail(_len),
                            "cb":cb.tail(_len),
                            "ub":ub.tail(_len)
                            })
                
        self.xdata,self.lb,self.cb,self.ub = self.df["index"].to_numpy(),self.df["lb"].to_numpy(),self.df["cb"].to_numpy(),self.df["ub"].to_numpy()
        
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
        
        lb,cb,ub = self.calculate(df)

        _len = min([len(lb),len(cb),len(ub)])
        _index = df["index"].tail(_len)
        
        _df = pd.DataFrame({
                            'index':_index,
                            "lb":lb.tail(_len),
                            "cb":cb.tail(_len),
                            "ub":ub.tail(_len)
                            })
        
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        
        self.xdata = np.concatenate((_df["index"].to_numpy(), self.xdata)) 
        self.lb = np.concatenate((_df["lb"].to_numpy(), self.lb))   
        self.cb = np.concatenate((_df["cb"].to_numpy(), self.cb))
        self.ub = np.concatenate((_df["ub"].to_numpy(), self.ub))
                
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False 
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*10)
                    
            lb,cb,ub = self.calculate(df)
            
            new_frame = pd.DataFrame({
                                    'index':[new_candle.index],
                                    "lb":[lb.iloc[-1]],
                                    "cb":[cb.iloc[-1]],
                                    "ub":[ub.iloc[-1]]
                                    })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
                                
            self.xdata = np.concatenate((self.xdata,np.array([new_candle.index])))
            self.lb = np.concatenate((self.lb,np.array([lb.iloc[-1]])))
            self.cb = np.concatenate((self.cb,np.array([cb.iloc[-1]])))
            self.ub = np.concatenate((self.ub,np.array([ub.iloc[-1]])))
            
            self.sig_add_candle.emit()
        #self.is_current_update = True
            
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*10)
                    
            lb,cb,ub = self.calculate(df)
                    
            self.df.iloc[-1] = [new_candle.index,lb.iloc[-1],cb.iloc[-1],ub.iloc[-1]]
                    
            self.xdata[-1],self.lb[-1],self.cb[-1],self.ub[-1] = new_candle.index,lb.iloc[-1],cb.iloc[-1],ub.iloc[-1]
            
            self.sig_update_candle.emit()
        #self.is_current_update = True
            
            
