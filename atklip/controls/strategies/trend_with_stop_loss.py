import numpy as np
import pandas as pd

from atklip.controls.momentum import macd
from atklip.controls.tradingview.atr_stoploss import atr_stoploss

"""_summary_
smaSrcHigh = ta.ema(high,cloud_val)
smaSrcLow = ta.ema(low, cloud_val)
[macdLine, signalLine, histLine] = ta.macd(close, 12, 26, 9)
plot_high = plot(showMovingAverageCloud? smaSrcHigh : na, color = na, transp = 1, editable = false)
plot_low  = plot(showMovingAverageCloud? smaSrcLow  : na, color = na, transp = 1, editable = false)

plotshape(longCond ? up : na, title="UpTrend Begins", location=location.belowbar, style=shape.circle, size=size.tiny, color=color.new(color.teal,transp = 50) )
plotshape(longCond and showBuySellSignals ? up : na, title="Buy", text="Buy", location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.new(color.teal,transp = 50), textcolor=color.white )
plotshape(shortCond ? dn : na, title="DownTrend Begins", location=location.abovebar, style=shape.circle, size=size.tiny, color=color.new(color.red,transp = 50) )
plotshape(shortCond and showBuySellSignals ? dn : na, title="Sell", text="Sell", location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new(color.red,transp = 50), textcolor=color.white)
 
fill(plot_high, plot_low, color = (macdLine > 0) and (macdLine[0] > macdLine[1]) ? color.new(color.aqua,transp = 85) : na, title = "Positive Cloud Uptrend")
fill(plot_high, plot_low, color = macdLine > 0 and macdLine[0] < macdLine[1]     ? color.new(color.aqua,transp = 85) : na, title = "Positive Cloud  Downtrend")
fill(plot_high, plot_low, color = macdLine < 0 and macdLine[0] < macdLine[1]     ? color.new(color.red,transp = 85) : na, title = "Negative Cloud  Uptrend")
fill(plot_high, plot_low, color = macdLine < 0 and macdLine[0] > macdLine[1]     ? color.new(color.red,transp = 85) : na, title = "Negative Cloud Downtrend")
"""

def paire_data(INDICATOR:pd.DataFrame):
    try:
        column_names = INDICATOR.columns.tolist()
        macd_name = ''
        histogram_name = ''
        signalma_name = ''
        for name in column_names:
            if name.__contains__("MACD"):
                macd_name = name
            elif name.__contains__("HISTOGRAM"):
                histogram_name = name
            elif name.__contains__("SIGNAL"):
                signalma_name = name

        macd = INDICATOR[macd_name].dropna().round(6)
        histogram = INDICATOR[histogram_name].dropna().round(6)
        signalma = INDICATOR[signalma_name].dropna().round(6)
        return macd,histogram,signalma
    except:
        return pd.Series([]),pd.Series([]),pd.Series([])
    
def calculate_macd(df: pd.DataFrame=None,source="close",fast_period=12,slow_period=26,signal_period=9,macd_mamode="ema"):
    INDICATOR = macd(close=df[source],
                    fast=fast_period,
                    slow=slow_period,
                    signal = signal_period,
                    mamode=macd_mamode,
                    talib= False)
    return paire_data(INDICATOR)

def trend_with_stoploss(data:pd.DataFrame, macd_fast=12, macd_slow=26, macd_signal=9,macd_mamode="ema",
                           atr_length=14,atr_mamode="rma",atr_multiplier=1.5):
    """
    Tính toán Positive Cloud Uptrend và Negative Cloud Uptrend.
    Parameters:
        data (pd.DataFrame): DataFrame chứa các cột ['open', 'high', 'low', 'close'].
        cloud_val (int): Độ dài trung bình động của Cloud.
        macd_fast (int): Chu kỳ nhanh của MACD.
        macd_slow (int): Chu kỳ chậm của MACD.
        macd_signal (int): Chu kỳ tín hiệu của MACD.

    Returns:
        pd.DataFrame: DataFrame với các cột 'Positive_Cloud_Uptrend' và 'Negative_Cloud_Uptrend'.
    """
    data = data.copy()
    # Kiểm tra các cột bắt buộc
    required_columns = ['open', 'high', 'low', 'close']
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"DataFrame phải chứa cột '{col}'.")

    # Tính toán EMA của high và low
    atr_stoploss(data,atr_length,atr_mamode,atr_multiplier)
    
    # Tính toán MACD
    macd_line,histogram,signalma = calculate_macd(data, fast_period=macd_fast, slow_period=macd_slow, signal_period=macd_signal,macd_mamode=macd_mamode)

    # Xác định Positive Cloud Uptrend và Negative Cloud Uptrend
    data["long_stoploss_diff"] = data['long_stoploss'] > data['long_stoploss'].shift(1)
    data["short_stoploss_diff"] = data['short_stoploss'] < data['short_stoploss'].shift(1)
    
    data["macd_line_diff"] = macd_line > macd_line.shift(1)
    data["histogram_diff"] = histogram > histogram.shift(1)
    data["signalma_diff"] = signalma > signalma.shift(1)
    data['_long_stoploss'] = data['long_stoploss'].shift(1)
    data['_short_stoploss'] = data['short_stoploss'].shift(1)
    
    "(macdLine > 0) and (macdLine[0] > macdLine[1])"
    data['Uptrend'] = (macd_line > 0) & (data["long_stoploss_diff"]) & ((data["macd_line_diff"]) | (data["histogram_diff"]==False) | (data["signalma_diff"]))
    #  & ((abs(data['_long_stoploss'] - data['open'])/data['_long_stoploss'])*100 < 0.5)
    "color = macdLine < 0 and macdLine[0] < macdLine[1]  "
    data['Downtrend'] = (macd_line < 0) & (data["short_stoploss_diff"]) & ( ((data["macd_line_diff"]==False))  | (data["histogram_diff"]) | (data["signalma_diff"]==False) )
    # & ((abs(data['_short_stoploss'] - data['open'])/data['_short_stoploss'])*100 < 0.5) 
    return data[["long_stoploss","short_stoploss","Uptrend","Downtrend"]]


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool

from PySide6.QtCore import Signal,QObject

class TrendWithStopLoss(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int)
    def __init__(self,_candles,dict_ta_params) -> None:
        super().__init__(parent=None)

        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.fast_period = dict_ta_params.get("fast_period",12) 
        self.slow_period = dict_ta_params.get("slow_period",26) 
        self.signal_period = dict_ta_params.get("signal_period",9) 
        self.macd_mamode = dict_ta_params.get("macd_mamode","ema") 
        
        self.atr_length = dict_ta_params.get("atr_length",14) 
        self.atr_mamode = dict_ta_params.get("atr_mamode","rma") 
        self.atr_multiplier = dict_ta_params.get("atr_multiplier",1.5) 
        

        #self.signal_delete.connect(self.deleteLater)
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"TrendWithStopLoss"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool
        
        self.xdata,self.long_stoploss,self.short_stoploss,self.Uptrend,self.Downtrend = np.array([]),np.array([]),np.array([]),np.array([]),np.array([])

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
            self.fast_period = dict_ta_params.get("fast_period",12) 
            self.slow_period = dict_ta_params.get("slow_period",26) 
            self.signal_period = dict_ta_params.get("signal_period",9) 
            self.macd_mamode = dict_ta_params.get("macd_mamode","ema")
            self.atr_length = dict_ta_params.get("atr_length",14) 
            self.atr_mamode = dict_ta_params.get("atr_mamode","rma") 
            self.atr_multiplier = dict_ta_params.get("atr_multiplier",1.5) 
            
            ta_name:str=dict_ta_params.get("ta_name")
            obj_id:str=dict_ta_params.get("obj_id") 
            
            ta_param = f"{obj_id}-{ta_name}-{self.fast_period}-{self.slow_period}-{self.signal_period}-{self.atr_length}-{self.atr_mamode}-{self.atr_multiplier}"

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
        self._candles.sig_add_historic.connect(self.add_historic_worker)
        self._candles.signal_delete.connect(self.signal_delete)
    
    
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
            return [],[],[],[],[]
        if start == 0 and stop == 0:
            x_data = self.xdata
            long_stoploss,short_stoploss,Uptrend,Downtrend=self.long_stoploss,self.short_stoploss,self.Uptrend,self.Downtrend
        elif start == 0 and stop != 0:
            x_data = self.xdata[:stop]
            long_stoploss,short_stoploss,Uptrend,Downtrend=self.long_stoploss[:stop],self.short_stoploss[:stop],self.Uptrend[:stop],self.Downtrend[:stop]
        elif start != 0 and stop == 0:
            x_data = self.xdata[start:]
            long_stoploss,short_stoploss,Uptrend,Downtrend=self.long_stoploss[start:],self.short_stoploss[start:],self.Uptrend[start:],self.Downtrend[start:]
        else:
            x_data = self.xdata[start:stop]
            long_stoploss,short_stoploss,Uptrend,Downtrend=self.long_stoploss[start:stop],self.short_stoploss[start:stop],self.Uptrend[start:stop],self.Downtrend[start:stop]
        return x_data,long_stoploss,short_stoploss,Uptrend,Downtrend
    
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
    
    def paire_data(self,INDICATOR:pd.DataFrame):
        try:
            long_stoploss = INDICATOR["long_stoploss"].dropna().round(6)
            short_stoploss = INDICATOR["short_stoploss"].dropna().round(6)
            Uptrend = INDICATOR["Uptrend"].dropna()
            Downtrend = INDICATOR["Downtrend"].dropna()
            return long_stoploss,short_stoploss,Uptrend,Downtrend
        except:
            return pd.Series([]),pd.Series([]),pd.Series([]),pd.Series([])
        
    def calculate(self,df: pd.DataFrame):
        INDICATOR = trend_with_stoploss(df,
                        macd_fast=self.fast_period,
                        macd_slow=self.slow_period,
                        macd_signal = self.signal_period,
                        macd_mamode = self.macd_mamode,
                        atr_length = self.atr_length,
                        atr_mamode = self.atr_mamode,
                        atr_multiplier = self.atr_multiplier)
        return self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        
        df:pd.DataFrame = self._candles.get_df()
        
        long_stoploss,short_stoploss,Uptrend,Downtrend = self.calculate(df)
        
        _len = min([len(long_stoploss),len(short_stoploss),len(Uptrend), len(Downtrend)])
        
        _index = df["index"]
        self.df = pd.DataFrame({
                            'index':_index.tail(_len),
                            "long_stoploss":long_stoploss.tail(_len),
                            "short_stoploss":short_stoploss.tail(_len),
                            "Uptrend":Uptrend.tail(_len),
                            "Downtrend":Downtrend.tail(_len),
                            })
        
        
        self.xdata,self.long_stoploss,self.short_stoploss,self.Uptrend,self.Downtrend = self.df["index"].to_numpy(),\
                                                                                    self.df["long_stoploss"].to_numpy(),\
                                                                                    self.df["short_stoploss"].to_numpy(),\
                                                                                    self.df["Uptrend"].to_numpy(),\
                                                                                    self.df["Downtrend"].to_numpy()
                                                                                        
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
        candle_df = self._candles.get_df()
        df:pd.DataFrame = candle_df.head(-_pre_len)
        
        long_stoploss,short_stoploss,Uptrend,Downtrend = self.calculate(df)
        
        _len = min([len(long_stoploss),len(short_stoploss),len(Uptrend), len(Downtrend)])
        
        _index = df["index"]
        
        _df = pd.DataFrame({
                            'index':_index.tail(_len),
                            "long_stoploss":long_stoploss.tail(_len),
                            "short_stoploss":short_stoploss.tail(_len),
                            "Uptrend":Uptrend.tail(_len),
                            "Downtrend":Downtrend.tail(_len),
                            })

        self.df = pd.concat([_df,self.df],ignore_index=True)        
        
        self.xdata = np.concatenate((_df["index"].to_numpy(), self.xdata)) 
        self.long_stoploss = np.concatenate((_df["long_stoploss"].to_numpy(), self.long_stoploss)) 
        self.short_stoploss = np.concatenate((_df["short_stoploss"].to_numpy(), self.short_stoploss)) 
        self.Uptrend = np.concatenate((_df["Uptrend"].to_numpy(), self.Uptrend)) 
        self.Downtrend = np.concatenate((_df["Downtrend"].to_numpy(), self.Downtrend)) 
        
        
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
            df:pd.DataFrame = self._candles.get_df(self.slow_period*5)
            
            long_stoploss,short_stoploss,Uptrend,Downtrend = self.calculate(df)
        
            # _len = min([len(long_stoploss),len(short_stoploss),len(Uptrend), len(Downtrend)])
            
            # _index = df["index"]
            
            new_frame = pd.DataFrame({
                                'index':[new_candle.index],
                                "long_stoploss":[long_stoploss.iloc[-1]],
                                "short_stoploss":[short_stoploss.iloc[-1]],
                                "Uptrend":[Uptrend.iloc[-1]],
                                "Downtrend":[Downtrend.iloc[-1]],
                                })
            
            self.df = pd.concat([self.df,new_frame],ignore_index=True)
            
            self.xdata = np.concatenate((self.xdata,np.array([new_candle.index])))
            self.long_stoploss = np.concatenate((self.long_stoploss,np.array([long_stoploss.iloc[-1]])))
            self.short_stoploss = np.concatenate((self.short_stoploss,np.array([short_stoploss.iloc[-1]])))
            self.Uptrend = np.concatenate((self.Uptrend,np.array([Uptrend.iloc[-1]])))
            self.Downtrend = np.concatenate((self.Downtrend,np.array([Downtrend.iloc[-1]])))
    
            self.sig_add_candle.emit()
        #self.is_current_update = True
        
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(self.slow_period*5)
            long_stoploss,short_stoploss,Uptrend,Downtrend = self.calculate(df)
            self.df.iloc[-1] = [new_candle.index,long_stoploss.iloc[-1],short_stoploss.iloc[-1],Uptrend.iloc[-1],Downtrend.iloc[-1]]
            self.xdata[-1],self.long_stoploss[-1],self.short_stoploss[-1],self.Uptrend[-1] ,self.Downtrend[-1] = new_candle.index,long_stoploss.iloc[-1],short_stoploss.iloc[-1],Uptrend.iloc[-1],Downtrend.iloc[-1]

            self.sig_update_candle.emit()
        #self.is_current_update = True
            
            
