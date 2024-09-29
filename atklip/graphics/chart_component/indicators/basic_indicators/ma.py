import time
from typing import Tuple, List,TYPE_CHECKING

import numpy as np
from atklip.graphics.pyqtgraph import functions as fn,PlotDataItem
from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtWidgets import QGraphicsItem
from atklip.controls import PD_MAType

from atklip.controls.ma import MA
from atklip.graphics.chart_component.base_items import PlotLineItem
from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart



class BasicMA(PlotDataItem):
    """DEMA EMA HMA SMA SMMA TEMA TRIX ZLEMA WMA"""
    on_click = Signal(QObject)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    sig_change_indicator_name = Signal(str)

    def __init__(self,chart,indicator_type: PD_MAType,pen:str="yellow",length:int=30,_type:str="close",id = None,clickable=True) -> None:
        """Choose colors of candle"""
        super().__init__()
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        # self.setCacheMode(QGraphicsItem.CacheMode.ItemCoordinateCache)
        self.setZValue(999)
        
        self.chart:Chart = chart
        
        self.has = {
            "name": f"{indicator_type.value} {_type} {length}",
            "y_axis_show":False,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name":self.chart.jp_candle.source_name,
                    "type":_type,
                    "ma_type":indicator_type,
                    "length":length,
                    "show":True
                    },

            "styles":{
                    'pen': pen,
                    'width': 1,
                    'style': Qt.PenStyle.SolidLine,}
        }
        
        self.opts.update({'pen':pen})
        self._pen = pen
        self.id = id
        self.is_reset = False
        # self.xData, self.yData = np.array([]),np.array([])
        
        self.Indicator  = MA(self,self.has["inputs"]["source"], self.has["inputs"]["type"],
                              self.has["inputs"]["ma_type"],self.has["inputs"]["length"])
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)
                
        self.signal_delete.connect(self.delete)
        
    def disconnect_signals(self):
        try:
            self.Indicator.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.Indicator.sig_update_candle.disconnect(self.setdata_worker)
            self.Indicator.sig_add_candle.disconnect(self.setdata_worker)
            self.Indicator.signal_delete.disconnect(self.replace_source)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.Indicator.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)

        self.Indicator.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.Indicator.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.AutoConnection)
        self.Indicator.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.AutoConnection)
        
        self.Indicator.signal_delete.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
    
    def fisrt_gen_data(self):
        self.connect_signals()
        self.Indicator.started_worker()
       
    def delete(self):
        self.Indicator.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        _index,_data = self.Indicator.get_data()
        setdata.emit((_index,_data))
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"{self.has["inputs"]["ma_type"].name} {self.has["inputs"]["length"]} {self.has["inputs"]["type"]}"
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
                    "type":self.has["inputs"]["type"],
                    "ma_type":self.has["inputs"]["ma_type"],
                    "length":self.has["inputs"]["length"],}
        return inputs
    
    def get_styles(self):
        styles =  {"pen":self.has["styles"]["pen"],
                    "width":self.has["styles"]["width"],
                    "style":self.has["styles"]["style"],}
        return styles
    def update_inputs(self,_input,_source):
        is_update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.Indicator.change_inputs(_input,self.has["inputs"]["source"])
        elif _input == "type":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        elif _input == "ma_type":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        elif _input == "length":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        if is_update:
            self.has["name"] = f"{self.has["inputs"]["ma_type"].name} {self.has["inputs"]["length"]} {self.has["inputs"]["type"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.Indicator.change_inputs(_input,_source)
            
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen" or _input == "width" or _input == "style":
            self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"])

    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return _value,self._pen
    
    def get_xaxis_param(self):
        return None,"#363a45"


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()  
    
    def set_Data(self,data):
        xData = data[0]
        yData = data[1]
        self.setData(xData, yData)

    def get_last_point(self):
        df = self.Indicator.get_df(2)
        _time = df["index"].iloc[-1]
        _value = df["data"].iloc[-1]
        return _time,_value
    
    
    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()    
    
    def add_historic_worker(self):
        self.worker = None
        self.worker = FastWorker(self.load_historic_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start() 
    
    def add_worker(self):
        self.worker = None
        self.worker = FastWorker(self.add_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()    
    
    def load_historic_data(self,setdata):
        _index,_data = self.Indicator.get_data()
        setdata.emit((_index,_data))        
    def add_data(self,setdata):
        _index,_data = self.Indicator.get_data()
        setdata.emit((_index,_data))        
    def update_data(self,setdata):
        _index,_data = self.Indicator.get_data()
        setdata.emit((_index,_data))        
    # def boundingRect(self) -> QRectF:
    #     x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
    #     start_index = self.chart.jp_candle.candles[0].index
    #     stop_index = self.chart.jp_candle.candles[-1].index
    #     if x_left > start_index:
    #         self._start = x_left+2
    #     else:
    #         self._start = start_index+2
            
    #     if x_right < stop_index:
    #         self._stop = x_right
    #     else:
    #         self._stop = stop_index
    #     if self.yData.size != 0:
    #         h_low,h_high = np.nanmin(self.yData), np.nanmax(self.yData) 
    #     else:
    #         h_low,h_high = self.chart.yAxis.range[0],self.chart.yAxis.range[1]
        
    #     rect = QRectF(self._start,h_low,self._stop-self._start,h_high-h_low)
    #     return rect#     
    
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mouseClickEvent(ev)

    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
    
    def setPen(self, *args, **kargs):
        pen = fn.mkPen(*args, **kargs)
        self.opts['pen'] = pen
        self.updateItems(styleUpdate=True)

    def data_bounds(self, ax=0, offset=0) -> Tuple:
        x, y = self.getData()
        if ax == 0:
            sub_range = x[-offset:]
        else:
            sub_range = y[-offset:]
        return np.nanmin(sub_range), np.nanmax(sub_range)