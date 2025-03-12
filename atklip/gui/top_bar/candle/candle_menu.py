
from PySide6.QtGui import QFont,QColor
from PySide6.QtWidgets import QWidget
from atklip.gui.components import Candle_Item
from atklip.gui import FluentIcon as FIF

from atklip.gui.qfluentwidgets.components import HWIDGET,HBoxLayout,RoundMenu,TitleLabel

from atklip.gui.qfluentwidgets.common import *

from .btn_candle import CandleButton
from atklip.appmanager import AppConfig
class CANDLES(HWIDGET):
    def __init__(self,parent:QWidget=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent = parent
        self.splitToolButton = CandleButton(self)
        #create menu 
        self.menu = RoundMenu(parent=self)
        #self.menu.setFixedWidth(240)
        line_header_wg = QWidget(self.menu)
        headerLayout = HBoxLayout(line_header_wg)
        line_headerLabel = TitleLabel("CANDLES")
        line_headerLabel.setFixedHeight(25)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(line_headerLabel, 13, QFont.DemiBold)
        headerLayout.addWidget(line_headerLabel)
        headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(line_header_wg)
        self.candle = Candle_Item(FIF.CANDLE,"Japanese Candles", 'CANDLES',self.splitToolButton)
        self.heikinashi = Candle_Item(FIF.HEIKINASHI,"Heikin Ashi", 'CANDLES',self.splitToolButton)
        self.chodu = Candle_Item(FIF.CHOIDU,"Choidu Candle", 'CANDLES',self.splitToolButton)
        self.renko = Candle_Item(FIF.RENKO,"Renko", 'CANDLES',self.splitToolButton)

        # add item to card
        self.candle.resize(200, 35)
        
        self.menu.addWidget(self.candle)
        self.menu.addWidget(self.heikinashi)
        self.menu.addWidget(self.chodu)
        self.menu.addWidget(self.renko)

        self.splitToolButton.setFlyout(self.menu)
        self.addWidget(self.splitToolButton)
        self.load_favorites()
        #self.splitToolButton.dropButton.hide()
    def load_favorites(self):
        self.list_old_favorites = AppConfig.get_config_value(f"topbar.candle.favorite")
        if self.list_old_favorites == None:
            AppConfig.sig_set_single_data.emit((f"topbar.candle.favorite",[]))
            self.list_old_favorites = AppConfig.get_config_value(f"topbar.candle.favorite")
        if self.list_old_favorites:
            for item_name in self.list_old_favorites:
                item = self.findChild(Candle_Item,item_name)
                if isinstance(item,Candle_Item):
                    item.btn_fovarite.added_to_favorite()
    
    def enterEvent(self, event):
        #self.splitToolButton.dropButton.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        #self.splitToolButton.dropButton.hide()
        super().leaveEvent(event)
