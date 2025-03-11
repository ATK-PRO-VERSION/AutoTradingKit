
from typing import Union
from PySide6.QtCore import Qt, Signal, Property, QRectF, QSize, QPoint, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QColor, QIcon, QPainterPath, QLinearGradient, QPen, QBrush, QMouseEvent
from PySide6.QtWidgets import (QWidget, QGraphicsDropShadowEffect, QHBoxLayout, QSizePolicy, 
                               QApplication,QHBoxLayout, QWidget, QSpacerItem,QSizePolicy,QApplication)

from atklip.gui import (TabBar, isDarkTheme)
from atklip.gui import FluentIcon as FIF
from atklip.gui.components._pushbutton import IconTextChangeButton
from atklip.gui.qfluentwidgets.common.icon import FluentIconBase
from atklip.gui.qfluentwidgets.common.style_sheet import FluentStyleSheet
from atklip.gui.qfluentwidgets.components.widgets.tab_view import TabItem

class tab_TabItem(TabItem):
    def _drawText(self, painter: QPainter):        
        tw = self.fontMetrics().boundingRect(self.text()).width()

        if self.icon().isNull():
            dw = 47 if self.closeButton.isVisible() else 20
            rect = QRectF(10, 0, self.width() - dw, self.height())
        else:
            dw = 70 if self.closeButton.isVisible() else 45
            rect = QRectF(33, 0, self.width() - dw, self.height())

        pen = QPen()
        color = Qt.white if isDarkTheme() else Qt.black
        color = self.textColor or color
        rw = rect.width()

        if tw > rw:
            gradient = QLinearGradient(rect.x(), 0, tw+rect.x(), 0)
            gradient.setColorAt(0, color)
            gradient.setColorAt(max(0, (rw - 10) / tw), color)
            gradient.setColorAt(max(0, rw / tw), Qt.transparent)
            gradient.setColorAt(1, Qt.transparent)
            pen.setBrush(QBrush(gradient))
        else:
            pen.setColor(color)

        painter.setPen(pen)
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, self.text())
    


class TitleBar(QWidget):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add buttons
        self.setStyleSheet("""
                           QWidget {
                                background-color: transparent;
                            }""")
        self._parent = self.parent()
        self.setFixedHeight(45)
        self.toolButtonLayout = QHBoxLayout()
        self.toolButtonLayout.setContentsMargins(5, 0, 5, 5)
        self.toolButtonLayout.setSpacing(2)
        self.setLayout(self.toolButtonLayout)
        
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)

        self.minbtn = IconTextChangeButton(FIF.MINDOWN, parent=self)
        self.maxbtn = IconTextChangeButton(FIF.MAXIMUM, parent=self)
        self.minbtn.setFixedSize(30,30)
        self.minbtn.setIconSize(QSize(25,25))
        self.maxbtn.setFixedSize(30,30)
        self.maxbtn.setIconSize(QSize(25,25))
        # add tab bar
        self.tabBar = TabBar(self)
        self.tabBar.__initWidget = self.__initWidget
        self.tabBar.insertTab = self.insertTab
        
        
        self.tabBar.setMovable(False)
        self.tabBar.setTabMaximumWidth(120)
        self.tabBar.setTabShadowEnabled(True)
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))
        self.tabBar.setScrollable(False)

        self.toolButtonLayout.addWidget(self.tabBar,0,Qt.AlignmentFlag.AlignLeft)
        item = QSpacerItem(380, 1, QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolButtonLayout.addSpacerItem(item)
        self.toolButtonLayout.addWidget(self.minbtn,0,Qt.AlignmentFlag.AlignRight)
        self.toolButtonLayout.addWidget(self.maxbtn,0,Qt.AlignmentFlag.AlignRight)
        
    def __initWidget(self):
        self.tabBar.setFixedHeight(40)
        self.tabBar.setWidget(self.view)
        self.tabBar.setWidgetResizable(True)
        self.tabBar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabBar.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # self.hBoxLayout.setSizeConstraint(QHBoxLayout.SetMaximumSize)

        self.tabBar.addButton.clicked.connect(self.tabAddRequested)

        self.tabBar.view.setObjectName('view')
        FluentStyleSheet.TAB_VIEW.apply(self.tabBar)
        FluentStyleSheet.TAB_VIEW.apply(self.tabBar.view)

        self.__initLayout()
    
    def __initLayout(self):
        self.tabBar.hBoxLayout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.tabBar.itemLayout.setAlignment(Qt.AlignVCenter)
        self.tabBar.widgetLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.tabBar.itemLayout.setContentsMargins(0, 0, 0, 0)
        self.tabBar.widgetLayout.setContentsMargins(0, 0, 0, 0)
        self.tabBar.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.tabBar.itemLayout.setSizeConstraint(QHBoxLayout.SetMinAndMaxSize)

        self.tabBar.hBoxLayout.setSpacing(0)
        self.tabBar.itemLayout.setSpacing(0)

        self.tabBar.hBoxLayout.addLayout(self.tabBar.itemLayout)
        self.tabBar.hBoxLayout.addSpacing(3)

        self.tabBar.widgetLayout.addWidget(self.tabBar.addButton, 0, Qt.AlignLeft)
        self.tabBar.hBoxLayout.addLayout(self.tabBar.widgetLayout)
        # self.tabBar.hBoxLayout.addStretch(1)
    def insertTab(self, index: int, routeKey: str, text: str, icon: Union[QIcon, str, FluentIconBase] = None,
                  onClick=None):
        """ insert tab

        Parameters
        ----------
        index: int
            the insert position of tab item

        routeKey: str
            the unique name of tab item

        text: str
            the text of tab item

        text: str
            the icon of tab item

        onClick: callable
            the slot connected to item clicked signal
        """
                
        if routeKey in self.tabBar.itemMap:
            raise ValueError(f"The route key `{routeKey}` is duplicated.")

        if index == -1:
            index = len(self.tabBar.items)

        # adjust current index
        if index <= self.tabBar.currentIndex() and self.tabBar.currentIndex() >= 0:
            self.tabBar._currentIndex += 1

        item = tab_TabItem(text, self.tabBar.view, icon)
        item.setRouteKey(routeKey)

        # set the size of tab
        w = self.tabBar.tabMaximumWidth() if self.tabBar.isScrollable() else self.tabBar.tabMinimumWidth()
        item.setMinimumWidth(w)
        item.setMaximumWidth(self.tabBar.tabMaximumWidth())

        item.setShadowEnabled(self.tabBar.isTabShadowEnabled())
        item.setCloseButtonDisplayMode(self.tabBar.closeButtonDisplayMode)
        item.setSelectedBackgroundColor(
            self.tabBar.lightSelectedBackgroundColor, self.tabBar.darkSelectedBackgroundColor)

        item.pressed.connect(self.tabBar._onItemPressed)
        item.closed.connect(lambda: self.tabBar.tabCloseRequested.emit(self.tabBar.items.index(item)))
        QApplication.processEvents()
        if onClick:
            item.pressed.connect(onClick)

        self.tabBar.itemLayout.insertWidget(index, item, 1)
        self.tabBar.items.insert(index, item)
        self.tabBar.itemMap[routeKey] = item

        if len(self.tabBar.items) == 1:
            self.tabBar.setCurrentIndex(0)

        return item
    