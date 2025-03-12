from functools import lru_cache
from typing import Union, Optional, Any, List, TYPE_CHECKING
import time
from PySide6 import QtGui
from PySide6.QtGui import QPainter,QMouseEvent
from PySide6.QtCore import Signal,QPointF,Qt,QThreadPool,QEvent
from PySide6.QtWidgets import QGraphicsView
import numpy as np
from atklip.app_utils.calculate import round_
from atklip.graphics.pyqtgraph import mkPen, PlotWidget
from atklip.appmanager import FastWorker
from atklip.graphics.chart_component.base_items import  PriceLine
from atklip.graphics.chart_component.indicators import *
from .plotitem import ViewPlotItem
from .proxy_signal import Signal_Proxy
from atklip.controls import *

from atklip.graphics.chart_component.indicator_panel import SubIndicatorContainer
from atklip.graphics.chart_component.indicator_panel import IndicatorPanel
from .globarvar import global_signal

if TYPE_CHECKING:
    from .viewchart import Chart
    from .viewbox import PlotViewBox
    from .axisitem import CustomDateAxisItem, CustomPriceAxisItem

class Crosshair:
    """Keyword arguments related to Crosshair used in LivePlotWidget"""
    ENABLED = "Crosshair_Enabled"  # Toggle crosshair: bool
    LINE_PEN = "Crosshair_Line_Pen"  # Pen to draw crosshair: QPen
    TEXT_KWARGS = "Text_Kwargs"  # Kwargs for crosshair markers: dict
    X_AXIS = "Crosshair_x_axis"  # Pick axis [default bottom] format and source for x ticks displayed in crosshair: str
    Y_AXIS = "Crosshair_y_axis"  # Pick axis [default left] format and source for y ticks displayed in crosshair: str


class ViewSubPanel(PlotWidget):
    mouse_clicked_signal = Signal(QEvent)
    crosshair_y_value_change = Signal(tuple)
    crosshair_x_value_change = Signal(tuple)
    mousepossiton_signal = Signal(tuple)
    sig_add_item = Signal(object)
    sig_remove_item = Signal(object)
    sig_add_indicator_panel = Signal(tuple)
    sig_delete_sub_panel = Signal(object)
    first_run = Signal()
    sig_update_y_axis = Signal()
    def __init__(self,chart, parent=None, background: str = "#161616",) -> None: #str = "#f0f0f0"
        # Make sure we have LiveAxis in the bottom
        #Crosshair()
        kwargs = {Crosshair.ENABLED: True,
          Crosshair.LINE_PEN: mkPen(color="#eaeaea", width=0.5,style=Qt.DashLine),
          Crosshair.TEXT_KWARGS: {"color": "#eaeaea"}} 
        self.Chart: Chart = chart
        self._precision = 3
        self.PlotItem = ViewPlotItem(context=self, type_chart="trading")    
        # self.sigSceneMouseMoved.
        self.manual_range = False
        self.magnet_on = False
        self.mouse_on_vb = False

        super().__init__(parent=parent,background=background, plotItem= self.PlotItem,**kwargs)
        
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)

        self.crosshair_enabled = kwargs.get(Crosshair.ENABLED, False)
        self._parent = parent
        # 

        
        
        self.sources = self.Chart.sources

        
        
        self.jp_candle = self.Chart.jp_candle
        self.container_indicator_wg = SubIndicatorContainer(self)

        #print("self.crosshair_enabled", self.crosshair_enabled)
        self.crosshair_items: List = []

        self.crosshair_x_axis = kwargs.get(Crosshair.X_AXIS, "bottom")
        self.crosshair_y_axis = kwargs.get(Crosshair.Y_AXIS, "left")
        
        
        self.ev_pos = None
        self.last_color = None
        self.last_close_price = None
        self.nearest_value = None
        
        # self.grid = GridItem(textPen="#1111")
        # self.addItem(self.grid)
        
        if self.crosshair_enabled:
            self._add_crosshair(kwargs.get(Crosshair.LINE_PEN, None),
                                kwargs.get(Crosshair.TEXT_KWARGS, {}))
        self.disableAutoRange()

        """Modified _______________________________________ """

        self.yAxis: CustomPriceAxisItem = self.getAxis('right')
        self.xAxis:CustomDateAxisItem = self.getAxis('bottom')
        self.yAxis.setWidth(70)
        self.xAxis.hide()
        
        self.vb:PlotViewBox = self.PlotItem.view_box

        self.lastMousePositon = None
        #self.ObjectManager = UniqueObjectManager()

        self.is_mouse_pressed = False
        self.indicator = None
        self.first_run = False
        self.threadpool = QThreadPool(self)
        self.threadpool.setMaxThreadCount(1)
        
        self.indicator_data = ()
        self.panel:IndicatorPanel = None
        
        self.sig_add_item.connect(self.add_item,Qt.ConnectionType.AutoConnection)
        self.sig_remove_item.connect(self.remove_item,Qt.ConnectionType.AutoConnection)

        self.sig_add_indicator_panel.connect(self.setup_indicator,Qt.ConnectionType.AutoConnection)
        
        Signal_Proxy(self.sig_update_y_axis,self.yAxis.change_view)
        Signal_Proxy(self.crosshair_y_value_change,slot=self.yAxis.change_value,connect_type = Qt.ConnectionType.AutoConnection)
        
        self.Chart.crosshair_x_value_change.connect(slot=self.xAxis.change_value,type=Qt.ConnectionType.AutoConnection)

        global_signal.sig_show_hide_cross.connect(self.show_hide_cross,Qt.ConnectionType.AutoConnection)
    
    def get_precision(self):
        return 3#self.Chart.get_precision()
     
    def setup_indicator(self,indicator_data):
        self.indicator_data = indicator_data
        _group_indicator = indicator_data[0][0]
        mainwindow = indicator_data[1]
        self.indicator_type =_indicator_type = indicator_data[0][1]
        self._precision = self.Chart.get_precision()
        if _indicator_type == IndicatorType.MACD:
            self.indicator = BasicMACD(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.RSI:
            self.indicator = BasicRSI(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.MOM:
            self.indicator = BasicMOM(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.RVGI:
            self.indicator = BasicRVGI(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.EMATrendMetter:
            self.indicator = EMATrendMetter(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.CCI:
            self.indicator = BasicCCI(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.VOLUME:
            self.indicator = Volume(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.ROC:
            self.indicator = BasicROC(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.TSI:
            self.indicator = BasicTSI(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.VTX:
            self.indicator = BasicVTX(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.StochRSI:
            self.indicator = BasicSTOCHRSI(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.TRIX:
            self.indicator = BasicTRIX(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.STC:
            self.indicator = BasicSTC(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.UO:
            self.indicator = BasicUO(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.Stoch:
            self.indicator = BasicSTOCH(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.SQEEZE:
            self.indicator = BaSicSqeeze(self.get_last_pos_worker,self.Chart,self)
        elif _indicator_type == IndicatorType.VOLUMEWITHMA:
            self.indicator = VolumeWithMA(self.get_last_pos_worker,self.Chart,self)
        
        
        
    
        if self.indicator:
            self.add_item(self.indicator)
            self.panel = IndicatorPanel(mainwindow,self, self.indicator)
            self.container_indicator_wg.add_indicator_panel(self.panel)
            self.indicator.fisrt_gen_data()
        return self.indicator
            
    
    def setdockLabel(self,docklabel):
        "để float kết nối more btn với float dock"
        self.dockLabel = docklabel
        self.panel.btn_more.clicked.connect(docklabel.floatDock)
        
    
    def fast_reset_worker(self):
        self.setup_indicator(self.indicator_data)
        
        
    async def reset_panel(self):
        while True:
            if len(self.jp_candle.candles) > 0:
                self.first_run = True
                break
            #await asyncio.sleep(0.1)
    def add_item(self,args):
        if isinstance(args,tuple):
            item = args[0]
        else:
            item = args
        self.addItem(item) 
        self.yAxis.dict_objects.update({item:item.has["y_axis_show"]})

    def remove_item(self,args):
        if isinstance(args,tuple):
            item = args[0]
        else:
            item = args
        del self.yAxis.dict_objects[item]
        
        if item in self.Chart.indicators:
            self.Chart.indicators.remove(item) 
        self.removeItem(item) 
        item.deleteLater()
        self.sig_delete_sub_panel.emit(self)
        #self.deleteLater()
    def slot_proxy_sigMouseMoved(self, pos):
        "de xem sau can lam gi khong"
        pass

    def get_last_pos_worker(self):
        self.worker = None
        self.worker = FastWorker(self.get_last_pos_of_indicator)
        self.worker.signals.setdata.connect(self.auto_xrange,Qt.ConnectionType.AutoConnection)
        self.worker.start()
    def get_last_pos_of_indicator(self,setdata):
        # if self.indicator != None:
        _min, _max = self.indicator.get_min_max()
        print(_min, _max)
        if _min != None:
            setdata.emit((_min, _max))
            return
        time.sleep(0.1)
        self.get_last_pos_of_indicator(setdata)
            
    def auto_xrange(self,lastpoint):
        _min,_max = lastpoint[0], lastpoint[1]
        # x_left,x_right = self.Chart.xAxis.range[0],self.Chart.xAxis.range[1]
        # self.setXRange(x_left,x_right,0.2)
        self.setYRange(_max + (_max-_min)*0.1, _min - (_max-_min)*0.1, padding=0.05)

    def show_hide_cross(self, value):
        _isshow, self.nearest_value = value[0],value[1]
        if _isshow:
            if self.nearest_value != None:
                if not self.vLine.isVisible():
                    self.vLine.show() 
                self.vLine.setPos(self.nearest_value)     
        else:
            self.hLine.hide()
            self.vLine.hide()
            self.crosshair_x_value_change.emit(("#363a45",None))
            self.crosshair_y_value_change.emit(("#363a45",None))
        self.vb.update()
    # Override addItem method
    def addItem(self, *args: Any, **kwargs: Any) -> None:
        self.vb.addItem(*args)
        # args[0].plot_widget = self
    
    def removeItem(self, *args):
        return self.vb.removeItem(*args)

    def _update_crosshair_position(self, pos) -> None:
        """Update position of crosshair based on mouse position"""
        # self._precision = self.Chart.get_precision()
        nearest_value_yaxis = pos.y()
        h_value = round(nearest_value_yaxis,4)
        if self.mouse_on_vb:
            if not self.hLine.isVisible():
                self.hLine.show()
            self.hLine.setPos(h_value)
            self.crosshair_y_value_change.emit(("#363a45",h_value))
        else:
            self.vLine.hide()
            self.hLine.hide()
        # self.vb.viewTransformChanged()
        # self.vb.informViewBoundsChanged()
        

    def _add_crosshair(self, crosshair_pen: QtGui.QPen, crosshair_text_kwargs: dict) -> None:
        self._precision = self.Chart.get_precision()
        """Add crosshair into plot"""
        self.vLine = PriceLine(angle=90, movable=False,precision=self._precision,dash=[5, 5])
        self.hLine = PriceLine(angle=0, movable=False,precision=self._precision,dash=[5, 5])
        # self.x_value_label = TextItem(**crosshair_text_kwargs)
        # self.y_value_label = TextItem(**crosshair_text_kwargs)
        # All Crosshair items
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

    def leaveEvent(self, ev: QMouseEvent) -> None:
        """Mouse left PlotWidget"""
        global_signal.sig_show_hide_cross.emit((False,self.nearest_value))
        self.crosshair_x_value_change.emit(("#363a45",None))
        self.crosshair_y_value_change.emit(("#363a45",None))

        if self.crosshair_enabled:
            self.hide_crosshair()
        super().leaveEvent(ev)

    def enterEvent(self, ev: QMouseEvent) -> None:
        """Mouse enter PlotWidget"""
        self._parent.sig_show_hide_cross.emit((True,self.nearest_value))
        if self.crosshair_enabled:
            self.show_crosshair()
        super().enterEvent(ev)

    # @lru_cache()
    def find_nearest_value(self,closest_value):
        #absolute_differences = np.abs(array - x)
        # Tìm chỉ số của phần tử có khoảng cách nhỏ nhất
        #index_of_closest_value = np.argmin(absolute_differences)
        # Lấy giá trị tại chỉ số tìm được
        #closest_value = array[index_of_closest_value]
        # closest_value = round_(x)
        # last_index = self.jp_candle.last_data().index
        # if last_index < closest_value:
        #     closest_value = last_index
        # index_of_closest_value = np.where(array == closest_value)[0][0]
        ohlcv = self.jp_candle.map_index_ohlcv[closest_value]
        #print(x,index,index_of_closest_value, closest_value)
        return ohlcv #index_of_closest_value, closest_value
    def mousePressEvent(self, ev):
        self.is_mouse_pressed =  True
        super().mousePressEvent(ev)
        
    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        self.is_mouse_pressed = False
    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        if not self.is_mouse_pressed:
            self._precision = self.Chart.get_precision()
            """Mouse moved in PlotWidget"""
            self.ev_pos = ev.position()

            self.lastMousePositon = self.PlotItem.vb.mapSceneToView(self.ev_pos)
            if self.crosshair_enabled and self.sceneBoundingRect().contains(self.ev_pos):
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
                    self.Chart.sig_show_candle_infor.emit(data)

                except:
                    pass
            elif not self.sceneBoundingRect().contains(self.ev_pos):
                self.mouse_on_vb = False
            
        super().mouseMoveEvent(ev)

    def emit_mouse_position(self, lastpos):
        pass

    def hide_crosshair(self) -> None:
        """Hide crosshair items"""
        self.hLine.setVisible(False)
        
    def show_crosshair(self) -> None:
        """Show crosshair items"""
        for item in self.crosshair_items:
            #if item.isVisible() is False:
            item.setVisible(True)