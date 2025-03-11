import time
from typing import Tuple, List,TYPE_CHECKING
import numpy as np
from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem

from atklip.graphics.chart_component.base_items import PriceLine
from PySide6.QtCore import Signal, QObject,Qt,QRectF
from PySide6.QtGui import QColor,QPicture,QPainter
from PySide6.QtWidgets import QGraphicsItem

from atklip.controls import PD_MAType,IndicatorType,STC
from atklip.controls.models import STCModel

from atklip.appmanager import FastWorker
from atklip.app_utils import *
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel
    
class BasicSTC(PlotDataItem):
    """RSI"""
    on_click = Signal(object)

    last_pos = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    sig_change_yaxis_range = Signal()
    
    sig_change_indicator_name = Signal(str)

    def __init__(self,get_last_pos_worker,chart,panel) -> None:
        """Choose colors of candle"""
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self._panel:ViewSubPanel = panel

        self._precision = self.chart._precision
        
        self.has = {
            "name": f"STC 9 12 26",
            "y_axis_show":True,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "indicator_type":IndicatorType.STC,
                    "type":"close",
                    "length_period":10,
                    "fast_period":12,
                    "slow_period":26,
                    "mamode":PD_MAType.EMA,
                    "show":True},

            "styles":{
                    'pen_stc_line': "red",
                    'width_stc_line': 1,
                    'style_stc_line': Qt.PenStyle.SolidLine,
                    'pen_stoch_line': "orange",
                    'width_stoch_line': 1,
                    'style_stoch_line': Qt.PenStyle.SolidLine,
                    'pen_macd_line': "green",
                    'width_macd_line': 1,
                    'style_macd_line': Qt.PenStyle.SolidLine,
                    }
                    }
     
        self.id = self.chart.objmanager.add(self)
        
        self.on_click.connect(self.on_click_event)
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)
        
        self.setPen(color="red")
        
        self.stoch_line = PlotDataItem(pen="orange")
        self.stoch_line.setParentItem(self)
        self.macd_line = PlotDataItem(pen="green")
        self.macd_line.setParentItem(self)
        

        self.price_line = PriceLine()  # for z value
        self.price_line.setParentItem(self)
        
        
        self.picture: QPicture = QPicture()
        
        self.last_pos.connect(self.price_line.update_price_line_indicator,Qt.ConnectionType.AutoConnection)

        self.worker = None
        
        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)
        
        self.INDICATOR  = STC(self.has["inputs"]["source"], self.model.__dict__)
        
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
        return STCModel(self.id,"STC",self.chart.jp_candle.source_name,
                        self.has["inputs"]["type"],
                        self.has["inputs"]["length_period"],
                        self.has["inputs"]["fast_period"],
                        self.has["inputs"]["slow_period"],
                        self.has["inputs"]["mamode"].name.lower())
    
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
    

    def regen_indicator(self,setdata):
        xdata,stc,macd,stoch= self.INDICATOR.get_data()        
        self.has["name"] = f"STC {self.has["inputs"]["mamode"].name} {self.has["inputs"]["length_period"]} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["type"]}"
        self.sig_change_indicator_name.emit(self.has["name"])
        setdata.emit((xdata,stc,macd,stoch))
        self.sig_change_yaxis_range.emit()
        
        
        
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
                    "length_period":self.has["inputs"]["length_period"],
                    "fast_period":self.has["inputs"]["fast_period"],
                    "slow_period":self.has["inputs"]["slow_period"],
                    "mamode":self.has["inputs"]["mamode"],}
        return inputs
    
    def get_styles(self):
        styles =  {"pen_stc_line":self.has["styles"]["pen_stc_line"],
                    "width_stc_line":self.has["styles"]["width_stc_line"],
                    "style_stc_line":self.has["styles"]["style_stc_line"],
                    "pen_stoch_line":self.has["styles"]["pen_stoch_line"],
                    "width_stoch_line":self.has["styles"]["width_stoch_line"],
                    "style_stoch_line":self.has["styles"]["style_stoch_line"],
                    "pen_macd_line":self.has["styles"]["pen_stoch_line"],
                    "width_macd_line":self.has["styles"]["width_stoch_line"],
                    "style_macd_line":self.has["styles"]["style_stoch_line"],
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
                self.INDICATOR.change_input(self.has["inputs"]["source"])
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                update = True
        if update:
            self.has["name"] = f"STC {self.has["inputs"]["mamode"].name} {self.has["inputs"]["length_period"]} {self.has["inputs"]["fast_period"]} {self.has["inputs"]["slow_period"]} {self.has["inputs"]["type"]}"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "pen_stc_line" or _input == "width_stc_line" or _input == "style_stc_line":
            self.setPen(color=self.has["styles"]["pen_stc_line"], width=self.has["styles"]["width_stc_line"],style=self.has["styles"]["style_stc_line"])
        elif _input == "pen_stoch_line" or _input == "width_stoch_line" or _input == "style_stoch_line":
            self.stoch_line.setPen(color=self.has["styles"]["pen_stoch_line"], width=self.has["styles"]["width_stoch_line"],style=self.has["styles"]["style_stoch_line"])
        elif _input == "pen_macd_line" or _input == "width_macd_line" or _input == "style_macd_line":
            self.macd_line.setPen(color=self.has["styles"]["pen_macd_line"], width=self.has["styles"]["width_macd_line"],style=self.has["styles"]["style_macd_line"])
        

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    def set_Data(self,data):
        xData = data[0]
        lb = data[1]
        cb = data[2]
        ub = data[3]
        self.setData(xData,lb)
        self.macd_line.setData(xData,cb)
        self.stoch_line.setData(xData,ub)
        self.INDICATOR.is_current_update = True

    def add_historic_Data(self,data):
        xData = data[0]
        lb = data[1]
        cb = data[2]
        ub = data[3]
        self.addHistoricData(xData,lb)
        self.macd_line.addHistoricData(xData,cb)
        self.stoch_line.addHistoricData(xData,ub)
        self.INDICATOR.is_current_update = True
        
    def update_Data(self,data):
        xData = data[0]
        lb = data[1]
        cb = data[2]
        ub = data[3]
        self.updateData(xData,lb)
        self.macd_line.updateData(xData,cb)
        self.stoch_line.updateData(xData,ub)
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
    
    def load_historic_data(self,_len,setdata):
        xdata,stc,macd,stoch = self.INDICATOR.get_data(stop=_len)
        setdata.emit((xdata,stc,macd,stoch))
    
    def update_data(self,setdata):
        xdata,stc,macd,stoch = self.INDICATOR.get_data(start=-1)
        setdata.emit((xdata,stc,macd,stoch))
        self.last_pos.emit((self.has["inputs"]["indicator_type"],stc[-1]))
        self._panel.sig_update_y_axis.emit()
        

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

    # def paint(self, p:QPainter, *args):
    #     self.picture.play(p)
    
    # def boundingRect(self) -> QRectF:
    #     return self.stc_line.boundingRect()
    
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
        
    #     if self.stc_line.yData is None:
    #         h_low,h_high = self._panel.yAxis.range[0],self._panel.yAxis.range[1]
    #     elif self.stc_line.yData.size != 0:
    #         h_low,h_high = np.nanmin(self.stc_line.yData), np.nanmax(self.stc_line.yData) 
    #     else:
    #         h_low,h_high = self._panel.yAxis.range[0],self._panel.yAxis.range[1]
    #     rect = QRectF(self._start,h_low,self._stop-self._start,h_high-h_low)
    #     return rect  
    
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
