import numpy as np
import pandas as pd
import pandas_ta as ta

# Define input parameters


"""
    // This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © BobRivera990
 
//@version=4
study(title = "Trend Type Indicator by BobRivera990", overlay = false)
//==========================================================================[Inputs]==========================================================================
useAtr = input(true, title = "Use ATR to detect Sideways Movements")            // Use Average True Range (ATR) to detect Sideways Movements

atrLen = input(14, minval = 1, title = "ATR Length")                            // length of the Average True Range (ATR) used to detect Sideways Movements

atrMaType = input("SMA", options = ["SMA", "EMA"], 
     title = "ATR Moving Average Type")                                         // Type of the moving average of the ATR used to detect Sideways Movements
atrMaLen = input(20, minval = 1, title = "ATR MA Length")                       // length of the moving average of the ATR used to detect Sideways Movements

useAdx = input(true, title = "Use ADX to detect Sideways Movements")            // Use Average Directional Index (ADX) to detect Sideways Movements

adxLen = input(14, minval = 1, maxval = 50, title = "ADX Smoothing")            // length of the Average Directional Index (ADX) used to detect Sideways Movements
diLen = input(14, minval = 1, title = "DI Length")                              // length of the Plus and Minus Directional Indicators (+DI & -DI) used to determine the direction of the trend
adxLim = input(25, minval = 1, title = "ADX Limit")                             // A level of ADX used as the boundary between Trend Market and Sideways Market

smooth = input(3, minval = 1, maxval = 5, title = "Smoothing Factor")           // Factor used for smoothing the oscillator
lag = input(8, minval = 0, maxval = 15, title = "Lag")                          // lag used to match indicator and chart
//============================================================================================================================================================
//===================================================================[Initial Calculations]===================================================================

atr = atr(atrLen)                                                               // Calculate the Average True Range (ATR)
atrMa = atrMaType == "EMA" ? ema(atr, atrMaLen) : sma(atr, atrMaLen)            // Calculate the moving average of the ATR

up = change(high)                                                               // Calculate parameter related to ADX, +DI and -DI
down = -change(low)                                                             // Calculate parameter related to ADX, +DI and -DI          
plusDM = na(up) ? na : (up > down and up > 0 ? up : 0)                          // Calculate parameter related to ADX, +DI and -DI
minusDM = na(down) ? na : (down > up and down > 0 ? down : 0)                   // Calculate parameter related to ADX, +DI and -DI
trur = rma(tr, diLen)                                                           // Calculate parameter related to ADX, +DI and -DI
plus = fixnan(100 * rma(plusDM, diLen) / trur)                                  // Calculate Plus Directional Indicator (+DI)
minus = fixnan(100 * rma(minusDM, diLen) / trur)                                // Calculate Minus Directional Indicator (-DI)
sum = plus + minus                                                              // Calculate parameter related to ADX

adx = 100 * rma(abs(plus - minus) / (sum == 0 ? 1 : sum), adxLen)               // Calculate Average Directional Index (ADX)
//============================================================================================================================================================
//========================================================================[Conditions]========================================================================

cndNa = na(atr) or na(adx) or na(plus) or na(minus) or na(atrMaLen)             // Conditions for lack of sufficient data for calculations

cndSidwayss1 = useAtr and atr <= atrMa                                                     // Sideways Movement condition (based on ATR)
cndSidwayss2 = useAdx and adx <= adxLim                                                    // Sideways Movement condition (based on ADX)
cndSidways = cndSidwayss1 or cndSidwayss2                                       // General Sideways Movement condition

cndUp = plus > minus                                                            // uptrend condition
cndDown = minus >= plus                                                         // downtrend condition

trendType  = cndNa ? na : cndSidways ? 0 : cndUp ? 2 : -2                       // Determine the type of trend
smoothType = na(trendType) ? na : round(sma(trendType, smooth) / 2) * 2         // Calculate the smoothed trend type oscillator
//============================================================================================================================================================
//=========================================================================[Drawing]==========================================================================

colGreen30 = color.new(color.green, 30)                                         // Define the color used in the drawings
colGreen90 = color.new(color.green, 90)                                         // Define the color used in the drawings
colGray = color.new(color.gray, 20)                                             // Define the color used in the drawings      
colWhite90 = color.new(color.white, 90)                                         // Define the color used in the drawings
colRed30 = color.new(color.red, 30)                                             // Define the color used in the drawings
colRed90 = color.new(color.red, 90)                                             // Define the color used in the drawings

band3 = plot(+3, title = "Band_3", color=color.black)                           // Draw the upper limit of the uptrend area
band2 = plot(+1, title = "Band_2", color=color.black)                           // Draw the boundary between Sideways and Uptrend areas
band1 = plot(-1, title = "Band_1", color=color.black)                           // Draw the boundary between Sideways and Downtrend areas
band0 = plot(-3, title = "Band_0", color=color.black)                           // Draw the lower limit of the downtrend area

fill(band2, band3, title = "Uptrend area", color = colGreen90)                  // Highlight the Uptrend area
fill(band1, band2, title = "Sideways area", color = colWhite90)                 // Highlight the Sideways area
fill(band0, band1, title = "Downtrend area", color = colRed90)                  // Highlight the Downtrend area

var label lblUp = na
label.delete(lblUp)
lblUp := label.new(x = time, y = 2, text = "UP", 
     color = color.new(color.green, 100), textcolor = color.black, 
     style = label.style_label_left, xloc = xloc.bar_time, 
     yloc = yloc.price, size=size.normal, textalign = text.align_left)          // Show Uptrend area label

var label lblSideways = na
label.delete(lblSideways)
lblSideways := label.new(x = time, y = 0, text = "SIDEWAYS", 
     color = color.new(color.green, 100), textcolor = color.black, 
     style = label.style_label_left, xloc = xloc.bar_time, 
     yloc = yloc.price, size = size.normal, textalign = text.align_left)        // Show Sideways area label
     
var label lblDown = na
label.delete(lblDown)
lblDown := label.new(x = time, y = -2, text = "DOWN", 
     color = color.new(color.green, 100), textcolor = color.black, 
     style = label.style_label_left, xloc = xloc.bar_time, 
     yloc = yloc.price, size = size.normal, textalign = text.align_left)        // Show Downtrend area label

var label lblCurrentType = na
label.delete(lblCurrentType)
lblCurrentType := label.new(x = time, y = smoothType, 
     color = color.new(color.blue, 30), style = label.style_label_right,
     xloc = xloc.bar_time, yloc = yloc.price, size = size.small)                // Show the latest status label

trendCol = smoothType == 2 ? colGreen30 : smoothType == 0 ? colGray : colRed30  // Determine the color of the oscillator in different conditions

plot(smoothType, title = "Trend Type Oscillator", color = trendCol, 
     linewidth = 3, offset = -lag, style = plot.style_stepline)                 // Draw the trend type oscillator
"""

def trend_type_indicator(df,
                        use_atr = True,
                        atr_length = 14,
                        atr_ma_type = "SMA",
                        atr_ma_len = 20,
                        use_adx = True,
                        adx_len = 14,
                        adx_limit = 25,
                        smoothing = 3,
                        lag = 8):
    """
    Implements the Trend Type Indicator by BobRivera990.
    :param df: DataFrame with columns ['open', 'high', 'low', 'close']
    :return: DataFrame with calculated trend type and smoothed trend type.
    """
    # Calculate ATR and its moving average
    df['atr'] = ta.atr(high=df['high'], low=df['low'], close=df['close'], length=atr_length,talib= False)
    if atr_ma_type == "EMA":
        df['atr_ma'] = ta.ema(df['atr'], atr_ma_len,talib= False)
    elif atr_ma_type == "SMA":
        df['atr_ma'] = ta.sma(df['atr'], atr_ma_len,talib= False)
    else:
        raise ValueError("Unsupported ATR MA Type")

    # Calculate ADX and DI
    adx_df = ta.adx(high=df['high'], low=df['low'], close=df['close'], length=adx_len,talib= False)
    df['plus_di'] = adx_df['DMP_14']  # +DI
    df['minus_di'] = adx_df['DMN_14']  # -DI
    df['adx'] = adx_df['ADX_14']  # ADX

    # Handle NaN values
    df['plus_di'] = df['plus_di'].fillna(0)
    df['minus_di'] = df['minus_di'].fillna(0)
    df['adx'] = df['adx'].fillna(0)

    # Determine sideways movement conditions
    df['sideways_atr'] = (df['atr'] <= df['atr_ma']) if use_atr else False
    df['sideways_adx'] = (df['adx'] <= adx_limit) if use_adx else False
    df['sideways'] = df['sideways_atr'] | df['sideways_adx']

    # Determine trend conditions
    df['trend_up'] = df['plus_di'] > df['minus_di']
    df['trend_down'] = df['minus_di'] >= df['plus_di']

    # Calculate trend type
    df['trend_type'] = np.where(df['sideways'], 0,
                                np.where(df['trend_up'], 2,
                                         np.where(df['trend_down'], -2, np.nan)))

    # Smooth the trend type
    df['smooth_trend_type'] = ta.sma(df['trend_type'], smoothing) / 2
    df['smooth_trend_type'] = df['smooth_trend_type'].round() * 2

    # Shift the trend type for lag
    df['smooth_trend_type_lagged'] = df['smooth_trend_type'].shift(lag)

    return df[['atr', 'atr_ma', 'adx', 'plus_di', 'minus_di', 'trend_type', 'smooth_trend_type', 'smooth_trend_type_lagged']]


import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject

class AllCandlePattern(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int) 
    def __init__(self,_candles,dict_ta_params:dict={}) -> None:
        super().__init__(parent=None)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"ALL CDL PATTERN"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool

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
        if len(self.df) == 0:
            return []
        if start == 0 and stop == 0:
            df=self.df
        elif start == 0 and stop != 0:
            df=self.df.iloc[:stop]
        elif start != 0 and stop == 0:
            df=self.df.iloc[start:]
        else:
            df=self.df.iloc[start:stop]
        return df
    
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
        column_names = INDICATOR.columns.tolist()
        
        vortex_name = ''
        signalma_name = ''
        
        patterns = ['doji', 'evening_star', 'morning_star', 'shooting_star', 'hammer', 'inverted_hammer', 'bearish_harami', 
            'bullish_harami', 'bearish_engulfing', 'bullish_engulfing', 'piercing_line', 'bullish_belt', 
            'bullish_kicker', 'bearish_kicker', 'hanging_man', 'dark_cloud_cover']
        
        
        for name in column_names:
            if name.__contains__("VTXP_"):
                vortex_name = name
            elif name.__contains__("VTXM_"):
                signalma_name = name

        vortex_ = INDICATOR[vortex_name].dropna().round(6)
        signalma = INDICATOR[signalma_name].dropna().round(6)
        
        return vortex_,signalma
    
    def calculate(self,df: pd.DataFrame):
        INDICATOR = candle_pattern(df)
        return INDICATOR#self.paire_data(INDICATOR)
    
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        
        self.df = self.calculate(df)
        
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
        
        _df= self.calculate(df)
        _len = len(_df)
        self.df = pd.concat([_df,self.df],ignore_index=True)
        
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
            df:pd.DataFrame = self._candles.get_df(10)
            _df:pd.DataFrame  = self.calculate(df)
            
            _new_df = _df.iloc[[-1]]
            
            # print(type(_new_df),_new_df)
            
            self.df = pd.concat([self.df,_new_df],ignore_index=True)
            self.sig_add_candle.emit()
        #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(10)
            _df = self.calculate(df)
            self.df.iloc[-1] = _df.iloc[-1]
            self.sig_update_candle.emit()
        #self.is_current_update = True
           
