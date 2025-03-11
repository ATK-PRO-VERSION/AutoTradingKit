

import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF,QPointF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem

from atklip.controls import PD_MAType,IndicatorType,UTBOT_ALERT,UTBOT_ALERT_WITH_BB
from atklip.graphics.chart_component.draw_tools.base_arrow import BaseArrowItem
from atklip.graphics.chart_component.draw_tools.entry import Entry

from atklip.appmanager import FastWorker
from atklip.app_utils import *
from atklip.controls.candle.n_time_smooth_candle import N_SMOOTH_CANDLE
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.trend.zigzag import ZIGZAG
from atklip.controls.momentum.macd import MACD
from atklip.controls.momentum.rsi import RSI
from atklip.controls.tradingview import SuperTrendWithStopLoss, EMA_TREND_METTER
from atklip.controls.models import (UTBOTWITHBBModel, MACDModel, MAModel, 
                                    RSIModel,SQeezeModel,SuperTrendModel, 
                                    SuperWithSlModel, TrendWithStopLossModel,
                                    EMATRENDMETTERModel)

from atklip.graphics.pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

class EMA_SUPER_TREND_BOT(GraphicsObject):
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart) -> None:
        # super().__init__()
        GraphicsObject.__init__(self)
        # self.setFlag(self.GraphicsItemFlag.ItemHasNoContents)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        
        self.chart:Chart = chart
        self.has = {
            "name": f"UTBOT Alert",
            "y_axis_show":False,
            
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    
                    #Super Trend ATR
                    "supertrend_length" :14,
                    "supertrend_atr_length":14,
                    "supertrend_multiplier" :3,
                    "supertrend_atr_mamode" :PD_MAType.RMA, 
                    "atr_length" : 14,
                    "atr_mamode" :PD_MAType.RMA, 
                    "atr_multiplier" : 1,
                    
                    #RSI
                    "rsi_type":"close",
                    "rsi_indicator_type":IndicatorType.RSI,
                    "rsi_period":14,
                    "rsi_mamode":PD_MAType.RMA,
                    
                    #EMA TREND METTER
                    "base_ema_length":3,
                    "ema_length_1":21,
                    "ema_length_2":34,
                    "ema_length_3":55,
                    
                    #UTBOT
                    "key_value":1,
                    "atr_utbot_length":10,
                    "mult":1,
                    "wicks":False,
                    "band_type":"Bollinger Bands",
                    "atr_length":10,
                    "channel_length":10,
                    
                    "indicator_type":IndicatorType.BUY_SELL_WITH_ETM_ST,
                    "show":False},

            "styles":{
                    }
                    }
        
        self.id = self.chart.objmanager.add(self)
        
        self.list_pos:dict = {}
        self.picture: QPicture = QPicture()

        self.INDICATOR  = N_SMOOTH_CANDLE(self.chart.get_precision(),self.chart.heikinashi,3,"ema",3)
        
        self.supertrend = SuperTrendWithStopLoss(self.INDICATOR, self.supertmodel.__dict__)
        
        self.cr_trend = None
        self.his_cr_trend = None
        
        self.ema_trend_metter = EMA_TREND_METTER(self.INDICATOR, self.ema_trend_metter_model.__dict__)
                
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    @property
    def is_all_updated(self):
        is_updated = self.INDICATOR.is_current_update and self.ema_trend_metter.is_current_update and self.supertrend.is_current_update
        return is_updated
    
    @property
    def id(self):
        return self.chart_id
    
    @id.setter
    def id(self,_chart_id):
        self.chart_id = _chart_id

    @property
    def ema_trend_metter_model(self) -> dict:
        return EMATRENDMETTERModel(self.id,"EMA TREND METTER",self.has["inputs"]["source"].source_name,
                        self.has["inputs"]["base_ema_length"],
                        self.has["inputs"]["ema_length_1"],
                        self.has["inputs"]["ema_length_2"],
                        self.has["inputs"]["ema_length_3"])
    @property
    def rsi_model(self) -> dict:
        return RSIModel(self.id,"RSI",self.has["inputs"]["source"].source_name,
                        self.has["inputs"]["rsi_type"],
                        self.has["inputs"]["rsi_period"],
                        self.has["inputs"]["rsi_mamode"].name.lower())
    
    @property
    def supertmodel(self) -> dict:
        return SuperWithSlModel(self.id,"SuperTrend",self.chart.jp_candle.source_name,
                    self.has["inputs"]["supertrend_length"],
                    self.has["inputs"]["supertrend_atr_length"],
                    self.has["inputs"]["supertrend_multiplier"],
                    self.has["inputs"]["supertrend_atr_mamode"].name.lower(),
                    self.has["inputs"]["atr_length"],
                    self.has["inputs"]["atr_mamode"].name.lower(),
                    self.has["inputs"]["atr_multiplier"]
                    )
    
    @property
    def model(self) -> dict:
        return UTBOTWITHBBModel(self.id,"UTBOT_WITH_BB",self.has["inputs"]["source"].source_name,
                                self.has["inputs"]["atr_length"],
                                self.has["inputs"]["channel_length"],
                                self.has["inputs"]["key_value"],
                                self.has["inputs"]["atr_utbot_length"],
                                self.has["inputs"]["mult"],
                                self.has["inputs"]["wicks"],
                                self.has["inputs"]["band_type"]
                                )
    
    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.add_worker)
            self.INDICATOR.signal_delete.disconnect(self.replace_source)
            self.INDICATOR.sig_add_historic.disconnect(self.add_historic_worker)
                        
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.INDICATOR.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.signal_delete.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
            
    def fisrt_gen_data(self):
        self.connect_signals()
        self.INDICATOR.fisrt_gen_data()
        self.supertrend.fisrt_gen_data()
        # self.rsi.fisrt_gen_data()
        self.ema_trend_metter.fisrt_gen_data()
    
    def check_pivot_points(self,df:pd.DataFrame,_type:str="high",n = 10, m=20):
        _len = len(df)
        # print(df)   
        if _type == "high":
            for i in range(n):  
                if _len - i - m > 0:  
                    array = df.iloc[_len-i - m:_len-i][_type].to_numpy()
                    index = df.iloc[_len-i - m:_len-i]["index"].to_numpy()
                    max_previous_m = array.max()  
                    
                    if array[-1] >= max_previous_m: 
                        # print(True, array[-1], index[-1])
                        return (True, array[-1], index[-1])
            
        elif _type == "low":
            for i in range(n):  
                if _len - i - m > 0:  
                    array = df.iloc[_len-i - m:_len-i][_type].to_numpy()
                    index = df.iloc[_len-i - m:_len-i]["index"].to_numpy()
                    min_previous_m = array.min()   
                         
                    if array[-1] <= min_previous_m: 
                        # print(True, array[-1], index[-1]) 
                        return (True, array[-1], index[-1])
        return (False, None, None)

    def check_active_pos(self,_type:str,_open: float):
        if self.list_pos:
            for x in self.list_pos.keys():
                entry_infor:dict = self.list_pos[x]
                is_entry_closed =  entry_infor["is_stoploss"]
                is_take_profit_2R =  entry_infor["take_profit_2R"]
                is_take_profit_1_5R =  entry_infor["take_profit_1_5R"]
                
                entry_type = entry_infor["type"]
                entry:Entry = entry_infor["entry"]
                
                if entry_type == _type:
                    if not is_entry_closed and not is_take_profit_2R:
                        # self.list_pos[x]["is_stoploss"] = _open
                        # entry.locked_handle()
                        return True
        return False
                        
    def delete(self):        
        self.disconnect_signals()
        self.INDICATOR.disconnect()
        self.INDICATOR.deleteLater()
        # self.macd.deleteLater()
        # self.super_smoothcandle.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        df= self.INDICATOR.get_df()
        setdata.emit(df)
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"Trend metter + Supertrend"
        self.sig_change_indicator_name.emit(self.has["name"])
        
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
    def reset_threadpool_asyncworker(self):
        self.reset_indicator()
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
      
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "key_value":self.has["inputs"]["key_value"],
                    "atr_utbot_length":self.has["inputs"]["atr_utbot_length"],
                    "mult":self.has["inputs"]["mult"],
                    "wicks":self.has["inputs"]["wicks"],
                    "band_type":self.has["inputs"]["band_type"],
                    "atr_length":self.has["inputs"]["atr_length"],
                    "channel_length":self.has["inputs"]["channel_length"],
                    }
        return inputs
    
    def get_styles(self):
        styles =  {
                    }
        return styles
    
    def update_inputs(self,_input,_source):
        is_update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.INDICATOR.change_input(self.has["inputs"]["source"])
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        
        if is_update:
            self.has["name"] = f"UTBOT_WITH_BB"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_input(self.has["inputs"]["source"])
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
    
    def get_xaxis_param(self):
        return None,"#363a45"

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def calculate_stop_loss(self,_type:str, price:float):
        return calculate_stoploss(_type,price,0.0)
            
    
    def check_n_long_short_pos(self,is_new: bool=True,_type:str="long",n:int=5):
        sorted_pos = sorted(list(self.list_pos.keys()))
        if len(sorted_pos) == 0:
            return False
        if len(sorted_pos) < n:
            pos =  sorted_pos[:n][::-1]
        if is_new:
            pos =  sorted_pos[-n:][::-1]
        else:
            pos =  sorted_pos[:n][::-1]
        if pos:
            for i in pos:
                # print(self.list_pos[i]["type"],_type )
                if self.list_pos[i]["type"] != _type:
                    return False
        return True
    
    def move_entry(self,index: float, high: float,low: float):
        """
        self.list_pos[pivot_point[2]] = {"stop_loss":pivot_point[1],"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, 
        "entry":entry, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}"""
        if self.list_pos:
            for x in self.list_pos.keys():
                entry_infor:dict = self.list_pos[x]
                is_entry_closed =  entry_infor["is_stoploss"]
                is_take_profit_2R =  entry_infor["take_profit_2R"]
                is_take_profit_1_5R =  entry_infor["take_profit_1_5R"]
                
                entry_type = entry_infor["type"]
                
                stoploss = entry_infor["stop_loss"]
                
                entry:Entry = entry_infor["entry"]
                
                
                
                if is_entry_closed or is_take_profit_2R:
                    continue
                
                entry_pos_1_5R:QPointF = entry.has["inputs"]["data"][2.5].chart_pos
                entry_pos_2R:QPointF = entry.has["inputs"]["data"][3].chart_pos
                
                
                profit_2R = entry_pos_2R.y()
                profit_1_5R = entry_pos_1_5R.y()
                
                if entry_type == "long":
                    if not is_take_profit_1_5R:
                        if profit_1_5R <= high:
                            self.list_pos[x]["take_profit_1_5R"] = profit_1_5R
                    if not is_take_profit_2R:
                        if profit_2R <= high:
                            self.list_pos[x]["take_profit_2R"] = profit_2R
                    if stoploss >= low:
                        self.list_pos[x]["is_stoploss"] = True
                elif entry_type == "short":
                    if not is_take_profit_1_5R:
                        if profit_1_5R >= low:
                            self.list_pos[x]["take_profit_1_5R"] = profit_1_5R
                    if not is_take_profit_2R:
                        if profit_2R >= low:
                            self.list_pos[x]["take_profit_2R"] = profit_2R
                    if stoploss <= high:
                        self.list_pos[x]["is_stoploss"] = True
                
                is_entry_closed =  self.list_pos[x]["is_stoploss"]
                is_take_profit_2R =  self.list_pos[x]["take_profit_2R"]
                
                entry_y = self.list_pos[x]["entry_y"]
                self.list_pos[x]["entry_x"] = index
                entry.moveEntry(index,entry_y)
                
                if is_entry_closed or is_take_profit_2R:
                    entry.locked_handle()
                    
    
    def set_Data(self,df):
        if self.list_pos:
            for obj in self.list_pos.values():
                if self.scene() is not None:
                    self.scene().removeItem(obj["obj"])
                    if hasattr(obj["obj"], "obj"):
                        obj["obj"].deleteLater()
        self.list_pos.clear()        
        for i in range(1,len(df)):
            _x = df.iloc[i]['index']
            
            supertrenddf = self.supertrend.df.loc[self.supertrend.df['index'] == _x-1]
            SUPERTd = 0
            if not supertrenddf.empty:
                SUPERTd = supertrenddf.iloc[-1]["SUPERTd"]
            
            pre_jp_cdl = self.chart.jp_candle.map_index_ohlcv[_x-1]
            
            pre_cdl_type = "green" if pre_jp_cdl.close > pre_jp_cdl.open else "red"
            
            ema_trend_metterdf = self.ema_trend_metter.df.loc[self.ema_trend_metter.df['index'] == _x-1]
            uptrend = False
            downtrend = False
            if not ema_trend_metterdf.empty:
                uptrend = ema_trend_metterdf.iloc[-1]["uptrend"]
                downtrend = ema_trend_metterdf.iloc[-1]["downtrend"]
            
            trend = not uptrend and not downtrend
            
            # if df.iloc[i-1]['long'] == True and trend and SUPERTd>0 :# and 20<rsidata
            if trend and SUPERTd>0  and pre_cdl_type== "red":#  and self.cr_trend == "up"
                _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                obj = BaseArrowItem(drawtool=self.chart.drawtool,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                obj.setParentItem(self)
                obj.setPos(_x, _val)
                obj.locked_handle()
                self.list_pos[_x] = {"type":"long","obj":obj}
                
            elif trend and SUPERTd<0 and pre_cdl_type== "green":#   and self.cr_trend == "down"
                _val = self.chart.jp_candle.map_index_ohlcv[_x].high
                obj =  BaseArrowItem(drawtool=self.chart.drawtool,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                obj.setParentItem(self)
                obj.locked_handle()
                obj.setPos(_x, _val)
                self.list_pos[_x] = {"type":"short","obj":obj}
            
            if uptrend:
                self.cr_trend = "up"
            elif downtrend:
                self.cr_trend = "down"
            else:
                self.cr_trend = "sideway"
    
    def add_historic_Data(self,df):
        for i in range(1,len(df)):
            _x = df.iloc[i]['index']
            if self.list_pos.get(_x):
                continue
            
            supertrenddf = self.supertrend.df.loc[self.supertrend.df['index'] == _x-1]
            SUPERTd = 0
            if not supertrenddf.empty:
                SUPERTd = supertrenddf.iloc[-1]["SUPERTd"]
            
            pre_jp_cdl = self.chart.jp_candle.map_index_ohlcv[_x-1]
            
            pre_cdl_type = "green" if pre_jp_cdl.close > pre_jp_cdl.open else "red"
            
            ema_trend_metterdf = self.ema_trend_metter.df.loc[self.ema_trend_metter.df['index'] == _x-1]
            uptrend = False
            downtrend = False
            if not ema_trend_metterdf.empty:
                uptrend = ema_trend_metterdf.iloc[-1]["uptrend"]
                downtrend = ema_trend_metterdf.iloc[-1]["downtrend"]

            trend = not uptrend and not downtrend
            
            # if df.iloc[i-1]['long'] == True and trend and SUPERTd>0:# and 20<rsidata
            if trend and SUPERTd>0 and pre_cdl_type== "red":#  and self.cr_trend == "up"
                _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                obj = BaseArrowItem(drawtool=self.chart.drawtool,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                obj.setParentItem(self)
                obj.setPos(_x, _val)
                obj.locked_handle()
                self.list_pos[_x] = {"type":"long","obj":obj}
                
            # elif df.iloc[i-1]['short'] == True and trend and SUPERTd<0:# and rsidata<80
            elif trend and SUPERTd<0  and pre_cdl_type== "green":#  and self.cr_trend == "down"
                _val = self.chart.jp_candle.map_index_ohlcv[_x].high
                obj =  BaseArrowItem(drawtool=self.chart.drawtool,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                obj.setParentItem(self)
                obj.locked_handle()
                obj.setPos(_x, _val)
                self.list_pos[_x] = {"type":"short","obj":obj}

            if uptrend:
                self.his_cr_trend = "up"
            elif downtrend:
                self.his_cr_trend = "down"
            else:
                self.cr_trend = "sideway"
    def update_Data(self,df):
        _x = df.iloc[-1]['index']
        
        if self.list_pos.get(_x):
                return

        supertrenddf = self.supertrend.df.loc[self.supertrend.df['index'] == _x-1]
        SUPERTd = 0
        if not supertrenddf.empty:
            SUPERTd = supertrenddf.iloc[-1]["SUPERTd"]
        
        pre_jp_cdl = self.chart.jp_candle.map_index_ohlcv[_x-1]
            
        pre_cdl_type = "green" if pre_jp_cdl.close > pre_jp_cdl.open else "red"
        
        ema_trend_metterdf = self.ema_trend_metter.df.loc[self.ema_trend_metter.df['index'] == _x-1]
        uptrend = False
        downtrend = False
        if not ema_trend_metterdf.empty:
            uptrend = ema_trend_metterdf.iloc[-1]["uptrend"]
            downtrend = ema_trend_metterdf.iloc[-1]["downtrend"]
        trend = not uptrend and not downtrend

        # if df.iloc[-2]['long'] == True and trend and SUPERTd>0 :# and 20<rsidata
        if trend and SUPERTd>0 and pre_cdl_type== "red":# and self.cr_trend == "up" 
            _val = self.chart.jp_candle.map_index_ohlcv[_x].low
            obj = BaseArrowItem(drawtool=self.chart.drawtool,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
            obj.setParentItem(self)
            obj.setPos(_x, _val)
            obj.locked_handle()
            self.list_pos[_x] = {"type":"long","obj":obj}
            
        # elif df.iloc[-2]['short'] == True and trend and SUPERTd<0:# and rsidata<80 
        elif trend and SUPERTd<0 and pre_cdl_type== "green":# or self.cr_trend == "down"
            _val = self.chart.jp_candle.map_index_ohlcv[_x].high
            obj =  BaseArrowItem(drawtool=self.chart.drawtool,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
            obj.setParentItem(self)
            obj.locked_handle()
            obj.setPos(_x, _val)
            self.list_pos[_x] = {"type":"short","obj":obj}
        if uptrend:
            self.cr_trend = "up"
        elif downtrend:
            self.cr_trend = "down"
        else:
            self.cr_trend = "sideway"
    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.update_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()  
    
    def add_historic_worker(self,_len):
        self.worker = None
        self.worker = FastWorker(self.load_historic_data,_len)
        self.worker.signals.setdata.connect(self.add_historic_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start() 
    
    def add_worker(self):
        self.worker = None
        self.worker = FastWorker(self.add_data)
        self.worker.signals.setdata.connect(self.update_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()    
    
    def load_historic_data(self,_len,setdata):
        df= self.INDICATOR.get_head_df(_len)
        setdata.emit(df)
        
    def add_data(self,setdata):
        df= self.INDICATOR.get_tail_df(10)
        setdata.emit(df)
    
    def update_data(self,setdata):
        df= self.INDICATOR.get_tail_df(10)
        setdata.emit(df)

    def boundingRect(self) -> QRectF:
        if self.list_pos:
            x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
            for _x in list(self.list_pos.keys()):
                obj = self.list_pos.get(_x)
                if obj:
                    if x_left < _x < x_right:
                        obj["obj"].show()
                    else:
                        obj["obj"].hide()

        return self.picture.boundingRect()
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
        # p.drawRect(self.boundingRect())
    
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return None,None
    
    def get_last_point(self):
        return None,None
    
    def get_min_max(self):
        return None,None
        try:
            _min, _max = np.nanmin(self.lowline.yData), np.nanmax(self.highline.yData)
            # if y_data.__len__() > 0:
            #     _min = y_data.min()
            #     _max = y_data.max()
            return _min,_max
        except Exception as e:
            pass
        time.sleep(0.1)
        self.get_min_max()
        return _min,_max

    def on_click_event(self):
        #print("zooo day__________________")
        pass

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mousePressEvent(ev)

    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name
    