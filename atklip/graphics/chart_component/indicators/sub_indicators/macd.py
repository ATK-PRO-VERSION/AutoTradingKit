import time
from typing import Tuple, List,TYPE_CHECKING
import numpy as np
from atklip.graphics.pyqtgraph import GraphicsObject, PlotDataItem
from atklip.graphics.chart_component.base_items import PriceLine
from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtGui import QColor,QPicture,QPainter
from PySide6.QtWidgets import QGraphicsItem

from atklip.controls import PD_MAType,IndicatorType, MACD

from .macd_histogram import MACDHistogram
from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel
    
class BasicMACD(GraphicsObject):
    """RSI"""
    on_click = Signal(QObject)

    last_pos = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    sig_change_yaxis_range = Signal()
    
    sig_change_indicator_name = Signal(str)

    def __init__(self,get_last_pos_worker,chart,panel,id = None) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self._panel:ViewSubPanel = panel

        self._precision = self.chart._precision
        
        self.has = {
            "name": f"MACD 9 12 26",
            "y_axis_show":True,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "type":"close",
                    "indicator_type":IndicatorType.MACD,
                    "fast_period":12,
                    "slow_period":26,
                    "signal_period":9,
                    "ma_type":PD_MAType.EMA,
                    "price_high":60,
                    "price_low":-60,
                    "show":True},

            "styles":{
                    'pen_macd_line': "red",
                    'width_macd_line': 1,
                    'style_macd_line': Qt.PenStyle.SolidLine,
                    'pen_signal_line': "orange",
                    'width_signal_line': 1,
                    'style_signal_line': Qt.PenStyle.SolidLine,
                    "pen_high_historgram": '#089981',
                    "pen_low_historgram" : '#f23645',
                    "brush_high_historgram":mkBrush('#089981',width=0.7),
                    "brush_low_historgram":mkBrush('#f23645',width=0.7)
                    }
                    }
     
        self.id = id
        self.fisrt_setup = False

        self.on_click.connect(self.on_click_event)
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        
        self.macd_line = PlotDataItem(pen="red")  # for z value
        self.macd_line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.macd_line.setParentItem(self)
        self.signal = PlotDataItem(pen="orange")
        self.signal.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.signal.setParentItem(self)
        
        

        self.price_line = PriceLine()  # for z value
        self.price_line.setParentItem(self)
        
        self.price_high = PriceLine(color="green",width=2,movable=True)  # for z value
        self.price_high.setParentItem(self)
        self.price_high.setPos(self.has["inputs"]["price_high"])
        
        self.price_low = PriceLine(color="red",width=2,movable=True)  # for z value
        self.price_low.setParentItem(self)
        self.price_low.setPos(self.has["inputs"]["price_low"])
        
        self.histogram = MACDHistogram(self.chart,self._panel,self.has)
        self.histogram.setParentItem(self)

        self.picture: QPicture = QPicture()
        
        self.last_pos.connect(self.price_line.update_price_line_indicator,Qt.ConnectionType.AutoConnection)

        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)
        
        self.Indicator  = MACD(parent=self,
                               _candles=self.has["inputs"]["source"], 
                                source=self.has["inputs"]["type"],
                                fast_period=self.has["inputs"]["fast_period"],
                                slow_period=self.has["inputs"]["slow_period"],
                                signal_period=self.has["inputs"]["signal_period"],
                                ma_type=self.has["inputs"]["ma_type"])
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
        self.object_id = self.chart.objmanager.add(self)
    @property
    def id(self):
        return self.object_id
        
    def disconnect_signals(self):
        try:
            self.Indicator.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.Indicator.sig_update_candle.disconnect(self.setdata_worker)
            self.Indicator.sig_add_candle.disconnect(self.add_worker)
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
    
    def update_histogram(self,data):
        self.histogram.sig_update_histogram.emit(data)
    
    def reset_histogram(self,data):
        xdata,histogram = data[0], data[3]
        self.histogram.sig_reset_histogram.emit((xdata,histogram),"reset")
        
    
    def add_historic_histogram(self,data):
        xdata,histogram = data[0], data[3]
        self.histogram.sig_load_historic_histogram.emit((xdata,histogram),"load_historic")
    
    def add_histogram(self,data):
        xdata,histogram = data[0][-3:-1], data[3][-3:-1]
        self.histogram.sig_add_histogram.emit((xdata,histogram),"add")
    
    def reset_indicator(self):
        self.fisrt_setup = True
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        xdata,lb,cb,ub= self.Indicator.get_data()
        self.reset_histogram((xdata,lb,cb,ub))
        setdata.emit((xdata,lb,cb,ub))
        self.has["name"] = f"MACD {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["signal_period"]} {self.has["inputs"]["type"]}"
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
                    "fast_period":self.has["inputs"]["fast_period"],
                    "slow_period":self.has["inputs"]["slow_period"],
                    "signal_period":self.has["inputs"]["signal_period"],
                    "ma_type":self.has["inputs"]["ma_type"],
                    "price_high":self.has["inputs"]["price_high"],
                    "price_low":self.has["inputs"]["price_low"]}
        return inputs
    
    def get_styles(self):
        styles =  {"pen_macd_line":self.has["styles"]["pen_macd_line"],
                    "width_macd_line":self.has["styles"]["width_macd_line"],
                    "style_macd_line":self.has["styles"]["style_macd_line"],
                    "pen_signal_line":self.has["styles"]["pen_signal_line"],
                    "width_signal_line":self.has["styles"]["width_signal_line"],
                    "style_signal_line":self.has["styles"]["style_signal_line"],
                    "pen_high_historgram":self.has["styles"]["pen_high_historgram"],
                    "pen_low_historgram":self.has["styles"]["pen_low_historgram"],
                    "brush_high_historgram":self.has["styles"]["brush_high_historgram"],
                    "brush_low_historgram":self.has["styles"]["brush_low_historgram"],}
        return styles
    
    def update_inputs(self,_input,_source):
        """"source":self.has["inputs"]["source"],
                "ma_type":self.has["inputs"]["ma_type"],
                "ma_period":self.has["inputs"]["ma_period"]"""
        update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.Indicator.change_inputs(_input,self.has["inputs"]["source"])
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
            self.has["name"] = f"MACD {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["signal_period"]} {self.has["inputs"]["type"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.Indicator.change_inputs(_input,_source)
    
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen_macd_line" or _input == "width_macd_line" or _input == "style_macd_line":
            self.macd_line.setPen(color=self.has["styles"]["pen_macd_line"], width=self.has["styles"]["width_macd_line"],style=self.has["styles"]["style_macd_line"])
        elif _input == "pen_signal_line" or _input == "width_signal_line" or _input == "style_signal_line":
            self.signal.setPen(color=self.has["styles"]["pen_signal_line"], width=self.has["styles"]["width_signal_line"],style=self.has["styles"]["style_signal_line"])
        elif _input == "pen_high_historgram" or _input == "pen_low_historgram" or _input == "brush_high_historgram" or _input == "brush_low_historgram":
            xdata,macd,signalma,histogram= self.Indicator.get_data()
            self.histogram.update_styles(_input,(xdata,histogram))
    
    def get_xaxis_param(self):
        return None,"#363a45"


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.start()    
    
    def add_historic_worker(self):
        self.worker = None
        self.worker = FastWorker(self.load_historic_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.signals.setdata.connect(self.add_historic_histogram,Qt.ConnectionType.QueuedConnection)
        self.worker.start() 
    
    def add_worker(self):
        self.worker = None
        self.worker = FastWorker(self.add_data)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.QueuedConnection)
        self.worker.signals.setdata.connect(self.add_histogram,Qt.ConnectionType.QueuedConnection)
        self.worker.start()    
    
    def load_historic_data(self,setdata):
        xdata,macd,signalma,histogram= self.Indicator.get_data()
        setdata.emit((xdata,macd,signalma,histogram))
        self.last_pos.emit((self.has["inputs"]["indicator_type"],signalma[-1]))
        self._panel.sig_update_y_axis.emit() 
    
    def update_data(self,setdata):
        xdata,macd,signalma,histogram= self.Indicator.get_data()
        setdata.emit((xdata,macd,signalma,histogram))
        self.last_pos.emit((self.has["inputs"]["indicator_type"],signalma[-1]))
        self._panel.sig_update_y_axis.emit() 
    
    def add_data(self,setdata):
        xdata,macd,signalma,histogram= self.Indicator.get_data()
        setdata.emit((xdata,macd,signalma,histogram))
        self.last_pos.emit((self.has["inputs"]["indicator_type"],signalma[-1]))
        self._panel.sig_update_y_axis.emit()  
    
    
    def set_Data(self,data):
        xData = data[0]
        lb = data[1]
        cb = data[2]
        histogram = data[3]
        self.update_histogram((xData[-2:],histogram[-2:]))
        try:
            self.macd_line.setData(xData,lb)
            self.signal.setData(xData,cb)
            if self.fisrt_setup:
                self.fisrt_setup = False
                self.sig_change_yaxis_range.emit()
        except Exception as e:
            pass
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()

    def boundingRect(self) -> QRectF:
        return self.histogram.boundingRect()
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
    
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
    
    def get_last_point(self):
        df = self.Indicator.get_df(2)
        _time = df["index"].iloc[-1]
        _value = df["macd"].iloc[-1]
        return _time,_value
    
    def get_min_max(self):
        _min = None
        _max = None
        try:
            if len(self.signal.yData) > 0:
                _min, _max = np.nanmin(self.signal.yData), np.nanmax(self.signal.yData)
                return _min,_max
        except Exception as e:
            pass
        time.sleep(0.1)
        self.get_min_max()
        return _min,_max

    def on_click_event(self):
        print("zooo day__________________")
        pass

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mousePressEvent(ev)

    def setObjectName(self, name):
        self.indicator_name = name

    def objectName(self):
        return self.indicator_name
