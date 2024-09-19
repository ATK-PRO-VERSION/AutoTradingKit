from typing import TYPE_CHECKING
import numpy as np
from atklip.graphics.pyqtgraph import GraphicsObject, PlotDataItem
from atklip.graphics.chart_component.base_items import PriceLine
from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtGui import QPicture,QPainter
from PySide6.QtWidgets import QGraphicsItem

from atklip.controls import PD_MAType,IndicatorType,TSI

from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel
    
class BasicTSI(GraphicsObject):
    """RSI"""
    on_click = Signal(QObject)

    last_pos = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    sig_change_yaxis_range = Signal()
    
    sig_change_indicator_name = Signal(str)

    def __init__(self,get_last_pos_worker,chart,panel,id = None,clickable=True) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        #super().__init__(clickable=clickable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self._panel:ViewSubPanel = panel

        self._precision = self.chart._precision
        
        self.has = {
            "name": f"TSI 9 12 26",
            "y_axis_show":True,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "type":"close",
                    "indicator_type":IndicatorType.TSI,
                    "fast_period":13,
                    "slow_period":25,
                    "signal_period":13,
                    "ma_type":PD_MAType.EMA,
                    "price_high":20,
                    "price_low":-20,
                    "show":True},

            "styles":{
                    'pen_tsi_line': "red",
                    'width_tsi_line': 1,
                    'style_tsi_line': Qt.PenStyle.SolidLine,
                    'pen_signal_line': "orange",
                    'width_signal_line': 1,
                    'style_signal_line': Qt.PenStyle.SolidLine,
                    }
                    }
     
        self.id = id
        

        self.on_click.connect(self.on_click_event)
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        
        self.tsi_line = PlotDataItem(pen="red")  # for z value
        self.tsi_line.setParentItem(self)
        self.signal = PlotDataItem(pen="orange")
        self.signal.setParentItem(self)
        
        self.price_line = PriceLine()  # for z value
        self.price_line.setParentItem(self)
        
        self.price_high = PriceLine(color="green",width=2,movable=True)  # for z value
        self.price_high.setParentItem(self)
        self.price_high.setPos(self.has["inputs"]["price_high"])
        
        self.price_low = PriceLine(color="red",width=2,movable=True)  # for z value
        self.price_low.setParentItem(self)
        self.price_low.setPos(self.has["inputs"]["price_low"])
        
        self.picture: QPicture = QPicture()
        
        self.last_pos.connect(self.price_line.update_price_line_indicator,Qt.ConnectionType.AutoConnection)

        self.worker = None
        
        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)
        
        self.INDICATOR  = TSI(parent=self,
                                _candles=self.has["inputs"]["source"],
                                source=  self.has["inputs"]["type"],
                                fast_period=self.has["inputs"]["fast_period"],
                                slow_period=self.has["inputs"]["slow_period"],
                                signal_period=self.has["inputs"]["signal_period"],
                                ma_type=self.has["inputs"]["ma_type"])
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.setdata_worker)
            self.INDICATOR.signal_delete.disconnect(self.replace_source)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.INDICATOR.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
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
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
    

    def regen_indicator(self,setdata):
        xdata,tsi,signalma= self.INDICATOR.get_data()  
        self.has["name"] = f"TSI {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["signal_period"]} {self.has["inputs"]["type"]}"
        self.sig_change_indicator_name.emit(self.has["name"])
        setdata.emit((xdata,tsi,signalma))
        self.sig_change_yaxis_range.emit()
         
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
    def reset_threadpool_asyncworker(self):
        self.reset_indicator()
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
    
    def update_inputs(self,_input,_source):
        """"source":self.has["inputs"]["source"],
                "ma_type":self.has["inputs"]["ma_type"],
                "ma_period":self.has["inputs"]["ma_period"]"""
        update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.INDICATOR.change_inputs(_input,self.has["inputs"]["source"])
        elif _input == "price_high":
            if _source != self.has["inputs"]["price_high"]:
                self.has["inputs"]["price_high"] = _source
                self.price_high.setPos(_source)
        elif _input == "price_low":
            if _source != self.has["inputs"]["price_low"]:
                self.has["inputs"]["price_low"] = _source
                self.price_low.setPos(_source)
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                update = True
        if update:
            self.has["name"] = f"TSI {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["signal_period"]} {self.has["inputs"]["type"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_inputs(_input,_source)

    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()    


    def update_data(self,setdata):
        xdata,tsi,signalma = self.INDICATOR.get_data()
        setdata.emit((xdata,tsi,signalma))
        self.last_pos.emit((self.has["inputs"]["indicator_type"],signalma[-1]))
        self._panel.sig_update_y_axis.emit()
        

    "old___________"
    
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "type":self.has["inputs"]["type"],
                    "fast_period":self.has["inputs"]["fast_period"],
                    "slow_period":self.has["inputs"]["slow_period"],
                    "signal_period":self.has["inputs"]["signal_period"],
                    "ma_type":self.has["inputs"]["ma_type"],
                    "price_high":self.has["inputs"]["price_high"],
                    "price_low":self.has["inputs"]["price_low"]}
        return inputs
    
    def get_styles(self):
        styles =  {"pen_tsi_line":self.has["styles"]["pen_tsi_line"],
                    "width_tsi_line":self.has["styles"]["width_tsi_line"],
                    "style_tsi_line":self.has["styles"]["style_tsi_line"],
                    "pen_signal_line":self.has["styles"]["pen_signal_line"],
                    "width_signal_line":self.has["styles"]["width_signal_line"],
                    "style_signal_line":self.has["styles"]["style_signal_line"],
                   }
        return styles

    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen_tsi_line" or _input == "width_tsi_line" or _input == "style_tsi_line":
            self.tsi_line.setPen(color=self.has["styles"]["pen_tsi_line"], width=self.has["styles"]["width_tsi_line"],style=self.has["styles"]["style_tsi_line"])
        elif _input == "pen_signal_line" or _input == "width_signal_line" or _input == "style_signal_line":
            self.signal.setPen(color=self.has["styles"]["pen_signal_line"], width=self.has["styles"]["width_signal_line"],style=self.has["styles"]["style_signal_line"])
        
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

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
    
    def boundingRect(self) -> QRectF:
        return self.signal.boundingRect()
    
    def boundingRect(self) -> QRectF:
        x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
        start_index = self.chart.jp_candle.candles[0].index
        stop_index = self.chart.jp_candle.candles[-1].index
        if x_left > start_index:
            self._start = x_left+2
        else:
            self._start = start_index+2
        if x_right < stop_index:
            self._stop = x_right
        else:
            self._stop = stop_index
        
        if self.signal.yData is None:
            h_low,h_high = self._panel.yAxis.range[0],self._panel.yAxis.range[1]
        elif self.signal.yData.size != 0:
            h_low,h_high = np.nanmin(self.signal.yData), np.nanmax(self.signal.yData) 
        else:
            h_low,h_high = self._panel.yAxis.range[0],self._panel.yAxis.range[1]
        rect = QRectF(self._start,h_low,self._stop-self._start,h_high-h_low)
        return rect   
    
    def set_Data(self,data):
        xData = data[0]
        lb = data[1]
        cb = data[2]

        try:
            self.tsi_line.setData(xData,lb)
            self.signal.setData(xData,cb)
        except Exception as e:
            pass
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        
    def get_last_point(self):
        _time = self.signal.xData[-1]
        _value = self.signal.yData[-1]
        return _time,_value
    
    def get_min_max(self):
        _min = None
        _max = None
        try:
            if len(self.signal.yData) > 0:
                _min, _max = np.nanmin(self.signal.yData), np.nanmax(self.signal.yData)
                if _min == np.nan or _max == np.nan:
                    return None, None
                return _min,_max
        except Exception as e:
            pass
        time.sleep(0.1)
        self.get_min_max()
        return _min,_max

    def on_click_event(self):
        print("zooo day__________________")
        pass