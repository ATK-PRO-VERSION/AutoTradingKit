from typing import Dict, Tuple, List,TYPE_CHECKING
import numpy as np
from PySide6.QtCore import Signal, QRect, QRectF, QPointF,Qt,QLineF
from PySide6.QtGui import QPainter, QPicture
from PySide6.QtWidgets import QGraphicsItem,QStyleOptionGraphicsItem,QWidget

from atklip.graphics.pyqtgraph import mkPen, GraphicsObject, mkBrush

from atklip.controls import OHLCV,IndicatorType
from atklip.controls.candle import JAPAN_CANDLE

from atklip.appmanager import FastWorker

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel
    
class Volume(GraphicsObject):
    """Live candlestick plot, plotting data [[open, close, min, max], ...]"""
    sigPlotChanged = Signal(object)
    sig_change_yaxis_range = Signal()
    signal_delete = Signal()
    sig_change_indicator_name = Signal(str)
    def __init__(self,get_last_pos_worker,chart,panel, high_color: str = '#089981', low_color: str = '#f23645') -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.chart:Chart = chart
        self._panel:ViewSubPanel = panel
        precision = 1
        self.has = {
            "name": f"Volume",
            "y_axis_show":True,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "type":IndicatorType.VOLUME,
                    "indicator_type":IndicatorType.VOLUME,
                    "show":False
                    },

            "styles":{
                "pen_highcolor":high_color,
                "pen_lowcolor" : low_color,
                "brush_highcolor":mkBrush(high_color,width=0.7),
                "brush_lowcolor":mkBrush(low_color,width=0.7)
                    }
                }
        
        self.chart.jp_candle.signal_delete.connect(self.signal_delete)
        if not isinstance(self.chart.jp_candle,JAPAN_CANDLE):
            self.chart.jp_candle.setParent(self)
            self.signal_delete.connect(self.chart.jp_candle.signal_delete)
        self.precision = precision
        self.output_y_data: List[float] = []
        self.historic_volume = SingleVolume(self.chart,self.has)
        self.historic_volume.setParentItem(self)
        self.type_picture = "volume"

        self.picture = QPicture()
        self.colorline = 'white'
        self.old_w = []
        self._start:int = None
        self._stop:int = None
        
        self._bar_picutures: Dict[int, QPicture] = {}
        self.picture: QPicture = None
        self._rect_area: Tuple[float, float] = None
        self._to_update: bool = False
        self._is_change_source: bool = False
        
        self.chart.jp_candle.sig_reset_all.connect(self.fisrt_gen_data,Qt.ConnectionType.AutoConnection)
        self.chart.jp_candle.sig_add_candle.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.chart.jp_candle.sig_add_historic.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        
        self.sig_change_yaxis_range.connect(get_last_pos_worker, Qt.ConnectionType.AutoConnection)
        self.object_id = self.chart.objmanager.add(self)
    @property
    def id(self):
        return self.object_id
        
    def get_inputs(self):
        inputs =  {}
        return inputs
    
    def get_styles(self):
        styles =  {"pen_highcolor":self.has["styles"]["pen_highcolor"],
                    "pen_lowcolor":self.has["styles"]["pen_lowcolor"],
                    "brush_highcolor":self.has["styles"]["brush_highcolor"],
                    "brush_lowcolor":self.has["styles"]["brush_lowcolor"],}
        return styles

    def update_styles(self, _input):
        self._is_change_source = True
        _style = self.has["styles"][_input]
        if _input == "brush_highcolor":
            self.has["styles"]["brush_highcolor"] = mkBrush(_style,width=0.7)
        elif _input == "brush_lowcolor":
            self.has["styles"]["brush_lowcolor"] = mkBrush(_style,width=0.7)
        self.historic_volume.fisrt_gen_data()
        self.threadpool_asyncworker(True)
    
    def get_min_max(self):
        volumes_fr = self.chart.jp_candle.get_df()
        sr = volumes_fr["volume"]
        _min,_max = sr.min(), sr.max()
        return _min,_max
    
    def fisrt_gen_data(self):
        self.worker = None
        self._is_change_source = True
        self.worker = FastWorker(self.update_last_data,True)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.QueuedConnection)
        self.worker.signals.finished.connect(self.sig_change_yaxis_range,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    def threadpool_asyncworker(self,candle):
        self.worker = None
        self.worker = FastWorker(self.update_last_data,candle)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    def get_yaxis_param(self):
        if len(self.chart.jp_candle.candles) > 0:
            last_candle = self.chart.jp_candle.last_data()
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

    def paint(self,painter: QPainter,opt: QStyleOptionGraphicsItem,w: QWidget) -> None:
        """
        Reimplement the paint method of parent class.

        This function is called by external QGraphicsView.
        """
        if self._start is None or self._stop is None:
            x_left,x_right = int(self._panel.xAxis.range[0]),int(self._panel.xAxis.range[1])
            
            start_index = self.chart.jp_candle.candles[0].index
            stop_index = self.chart.jp_candle.candles[-1].index
            if x_left > start_index:
                self._start = x_left
            else:
                self._start = start_index
            if x_right < stop_index:
                self._stop = x_right
            else:
                self._stop = stop_index
                
        rect_area: tuple = (self._start, self._stop)
        if self._to_update:
            self._draw_item_picture(self._start, self._stop)
            self._to_update = False
        elif (rect_area != self._rect_area):
            self._rect_area = rect_area
            self._draw_item_picture(self._start, self._stop)
        elif self.picture == None:
            self._rect_area = rect_area
            self._draw_item_picture(self._start, self._stop)
            
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
        bar_picture = self._bar_picutures.get(ix)
        if bar_picture is not None:
            bar_picture.play(painter)    
    
    def boundingRect(self) -> QRectF:
        x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])  
        start_index = self.chart.jp_candle.candles[0].index
        stop_index = self.chart.jp_candle.candles[-1].index
        if x_left > start_index:
            self._start = x_left+2
        elif x_left > stop_index:
            self._start = start_index+2
        else:
            self._start = start_index+2
            
        if x_right < stop_index:
            self._stop = x_right
        else:
            self._stop = stop_index
        h_high =  self.chart.jp_candle.get_df()["volume"].iloc[self._start:self._stop].max()
        h_low = self.chart.jp_candle.get_df()["volume"].iloc[self._start:self._stop].min()
        rect = QRectF(self._start,h_low,self._stop-self._start,h_high-h_low)
        return rect

    def draw_volume(self,_open,close,volume,w,t):
        if self._bar_picutures.get(t) == None:
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
            self._bar_picutures[t] = candle_picture

    def setData(self, data) -> None:
        """y_data must be in format [[open, close, min, max], ...]"""
        
        x_data, y_data = data[0], data[1]
        # self.picture = QPicture()
        # p = QPainter(self.picture)
        _open,_close, _volume = y_data[0],y_data[1],y_data[2]
        self._to_update = False
        w = 1 / 5
        if self._is_change_source:
            self._bar_picutures.clear()
            self._is_change_source = False
        [self.draw_volume(_open[index],_close[index],_volume[index],w,x_data[index]) for index in range(len(x_data))]
        # p.end()
        self._to_update = True
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
    
    def update_last_data(self, candles,setdata) -> None:
        if candles is None or isinstance(candles,list):
            x_data, y_data = self.chart.jp_candle.get_index_volumes(start=-3,stop=-1)
        elif candles == True:
            x_data, y_data = self.chart.jp_candle.get_index_volumes(stop=-1)
        else:
            x_data, y_data = self.chart.jp_candle.get_index_volumes(stop=candles+1)
        try:
            if len(x_data) != len(y_data[0]):
                raise Exception("Len of x_data must be the same as y_data")
            # setdata.emit((x_data, y_data))
            self.setData((x_data, y_data))
        except Exception as e:
            print(e)
      
class SingleVolume(GraphicsObject):
    """Live candlestick plot, plotting data [[open, close, min, max], ...]"""
    sigPlotChanged = Signal(object)
    def __init__(self,chart, has) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        
        self.chart:Chart  = chart
        sig_reset_all,sig_update_candle,self._canldes= self.chart.jp_candle.sig_reset_all,self.chart.jp_candle.sig_update_candle,self.chart.jp_candle
        self.has = has
        precision = 1
        
        self.output_y_data: List[float] = []

        self.type_picture = "candlestick"
        self.picture = QPicture()
        self.colorline = 'white'

        self.old_w = []
        self.setAcceptHoverEvents(True)
        self.precision = precision
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        
        sig_update_candle.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)

    def fisrt_gen_data(self):
        self.worker = None
        self.worker = FastWorker(self.update_last_data)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)
    
    def threadpool_asyncworker(self, last_candle:List[OHLCV]=[]):
        self.worker = None
        self.worker = FastWorker(self.update_last_data)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
        #self.threadpool.start(self.worker)

    def paint(self, p: QPainter, *args) -> None:
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self) -> QRect:
        return QRectF(self.picture.boundingRect())
    
    def draw_volume(self,p:QPainter,_open,close,volume,w,t):
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
            #path = QPainterPath()
            rect = QRectF(t - w, 0, w * 2, volume)  
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
        
        w = 1 / 5
        index = -1
        t = x_data[index]
        _open, close,volume = y_data[-1][0],y_data[-1][1],y_data[-1][2]
        self.draw_volume(p,_open,close,volume,w,t)
        p.end()
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()

    def update_last_data(self,setdata) -> None:
        if self._canldes.first_gen:
            if self._canldes.candles != []:
                last_candle = self._canldes.last_data()
                x_data, _y_data = np.array([last_candle.index]), np.array([[last_candle.open,last_candle.close,last_candle.volume]])
                #self.setData((x_data, _y_data))
                try:
                    setdata.emit((x_data, _y_data))
                    #QCoreApplication.processEvents()
                except Exception as e:
                    pass
