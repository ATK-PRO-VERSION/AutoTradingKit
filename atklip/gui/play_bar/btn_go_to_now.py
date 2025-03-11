from typing import TYPE_CHECKING
from PySide6.QtCore import QSize,QPoint,Signal,QRectF
from PySide6.QtWidgets import QWidget
from atklip.gui.qfluentwidgets.common import FluentIcon as FIF
from atklip.gui.components._pushbutton import IconTextChangeButton


if TYPE_CHECKING:
    from views.mainlayout import MainWidget


class GotoNow(IconTextChangeButton):
    # clicked = Signal()
    sig_remove_menu = Signal()
    def __init__(self,parent:QWidget=None):
        super().__init__(FIF.JUMP_TO_NOW,parent=parent)
        self._parent:MainWidget = parent
        self.setFixedSize(30,30)
        self.setIconSize(QSize(30,30))
        self._menu = None
        self.clicked.connect(self.show_menu)
        self.sig_remove_menu.connect(self.remove_menu)

    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)

    def setupcalendar(self):
        self._menu = None
        #self._menu.moveToThread(QApplication.instance().thread())
        _x = self._parent.width()
        _y = self._parent.height()
        x = (_x-self._menu.width())/2
        y = (_y-self._menu.height())/2
        self._menu.move(QPoint(x, y))
        self._menu.hide()
    def show_menu(self)->None:
        if self._menu is None:
            self._menu = None
            #self._menu.moveToThread(QApplication.instance().thread())
            _x = self._parent.width()
            _y = self._parent.height()
            x = (_x-self._menu.width())/2
            y = (_y-self._menu.height())/3
            self._menu.move(QPoint(x, y))
            self._menu.show()
        else:
            if self._menu.isVisible():
                self._menu.hide() 
            else:
                _x = self._parent.width()
                _y = self._parent.height()
                x = (_x-self._menu.width())/2
                y = (_y-self._menu.height())/3
                self._menu.move(QPoint(x, y))
                self._menu.show()
    
    def delete(self,ev):
        try:
            ev_pos = ev.position()
        except:
            ev_pos = ev.pos()
        self.remove_menu(ev_pos)
    
    def remove_menu(self,pos=None)->None:
        if self._menu != None:
            self.setChecked(False)
            self.set_icon_color()
            if pos!=None:
                _pos = self.mapFromParent(QPoint(pos.x(),pos.y()))
                _rect = QRectF(self._menu.x(),self._menu.y(),self._menu.width(),self._menu.height())
                if not _rect.contains(QPoint(pos.x(),pos.y())):
                    self._menu.hide()
            else:
                self._menu.hide()
  