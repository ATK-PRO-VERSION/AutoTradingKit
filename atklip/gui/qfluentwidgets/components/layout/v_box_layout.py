# coding:utf-8
from typing import List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QFrame, QVBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QToolButton, QWidget)
from atklip.gui.qfluentwidgets.components.widgets import *

class VBoxLayout(QVBoxLayout):
    """ Vertical box layout """

    def __init__(self, parent):
        super().__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setSpacing(0)
        self.widgets = []

    def addSeparator(self,_type:str="HORIZONTAL",w: int = 30,h: int = 10):
        if _type == "HORIZONTAL":
            Separator = HorizontalSeparator(self.parent(),w,h)
        else:
            Separator = VerticalSeparator(self.parent(),w,h)
        self.addWidget(Separator)

    def addSpacer(self,_type:str="HORIZONTAL"):
        if _type == "HORIZONTAL":
            spacer = QSpacerItem(380, 20, QSizePolicy.Expanding, QSizePolicy.Preferred)
        else:
            spacer = QSpacerItem(20, 380, QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.addItem(spacer)  
    def addWidgets(self, widgets: List[QWidget], stretch=0, alignment=Qt.AlignTop):
        """ add widgets to layout """
        for widget in widgets:
            self.addWidget(widget, stretch, alignment)

    def addWidget(self, widget: QWidget, stretch=0, alignment=Qt.AlignTop):
        """ add widget to layout """
        super().addWidget(widget, stretch, alignment)
        self.widgets.append(widget)
        widget.show()
    
    def get_widgets(self)->List[QWidget]:
        """ get all widgets """
        return self.widgets

    def removeWidget(self, widget: QWidget):
        """ remove widget from layout but not delete it """
        self.widgets.remove(widget)
        super().removeWidget(widget)
        

    def deleteWidget(self, widget: QWidget):
        """ remove widget from layout and delete it """
        self.removeWidget(widget)
        widget.hide()
        widget.deleteLater()

    def removeAllWidget(self):
        """ remove all widgets from layout """
        for widget in self.widgets:
            super().removeWidget(widget)

        self.widgets.clear()
