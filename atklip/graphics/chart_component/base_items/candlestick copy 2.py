from typing import Dict, Optional, Tuple, List,TYPE_CHECKING
import numpy as np

from PySide6.QtCore import Signal, QRect, QRectF, QPointF,QThreadPool,Qt,QLineF,QCoreApplication
from PySide6.QtGui import QPainter, QPicture,QPainterPath
from PySide6.QtWidgets import QGraphicsItem,QStyleOptionGraphicsItem,QWidget
from atklip.graphics.pyqtgraph import mkPen, GraphicsObject, mkBrush

from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE

from atklip.appmanager import FastWorker
from .price_lines import PriceLine

from atklip.controls.ma_type import  PD_MAType,IndicatorType
from atklip.controls.ohlcv import OHLCV

from atklip.controls.models import BaseCandleModel

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_chart import SubChart


class CandleStick(GraphicsObject):
    """Live candlestick plot, plotting data [[open, close, min, max], ...]"""
    sig_deleted_source = Signal(object)
    signal_delete = Signal()
    sig_change_name = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart,name, high_color: str = '#089981', low_color: str = '#f23645') -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.setZValue(999)
        
        self.chart:Chart|SubChart = chart
        
        self.object_id = self.chart.objmanager.add(self)
        
                
        self.params = BaseCandleModel(self.chart.id,self.id,name,self.chart.exchange_name,self.chart.symbol,self.chart.interval)
        
        if ma_type != None:
            self.has = {
            "is_candle": True,
            "name": f"{self.source.source_name} {ma_type.name} {period} {n}",
            "y_axis_show":True,
            "inputs":{
                    "source":self.source,
                    "ma_type":ma_type,
                    "ma_period":period,
                    "n_smooth_period": n,
                    "show":True
                    },

            "styles":{
                "pen_highcolor":high_color,
                "pen_lowcolor" : low_color,
                "brush_highcolor":mkBrush(high_color,width=0.7),
                "brush_lowcolor":mkBrush(low_color,width=0.7)
                    }
                }
        else:
            self.has = {
            "name": f"{self.source.source_name}",
            "y_axis_show":True,
            "inputs":{
                    "source":self.source,
                    "show":False
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
        self.picture: QPicture = None
        self._rect_area: Tuple[float, float] = None
        self._to_update: bool = False
        self._is_change_source:bool=False
        self._start:int = None
        self._stop:int = None

        self.historic_candle = SingleCandleStick(self.chart,self.source,has=self.has)
        self.historic_candle.setParentItem(self)
        
        self.signal_delete.connect(self.delete_source)
        self.sig_deleted_source.connect(self.chart.remove_source)
        
        self.source.sig_reset_all.connect(self.update_source,Qt.ConnectionType.QueuedConnection)
        
        self.source.sig_add_candle.connect(self.threadpool_asyncworker,Qt.ConnectionType.QueuedConnection)
        self.source.sig_add_historic.connect(self.threadpool_asyncworker,Qt.ConnectionType.QueuedConnection)
        
    
    @property
    def id(self):
        return self.object_id
    
    @property
    def id(self):
        return self.object_id
    
    def delete_source(self):
        self.sig_deleted_source.emit(self.source)
        self.source.signal_delete.emit()
        
    def update_source(self):
        self._is_change_source = True
        self.chart.remove_source(self.source)
        source_name = self.has["name"].split(" ")[0]
        if isinstance(self.source,N_SMOOTH_CANDLE):
            self.has["name"] = f"{source_name} {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["ma_period"]} {self.has["inputs"]["n_smooth_period"]}"
        if isinstance(self.source,SMOOTH_CANDLE):
            self.has["name"] = f"{source_name} {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["ma_period"]}"
        else:
            self.has["name"] = f"{source_name} {self.chart.symbol} {self.chart.interval}"
        
        self.source.source_name = self.has["name"]
        
        self.chart.update_sources(self.source)
        self.sig_change_indicator_name.emit(self.has["name"])
        
        self.first_setup_market()
    
    def update_inputs(self,_input,_source):
        """"source":self.source,
                "ma_type":self.has["inputs"]["ma_type"],
                "ma_period":self.has["inputs"]["ma_period"]"""
        update = False
        if _input == "ma_type":
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
            ma_type = self.has["inputs"].get("ma_type")
            
            if ma_type != None:
                if isinstance(self.source,N_SMOOTH_CANDLE):
                    self.has["name"] = f"{self.source.source_name} {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["ma_period"]} {self.has["inputs"]["n_smooth_period"]}"
                else:
                    self.has["name"] = f"{self.source.source_name} {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["ma_period"]}"
            else:
                self.has.update({"inputs":{
                        "source":self.source,
                        "show":False
                        }}) 
                self.has["name"] = f"{self.source.source_name}"
                
            self.sig_change_indicator_name.emit(self.has["name"])
            
            if ma_type != None:
                self.source.refresh_data(ma_type,ma_period,n_smooth_period)
            
    def change_interval(self):
        self._is_change_source = True
        ma_period = self.has["inputs"].get("ma_type")
        n_smooth_period = self.has["inputs"].get("n_smooth_period")
        ma_type = self.has["inputs"].get("ma_type")

        if ma_type != None:
            self.has["name"] = f"{self.source.source_name} {self.has["inputs"]["ma_type"].name} {self.has["inputs"]["ma_period"]} {self.has["inputs"]["n_smooth_period"]}"
        else:
            self.has["name"] = f"{self.source.source_name}"
            
        self.sig_change_indicator_name.emit(self.has["name"])
        
        self.chart.sig_update_source.emit(self.source)

    
    
    def get_source(self,_type:IndicatorType,ma_type:PD_MAType=PD_MAType.EMA, period:int=3,n:int=3):

        if _type.value == "japan" or _type.value == "Sub_Chart":
            return self.chart.jp_candle, None,None, n

        elif _type.value == "smooth_jp":
            smooth_jp_candle = SMOOTH_CANDLE(self.precision,self.chart.jp_candle,ma_type,period)
            smooth_jp_candle._source_name = f"sm_jp {self.chart.symbol} {self.chart.interval}"
            self.chart.update_sources(smooth_jp_candle)
            smooth_jp_candle.fisrt_gen_data()
            return smooth_jp_candle, ma_type,period, n
        
        elif _type.value == "n_smooth_jp":
            n_smooth_jp = N_SMOOTH_CANDLE(self.precision,self.chart.jp_candle,n,ma_type,period)
            n_smooth_jp._source_name = f"n_smooth_jp {self.chart.symbol} {self.chart.interval}"
            self.chart.update_sources(n_smooth_jp)
            n_smooth_jp.fisrt_gen_data()
            return n_smooth_jp, ma_type, period,n
        
        elif _type.value == "heikin":
            return self.chart.heikinashi, None,None, n
            
        elif _type.value == "smooth_heikin":
            smooth_heikin = SMOOTH_CANDLE(self.precision,self.chart.heikinashi,ma_type,period)
            smooth_heikin._source_name = f"sm_heikin {self.chart.symbol} {self.chart.interval}"
            self.chart.update_sources(smooth_heikin)
            smooth_heikin.fisrt_gen_data()
            return smooth_heikin, ma_type,period, n
            
        elif _type.value == "n_smooth_heikin":
            n_smooth_heikin = N_SMOOTH_CANDLE(self.precision,self.chart.heikinashi,n,ma_type,period)
            n_smooth_heikin._source_name = f"n_smooth_heikin {self.chart.symbol} {self.chart.interval}"
            self.chart.update_sources(n_smooth_heikin)
            n_smooth_heikin.fisrt_gen_data()
            return n_smooth_heikin, ma_type, period,n
            
    def get_inputs(self):
        if isinstance(self.source,JAPAN_CANDLE) or isinstance(self.source,HEIKINASHI):
            return {}
        if isinstance(self.source,N_SMOOTH_CANDLE):
            return  {"ma_type":self.has["inputs"]["ma_type"],
                    "ma_period":self.has["inputs"]["ma_period"],
                    "n_smooth_period":self.has["inputs"]["n_smooth_period"],}
        inputs =  {"ma_type":self.has["inputs"]["ma_type"],
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
        self.historic_candle.reset_threadpool_asyncworker()
        self.threadpool_asyncworker(True)
        
    def set_price_line(self):
        self.historic_candle.price_line.update_data(self.source.candles[-2:])
        self.historic_candle.threadpool_asyncworker(self.source.candles[-2:])
    
    
    def first_setup_market(self):
        self.threadpool_asyncworker(True)
        # x_data, y_data = self.source.get_index_data(stop=-1)
        # self.setData((x_data, y_data))
  
    def threadpool_asyncworker(self,candles=None):
        self.worker = None
        self.worker = FastWorker(self.update_last_data,candles)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.QueuedConnection)
        self.worker.signals.finished.connect(self.set_price_line,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    def get_yaxis_param(self):
        if len(self.source.candles) > 0:
            last_candle = self.source.last_data()
            last_close_price_ = last_candle.close
            last_open_price_ = last_candle.open
            colorline = "green" if last_close_price_ >= last_open_price_ else "red"
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
        if self._start is None or self._stop is None:
            x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
            start_index = self.chart.jp_candle.candles[0].index
            stop_index = self.chart.jp_candle.candles[-1].index
            if x_left > start_index:
                self._start = x_left+2
            else:
                self._start = start_index+2
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
        df = self.chart.jp_candle.get_df()
        if len(df) == 0:
            return QRectF(0,0,0,0)
        h_high =  df["high"].iloc[self._start:self._stop].max()
        h_low = df["low"].iloc[self._start:self._stop].min()
        rect = QRectF(x_left,h_low,self._stop-self._start,h_high-h_low)
        return rect

    def draw_candle(self,_open,_max,_min,close,w,t):
        # t = x_data[index]
        "dieu kien de han che viec ve lai khi add new candle"
        if not self._bar_picutures.get(t):
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
            _height = close - _open
            if _height == 0:
                if _max != _min:
                    line = QLineF(QPointF(t, _min), QPointF(t, _max))
                    p.drawLine(line)
                _line = QLineF(QPointF(t - w, _open), QPointF(t + w, close))
                p.drawLine(_line)
            else:
                line = QLineF(QPointF(t, _min), QPointF(t, _max))
                p.drawLine(line)
                rect = QRectF(t - w, _open, w * 2, close - _open)  
                p.drawRect(rect)
            p.end()
            self._bar_picutures[t] = candle_picture

    def setData(self, data) -> None:
        """y_data must be in format [[open, close, min, max], ...]"""
        self._to_update = False
        w = 1 / 5
        x_data, y_data = data[0],data[1]
        _open,_max,_min,close = y_data[0],y_data[1],y_data[2],y_data[3]
        if self._is_change_source:
            self._bar_picutures.clear()
            self._is_change_source = False
        [self.draw_candle(_open[index],_max[index],_min[index],close[index],w,x_data[index]) for index in range(len(x_data))]
        # p.end()
        self._to_update = True
        # self.chart.sig_update_y_axis.emit()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        
    def update_last_data(self,candles, setdata) -> None:
        if candles is None or isinstance(candles,list):
            last_candles = self.source.get_candles(-2)
            last_candle = last_candles[0]
            x_data, y_data = [last_candle.index], [[last_candle.open],[last_candle.high],[last_candle.low],[last_candle.close]]
        elif candles == True:
            x_data, y_data = self.source.get_index_data(stop=-1)
        else:
            n = len(self._bar_picutures)
            x_data, y_data = self.source.get_index_data(stop=n+1)
        try:
            if len(x_data) != len(y_data[0]):
                raise Exception("Len of x_data must be the same as y_data")
            # setdata.emit((x_data, y_data))
            self.setData((x_data, y_data))
            # QCoreApplication.processEvents()
        except Exception as e:
            print(f"loi update {e}")
    
class SingleCandleStick(GraphicsObject):
    """Live candlestick plot, plotting data [[open, close, min, max], ...]"""
    sigPlotChanged = Signal(object)
    yaxis_lastprice =  Signal()

    def __init__(self,chart,_candles, has) -> None:
        """Choose colors of candle"""
        GraphicsObject.__init__(self)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.setZValue(999)
        
        self.has = has
        self.chart:Chart|SubChart = chart 
        
        self._canldes: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE = _candles
        
        self.price_line = PriceLine()  # for z value
        self.price_line.setParentItem(self)
        self.destroyed.connect(self.price_line.deleteLater)

        self.picture = QPicture()
        self.colorline = 'white'

        self.old_w = []

        self._canldes.sig_update_candle.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self._canldes.sig_add_candle.connect(self.threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self._canldes.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)

    def set_price_line(self):
        self.price_line.update_data(self._canldes.last_data())
  
    def reset_threadpool_asyncworker(self):
        self.worker = None
        self.worker = FastWorker(self.update_last_data)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.QueuedConnection)
        self.worker.signals.finished.connect(self.set_price_line,Qt.ConnectionType.QueuedConnection)
        self.worker.start()
    
    def threadpool_asyncworker(self, last_candle:List[OHLCV]=[]):
        self.worker = None
        self.worker = FastWorker(self.update_last_data)
        self.worker.signals.setdata.connect(self.setData,Qt.ConnectionType.QueuedConnection)
        self.worker.signals.finished.connect(self.set_price_line,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    def paint(self, p: QPainter, *args) -> None:
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self) -> QRect:
        return QRectF(self.picture.boundingRect())
    
    def draw_candle(self,p:QPainter,_open,_max,_min,close,w,t):
        if _open > close:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_lowcolor"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_lowcolor"])
            
        else:
            self.outline_pen = mkPen(color=self.has["styles"]["pen_highcolor"],width=0.7) #,width=0.7
            p.setPen(self.outline_pen)
            p.setBrush(self.has["styles"]["brush_highcolor"])
        
        _height = close - _open
        if _height == 0:
            if _max != _min:
                line = QLineF(QPointF(t, _min), QPointF(t, _max))
                p.drawLine(line)
            _line = QLineF(QPointF(t - w, _open), QPointF(t + w, close))
            p.drawLine(_line)
        else:
            line = QLineF(QPointF(t, _min), QPointF(t, _max))
            p.drawLine(line)
            rect = QRectF(t - w, _open, w * 2, close - _open)  
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
        _open, _max, _min, close = y_data[-1][0],y_data[-1][1],y_data[-1][2],y_data[-1][3]
        self.draw_candle(p,_open,_max,_min,close,w,t)
        p.end()
        self.chart.sig_update_y_axis.emit()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()

    def update_last_data(self,setdata) -> None:
        if self._canldes.first_gen:
            if self._canldes.candles != []:
                last_candle = self._canldes.last_data()
                x_data, _y_data = [last_candle.index], [[last_candle.open,last_candle.high,last_candle.low,last_candle.close]]
                try:
                    setdata.emit((x_data, _y_data))
                    self.yaxis_lastprice.emit()
                except Exception as e:
                    pass

