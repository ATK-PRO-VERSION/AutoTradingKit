

import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF,QPointF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem

from atklip.controls import PD_MAType,IndicatorType,UTBOT_ALERT
from atklip.controls.models import UTBOTModel, MACDModel, RSIModel
from atklip.graphics.chart_component.draw_tools.base_arrow import BaseArrowItem
from atklip.graphics.chart_component.draw_tools.entry import Entry

from atklip.appmanager import FastWorker
from atklip.app_utils import *
from atklip.controls.candle.n_time_smooth_candle import N_SMOOTH_CANDLE
from atklip.controls.pandas_ta.ma import ma
from atklip.controls.trend.zigzag import ZIGZAG
from atklip.controls.momentum.macd import MACD
from atklip.controls.momentum.rsi import RSI
from atklip.graphics.pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

class UTBOT(GraphicsObject):
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
                    
                    "key_value_long":1,
                    "key_value_short":1,
                    
                    "atr_long_period":10,
                    "ema_long_period":1,
                    
                    "atr_short_period":10,
                    "ema_short_period":1,
                    
                    "indicator_type":IndicatorType.UTBOT,
                    "show":False},

            "styles":{
                    }
                    }
        
        self.id = self.chart.objmanager.add(self)
        
        self.list_pos:dict = {}
        self.picture: QPicture = QPicture()

        self.INDICATOR  = UTBOT_ALERT(self.has["inputs"]["source"], self.model.__dict__)
                
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    @property
    def is_all_updated(self):
        is_updated = self.INDICATOR.is_current_update 
        return is_updated
    
    @property
    def id(self):
        return self.chart_id
    
    @id.setter
    def id(self,_chart_id):
        self.chart_id = _chart_id

    @property
    def model(self) -> dict:
        return UTBOTModel(self.id,"UTBOT",self.has["inputs"]["source"].source_name,self.has["inputs"]["key_value_long"],self.has["inputs"]["key_value_short"],
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
        print("deleted--------------------------")
        
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
        xdata,_long,_short= self.INDICATOR.get_data()
        setdata.emit((xdata,_long,_short))
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"UTBOT Ver_1.0"
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
            self.has["name"] = f"UTBOT"
            self.sig_change_indicator_name.emit(self.has["name"])
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
                   
    
    def set_Data(self,data):
        if self.list_pos:
            for obj in self.list_pos.values():
                if self.scene() is not None:
                    self.scene().removeItem(obj["obj"])
                    if hasattr(obj["obj"], "obj"):
                        obj["obj"].deleteLater()
        self.list_pos.clear()        
        xData:np.ndarray = data[0]
        _long:np.ndarray  = data[1]
        _short:np.ndarray  = data[2]
        df = pd.DataFrame({
            "x":xData,
            "long":_long,
            "short":_short,
        })
        
        for i in range(1,len(df)):
            _x = df.iloc[i]['x']
            if df.iloc[i-1]['long'] == True:
                _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                obj = BaseArrowItem(drawtool=self.chart.drawtool,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                obj.setParentItem(self)
                obj.setPos(_x, _val)
                obj.locked_handle()
                self.list_pos[_x] = {"type":"long","obj":obj}
                
            elif df.iloc[i-1]['short'] == True:
                _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                obj =  BaseArrowItem(drawtool=self.chart.drawtool,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                obj.setParentItem(self)
                obj.locked_handle()
                obj.setPos(_x, _val)
                self.list_pos[_x] = {"type":"short","obj":obj}
        self.INDICATOR.is_current_update = True

    
    def add_historic_Data(self,data):
        xData:np.ndarray = data[0]
        _long:np.ndarray  = data[1]
        _short:np.ndarray  = data[2]
        df = pd.DataFrame({
            "x":xData,
            "long":_long,
            "short":_short,
        })
        
        for i in range(1,len(df)):
            _x = df.iloc[i]['x']
            if self.list_pos.get(_x):
                continue
            if df.iloc[i-1]['long'] == True:
                _val = self.chart.jp_candle.map_index_ohlcv[_x].low
                obj = BaseArrowItem(drawtool=self.chart.drawtool,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
                obj.setParentItem(self)
                obj.setPos(_x, _val)
                obj.locked_handle()
                self.list_pos[_x] = {"type":"long","obj":obj}
                
            elif df.iloc[i-1]['short'] == True:
                _val = self.chart.jp_candle.map_index_ohlcv[_x].open
                obj =  BaseArrowItem(drawtool=self.chart.drawtool,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
                obj.setParentItem(self)
                obj.locked_handle()
                obj.setPos(_x, _val)
                self.list_pos[_x] = {"type":"short","obj":obj}
        self.INDICATOR.is_current_update = True
    
    def update_Data(self,data):
        xData:np.ndarray = data[0]
        _long:np.ndarray  = data[1]
        _short:np.ndarray  = data[2]
        df = pd.DataFrame({
            "x":xData,
            "long":_long,
            "short":_short,
        })
        
        _x = df.iloc[-1]['x']
        
        if self.list_pos.get(_x):
            self.INDICATOR.is_current_update = True
            return

        if df.iloc[-2]['long'] == True:
            _val = self.chart.jp_candle.map_index_ohlcv[_x].low
            obj = BaseArrowItem(drawtool=self.chart.drawtool,angle=90, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='green')
            obj.setParentItem(self)
            obj.setPos(_x, _val)
            obj.locked_handle()
            self.list_pos[_x] = {"type":"long","obj":obj}
            
        elif df.iloc[-2]['short'] == True:
            _val = self.chart.jp_candle.map_index_ohlcv[_x].open
            obj =  BaseArrowItem(drawtool=self.chart.drawtool,angle=270, tipAngle=60, headLen=10, tailLen=10, tailWidth=5, pen=None, brush='red')
            obj.setParentItem(self)
            obj.locked_handle()
            obj.setPos(_x, _val)
            self.list_pos[_x] = {"type":"short","obj":obj}
        self.INDICATOR.is_current_update = True
        
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
        xdata,_long,_short= self.INDICATOR.get_data(start=-10)
        setdata.emit((xdata,_long,_short))
    
    def update_data(self,setdata):
        xdata,_long,_short= self.INDICATOR.get_data(start=-10)
        setdata.emit((xdata,_long,_short))

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
    