import time
from typing import Tuple, List, TYPE_CHECKING
import numpy as np
from atklip.graphics.pyqtgraph import PlotDataItem
from atklip.graphics.chart_component.base_items import PriceLine

from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtWidgets import QGraphicsItem

from atklip.controls import PD_MAType,IndicatorType,RSI

from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel
class BasicRSI(PlotDataItem):
    """RSI"""
    on_click = Signal(QObject)

    last_pos = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    sig_change_yaxis_range = Signal()
    
    sig_change_indicator_name = Signal(str)

    def __init__(self,get_last_pos_worker, chart,panel,id = None,clickable=True) -> None:
        """Choose colors of candle"""
        super().__init__(clickable=clickable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self._panel:ViewSubPanel = panel

        self._precision = self.chart._precision
        
        self.has = {
            "name" :f"RSI 3",
            "y_axis_show":F,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "type":"close",
                    "indicator_type":IndicatorType.RSI,
                    "period":3,
                    "ma_type":PD_MAType.RMA,
                    "price_high":80,
                    "price_low":20,
                    "show":True},

            "styles":{
                    'pen': "yellow",
                    'width': 1,
                    'style': Qt.PenStyle.SolidLine,}
                }
        
        self.opts.update({'pen':"yellow"})

        self.id = id

        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)

        self.is_reset = False
        self.price_line = PriceLine()  # for z value
        self.price_line.setParentItem(self)
        self.destroyed.connect(self.price_line.deleteLater)
        self.last_pos.connect(self.price_line.update_price_line_indicator,Qt.ConnectionType.AutoConnection)

        self.price_high = PriceLine(color="green",width=2,movable=True)  # for z value
        self.price_high.setParentItem(self)
        self.price_high.setPos(self.has["inputs"]["price_high"])
        
        self.price_low = PriceLine(color="red",width=2,movable=True)  # for z value
        self.price_low.setParentItem(self)
        self.price_low.setPos(self.has["inputs"]["price_low"])
        
        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)
        
        self.Indicator  = RSI(parent=self,
                               _candles=self.has["inputs"]["source"], 
                                source=self.has["inputs"]["type"],
                                length=self.has["inputs"]["period"],
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
            self.Indicator.sig_add_candle.disconnect(self.setdata_worker)
            self.Indicator.signal_delete.disconnect(self.replace_source)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.Indicator.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.Indicator.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.Indicator.sig_add_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
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
        xdata,y_data= self.Indicator.get_data()
        setdata.emit((xdata,y_data))
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"RSI {self.has["inputs"]["period"]} {self.has["inputs"]["type"]}"
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
                    "period":self.has["inputs"]["period"],
                    "ma_type":self.has["inputs"]["ma_type"],
                    "price_high":self.has["inputs"]["price_high"],
                    "price_low":self.has["inputs"]["price_low"]}
        return inputs
    
    def get_styles(self):
        styles =  {"pen":self.has["styles"]["pen"],
                    "width":self.has["styles"]["width"],
                    "style":self.has["styles"]["style"],}
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
            self.has["name"] = f"RSI {self.has["inputs"]["period"]} {f"{self.has["inputs"]["ma_type"].name}".lower()} {self.has["inputs"]["type"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.Indicator.change_inputs(_input,_source)
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen" or _input == "width" or _input == "style":
            self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"])

    
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
        self.worker.start()
    
    def load_historic_data(self,setdata):
        _index,_data = self.Indicator.get_data()
        setdata.emit((_index,_data))
    
    def set_Data(self,data):
        xData = data[0]
        yData = data[1]
        try:
            self.setData(xData, yData)
        except Exception as e:
            pass
        # 
        # self.prepareGeometryChange()
        # self.informViewBoundsChanged()

    def update_data(self,setdata):
        xdata,y_data = self.Indicator.get_data()
        setdata.emit((xdata,y_data))
        self.last_pos.emit((IndicatorType.RSI,y_data[-1]))
        self._panel.sig_update_y_axis.emit()

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
        
    #     if self.yData is None:
    #         h_low,h_high = self._panel.yAxis.range[0],self._panel.yAxis.range[1]
    #     elif self.yData.size != 0:
    #         h_low,h_high = np.nanmin(self.yData), np.nanmax(self.yData) 
    #     else:
    #         h_low,h_high = self._panel.yAxis.range[0],self._panel.yAxis.range[1]
    #     rect = QRectF(self._start,h_low,self._stop-self._start,h_high-h_low)
    #     return rect  
    def get_last_point(self):
        _time = self.xData[-1]
        _value = self.yData[-1]
        return _time,round(_value,3)
    
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
        return _value, "#363a45"
    

    
   