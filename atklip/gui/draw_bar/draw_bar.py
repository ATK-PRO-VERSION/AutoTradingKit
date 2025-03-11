# type: ignore
from PySide6.QtWidgets import QWidget, QFrame 
from PySide6.QtCore import Signal
from atklip.gui.draw_bar.draw_lines import *
from atklip.gui.draw_bar.draw_projection import *
from atklip.gui.draw_bar.draw_fibonaci import *
from atklip.gui.draw_bar.draw_brushs import *
from atklip.gui.draw_bar.draw_text_note import *
from atklip.gui.draw_bar.draw_cursor import *
from atklip.gui.draw_bar.draw_magnet import *
from atklip.gui.draw_bar.draw_hide import *
from atklip.gui.draw_bar.draw_measure import *
from atklip.gui.draw_bar.draw_recirclebin import *
from atklip.gui.draw_bar.draw_zoom import *
from atklip.gui.draw_bar.draw_favorite import *
from atklip.gui.draw_bar.draw_lock import *

from atklip.gui.components._pushbutton import Tradingview_Button,ShowmenuButton

from atklip.gui.qfluentwidgets.components import HorizontalSeparator
from atklip.gui.qfluentwidgets.common import isDarkTheme, Theme

from .draw_bar_ui import Ui_draw_bar

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainlayout import MainWidget
    from atklip.graphics.chart_component.viewchart import Chart

class DRAW_BAR(QFrame,Ui_draw_bar):
    sig_draw_object_name = Signal(tuple)
    sig_delete_all = Signal()
    sig_add_to_favorite = Signal(tuple)
    def __init__(self,parent:QWidget=None):
        super().__init__(parent)
        self.parent:MainWidget = self.parent()
        
        # self.chart:Chart= self.parent.chartbox_splitter.chart
        self.setupUi(self)
        self.items = []
        self._cursor = CURSOR(self)
        self.current_btn = self._cursor.splitToolButton
        #self.current_btn.setChecked(True)
        self.current_btn.set_icon_color()
        self.add_item(self._cursor)
        self.LINES = LINES(self,self.sig_draw_object_name,self.sig_add_to_favorite)
        self.FIBONACCI = FIBONACCI(self,self.sig_draw_object_name,self.sig_add_to_favorite)
        self.PROJECTS = PROJECTS(self,self.sig_draw_object_name,self.sig_add_to_favorite)
        self.BRUSHS = BRUSHS(self,self.sig_draw_object_name,self.sig_add_to_favorite)
        self.TEXTS = TEXTS(self,self.sig_draw_object_name,self.sig_add_to_favorite)
        self.RECIRCLEBIN = RECIRCLEBIN(self,self.sig_delete_all)
        self.FAVORITE = FAVORITE(self.parent,self.sig_add_to_favorite,self.sig_draw_object_name)
        self.MAGNET = MAGNET(self.parent,self.sig_draw_object_name)
        self.LOCK = LOCK(self.parent,self.sig_draw_object_name)
        
        self.add_item(self.LINES)
        self.add_item(self.FIBONACCI)
        self.add_item(self.PROJECTS)
        self.add_item(self.BRUSHS)
        self.add_item(self.TEXTS)
        self.addSeparator()
        # self.add_item(MEASURE(self))
        #self.addSeparator()
        # self.add_item(ZOOM(self))
        self.add_btn(self.MAGNET)
        self.add_btn(self.LOCK)
        # self.add_item(EYES(self))
        # self.add_item(EYES(self))
        self.addSeparator()
        self.add_item(self.RECIRCLEBIN)
        self._setting_layout.setContentsMargins(1,1,1,5)
        self._setting_layout.addWidget(self.FAVORITE)
        
        
        
    
    def reset_drawbar(self,drawed_obj):
        self.current_btn = self._cursor.splitToolButton
        self.reset_draw_bar()
    
    def get_current_btn(self):
        if isinstance(self.current_btn, ShowmenuButton):
            return self.current_btn._fluent_icon
        if isinstance(self.current_btn, Tradingview_Button):
            return self.current_btn.icon
        raise None
    
    def addSeparator(self):
        self._draw_layout.addWidget(HorizontalSeparator(self,45))
    
    def add_item(self,item):
        self.items.append(item)
        self._draw_layout.addWidget(item)
    
    def add_btn(self,wg):
        self._draw_layout.addWidget(wg)
    
    
    def uncheck_items(self,_item:Tradingview_Button|ShowmenuButton):
        
        print(_item)
        
        self.current_btn = _item
        if self.current_btn == self._cursor.splitToolButton:
            self.reset_draw_bar()
            return
        if type(self.current_btn.parent()).__name__ == "FAVORITE": return
        if type(self.current_btn.parent()).__name__ == "Card_Item": return
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
                        #print(item.splitToolButton._fluent_icon.path(Theme.DARK),item.splitToolButton._fluent_icon)
                        if item.splitToolButton._fluent_icon == None:
                            item.splitToolButton.setIcon(item.splitToolButton._icon)
                        else:
                            item.splitToolButton.setfluentIcon(item.splitToolButton._fluent_icon)
                        item.splitToolButton.button.setChecked(False)
                else:
                    pass
                    #print(self.current_btn.isChecked(),self.current_btn)
            if not self.current_btn.isChecked() and self.current_btn != self._cursor.splitToolButton:
                self.current_btn = self._cursor.splitToolButton
                self.current_btn.setChecked(True)
                self.current_btn.set_icon_color()
    
    def reset_draw_bar(self):
        # if self.current_btn != self._cursor.splitToolButton:
        #     self.current_btn = self._cursor.splitToolButton
        if self.items != []:
            for item in self.items: 
                # if type(item).__name__ not in ["LINES","FIBONACCI","PROJECTS","BRUSHS","TEXTS"]:
                if item.splitToolButton != self.current_btn:
                    if not isinstance(item.splitToolButton, ShowmenuButton):
                        #print(item.splitToolButton)
                        if isDarkTheme():
                            item.splitToolButton.setIcon(item.splitToolButton.icon.path(Theme.DARK))
                        else:
                            item.splitToolButton.setIcon(item.splitToolButton.icon.path(Theme.LIGHT))
                        item.splitToolButton.setChecked(False)
                    else:
                        if item.splitToolButton._fluent_icon == None:
                            item.splitToolButton.setIcon(item.splitToolButton._icon)
                        else:
                            item.splitToolButton.setfluentIcon(item.splitToolButton._fluent_icon)
                        item.splitToolButton.button.setChecked(False)
        if not self.current_btn.isChecked():
            self.current_btn.setChecked(True)
            self.current_btn.set_icon_color()
