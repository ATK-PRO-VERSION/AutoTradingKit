
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.components import Tradingview_Button
from atklip.gui import FluentIcon as FIF
# from atklip.gui.draw_bar import *
from atklip.gui.qfluentwidgets.common import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainlayout import MainWidget
    from atklip.graphics.chart_component.viewchart import Chart
class MAGNET(QFrame):
    def __init__(self,parent:QWidget=None,sig_draw_object_name=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent:MainWidget = parent
        self.sig_draw_object_name = sig_draw_object_name
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(50,40)
        self._QLayout = QHBoxLayout(self)
        self._QLayout.setSpacing(0)
        self._QLayout.setContentsMargins(0, 0, 0, 0)
        self._QLayout.setAlignment(Qt.AlignLeft)
        self.splitToolButton = Tradingview_Button(FIF.MAGNET,self)
        self.splitToolButton.clicked.connect(self.magnet_unmagnet)
        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
    
    def magnet_unmagnet(self):
        if self.splitToolButton.isChecked():
            self.parent.chartbox_splitter.chart.magnet_on = True
        else:
            self.parent.chartbox_splitter.chart.magnet_on = False
    
    def set_current_tool(self,tool_infor):
        tool,icon = tool_infor[0],tool_infor[1]
        self.current_tool = tool
        self.splitToolButton.change_item(icon)
        self.set_enable()
        self.sig_draw_object_name.emit((self.current_tool,self.is_enabled,"draw_trenlines"))
    def set_enable(self):
        if self.splitToolButton.button.isChecked():
            self.is_enabled = True
        else:
            self.is_enabled = False
    
    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)
