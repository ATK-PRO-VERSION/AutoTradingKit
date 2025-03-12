import time
from typing import Tuple, List,TYPE_CHECKING
import numpy as np
from atklip.graphics.pyqtgraph import GraphicsObject
from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem

from atklip.graphics.chart_component.base_items import PriceLine
from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtGui import QColor,QPicture,QPainter
from PySide6.QtWidgets import QGraphicsItem

from atklip.controls import PD_MAType,IndicatorType, MACD
from atklip.controls.models import MACDModel

from .macd_histogram import MACDHistogram
from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel
    
class BasicMACD(GraphicsObject):
    """RSI"""
    on_click = Signal(object)

    last_pos = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    sig_change_yaxis_range = Signal()
    
    sig_change_indicator_name = Signal(str)

    def __init__(self,get_last_pos_worker,chart,panel) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self._panel:ViewSubPanel = panel

        self._precision = self.chart._precision
        
        self.has: dict = {
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
                    "mamode":PD_MAType.RMA,
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
     
        self.id = self.chart.objmanager.add(self)
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
        
        self.price_high = PriceLine(color="green",width=1,movable=True)  # for z value
        self.price_high.setParentItem(self)
        self.price_high.setPos(self.has["inputs"]["price_high"])
        
        self.price_low = PriceLine(color="red",width=1,movable=True)  # for z value
        self.price_low.setParentItem(self)
        self.price_low.setPos(self.has["inputs"]["price_low"])
        
        self.histogram = MACDHistogram(self.chart,self._panel,self.has)
        self.histogram.setParentItem(self)

        self.picture: QPicture = QPicture()
        
        self.last_pos.connect(self.price_line.update_price_line_indicator,Qt.ConnectionType.AutoConnection)

        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)
        
        self.INDICATOR  = MACD(self.has["inputs"]["source"], self.model.__dict__)
        
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
    def model(self):
        return MACDModel(self.id,"MACD",self.chart.jp_candle.source_name,
                        self.has["inputs"]["type"],
                        self.has["inputs"]["slow_period"],
                        self.has["inputs"]["fast_period"],
                        self.has["inputs"]["signal_period"],
                        self.has["inputs"]["mamode"].name.lower())
    
    
    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_indicator)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.add_worker)
            self.INDICATOR.signal_delete.disconnect(self.replace_source)
            self.INDICATOR.sig_add_historic.disconnect(self.add_historic_worker)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.INDICATOR.sig_reset_all.connect(self.reset_indicator,Qt.ConnectionType.AutoConnection)
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
    
    def reset_histogram(self,data):
        xdata,histogram = data[0], data[3]
        self.histogram.sig_reset_histogram.emit((xdata,histogram),"reset")
        
    def reset_indicator(self):
        self.fisrt_setup = True
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        xdata,lb,cb,ub= self.INDICATOR.get_data()
        self.reset_histogram((xdata,lb,cb,ub))
        setdata.emit((xdata,lb,cb,ub))
        self.has["name"] = f"""MACD {self.has["inputs"]["mamode"].name} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["signal_period"]} {self.has["inputs"]["type"]}"""
        self.sig_change_indicator_name.emit(self.has["name"])
        
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
      
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "type":self.has["inputs"]["type"],
                    "fast_period":self.has["inputs"]["fast_period"],
                    "slow_period":self.has["inputs"]["slow_period"],
                    "signal_period":self.has["inputs"]["signal_period"],
                    "mamode":self.has["inputs"]["mamode"],
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
                "mamode":self.has["inputs"]["mamode"],
                "ma_period":self.has["inputs"]["ma_period"]"""
        update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.INDICATOR.change_input(self.has["inputs"]["source"])
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
            self.has["name"] = f"""MACD {self.has["inputs"]["mamode"].name} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["signal_period"]} {self.has["inputs"]["type"]}"""
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)
    
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen_macd_line" or _input == "width_macd_line" or _input == "style_macd_line":
            self.macd_line.setPen(color=self.has["styles"]["pen_macd_line"], width=self.has["styles"]["width_macd_line"],style=self.has["styles"]["style_macd_line"])
        elif _input == "pen_signal_line" or _input == "width_signal_line" or _input == "style_signal_line":
            self.signal.setPen(color=self.has["styles"]["pen_signal_line"], width=self.has["styles"]["width_signal_line"],style=self.has["styles"]["style_signal_line"])
        elif _input == "pen_high_historgram" or _input == "pen_low_historgram" or _input == "brush_high_historgram" or _input == "brush_low_historgram":
            xdata,macd,signalma,histogram= self.INDICATOR.get_data()
            self.histogram.update_styles(_input,(xdata,histogram))
    
    def get_xaxis_param(self):
        return None,"#363a45"


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
    
    def set_Data(self,data):
        xData = data[0]
        lb = data[1]
        cb = data[2]
        histogram = data[3]

        self.histogram.sig_update_histogram.emit((xData[-2:],histogram[-2:]),"add")
        
        self.macd_line.setData(xData,lb)
        self.signal.setData(xData,cb)
        if self.fisrt_setup:
            self.fisrt_setup = False
            self.sig_change_yaxis_range.emit()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.INDICATOR.is_current_update = True
    
    def add_historic_Data(self,data):
        xData = data[0]
        lb = data[1]
        cb = data[2]
        histogram = data[3]
        
        print(len(xData),len(lb),len(cb),len(histogram))
        
        self.histogram.sig_load_historic_histogram.emit((xData,histogram),"load_historic")
        self.macd_line.addHistoricData(xData,lb)
        self.signal.addHistoricData(xData,cb)
        self.INDICATOR.is_current_update = True

        
    def update_Data(self,data):
        xData = data[0]
        lb = data[1]
        cb = data[2]
        histogram = data[3]
        
        self.histogram.sig_update_histogram.emit((xData,histogram),"add")
        
        self.macd_line.updateData(xData,lb)
        self.signal.updateData(xData,cb)
        self.INDICATOR.is_current_update = True
    
    def add_Data(self,data):
        xData = data[0]
        lb = data[1]
        cb = data[2]
        histogram = data[3]
        
        self.histogram.sig_add_histogram.emit((xData, histogram),"add")
        self.macd_line.updateData(xData,lb)
        self.signal.updateData(xData,cb)
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
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.add_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()    
    
    def load_historic_data(self,_len,setdata):        
        xdata,macd,signalma,histogram= self.INDICATOR.get_data(stop=_len)
        setdata.emit((xdata,macd,signalma,histogram))

    
    def update_data(self,setdata):
        xdata,macd,signalma,histogram= self.INDICATOR.get_data(start=-2)
        setdata.emit((xdata,macd,signalma,histogram))
        self.last_pos.emit((self.has["inputs"]["indicator_type"],signalma[-1]))
        self._panel.sig_update_y_axis.emit() 
    
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
        df = self.INDICATOR.get_df(2)
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
