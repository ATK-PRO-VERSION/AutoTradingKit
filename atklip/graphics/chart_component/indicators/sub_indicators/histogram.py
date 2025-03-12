from typing import Tuple, List
import numpy as np

from PySide6.QtCore import Signal, QRect, QRectF, QPointF,Qt,QLineF
from PySide6.QtGui import QPainter, QPicture
from PySide6.QtWidgets import QGraphicsItem

from atklip.graphics.pyqtgraph import mkPen, GraphicsObject, mkBrush

from atklip.controls import OHLCV,IndicatorType
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE

from atklip.graphics.chart_component.proxy_signal import Signal_Proxy
from atklip.appmanager import FastWorker

class Histogram(GraphicsObject):
    """Live candlestick plot, plotting data [[open, close, min, max], ...]"""
    sigPlotChanged = Signal(object)
    sig_change_yaxis_range = Signal()
    def __init__(self,sig_reset_all,_type,precision,change_lastprice,lastcandle, update_signal,_candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE=[], high_color: str = '#089981', low_color: str = '#f23645') -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.has: dict = {
            "name": f"{_type.name}",
            "y_axis_show":False,
            "inputs":{
                    "source":_candles,
                    "type":_type,
                    "indicator_type":IndicatorType.VOLUME,
                    },

            "styles":{
                "highcolor":high_color,
                "lowcolor" : low_color,
                "high_brush":mkBrush(high_color,width=0.7),
                "low_brush":mkBrush(low_color,width=0.7)
                    }
                }

        if not isinstance(self.has["inputs"]["source"],JAPAN_CANDLE):
            self.has["inputs"]["source"].setParent(self)
            self.destroyed.connect(self.has["inputs"]["source"].deleteLater)
        
        self.precision = precision
        self.output_y_data: List[float] = []

        self.historic_candle = SingleHistogram(sig_reset_all,precision,change_lastprice,lastcandle,_candles,high_color=high_color,low_color=low_color)
        self.historic_candle.setParentItem(self)

        self.type_picture = "candlestick"
        self.picture = QPicture()
        self.colorline = 'white'

        self.old_w = []
        self.setAcceptHoverEvents(True)

  
        sig_reset_all.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        lastcandle.connect(self.threadpool_asyncworker,Qt.ConnectionType.SingleShotConnection)
        self.proxy_update_signal = Signal_Proxy(update_signal,slot=self.threadpool_asyncworker,connect_type=Qt.ConnectionType.AutoConnection)
        
        self.threadpool_asyncworker()

    def get_min_max(self):
        x_data, y_data = self.has["inputs"]["source"].get_index_volumes(stop=len(self.has["inputs"]["source"].candles))
        values = [y[2] for y in y_data]
        
        _min,_max = None,None
        if values != []:
            _min,_max = min(values), max(values)
        return _min,_max
    def setup_color(self, colors):
        self.inbound_color = colors.get("in") if colors.get("in") else "#c824d3"
        self.outbound_color = colors.get("out") if colors.get("out") else "#fff7f9"
        self.has["styles"]["highcolor"] =  colors.get("high") if colors.get("high") else"#0ecb81"
        self.has["styles"]["lowcolor"] = colors.get("low") if colors.get("low") else "#f6465d"
        self.inbound_brush = mkBrush(self.inbound_color,width=0.7)
        self.outbound_brush = mkBrush(self.outbound_color,width=0.7)

    def threadpool_asyncworker(self):
        self.worker = None
        self.worker = FastWorker(self.update_last_data)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.AutoConnection)
        self.worker.signals.finished.connect(self.sig_change_yaxis_range,Qt.ConnectionType.AutoConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    def get_yaxis_param(self):
        if len(self.has["inputs"]["source"].candles) > 0:
            last_candle = self.has["inputs"]["source"].last_data()
            last_close_price_ = last_candle.close
            last_open_price_ = last_candle.open
            colorline = "green" if last_close_price_ >= last_open_price_ else "red"
            last_color,last_close_price = colorline,last_close_price_
            return last_close_price,last_color
        else:
            return None,None
    def get_xaxis_param(self):
        return None,None

    def paint(self, p: QPainter, *args) -> None:
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self) -> QRect:
        return QRectF(self.picture.boundingRect())
    
    def draw_histogram(self,p:QPainter,value,w,x_data,index):
        if value > 0:
            self.outline_pen = mkPen(color=self.has["styles"]["lowcolor"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["low_brush"])
        else:
            self.outline_pen = mkPen(color=self.has["styles"]["highcolor"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["high_brush"])
        t = x_data[index]

        if value == 0:
            _line = QLineF(QPointF(t - w, 0), QPointF(t + w, 0))
            p.drawLine(_line)
        else:
            #path = QPainterPath()
            rect = QRectF(t - w, 0, w * 2, value)  
            #path.addRect(rect)  
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
        try:
            w = (x_data[1] - x_data[0]) / 5
        except IndexError:
            w = 1 / 5
        [self.draw_histogram(p,value,w,x_data,index) for index, value in enumerate(y_data)]
        p.end()
        

    def update_last_data(self, setdata) -> None:
        x_data, y_data = self.has["inputs"]["source"].get_index_volumes(stop=len(self.has["inputs"]["source"].candles))
        try:
            setdata.emit((x_data, y_data))
        except Exception as e:
            pass
        
    def getData(self) -> Tuple[List[float], List[Tuple[float, ...]]]:
        return self.x_data, self.y_data
    

class SingleHistogram(GraphicsObject):
    """Live candlestick plot, plotting data [[open, close, min, max], ...]"""
    sigPlotChanged = Signal(object)
    yaxis_lastprice =  Signal()

    def __init__(self,sig_reset_all,precision, change_lastprice,lastcandle,_candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE, high_color: str = '#0ecb81', low_color: str = '#f6465d') -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        
        self.has: dict = {
            "name": f"",
            "inputs":{
                    "source":_candles,
                    },

            "styles":{
                "highcolor":high_color,
                "lowcolor" : low_color,
                "high_brush":mkBrush(high_color,width=0.7),
                "low_brush":mkBrush(low_color,width=0.7)
                    }
                }
        
        self._canldes = _candles
        self.output_y_data: List[float] = []

        self.type_picture = "candlestick"
        self.picture = QPicture()
        self.colorline = 'white'

        self.old_w = []
        self.setAcceptHoverEvents(True)
        self.precision = precision

        self.yaxis_lastprice.connect(change_lastprice,Qt.ConnectionType.AutoConnection)
        lastcandle.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)

    def setup_color(self, colors):
        self.inbound_color = colors.get("in") if colors.get("in") else "#c824d3"
        self.outbound_color = colors.get("out") if colors.get("out") else "#fff7f9"
        self.has["styles"]["highcolor"] =  colors.get("high") if colors.get("high") else"#0ecb81"
        self.has["styles"]["lowcolor"] = colors.get("low") if colors.get("low") else "#f6465d"
        self.inbound_brush = mkBrush(self.inbound_color,width=0.7)
        self.outbound_brush = mkBrush(self.outbound_color,width=0.7)

    def reset_threadpool_asyncworker(self):
        self.worker = None
        worker = FastWorker(self.update_last_data)
        worker.signals.setdata.connect(self.setData,Qt.ConnectionType.AutoConnection)
        self.threadpool.start(worker)
    
    def threadpool_asyncworker(self, last_candle:List[OHLCV]):
        self.worker = None
        self.worker = FastWorker(self.update_last_data)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.AutoConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)

    def paint(self, p: QPainter, *args) -> None:
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self) -> QRect:
        return QRectF(self.picture.boundingRect())
    
    def draw_histogram(self,p:QPainter,value,w,t):
        if value > 0:
            self.outline_pen = mkPen(color=self.has["styles"]["lowcolor"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["low_brush"])
        else:
            self.outline_pen = mkPen(color=self.has["styles"]["highcolor"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["high_brush"])
        if value == 0:
            _line = QLineF(QPointF(t - w, 0), QPointF(t + w, 0))
            p.drawLine(_line)
        else:
            #path = QPainterPath()
            rect = QRectF(t - w, 0, w * 2, value)  
            #path.addRect(rect)  
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
        try:
            w = (x_data[1] - x_data[0]) / 5
        except IndexError:
            w = 1 / 5
        index = -1
        t = x_data[index]
        value = y_data[-1]
        self.draw_histogram(p,value,w,t)
        p.end()
        
        #self.prepareGeometryChange()
        self.informViewBoundsChanged()
        # self.bounds = [None, None]
        # self.sigPlotChanged.emit(self)

    def update_last_data(self,setdata) -> None:
        if self._canldes.first_gen:
            if self._canldes.candles != []:
                last_candle = self._canldes.last_data()
                x_data, _y_data = [last_candle.index], [[last_candle.open,last_candle.close,last_candle.volume]]
                try:
                    setdata.emit((x_data, _y_data))
                    self.yaxis_lastprice.emit()
                except Exception as e:
                    pass
    def getData(self) -> Tuple[List[float], List[Tuple[float, ...]]]:
        return self.x_data, self.y_data
