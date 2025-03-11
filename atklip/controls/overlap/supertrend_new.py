# -*- coding: utf-8 -*-
from concurrent.futures import Future
from numpy import nan
from pandas import DataFrame, Series
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.overlap import hl2
from atklip.controls.pandas_ta.utils import v_mamode, v_offset, v_pos_default, v_series
from atklip.controls.volatility import atr



def supertrend(
    high: Series, low: Series, close: Series,
    length: Int = None, atr_length: Int = None,
    multiplier: IntFloat = None,
    atr_mamode : str = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Supertrend (supertrend)

    Supertrend is an overlap indicator. It is used to help identify trend
    direction, setting stop loss, identify support and resistance, and/or
    generate buy & sell signals.

    Sources:
        http://www.freebsensetips.com/blog/detail/7/What-is-supertrend-indicator-its-calculation

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        length (int) : Length for ATR calculation. Default: 7
        atr_length (int) : If None, defaults to length otherwise, provides
            variable of control. Default: length
        multiplier (float): Coefficient for upper and lower band distance to
            midrange. Default: 3.0
        atr_mamode (str) : MA type to be used for ATR calculation.
            See ``help(ta.ma)``. Default: 'rma'
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: SUPERT (trend), SUPERTd (direction),
            SUPERTl (long), SUPERTs (short) columns.
    """
    # Validate
    length = v_pos_default(length, 7)
    atr_length = v_pos_default(atr_length, length)
    high = v_series(high, length + 1)
    low = v_series(low, length + 1)
    close = v_series(close, length + 1)

    if high is None or low is None or close is None:
        return

    multiplier = v_pos_default(multiplier, 3.0)
    atr_mamode = v_mamode(atr_mamode, "rma")
    offset = v_offset(offset)

    # Calculate
    m = close.size
    dir_, trend = [1] * m, [0] * m
    long, short = [nan] * m, [nan] * m

    hl2_ = hl2(high, low)
    matr = multiplier * atr(high, low, close, atr_length, mamode=atr_mamode)
    lb = hl2_ - matr
    ub = hl2_ + matr

    for i in range(1, m):
        if close.iat[i] > ub.iat[i - 1]:
            dir_[i] = 1
        elif close.iat[i] < lb.iat[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lb.iat[i] < lb.iat[i - 1]:
                lb.iat[i] = lb.iat[i - 1]
            if dir_[i] < 0 and ub.iat[i] > ub.iat[i - 1]:
                ub.iat[i] = ub.iat[i - 1]

        if dir_[i] > 0:
            trend[i] = long[i] = lb.iat[i]
        else:
            trend[i] = short[i] = ub.iat[i]

    trend[0] = nan
    dir_[:length] = [nan] * length

    _props = f"_{length}_{multiplier}"
    data = {
        f"SUPERTt{_props}": trend,
        f"SUPERTd{_props}": dir_,
        f"SUPERTl{_props}": long,
        f"SUPERTs{_props}": short
    }
    df = DataFrame(data, index=close.index)

    df.name = f"SUPERT{_props}"
    df.category = "overlap"

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Fill
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    return df


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE

class SuperTrend(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int)
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)

        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.length = dict_ta_params.get("length",7)
        self.atr_length = dict_ta_params.get("atr_length",7)
        self.multiplier = dict_ta_params.get("multiplier",3.0)
        self.atr_mamode = dict_ta_params.get("atr_mamode",'rma')

        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"SuperTrend {self.length} {self.atr_length} {self.multiplier} {self.atr_mamode}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.SUPERTt,self.SUPERTd,self.SUPERTl,self.SUPERTs = np.array([]),np.array([]),np.array([]),np.array([]),np.array([])

        self.connect_signals()
    
    @property
    def source_name(self)-> str:
        return self._source_name
    @source_name.setter
    def source_name(self,source_name):
        self._source_name = source_name
    
    def change_input(self,candles=None,dict_ta_params:dict={}):
        if candles != None:
            self.disconnect_signals()
            self._candles : JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE= candles
            self.connect_signals()
        
        if dict_ta_params != {}:
            
            self.length = dict_ta_params.get("length",7)
            self.atr_length = dict_ta_params.get("atr_length",7)
            self.multiplier = dict_ta_params.get("multiplier",3.0)
            self.atr_mamode = dict_ta_params.get("atr_mamode",'rma')
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.length} {self.atr_length} {self.multiplier} {self.atr_mamode}"

            self._name = ta_param
        
        self.first_gen = False
        self.is_genering = True
        
        
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
        self._candles.sig_add_historic.connect(self.add_historic_worker)
        self._candles.signal_delete.connect(self.signal_delete)
    
    
    def change_source(self,_candles):
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
            return [],[],[]
        if start == 0 and stop == 0:
            x_data = self.xdata
            SUPERTt,SUPERTd=self.SUPERTt,self.SUPERTd
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            SUPERTt,SUPERTd=self.SUPERTt[:stop],self.SUPERTd[:stop]  
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            SUPERTt,SUPERTd=self.SUPERTt[start:],self.SUPERTd[start:]   
        else:
            x_data = self.xdata[start:stop]
            SUPERTt,SUPERTd=self.SUPERTt[start:stop],self.SUPERTd[start:stop]    
        return x_data,SUPERTt,SUPERTd
    
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
        try:
            column_names = INDICATOR.columns.tolist()
            SUPERT_name = ''
            SUPERTd_name = ''
            SUPERTl_name = ''
            SUPERTs_name = ''
            for name in column_names:
                if name.__contains__("SUPERTt"):
                    SUPERT_name = name
                elif name.__contains__("SUPERTd"):
                    SUPERTd_name = name
                elif name.__contains__("SUPERTl"):
                    SUPERTl_name = name
                elif name.__contains__("SUPERTs"):
                    SUPERTs_name = name
                    

            SUPERTt = INDICATOR[SUPERT_name].dropna().round(6)
            SUPERTd = INDICATOR[SUPERTd_name].dropna().round(6)
            SUPERTl = INDICATOR[SUPERTl_name].round(6)
            SUPERTs = INDICATOR[SUPERTs_name].round(6)
            return SUPERTt,SUPERTd
        except:
            return Series([]),Series([])
    
    @staticmethod
    def calculate(df: pd.DataFrame,length,atr_length,multiplier,atr_mamode):
        _index = df["index"]
        df = df.copy()
        df = df.reset_index(drop=True)
        INDICATOR = supertrend(high=df["high"], 
                                low=df["low"], 
                                close=df["close"],
                                length = length, 
                                atr_length = atr_length,
                                multiplier = multiplier,
                                atr_mamode = atr_mamode,
                                )
        
        column_names = INDICATOR.columns.tolist()
        SUPERT_name = ''
        SUPERTd_name = ''
        SUPERTl_name = ''
        SUPERTs_name = ''
        for name in column_names:
            if name.__contains__("SUPERTt"):
                SUPERT_name = name
            elif name.__contains__("SUPERTd"):
                SUPERTd_name = name
            elif name.__contains__("SUPERTl"):
                SUPERTl_name = name
            elif name.__contains__("SUPERTs"):
                SUPERTs_name = name
                

        SUPERTt = INDICATOR[SUPERT_name].dropna().round(6)
        SUPERTd = INDICATOR[SUPERTd_name].dropna().round(6)
        # SUPERTl = INDICATOR[SUPERTl_name].round(6)
        # SUPERTs = INDICATOR[SUPERTs_name].round(6)
        _len = min([len(SUPERTt),len(SUPERTd)])
        
        return pd.DataFrame({
                            'index':_index.tail(_len),
                            "SUPERTt":SUPERTt.tail(_len),
                            "SUPERTd":SUPERTd.tail(_len)
                            })
    
    
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df,
                               self.length,
                               self.atr_length,
                               self.multiplier,
                               self.atr_mamode)
        process.start()       
     
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        df:pd.DataFrame = self._candles.get_df().iloc[:-1*_pre_len]
        
        process = HeavyProcess(self.calculate,
                               self.callback_gen_historic_data,
                               df,
                               self.length,
                               self.atr_length,
                               self.multiplier,
                               self.atr_mamode)
        process.start() 
        
    
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*5)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.length,
                               self.atr_length,
                               self.multiplier,
                               self.atr_mamode)
            process.start() 
            
        else:
            pass
            #self.is_current_update = True
            
    
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.length*5)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.length,
                               self.atr_length,
                               self.multiplier,
                               self.atr_mamode)
            process.start() 
        else:
            pass
            #self.is_current_update = True
            
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.xdata,self.SUPERTt,self.SUPERTd = self.df["index"].to_numpy(),self.df["SUPERTt"].to_numpy(),self.df["SUPERTd"].to_numpy()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        #self.is_current_update = True
        self.sig_reset_all.emit()
        
    def callback_gen_historic_data(self, future: Future):
        _df = future.result()
        _len = len(_df)
        
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
        self.xdata = np.concatenate((_df["index"].to_numpy(), self.xdata)) 
        self.SUPERTd = np.concatenate((_df["SUPERTd"].to_numpy(), self.SUPERTd))   
        self.SUPERTt = np.concatenate((_df["SUPERTt"].to_numpy(), self.SUPERTt))

        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
        
    def callback_add(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_SUPERTt = df["SUPERTt"].iloc[-1]
        last_SUPERTd = df["SUPERTd"].iloc[-1]
 
        new_frame = pd.DataFrame({
                                'index':[last_index],
                                "SUPERTt":[last_SUPERTt],
                                "SUPERTd":[last_SUPERTd],
                                })
        self.df = pd.concat([self.df,new_frame],ignore_index=True)
        
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.SUPERTd = np.concatenate((self.SUPERTd,np.array([last_SUPERTt])))
        self.SUPERTt = np.concatenate((self.SUPERTt,np.array([last_SUPERTd])))
        self.sig_add_candle.emit()
        #self.is_current_update = True
    
    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_SUPERTt = df["SUPERTt"].iloc[-1]
        last_SUPERTd = df["SUPERTd"].iloc[-1]
        self.df.iloc[-1] = [last_index,last_SUPERTt,last_SUPERTd]
        self.xdata[-1],self.SUPERTt[-1],self.SUPERTd[-1] = last_index,last_SUPERTt,last_SUPERTd
        self.sig_update_candle.emit()
        #self.is_current_update = True