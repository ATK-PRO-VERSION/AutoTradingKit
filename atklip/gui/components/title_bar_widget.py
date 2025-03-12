from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize, Qt

from atklip.gui.qfluentwidgets.components.container import HWIDGET
from atklip.gui.qfluentwidgets.components.widgets import SubtitleLabel
from atklip.gui.components._pushbutton import _PushButton
from atklip.gui.qfluentwidgets.common import FluentIcon as FIF
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.qfluentwidgets.components.widgets.button import PushButton

class TitleBar(HWIDGET):
    sig_mouse_move = Signal(tuple)
    def __init__(self, parent:QWidget=None, title:str=""):
        super().__init__(parent,title)
        self._parent = self.parent()
        self.title = SubtitleLabel(title,self)
        self.addWidget(self.title)
        self.addSpacer()
        self.btn_close = _PushButton(FIF.CLOSE,self)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setIconSize(QSize(20,20))
        self.addWidget(self.btn_close)
        self.setFixedHeight(50)
        self.setContentsMargins(10,10,10,10)
        self.startPos = None
        self.btn_close.clicked.connect(lambda : self._parent.hide())
        self.sig_mouse_move.connect(self.move_parent,Qt.ConnectionType.AutoConnection)
        #print((self._parent.parent().width() - self._parent.width())/2,(self._parent.parent().height() - self._parent.height())/2)
        #self._parent.move((self._parent.parent().width() - self._parent.width())/2,(self._parent.parent().height() - self._parent.height())/2)
        FluentStyleSheet.TITLEBAR.apply(self)

    def mousePressEvent(self, event):
        ev_pos = event.position()

        self.startPos = ev_pos
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        return super().mousePressEvent(event)

    def move_parent(self,updated_cursor):
        updated_cursor_x, updated_cursor_y = updated_cursor[0], updated_cursor[1]
        self._parent.move(updated_cursor_x, updated_cursor_y)
    
    def mouseMoveEvent(self, event):
        ev_pos = event.position()
 
        if self.startPos == None:
            return
        
        orig_cursor_position = self.startPos    # lastScenePos()
        if orig_cursor_position == None:
            self.startPos = ev_pos
            orig_cursor_position = self.startPos

        updated_cursor_position = ev_pos   # scenePos()

        orig_position = self._parent.pos()  # scenePos()
        # width_chart = self._parent.parent().width() - self._parent.width()    # - 240
        # height_chart = self._parent.parent().height() - self._parent.height()

        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        # print(86, updated_cursor_x, updated_cursor_y)
        # left 0, top 5  dang thu nho la bot 196 of 400, right 560 of 800\\ mo lon right 1295 of 1536 , bot 567 of 793
        # if width_chart < updated_cursor_x:
        #     updated_cursor_x = width_chart
        # if updated_cursor_x < 0:
        #     updated_cursor_x = 0
        # if height_chart < updated_cursor_y:
        #     updated_cursor_y = height_chart
        if updated_cursor_y < 5:
            updated_cursor_y = 5
        #print(updated_cursor_x, updated_cursor_y)
        self.sig_mouse_move.emit((updated_cursor_x, updated_cursor_y))
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        # self.startPos = event.position().toPoint()
        self.startPos = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        return super().mouseReleaseEvent(event)
    def enterEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        return super().enterEvent(event)
    def leaveEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().leaveEvent(event)
    
class DragWidget(PushButton):
    sig_mouse_move = Signal(tuple)
    def __init__(self, parent:QWidget=None, name:str=""):
        super().__init__(parent)
        self._parent = self.parent()
        self.setFixedSize(35,35)
        self.startPos = None
        self.sig_mouse_move.connect(self.move_parent,Qt.ConnectionType.AutoConnection)

    def mousePressEvent(self, event):
        ev_pos = event.position()
        self.startPos = ev_pos
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        return super().mousePressEvent(event)

    def move_parent(self,updated_cursor):
        updated_cursor_x, updated_cursor_y = updated_cursor[0], updated_cursor[1]
        self._parent.move(updated_cursor_x, updated_cursor_y)
    
    def mouseMoveEvent(self, event):
        ev_pos = event.position()
        if self.startPos == None:
            return
        orig_cursor_position = self.startPos    # lastScenePos()
        if orig_cursor_position == None:
            self.startPos = ev_pos
            orig_cursor_position = self.startPos

        updated_cursor_position = ev_pos   # scenePos()

        orig_position = self._parent.pos()  # scenePos()
        # width_chart = self._parent.parent().width() - self._parent.width()    # - 240
        # height_chart = self._parent.parent().height() - self._parent.height()

        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        # print(86, updated_cursor_x, updated_cursor_y)
        # left 0, top 5  dang thu nho la bot 196 of 400, right 560 of 800\\ mo lon right 1295 of 1536 , bot 567 of 793
        # if width_chart < updated_cursor_x:
        #     updated_cursor_x = width_chart
        # if updated_cursor_x < 0:
        #     updated_cursor_x = 0
        # if height_chart < updated_cursor_y:
        #     updated_cursor_y = height_chart
        if updated_cursor_y < 5:
            updated_cursor_y = 5
        #print(updated_cursor_x, updated_cursor_y)
        self.sig_mouse_move.emit((updated_cursor_x, updated_cursor_y))
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        # self.startPos = event.position().toPoint()
        self.startPos = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        return super().mouseReleaseEvent(event)
    def enterEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        return super().enterEvent(event)
    def leaveEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().leaveEvent(event)