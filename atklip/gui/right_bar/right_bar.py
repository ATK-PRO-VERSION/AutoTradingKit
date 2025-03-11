from PySide6.QtWidgets import QWidget, QFrame

from atklip.gui.components._pushbutton import Tradingview_Button,ShowmenuButton
from atklip.gui.qfluentwidgets.components import HorizontalSeparator
from atklip.gui.qfluentwidgets.common import isDarkTheme, Theme
from atklip.gui.right_bar.graph_data_objects import *
from atklip.gui.right_bar.hotlists import *
from atklip.gui.right_bar.watchlists import *

from .right_bar_ui import Ui_right_bar

class RIGHT_BAR(QFrame,Ui_right_bar):
    def __init__(self,parent:QWidget=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.items = []

        #self.addSeparator()
        self.object = OBJECTS(self)
        self.add_item(self.object)
        #self.addSeparator()
        self.hotlist = HOTLISTS(self)
        self.add_item(self.hotlist)
        #self.addSeparator()
        self.watchlist = WATCHLISTS(self)
        self.add_item(self.watchlist)
        #self.addSeparator()


    def get_current_btn(self):
        if isinstance(self.current_btn, ShowmenuButton):
            return self.current_btn._fluent_icon
        if isinstance(self.current_btn, Tradingview_Button):
            return self.current_btn.icon
        raise None
    
    def addSeparator(self):
        self._draw_layout.addWidget(HorizontalSeparator(self))
    
    def add_item(self,item):
        self.items.append(item)
        self._draw_layout.addWidget(item)
    def uncheck_items(self,_item:Tradingview_Button|ShowmenuButton):
        self.current_btn = _item
        if self.items != []:
            for item in self.items: 
                if item.splitToolButton != self.current_btn:
                    if isinstance(item.splitToolButton, Tradingview_Button):
                        #print(item.splitToolButton, item.splitToolButton.icon)
                        if isDarkTheme():
                            item.splitToolButton.setIcon(item.splitToolButton.icon.path(Theme.DARK))
                        else:
                            item.splitToolButton.setIcon(item.splitToolButton.icon.path(Theme.LIGHT))
                        item.splitToolButton.setChecked(False)
                    else:
                        pass

 