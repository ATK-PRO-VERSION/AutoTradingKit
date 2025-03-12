# -*- coding: utf-8 -*-
from concurrent.futures import Future
from atklip.appmanager.worker.return_worker import HeavyProcess
from atklip.controls.pandas_ta._typing import Int, IntFloat
from atklip.app_utils import percent_caculator
import numpy as np
import pandas as pd
from typing import List
from PySide6.QtCore import Qt, Signal,QObject
from atklip.controls.ma_type import PD_MAType
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import CandleWorker


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
    map_x_y:dict = {}
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int) 
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
        self.list_zizgzag:list = []
        self.is_current_update = False
        self._name = f"ZIGZAG {self.legs} {self.deviation}"
        self.df = pd.DataFrame([])
        self.x_data,self.y_data  = np.array([]),np.array([])
        self.connect_signals()
    
    @property
    def is_current_update(self)-> bool:
        return self._is_current_update
    @is_current_update.setter
    def is_current_update(self,_is_current_update):
        self._is_current_update = _is_current_update
     
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
        self._candles.sig_update_candle.connect(self.update_worker,Qt.ConnectionType.AutoConnection)
        self._candles.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.AutoConnection)
        self._candles.signal_delete.connect(self.signal_delete)
        self._candles.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.AutoConnection)
    
    
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
    def name(self):
        return self._name
    @name.setter
    def name(self,_name):
        self._name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_data(self):
        return self.x_data,self.y_data 
    
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
    
    @staticmethod
    def calculate(list_zizgzag, candles: List[OHLCV],process:str="",deviation:float=1):
        if process == "add" or process == "update":
            list_zizgzag = update_zz(list_zizgzag=list_zizgzag,
                                ohlcv=candles[-1],
                                percent= deviation
                                )
        elif process == "load":
            list_zizgzag = load_zz(list_zizgzag=list_zizgzag,
                                candles=candles,
                                percent= deviation
                                )
        else:
            list_zizgzag = my_zigzag(list_zizgzag=list_zizgzag,
                                candles=candles,
                                percent= deviation)
        
        if len(list_zizgzag) == 2:
            if percent_caculator(list_zizgzag[0][1],list_zizgzag[1][1]) >= deviation:
                x_data = [x[0] for x in list_zizgzag]
                y_data = [x[1] for x in list_zizgzag]   
            else:
                x_data,y_data = [],[]
        else:
            x_data = [x[0] for x in list_zizgzag]
            y_data = [x[1] for x in list_zizgzag]  
 
        return list_zizgzag,x_data,y_data
           
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        self.list_zizgzag = []
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               self.list_zizgzag, 
                               self._candles.candles,
                               "",
                               self.deviation)
        process.start()
        
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        process = HeavyProcess(self.calculate,
                               self.callback_gen_historic_data,
                               self.list_zizgzag, 
                               self._candles.candles,
                               "load",
                               self.deviation)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               self.list_zizgzag, 
                               self._candles.candles,
                               "add",
                               self.deviation)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               self.list_zizgzag, 
                               self._candles.candles,
                               "update",
                               self.deviation)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.list_zizgzag,self.x_data,self.y_data = future.result()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        #self.is_current_update = True
        self.sig_reset_all.emit()
        
    def callback_gen_historic_data(self, future: Future):
        self.list_zizgzag,self.x_data,self.y_data = future.result()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        #self.is_current_update = True
        _len = len(self.list_zizgzag)
        self.sig_add_historic.emit(_len)
        
    def callback_add(self,future: Future):
        self.list_zizgzag,self.x_data,self.y_data = future.result()
        self.sig_add_candle.emit()
        #self.is_current_update = True
        
    def callback_update(self,future: Future):
        self.list_zizgzag,self.x_data,self.y_data = future.result()
        self.sig_update_candle.emit()
        #self.is_current_update = True

