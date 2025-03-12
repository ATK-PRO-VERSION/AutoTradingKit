# -*- coding: utf-8 -*-
from concurrent.futures import Future
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta.momentum import squeeze
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
        