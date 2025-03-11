# coding:utf-8
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout
from atklip.gui.qfluentwidgets import (Pivot)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from atklip.gui.qfluentwidgets.common import *
# from .scroll_interface import ScrollInterface


class PivotInterface(QWidget):
    """ Pivot interface """

    Nav = Pivot
    sig_change_widget = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.setFixedSize(300, 140)
        self.pivot = self.Nav(self)
        self.pivot.setFixedHeight(40)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.stackedWidget.setContentsMargins(0,0,0,0)
        
        # FluentStyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        
    def addSubInterface(self, widget, objectName, text):
        widget.setObjectName(objectName)
        # widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stackedWidget.addWidget(widget)
        self.stackedWidget.setFixedHeight(widget.height())
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )
        _height_widget = widget.height() + self.pivot.height()
        self.setFixedHeight(_height_widget)

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        # _height_widget = self.stackedWidget.height() + self.pivot.height()
        self.stackedWidget.setFixedHeight(widget.height())
        _height_widget = widget.height() + self.pivot.height()
        self.sig_change_widget.emit(_height_widget)
        self.setFixedHeight(_height_widget)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

