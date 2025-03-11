import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture

from .fillbetweenitem import FillBetweenItem
from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem
from atklip.graphics.pyqtgraph import GraphicsObject

from atklip.controls import PD_MAType,IndicatorType,BBANDS
from atklip.controls.models import SuperTrendModel
from atklip.controls.overlap.supertrend import SuperTrend


from atklip.graphics.chart_component.base_items import SuperTrendLine

from atklip.appmanager import FastWorker
from atklip.app_utils import *

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart


class BasicSuperTrend(GraphicsObject):
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart) -> None:
        GraphicsObject.__init__(self)
        # super().__init__()
        # self.setFlag(self.GraphicsItemFlag.ItemHasNoContents)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self.has = {
            "name": f"BB 20 2",
            "y_axis_show":False,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    
                    "supertrend_length" :14,
                    "supertrend_atr_length":14,
                    "supertrend_multiplier" :3.0,
                    "supertrend_atr_mamode" :PD_MAType.RMA, 
                     
                    "indicator_type":IndicatorType.SuperTrend,
                    "show":False},

            "styles":{
                    'pen_high_line': "green",
                    'width_high_line': 1,
                    'style_high_line': Qt.PenStyle.SolidLine,
                    
                    'pen_low_line': "red",
                    'width_low_line': 1,
                    'style_low_line': Qt.PenStyle.SolidLine,
                    
                    }
                    }
        self.id = self.chart.objmanager.add(self)
        
        self.lowline = SuperTrendLine(self.chart,"red")  # for z value
        self.lowline.setParentItem(self)

        self.highline = SuperTrendLine(self.chart,"green")
        self.highline.setParentItem(self)
        
     
        self.picture: QPicture = QPicture()
                
        self.INDICATOR  = SuperTrend(self.has["inputs"]["source"], self.model.__dict__)
        
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
        return SuperTrendModel(self.id,"SuperTrend",self.chart.jp_candle.source_name,
                    self.has["inputs"]["supertrend_length"],
                    self.has["inputs"]["supertrend_atr_length"],
                    self.has["inputs"]["supertrend_multiplier"],
                    self.has["inputs"]["supertrend_atr_mamode"].name.lower()
                    )
    
    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_historic.disconnect(self.add_historic_worker)
            self.INDICATOR.signal_delete.disconnect(self.replace_source)
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
        x_data,SUPERTt,SUPERTd= self.INDICATOR.get_data()
        setdata.emit((x_data,SUPERTt,SUPERTd))
        
        self.has["name"] = f"SupperTrend {self.has["inputs"]["supertrend_length"]} {self.has["inputs"]["supertrend_atr_length"]} {self.has["inputs"]["supertrend_multiplier"]} {self.has["inputs"]["supertrend_atr_mamode"].name}"
        self.sig_change_indicator_name.emit(self.has["name"])
        
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
    def reset_threadpool_asyncworker(self):
        self.highline._is_change_source=True
        self.lowline._is_change_source=True
        self.reset_indicator()
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)

    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "supertrend_length":self.has["inputs"]["supertrend_length"],
                    "supertrend_atr_length":self.has["inputs"]["supertrend_atr_length"],
                    "supertrend_multiplier":self.has["inputs"]["supertrend_multiplier"],
                    "supertrend_atr_mamode":self.has["inputs"]["supertrend_atr_mamode"],
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
                is_update = True

        if is_update:
            self.has["name"] = f"SupperTrend {self.has["inputs"]["supertrend_length"]} {self.has["inputs"]["supertrend_atr_length"]} {self.has["inputs"]["supertrend_multiplier"]} {self.has["inputs"]["supertrend_atr_mamode"].name}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        return
    
    
    def get_xaxis_param(self):
        return None,"#363a45"


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
    
    def set_Data(self,data):
        x_data,SUPERTt,SUPERTd = data[0],data[1],data[2]
        self.lowline.setData((x_data,SUPERTt,SUPERTd))
        self.highline.setData((x_data,SUPERTt,SUPERTd))
        self.INDICATOR.is_current_update = True
    
    def add_historic_Data(self,data):
        x_data,SUPERTt,SUPERTd = data[0],data[1],data[2]
        self.lowline.setData((x_data,SUPERTt,SUPERTd))
        self.highline.setData((x_data,SUPERTt,SUPERTd))
        self.INDICATOR.is_current_update = True

        
    def update_Data(self,data):
        x_data,SUPERTt,SUPERTd = data[0],data[1],data[2]
        self.lowline.updateData((x_data,SUPERTt,SUPERTd))
        self.highline.updateData((x_data,SUPERTt,SUPERTd))
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
        x_data,SUPERTt,SUPERTd = self.INDICATOR.get_data(stop=_len)
        setdata.emit((x_data,SUPERTt,SUPERTd))
        

    def add_data(self,setdata):
        x_data,SUPERTt,SUPERTd= self.INDICATOR.get_data(start=-3)
        setdata.emit((x_data,SUPERTt,SUPERTd))
        
    
    def update_data(self,setdata):
        x_data,SUPERTt,SUPERTd= self.INDICATOR.get_data(start=-3)
        setdata.emit((x_data,SUPERTt,SUPERTd))

    def boundingRect(self) -> QRectF:
        return self.lowline.boundingRect()
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
    
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return _value,"#363a45"
    
    
    def get_last_point(self):
        return None,None
    
    def get_min_max(self):
        try:
            return None,None
        except Exception as e:
            pass
        return None,None

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
    

