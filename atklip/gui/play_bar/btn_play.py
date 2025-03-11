from typing import TYPE_CHECKING
from PySide6.QtCore import QSize,Signal
from PySide6.QtWidgets import QWidget
from atklip.gui.qfluentwidgets.common import FluentIcon as FIF
from atklip.gui.components._pushbutton import IconTextChangeButton


if TYPE_CHECKING:
    from views.mainlayout import MainWidget


class PlayButton(IconTextChangeButton):
    # clicked = Signal()
    sig_remove_menu = Signal()
    def __init__(self,parent:QWidget=None):
        super().__init__(FIF.PLAY,parent=parent)
        self._parent:MainWidget = parent
        self.setFixedSize(30,30)
        self.setIconSize(QSize(15,15))
        self._menu = None


    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)
