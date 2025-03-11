import time
from typing import Tuple, List,TYPE_CHECKING
import numpy as np
from atklip.graphics.pyqtgraph import GraphicsObject, PlotDataItem
from atklip.graphics.chart_component.base_items import PriceLine
from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtGui import QColor,QPicture,QPainter
from PySide6.QtWidgets import QGraphicsItem

from atklip.controls import PD_MAType,IndicatorType,ZIGZAG

from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel
    
class BasicZIGZAG(PlotDataItem):
    """RSI"""
    on_click = Signal(object)

    last_pos = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    sig_change_yaxis_range = Signal()
    
    sig_change_indicator_name = Signal(str)

    def __init__(self,chart) -> None:
        """Choose colors of candle"""
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart

        self._precision = self.chart._precision
        
        self.has = {
            "name": f"ZIGZAG 10 1",
            "y_axis_show":False,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "indicator_type":IndicatorType.ZIGZAG,
                    "legs":5,
                    "deviation":0.5,
                    "show":True},

            "styles":{
                    'pen_zz_line': "red",
                    'width_zz_line': 1,
                    'style_zz_line': Qt.PenStyle.SolidLine
                    }
                    }
     
        self.id = self.chart.objmanager.add(self)
        
        self.on_click.connect(self.on_click_event)
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        
        self.setPen(color="red")
        
        
        self.picture: QPicture = QPicture()
        
        self.worker = None
        
        
        self.INDICATOR  = ZIGZAG(parent=self,
                                _candles=self.has["inputs"]["source"], 
                                legs =self.has["inputs"]["legs"],
                                deviation= self.has["inputs"]["deviation"]
                               )
        
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
        
    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.setdata_worker)
            self.INDICATOR.signal_delete.disconnect(self.replace_source)
            self.INDICATOR.sig_add_historic.disconnect(self.add_historic_worker)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.INDICATOR.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
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
    
  
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
    def reset_threadpool_asyncworker(self):
        self.reset_indicator()
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
    
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "legs":self.has["inputs"]["legs"],
                    "deviation":self.has["inputs"]["deviation"],}
        return inputs
    
    def get_styles(self):
        styles =  {"pen_zz_line":self.has["styles"]["pen_zz_line"],
                    "width_zz_line":self.has["styles"]["width_zz_line"],
                    "style_zz_line":self.has["styles"]["style_zz_line"],
                   }
        return styles
    
    
    def update_inputs(self,_input,_source):
        """"source":self.has["inputs"]["source"],
                "mamode":self.has["inputs"]["mamode"],
                "ma_period":self.has["inputs"]["ma_period"]"""
        update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.INDICATOR.change_inputs(_input,self.has["inputs"]["source"])
        elif _source != self.has["inputs"][_input]:
            if _input == "legs":
                if _source < 2:
                    print("ZigZag leg must be gratter than 2")
                    return
            self.has["inputs"][_input] = _source
            update = True
        if update:
            self.has["name"] = f"ZIGZAG {self.has["inputs"]["legs"]} {self.has["inputs"]["deviation"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_inputs(_input,_source)
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen_zz_line" or _input == "width_zz_line" or _input == "style_zz_line":
            self.setPen(color=self.has["styles"]["pen_zz_line"], width=self.has["styles"]["width_zz_line"],style=self.has["styles"]["style_zz_line"])
        
    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()    
    def add_historic_worker(self,_len):
        self.worker = None
        self.worker = FastWorker(self.load_historic_data,_len)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()
    def regen_indicator(self,setdata):
        xdata, zz_value = self.INDICATOR.get_data()
        setdata.emit((xdata,zz_value))   
        self.has["name"] = f"ZIGZAG {self.has["inputs"]["legs"]} {self.has["inputs"]["deviation"]}"
        self.sig_change_indicator_name.emit(self.has["name"])
        self.sig_change_yaxis_range.emit()
    def load_historic_data(self,_len,setdata):
        "zigzag do not need _len"
        xdata, zz_value = self.INDICATOR.get_data()
        setdata.emit((xdata,zz_value))
    def set_Data(self,data):
        xData = data[0]
        lb = data[1]
        try:
            self.setData(xData,lb)
        except Exception as e:
            pass
        self.INDICATOR.is_current_update = True
        # self.prepareGeometryChange()
        # self.informViewBoundsChanged()

    def update_data(self,setdata):
        xdata, zz_value = self.INDICATOR.get_data()
        setdata.emit((xdata,zz_value))
        self.INDICATOR.is_current_update = True
        # self.last_pos.emit((self.has["inputs"]["indicator_type"],stc[-1]))
        
    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mousePressEvent(ev)

    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name
    
    
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        if _value != None:
            if self._precision != None:
                _value = round(_value,self._precision)
            else:
                _value = round(_value,3)
        return _value,"#363a45"
    
    
    def get_xaxis_param(self):
        return None,"#363a45"

    
    def boundingRect(self) -> QRectF:
        x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
        start_index = self.chart.jp_candle.start_index
        stop_index = self.chart.jp_candle.stop_index
        if x_left > start_index:
            _start = x_left+2
        else:
            _start = start_index+2
        if x_right < stop_index:
            _width = x_right-_start
            _stop = x_right
        else:
            _width = stop_index-_start
            _stop = stop_index
        if self.yData is not None:
            if self.yData.size != 0:
                try:
                    h_low,h_high = np.nanmin(self.yData[_start:_stop]), np.nanmax(self.yData[_start:_stop])
                except ValueError:
                    h_low,h_high = int(self.chart.yAxis.range[0]),int(self.chart.yAxis.range[1])  
            else:
                h_low,h_high = self.chart.yAxis.range[0],self.chart.yAxis.range[1]
        else:
            h_low,h_high = self.chart.yAxis.range[0],self.chart.yAxis.range[1]
        rect = QRectF(_start,h_low,_width,h_high-h_low)
        return rect
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
    
    def get_last_point(self):
        _time = self.xData[-1]
        _value = self.yData[-1]
        return _time,_value
    
    def get_min_max(self):
        _min = None
        _max = None
        try:
            if len(self.yData) > 0:
                _min, _max = np.nanmin(self.yData), np.nanmax(self.yData)
                if _min == np.nan or _max == np.nan:
                    return None, None
                return _min,_max
        except Exception as e:
            pass
        time.sleep(0.1)
        self.get_min_max()
        return _min,_max

    def on_click_event(self):
        #print("zooo day__________________")
        pass
