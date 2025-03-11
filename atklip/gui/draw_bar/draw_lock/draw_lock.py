
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.components import Lock_Unlock_Button,Tradingview_Button
from atklip.gui import FluentIcon as FIF
# from atklip.gui.draw_bar import *
from atklip.gui.qfluentwidgets.common import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainlayout import MainWidget
    from atklip.graphics.chart_component.viewchart import Chart
class LOCK(QFrame):
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
        self.splitToolButton = Lock_Unlock_Button(FIF.UNLOCK,self.parent)
        # self.splitToolButton = Tradingview_Button(FIF.UNLOCK,self.parent)
        self.splitToolButton.clicked.connect(self.lock_unlock_all_tools)
        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()

    def lock_unlock_all_tools(self):
        is_checked = self.splitToolButton.isChecked()
        all_tools =  self.parent.chartbox_splitter.chart.drawtools
        if all_tools:
            for tool in all_tools:
                if is_checked:
                    tool.locked_handle()
                else:
                    tool.unlocked_handle()
        
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
