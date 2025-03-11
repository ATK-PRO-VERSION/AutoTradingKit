# coding:utf-8
from PySide6.QtWidgets import QWidget, QVBoxLayout,QFrame,QWidget, QStackedWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt,QSize
from atklip.gui.qfluentwidgets.common.router import qrouter
from atklip.gui.qfluentwidgets.components import  TabBar
from .position_table import  PositionTable
from .titlebar import TitleBar

class BottomInterface(QWidget):
    """ Tab interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setSpacing(1)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vBoxLayout)
        
        self.tabCount = 1
        self.setStyleSheet("""
                           QWidget {
                                background-color: transparent;
                            }""")
        self.title_bar = TitleBar(self)
        self.tabBar = self.title_bar.tabBar
        self.tabBar.addButton.hide()
        self.stackedWidget = QStackedWidget(self)
        # self.tabView = QWidget(self)
        
        
        self.frame = QFrame(self)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 2))
        self.frame.setMaximumSize(QSize(16777215, 2))
        self.frame.setStyleSheet(u"background-color: #474747;")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Plain)
        
        self.vBoxLayout.addWidget(self.frame)
        self.vBoxLayout.addWidget(self.title_bar)
        self.vBoxLayout.addWidget(self.stackedWidget)
        
        
        self.overview = PositionTable(self)
        self.PositionTable = PositionTable(self)
        self.property = PositionTable(self)
        
        self.tabBar.setCloseButtonDisplayMode(2)
        self.addSubInterface(self.PositionTable,
                             'tabposition', self.tr('List of trades'))
        self.addSubInterface(self.overview,
                             'taboverview', self.tr('Overview'))
        self.addSubInterface(self.property,
                             'tabproperty', self.tr('Properties'))
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)  
        qrouter.setDefaultRouteKey(
            self.stackedWidget, self.PositionTable.objectName())

    def addSubInterface(self, widget: QLabel|QWidget, objectName, text, icon=None):
        widget.setObjectName(objectName)
        # widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stackedWidget.addWidget(widget)
        self.tabBar.addTab(
            routeKey=objectName,
            text=text,
            icon=icon,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onDisplayModeChanged(self, index):
        mode = self.closeDisplayModeComboBox.itemData(index)
        self.tabBar.setCloseButtonDisplayMode(mode)

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        if not widget:
            return

        self.tabBar.setCurrentTab(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

    def addTab(self):
        text = f'硝子酱一级棒卡哇伊×{self.tabCount}'
        self.addSubInterface(QLabel('🥰 ' + text), text, text, ':/gallery/images/Smiling_with_heart.png')
        self.tabCount += 1

    def removeTab(self, index):
        item = self.tabBar.tabItem(index)
        widget = self.findChild(QLabel, item.routeKey())

        self.stackedWidget.removeWidget(widget)
        self.tabBar.removeTab(index)
        widget.deleteLater()

