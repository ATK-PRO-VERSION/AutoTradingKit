import time
from typing import Tuple, List,TYPE_CHECKING

import numpy as np
from atklip.graphics.pyqtgraph import functions as fn
from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtWidgets import QGraphicsItem
from atklip.controls import PD_MAType

from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem
from atklip.controls import VWMA
from atklip.appmanager import FastWorker
from atklip.app_utils import *
from atklip.controls.models import VWMAModel
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart



class BASE_VWMA(PlotDataItem):
    """DEMA EMA HMA SMA SMMA TEMA TRIX ZLEMA WMA"""
    on_click = Signal(object)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    sig_change_indicator_name = Signal(str)

    def __init__(self,chart) -> None:
        """Choose colors of candle"""
        super().__init__()
    
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        
        self.setZValue(700)
        self.chart:Chart = chart

        self.has = {
            "name": f"VWMA 10",
            "y_axis_show":False,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name":self.chart.jp_candle.source_name,
                    "type":"close",
                    "length":10,
                    "show":True
                    },

            "styles":{
                    'pen': "orange",
                    'width': 1,
                    'style': Qt.PenStyle.SolidLine,}
        }
        
        self.id = self.chart.objmanager.add(self)
        
        self.opts.update({'pen':"orange"})
        
        self.is_reset = False
        
        self.INDICATOR  = VWMA(self.has["inputs"]["source"], self.model.__dict__)
        
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
        return VWMAModel(self.id,"VWMA",self.chart.jp_candle.source_name,
                         self.has["inputs"]["type"],
                         self.has["inputs"]["length"])
    
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
       
    def delete(self):
        self.INDICATOR.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        _index,_data = self.INDICATOR.get_data()
        setdata.emit((_index,_data))
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"VWMA {self.has["inputs"]["length"]} {self.has["inputs"]["type"]}"
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
                self.INDICATOR.change_input(self.has["inputs"]["source"])
        else:
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True

        if is_update:
            self.has["name"] = f"VWMA {self.has["inputs"]["length"]} {self.has["inputs"]["type"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            
            self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)
            
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
        return _value,"#363a45"
    
    def get_xaxis_param(self):
        return None,"#363a45"

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()  
    
    def get_last_point(self):
        df = self.INDICATOR.get_df(2)
        _time = df["index"].iloc[-1]
        _value = df["data"].iloc[-1]
        return _time,_value
    
    
    def set_Data(self,data):
        xData = data[0]
        yData = data[1]
        self.setData(xData, yData)
        self.INDICATOR.is_current_update = True
    
    def add_historic_Data(self,data):
        xData = data[0]
        yData = data[1]
        self.addHistoricData(xData, yData)
        self.INDICATOR.is_current_update = True
    
    def update_Data(self,data):
        xData = data[0]
        yData = data[1]
        self.updateData(xData, yData)
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
        _index,_data = self.INDICATOR.get_data(stop=_len)
        setdata.emit((_index,_data))   
             
    def add_data(self,setdata):
        _index,_data = self.INDICATOR.get_data(start=-1)
        setdata.emit((_index,_data))  
        # setdata.emit((_index,_data))  
    def update_data(self,setdata):
        _index,_data = self.INDICATOR.get_data(start=-1)
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
        self.name = name

    def objectName(self):
        return self.name
    
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