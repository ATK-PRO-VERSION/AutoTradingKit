# coding:utf-8
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget

from ...common.style_sheet import isDarkTheme


class HorizontalSeparator(QWidget):
    """ Horizontal separator """

    def __init__(self, parent=None,w=30,h=10):
        super().__init__(parent=parent)
        self.setSize(w,h)
    def setSize(self,w=30,h=10):
        self.setFixedWidth(w)
        self.setFixedHeight(h)
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        if isDarkTheme():
            painter.setPen(QColor(255,255,255,50))
        else:
            painter.setPen("#e0e3eb")

        painter.drawLine(0, 1, self.width(), 1)


class VerticalSeparator(QWidget):
    """ Vertical separator """

    def __init__(self, parent=None,w=10,h=30):
        super().__init__(parent=parent)
        self.setSize(w,h)

    def setSize(self,w=10,h=30):
        self.setFixedWidth(w)
        self.setFixedHeight(h)
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        if isDarkTheme():
            painter.setPen(QColor(255,255,255,50))
        else:
            painter.setPen("#e0e3eb")

        painter.drawLine(1, 0, 1, self.height())