# -*- coding: utf-8 -*-
from concurrent.futures import Future
from numpy import nan
from pandas import DataFrame, Series
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta._typing import DictLike, Int, IntFloat
from atklip.controls.pandas_ta.overlap import ema, linreg, sma
from atklip.controls.trend import decreasing, increasing
from atklip.controls.pandas_ta.utils import (
    simplify_columns,
    unsigned_differences,
    v_bool,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series
)
from atklip.controls.volatility import bbands, kc
from .mom import mom



def squeeze(
    high: Series, low: Series, close: Series,
    bb_length: Int = None, bb_std: IntFloat = None,
    kc_length: Int = None, kc_scalar: IntFloat = None,
    mom_length: Int = None, mom_smooth: Int = None,
    use_tr: bool = None, mamode: str = None,
    prenan: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Squeeze (SQZ)

    The default is based on John Carter's "TTM Squeeze" indicator, as
    discussed in his book "Mastering the Trade" (chapter 11). The Squeeze
    indicator attempts to capture the relationship between two studies:
    Bollinger Bands® and Keltner's Channels. When the volatility increases,
    so does the distance between the bands, conversely, when the volatility
    declines, the distance also decreases. It finds sections of the
    Bollinger Bands® study which fall inside the Keltner's Channels.

    Sources:
        https://tradestation.tradingappstore.com/products/TTMSqueeze
        https://www.tradingview.com/scripts/lazybear/
        https://tlc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/T-U/TTM-Squeeze

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        bb_length (int): Bollinger Bands period. Default: 20
        bb_std (float): Bollinger Bands Std. Dev. Default: 2
        kc_length (int): Keltner Channel period. Default: 20
        kc_scalar (float): Keltner Channel scalar. Default: 1.5
        mom_length (int): Momentum Period. Default: 12
        mom_smooth (int): Smoothing Period of Momentum. Default: 6
        mamode (str): Only "ema" or "sma". Default: "sma"
        prenan (bool): If True, sets nan for all columns up the first
            valid squeeze value. Default: False
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        tr (value, optional): Use True Range for Keltner Channels.
            Default: True
        asint (value, optional): Use integers instead of bool. Default: True
        mamode (value, optional): Which MA to use. Default: "sma"
        lazybear (value, optional): Use LazyBear's TradingView implementation.
            Default: False
        detailed (value, optional): Return additional variations of SQZ for
            visualization. Default: False
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: SQZ, SQZ_ON, SQZ_OFF, NO_SQZ columns by default. More
            detailed columns if 'detailed' kwarg is True.
    """
    # Validate
    bb_length = v_pos_default(bb_length, 20)
    kc_length = v_pos_default(kc_length, 20)
    mom_length = v_pos_default(mom_length, 12)
    mom_smooth = v_pos_default(mom_smooth, 6)
    _length = max(bb_length, kc_length, mom_length, mom_smooth) + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    bb_std = v_pos_default(bb_std, 2.0)
    kc_scalar = v_pos_default(kc_scalar, 1.5)
    mamode = v_mamode(mamode, "sma")
    prenan = v_bool(prenan, False)
    offset = v_offset(offset)

    use_tr = kwargs.pop("tr", True)
    asint = kwargs.pop("asint", True)
    detailed = kwargs.pop("detailed", False)
    lazybear = kwargs.pop("lazybear", False)

    # Calculate
    bbd = bbands(close, length=bb_length, std=bb_std, mamode=mamode)
    kch = kc(
        high, low, close, length=kc_length, scalar=kc_scalar,
        mamode=mamode, tr=use_tr
    )

    # Simplify KC and BBAND column names for dynamic access
    bbd.columns = simplify_columns(bbd)
    kch.columns = simplify_columns(kch)

    if lazybear:
        highest_high = high.rolling(kc_length).max()
        lowest_low = low.rolling(kc_length).min()
        avg_ = 0.5 * (0.5 * (highest_high + lowest_low) + kch.b)

        squeeze = linreg(close - avg_, length=kc_length)

    else:
        momo = mom(close, length=mom_length)
        if mamode.lower() == "ema":
            squeeze = ema(momo, length=mom_smooth)
        else:  # "sma"
            squeeze = sma(momo, length=mom_smooth)

    # Classify Squeezes
    squeeze_on = (bbd.l > kch.l) & (bbd.u < kch.u)
    squeeze_off = (bbd.l < kch.l) & (bbd.u > kch.u)
    no_squeeze = ~squeeze_on & ~squeeze_off

    # Offset
    if offset != 0:
        squeeze = squeeze.shift(offset)
        squeeze_on = squeeze_on.shift(offset)
        squeeze_off = squeeze_off.shift(offset)
        no_squeeze = no_squeeze.shift(offset)

    # Fill
    if "fillna" in kwargs:
        squeeze.fillna(kwargs["fillna"], inplace=True)
        squeeze_on.fillna(kwargs["fillna"], inplace=True)
        squeeze_off.fillna(kwargs["fillna"], inplace=True)
        no_squeeze.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = "" if use_tr else "hlr"
    _props += f"_{bb_length}_{bb_std}_{kc_length}_{kc_scalar}"
    _props += "_LB" if lazybear else ""
    squeeze.name = f"SQZ{_props}"

    if asint:
        squeeze_on = squeeze_on.astype(int)
        squeeze_off = squeeze_off.astype(int)
        no_squeeze = no_squeeze.astype(int)

    if prenan:
        nanlength = max(bb_length, kc_length) - 2
        squeeze_on[:nanlength] = nan
        squeeze_off[:nanlength] = nan
        no_squeeze[:nanlength] = nan

    data = {
        squeeze.name: squeeze,
        f"SQZ_ON": squeeze_on,
        f"SQZ_OFF": squeeze_off,
        f"SQZ_NO": no_squeeze
    }
    df = DataFrame(data, index=close.index)
    df.name = squeeze.name
    df.category = squeeze.category = "momentum"

    # More Detail
    if detailed:
        pos_squeeze = squeeze[squeeze >= 0]
        neg_squeeze = squeeze[squeeze < 0]

        pos_inc, pos_dec = unsigned_differences(pos_squeeze, asint=True)
        neg_inc, neg_dec = unsigned_differences(neg_squeeze, asint=True)

        pos_inc *= squeeze
        pos_dec *= squeeze
        neg_dec *= squeeze
        neg_inc *= squeeze

        pos_inc.replace(0, nan, inplace=True)
        pos_dec.replace(0, nan, inplace=True)
        neg_dec.replace(0, nan, inplace=True)
        neg_inc.replace(0, nan, inplace=True)

        sqz_inc = squeeze * increasing(squeeze)
        sqz_dec = squeeze * decreasing(squeeze)
        sqz_inc.replace(0, nan, inplace=True)
        sqz_dec.replace(0, nan, inplace=True)

        # Handle fills
        if "fillna" in kwargs:
            sqz_inc.fillna(kwargs["fillna"], inplace=True)
            sqz_dec.fillna(kwargs["fillna"], inplace=True)
            pos_inc.fillna(kwargs["fillna"], inplace=True)
            pos_dec.fillna(kwargs["fillna"], inplace=True)
            neg_dec.fillna(kwargs["fillna"], inplace=True)
            neg_inc.fillna(kwargs["fillna"], inplace=True)

        df[f"SQZ_INC"] = sqz_inc
        df[f"SQZ_DEC"] = sqz_dec
        df[f"SQZ_PINC"] = pos_inc
        df[f"SQZ_PDEC"] = pos_dec
        df[f"SQZ_NDEC"] = neg_dec
        df[f"SQZ_NINC"] = neg_inc

    return df


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject

class SQEEZE(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()   
    sig_add_historic = Signal(int)  
    def __init__(self,_candles,dict_ta_params: dict={}) -> None:
        super().__init__(parent=None)
        
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
    
        self.bb_length = dict_ta_params.get("bb_length",20)
        self.bb_std = dict_ta_params.get("bb_std",2)
        self.kc_length = dict_ta_params.get("kc_length",20)
        self.kc_scalar = dict_ta_params.get("kc_scalar",1.5)
        self.mom_length = dict_ta_params.get("mom_length",12)
        self.mom_smooth = dict_ta_params.get("mom_smooth",6)
        self.mamode = dict_ta_params.get("mamode","sma").lower()
        self.kwargs ={"use_tr" : dict_ta_params.get("use_tr",True),
                    "lazybear" : dict_ta_params.get("lazybear",True),
                    "detailed" : dict_ta_params.get("detailed",False)}
        
        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"SQEEZE {self.bb_length} {self.bb_std} {self.kc_length} {self.kc_scalar} {self.mom_length} {self.mom_smooth} {self.mamode.lower()}"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        # self.SQZ_data,self.SQZ_ON_data,self.SQZ_OFF_data,self.NO_SQZ_data,self.SQZ_INC_data,self.SQZ_DEC_data,self.SQZ_PINC_data,\
        #     self.SQZ_PDEC_data,self.SQZ_NDEC_data,self.SQZ_NINC_data = \
        #     np.array([]),np.array([]),np.array([]),np.array([]),np.array([]),\
        #         np.array([]),np.array([]),np.array([]),np.array([]),np.array([])
        
        self.xdata, self.SQZ_data,self.SQZ_ON_data,self.SQZ_OFF_data,self.NO_SQZ_data=np.array([]), np.array([]),np.array([]),np.array([]),np.array([])

        self.connect_signals()
    @property
    def is_current_update(self)-> bool:
        return self._is_current_update
    @is_current_update.setter
    def is_current_update(self,_is_current_update):
        self._is_current_update = _is_current_update
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
            self.bb_length = dict_ta_params.get("bb_length",20)
            self.bb_std = dict_ta_params.get("bb_std",2)
            self.kc_length = dict_ta_params.get("kc_length",20)
            self.kc_scalar = dict_ta_params.get("kc_scalar",1.5)
            self.mom_length = dict_ta_params.get("mom_length",12)
            self.mom_smooth = dict_ta_params.get("mom_smooth",6)
            self.mamode = dict_ta_params.get("mamode","sma").lower()
            self.kwargs ={"use_tr" : dict_ta_params.get("use_tr",True),
                        "lazybear" : dict_ta_params.get("lazybear",True),
                        "detailed" : dict_ta_params.get("detailed",False)}
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.bb_length} {self.bb_std} {self.kc_length} {self.kc_scalar} {self.mom_length} {self.mom_smooth} {self.mamode.lower()}"

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
            return self.xdata, self.SQZ_data
        if start == 0 and stop == 0:
            x_data = self.xdata
            SQZ_data =self.SQZ_data
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            SQZ_data=self.SQZ_data[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            SQZ_data=self.SQZ_data[start:]
        else:
            x_data = self.xdata[start:stop]
            SQZ_data=self.SQZ_data[start:stop]
        return x_data,SQZ_data
    
    
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
        """     
        SQZ, SQZ_ON, SQZ_OFF, NO_SQZ   
        df[f"SQZ_INC"] = sqz_inc
        df[f"SQZ_DEC"] = sqz_dec
        df[f"SQZ_PINC"] = pos_inc
        df[f"SQZ_PDEC"] = pos_dec
        df[f"SQZ_NDEC"] = neg_dec
        df[f"SQZ_NINC"] = neg_inc"""
        column_names = INDICATOR.columns.tolist()
        SQZ = ''
        SQZ_ON = ''
        SQZ_OFF = ''
        NO_SQZ = ''
        SQZ_INC = ''
        SQZ_DEC = ''
        SQZ_PINC = ''
        SQZ_PDEC = ''
        SQZ_NDEC = ''
        SQZ_NINC = ''
        SQZ_data,SQZ_ON_data,SQZ_OFF_data,NO_SQZ_data,SQZ_INC_data,SQZ_DEC_data,SQZ_PINC_data,SQZ_PDEC_data,SQZ_NDEC_data,SQZ_NINC_data = \
            None,None,None,None,None,None,None,None,None,None
        for name in column_names:
            if name.__contains__("_NINC"):
                SQZ_NINC = name
            elif name.__contains__("_NDEC"):
                SQZ_NDEC = name
            elif name.__contains__("_PDEC"):
                SQZ_PDEC = name
            elif name.__contains__("_PINC"):
                SQZ_PINC = name
            elif name.__contains__("_DEC"):
                SQZ_DEC = name
            elif name.__contains__("_INC"):
                SQZ_INC = name
            elif name.__contains__("NO_"):
                NO_SQZ = name
            elif name.__contains__("_OFF"):
                SQZ_OFF = name
            elif name.__contains__("_ON"):
                SQZ_ON = name
            elif name.__contains__(f"SQZ_{self.bb_length}"):
                SQZ = name

        if SQZ != "":
            SQZ_data = INDICATOR[SQZ].dropna().round(6)
        # elif SQZ_ON != "":
        #     SQZ_ON_data = INDICATOR[SQZ_ON].dropna().round(6)
        # elif SQZ_OFF != "":
        #     SQZ_OFF_data = INDICATOR[SQZ_OFF].dropna().round(6)
        # elif NO_SQZ != "":
        #     NO_SQZ_data = INDICATOR[NO_SQZ].dropna().round(6)
        # elif SQZ_INC != "":
        #     SQZ_INC_data = INDICATOR[SQZ_INC].dropna().round(6)
        # elif SQZ_DEC != "":
        #     SQZ_DEC_data = INDICATOR[SQZ_DEC].dropna().round(6)
        # elif SQZ_PINC != "":
        #     SQZ_PINC_data = INDICATOR[SQZ_PINC].dropna().round(6)
        # elif SQZ_PDEC != "":
        #     SQZ_PDEC_data = INDICATOR[SQZ_PDEC].dropna().round(6)
        # elif SQZ_NDEC != "":
        #     SQZ_NDEC_data = INDICATOR[SQZ_NDEC].dropna().round(6)
        # elif SQZ_NINC != "":
        #     SQZ_NINC_data = INDICATOR[SQZ_NINC].dropna().round(6)

        return SQZ_data #,SQZ_ON_data,SQZ_OFF_data,NO_SQZ_data #,SQZ_INC_data,SQZ_DEC_data,SQZ_PINC_data,SQZ_PDEC_data,SQZ_NDEC_data,SQZ_NINC_data
    
    @staticmethod
    def calculate(df: pd.DataFrame,bb_length,bb_std,kc_length,kc_scalar,mom_length,mom_smooth,mamode,kwargs):
        df = df.copy()
        df = df.reset_index(drop=True)
        
        INDICATOR = squeeze(high=df["high"],
                            low=df["low"],
                            close=df["close"],
                            bb_length=bb_length,
                            bb_std=bb_std,
                            kc_length=kc_length,
                            kc_scalar=kc_scalar,
                            mom_length = mom_length,
                            mom_smooth = mom_smooth,
                            mamode=mamode.lower(),
                            kwargs=kwargs).dropna()
        
        column_names = INDICATOR.columns.tolist()
        SQZ = ''
        SQZ_ON = ''
        SQZ_OFF = ''
        NO_SQZ = ''
        SQZ_INC = ''
        SQZ_DEC = ''
        SQZ_PINC = ''
        SQZ_PDEC = ''
        SQZ_NDEC = ''
        SQZ_NINC = ''
        SQZ_data,SQZ_ON_data,SQZ_OFF_data,NO_SQZ_data,SQZ_INC_data,SQZ_DEC_data,SQZ_PINC_data,SQZ_PDEC_data,SQZ_NDEC_data,SQZ_NINC_data = \
            None,None,None,None,None,None,None,None,None,None
        for name in column_names:
            if name.__contains__("_NINC"):
                SQZ_NINC = name
            elif name.__contains__("_NDEC"):
                SQZ_NDEC = name
            elif name.__contains__("_PDEC"):
                SQZ_PDEC = name
            elif name.__contains__("_PINC"):
                SQZ_PINC = name
            elif name.__contains__("_DEC"):
                SQZ_DEC = name
            elif name.__contains__("_INC"):
                SQZ_INC = name
            elif name.__contains__("NO_"):
                NO_SQZ = name
            elif name.__contains__("_OFF"):
                SQZ_OFF = name
            elif name.__contains__("_ON"):
                SQZ_ON = name
            elif name.__contains__(f"SQZ_{bb_length}"):
                SQZ = name
        SQZ_data = INDICATOR[SQZ].dropna().round(6)
        _len = len(SQZ_data)
        _index = df["index"].tail(_len)
        return pd.DataFrame({
                            'index':_index,
                            "SQZ_data":SQZ_data.tail(_len)
                            })
        
        
        

    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df,
                               self.bb_length,self.bb_std,
                               self.kc_length,self.kc_scalar,
                               self.mom_length,self.mom_smooth,
                               self.mamode,self.kwargs)
        process.start()
        
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        candle_df = self._candles.get_df()
        df:pd.DataFrame = candle_df.head(-_pre_len)
        
        process = HeavyProcess(self.calculate,
                               self.callback_gen_historic_data,
                               df,
                               self.bb_length,self.bb_std,
                               self.kc_length,self.kc_scalar,
                               self.mom_length,self.mom_smooth,
                               self.mamode,self.kwargs)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(int(self.bb_length+self.kc_length+self.mom_length+self.mom_smooth)+10)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df,
                               self.bb_length,self.bb_std,
                               self.kc_length,self.kc_scalar,
                               self.mom_length,self.mom_smooth,
                               self.mamode,self.kwargs)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(int(self.bb_length+self.kc_length+self.mom_length+self.mom_smooth)+10)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df,
                               self.bb_length,self.bb_std,
                               self.kc_length,self.kc_scalar,
                               self.mom_length,self.mom_smooth,
                               self.mamode,self.kwargs)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        
        self.xdata,self.SQZ_data = self.df["index"].to_numpy(),self.df["SQZ_data"].to_numpy()
        
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
        self.SQZ_data = np.concatenate((_df["SQZ_data"].to_numpy(), self.SQZ_data))

        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
         
    def callback_add(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_SQZ_data = df["SQZ_data"].iloc[-1]
        
        new_frame = pd.DataFrame({
                                    'index':[last_index],
                                    "SQZ_data":[last_SQZ_data]
                                    })
            
        self.df = pd.concat([self.df,new_frame],ignore_index=True)
        self.xdata = np.concatenate((self.xdata,np.array([last_index])))
        self.SQZ_data = np.concatenate((self.SQZ_data,np.array([last_SQZ_data])))
        self.sig_add_candle.emit()
        #self.is_current_update = True
        

    def callback_update(self,future: Future):
        df = future.result()
        last_index = df["index"].iloc[-1]
        last_SQZ_data = df["SQZ_data"].iloc[-1]
        self.df.iloc[-1] = [last_index,last_SQZ_data]
        self.xdata[-1],self.SQZ_data[-1] = last_index,last_SQZ_data
        self.sig_update_candle.emit()
        #self.is_current_update = True
        