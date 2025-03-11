from typing import Dict, Tuple, List,TYPE_CHECKING
import numpy as np

from PySide6.QtCore import Signal, Slot, QRectF, QPointF,QThreadPool,Qt,QLineF,QCoreApplication
from PySide6.QtGui import QPainter, QPicture,QPainterPath
from PySide6.QtWidgets import QGraphicsItem,QStyleOptionGraphicsItem,QWidget
from atklip.graphics.pyqtgraph import mkPen, GraphicsObject, mkBrush

from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE

from atklip.appmanager import FastWorker,CandleWorker
from .price_lines import PriceLine

from atklip.controls.ma_type import  PD_MAType,IndicatorType
from atklip.controls.ohlcv import OHLCV

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_chart import SubChart
        

class CandleStick(GraphicsObject):
    """Live candlestick plot, plotting data [[open, close, min, max], ...]"""
    sig_deleted_source = Signal(object)
    signal_delete = Signal()
    sig_change_name = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart,_type, high_color: str = '#089981', low_color: str = '#f23645') -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        # self.setZValue(500)
        
        self.chart:Chart|SubChart = chart
        self.precision = self.chart._precision
        self.symbol = self.chart.symbol
        self.interval = self.chart.interval
        self._type:str = _type
        
        self.source, mamode, period, n = self.get_source(self._type)
        
    
        if not isinstance(self.source,JAPAN_CANDLE):# mamode != None:
            if isinstance(self.source,HEIKINASHI):
                name = f"{self.source.source_name}"
            else:
                name = f"{self.source.source_name} {mamode.name} {period} {n}"
            
            self.has = {
            "is_candle": True,
            "name": name,
            "y_axis_show":True,
            "inputs":{
                    "source":self.source,
                    "mamode":mamode,
                    "ma_period":period,
                    "n_smooth_period": n,
                    "show":True
                    },

            "styles":{
                "pen_highcolor":"#006c3c",
                "pen_lowcolor" : "#750000",
                "brush_highcolor":mkBrush("#006c3c",width=0.7),
                "brush_lowcolor":mkBrush("#750000",width=0.7)
                    }
                }
        else:
            self.has = {
            "name": f"{self.source.source_name}",
            "y_axis_show":True,
            "inputs":{
                    "source":self.source,
                    "show":True
                    },

            "styles":{
                "pen_highcolor":high_color,
                "pen_lowcolor" : low_color,
                "brush_highcolor":mkBrush(high_color,width=0.7),
                "brush_lowcolor":mkBrush(low_color,width=0.7)
                    }
                }
        
        self.sig_change_indicator_name.emit(self.has["name"])
        
        if not isinstance(self.source,JAPAN_CANDLE) and not isinstance(self.source,HEIKINASHI):
            "để không xóa jp và heikin trong viewchart"
            self.source.setParent(self)
            self.signal_delete.connect(self.source.signal_delete)

        self._bar_picutures: Dict[int, QPicture] = {}
        self.picture: QPicture = QPicture()
        self._rect_area: Tuple[float, float] = ()
        self._to_update: bool = False
        self._is_change_source:bool=False
        self._start:int = None
        self._stop:int = None

        self.price_line = PriceLine()  # for z value
        self.price_line.setParentItem(self)
        
        self.signal_delete.connect(self.delete_source)
        self.sig_deleted_source.connect(self.chart.remove_source)
        
        self.source.sig_reset_all.connect(self.update_source,Qt.ConnectionType.AutoConnection)
        
        self.source.sig_update_candle.connect(self.update_asyncworker,Qt.ConnectionType.AutoConnection)
        self.source.sig_add_candle.connect(self.update_asyncworker,Qt.ConnectionType.AutoConnection)
        self.source.sig_add_historic.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        
        if not (isinstance(self.source,JAPAN_CANDLE) or isinstance(self.source,HEIKINASHI)):
            self.source.fisrt_gen_data()
        else:
            self.first_setup_candle()
        
    
    @property
    def is_all_updated(self):
        is_updated = self.source.is_current_update 
        return is_updated
    
    def delete_source(self):
        self.sig_deleted_source.emit(self.source)
        # self.source.signal_delete.emit()
        
    def update_source(self):
        self._is_change_source = True
        self.chart.remove_source(self.source)
        source_name = self.has["name"].split(" ")[0]
        if isinstance(self.source,N_SMOOTH_CANDLE):
            self.has["name"] = f"{source_name} {self.has["inputs"]["mamode"].name} {self.has["inputs"]["ma_period"]} {self.has["inputs"]["n_smooth_period"]}"
        if isinstance(self.source,SMOOTH_CANDLE):
            self.has["name"] = f"{source_name} {self.has["inputs"]["mamode"].name} {self.has["inputs"]["ma_period"]}"
        else:
            self.has["name"] = f"{source_name} {self.chart.symbol} {self.chart.interval}"
        
        self.source.source_name = self.has["name"]
        
        self.chart.update_sources(self.source)
        self.sig_change_indicator_name.emit(self.has["name"])
        
        self.first_setup_candle()
    
    def update_inputs(self,_input,_source):
        """"source":self.source,
                "mamode":self.has["inputs"]["mamode"],
                "ma_period":self.has["inputs"]["ma_period"]"""
        update = False
        if _input == "mamode":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                update = True

        elif _input == "ma_period":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                update = True
        elif _input == "n_smooth_period":
            if _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                update = True
        
        if update:
            self._is_change_source = True
            ma_period = self.has["inputs"].get("ma_period")
            n_smooth_period = self.has["inputs"].get("n_smooth_period")
            mamode = self.has["inputs"].get("mamode")
            
            if mamode != None:
                if isinstance(self.source,N_SMOOTH_CANDLE):
                    self.has["name"] = f"{self.source.source_name} {self.has["inputs"]["mamode"].name} {self.has["inputs"]["ma_period"]} {self.has["inputs"]["n_smooth_period"]}"
                else:
                    self.has["name"] = f"{self.source.source_name} {self.has["inputs"]["mamode"].name} {self.has["inputs"]["ma_period"]}"
            else:
                self.has.update({"inputs":{
                        "source":self.source,
                        "show":False
                        }}) 
                self.has["name"] = f"{self.source.source_name}"
                
            self.sig_change_indicator_name.emit(self.has["name"])
            
            if mamode != None:
                self.source.refresh_data(mamode,ma_period,n_smooth_period)
            
    def change_interval(self):
        self._is_change_source = True
        ma_period = self.has["inputs"].get("mamode")
        n_smooth_period = self.has["inputs"].get("n_smooth_period")
        mamode = self.has["inputs"].get("mamode")

        if mamode != None:
            self.has["name"] = f"{self.source.source_name} {self.has["inputs"]["mamode"].name} {self.has["inputs"]["ma_period"]} {self.has["inputs"]["n_smooth_period"]}"
        else:
            self.has["name"] = f"{self.source.source_name}"
            
        self.sig_change_indicator_name.emit(self.has["name"])
        
        self.chart.sig_update_source.emit(self.source)

    
    def get_source(self,_type:IndicatorType,mamode:PD_MAType=PD_MAType.EMA, period:int=3,n:int=3):
        candle = None
        if _type == "japan" or _type == "Sub_Chart":
            candle = self.chart.jp_candle
            return self.chart.jp_candle, None,None, n

        elif _type == "smooth_jp":
            candle = SMOOTH_CANDLE(self.chart,self.chart.jp_candle,mamode,period)
            candle._source_name = f"sm_jp {self.chart.symbol} {self.chart.interval}"
            self.chart.update_sources(candle)
            return candle, mamode,period, n
        
        elif _type == "n_smooth_jp":
            candle = N_SMOOTH_CANDLE(self.chart,self.chart.jp_candle,n,mamode,period)
            candle._source_name = f"n_smooth_jp {self.chart.symbol} {self.chart.interval}"
            self.chart.update_sources(candle)
            return candle, mamode, period,n
        
        elif _type == "heikin":
            candle = self.chart.heikinashi
            return self.chart.heikinashi, None,None, n
            
        elif _type == "smooth_heikin":
            candle = SMOOTH_CANDLE(self.chart,self.chart.heikinashi,mamode,period)
            candle._source_name = f"sm_heikin {self.chart.symbol} {self.chart.interval}"
            self.chart.update_sources(candle)
            return candle, mamode,period, n
            
        elif _type == "n_smooth_heikin":
            candle = N_SMOOTH_CANDLE(self.chart,self.chart.heikinashi,n,mamode,period)
            candle._source_name = f"n_smooth_heikin {self.chart.symbol} {self.chart.interval}"
            self.chart.update_sources(candle)
            return candle, mamode, period,n
            
    def get_inputs(self):
        if isinstance(self.source,JAPAN_CANDLE) or isinstance(self.source,HEIKINASHI):
            return {}
        if isinstance(self.source,N_SMOOTH_CANDLE):
            return  {"mamode":self.has["inputs"]["mamode"],
                    "ma_period":self.has["inputs"]["ma_period"],
                    "n_smooth_period":self.has["inputs"]["n_smooth_period"],}
        inputs =  {"mamode":self.has["inputs"]["mamode"],
                    "ma_period":self.has["inputs"]["ma_period"],}
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
        self.threadpool_asyncworker(True)
    @Slot() 
    def set_price_line(self):
        lastcandle = self.source.last_data()
        self.price_line.update_data(lastcandle)
        
    def first_setup_candle(self):
        self.threadpool_asyncworker(True)
  
    def threadpool_asyncworker(self,candles=None|bool|list|int):
        self.worker = None
        self.worker = FastWorker(self.update_last_data,candles)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.AutoConnection)
        self.worker.signals.finished.connect(self.set_price_line,Qt.ConnectionType.AutoConnection)
        self.worker.start()
    
    def update_asyncworker(self,candles=None):
        self.worker = None
        self.worker = FastWorker(self.update_last_data,candles)
        self.worker.signals.setdata.connect(self.updateData,Qt.ConnectionType.AutoConnection)
        self.worker.signals.finished.connect(self.set_price_line,Qt.ConnectionType.AutoConnection)
        self.worker.start()
        
    def get_yaxis_param(self):
        if len(self.source.candles) > 0:
            last_candle = self.source.last_data()
            last_close_price_ = last_candle.close
            last_open_price_ = last_candle.open
            colorline = '#089981' if last_close_price_ >= last_open_price_ else '#f23645'
            last_color,last_close_price = colorline,last_close_price_
            return last_close_price,last_color
        else:
            return None,None
    def get_xaxis_param(self):
        return None,None

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

    def draw_candle(self,_open,_max,_min,close,w,t):
        "dieu kien de han che viec ve lai khi add new candle"
        if not self._bar_picutures.get(t):
            self.draw_single_candle(_open,_max,_min,close,w,t)
            return True
        return False

    def draw_single_candle(self,_open,_max,_min,close,w,t):
        candle_picture:QPicture =QPicture()
        p:QPainter =QPainter(candle_picture)
        if _open > close:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_lowcolor"],width=0.7)
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_lowcolor"])
            # brush = self.has["styles"]["brush_lowcolor"]
        else:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_highcolor"],width=0.7) 
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_highcolor"])
            # brush = self.has["styles"]["brush_highcolor"]
        if close == _open:
            if _max != _min:
                line = QLineF(QPointF(t, _min), QPointF(t, _max))
                p.drawLine(line)
            _line = QLineF(QPointF(t - w, _open), QPointF(t + w, close))
            p.drawLine(_line)
        else:
            if _max != _min:
                line = QLineF(QPointF(t, _min), QPointF(t, _max))
                p.drawLine(line)
            rect = QRectF(t - w, _open, w * 2, close - _open)  
            p.drawRect(rect)
            # p.fillRect(rect,brush)
        p.end()
        self._bar_picutures[t] = candle_picture
    @Slot()
    def setData(self, data) -> None:
        """y_data must be in format [[open, close, min, max], ...]"""
        self._to_update = False
        x_data, y_data = data[0],data[1]
        # w = (x_data[-1] - x_data[-2]) / 5
        w = 1 / 5
        _open,_max,_min,close = y_data[0],y_data[1],y_data[2],y_data[3]
        if self._is_change_source:
            self._bar_picutures.clear()
            self._is_change_source = False
        [self.draw_candle(_open[index],_max[index],_min[index],close[index],w,x_data[index]) for index in range(len(x_data))]
        self._to_update = True
        self.chart.sig_update_y_axis.emit()
        self.source.is_current_update = True
        # self.prepareGeometryChange()
        # self.informViewBoundsChanged()
        # self.update(self.boundingRect())
    @Slot()
    def updateData(self, data) -> None:
        """y_data must be in format [[open, close, min, max], ...]"""
        self._to_update = False
        x_data, y_data = data[0],data[1]
        w = (x_data[-1] - x_data[-2]) / 5
        pre_t = x_data[-2]
        t = x_data[-1]
        pre_open, pre_max, pre_min, pre_close = y_data[0][-2],y_data[1][-2],y_data[2][-2],y_data[3][-2]
        _open, _max, _min, _close = y_data[0][-1],y_data[1][-1],y_data[2][-1],y_data[3][-1]
        self.draw_single_candle(pre_open,pre_max,pre_min,pre_close,w,pre_t)
        self.draw_single_candle(_open,_max,_min,_close,w,t)
        self._to_update = True
        self.chart.sig_update_y_axis.emit()
        self.source.is_current_update = True
        # self.prepareGeometryChange()
        # self.informViewBoundsChanged()
        # self.update(self.boundingRect())
        
        
    def update_last_data(self,candles, setdata) -> None:
        if candles is None or isinstance(candles,list):
            x_data, y_data = self.source.get_index_data(start=-2)
        elif candles == True:
            x_data, y_data = self.source.get_index_data()
        else:
            n = len(self._bar_picutures)
            x_data, y_data = self.source.get_index_data(stop=n)
            
        if len(x_data) != len(y_data[0]):
            raise Exception("Len of x_data must be the same as y_data")
        setdata.emit((x_data, y_data))
        # self.setData((x_data, y_data))
