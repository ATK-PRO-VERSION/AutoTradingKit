from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction,QIcon,QFont
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout,QFrame,QHBoxLayout
from atklip.gui.components._pushbutton import Tradingview_Button
from atklip.gui import FluentIcon as FIF

class WATCHLISTS(QFrame):
    def __init__(self,parent:QWidget=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent = parent
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(50,40)
        self._QLayout = QHBoxLayout(self)
        self._QLayout.setSpacing(0)
        self._QLayout.setContentsMargins(0, 0, 0, 0)
        self._QLayout.setAlignment(Qt.AlignRight)

        self.splitToolButton = Tradingview_Button(FIF.WATCHLIST,self)

        self.splitToolButton.setIconSize(QSize(40,40))

        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)
