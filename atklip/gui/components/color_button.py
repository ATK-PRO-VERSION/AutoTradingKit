from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtGui import QIcon, QPainter, QColor
from PySide6.QtWidgets import QPushButton, QWidget
from atklip.gui.qfluentwidgets.common import *


class ColorButton(QPushButton):
    sig_change_color = Signal(int)
    sig_color_out = Signal(str)
    def __init__(self,parent:QWidget):
        super().__init__(parent=parent)
        self.setFixedSize(25,25)
        self._color = ()
        self._hex_color = ''
        self.sig_change_color.connect(self.change_alpha)
        self.clicked.connect(self.emit_change_color)
    def title(self):
        return self.text()
    def emit_change_color(self):
        self.sig_color_out.emit(f"#{self._hex_color}")
    def change_alpha(self,alpha):
        if self._color == ():
            return 
        self._color = (self._color[0],self._color[1],self._color[2],alpha)
        self._hex_color = rgb2hex(self._color)
        self.set_stylesheet(self._hex_color)
        self.update()
    def set_stylesheet(self,color):
        self._color = color
        self._hex_color = rgb2hex(color)
        self.setStyleSheet(f"""QPushButton {{
                            background-color: #{self._hex_color};
                            border: none;
                            border-radius: 5px;
                            }}""")
    def enterEvent(self, event):
        self.setStyleSheet(f"""QPushButton {{
            background-color: #{self._hex_color};
            border: 3px solid #b8bbc2;
            border-radius: 5px;
            }}""")
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.setStyleSheet(f"""QPushButton {{
                            background-color: #{self._hex_color};
                            border: none;
                            border-radius: 5px;
                            }}""")
        super().leaveEvent(event)