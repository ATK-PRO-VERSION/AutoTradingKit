import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF,QPointF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem
from atklip.graphics.pyqtgraph import GraphicsObject

from atklip.controls import PD_MAType,IndicatorType,ATKBOT_ALERT
from atklip.controls.models import ATKBOTModel, MACDModel, RSIModel,SQeezeModel,SuperTrendModel
from atklip.graphics.chart_component.draw_tools.base_arrow import BaseArrowItem
from atklip.graphics.chart_component.draw_tools.TargetItem import ArrowItem
from atklip.graphics.chart_component.draw_tools.entry import Entry

from atklip.appmanager import FastWorker
from atklip.app_utils import *
from atklip.controls.candle.n_time_smooth_candle import N_SMOOTH_CANDLE
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.trend.zigzag import ZIGZAG
from atklip.controls.momentum.macd import MACD
from atklip.controls.momentum.rsi import RSI
from atklip.controls import  SQEEZE
from atklip.controls import SuperTrend
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
        self.has: dict = {
            "name": f"ATKPRO Ver_1.0",
            "y_axis_show":False,
            
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    
                    "key_value_long":0.1,
                    "key_value_short":0.1,
                    
                    "atr_long_period":1,
                    "ema_long_period":2,
                    
                    "atr_short_period":1,
                    "ema_short_period":2,
                    
                    "n_smooth_period":3,
                    "ma_smooth_period":3,
                    "mamode":PD_MAType.EMA,
                    
                    "supertrend_length":5,
                    "supertrend_atr_length":5,
                    "supertrend_multiplier":0.1,
                    "supertrend_atr_mamode":PD_MAType.RMA,
                    
                    
                    "type":"close",
                    "fast_period":12,
                    "slow_period":26,
                    "signal_period":9,
                    "macd_type":PD_MAType.RMA,
                    "price_high":60,
                    "price_low":-60,
                    
                    "max_price_high":150,
                    "min_price_low":-150,
                    

                    "rsi_period":14,
                    "rsi_ma_type":PD_MAType.RMA,
                    "rsi_price_high":40,
                    "rsi_price_low":60,
                    
                    
                    "n_period": 10,
                    "m_period": 10,
                    
                    "indicator_type":IndicatorType.ATKPRO,
                    
                    "bb_length":20,
                    "bb_std":2,
                    "kc_length":10,
                    "kc_scalar":1.5,
                    "mom_length":10,
                    "mom_smooth":10,
                    "use_tr":True,
                    "lazybear":True,
                    "detailed":False,
                    "sqeeze_mamode":PD_MAType.SMA,
                    
                    
                    "show":False},

            "styles":{
                    'pen_high_line': "#089981",
                    'width_high_line': 1,
                    'style_high_line': Qt.PenStyle.SolidLine,
                    
                    'pen_low_line': "#f23645",
                    'width_low_line': 1,
                    'style_low_line': Qt.PenStyle.SolidLine,
                    }
                    }
        
        self.id = self.chart.objmanager.add(self)
        
        self.list_pos:dict = {}
        self.picture: QPicture = QPicture()

        self.smooth_heikin = N_SMOOTH_CANDLE(self.chart._precision,self.chart.heikinashi,
                                                  13,
                                                  self.has["inputs"]["mamode"].value,
                                                  3)
        self.smooth_heikin.fisrt_gen_data()
        
        
        self.stoploss_smooth_heikin = N_SMOOTH_CANDLE(self.chart._precision,self.chart.heikinashi,
                                                  3,
                                                  self.has["inputs"]["mamode"].value,
                                                  3)
        self.stoploss_smooth_heikin.fisrt_gen_data()
        
        
        self.super_smoothcandle = N_SMOOTH_CANDLE(self.chart._precision,self.has["inputs"]["source"],
                                                  self.has["inputs"]["n_smooth_period"],
                                                  self.has["inputs"]["mamode"].value,
                                                  self.has["inputs"]["ma_smooth_period"])
        self.super_smoothcandle.fisrt_gen_data()
        
        # self.macd = MACD(self.has["inputs"]["source"], self.macd_model.__dict__)
        # self.macd.fisrt_gen_data()
        
        # self.sqeeze = SQEEZE(self.has["inputs"]["source"], self.sqeeze_model.__dict__)
        # self.sqeeze.fisrt_gen_data()
        
        self.super_trend = SuperTrend(self.super_smoothcandle, self.supertrend_model.__dict__)
        self.super_trend.fisrt_gen_data()
        
        self.INDICATOR  = ATKBOT_ALERT(self.has["inputs"]["source"], self.model.__dict__)
                
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    
    @property
    def is_all_updated(self):
        is_updated = self.INDICATOR.is_current_update and self.super_trend.is_current_update and self.super_smoothcandle.is_current_update and self.stoploss_smooth_heikin.is_current_update and self.smooth_heikin.is_current_update
        return is_updated
    @property
    def id(self):
        return self.chart_id
    
    @id.setter
    def id(self,_chart_id):
        self.chart_id = _chart_id

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
    def supertrend_model(self)-> dict:
        return SuperTrendModel(self.id,"SQEEZE",self.chart.jp_candle.source_name,
                        self.has["inputs"]["supertrend_length"],
                        self.has["inputs"]["supertrend_atr_length"],
                        self.has["inputs"]["supertrend_multiplier"],
                        self.has["inputs"]["supertrend_atr_mamode"].name.lower()
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
                        self.has["inputs"]["type"],
                        self.has["inputs"]["rsi_period"],
                        self.has["inputs"]["rsi_ma_type"].name.lower())
    
    @property
    def model(self):
        return ATKBOTModel(self.id,"ATKPRO",self.has["inputs"]["source"].source_name,self.has["inputs"]["key_value_long"],self.has["inputs"]["key_value_short"],
                              self.has["inputs"]["atr_long_period"],self.has["inputs"]["ema_long_period"],
                              self.has["inputs"]["atr_short_period"],self.has["inputs"]["ema_short_period"])
    
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
        self.INDICATOR.started_worker()
    
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
        self.INDICATOR.deleteLater()
        # self.macd.deleteLater()
        # self.sqeeze.deleteLater()
        # self.super_smoothcandle.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        xdata,_long,_short= self.INDICATOR.get_data()
        setdata.emit((xdata,_long,_short))
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"ATKPRO Ver_1.0"
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
                    
                    
                    
                    "n_smooth_period":self.has["inputs"]["n_smooth_period"],
                    "ma_smooth_period":self.has["inputs"]["ma_smooth_period"],
                    "mamode":self.has["inputs"]["mamode"],


                    # "type":self.has["inputs"]["type"],
                    # "fast_period":self.has["inputs"]["fast_period"],
                    # "slow_period":self.has["inputs"]["slow_period"],
                    # "signal_period":self.has["inputs"]["signal_period"],
                    # "macd_type":self.has["inputs"]["macd_type"],
                    
                    # "price_high":self.has["inputs"]["price_high"],
                    # "price_low":self.has["inputs"]["price_low"],
                    
                    # "max_price_high":self.has["inputs"]["max_price_high"],
                    # "min_price_low":self.has["inputs"]["min_price_low"],
                    
                    
                    # "rsi_period":self.has["inputs"]["rsi_period"],
                    # "rsi_ma_type":self.has["inputs"]["rsi_ma_type"],
                    # "rsi_price_high":self.has["inputs"]["rsi_price_high"],
                    # "rsi_price_low":self.has["inputs"]["rsi_price_low"],
                    
                    "n_period":self.has["inputs"]["n_period"],
                    "m_period":self.has["inputs"]["m_period"],
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
                self.INDICATOR.change_input(self.has["inputs"]["source"])
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                # if  _input != "price_high" and _input != "price_low":
                is_update = True
        
        if is_update:
            self.has["name"] = f"ATKPRO Ver_1.0"
            self.sig_change_indicator_name.emit(self.has["name"])
            
            if _input == "n_smooth_period" or _input == "ma_smooth_period" or _input == "mamode":
                self.super_smoothcandle.refresh_data(self.has["inputs"]["mamode"].value,self.has["inputs"]["ma_smooth_period"],self.has["inputs"]["n_smooth_period"])
            
            # if  _input == "type" or _input == "fast_period" or _input == "slow_period" or _input == "signal_period" or _input == "macd_type":
            #     self.macd.change_input(dict_ta_params=self.macd_model.__dict__)
            # elif  _input == "bb_length" or _input == "bb_std" or _input == "kc_length" \
            #         or _input == "kc_scalar" or _input == "mom_length"\
            #             or _input == "mom_smooth":
            #     self.sqeeze.change_input(dict_ta_params=self.sqeeze_model.__dict__)
            
            
            if  _input == "supertrend_length" or _input == "supertrend_atr_length" or \
                    _input == "supertrend_multiplier" or _input == "supertrend_atr_mamode":
                self.super_trend.change_input(dict_ta_params=self.supertrend_model.__dict__)
            
            
            self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)
    
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
        entry.moveEntry(index,entry_y)
        
        if is_entry_closed or is_take_profit_2R:
            entry.locked_handle()
        
                
    def set_Data(self,data):
        
        if self.list_pos:
            for obj in self.list_pos.values():
                if self.scene() is not None:
                    self.scene().removeItem(obj["obj"])
                    self.scene().removeItem(obj["entry"])
                    if hasattr(obj["obj"], "deleteLater"):
                        obj["obj"].deleteLater()
                    if hasattr(obj["entry"], "deleteLater"):
                        obj["entry"].deleteLater()
                    # 
        self.list_pos.clear()   
        
        xdata,_long,_short = data[0],data[1],data[2]
             
        df = pd.DataFrame({
            "x":xdata,
            "long":_long,
            "short":_short,
        })
        for i in range(1,len(df)):
            _x = df.iloc[i]['x']

            if i-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1 <=0:
                    continue
            
            row = self.super_smoothcandle.df.loc[self.super_smoothcandle.df['index'] == _x-1]
            sm_candle_short_signal = False
            sm_candle_long_signal = False
            if not row.empty:
                _high = row.iloc[-1]["high"]
                _low = row.iloc[-1]["low"]
                _open = row.iloc[-1]["open"]
                _close = row.iloc[-1]["close"]
                sm_candle_long_signal = _open < _close
                sm_candle_short_signal = _open > _close
            
            
            jp_high = self.chart.jp_candle.map_index_ohlcv[_x-1].high
            jp_low = self.chart.jp_candle.map_index_ohlcv[_x-1].low
            jp_open = self.chart.jp_candle.map_index_ohlcv[_x-1].open
            jp_close = self.chart.jp_candle.map_index_ohlcv[_x-1].close
            
            
            row_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x-1]
            # cr_row_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x]
            smooth_heikin_short_signal = False
            smooth_heikin_long_signal = False
            if not row_smooth_heikin.empty:
                _high = row_smooth_heikin.iloc[-1]["high"]
                _low = row_smooth_heikin.iloc[-1]["low"]
                _open = row_smooth_heikin.iloc[-1]["open"]
                _close = row_smooth_heikin.iloc[-1]["close"]
                smooth_heikin_long_signal = _high < jp_low and jp_open < jp_close
                smooth_heikin_short_signal = _low > jp_high and jp_open > jp_close
                

            stoploss_smooth_heikin = self.stoploss_smooth_heikin.df.loc[self.stoploss_smooth_heikin.df['index'] == _x-1]
            stoploss_high = None
            stoploss_low = None
            if not stoploss_smooth_heikin.empty:
                stoploss_high = stoploss_smooth_heikin.iloc[-1]["low"]
                stoploss_low = stoploss_smooth_heikin.iloc[-1]["high"]
            
            cr_jp_high = self.chart.jp_candle.map_index_ohlcv[_x].high
            cr_jp_low = self.chart.jp_candle.map_index_ohlcv[_x].low
            
            self.move_entry(_x,cr_jp_high,cr_jp_low)
            
            super_trend_df = self.super_trend.df.loc[(self.super_trend.df['index'] <= _x-1) & (self.super_trend.df['index'] >= _x-4)]
            super_trend_long_signal = False
            super_trend_short_signal = False
            if len(super_trend_df) >= 3:
                sqz_histogram = super_trend_df.iloc[-1]['SUPERTd']
                super_trend_long_signal = sqz_histogram > 0 
                super_trend_short_signal = sqz_histogram < 0
            

            if df.iloc[i-1]['long'] == True:
                _type,is_sl,is_tp = self.check_last_pos()
                
                if _type == "long":
                    if is_sl == True:
                        pass
                    else:
                        continue

                if super_trend_long_signal and sm_candle_long_signal and smooth_heikin_long_signal:     
                    
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                       
                    obj = ArrowItem(drawtool=self,angle=90,pen="green",brush = "green")
                    obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                    obj.setParentItem(self)
                    obj.setPos(_x, _val)
                    obj.locked_handle()
                    # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                    stop_loss =  stoploss_low
                    entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                    entry.setPoint(_x-1,_val)
                    entry.setParentItem(self)
                    entry.moveEntry(_x,_val)
                    # self.chart.sig_add_item.emit(entry)
                    self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":entry, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            elif df.iloc[i-1]['short'] == True:
                _type,is_sl,is_tp = self.check_last_pos()
                
                if _type == "short":
                    if is_sl:
                        pass
                    else:
                        continue
                
                # elif _type == "long":
                #     _open = self.chart.jp_candle.map_index_ohlcv[_x].open
                #     self.check_active_other_side_pos("long",_open)
                
                if  super_trend_short_signal and sm_candle_short_signal and smooth_heikin_short_signal:     
                    
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                       
                    obj = ArrowItem(drawtool=self,angle=270,pen="red",brush = "red")
                    obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                    obj.setParentItem(self)
                    obj.setPos(_x, _val)
                    obj.locked_handle()
                    
                    # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                    stop_loss =  stoploss_high
                    entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                    entry.setPoint(_x-1,_val)
                    entry.setParentItem(self)
                    entry.moveEntry(_x,_val)
                    # self.chart.sig_add_item.emit(entry)
                    self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"short","obj":obj, "entry":entry, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            
        
        
    def add_historic_Data(self,data):
        return
        xData:np.ndarray = data[0]
        _long:np.ndarray  = data[1]
        _short:np.ndarray  = data[2]
        df = pd.DataFrame({
            "x":xData,
            "long":_long,
            "short":_short,
        })
        
        # df = data.loc[(data['long'] == True) | (data['short'] == True)]
        for i in range(1,len(df)):
            _x = df.iloc[i]['x']
            
            

            if i-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1 <=0:
                    continue
            
            # row = self.smoothcandle.df.loc[self.smoothcandle.df['index'] == _x-1]
            # sm_candle_short_signal = False
            # sm_candle_long_signal = False
            # if not row.empty:
            #     _high = row.iloc[-1]["high"]
            #     _low = row.iloc[-1]["low"]
            #     _open = row.iloc[-1]["open"]
            #     _close = row.iloc[-1]["close"]
            #     sm_candle_long_signal = _open < _close
            #     sm_candle_short_signal = _open > _close
            
            # jp_open = self.chart.jp_candle.map_index_ohlcv[_x-1].open
            # jp_close = self.chart.jp_candle.map_index_ohlcv[_x-1].close
            
            # macd_df = self.macd.df.loc[(self.macd.df['index'] == _x-1)]
            # macd = None
            # signalma = None
            # histogram = None
            # macd_long_signal = False
            # macd_short_signal = False
            # if len(macd_df) > 0:
            #     macd = macd_df.iloc[-1]['macd']
            #     signalma = macd_df.iloc[-1]['signalma']
            #     histogram = macd_df.iloc[-1]['histogram']
                
            #     macd_long_signal = ((histogram < 0) and (self.has["inputs"]["min_price_low"] < signalma < self.has["inputs"]["price_low"])  and (macd < 0)) 
            #     macd_short_signal = ((histogram > 0) and (self.has["inputs"]["price_high"] < signalma < self.has["inputs"]["max_price_high"])  and (macd > 0))
            
            if df.iloc[i-1]['long'] == True:
                # if self.check_n_long_short_pos(True,"long",1):
                #     continue
                
                pv_df =  self.chart.jp_candle.df.loc[(self.chart.jp_candle.df['index'] < _x) & (self.chart.jp_candle.df['index'] >= _x-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1)]   
                pivot_point = self.check_pivot_points(pv_df,"low",self.has["inputs"]["n_period"],self.has["inputs"]["m_period"])
                
                if self.list_pos.get(pivot_point[2]):
                    continue
                
                if pivot_point[0]:
  
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                    
                    if macd_long_signal and sm_candle_long_signal:
                        obj = BaseArrowItem(drawtool=self,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                        obj.setParentItem(self)
                        obj.setPos(_x, _val)
                        obj.locked_handle()
                        self.chart.sig_add_item.emit(obj)
                        entry = Entry([pivot_point[2], pivot_point[1]], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=self.chart.vb, drawtool=self.chart.drawtool)
                        
                        entry.setPoint(_x,_val)
                        entry.locked_handle()
                        entry.setParentItem(self)
                        self.chart.sig_add_item.emit(entry)
                        
                        self.list_pos[pivot_point[2]] = {"stop_loss":pivot_point[1],"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":entry}
            elif df.iloc[i-1]['short'] == True:
                # if self.check_n_long_short_pos(True,"short",1):
                #     continue
                pv_df =  self.chart.jp_candle.df.loc[(self.chart.jp_candle.df['index'] < _x) & (self.chart.jp_candle.df['index'] >= _x-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1)]   
                pivot_point = self.check_pivot_points(pv_df,"high",self.has["inputs"]["n_period"],self.has["inputs"]["m_period"])
                if self.list_pos.get(pivot_point[2]):
                    continue
                if pivot_point[0]:
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                    "Check dieu kien so voi smcandle 50"
                    if macd_short_signal and sm_candle_short_signal:
                        obj =  BaseArrowItem(drawtool=self,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                        obj.setParentItem(self)
                        obj.locked_handle()
                        obj.setPos(_x, _val)
                        self.chart.sig_add_item.emit(obj)
                        entry = Entry([pivot_point[2], pivot_point[1]], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=self.chart.vb, drawtool=self.chart.drawtool)
                        
                        entry.setPoint(_x,_val)
                        entry.locked_handle()
                        entry.setParentItem(self)
                        self.chart.sig_add_item.emit(entry)
                        
                        self.list_pos[pivot_point[2]] = {"stop_loss":pivot_point[1],"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":entry}
        
    
    def update_Data(self,data):
        
        xdata,_long,_short = data[0],data[1],data[2]
             
        df = pd.DataFrame({
            "x":xdata,
            "long":_long,
            "short":_short,
        })
        for i in range(1,len(df)):
            _x = df.iloc[i]['x']

            if i-self.has["inputs"]["n_period"]-self.has["inputs"]["m_period"]-1 <=0:
                    continue
            
            row = self.super_smoothcandle.df.loc[self.super_smoothcandle.df['index'] == _x-1]
            sm_candle_short_signal = False
            sm_candle_long_signal = False
            if not row.empty:
                _high = row.iloc[-1]["high"]
                _low = row.iloc[-1]["low"]
                _open = row.iloc[-1]["open"]
                _close = row.iloc[-1]["close"]
                sm_candle_long_signal = _open < _close
                sm_candle_short_signal = _open > _close
            
            
            jp_high = self.chart.jp_candle.map_index_ohlcv[_x-1].high
            jp_low = self.chart.jp_candle.map_index_ohlcv[_x-1].low
            jp_open = self.chart.jp_candle.map_index_ohlcv[_x-1].open
            jp_close = self.chart.jp_candle.map_index_ohlcv[_x-1].close
            
            
            row_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x-1]
            # cr_row_smooth_heikin = self.smooth_heikin.df.loc[self.smooth_heikin.df['index'] == _x]
            smooth_heikin_short_signal = False
            smooth_heikin_long_signal = False
            if not row_smooth_heikin.empty:
                _high = row_smooth_heikin.iloc[-1]["high"]
                _low = row_smooth_heikin.iloc[-1]["low"]
                _open = row_smooth_heikin.iloc[-1]["open"]
                _close = row_smooth_heikin.iloc[-1]["close"]
                smooth_heikin_long_signal = _high < jp_low and jp_open < jp_close
                smooth_heikin_short_signal = _low > jp_high and jp_open > jp_close
                

            stoploss_smooth_heikin = self.stoploss_smooth_heikin.df.loc[self.stoploss_smooth_heikin.df['index'] == _x-1]
            stoploss_high = None
            stoploss_low = None
            if not stoploss_smooth_heikin.empty:
                stoploss_high = stoploss_smooth_heikin.iloc[-1]["low"]
                stoploss_low = stoploss_smooth_heikin.iloc[-1]["high"]
            
            cr_jp_high = self.chart.jp_candle.map_index_ohlcv[_x].high
            cr_jp_low = self.chart.jp_candle.map_index_ohlcv[_x].low
            self.move_entry(_x,cr_jp_high,cr_jp_low)
            
            super_trend_df = self.super_trend.df.loc[(self.super_trend.df['index'] <= _x-1) & (self.super_trend.df['index'] >= _x-4)]
            super_trend_long_signal = False
            super_trend_short_signal = False
            if len(super_trend_df) >= 3:
                sqz_histogram = super_trend_df.iloc[-1]['SUPERTd']
                super_trend_long_signal = sqz_histogram > 0 
                super_trend_short_signal = sqz_histogram < 0
            

            if df.iloc[i-1]['long'] == True:
                _type,is_sl,is_tp = self.check_last_pos()
                
                if _type == "long":
                    if is_sl == True:
                        pass
                    else:
                        continue

                if super_trend_long_signal and sm_candle_long_signal and smooth_heikin_long_signal:     
                    
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                       
                    obj = ArrowItem(drawtool=self,angle=90,pen="green",brush = "green")
                    obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                    obj.setParentItem(self)
                    obj.setPos(_x, _val)
                    obj.locked_handle()
                    # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                    stop_loss =  stoploss_low
                    entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                    # entry.setPoint(_x,_val)
                    entry.setParentItem(self)
                    entry.moveEntry(_x,_val)
                    # self.chart.sig_add_item.emit(entry)
                    self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"long","obj":obj, "entry":entry, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            elif df.iloc[i-1]['short'] == True:
                _type,is_sl,is_tp = self.check_last_pos()
                
                if _type == "short":
                    if is_sl:
                        pass
                    else:
                        continue
                
                # elif _type == "long":
                #     _open = self.chart.jp_candle.map_index_ohlcv[_x].open
                #     self.check_active_other_side_pos("long",_open)
                
                if  super_trend_short_signal and sm_candle_short_signal and smooth_heikin_short_signal:     
                    
                    _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                                       
                    obj = ArrowItem(drawtool=self,angle=270,pen="red",brush = "red")
                    obj.setFlags(obj.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
                    obj.setParentItem(self)
                    obj.setPos(_x, _val)
                    obj.locked_handle()
                    
                    # stop_loss =  self.calculate_stop_loss("long",pivot_point[1])
                    stop_loss =  stoploss_high
                    entry = Entry([_x-1, stop_loss], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=None, drawtool=self.chart.drawtool)
                    entry.setParentItem(self)
                    entry.moveEntry(_x,_val)
                    # self.chart.sig_add_item.emit(entry)
                    self.list_pos[_x] = {"stop_loss":stop_loss,"entry_x":_x,"entry_y":_val,"type":"short","obj":obj, "entry":entry, "is_stoploss":False, "take_profit_1_5R":None,"take_profit_2R":None}
            
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
        xdata,_long,_short= self.INDICATOR.get_data(stop=_len)
        setdata.emit((xdata,_long,_short))
        
    def add_data(self,setdata):
        xdata,_long,_short= self.INDICATOR.get_data(start=-int(self.has["inputs"]["n_period"]+self.has["inputs"]["m_period"]+10))
        setdata.emit((xdata,_long,_short))
    
    def update_data(self,setdata):
        xdata,_long,_short= self.INDICATOR.get_data(start=-int(self.has["inputs"]["n_period"]+self.has["inputs"]["m_period"]+10))
        setdata.emit((xdata,_long,_short))

    def boundingRect(self) -> QRectF:
        # if self.list_pos:
        #     x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
        #     for _x in self.list_pos.keys():
        #         obj = self.list_pos.get(_x)
        #         if obj:
        #             if x_left < _x < x_right:
        #                 obj["obj"].show()
        #             else:
        #                 obj["obj"].hide()

        return self.picture.boundingRect()
    
    def paint(self, p:QPainter, *args):
        # self.picture.play(p)
        p.drawRect(self.boundingRect())
    
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return _value,self.has["styles"]['pen_high_line']
    
    def get_last_point(self):
        # _time = self.centerline.xData[-1]
        _time = self.xData[-1]
        # _value = self.centerline.yData[-1]
        _value = self.yData[-1]
        return _time,_value
    
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
    