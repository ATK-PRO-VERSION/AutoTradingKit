# type: ignore
from typing import Union, Optional, Any, List, TYPE_CHECKING 
from functools import lru_cache
from .plotitem import ViewPlotItem
from atklip.controls import *

from PySide6 import QtGui
from PySide6.QtCore import Signal,QPointF,Qt,QSize,QEvent,QCoreApplication
from PySide6.QtGui import QColor,QPainter
from PySide6.QtWidgets import QGraphicsView
from atklip.graphics.pyqtgraph import mkPen, PlotWidget, InfiniteLine,SignalProxy


from atklip.controls.candle import SMOOTH_CANDLE, JAPAN_CANDLE

from .globarvar import global_signal
from .proxy_signal import Signal_Proxy
from atklip.graphics.chart_component.base_items import CandleStick, PriceLine
from atklip.graphics.chart_component.indicator_panel import IndicatorContainer
from atklip.app_utils import *
from atklip.graphics.chart_component.draw_tools import DrawTool
if TYPE_CHECKING:
    from .viewbox import PlotViewBox
    from .axisitem import CustomDateAxisItem, CustomPriceAxisItem
    

class Crosshair:
    """Keyword arguments related to Crosshair used in LivePlotWidget"""

    ENABLED = "Crosshair_Enabled"  # Toggle crosshair: bool
    LINE_PEN = "Crosshair_Line_Pen"  # Pen to draw crosshair: QPen
    TEXT_KWARGS = "Text_Kwargs"  # Kwargs for crosshair markers: dict
    X_AXIS = "Crosshair_x_axis"  # Pick axis [default bottom] format and source for x ticks displayed in crosshair: str
    Y_AXIS = "Crosshair_y_axis"  # Pick axis [default left] format and source for y ticks displayed in crosshair: str


class ViewPlotWidget(PlotWidget):
    mouse_clicked_signal = Signal(Any)
    sig_show_process = Signal(bool)
    sig_change_tab_infor = Signal(tuple)
    sig_goto_date = Signal(tuple)
    sig_change_market_type = Signal(str)
    "signal from TopBar"
    sig_add_item = Signal(object)
    sig_remove_item = Signal(object)
    crosshair_y_value_change = Signal(tuple)
    crosshair_x_value_change = Signal(tuple)
    mousepossiton_signal = Signal(tuple)
    sig_show_candle_infor = Signal(list)
    first_run = Signal()
    sig_add_indicator_panel = Signal(tuple)
    sig_reload_indicator_panel = Signal()
    sig_update_source = Signal(object)
    sig_remove_source = Signal(str)
    sig_update_y_axis = Signal() 

    def __init__(self, parent=None, type_chart="trading", background: str = "#161616",) -> None: #str = "#f0f0f0"
        # Make sure we have LiveAxis in the bottom
        #Crosshair()
        kwargs = {Crosshair.ENABLED: True,
          Crosshair.LINE_PEN: mkPen(color="#eaeaea", width=0.5,style=Qt.DashLine),
          Crosshair.TEXT_KWARGS: {"color": "#eaeaea"}} 

        self.PlotItem = ViewPlotItem(context=self, type_chart=type_chart)     # parent?
        # self.sigSceneMouseMoved.
        self.manual_range = False
        self.magnet_on = False
        self.mouse_on_vb = False

        super().__init__(parent=parent,background=background, plotItem= self.PlotItem,**kwargs)
        self.crosshair_enabled = kwargs.get(Crosshair.ENABLED, False)
                
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        # self.setOptimizationFlag(QGraphicsView.OptimizationFlag.IndirectPainting, True)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)

        self._parent = parent

        self.list_candle_indicators = []
        
        self.is_living = False
        self._precision = 3
        
        self.jp_candle = JAPAN_CANDLE()
        
        self.heikinashi = HEIKINASHI(self._precision,self.jp_candle)
        
        self.container_indicator_wg = IndicatorContainer(self)
        self.sig_show_candle_infor.connect(self.container_indicator_wg.get_candle_infor, Qt.ConnectionType.AutoConnection)

        #print("self.crosshair_enabled", self.crosshair_enabled)
        self.crosshair_items: List = []
        
        self.crosshair_x_axis = kwargs.get(Crosshair.X_AXIS, "bottom")
        self.crosshair_y_axis = kwargs.get(Crosshair.Y_AXIS, "left")
        
        self.yAxis = self.getAxis('right')
        self.xAxis = self.getAxis('bottom')
        self.ev_pos = None
        self.last_color = None
        self.last_close_price = None
        
        Signal_Proxy(self.crosshair_y_value_change,slot=self.yAxis.change_value,connect_type = Qt.ConnectionType.AutoConnection)
        Signal_Proxy(self.sig_update_y_axis,self.yAxis.change_view)
        if self.crosshair_enabled:
            self._add_crosshair(kwargs.get(Crosshair.LINE_PEN, None),
                                kwargs.get(Crosshair.TEXT_KWARGS, {}))
  
    
        self.disableAutoRange()
        # self.addItem = addItem
        # self.removeItem = removeItem
        
        """Modified _______________________________________ """

        self.yAxis: CustomPriceAxisItem = self.getAxis('right')
        self.xAxis:CustomDateAxisItem = self.getAxis('bottom')
        
        self.yAxis.setWidth(60)
        self.xAxis.hide()
        
        self.timedata, self.data = [], []
        self.vb:PlotViewBox = self.getViewBox()
        self.lastMousePositon = None
        self.nearest_value = None
        self.is_mouse_click = False
        #self.ObjectManager = UniqueObjectManager()
        self.mode_replay = False
        self.replay_enabled = False
        self.stop_replay_enabled = False
        self.is_running_replay = False
        self.is_cutting_replay = False
        self.is_get_old_zigzag_base = False

        self.drawtool = DrawTool(self)
        
        Signal_Proxy(signal=self.sig_add_item,slot=self.add_item,connect_type=Qt.ConnectionType.QueuedConnection)
        Signal_Proxy(signal=self.sig_remove_item,slot=self.remove_item,connect_type=Qt.ConnectionType.QueuedConnection)

        global_signal.sig_show_hide_cross.connect(self.show_hide_cross,Qt.ConnectionType.AutoConnection)

    def set_precision(self,precision):
        self._precision = precision
    
    def get_precision(self):
        return self._precision

    def show_hide_cross(self, value):
        _isshow, self.nearest_value = value[0],value[1]
        if _isshow:
            if self.nearest_value != None:
                self.vLine.setPos(self.nearest_value)  
                if not self.vLine.isVisible():
                    self.vLine.show()
                self.crosshair_x_value_change.emit(("#363a45",self.nearest_value))
        else:
            self.hLine.hide()
            self.vLine.hide()
            self.crosshair_x_value_change.emit(("#363a45",None))
            self.crosshair_y_value_change.emit(("#363a45",None))
        # self.vb.viewTransformChanged()
        # self.vb.informViewBoundsChanged()
            
    # Override addItem method
    def add_item(self,args):
        if isinstance(args,tuple):
            item = args[0]
        else:
            item = args
        self.list_candle_indicators.append(item)
        self.addItem(item) 
        if "y_axis_show" in list(item.has.keys()):
            self.yAxis.dict_objects.update({item:item.has["y_axis_show"]})
        if "x_axis_show" in list(item.has.keys()):
            self.xAxis.dict_objects.update({item:item.has["x_axis_show"]})
                
    def remove_item(self,args):
        if isinstance(args,tuple):
            item = args[0]
        else:
            item = args
        self.list_candle_indicators.remove(item)
        del self.yAxis.dict_objects[item]
        self.removeItem(item) 
        item.deleteLater()
    def addItem(self, *args: Any, **kwargs: Any) -> None:
        if hasattr(args[0], "_vl_kwargs") and args[0]._vl_kwargs is not None:
            self.plotItem.addItem(args[0]._vl_kwargs["line"], ignoreBounds=True)
            self.plotItem.addItem(args[0]._vl_kwargs["text"], ignoreBounds=True)
            args[0].plot_widget = self
            return
        elif hasattr(args[0], "_hl_kwargs") and args[0]._hl_kwargs is not None:
            self.plotItem.addItem(args[0]._hl_kwargs["line"], ignoreBounds=True)
            self.plotItem.addItem(args[0]._hl_kwargs["text"], ignoreBounds=True)
            args[0].plot_widget = self
            return
        elif hasattr(args[0], "update_leading_line"):
            setattr(args[0], "x_format", self.x_format)
            setattr(args[0], "y_format", self.y_format)
        self.plotItem.addItem(*args)
        args[0].plot_widget = self
    def auto_xrange(self):
        timedata,data = self.jp_candle.get_index_data()
        # Clip values to avoid overflow
        timedata = np.clip(timedata, -1e30, 1e30)
        # Optionally normalize data
        # timedata = (timedata - np.mean(timedata)) / np.std(timedata)
        if len(timedata) >= 800:
            x1 = np.float64(timedata[-1])
            x2 = np.float64(timedata[-800])
            self.setXRange(x1, x2, padding=0.2)
            
            _min = data[2][-800:].min()
            _max = data[1][-800:].max()
            self.setYRange(_max, _min, padding=0.2)
        else:
            x1 = np.float64(timedata[-1])
            x2 = np.float64(timedata[-1*len(timedata)])
            self.setXRange(x1, x2, padding=0.2)
            _min = data[2][-800:].min()
            _max = data[1][-800:].max()
            self.setYRange(_max, _min, padding=0.2)
    def removeItem(self, *args):
        return self.plotItem.removeItem(*args)

    def set_replay_data(self, data):
        #print(data)
        cursor_pixmap = QtGui.QPixmap('scissors.png')
        # Create a QCursor object with the custom pixmap
        # Resize the pixmap to the desired dimensions
        new_size = QSize(25, 25)  # Set the desired width and height
        cursor_pixmap = cursor_pixmap.scaled(new_size)
        cursor = QtGui.QCursor(cursor_pixmap)
        # Set the cursor on the view
        self.vb.setCursor(cursor)
        # self.vLine_replay.setPos(data[0])
        # self.replay_object.set_data(data[0],data[1],data[2],data[3])

    def _update_crosshair_position(self, pos) -> None:
        """Update position of crosshair based on mouse position"""
        nearest_value_yaxis = pos.y()
        h_value = round(nearest_value_yaxis,self._precision)
        if not self.is_cutting_replay and self.mouse_on_vb:
            self.hLine.setPos(h_value)
            self.crosshair_y_value_change.emit(("#363a45",h_value))
        else:
            self.vLine.hide()
            self.hLine.hide()
        
    def _add_crosshair(self, crosshair_pen: QtGui.QPen, crosshair_text_kwargs: dict) -> None:
        """Add crosshair into plot"""
        self.vLine = PriceLine(angle=90, movable=False,precision=self._precision,dash=[5, 5])
        self.hLine = PriceLine(angle=0, movable=False,precision=self._precision,dash=[5, 5])
        self.crosshair_items = [self.hLine, self.vLine]
        for item in self.crosshair_items:
            # Make sure, that every crosshair item is painted on top of everything
            item.setZValue(999)
            self.addItem(item)
        # Hide crosshair at the beginning
        self.hide_crosshair()

    def x_format(self, value: Union[int, float]) -> str:
        """X tick format"""
        try:
            # Get crosshair X str format from bottom tick axis format
            return self.getPlotItem().axes[self.crosshair_x_axis]["item"].tickStrings((value,), 0, 1)[0]
        except Exception:
            return str(round(value, 4))

    def y_format(self, value: Union[int, float]) -> str:
        """Y tick format"""
        try:
            # Get crosshair Y str format from left tick axis format
            return self.getPlotItem().axes[self.crosshair_y_axis]["item"].tickStrings((value,), 0, 1)[0]
        except Exception:
            return str(round(value, 4))

    def leaveEvent(self, ev: QEvent) -> None:
        """Mouse left PlotWidget"""
        global_signal.sig_show_hide_cross.emit((False,self.nearest_value))

        self.crosshair_x_value_change.emit(("#363a45",None))
        self.crosshair_y_value_change.emit(("#363a45",None))

        if self.crosshair_enabled:
            self.hide_crosshair()
        super().leaveEvent(ev)

    def enterEvent(self, ev: QEvent) -> None:
        """Mouse enter PlotWidget"""
        if not self.vLine.isVisible():
                self.vLine.show()
        self._parent.sig_show_hide_cross.emit((True,self.nearest_value))
        if self.crosshair_enabled:
            self.show_crosshair()
        super().enterEvent(ev)

    # @lru_cache()
    def find_nearest_value(self,closest_index):
        #absolute_differences = np.abs(array - x)
        # Tìm chỉ số của phần tử có khoảng cách nhỏ nhất
        #index_of_closest_value = np.argmin(absolute_differences)
        # Lấy giá trị tại chỉ số tìm được
        #closest_value = array[index_of_closest_value]
        #closest_index = round_(x)
        # index_of_closest_value = np.where(array == closest_value)[0][0]
        ohlcv = self.jp_candle.dict_index_ohlcv[closest_index]
        #print(x,index,index_of_closest_value, closest_value)
        return ohlcv #index_of_closest_value, closest_value
    
    def mousePressEvent(self, ev):
        self.is_mouse_click =  True
        self.mouse_clicked_signal.emit(None)
        super().mousePressEvent(ev)
        

    def mouseReleaseEvent(self, ev):
        self.is_mouse_click = False
        self.drawtool.drawing_object = None
        self.drawtool.draw_object_name = None
        super().mouseReleaseEvent(ev)
        

    def mouseMoveEvent(self, ev: QEvent) -> None:
        """Mouse moved in PlotWidget"""
        if not self.is_mouse_click:# and not self.drawtool.drawing_object:
            try:
                self.ev_pos = ev.position()
            except:
                self.ev_pos = ev.pos()
            self.lastMousePositon = self.plotItem.vb.mapSceneToView(self.ev_pos)

            if self.crosshair_enabled and self.sceneBoundingRect().contains(self.ev_pos):
                if not self.hLine.isVisible():
                    self.hLine.show()
                self.mouse_on_vb = True
                nearest_index = None
                try:
                    closest_index = round_(self.lastMousePositon.x())
                    last_index = self.jp_candle.last_data().index
                    if last_index < closest_index:
                        closest_index = last_index
                    ohlcv:OHLCV = self.find_nearest_value(closest_index)
                    self.nearest_value = ohlcv.time
                    data = [ohlcv.open,ohlcv.high,ohlcv.low,ohlcv.close]
                    self._update_crosshair_position(self.lastMousePositon)
                
                    self._parent.sig_show_hide_cross.emit((True,ohlcv.index))
                    ##QCoreApplication.processEvents()
                    self.sig_show_candle_infor.emit(data)
                    ##QCoreApplication.processEvents()
                except:
                    pass
            elif not self.sceneBoundingRect().contains(self.ev_pos):
                self.mouse_on_vb = False
            
            self.emit_mouse_position(self.lastMousePositon)
        super().mouseMoveEvent(ev)

    def emit_mouse_position(self, lastpos):
        if not self.drawtool.drawing_object:
            if hasattr(self.drawtool.drawing_object,"setPoint"): 
                self.drawtool.drawing_object.setPoint(lastpos.x(),lastpos.y())

    def hide_crosshair(self) -> None:
        """Hide crosshair items"""
        self.hLine.setVisible(False)

    def show_crosshair(self) -> None:
        """Show crosshair items"""
        for item in self.crosshair_items:
            #if item.isVisible() is False:
            item.setVisible(True)
    @property
    def vbrange(self):
        vbrange = self.vb.viewRange()
        xmin, xmax = map(int, vbrange[0])
        return (xmin, xmax)