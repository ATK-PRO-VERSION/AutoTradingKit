import sys

from PySide6.QtCore import Qt, QSize, QUrl, QPoint
from PySide6.QtGui import QIcon, QDesktopServices, QColor
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QFrame, QStackedWidget,QApplication

from atklip.gui.qfluentwidgets import (qrouter, MessageBox, MSFluentTitleBar, MSFluentWindow, SubtitleLabel, setFont, TabCloseButtonDisplayMode, IconWidget, FluentStyleSheet,
                            TransparentDropDownToolButton, TransparentToolButton, setTheme, Theme, isDarkTheme)
from atklip.gui import FluentIcon as FIF

from typing import TYPE_CHECKING

from atklip.gui.qfluentwidgets.components.widgets.tab_view import TabBar
from atklip.gui.top_bar.layouts_saving.btn_layout_saving import DonateBtn
from atklip.gui.top_bar.profile.btn_profile import AvatarButton

if TYPE_CHECKING:
    from .fluentwindow import WindowBase


class _TabBar(TabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        
    def removeTab(self, index: int):
        if not 0 <= index < len(self.items):
            return
        # adjust current index
        if index < self.currentIndex():
            self._currentIndex -= 1
        elif index == self.currentIndex():
            if self.currentIndex() > 0:
                self.setCurrentIndex(self.currentIndex() - 1)
                QApplication.processEvents()
            elif len(self.items) == 1:
                self._currentIndex = -1
            else:
                self.setCurrentIndex(1)
                self._currentIndex = 0
                QApplication.processEvents()
        # remove tab
        item = self.items.pop(index)
        self.itemMap.pop(item.routeKey())
        self.hBoxLayout.removeWidget(item)
        # qrouter.remove(item.routeKey())
        item.deleteLater()
        # remove shadow
        self.update()


class TitleBar(MSFluentTitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add buttons
        self._parent:WindowBase = self.parent()
        # self.toolButtonLayout = QHBoxLayout()
        # color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        
        # self.forwardButton = TransparentToolButton(FIF.RIGHT_ARROW.icon(color=color), self)
        # self.backButton = TransparentToolButton(FIF.LEFT_ARROW.icon(color=color), self)

        # self.forwardButton.setDisabled(True)
        # self.toolButtonLayout.setContentsMargins(20, 0, 20, 0)
        # self.toolButtonLayout.setSpacing(15)

        # self.toolButtonLayout.addWidget(self.backButton)
        # self.toolButtonLayout.addWidget(self.forwardButton)
        # self.hBoxLayout.insertLayout(4, self.toolButtonLayout)

        # add tab bar
        self.tabBar = _TabBar(self)

        self.tabBar.setMovable(False)
        self.tabBar.setTabMaximumWidth(180)
        self.tabBar.setTabShadowEnabled(True)
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))

        self.tabBar.setScrollable(True)
        self.tabBar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)

        self.hBoxLayout.insertWidget(4, self.tabBar, 1)
        self.hBoxLayout.setStretch(5, 0)
        
        self.Donate_Btn = DonateBtn("Sponsor",self._parent)
        self.profile = AvatarButton(self._parent)
        self.hBoxLayout.insertWidget(5,self.Donate_Btn, 0, Qt.AlignRight)
        self.hBoxLayout.insertWidget(6,self.profile, 0, Qt.AlignRight)
        
        FluentStyleSheet.TITLEBAR.apply(self)

    def canDrag(self, pos: QPoint):
        if not super().canDrag(pos):
            return False
        pos.setX(pos.x() - self.tabBar.x())
        return not self.tabBar.tabRegion().contains(pos)
    
    def mousePressEvent(self, event):
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        return super().mouseReleaseEvent(event)
    
    def enterEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        return super().enterEvent(event)
    def leaveEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().leaveEvent(event)