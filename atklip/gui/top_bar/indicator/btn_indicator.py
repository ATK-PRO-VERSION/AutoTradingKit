from typing import TYPE_CHECKING
from PySide6.QtCore import Signal, Qt, QSize, QPoint,QRectF
from PySide6.QtGui import QIcon

from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF
from atklip.gui.components._pushbutton import IconTextChangeButton

from .indicator_menu import IndicatorMenu

if TYPE_CHECKING:
    from views.mainlayout import MainWidget

class IndicatorButton(IconTextChangeButton):
    sig_remove_menu = Signal()
    def __init__(self,sig_add_indicator_to_chart, parent):
        # _icon = QIcon(FIF.INDICATOR.path())
        super().__init__(FIF.INDICATOR, "Indicators", parent)
        self._parent:MainWidget = parent
        self.setIconSize(QSize(30, 30))
        self._pre_x_pos = None
        self._pre_y_pos = None
        self._menu:IndicatorMenu = None
        self.sig_add_indicator_to_chart = sig_add_indicator_to_chart
        self.clicked.connect(self.show_menu)
        self.sig_remove_menu.connect(self.remove_menu,Qt.ConnectionType.AutoConnection)
    def symbol(self) -> str:
        return self._symbol
        
    def set_text(self, text):
        super().setText(text)
    def icon(self):
        return super().icon()
    
    def set_symbol(self,args):
        """("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path,_mode)"""
        icon =  args[4] 
        symbol = args[1]
        self._symbol = symbol
        self.set_text(symbol)
        _icon = QIcon(icon)
        self.setIcon(_icon)

    def setup_menu(self):
        if self._menu is None:
            self._menu = IndicatorMenu(self.sig_remove_menu,self.sig_add_indicator_to_chart,self._parent)
            _x = self._parent.width()
            _y = self._parent.height()
            x = (_x-self._menu.width())/2
            y = (_y-self._menu.height())/2
            self._menu.move(QPoint(x, y))
            self._menu.hide()
    
    def show_menu(self)->None:
        if self._menu is None:
            self._menu = IndicatorMenu(self.sig_remove_menu,self.sig_add_indicator_to_chart,self._parent)
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
                
    