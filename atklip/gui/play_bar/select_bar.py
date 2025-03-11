from typing import TYPE_CHECKING
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QIcon

from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF
from atklip.gui.components._pushbutton import IconTextChangeButton

if TYPE_CHECKING:
    from views.mainlayout import MainWidget

class SelectBar(IconTextChangeButton):
    sig_remove_menu = Signal()
    def __init__(self,parent):
        super().__init__(FIF.SELECT_BAR, "Select bar", parent)
        self.setObjectName("btn_seclect_bar")
        self._parent:MainWidget = parent
        self.setFixedSize(100,30)
        self.setIconSize(QSize(30,30))
        self._pre_x_pos = None
        self._pre_y_pos = None
        self._menu = None

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

   