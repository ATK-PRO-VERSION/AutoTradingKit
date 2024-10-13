
from typing import TYPE_CHECKING
from .mainwidget_ui import Ui_MainWidget
from atklip.gui.components import CircularProgress,LoadingProgress
from atklip.gui.qfluentwidgets.common import FluentStyleSheet
from PySide6.QtWidgets import QFrame,QWidget
from PySide6.QtCore import QPropertyAnimation,QEasingCurve, Signal, Qt
from atklip.gui.qfluentwidgets.common.icon import *


if TYPE_CHECKING:
    from .fluentwindow import WindowBase

class MainWidget(QWidget,Ui_MainWidget):
    def __init__(self, parent,tabItem,name,current_ex,current_symbol,curent_interval):
        super().__init__(parent)
        self.setObjectName(name)
        self.setupUi(self)
        self.maxExtend = 250

        self._parent:WindowBase = parent

        self.tabItem = tabItem
        
        self.chartbox_splitter.setup_chart(self,current_ex,current_symbol,curent_interval)
        
        self.rightbar.object.splitToolButton.clicked.connect(lambda :self.extend_right_menu(self.rightview))

        self.chartbox_splitter.chart.sig_change_tab_infor.connect(self.change_tab_infor,Qt.ConnectionType.AutoConnection)

        "signal from drawbar"
        self.drawbar.sig_draw_object_name.connect(self.draw_tool)
        
        
        "signal from TopBar"
        self.topbar.sig_change_symbol.connect(self.chartbox_splitter.chart.on_reset_exchange,Qt.ConnectionType.AutoConnection)
        self.topbar.sig_change_inteval.connect(self.chartbox_splitter.chart.on_change_inteval,Qt.ConnectionType.AutoConnection)
        self.topbar.sig_goto_date.connect(self.chartbox_splitter.chart.sig_goto_date,Qt.ConnectionType.AutoConnection)
        
        self.topbar.sig_add_indicator_to_chart.connect(self.chartbox_splitter.sig_add_indicator_to_chart,Qt.ConnectionType.AutoConnection)
        self.topbar.sig_change_market_type.connect(self.chartbox_splitter.chart.sig_change_market_type,Qt.ConnectionType.AutoConnection)
        "signal from TopBar"
        self.progress = LoadingProgress(self)
        self.chartbox_splitter.chart.sig_show_process.connect(self.progress.run_process,Qt.ConnectionType.AutoConnection)
        # self.progress.run_process(True)
        
        self.topbar.mode.clicked.connect(self.chartbox_splitter.chart.change_mode)
        
        "khởi tạo indicator menu, symbol menu trước. đang test"
        self.topbar.setup_indicator_menu()
        self.topbar.setup_symbol_menu()
        FluentStyleSheet.SPLITTER.apply(self.chartbox_splitter)
    
    def draw_tool(self,tool_infor):
        current_tool,is_enabled,tool_name = tool_infor[0],tool_infor[1],tool_infor[2]# "draw_trenlines"
        print(current_tool,is_enabled,tool_name)
        self.chartbox_splitter.chart.drawtool.draw_object_name = tool_name
    
    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.progress.isVisible():
            self.progress.run_process(True)

    def change_tab_infor(self,data):
        symbol = data[0]
        interval = data[1]
        symbol_icon = get_symbol_icon(symbol)
        symbol_icon_path = CryptoIcon.crypto_url(symbol_icon)
        text = f"{symbol} {interval}"
        self.tabItem.setIcon(symbol_icon_path)
        self.tabItem.setText(text)

        #self.maxExtend = width
    def extend_right_menu(self, target_object:QFrame):
        width = target_object.width()
        self.maxExtend = 250
        print(width)
        # SET MAX WIDTH
        if width < self.maxExtend:
            box_width = width
            widthExtended = self.maxExtend

        else:
            widthExtended = 0
            box_width = self.maxExtend

        self.box = QPropertyAnimation(target_object, b"minimumWidth")
        self.box.setDuration(10)
        self.box.setStartValue(box_width)
        self.box.setEndValue(widthExtended)
        self.box.setEasingCurve(QEasingCurve.Linear)
        self.box.start()
