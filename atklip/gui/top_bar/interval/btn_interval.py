from typing import List
from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtWidgets import (QWidget,QPushButton,QHBoxLayout, QSizePolicy, QVBoxLayout)
from atklip.appmanager.setting.config import AppConfig

from atklip.gui.qfluentwidgets.components.widgets import SplitWidgetBase,PushButton,RoundMenu

from atklip.gui.components import _SplitDropButton,_PushButton
from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF
from atklip.gui.qfluentwidgets.common import isDarkTheme

from atklip.gui import qconfig, Config

from .interval_menu import INTERVALS


class _PushButton(QPushButton):
    """ Transparent push button
    Constructors
    ------------
    * TransparentPushButton(`parent`: QWidget = None)
    * TransparentPushButton(`text`: str, `parent`: QWidget = None, `icon`: QIcon | str | FluentIconBase = None)
    * TransparentPushButton(`icon`: QIcon | FluentIcon, `text`: str, `parent`: QWidget = None)
    """
    def __init__(self, text="",parent=None):
        super().__init__(text,parent)
        self.setObjectName(text.lower())
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self._parent = self.parent()
        self.set_stylesheet(color)
        self.setMinimumWidth(40)
        self.setFixedHeight(35)
        self.setContentsMargins(2,2,2,2)
        self.setCheckable(True)
        self.setChecked(False)

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

        super().enterEvent(event)
    def leaveEvent(self, event):
        #background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        super().leaveEvent(event)

class IntervalButton(SplitWidgetBase):
    """ Split tool button

    Constructors
    ------------
    * SplitToolButton(`parent`: QWidget = None)
    * SplitToolButton(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
    """

    clicked = Signal()
    def __init__(self, parent: QWidget = None,sig_change_inteval:Signal=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setObjectName('IntervalButton')
        self.intervals:List[_PushButton]  = []
        self.favorites:List[_PushButton] = []
        self.current_active:_PushButton = None

        self.cfg:Config = qconfig._cfg

        self.m1 = _PushButton("1m",self)
        self.m3 = _PushButton("3m",self)
        self.m5 = _PushButton("5m",self)
        self.m15 = _PushButton("15m",self)
        self.m30 = _PushButton("30m",self)
        self.h1 = _PushButton("1H",self)
        self.h2 = _PushButton("2H",self)
        self.h4 = _PushButton("4H",self)
        self.h6 = _PushButton("6H",self)
        self.h12 = _PushButton("12H",self)
        self.d1 = _PushButton("1D",self)
        self.d3 = _PushButton("3D",self)
        self.w1 = _PushButton("1W",self)
        self.is_loaded = False
        self._w:float=None
        self._postInit()
        
        self.sig_change_inteval = sig_change_inteval
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        self.interval_menu = INTERVALS(parent,self)

    def resizeEvent(self, e):
        super().resizeEvent(e)
    
    def get_current_inteval(self):
        return self.current_active.title()

    def save_favorites(self):
        if self.favorites != []:
            for item in  self.favorites:
                pass
    def setWidget(self, widget: QWidget):
        """ set the widget on left side """
        self.intervals.append(widget)
        self.hBoxLayout.addWidget(widget, 1, Qt.AlignLeft)

    def uncheck_items(self,btn):
        btn.setChecked(False)
        color = "#d1d4dc" if isDarkTheme() else  "#d1d4dc"
        btn.setStyleSheet(f"""QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
            margin: 0;
            color: {color};
            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';
            }}""")
        
    def set_text_color(self,btn):
        if btn.isChecked():
            btn.setStyleSheet("""QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    margin: 0;
                    color: "#0055ff";
                    font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';
                    }""")

    def _postInit(self):
        
        self.list_old_favorites = AppConfig.get_config_value(f"topbar.interval.favorite")
        self.old_actice_btn = AppConfig.get_config_value(f"topbar.interval.acticebtn")
        if self.list_old_favorites == None:
            AppConfig.sig_set_single_data.emit((f"topbar.interval.favorite",[]))
            self.list_old_favorites = AppConfig.get_config_value(f"topbar.interval.favorite")
        if self.old_actice_btn == None:
            AppConfig.sig_set_single_data.emit((f"topbar.interval.acticebtn","1m"))
            self.old_actice_btn = AppConfig.get_config_value(f"topbar.interval.acticebtn")
            
        for button in [self.m1, self.m3,self.m5,self.m15,self.m30,self.h1,self.h2,self.h4,self.h6,self.h12,self.d1,self.d3,self.w1]:
            button.clicked.connect(self.change_item)
            self.setWidget(button)
            button.hide()
            if button.title().lower() == self.old_actice_btn:
                    self.setcurrent_item(button)
            if self.list_old_favorites != []:
                if button.title().lower() in self.list_old_favorites:
                    self.favorites.append(button)
                    button.show()
        self._w = self.width()
        for button in [self.m1, self.m3,self.m5,self.m15,self.m30,self.h1,self.h2,self.h4,self.h6,self.h12,self.d1,self.d3,self.w1]:
            # if button.title().lower() == self.old_actice_btn:
            #     continue
            if button.isVisible():
                self._w += button.width()+35
        _h = self.height()
        
                
        self.setDropButton(_SplitDropButton(self))
        self.setDropIcon(FIF.ARROW_DOWN)
        self.setDropIconSize(QSize(10, 10))
        self.dropButton.setFixedSize(16,35)
        self.is_loaded = True
        self._w += self.dropButton.width()
        self.resize(self._w,_h)
        # self._parent._parent.resize()

    def setcurrent_item(self,current_active:_PushButton):
        if self.current_active == None:
            self.current_active = current_active
        elif self.current_active != current_active:
            self.current_active = current_active 
            if self.is_loaded:
                self.sig_change_inteval.emit(("change_interval",self.current_active.title().lower()))
        
        self.current_active.setChecked(True)
        self.current_active.show()
        self.set_text_color(self.current_active)
        
        if self.favorites != []:
            for item in self.intervals:
                if item not in self.favorites and item  is not self.current_active:
                    item.hide()
        else:
            for item in self.intervals:
                if item  is not self.current_active:
                    item.hide()
        AppConfig.sig_set_single_data.emit((f"topbar.interval.acticebtn",self.current_active.title().lower()))

    def setFlyout(self, flyout):
        self.flyout = flyout
    def showFlyout(self):
        """ show flyout """
        w = self.flyout
        if not w:
            return
        if isinstance(w, RoundMenu):
            #w.view.setMinimumWidth(self.width())
            #w.view.adjustSize()
            #w.adjustSize()
            x = self.width()
            #y = self.height()
            y = 0
            w.exec(self.mapToGlobal(QPoint(x, y)))
    
    def add_remove_to_favorites(self, title:str=None):
        """ add item to favorites """
        if self.intervals != []:
            for button in self.intervals:
                if button.title().lower() == title.lower():
                    if button not in self.favorites:
                        self.favorites.append(button)
                        # self.cfg.intervalFavorites
                        button.show()
                    else:
                        if self.current_active != None:
                            if button != self.current_active:
                                self.favorites.remove(button)
                                button.hide()
                            else:
                                self.favorites.remove(button)
                        else:
                            if button.isVisible():
                                self.favorites.remove(button)
                                button.hide()
        
        _list_favorites = []
        if self.favorites != []:
            _list_favorites = [button.title().lower() for button in self.favorites]
        AppConfig.sig_set_single_data.emit((f"topbar.interval.favorite",_list_favorites))
        self.update()
        self.showFlyout()
    def change_item(self,name=""):
        """ change item """
        if isinstance(self.current_active,_PushButton):
            self.uncheck_items(self.current_active)
        btn = self.sender()
        if isinstance(btn,_PushButton):
            self.setcurrent_item(btn)
        else:
            btn = self.findChild(_PushButton,name)
            if btn != None:
                self.setcurrent_item(btn)
        self.update()
