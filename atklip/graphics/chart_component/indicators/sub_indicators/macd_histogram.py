from typing import Dict, Tuple, List,TYPE_CHECKING
import numpy as np

from PySide6.QtCore import Signal, QRect, QRectF, QPointF,QThreadPool,Qt,QLineF
from PySide6.QtGui import QPainter, QPicture
from PySide6.QtWidgets import QGraphicsItem,QStyleOptionGraphicsItem,QWidget
from atklip.graphics.pyqtgraph import mkPen, GraphicsObject, mkBrush

from atklip.appmanager import FastWorker

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel

class MACDHistogram(GraphicsObject):
    """Live candlestick plot, plotting data [[open, close, min, max], ...]"""
    sigPlotChanged = Signal(object)
    sig_change_yaxis_range = Signal()
    
    sig_update_histogram = Signal(tuple,str)
    sig_reset_histogram = Signal(tuple,str)
    sig_add_histogram = Signal(tuple,str)
    sig_load_historic_histogram = Signal(tuple,str)
    
    def __init__(self,chart,panel,has) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self._panel:ViewSubPanel = panel

        precision = 1
        
        self.has = has

        self.precision = precision
        self.output_y_data: List[float] = []


        self.x_data, self.y_data = np.array([]),np.array([])
        
        self._bar_picutures: Dict[int, QPicture] = {}
        self.picture: QPicture = None
        self._rect_area: Tuple[float, float] = None
        self._to_update: bool = False
        self._is_change_source: bool = False
        self._start:int = None
        self._stop:int = None
        
        self.sig_reset_histogram.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.sig_add_histogram.connect(self.update_asyncworker,Qt.ConnectionType.AutoConnection)
        self.sig_update_histogram.connect(self.update_asyncworker,Qt.ConnectionType.AutoConnection)
        self.sig_load_historic_histogram.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)

    def get_inputs(self):
        inputs =  {}
        return inputs
    
    def get_styles(self):
        styles =  {"pen_high_historgram":self.has["styles"]["pen_high_historgram"],
                    "pen_low_historgram":self.has["styles"]["pen_low_historgram"],
                    "brush_high_historgram":self.has["styles"]["brush_high_historgram"],
                    "brush_low_historgram":self.has["styles"]["brush_low_historgram"],}
        return styles

    def update_styles(self, _input,data):
        self._is_change_source = True
        _style = self.has["styles"][_input]
        if _input == "brush_high_historgram":
            self.has["styles"]["brush_high_historgram"] = mkBrush(_style,width=0.7)
        elif _input == "brush_low_historgram":
            self.has["styles"]["brush_low_historgram"] = mkBrush(_style,width=0.7)
        self.threadpool_asyncworker(data,"reset")
        
    def get_min_max(self):
        x_data, y_data = self.has["inputs"]["source"].get_index_volumes(stop=len(self.has["inputs"]["source"].candles))
        values = [y[2] for y in y_data]
        _min,_max = None,None
        if values != []:
            _min,_max = min(values), max(values)
        return _min,_max
    
    def threadpool_asyncworker(self,data,_type):
        self.worker = None
        self.worker = FastWorker(self.update_last_data,data,_type)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.AutoConnection)
        self.worker.start()
    
    
    def update_asyncworker(self,data,_type):
        self.worker = None
        self.worker = FastWorker(self.update_last_data,data,_type)
        self.worker.signals.setdata.connect(self.updateData,Qt.ConnectionType.AutoConnection)
        self.worker.start()    
    
    def updateData(self, data) -> None:
        """y_data must be in format [[open, close, min, max], ...]"""
        self._to_update = False
        x_data, y_data = data[0],data[1]
                
        w = (x_data[-1] - x_data[-2]) / 5
        pre_t = x_data[-2]
        t = x_data[-1]
        
        pre_value= y_data[-2]
        _value = y_data[-1]
        
        self.draw_single_volume(pre_value,w,pre_t)
        self.draw_single_volume(_value,w,t)
        
        self._to_update = True
        # self._panel.sig_update_y_axis.emit()
        # self.prepareGeometryChange()
        # self.informViewBoundsChanged()
        self.update(self.boundingRect())
    
    
    def get_yaxis_param(self):
        if len(self.has["inputs"]["source"].candles) > 0:
            last_candle = self.has["inputs"]["source"].last_data()
            last_volume_ = last_candle.volume
            last_close_price_ = last_candle.close
            last_open_price_ = last_candle.open
            colorline = "green" if last_close_price_ >= last_open_price_ else "red"
            last_color,last_close_price = colorline,last_close_price_
            return None,None
            return last_volume_,last_color
        else:
            return None,None
    def get_xaxis_param(self):
        return None,None
    

    def update_last_data(self,data,_type, setdata) -> None:
        x_data, y_data = data[0],data[1]
        try:
            if _type == "reset":
                self._is_change_source = True
                setdata.emit((x_data, y_data))
            if _type == "load_historic":
                _len = len(self._bar_picutures)
                setdata.emit((x_data, y_data))
            if _type == "add":
                setdata.emit((x_data, y_data))
        except Exception as e:
            pass
    
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

    def draw_volume(self,value,w,x_data,index):
        "dieu kien de han che viec ve lai khi add new candle"
        t = x_data[index]
        if not self._bar_picutures.get(t):
            self.draw_single_volume(value,w,t)
            return True
        return False
        
    def draw_single_volume(self,value,w,t):
        candle_picture:QPicture =QPicture()
        p:QPainter =QPainter(candle_picture)
        if value < 0:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_low_historgram"],width=0.7) 
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_low_historgram"])
        else:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_high_historgram"],width=0.7) 
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_high_historgram"])
        if value == 0:
            _line = QLineF(QPointF(t - w, 0), QPointF(t + w, 0))
            p.drawLine(_line)
        else:
            rect = QRectF(t - w, 0, w * 2, value)  
            p.drawRect(rect)
        p.end()
        self._bar_picutures[t] = candle_picture
        

    def setData(self, data) -> None:
        """y_data must be in format [[open, close, min, max], ...]"""
        self._to_update = False
        
        x_data, y_data = data[0],data[1]
        w = (x_data[-1] - x_data[-2]) / 5
        
        
        self.x_data, self.y_data = x_data, y_data

        if self._is_change_source:
            self._bar_picutures.clear()
            self._is_change_source = False
        [self.draw_volume(value,w,x_data,index) for index, value in enumerate(y_data)]
        self._to_update = True
        self._panel.sig_update_y_axis.emit()
        # self.prepareGeometryChange()
        # self.informViewBoundsChanged()
        self.update(self.boundingRect())
         
    def getData(self) -> Tuple[List[float], List[Tuple[float, ...]]]:
        return self.x_data, self.y_data
    

class SingleMACDHistogram(GraphicsObject):
    """Live candlestick plot, plotting data [[open, close, min, max], ...]"""
    sigPlotChanged = Signal(object)
    def __init__(self,sig_update_histogram, has) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        
        self.has = has
        
        self.output_y_data: List[float] = []

        self.picture = QPicture()

        self.old_w = []
        self.setAcceptHoverEvents(True)

        sig_update_histogram.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)

    
    def threadpool_asyncworker(self, last_candle:List):
        self.worker = None
        self.worker = FastWorker(self.update_last_data,last_candle)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def paint(self, p: QPainter, *args) -> None:
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self) -> QRect:
        return QRectF(self.picture.boundingRect())
    
    def draw_volume(self,p:QPainter,value,w,t):
        if value < 0:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_low_historgram"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_low_historgram"])
        else:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_high_historgram"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_high_historgram"])

        if value == 0:
            _line = QLineF(QPointF(t - w, 0), QPointF(t + w, 0))
            p.drawLine(_line)
        else:
            rect = QRectF(t - w, 0, w * 2, value)  
            p.drawRect(rect)

    def setData(self, data) -> None:
        """y_data must be in format [[open, close, min, max], ...]"""
        
        x_data, y_data = data[0], data[1]
        if not isinstance(x_data, np.ndarray):
            x_data = np.array(x_data)
            y_data = np.array(y_data)
        if len(x_data) != len(y_data):
            raise Exception("Len of x_data must be the same as y_data")
        self.picture = QPicture()
        p = QPainter(self.picture)
        
        w = 1 / 5
        index = -1
        t = x_data[index]
        value = y_data[index]
        self.draw_volume(p,value,w,t)
        p.end()
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()

    def update_last_data(self,last_candle,setdata) -> None:
        try:
            setdata.emit((last_candle[0], last_candle[1]))
            #QCoreApplication.processEvents()
        except Exception as e:
            pass
    def getData(self) -> Tuple[List[float], List[Tuple[float, ...]]]:
        return self.x_data, self.y_data
