
from typing import TYPE_CHECKING
from .mainwidget_ui import Ui_MainWidget
from atklip.gui.components import CircularProgress,LoadingProgress
from atklip.gui.qfluentwidgets.common import FluentStyleSheet
from PySide6.QtWidgets import QFrame,QWidget
from PySide6.QtCore import QPropertyAnimation,QEasingCurve, Signal, Qt,QEvent,QTime
from atklip.gui.qfluentwidgets.common.icon import *
from atklip.appmanager.setting import AppConfig
# from atklip.gui.components.possition_table import PositionTable
from atklip.gui.bottom_widget.tab_interface import BottomInterface

if TYPE_CHECKING:
    from .fluentwindow import WindowBase

class MainWidget(QWidget,Ui_MainWidget):
    mouse_clicked_signal = Signal(QEvent)
    def __init__(self, parent,tabItem,name,current_ex,current_symbol,curent_interval):
        super().__init__(parent)
        self._parent:WindowBase = parent
        self.setObjectName(name)
        self.setupUi(self)
     
        self.maxExtend = 250

        self.tabItem = tabItem
        
        self.chartbox_splitter.setup_chart(self,current_ex,current_symbol,curent_interval)
        
        self.rightbar.hide()
        
        self.rightbar.object.splitToolButton.clicked.connect(lambda :self.extend_right_menu(self.rightview))

        self.chartbox_splitter.chart.sig_change_tab_infor.connect(self.change_tab_infor,Qt.ConnectionType.AutoConnection)
        self.chartbox_splitter.chart.mouse_clicked_on_chart.connect(self.mouse_clicked_signal)
        "signal from drawbar"
        self.drawbar.sig_draw_object_name.connect(self.draw_tool)
        self.drawbar.sig_delete_all.connect(self.chartbox_splitter.chart.delete_all_draw_obj)

        self.chartbox_splitter.chart.sig_reset_drawbar_favorite_btn.connect(self.drawbar.reset_drawbar)
        
        self.chartbox_splitter.chart.sig_reload_indicator_panel.connect(self.show_favorite_draw_btn)
        
        self.tool_name:str = None
        
        "signal from TopBar--------start"
        self.topbar.sig_change_symbol.connect(self.chartbox_splitter.chart.on_reset_exchange,Qt.ConnectionType.AutoConnection)
        self.topbar.sig_change_inteval.connect(self.chartbox_splitter.chart.on_change_inteval,Qt.ConnectionType.AutoConnection)
        self.topbar.sig_goto_date.connect(self.chartbox_splitter.chart.sig_goto_date,Qt.ConnectionType.AutoConnection)
        self.topbar.gotonow.clicked.connect(self.chartbox_splitter.chart.roll_till_now)
        self.topbar.sig_add_indicator_to_chart.connect(self.chartbox_splitter.create_indicator,Qt.ConnectionType.AutoConnection)
        "signal from TopBar-------end"
        
        self.topbar.replay.clicked.connect(self.chartbox_splitter.chart.set_replay_mode)
        self.topbar.replay.clicked.connect(self.chartbox_splitter.show_hide_playbar)
        

        self.progress = LoadingProgress(self,size=40)
        self.chartbox_splitter.chart.sig_show_process.connect(self.progress.run_process,Qt.ConnectionType.AutoConnection)
        self.progress.run_process(False)
        
        self.topbar.mode.clicked.connect(self.chartbox_splitter.chart.change_mode)
        
        "khởi tạo indicator menu, symbol menu trước. đang test"
        # self.topbar.setup_indicator_menu()
        # self.topbar.setup_symbol_menu()
        
        self.TabInterface = BottomInterface(self)
        
        # self.layout_bottom.setContentsMargins(0,0,0,0)
        self.layout_bottom.addWidget(self.TabInterface) #,0,alignment=Qt.AlignmentFlag.AlignVCenter
        # self.TabInterface.setFixedHeight(60)
        self.splitter.setSizes([800,0])
        
        self.press_time = None
        self.release_time = None
        
    def show_favorite_draw_btn(self):
        "Drawbar ---------start"
        "show favorite draw tools on chart when start"
        favorite_draw_btn = AppConfig.get_config_value(f"drawbar.favorite_draw_btn")
        if favorite_draw_btn == None:
            AppConfig.sig_set_single_data.emit((f"drawbar.favorite_draw_btn",False))
            favorite_draw_btn = AppConfig.get_config_value(f"drawbar.favorite_draw_btn")
        if favorite_draw_btn:
            self.drawbar.FAVORITE.splitToolButton.setChecked(True)
            self.drawbar.FAVORITE.splitToolButton.change_status_favorite_btn()
            self.drawbar.FAVORITE.add_remove_favorite_wg()
        "Drawbar ---------end"
    
    def draw_tool(self,tool_infor):
        current_tool,is_enabled,self.tool_name = tool_infor[0],tool_infor[1],tool_infor[2]# "draw_trenlines"
        print(current_tool,is_enabled,self.tool_name)
        self.chartbox_splitter.chart.drawtool.draw_object_name = self.tool_name
    
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

    def mousePressEvent(self, ev:QEvent):
        if Qt.MouseButton.LeftButton:
            self.press_time = QTime.currentTime()
            super().mousePressEvent(ev)
    
    def mouseReleaseEvent(self, ev:QEvent):
        self.is_mouse_pressed = False
        self.release_time = QTime.currentTime() 
        if self.press_time:
            elapsed_time = self.press_time.msecsTo(self.release_time)
            if elapsed_time < 200:
                self.mouse_clicked_signal.emit(ev)
        super().mouseReleaseEvent(ev)