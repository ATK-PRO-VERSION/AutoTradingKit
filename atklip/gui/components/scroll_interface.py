# coding:utf-8
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QSizePolicy, QSpacerItem

from atklip.gui.qfluentwidgets.components import SmoothScrollArea,VBoxLayout,HorizontalSeparator,VerticalSeparator
from atklip.gui.qfluentwidgets.common import *


class ScrollInterface(SmoothScrollArea):
    """ Gallery interface """

    def __init__(self, parent=None):
        """
        Parameters
        ----------
        parent: QWidget
            parent widget
        """
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.vBoxLayout = VBoxLayout(self.view)
        self.view.setLayout(self.vBoxLayout)

        self._parent = self.parent()
        self.isAdded = False

        self.old_vertival_val = None

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setSpacing(1)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.view.setObjectName('view')
        self.setWidget(self.view)
        # self.installEventFilter(self)
        FluentStyleSheet.SCROLLINTERFACE.apply(self)
    
    def setSpacing(self,value):
        self.vBoxLayout.setSpacing(value)
    def setContentsMargins(self,l,t,r,b):
        self.vBoxLayout.setContentsMargins(l,t,r,b)
    def addSeparator(self,_type:str="HORIZONTAL",w: int = 30,h: int = 10):
        if _type == "HORIZONTAL":
            Separator = HorizontalSeparator(self.parent(),w,h)
        else:
            Separator = VerticalSeparator(self.parent(),w,h)
        self.addWidget(Separator)

    def addSpacer(self,_type:str="HORIZONTAL"):
        if _type == "HORIZONTAL":
            spacer = QSpacerItem(380, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        else:
            spacer = QSpacerItem(20, 380, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vBoxLayout.addItem(spacer)  
    def addWidget(self, widget:QWidget, stretch=0, alignment=Qt.AlignmentFlag.AlignTop):
        self.vBoxLayout.addWidget(widget, stretch=stretch, alignment=alignment)
        return widget
    
    def insertWidget(self,index, widget:QWidget, stretch=0, alignment=Qt.AlignmentFlag.AlignTop):
        self.vBoxLayout.insertWidget(index,widget, stretch=stretch, alignment=alignment)
        return widget
    
    def removeWidget(self, widget:QWidget):
        self.vBoxLayout.removeWidget(widget)
        widget.deleteLater()

    def scrollToCard(self, index: int):
        """ scroll to example card """
        w = self.vBoxLayout.itemAt(index).widget()
        self.verticalScrollBar().setValue(w.y())
        
    def resizeEvent(self, e):
        super().resizeEvent(e)
    
    # def eventFilter(self, obj, e: QEvent):
        
    #     if e.type() == QEvent.Wheel:
    #         print(self.delegate.vScrollBar.val)
    #         _widgets = self.vBoxLayout.get_widgets()

    #         print(len(_widgets), _widgets[-1].y())
    #         print(self.verticalScrollBar().value())

    #         if e.angleDelta().y() != 0:
    #             self.delegate.vScrollBar.scrollValue(-e.angleDelta().y())
    #         else:
    #             self.delegate.hScrollBar.scrollValue(-e.angleDelta().x())

    #         if self.old_vertival_val == None:
    #             self.old_vertival_val = self.verticalScrollBar().value()
    #         elif self.old_vertival_val < self.verticalScrollBar().value():
    #             self.old_vertival_val = self.verticalScrollBar().value()
    #         elif self.old_vertival_val > self.verticalScrollBar().value():
    #             self.old_vertival_val = self.verticalScrollBar().value()
    #         elif self.old_vertival_val == self.verticalScrollBar().value() and self.verticalScrollBar().value() != 0:
    #             self.old_vertival_val = self.verticalScrollBar().value()
    #             n = len(_widgets)
    #             print(n)
    #             #self._parent.update_symbol(n)

    #         e.setAccepted(True)
    #         return True

    #     return super().eventFilter(obj, e)
    