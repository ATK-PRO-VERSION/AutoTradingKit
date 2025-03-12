from typing import List
from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtWidgets import QWidget
from atklip.gui.qfluentwidgets import ToggleToolButton,SplitDropButton,SplitWidgetBase,RoundMenu
from atklip.gui.components._pushbutton import Candle_Button
from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF
from atklip.gui.qfluentwidgets.common import isDarkTheme
from atklip.appmanager import AppConfig

class _SplitDropButton(SplitDropButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""QToolButton {
                            border: none;
                            border-radius: 4px;
                            background-color: transparent;}""")
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        self.setStyleSheet(f"""QToolButton {{
                                    border: none;
                                    border-radius: 4px;
                                    background-color: {background_color};}}""")
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.setStyleSheet("""QToolButton {
                                    border: none;
                                    border-radius: 4px;
                                    background-color: transparent;}""")
        super().leaveEvent(event)



class CandleButton(SplitWidgetBase):
    """ Split tool button

    Constructors
    ------------
    * SplitToolButton(`parent`: QWidget = None)
    * SplitToolButton(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
    """
    clicked = Signal()
    #@singledispatchmethod
    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent)
        self.setObjectName('Candle Button')
        self.intervals:List[ToggleToolButton]  = []
        self.favorites:List[ToggleToolButton] = []
        self.current_active = None

        self.candle = Candle_Button(self,FIF.CANDLE,"Japanese Candles")  
        self.heikinashi = Candle_Button(self,FIF.HEIKINASHI,"Heikin Ashi")  
        self.choidu = Candle_Button(self,FIF.CHOIDU,"Choidu Candle")  
        self.renko = Candle_Button(self,FIF.RENKO,"Renko")  
        # self.setDropButton(_SplitDropButton(self))
        # self.setDropIcon(FIF.ARROW_DOWN)
        # self.setDropIconSize(QSize(10, 10))
        # self.dropButton.setFixedSize(16,35)
        self.is_loaded = False

        self._postInit()

    def loadcofig(self):
        self.current_active = self.candle
    def setWidget(self, widget: QWidget):
        """ set the widget on left side """
        self.intervals.append(widget)
        self.hBoxLayout.insertWidget(0, widget, 1, Qt.AlignLeft)

    def uncheck_items(self,btn):
        if self.intervals != []:
            for button in self.intervals:
                if button != btn:
                    button.setChecked(False)
                    button.set_icon_color()
                    if button not in self.favorites:
                        button.hide() 


    def _postInit(self):
        self.list_old_favorites = AppConfig.get_config_value(f"topbar.candle.favorite")
        self.old_actice_btn = AppConfig.get_config_value(f"topbar.candle.acticebtn")
        if self.list_old_favorites == None:
            AppConfig.sig_set_single_data.emit((f"topbar.candle.favorite",[]))
            self.list_old_favorites = AppConfig.get_config_value(f"topbar.candle.favorite")
        if self.old_actice_btn == None:
            AppConfig.sig_set_single_data.emit((f"topbar.candle.acticebtn","japanese candles"))
            self.old_actice_btn = AppConfig.get_config_value(f"topbar.candle.acticebtn")
            
        for button in [self.renko,self.choidu,self.heikinashi,self.candle]:
            button.clicked.connect(self.change_item)
            self.setWidget(button)
            button.hide()
            if button.objectName() == self.old_actice_btn:
                    self.setcurrent_item(button)
            if self.list_old_favorites:
                if button.objectName() in self.list_old_favorites:
                    self.favorites.append(button)
                    button.show()
                    
            
        self.setDropButton(_SplitDropButton(self))
        self.setDropIcon(FIF.ARROW_DOWN)
        self.setDropIconSize(QSize(10, 10))
        self.dropButton.setFixedSize(16,30)
        self.is_loaded = True
        
    def setcurrent_item(self,current_active:Candle_Button):
        if self.current_active == None:
            self.current_active = current_active
        elif self.current_active != current_active:
            self.current_active = current_active 

        
        self.current_active.setChecked(True)
        self.current_active.show()
        self.uncheck_items(self.current_active)
        self.current_active.set_icon_color()
        
        if self.favorites != []:
            for item in self.intervals:
                if item not in self.favorites and item  is not self.current_active:
                    item.hide()
        else:
            for item in self.intervals:
                if item  is not self.current_active:
                    item.hide()
        AppConfig.sig_set_single_data.emit((f"topbar.candle.acticebtn",self.current_active.objectName()))

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

    def add_remove_to_favorites(self, icon=None):
        """ add item to favorites """
        if self.intervals != []:
            for button in self.intervals:
                if button._icon.value == icon.value:
                    if button not in self.favorites:
                        self.favorites.append(button)
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
            _list_favorites = [button.objectName() for button in self.favorites]
        AppConfig.sig_set_single_data.emit((f"topbar.candle.favorite",_list_favorites))
        self.update()
        self.showFlyout()
    def change_item(self):
        """ change item """
        btn = self.sender()
        if self.intervals != []:
            for button in self.intervals:
                if button == btn:
                    #button.setIcon(QIcon(_icon))
                    self.setcurrent_item(button)
                    break
        self.update()
        #self.showFlyout()
