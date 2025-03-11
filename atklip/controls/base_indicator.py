from concurrent.futures import Future
import pandas as pd
from typing import List,TYPE_CHECKING
from atklip.controls.ohlcv import OHLCV
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import QObject,Signal
if TYPE_CHECKING:
    from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE

class INDICATOR(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int)
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f""
        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self,_name):
        self._name = _name
    @property
    def source_name(self)-> str:
        return self._source_name
    @source_name.setter
    def source_name(self,source_name):
        self._source_name = source_name
    
    def change_input(self,candles=None,dict_ta_params:dict={}):...
    
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
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
     
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    def get_data(self,start:int=0,stop:int=0):...
    
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
    
    @staticmethod
    def paire_data(INDICATOR:pd.DataFrame):...
    
    @staticmethod
    def calculate(df: pd.DataFrame,source,fast_period,slow_period,signal_period,mamode,offset):...
    
    def callback_first_gen(self, future: Future):...
    
    def fisrt_gen_data(self):...
    
    def callback_gen_historic_data(self, future: Future):...
    
    def add_historic(self,n:int):...
        
    def add_update_calculate(self,df: pd.DataFrame):...
    
    def callback_add(self):...
    
    def add(self,new_candles:List[OHLCV]):...
        
    def callback_update(self):...
    
    def update(self, new_candles:List[OHLCV]):...
            
            
