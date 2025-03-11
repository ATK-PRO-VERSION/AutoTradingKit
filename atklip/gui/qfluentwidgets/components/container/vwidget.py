from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QWidget, QLayout
from typing import List
from atklip.gui.qfluentwidgets.components.layout.v_box_layout import VBoxLayout
from atklip.gui.qfluentwidgets.common import *

class VWIDGET(QFrame):
    def __init__(self, parent=None,name:str=""):
        super().__init__(parent=parent)
        self.Layout = VBoxLayout(self)
        self.setObjectName(name)
        self.setLayout(self.Layout)
        FluentStyleSheet.VWIDGET.apply(self)
    def setSpacing(self,spacing:int):
        self.Layout.setSpacing(spacing)

    def setContentsMargins(self,left: int,top: int,right: int,bottom: int):
        self.Layout.setContentsMargins(left,top,right,bottom)
    def addSeparator(self,_type:str="VERTICAL",w: int = 30,h: int = 10):
        self.Layout.addSeparator(_type, w, h)

    def addSpacer(self,_type:str="VERTICAL"):
        self.Layout.addSpacer(_type)
    def addWidget(self, widget: QWidget, stretch=0, alignment=Qt.AlignmentFlag.AlignVCenter):
        self.Layout.addWidget(widget, stretch, alignment)
    def addLayout(self, layout: QLayout, stretch=0, alignment=Qt.AlignTop):
        self.Layout.addLayout(layout, stretch)
    def addWidgets(self, widgets: List[QWidget], stretch=0, alignment=Qt.AlignTop):
        """ add widgets to layout """
        self.Layout.addWidgets(widgets,stretch,alignment)

    def removeWidget(self, widget: QWidget):
        """ remove widget from layout but not delete it """
        self.Layout.removeWidget(widget)

    def deleteWidget(self, widget: QWidget):
        """ remove widget from layout and delete it """
        self.removeWidget(widget)
        #widget.hide()
        widget.deleteLater()

    def removeAllWidget(self):
        """ remove all widgets from layout """
        for widget in self.widgets:
            self.removeWidget(widget)
        self.Layout.widgets.clear()