from typing import TYPE_CHECKING
from PySide6.QtCore import Signal,QSize
from PySide6.QtWidgets import QFrame,QSizePolicy

from atklip.gui.qfluentwidgets.common import FluentIcon as FIF
from atklip.gui.qfluentwidgets.components import VerticalSeparator

from atklip.gui.components._pushbutton import _PushButton

from .playbar_ui import  Ui_Frame as PlaybarFrame
from .select_bar import SelectBar
from .replay_speed import ReplaySpeed
from .btn_play import PlayButton

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.gui.views.mainlayout import MainWidget
    from atklip.graphics.chart_component.viewchart import Chart
    
class Playbar(QFrame,PlaybarFrame):
    sig_change_symbol = Signal(tuple)
    sig_change_inteval = Signal(tuple)
    sig_goto_date = Signal(tuple)
    sig_add_indicator_to_chart = Signal(tuple)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent:MainWidget = parent
        self.chart: Chart = self._parent.chartbox_splitter.chart
        
        self.btn_replay = self._parent.topbar.replay
        
        self.setupUi(self)
        self.setFixedHeight(40)
        self.select_bar = SelectBar(self)
        self.play = PlayButton(self)
        self.forward = _PushButton(FIF.FORWARD,self) 
        self.forward.setIconSize(QSize(28,28))
        self.ReplaySpeed = ReplaySpeed(self)
        # self.gotonow = _PushButton(FIF.JUMP_TO_NOW,self) 
        # self.gotonow.setIconSize(QSize(27,27))
        
        self.center_layout.addWidget(self.select_bar)
        self.center_layout.addWidget(VerticalSeparator(self))
        
        self.center_layout.addWidget(self.play)
        self.center_layout.addWidget(self.ReplaySpeed)
        self.center_layout.addWidget(self.forward)
        
        # self.center_layout.addWidget(VerticalSeparator(self))
        
        # self.center_layout.addWidget(self.gotonow)

        self.btn_close = _PushButton(FIF.CLOSE,self)
        self.btn_close.setIconSize(QSize(16,16))
        self.btn_close.setObjectName("btn_close_playbar")
        self.right_layout.addWidget(self.btn_close)
        
        self.setContentsMargins(0,0,0,0)
        
        self.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        
        "connect signal slot"
        self.select_bar.clicked.connect(self.chart.set_replay_mode)        
        self.select_bar.clicked.connect(self.ena_btn_select_bar)        
        self.play.clicked.connect(self.dis_from_play_btn)        
        self.btn_close.clicked.connect(self.chart.set_replay_mode)        
        self.chart.mouse_clicked_on_chart.connect(self.dis_btn_select_bar)
        self.ReplaySpeed.currentTextChanged.connect(self.chart.set_replay_speed)
        
        
    def dis_btn_select_bar(self):
        self.select_bar.setChecked(False)
        self.select_bar.set_icon_color()
        self.play.setEnabled(True)
        self.play.set_icon_color()
        self.forward.setEnabled(True)
    
    def ena_btn_select_bar(self):
        btn = self.sender()
        if btn.isChecked():
            self.play.setEnabled(False)
            self.play.setChecked(False)
            self.play.set_icon_color()
            self.forward.setEnabled(False)
        else:
            self.play.setEnabled(True)
            self.forward.setEnabled(True)

    def set_enable_selectbar(self):
        self.select_bar.setEnabled(True)
        self.select_bar.setChecked(True)
        self.select_bar.set_icon_color()
        self.play.setEnabled(False)
        self.play.setChecked(False)
        # self.play.set_icon_color()
        self.forward.setEnabled(False)

    def dis_from_play_btn(self):
        btn = self.sender()
        if btn.isChecked():
            self.select_bar.setEnabled(False)
            self.select_bar.setChecked(False)
            self.select_bar.set_icon_color()
            self.forward.setEnabled(False)
        else:
            self.select_bar.setEnabled(True)
            self.forward.setEnabled(True)
