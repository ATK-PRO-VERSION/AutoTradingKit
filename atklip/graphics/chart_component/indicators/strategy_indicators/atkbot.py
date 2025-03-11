import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF,QPointF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.controls.candle.candle import JAPAN_CANDLE
from atklip.controls.candle.heikinashi import HEIKINASHI
from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem
from atklip.graphics.pyqtgraph import GraphicsObject

from atklip.controls import PD_MAType,IndicatorType,UTBOT_ALERT
from atklip.controls.models import ATKBOTModel, MACDModel, MAModel, RSIModel,SQeezeModel,SuperTrendModel, SuperWithSlModel, TrendWithStopLossModel
from atklip.graphics.chart_component.draw_tools.base_arrow import BaseArrowItem
from atklip.graphics.chart_component.draw_tools.TargetItem import ArrowItem
from atklip.graphics.chart_component.draw_tools.entry import Entry

from atklip.appmanager import FastWorker
from atklip.app_utils import *
from atklip.controls.candle import N_SMOOTH_CANDLE, SMOOTH_CANDLE
from atklip.controls.ma import MA, ma
from atklip.controls.trend.zigzag import ZIGZAG
from atklip.controls.momentum.macd import MACD
from atklip.controls.momentum.rsi import RSI
from atklip.controls import  SQEEZE
from atklip.controls import SuperTrend
from atklip.controls import AllCandlePattern
from atklip.graphics.pyqtgraph.Point import Point
from atklip.graphics.pyqtgraph.graphicsItems.TextItem import TextItem
from atklip.controls.tradingview.trend_with_stop_loss import TrendWithStopLoss

from atklip.controls.tradingview import SuperTrendWithStopLoss


from atklip.controls.tradingview.custom_utbot import CUSTOM_UTBOT_ALERT
from atklip.controls.models import UTBOTModel
from atklip.controls.strategies.base_strategy import StrategyBase
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

class ATKBOT(GraphicsObject):
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
        self.setFlag(self.GraphicsItemFlag.ItemHasNoContents)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        
        self.chart:Chart = chart
        self.has = {
            "name": f"Strategy SuperTrend_UTBot",
            "y_axis_show":False,
            
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    
                    # UT BOT
                    "key_value_long":1,
                    "key_value_short":1,
                    "atr_long_period":10,
                    "ema_long_period":1,
                    "atr_short_period":10,
                    "ema_short_period":1,
                    
                    #Super Trend ATR
                    "supertrend_length" :14,
                    "supertrend_atr_length":14,
                    "supertrend_multiplier" :3.0,
                    "supertrend_atr_mamode" :PD_MAType.RMA, 
                    "atr_length" : 14,
                    "atr_mamode" :PD_MAType.RMA, 
                    "atr_multiplier" : 1,
                    
                    #Trend vs stoploss
                    "trend_fast_period" :12,
                    "trend_slow_period" :26,
                    "trend_signal_period" :9,
                    "trend_atr_length" :14, 
                    "trend_atr_mamode" :PD_MAType.RMA, 
                    "trend_atr_multiplier":0.5, 
                    
                    #RSI
                    "rsi_type":"close",
                    "rsi_indicator_type":IndicatorType.RSI,
                    "rsi_period":14,
                    "rsi_mamode":PD_MAType.RMA,
                    
                    #RSIFast
                    "rsi_fast_type":"close",
                    "rsi_fast_indicator_type":IndicatorType.RSI,
                    "rsi_fast_period":2,
                    "rsi_fast_mamode":PD_MAType.RMA,
                    
                    #MAfast
                    "mafast_type":"close",
                    "mafast_mamode":PD_MAType.EMA,
                    "mafast_length":3,
                    
                    #MAslow
                    "maslow_type":"close",
                    "maslow_mamode":PD_MAType.EMA,
                    "maslow_length":30,
                    
                    "show":False},

            "styles":{
                    'pen_high_line': "green",
                    'width_high_line': 1,
                    'style_high_line': Qt.PenStyle.SolidLine,
                    
                    'pen_center_line': "orange",
                    'width_center_line': 1,
                    'style_center_line': Qt.PenStyle.SolidLine,
                    
                    'pen_low_line': "red",
                    'width_low_line': 1,
                    'style_low_line': Qt.PenStyle.SolidLine,
                    
                    "brush_color": mkBrush('#3f3964',width=0.7),
                    }
                    }
        
        self.id = self.chart.objmanager.add(self)
        
        self.list_pos:dict = {}
        self.picture: QPicture = QPicture()
        self.cr_position:dict = {"type":None,"index":None,"side_count":0}

        self.supertrend = SuperTrendWithStopLoss(self.has["inputs"]["source"], self.supertmodel.__dict__)
        # self.trendwithsl = TrendWithStopLoss(self.has["inputs"]["source"], self.trendwithsltmodel.__dict__)
        self.utbot  = UTBOT_ALERT(self.has["inputs"]["source"], self.utbotmodel.__dict__)
        # self.utbot  = CUSTOM_UTBOT_ALERT(self.has["inputs"]["source"], self.utbotmodel.__dict__)
        
        self.rsi  = RSI(self.has["inputs"]["source"], self.rsi_model.__dict__)
        self.rsifast  = RSI(self.has["inputs"]["source"], self.rsi_fast_model.__dict__)
        # self.mafast  = MA(self.has["inputs"]["source"], self.mafastmodel.__dict__)
        # self.maslow  = MA(self.has["inputs"]["source"], self.maslowmodel.__dict__)
        
        self.Source: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE = self.has["inputs"]["source"]

        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    @property
    def is_all_updated(self):
        is_updated = (self.supertrend.is_current_update and self.utbot.is_current_update
                       and self.rsi.is_current_update and self.rsifast.is_current_update)
                        # and self.mafast.is_current_update and self.maslow.is_current_update
                        # and self.trendwithsl.is_current_update)
        return is_updated
    @property
    def id(self):
        return self.chart_id
    
    @id.setter
    def id(self,_chart_id):
        self.chart_id = _chart_id

    @property
    def mafastmodel(self) -> dict:
        return MAModel(self.id,"MA",self.chart.jp_candle.source_name,self.has["inputs"]["mafast_mamode"].name.lower(),
                              self.has["inputs"]["mafast_type"],self.has["inputs"]["mafast_length"])
    
    @property
    def maslowmodel(self) -> dict:
        return MAModel(self.id,"MA",self.chart.jp_candle.source_name,self.has["inputs"]["maslow_mamode"].name.lower(),
                              self.has["inputs"]["maslow_type"],self.has["inputs"]["maslow_length"])
    
    
    
    @property
    def utbotmodel(self) -> dict:
        return UTBOTModel(self.id,"UTBOT",self.has["inputs"]["source"].source_name,self.has["inputs"]["key_value_long"],self.has["inputs"]["key_value_short"],
                              self.has["inputs"]["atr_long_period"],self.has["inputs"]["ema_long_period"],
                              self.has["inputs"]["atr_short_period"],self.has["inputs"]["ema_short_period"])
    
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
    def trendwithsltmodel(self) -> dict:
        return TrendWithStopLossModel(self.id,"TrendStopLoss",self.chart.jp_candle.source_name,
                                        self.has["inputs"]["trend_fast_period"],
                                        self.has["inputs"]["trend_slow_period"],
                                        self.has["inputs"]["trend_signal_period"],
                                        self.has["inputs"]["trend_atr_length"],
                                        self.has["inputs"]["trend_atr_mamode"].name.lower(),
                                        self.has["inputs"]["trend_atr_multiplier"])
    
    @property
    def sqeeze_model(self)-> dict:
        return SQeezeModel(self.id,"SQEEZE",self.chart.jp_candle.source_name,
                        self.has["inputs"]["bb_length"],
                        self.has["inputs"]["bb_std"],
                        self.has["inputs"]["kc_length"],
                        self.has["inputs"]["kc_scalar"],
                        self.has["inputs"]["mom_length"],
                        self.has["inputs"]["mom_smooth"],
                        self.has["inputs"]["sqeeze_mamode"].name.lower(),
                        self.has["inputs"]["use_tr"],
                        self.has["inputs"]["lazybear"],
                        self.has["inputs"]["detailed"]
                        )
    
    @property
    def macd_model(self) -> dict:
        return MACDModel(self.id,"MACD",self.has["inputs"]["source"].source_name,
                        self.has["inputs"]["type"],
                        self.has["inputs"]["slow_period"],
                        self.has["inputs"]["fast_period"],
                        self.has["inputs"]["signal_period"],
                        self.has["inputs"]["macd_type"].name.lower())
    
    @property
    def rsi_model(self) -> dict:
        return RSIModel(self.id,"RSI",self.has["inputs"]["source"].source_name,
                        self.has["inputs"]["rsi_type"],
                        self.has["inputs"]["rsi_period"],
                        self.has["inputs"]["rsi_mamode"].name.lower())
    
    @property
    def rsi_fast_model(self) -> dict:
        return RSIModel(self.id,"RSI",self.has["inputs"]["source"].source_name,
                        self.has["inputs"]["rsi_fast_type"],
                        self.has["inputs"]["rsi_fast_period"],
                        self.has["inputs"]["rsi_fast_mamode"].name.lower())
    
    @property
    def model(self) -> dict:
        return ATKBOTModel(self.id,"ATKPRO",self.has["inputs"]["source"].source_name,self.has["inputs"]["key_value_long"],self.has["inputs"]["key_value_short"],
                              self.has["inputs"]["atr_long_period"],self.has["inputs"]["ema_long_period"],
                              self.has["inputs"]["atr_short_period"],self.has["inputs"]["ema_short_period"])
    
    def disconnect_signals(self):
        try:
            self.Source.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.Source.sig_update_candle.disconnect(self.setdata_worker)
            self.Source.sig_add_candle.disconnect(self.add_worker)
            self.Source.signal_delete.disconnect(self.replace_source)
            self.Source.sig_add_historic.disconnect(self.add_historic_worker)
                        
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.Source.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.Source.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.Source.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.AutoConnection)
        self.Source.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.AutoConnection)
        self.Source.signal_delete.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
            
    def fisrt_gen_data(self):
        self.connect_signals()
        self.utbot.fisrt_gen_data()
        self.supertrend.fisrt_gen_data()
        # self.trendwithsl.fisrt_gen_data()
        self.rsi.fisrt_gen_data()
        self.rsifast.fisrt_gen_data()
        # self.mafast.fisrt_gen_data()
        # self.maslow.fisrt_gen_data()
        # self.Source.sig_reset_all.emit()
        self.reset_threadpool_asyncworker()
    
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

    def check_active_pos(self,_type:str,_open: float=0):
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
    
    
    def check_active_other_side_pos(self,_type:str,_open: float):
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
                        self.list_pos[x]["is_stoploss"] = _open
                        entry.locked_handle()
        #                 return True
        # return False
    
                        
    def delete(self):
        print("vao day")
        self.Source.deleteLater()
        # self.macd.deleteLater()
        # self.sqeeze.deleteLater()
        # self.super_smoothcandle.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        if self.list_pos:
            for obj in self.list_pos.values():
                if self.scene() is not None:
                    self.scene().removeItem(obj["obj"])
                    if hasattr(obj["obj"], "obj"):
                        obj["obj"].deleteLater()
        self.list_pos.clear() 
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
         
        
        for i in range(1,len(self.utbot.df)):
            _x = self.utbot.df.iloc[i]['index']
            
            jp_cdl = self.chart.jp_candle.map_index_ohlcv[_x]
            jp_high = jp_cdl.high
            jp_low = jp_cdl.low
            jp_open = jp_cdl.open
            
            supertrenddf = self.supertrend.df.loc[self.supertrend.df['index'] == _x-1]
            SUPERTd = 0
            if not supertrenddf.empty:
                SUPERTd = supertrenddf.iloc[-1]["SUPERTd"]

            # trendsldf = self.trendwithsl.df.loc[self.trendwithsl.df['index'] == _x-1]
            
            # Uptrend = False
            # Downtrend = False

            # sl_long = None
            # sl_short = None
            # if not trendsldf.empty:
            #     Uptrend = trendsldf.iloc[-1]["Uptrend"]
            #     Downtrend = trendsldf.iloc[-1]["Downtrend"]
            #     sl_long = trendsldf.iloc[-1]["long_stoploss"]
            #     sl_short = trendsldf.iloc[-1]["short_stoploss"]
           
            rsidf = self.rsi.df.loc[self.rsi.df['index'] == _x-1]
            rsidata = None
            if not rsidf.empty:
                rsidata = rsidf.iloc[-1]["data"]
            
            
            # rsifastdf = self.rsifast.df.loc[self.rsifast.df['index'] == _x-1]
            # rsifastdata = None
            # if not rsifastdf.empty:
            #     rsifastdata = rsifastdf.iloc[-1]["data"]
            
            "MA3 MA30"
            # mafastdf = self.mafast.df.loc[self.mafast.df['index'] == _x-1]
            # mafastdata = None
            # if not mafastdf.empty:
            #     mafastdata = mafastdf.iloc[-1]["data"]
            # maslowdf = self.maslow.df.loc[self.maslow.df['index'] == _x-1]
            # maslowdata = None
            # if not maslowdf.empty:
            #     maslowdata = maslowdf.iloc[-1]["data"]

            # if not maslowdata or not mafastdata:
            #     continue
            
            if self.utbot.df.iloc[i-1]['long'] == True and SUPERTd>0 and rsidata>50:#  and 90 < rsifastdata < 100: # and maslowdata < mafastdata
                
                # if percent_caculator(sl_long,jp_open) > 0.1:
                #     continue
                
                _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                obj = BaseArrowItem(drawtool=self.chart.drawtool,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                # obj.setParentItem(self)
                obj.setPos(_x, _val)
                obj.locked_handle()
                self.list_pos[_x] = {"type":"long","obj":obj}
                
            elif self.utbot.df.iloc[i-1]['short'] == True and  SUPERTd<0 and rsidata<50:# and SUPERTd<0 and 0 < rsifastdata < 20: # and maslowdata > mafastdata
                
                # if percent_caculator(sl_short,jp_open) > 0.1:
                #     continue
                
                _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                obj =  BaseArrowItem(drawtool=self.chart.drawtool,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                # obj.setParentItem(self)
                obj.locked_handle()
                obj.setPos(_x, _val)
                self.list_pos[_x] = {"type":"short","obj":obj}
            
                
        setdata.emit(None)
        self.sig_change_yaxis_range.emit()

        
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
    def reset_threadpool_asyncworker(self):
        self.reset_indicator()
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
      
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "key_value_long":self.has["inputs"]["key_value_long"],
                    "key_value_short":self.has["inputs"]["key_value_short"],
                    "atr_long_period":self.has["inputs"]["atr_long_period"],
                    "ema_long_period":self.has["inputs"]["ema_long_period"],
                    "atr_short_period":self.has["inputs"]["atr_short_period"],
                    "ema_short_period":self.has["inputs"]["ema_short_period"],
                    
                    "supertrend_length":self.has["inputs"]["supertrend_length"],
                    "supertrend_atr_length":self.has["inputs"]["supertrend_atr_length"],
                    "supertrend_multiplier":self.has["inputs"]["supertrend_multiplier"],
                    "supertrend_atr_mamode":self.has["inputs"]["supertrend_atr_mamode"],
                    "atr_length":self.has["inputs"]["atr_length"],
                    "atr_mamode":self.has["inputs"]["atr_mamode"],
                    "atr_multiplier":self.has["inputs"]["atr_multiplier"],
                    
                    "rsi_type":self.has["inputs"]["rsi_type"],
                    "rsi_indicator_type":self.has["inputs"]["rsi_indicator_type"],
                    "rsi_period":self.has["inputs"]["rsi_period"],
                    "rsi_mamode":self.has["inputs"]["rsi_mamode"],

                    }
        return inputs
    
    def get_styles(self):
        styles =  {"pen_high_line":self.has["styles"]["pen_high_line"],
                    "width_high_line":self.has["styles"]["width_high_line"],
                    "style_high_line":self.has["styles"]["style_high_line"],
                    
                    "pen_low_line":self.has["styles"]["pen_low_line"],
                    "width_low_line":self.has["styles"]["width_low_line"],
                    "style_low_line":self.has["styles"]["style_low_line"],
                    }
        return styles
    
    def update_inputs(self,_input,_source):
        is_update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.fisrt_gen_data()
                # self.Source.change_input(self.has["inputs"]["source"])
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                # if  _input != "price_high" and _input != "price_low":
                is_update = True
        
        if is_update:
            self.has["name"] = f"ATKPRO Ver_1.0"
            self.sig_change_indicator_name.emit(self.has["name"])
            
            if _input == "n_smooth_period" or _input == "ma_smooth_period" or _input == "mamode":
                self.stoploss_smooth_heikin.refresh_data(self.has["inputs"]["mamode"].value,self.has["inputs"]["ma_smooth_period"],self.has["inputs"]["n_smooth_period"])
                self.stoploss_smooth_heikin.fisrt_gen_data()
                # self.super_trend.fisrt_gen_data()
                # self.sqeeze.fisrt_gen_data()

            
            # if  _input == "supertrend_length" or _input == "supertrend_atr_length" or \
            #         _input == "supertrend_multiplier" or _input == "supertrend_atr_mamode":
            #     self.super_trend.change_input(dict_ta_params=self.supertrend_model.__dict__)
            
            self.fisrt_gen_data()
            
            # self.Source.change_input(dict_ta_params=self.model.__dict__)
    
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
        return calculate_stoploss(_type,price,0)
            
    
    def check_n_long_short_pos(self,is_new: bool=True,_type:str="long",n:int=5):
        sorted_pos = sorted(list(self.list_pos.keys()))
        if len(sorted_pos) < n:
            return False
        if is_new:
            pos =  sorted_pos[-n:]
        else:
            pos =  sorted_pos[:n]
        if pos:
            for i in pos:
                # print(self.list_pos[i]["type"],_type )
                if self.list_pos[i]["type"] != _type:
                    return False
        return True
    
    def check_last_pos(self):
        sorted_pos = sorted(list(self.list_pos.keys()))

        if len(sorted_pos) < 1:
            return None, False, False
        
        entry_infor = self.list_pos[sorted_pos[-1]]
        
        is_entry_closed =  entry_infor["is_stoploss"]
        is_take_profit_2R =  entry_infor["take_profit_2R"]
        is_take_profit_1_5R =  entry_infor["take_profit_1_5R"]
        
        entry_type = entry_infor["type"]
        
        stoploss = entry_infor["stop_loss"]
        
        entry:Entry = entry_infor["entry"]
        
        return entry_type, is_entry_closed, is_take_profit_2R
        
    
    
    def move_entry(self,index: float, high: float,low: float):
        return
        """
        self.list_pos[pivot_point[2]] = {"stop_loss":pivot_point[1],"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, 
        "entry":entry, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}"""
        sorted_pos = sorted(list(self.list_pos.keys()))

        if len(sorted_pos) < 1:
            return None, False, False
        
        entry_infor = self.list_pos[sorted_pos[-1]]
        
        is_entry_closed =  entry_infor["is_stoploss"]
        is_take_profit_2R =  entry_infor["take_profit_2R"]
        is_take_profit_1_5R =  entry_infor["take_profit_1_5R"]
        
        entry_type = entry_infor["type"]
        
        stoploss = entry_infor["stop_loss"]
        
        entry:Entry = entry_infor["entry"]
        
        if is_entry_closed or is_take_profit_2R:
            return True
        
        entry_pos_1_5R:QPointF = entry.has["inputs"]["data"][2.5].chart_pos
        entry_pos_2R:QPointF = entry.has["inputs"]["data"][3].chart_pos
        
        
        profit_2R = entry_pos_2R.y()
        profit_1_5R = entry_pos_1_5R.y()
        
        if entry_type == "long":
            if not is_take_profit_1_5R:
                if profit_1_5R <= high:
                    entry_infor["take_profit_1_5R"] = profit_1_5R
            if not is_take_profit_2R:
                if profit_2R <= high:
                    entry_infor["take_profit_2R"] = profit_2R
            if stoploss >= low:
                entry_infor["is_stoploss"] = True
        elif entry_type == "short":
            if not is_take_profit_1_5R:
                if profit_1_5R >= low:
                    entry_infor["take_profit_1_5R"] = profit_1_5R
            if not is_take_profit_2R:
                if profit_2R >= low:
                    entry_infor["take_profit_2R"] = profit_2R
            if stoploss <= high:
                entry_infor["is_stoploss"] = True
        
        is_entry_closed =  entry_infor["is_stoploss"]
        is_take_profit_2R =  entry_infor["take_profit_2R"]
        
        entry_y = entry_infor["entry_y"]
        # self.list_pos[sorted_pos[-1]]["entry_x"] = index
        self.list_pos[sorted_pos[-1]] = entry_infor
        # entry.moveEntry(index,entry_y)
        
        if is_entry_closed or is_take_profit_2R:
            entry.locked_handle()
    
    
    def check_pos_is_near_pivot(self,_x:int, check_type:str):
        
        stoploss_smooth_heikin = self.stoploss_smooth_heikin.df.loc[(self.stoploss_smooth_heikin.df['index'] >= _x-3) & (self.stoploss_smooth_heikin.df['index'] < _x)]
        
        if not stoploss_smooth_heikin.empty:
            
            pre_last_candle_open = stoploss_smooth_heikin.iloc[-1]["open"]
            pre_last_candle_close = stoploss_smooth_heikin.iloc[-1]["close"]
            
            pre_green = pre_last_candle_open - pre_last_candle_close < 0
            pre_red = pre_last_candle_open - pre_last_candle_close > 0
            
            for i in range(len(stoploss_smooth_heikin)):
                heikin_open = stoploss_smooth_heikin.iloc[i]["open"]
                heikin_close = stoploss_smooth_heikin.iloc[i]["close"]
                red = heikin_open - heikin_close > 0
                green = heikin_open - heikin_close < 0
                
                if check_type == "red" and red and pre_green:
                    return True
                elif check_type == "green" and green and pre_red:
                    return True
        return False
    
    def set_Data(self,data=None):
        # utbot_df,supertrend_df = data[0], data[1]
        if self.list_pos:
            for obj in self.list_pos.values():
                obj["obj"].setParentItem(self)
        

        
    def add_historic_Data(self,ls_obj):
        if ls_obj:
            for obj in ls_obj:
                obj.setParentItem(self)
                obj.show()
        
    
    def update_Data(self,df: pd.DataFrame):
        while not self.is_all_updated:
            print("not updated")
            time.sleep(0.01)
            continue
        
        _x = self.utbot.df.iloc[-1]['index']
        if self.list_pos.get(_x):
            return
        supertrenddf = self.supertrend.df.loc[self.supertrend.df['index'] == _x-1]
        SUPERTd = 0
        # Downtrend = False
        if not supertrenddf.empty:
            SUPERTd = supertrenddf.iloc[-1]["SUPERTd"]
            # Downtrend = supertrenddf.iloc[-1]["Downtrend"]
        
        rsidf = self.rsi.df.loc[self.rsi.df['index'] == _x-1]
        rsidata = None
        if not rsidf.empty:
            rsidata = rsidf.iloc[-1]["data"]
        
        
        rsifastdf = self.rsifast.df.loc[self.rsifast.df['index'] == _x-1]
        rsifastdata = None
        if not rsifastdf.empty:
            rsifastdata = rsifastdf.iloc[-1]["data"]
        
        # mafastdf = self.mafast.df.loc[self.mafast.df['index'] == _x-1]
        # mafastdata = None
        # if not mafastdf.empty:
        #     mafastdata = mafastdf.iloc[-1]["data"]
        
        # maslowdf = self.maslow.df.loc[self.maslow.df['index'] == _x-1]
        # maslowdata = None
        # if not maslowdf.empty:
        #     maslowdata = maslowdf.iloc[-1]["data"]

        # if not maslowdata or not mafastdata:
        #     return
        
        
        if self.utbot.df.iloc[-2]['long'] == True and SUPERTd>0 and rsidata>50:#  and 90 < rsifastdata < 100: # and maslowdata < mafastdata
                
            # if percent_caculator(sl_long,jp_open) > 0.1:
            #     continue
            
            _val = self.chart.jp_candle.map_index_ohlcv[_x].low
            obj = BaseArrowItem(drawtool=self.chart.drawtool,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
            obj.setParentItem(self)
            obj.setPos(_x, _val)
            obj.locked_handle()
            self.list_pos[_x] = {"type":"long","obj":obj}
            
        elif self.utbot.df.iloc[-2]['short'] == True and  SUPERTd<0 and rsidata<50:# and SUPERTd<0 and 0 < rsifastdata < 20: # and maslowdata > mafastdata
            
            # if percent_caculator(sl_short,jp_open) > 0.1:
            #     continue
            
            _val = self.chart.jp_candle.map_index_ohlcv[_x].open
            obj =  BaseArrowItem(drawtool=self.chart.drawtool,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
            obj.setParentItem(self)
            obj.locked_handle()
            obj.setPos(_x, _val)
            self.list_pos[_x] = {"type":"short","obj":obj}
        
                
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
        while not self.is_all_updated:
            time.sleep(0.01)
            continue
        list_objs = []
        for i in range(1,len(self.utbot.df)):
            
            _x = self.utbot.df.iloc[i]['index']
            if self.list_pos.get(_x):
                continue
            supertrenddf = self.supertrend.df.loc[self.supertrend.df['index'] == _x-1]
            SUPERTd = 0
            # Downtrend = False
            if not supertrenddf.empty:
                SUPERTd = supertrenddf.iloc[-1]["SUPERTd"]
                # Downtrend = supertrenddf.iloc[-1]["Downtrend"]
            
            rsidf = self.rsi.df.loc[self.rsi.df['index'] == _x-1]
            rsidata = None
            if not rsidf.empty:
                rsidata = rsidf.iloc[-1]["data"]
            
            
            rsifastdf = self.rsifast.df.loc[self.rsifast.df['index'] == _x-1]
            rsifastdata = None
            if not rsifastdf.empty:
                rsifastdata = rsifastdf.iloc[-1]["data"]
            
            # mafastdf = self.mafast.df.loc[self.mafast.df['index'] == _x-1]
            # mafastdata = None
            # if not mafastdf.empty:
            #     mafastdata = mafastdf.iloc[-1]["data"]
            
            # maslowdf = self.maslow.df.loc[self.maslow.df['index'] == _x-1]
            # maslowdata = None
            # if not maslowdf.empty:
            #     maslowdata = maslowdf.iloc[-1]["data"]

            # if not maslowdata or not mafastdata:
            #     continue
            
            if self.utbot.df.iloc[i-1]['long'] == True and SUPERTd>0 and rsidata>50:#  and 90 < rsifastdata < 100: # and maslowdata < mafastdata
                
                # if percent_caculator(sl_long,jp_open) > 0.1:
                #     continue
                
                _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                obj = BaseArrowItem(drawtool=self.chart.drawtool,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                # obj.setParentItem(self)
                obj.setPos(_x, _val)
                obj.locked_handle()
                self.list_pos[_x] = {"type":"long","obj":obj}
                
            elif self.utbot.df.iloc[i-1]['short'] == True and  SUPERTd<0 and rsidata<50:# and SUPERTd<0 and 0 < rsifastdata < 20: # and maslowdata > mafastdata
                
                # if percent_caculator(sl_short,jp_open) > 0.1:
                #     continue
                
                _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                obj =  BaseArrowItem(drawtool=self.chart.drawtool,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                # obj.setParentItem(self)
                obj.locked_handle()
                obj.setPos(_x, _val)
                self.list_pos[_x] = {"type":"short","obj":obj}
   
        setdata.emit(list_objs)
        
    def add_data(self,setdata):
        df = self.Source.get_data(start=-10)
        setdata.emit(df)
    
    def update_data(self,setdata):
        df= self.Source.get_data(start=-10)
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
    