import time
from typing import Dict, Tuple, List,TYPE_CHECKING

import numpy as np
from atklip.graphics.pyqtgraph import functions as fn,mkPen, GraphicsObject, mkBrush
from PySide6.QtCore import Signal, QObject, QRect, QRectF, QPointF,Qt,QLineF
from PySide6.QtGui import QPainter, QPicture
from PySide6.QtWidgets import QGraphicsItem,QStyleOptionGraphicsItem,QWidget
from atklip.controls import PD_MAType
from atklip.controls import OHLCV,IndicatorType
from atklip.controls.volume_with_ma import VolumeWithMa
from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem
from atklip.controls.ma import MA
from atklip.appmanager import FastWorker
from atklip.app_utils import *
from atklip.controls.models import MAModel
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel


class VolumeWithMA(GraphicsObject):
    """DEMA EMA HMA SMA SMMA TEMA TRIX ZLEMA WMA"""
    on_click = Signal(object)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    sig_change_indicator_name = Signal(str)

    def __init__(self,get_last_pos_worker,chart,panel, high_color: str = '#089981', low_color: str = '#f23645',
                 indicator_type: PD_MAType=PD_MAType.SMA,pen:str="yellow",length:int=5,_type:str="volume") -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        # self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        # self.setCacheMode(QGraphicsItem.CacheMode.ItemCoordinateCache)
        self.setZValue(999)
        self.chart:Chart = chart
        self._panel:ViewSubPanel = panel

        
        self.has = {
            "name": f"Volume",
            "y_axis_show":False,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name":self.chart.jp_candle.source_name,
                    "type":_type,
                    "indicator_type":IndicatorType.VOLUME,
                    "mamode":indicator_type,
                    "length":length,
                    "show":False
                    },

            "styles":{
                'pen': pen,
                'width': 1,
                'style': Qt.PenStyle.SolidLine,
                "pen_highcolor":high_color,
                "pen_lowcolor" : low_color,
                "brush_highcolor":mkBrush(high_color,width=0.7),
                "brush_lowcolor":mkBrush(low_color,width=0.7)
                    }
                }
        
        self.id = self.chart.objmanager.add(self)
        
        
        self.ma_line = PlotDataItem(pen="orange")
        self.ma_line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.ma_line.setParentItem(self)
        
        self._pen = pen
        self.is_reset = False
        self.picture = QPicture()
        self.colorline = 'white'
        self.old_w = []
        self._start:int = None
        self._stop:int = None
        
        self._bar_picutures: Dict[int, QPicture] = {}
        self._rect_area: Tuple[float, float] = None
        self._to_update: bool = False
        self._is_change_source: bool = False
        
        
        # self.xData, self.yData = np.array([]),np.array([])
        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)
        self.INDICATOR  = VolumeWithMa(self.has["inputs"]["source"], self.model.__dict__)
        
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
        return MAModel(self.id,"MA",self.chart.jp_candle.source_name,self.has["inputs"]["mamode"].name.lower(),
                              self.has["inputs"]["type"],self.has["inputs"]["length"])
    
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
        x_data,y_data,_open, close, volume = self.INDICATOR.get_data()
        setdata.emit((x_data,y_data,_open, close, volume))
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"{self.has["inputs"]["mamode"].name} {self.has["inputs"]["length"]} {self.has["inputs"]["type"]}"
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
                    "mamode":self.has["inputs"]["mamode"],
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
        elif _input == "type":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        elif _input == "mamode":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        elif _input == "length":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        if is_update:
            self.has["name"] = f"{self.has["inputs"]["mamode"].name} {self.has["inputs"]["length"]} {self.has["inputs"]["type"]}"
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
        x_data = data[0]
        yData = data[1]
        _open = data[2]
        _close = data[3]
        _volume = data[4]
        self.ma_line.setData(x_data, yData)
        
        self._to_update = False
        
        w = (x_data[-1] - x_data[-2]) / 5

        if self._is_change_source:
            self._bar_picutures.clear()
            self._is_change_source = False
            
        [self.draw_volume(_open[index],_close[index],_volume[index],w,x_data[index]) for index in range(len(x_data))]
        
        self._to_update = True
        # self.prepareGeometryChange()
        # self.informViewBoundsChanged()
        self.update(self.boundingRect())
        self.INDICATOR.is_current_update = True
        
        
    def add_historic_Data(self,data):
        x_data = data[0]
        yData = data[1]
        _open = data[2]
        _close = data[3]
        _volume = data[4]
        self.ma_line.addHistoricData(x_data, yData)
        w = (x_data[-1] - x_data[-2]) / 5
        [self.draw_volume(_open[index],_close[index],_volume[index],w,x_data[index]) for index in range(len(x_data))]
        
        self.update(self.boundingRect())
        self.INDICATOR.is_current_update = True
    
    def update_Data(self,data):
        x_data = data[0]
        yData = data[1]
        _open = data[2]
        _close = data[3]
        _volume = data[4]
        self.ma_line.updateData(x_data, yData)
        
        self._to_update = False
        w = (x_data[-1] - x_data[-2]) / 5
        pre_t = x_data[-2]
        t = x_data[-1]
        
        pre_open,pre_close, pre_volume = _open[-2],_close[-2],_volume[-2]
        cr_open,cr_close, cr_volume = _open[-1],_close[-1],_volume[-1]
        
        self.draw_single_volume(pre_open,pre_close, pre_volume,w,pre_t)
        self.draw_single_volume(cr_open,cr_close, cr_volume,w,t)
        
        self._to_update = True
        self._panel.sig_update_y_axis.emit()
        # self.prepareGeometryChange()
        # self.informViewBoundsChanged()
        self.update(self.boundingRect())
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
        x_data,y_data,_open, close, volume = self.INDICATOR.get_data(stop=_len)
        setdata.emit((x_data,y_data,_open, close, volume))   
             
    def add_data(self,setdata):
        x_data,y_data,_open, close, volume  = self.INDICATOR.get_data(start=-3)
        setdata.emit((x_data,y_data,_open, close, volume ))  
    def update_data(self,setdata):
        x_data,y_data,_open, close, volume  = self.INDICATOR.get_data(start=-3)
        setdata.emit((x_data,y_data,_open, close, volume ))   
          
    
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
        self.ma_line.opts['pen'] = pen
        self.ma_line.updateItems(styleUpdate=True)

    def data_bounds(self, ax=0, offset=0) -> Tuple:
        x, y = self.getData()
        if ax == 0:
            sub_range = x[-offset:]
        else:
            sub_range = y[-offset:]
        return np.nanmin(sub_range), np.nanmax(sub_range)
    
    def paint(self,painter: QPainter,opt: QStyleOptionGraphicsItem,w: QWidget) -> None:
        """
        Reimplement the paint method of parent class.

        This function is called by external QGraphicsView.
        """
        self.picture.play(painter)

    def _draw_item_picture(self, min_ix: int, max_ix: int) -> None:
        """
        Draw the picture of item in specific range.
        """
        self.picture = QPicture()
        painter = QPainter(self.picture)
        [self.play_bar(painter,ix) for ix in range(min_ix, max_ix)]
        painter.end()
    
    def play_bar(self,painter,ix):
        bar_picture = self._bar_picutures.get(ix,None)
        if bar_picture:
            bar_picture.play(painter)   
    
    
    def boundingRect(self) -> QRectF:
        x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])   
        start_index = self.chart.jp_candle.start_index
        stop_index = self.chart.jp_candle.stop_index
        if x_left > start_index:
            self._start = x_left+2
        elif x_left > stop_index:
            self._start = start_index+2
        else:
            self._start = start_index+2
            
        if x_right < stop_index:
            self._stop = x_right+2
        else:
            self._stop = stop_index+2

        rect_area: tuple = (self._start, self._stop)
        if self._to_update:
            self._rect_area = rect_area
            self._draw_item_picture(self._start, self._stop)
            self._to_update = False
        elif rect_area != self._rect_area:
            self._rect_area = rect_area
            self._draw_item_picture(self._start, self._stop)
        return self.picture.boundingRect()

    def draw_volume(self,_open,close,volume,w,t):
        "dieu kien de han che viec ve lai khi add new candle"
        if not self._bar_picutures.get(t):
            self.draw_single_volume(_open,close,volume,w,t)
            return True
        return False
        
    def draw_single_volume(self,_open,close,volume,w,t):
        candle_picture:QPicture =QPicture()
        p:QPainter =QPainter(candle_picture)
        if _open > close:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_lowcolor"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_lowcolor"])
        else:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_highcolor"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_highcolor"])

        if volume == 0:
            _line = QLineF(QPointF(t - w, 0), QPointF(t + w, 0))
            p.drawLine(_line)
        else:
            rect = QRectF(t - w, 0, w * 2, volume)  
            p.drawRect(rect)
        p.end()
        self._bar_picutures[t] = candle_picture
    
    def get_min_max(self):
        volumes_fr = self.chart.jp_candle.get_df()
        sr = volumes_fr["volume"]
        _min,_max = sr.min(), sr.max()
        return _min,_max