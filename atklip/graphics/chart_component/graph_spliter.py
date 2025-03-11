import asyncio
from functools import partial
from atklip.graphics.pyqtgraph import GraphicsView,GraphicsLayout, setConfigOption
from atklip.graphics.pyqtgraph.dockarea import DockArea, Dock,DockLabel
from atklip.graphics.chart_component import  CustomDateAxisItem
from .viewchart import Chart
from .sub_chart import SubChart
from atklip.gui.qfluentwidgets.common import FluentStyleSheet
from PySide6.QtWidgets import QWidget, QSplitter,QApplication,QLabel,QFrame
from .pliterbox_ui import Ui_Form
from .axisitem import *
from .sub_panel_indicator import ViewSubPanel 
from .proxy_signal import Signal_Proxy
from atklip.graphics.chart_component.indicators import *
from atklip.controls import IndicatorType
from atklip.gui.qfluentwidgets.components.dialog_box import MessageBox
from atklip.gui.play_bar.replay_bar import Playbar


from PySide6.QtCore import QCoreApplication,QSize,QEvent
from PySide6.QtGui import QCloseEvent,QIcon
from PySide6.QtWidgets import QApplication

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.gui.views.mainlayout import MainWidget

setConfigOption("crashWarning",True)

class CustomDockArea(DockArea):
    def __init__(self, parent=None, temporary=False, home=None):
        super(CustomDockArea, self).__init__(parent=parent, temporary=temporary, home=home)
        self._parent: ViewSplitter = parent
        self.setContentsMargins(0,0,0,0)
        
    def addDock(self, dock=None, position='bottom', relativeTo=None, **kwds):
        _dock:CustomDock = dock
        if self._parent.chart is not None and not isinstance(_dock.panel, Chart):
            if not isinstance(_dock.panel, SubChart):
                _dock.panel.vb.setXLink(self._parent.chart.vb)
            _dock.panel.xAxis.hide()
            self._parent.chart.crosshair_x_value_change.disconnect(_dock.panel.xAxis.change_value)
        super().addDock(dock=dock, position=position, relativeTo=relativeTo, **kwds)
    
    def floatDock(self, dock):
        """Removes *dock* from this DockArea and places it in a new window."""
        area = self.addTempArea()
        area.win.resize(dock.size())
        area.moveDock(dock, 'top', None)
        return area
    def closeEvent(self, event: QCloseEvent) -> None:
        event.accept()
    
class CustomDock(Dock):
    sig_delete = Signal()
    def __init__(self,parent, name, area=None, size=(10, 10), widget=None, hideTitle=False, autoOrientation=True, label=None, **kargs):
        super(CustomDock, self).__init__(name, area=area, size=size, widget=widget, hideTitle=hideTitle, autoOrientation=autoOrientation, label=label, **kargs)
        self.parent:ViewSplitter = parent
        self.chart = self.parent.chart
        self.panel: ViewSubPanel|Chart|SubChart = None
        self.sig_delete.connect(self.deleteLater)
        
    def addWidget(self, widget: QWidget|Chart|SubChart|ViewSubPanel, row=None, col=0, rowspan=1, colspan=1):
        self.panel = widget
        # if isinstance(self.panel,SubChart):
        #     self.panel.xAxis.show()
        super().addWidget(widget, row=row, col=col, rowspan=rowspan, colspan=colspan)
    def float(self):
        if self.panel is not None and self.chart is not None:
            self.panel.vb.setXLink(self.panel.vb)
            self.panel.xAxis.show()
            if not isinstance(self.panel,SubChart):
                self.panel.Chart.crosshair_x_value_change.connect(slot=self.panel.xAxis.change_value,type=Qt.ConnectionType.AutoConnection)  
        area:QWidget = self.area.floatDock(self)
        self.sig_delete.connect(area.parent().close)
        self.sig_delete.connect(area.parent().deleteLater)

class CustomDockLabel(DockLabel):
    
    def __init__(self, text):
        super(CustomDockLabel, self).__init__(text, closable=False, fontSize="12px")
    
    def mouseDoubleClickEvent(self, ev):
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dock.float()
    def floatDock(self):
        self.dock.float()
    
    def updateStyle(self):
        r = '3px'
        if self.dim:
            fg = '#d1d4dc'
            bg = 'rgb(43, 43, 43)'
            border = 'rgb(43, 43, 43)'
        else:
            fg = '#d1d4dc'
            bg = 'rgb(43, 43, 43)'
            border = 'rgb(43, 43, 43)'

        if self.orientation == 'vertical':
            self.vStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: 0px;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: %s;
                border-width: 0px;
                border-right: 2px solid %s;
                padding-top: 3px;
                padding-bottom: 3px;
                font-size: %s;
            }""" % (bg, fg, r, r, border, self.fontSize)
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: %s;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-width: 0px;
                border-bottom: 2px solid %s;
                padding-left: 3px;
                padding-right: 3px;
                font-size: %s;
            }""" % (bg, fg, r, r, border, self.fontSize)
            self.setStyleSheet(self.hStyle)
    

class ViewSplitter(QFrame,Ui_Form):
    # sig_add_indicator_to_chart = Signal(tuple)
    sig_add_sub_panel = Signal(object)
    sig_show_hide_cross = Signal(tuple)
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self.listwidgets = []
        self.setContentsMargins(0,0,0,0)
        self.setFrameShape(QFrame.NoFrame)
        self.setupUi(self)
        self.axis_layout.setContentsMargins(0,0,0,0)
        self.axis_layout.setSpacing(0)
        self.splitter.setContentsMargins(0,0,0,0)
        self.splitter.setSpacing(0)
        
        
        self.mainwindow = None
        self.chart:Chart = None
        
        self.replay_bar:Playbar = None
        
        self.dateAxis = None
        self.is_started = False
        
        self.DockArea = CustomDockArea(self)
        self.splitter.addWidget(self.DockArea)

    def create_indicator(self,data):...
    
    def addWidget(self,widget:QWidget|Chart|SubChart|ViewSubPanel):
        _dock = CustomDock(parent=self,name="",closable = False,hideTitle=True,label=CustomDockLabel(""))
        if isinstance(widget,ViewSubPanel) or isinstance(widget,SubChart):
            widget.setdockLabel(_dock.label)
        _dock.addWidget(widget)
        widget.destroyed.connect(_dock.sig_delete)
        self.DockArea.addDock(_dock)
  
    def addItem(self,item:QWidget):
        self.axis_layout.addWidget(item,0,Qt.AlignmentFlag.AlignTop)
    
    def removeItem(self,item: QWidget):
        self.axis_layout.removeWidget(item)
        item.deleteLater()


class GraphSplitter(ViewSplitter):
    mouse_clicked_signal = Signal(QEvent)
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self.stratygies:dict = {IndicatorType.ATKBOT_SUPERTREND_SSCANDLE:{"Advance Indicator":IndicatorType.ATKPRO,
                                                                         "Advance Indicator":IndicatorType.ATKPRO,
                                                                         "Candle Indicator":IndicatorType.N_SMOOTH_JP},
                                IndicatorType.ATKBOT_SUPERTREND:[],
                                IndicatorType.ATKBOT_CCI:[]}
        # self.sig_add_indicator_to_chart.connect(self.create_indicator,Qt.ConnectionType.AutoConnection)
        self.sig_add_sub_panel.connect(self.add_sub_panel,Qt.ConnectionType.AutoConnection)

    def reload_pre_indicator(self):
        "load pre saved indicator"
        self.create_indicator(("Candle Idicators",IndicatorType.JAPAN_CANDLE))

    def create_indicator(self,data):
        "Tạo Indicator panel và setup cho Chart hoặc Sub-Indicator"
        """('Basic Indicator', 'SMA-Simple Moving Average')"""  
        indicator_type = data[0]
        name = data[1]
        if indicator_type =="Sub Indicators":
            self.create_sub_indicator(data)
        elif indicator_type =="Basic Indicators":
            self.create_basic_indicator(data)
        elif indicator_type =="Candle Idicators":
            self.create_candle_indicator(data)
        elif indicator_type =="Advand Idicators":
            self.create_advand_indicator(data)
        elif indicator_type =="Sub View Idicators":
            self.create_sub_chart(data)
        elif indicator_type =="Strategies":
            self.create_strategy(data)
        elif indicator_type =="Paterns":
            self.create_advand_indicator(data)  
        elif indicator_type =="Profiles":
            self.create_advand_indicator(data)  
        else:
            print("Unknown Indicator Type")

    def create_strategy(self,data):
        "Tạo Panel cho Strategy"
        strategy_group = data[0]
        strategy_type = data[1]
        indicators = self.stratygies.get(strategy_type)
        if indicators:
            print(indicators)
    
    def create_sub_chart(self,name:IndicatorType):
        panel = SubChart(self.chart,self,name,self.mainwindow)
        #panel.setup_indicator((name,self.mainwindow))
        self.add_sub_panel(panel)
        QApplication.processEvents()
    
    def create_sub_indicator(self,name:IndicatorType):
        panel = ViewSubPanel(self.chart,self)
        indicator = panel.setup_indicator((name,self.mainwindow))
        if indicator:
            self.chart.indicators.append(indicator) 
        self.add_sub_panel(panel)
        QApplication.processEvents()

    def create_basic_indicator(self,name:IndicatorType):
        self.chart.setup_indicator((name,self.mainwindow))
        QApplication.processEvents()
    
    def create_candle_indicator(self,name:IndicatorType):
        self.chart.setup_indicator((name,self.mainwindow))
        QApplication.processEvents()
        
    def create_advand_indicator(self,name:IndicatorType):
        self.chart.setup_indicator((name,self.mainwindow))
        QApplication.processEvents()

    def create_normal_indicator(self,name:IndicatorType):
        QApplication.processEvents()

    def setup_chart(self,mainwindow,current_ex:str="",current_symbol:str="",curent_interval:str=""):
        self.mainwindow:MainWidget = mainwindow
        self.chart = Chart(parent=self,exchange_name=current_ex,symbol=current_symbol,interval=curent_interval)
        Signal_Proxy(
            signal=self.sig_show_hide_cross,
            slot=self.mouse_move,connect_type=Qt.ConnectionType.AutoConnection
        )

        self.addWidget(self.chart)  # add first chart to list
        self.listwidgets.append(self.chart)
        self.list_proxy = []
        
        self.dateAxis = CustomDateAxisItem(orientation='bottom',context=self.chart,vb=self.chart.vb,
                                           showValues=True, axisPen="#5b626f", textPen="#5b626f",
                                            **{Axis.TICK_FORMAT: Axis.DATETIME})
        
        self.dateAxis.setHeight(25)
        self.xaxisview = GraphicsView(self,background="#161616")
        self.xaxisview.setFixedHeight(25)
        self.xaxisview.setContentsMargins(0,0,0,0)
        self.xaxislayout = GraphicsLayout()
        self.xaxisview.setCentralItem(self.xaxislayout)
        self.xaxislayout.setContentsMargins(0,0,70,0)
        self.xaxislayout.addItem(self.dateAxis, row=0, col=0)
        self.addItem(self.xaxisview)
        self.dateAxis.linkToView(self.chart.vb)
        
        Signal_Proxy(
            self.chart.crosshair_x_value_change,
            slot=self.dateAxis.change_value,connect_type=Qt.ConnectionType.AutoConnection
        )
        
        self.mouse_clicked_signal.connect(self.chart.mouse_clicked_signal)
    
    def show_hide_playbar(self):
        btn = self.sender()
        if btn.isChecked():
            self.replay_bar = Playbar(self.mainwindow)
            
            self.replay_bar.set_enable_selectbar()

            
            self.replay_bar.btn_close.clicked.connect(self.remove_replay_bar)
            self.replay_bar.play.clicked.connect(self.chart.worker_replay_loop_start)
            self.replay_bar.forward.clicked.connect(self.chart.replay_forward_update)
            
            
            self.frame.setMaximumSize(QSize(16777215, 60))
            self.frame.setContentsMargins(0,0,0,0)
            self.addItem(self.replay_bar)
            self.replay_bar.show()
        else:
            self.frame.setContentsMargins(0,0,0,0)
            self.frame.setMaximumSize(QSize(16777215, 25))
            self.removeItem(self.replay_bar)
    
    def remove_replay_bar(self):
        btn = self.sender()
        self.frame.setContentsMargins(0,0,0,0)
        self.frame.setMaximumSize(QSize(16777215, 25))
        self.removeItem(self.replay_bar)
        self.mainwindow.topbar.replay.setChecked(False)
        self.mainwindow.topbar.replay.set_icon_color()
    
    def add_sub_panel(self,panel:ViewSubPanel|SubChart):
        self.listwidgets.append(panel)
        self.addWidget(panel)
        panel.setVisible(True)
        panel.sig_delete_sub_panel.connect(self.delete_panel)
        self.mouse_clicked_signal.connect(panel.mouse_clicked_signal)

    def delete_panel(self,panel:ViewSubPanel|SubChart):
        self.listwidgets.remove(panel)
        if isinstance(panel,SubChart):
            asyncio.run(panel.close())
        panel.deleteLater()
    
    def mouse_move(self,data):
        [panel.show_hide_cross(data) for panel in self.listwidgets]
            
    def show_sub_panel(self,is_show:bool=True):
        if not self.is_started:
            self.is_started = True
    def mousePressEvent(self, ev):
        self.mouse_clicked_signal.emit(ev)
        super().mousePressEvent(ev)
