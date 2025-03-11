
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.components import Tradingview_Button
from atklip.gui import FluentIcon as FIF
# from atklip.gui.draw_bar import *
from atklip.gui.qfluentwidgets.common import *

class RECIRCLEBIN(QFrame):
    def __init__(self,parent:QWidget=None,sig_delete_all=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent = parent
        self.sig_delete_all = sig_delete_all
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(50,40)
        self._QLayout = QHBoxLayout(self)
        self._QLayout.setSpacing(0)
        self._QLayout.setContentsMargins(0, 0, 0, 0)
        self._QLayout.setAlignment(Qt.AlignLeft)
        self.splitToolButton = Tradingview_Button(FIF.CYCLEBIN,self.parent)
        self.splitToolButton.clicked.connect(self.sig_delete_all)

        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
    
    def set_current_tool(self,tool_infor):
        tool,icon = tool_infor[0],tool_infor[1]
        self.current_tool = tool
        self.splitToolButton.change_item(icon)
        self.set_enable()
        
    def set_enable(self):
        if self.splitToolButton.button.isChecked():
            self.is_enabled = True
        else:
            self.is_enabled = False
    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)
