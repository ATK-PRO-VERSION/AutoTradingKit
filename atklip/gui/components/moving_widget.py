from PySide6.QtGui import QKeyEvent,Qt
from PySide6.QtCore import QPoint,QPointF,QRectF,Signal
from PySide6.QtWidgets import QWidget, QSizePolicy,QFrame
from atklip.gui.qfluentwidgets.components.container import VWIDGET
from atklip.gui.qfluentwidgets.components.widgets import PushButton
from atklip.gui.qfluentwidgets.components.widgets.flyout import Flyout

from .title_bar_widget import TitleBar,DragWidget


class MovingWidget(VWIDGET):
    def __init__(self, parent:QWidget=None, name:str="Indicators, Metrics, Strategies"):
        super(MovingWidget, self).__init__(parent,name)
        self._parent = parent
        self.setContentsMargins(1,1,1,1)
        self.setSpacing(0)
        self.setObjectName(name)
        self.startPos = None
        self.title = TitleBar(self,name)
        self.addWidget(self.title)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

class MovingParentWG(PushButton):
    sig_mouse_move = Signal(tuple)
    def __init__(self, parent:QWidget=None,flyout=None, name:str=""):
        super().__init__(flyout)
        self.chart = parent
        self.setFixedSize(35,35)
        self.flyout:Flyout = flyout
        self.setObjectName(name)
        self.startPos = None
        self.sig_mouse_move.connect(self.move_parent,Qt.ConnectionType.AutoConnection)

    def mousePressEvent(self, event):
        try:
            ev_pos = event.position()
        except:
            ev_pos = event.pos()
 
        self.startPos = ev_pos
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        return super().mousePressEvent(event)

    def move_parent(self,updated_cursor):
        updated_cursor_x, updated_cursor_y = updated_cursor[0], updated_cursor[1]
        self.flyout.move(updated_cursor_x, updated_cursor_y)
    
    def mouseMoveEvent(self, event):
        try:
            ev_pos = event.position()
        except:
            ev_pos = event.pos()
            
        if self.startPos == None:
            return
        
        orig_cursor_position = self.startPos    # lastScenePos()
        if orig_cursor_position == None:
            self.startPos = ev_pos
            orig_cursor_position = self.startPos

        updated_cursor_position = ev_pos   # scenePos()

        orig_position = self.flyout.pos()  # scenePos()
        
        width_chart = self.chart.width() - self.flyout.width()    # - 240
        height_chart = self.chart.height() - self.flyout.height()
        
        chart_pos = self.chart.pos()

        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        # print(86, updated_cursor_x, updated_cursor_y)
        # left 0, top 5  dang thu nho la bot 196 of 400, right 560 of 800\\ mo lon right 1295 of 1536 , bot 567 of 793
        if chart_pos.x()+width_chart < updated_cursor_x:
            updated_cursor_x = chart_pos.x()+width_chart
        elif updated_cursor_x < chart_pos.x():
            updated_cursor_x = chart_pos.x()
        if chart_pos.y() + height_chart < updated_cursor_y:
            updated_cursor_y = chart_pos.y() +height_chart
        elif updated_cursor_y < chart_pos.y() + 5:
            updated_cursor_y = chart_pos.y() + 5
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
    


