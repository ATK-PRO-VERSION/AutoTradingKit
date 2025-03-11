
from typing import TYPE_CHECKING
from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QPushButton,QHBoxLayout, QSizePolicy, QVBoxLayout)

from atklip.gui.qfluentwidgets.common import *
from atklip.gui.qfluentwidgets.common.icon import CryptoIcon as CI
from atklip.appmanager.setting import AppConfig
from .symbol_menu import SymbolSearchMenu
if TYPE_CHECKING:
    from views.mainlayout import MainWidget

class _PushButton(QPushButton):
    """ Transparent push button
    Constructors
    ------------
    * TransparentPushButton(`parent`: QWidget = None)
    * TransparentPushButton(`text`: str, `parent`: QWidget = None, `icon`: QIcon | str | FluentIconBase = None)
    * TransparentPushButton(`icon`: QIcon | FluentIcon, `text`: str, `parent`: QWidget = None)
    """
    def __init__(self, icon, text, parent):
        super().__init__(icon=icon, text=text, parent=parent)
        
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        self.setFixedHeight(35)
        # self.setMinimumWidth(100)
        # self.setMaximumWidth(130)
        
        self.setContentsMargins(5,2,5,2)
    
    def set_text(self,text,color):
        self.setText(text)
        self.set_stylesheet(color)
    def title(self):
        return self.text()
    def set_stylesheet(self,color):
        self.setStyleSheet(f"""QPushButton {{
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            color: {color};
                            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';
                            }}""")
    
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.setStyleSheet(f"""QPushButton {{
            background-color: {background_color};
            border: none;
            border-radius: 4px;
            color: {color};
            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';
            }}""")

        #super().enterEvent(event)
    def leaveEvent(self, event):
        #background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        super().leaveEvent(event)

class SymbolButton(_PushButton):
    sig_remove_menu = Signal()
    def __init__(self,sig_change_symbol, icon, text, parent):
        _icon = QIcon(icon.path())
        super().__init__(_icon, text, parent)
        self._parent:MainWidget = self.parent()
        self.setIconSize(QSize(20, 20))

        self._pre_x_pos = None
        self._pre_y_pos = None
        self._menu = None
        self.sig_change_symbol = sig_change_symbol
        self.clicked.connect(self.show_menu,Qt.ConnectionType.AutoConnection)
        self.sig_remove_menu.connect(self.remove_menu,Qt.ConnectionType.AutoConnection)
        self.sig_change_symbol.connect(self.set_symbol,Qt.ConnectionType.AutoConnection)
        self.load_pre_config()
    
    def load_pre_config(self):
        curent_tab = AppConfig.get_config_value("profiles.current_tab")
        if curent_tab == None:
            AppConfig.sig_set_single_data.emit(("profiles.current_tab", {"exchangeID":"binanceusdm","symbol":"BTC/USDT"}))
            curent_tab = AppConfig.get_config_value("profiles.current_tab")
        # current_ex = curent_tab["exchangeID"]
        current_symbol = curent_tab["symbol"]
        symbol_icon = get_symbol_icon(current_symbol)
        symbol_icon_path = CI.crypto_url(symbol_icon)
        self._symbol = current_symbol
        self.set_text(current_symbol)
        _icon = QIcon(symbol_icon_path)
        self.setIcon(_icon)

    def symbol(self) -> str:
        return self._symbol
        
    def set_text(self, text):
        super().setText(text)
    def icon(self):
        return super().icon()
    
    def set_symbol(self,args):
        """("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path,_mode)"""
        print(args)
        icon =  args[4] 
        symbol = args[1]
        self._symbol = symbol
        self.set_text(symbol)
        _icon = QIcon(icon)
        self.setIcon(_icon)
    def setup_menu(self):
        if self._menu is None:
            self._menu = SymbolSearchMenu(self.sig_remove_menu,self.sig_change_symbol,self._parent)
            _x = self._parent.width()
            _y = self._parent.height()
            x = (_x-self._menu.width())/2
            y = (_y-self._menu.height())/2
            self._menu.move(QPoint(x, y))
            self._menu.hide()
    def show_menu(self)->None:
        if self._menu is None:
            self._menu = SymbolSearchMenu(self.sig_remove_menu,self.sig_change_symbol,self._parent)
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
            if pos!=None:
                _pos = self.mapFromParent(QPoint(pos.x(),pos.y()))
                _rect = QRectF(self._menu.x(),self._menu.y(),self._menu.width(),self._menu.height())
                if not _rect.contains(QPoint(pos.x(),pos.y())):
                    self._menu.hide()
            else:
                self._menu.hide()