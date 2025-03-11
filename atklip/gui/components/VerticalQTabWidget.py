from PySide6.QtWidgets import (QTabBar, QStylePainter, QStyle, QStyleOptionTab, QTabWidget,
                               QStyleOptionTabWidgetFrame, QApplication)
from PySide6 import QtCore


class VerticalQTabWidget(QTabWidget):
    def __init__(self, force_top_valign=False):
        super(VerticalQTabWidget, self).__init__()
        self.setTabBar(VerticalQTabBar())
        self.setTabPosition(QTabWidget.West)
        if force_top_valign:
            self.setStyleSheet("QTabWidget::tab-bar {left : 0;}")  # using stylesheet on initializing

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTabWidgetFrame()
        self.initStyleOption(option)
        option.rect = QtCore.QRect(QtCore.QPoint(self.tabBar().geometry().width(), 0),
                                   QtCore.QSize(option.rect.width(), option.rect.height()))
        painter.drawPrimitive(QStyle.PE_FrameTabWidget, option)


class VerticalQTabBar(QTabBar):
    def __init__(self, *args, **kwargs):
        super(VerticalQTabBar, self).__init__(*args, **kwargs)
        self.setElideMode(QtCore.Qt.ElideNone)

    def tabSizeHint(self, index):
        size_hint = super(VerticalQTabBar, self).tabSizeHint(index)
        size_hint.transpose()
        return size_hint

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            if QApplication.style().objectName() == "macos":
                option.shape = QTabBar.RoundedNorth
                option.position = QStyleOptionTab.Beginning
            else:
                option.shape = QTabBar.RoundedWest
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            option.shape = QTabBar.RoundedNorth
            painter.drawControl(QStyle.CE_TabBarTabLabel, option)

