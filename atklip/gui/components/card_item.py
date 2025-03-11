

from typing import TYPE_CHECKING
from atklip.gui.qfluentwidgets.common.icon import *
from atklip.gui.qfluentwidgets.common import CryptoIcon as CI, FluentIcon as FIF
from atklip.gui.qfluentwidgets.components import IconWidget,BodyLabel,HBoxLayout,CardWidget

from atklip.gui.components._pushbutton import Favorite_Button,CircleICon,Help_Button,Candle_Button
from atklip.controls import IndicatorType,PD_MAType
from atklip.appmanager.setting import AppConfig

if TYPE_CHECKING:  # pragma
    from atklip.gui.top_bar import IntervalButton

from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QHBoxLayout

class Card_Item(CardWidget):
    """ App card only for draw bar btn"""
    signal_infor = Signal(tuple)
    def __init__(self, icon, title, _type:str="", parent=None):
        super().__init__(parent)
        self.parent = parent
        self.icon = icon
        self.title = title
        self.setContentsMargins(0,0,0,0)
        self.setClickEnabled(True)
        self.iconWidget = IconWidget(self.icon,self)
        self.titleLabel = BodyLabel(title, self)
        self.btn_fovarite = Favorite_Button(FIF.HEART, self)
        self.hBoxLayout = QHBoxLayout(self)
        self.setFixedHeight(40)
        self.iconWidget.setFixedSize(30, 30)
        #self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.hBoxLayout.setContentsMargins(10, 5, 5, 5)
        self.hBoxLayout.setSpacing(5)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.hBoxLayout.addWidget(self.titleLabel)

        self.hBoxLayout.addStretch(1)

        self.hBoxLayout.addWidget(self.btn_fovarite, 0, Qt.AlignRight)

        self.btn_fovarite.setFixedSize(20, 20)
        self.btn_fovarite.clicked.connect(self.onbtn_fovariteClicked)
        self.clicked.connect(self.on_clicked)
        self.setObjectName(f"{_type}_{title}")
        
        self.list_favorites = AppConfig.get_config_value(f"drawbar.favorite")
        if self.list_favorites:
            for in_for in self.list_favorites:
                old_title = in_for["tool"]
                if old_title == title:
                    self.btn_fovarite.setChecked(True)
                    self.btn_fovarite.set_icon_color()
        
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()

    def setObjectName(self, name: str) -> None:
        self.ob_name = name
        return super().setObjectName(self.ob_name)
    def getObjectname(self) -> str:
        return self.ob_name
    def onbtn_fovariteClicked(self):
        self.parent.favorite_infor((self,self.icon,self.btn_fovarite.isChecked()))
    def on_clicked(self):
        self.parent.set_current_tool((self,self.icon))
    
    def enterEvent(self, event):
        self.btn_fovarite.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()
        super().leaveEvent(event)


class Symbol_Item(CardWidget): 
    """ App card """
    def __init__(self,sig_add_remove_favorite,sig_change_symbol, symbol:str, exchange:str, parent=None):
        super().__init__(parent)

        self.setObjectName(f"{symbol}_{exchange}")
        self.symbol_name = symbol
        self.exchange_id = exchange
        self._parent = self.parent()
        self.setContentsMargins(0,0,0,0)
        self.setClickEnabled(True)

        self.sig_change_symbol = sig_change_symbol

        symbol_icon = get_symbol_icon(symbol)
        symbol_icon_path = CI.crypto_url(symbol_icon)

        "favorite btn"
        self.btn_fovarite = Favorite_Button(FIF.HEART, self)
        self.btn_fovarite.sig_add_to_favorite.connect(self.emit_infor_add_to_favorite)
        self.btn_fovarite.setFixedSize(15, 15)
        #self.btn_fovarite.clicked.connect(self.onbtn_fovariteClicked)
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()

        self.symbol_icon = CircleICon(self, symbol_icon_path)
        self.symbol = BodyLabel(symbol, self)
        self.symbol.setContentsMargins(1,1,1,1)

        echange_icon_path,exchange_name,_mode = get_exchange_icon(exchange)

        self.exchange = BodyLabel(exchange_name, self)
        self.exchange_icon = CircleICon(self,echange_icon_path)
        self.hBoxLayout = HBoxLayout(self)
        self.setFixedHeight(40)

        self.symbol_infor = ("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path,_mode)

        self.symbol_icon.setFixedSize(30, 30)
        self.exchange_icon.setFixedSize(30, 30)
        #self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.hBoxLayout.setContentsMargins(10, 5, 5, 5)
        self.hBoxLayout.setSpacing(10)

        
        self.hBoxLayout.addWidget(self.symbol_icon, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.symbol, 0, Qt.AlignLeft)
        
        self.hBoxLayout.addSpacer()

        self.hBoxLayout.addWidget(self.btn_fovarite, 0, Qt.AlignRight)
        self.btn_fovarite.hide()
        self.hBoxLayout.addWidget(self.exchange, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.exchange_icon, 0, Qt.AlignRight)

        self.clicked.connect(self.on_clicked)

        "emit to Item Menu to add to favorite"
        self.sig_add_remove_favorite = sig_add_remove_favorite
    def emit_infor_add_to_favorite(self,_bool):
        self.sig_add_remove_favorite.emit((_bool,self.symbol_infor))

    def setObjectName(self, name: str) -> None:
        self.ob_name = name
        return super().setObjectName(self.ob_name)
    def getObjectname(self) -> str:
        return self.ob_name
    def onbtn_fovariteClicked(self):
        pass
        #self.parent.splitToolButton.add_remove_to_favorites(self.icon)
    def on_clicked(self):
        """('change_symbol', 'ACHUSDT', 'binanceusdm', 'Binance Perpetual', 
        ':/qfluentwidgets/images/crypto/ach.svg', ':/qfluentwidgets/images/exchange/binance_logo.svg', 'FUTURES')"""
        self.sig_change_symbol.emit(self.symbol_infor)

    def enterEvent(self, event):
        self.btn_fovarite.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()
        super().leaveEvent(event)

class Indicator_Item(CardWidget):
    """ App card """
    def __init__(self,sig_add_remove_favorite,sig_add_indicator_to_chart, _type_indicator,title, parent=None):
        super().__init__(parent)
        self.title:IndicatorType|PD_MAType = title
        self.setObjectName(self.title.name)
        self.parent = parent
        self._type_indicator = _type_indicator
        
        self.sig_add_remove_favorite,self.sig_add_indicator_to_chart = sig_add_remove_favorite,sig_add_indicator_to_chart
        self.setContentsMargins(0,0,0,0)
        self.setClickEnabled(True)
        self.helpBtn = Help_Button(FIF.HELP,self)
        self.titleLabel = BodyLabel(self.title.value, self)
        self.btn_fovarite = Favorite_Button(FIF.HEART, self)
        self.btn_fovarite.sig_add_to_favorite.connect(self.emit_infor_add_to_favorite)
        self.btn_fovarite.setFixedSize(30, 30)
        self.btn_fovarite.hide()

        self.hBoxLayout = QHBoxLayout(self)
        self.setFixedHeight(40)
        self.helpBtn.setFixedSize(30, 30)
        #self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.hBoxLayout.setContentsMargins(10, 5, 5, 5)
        self.hBoxLayout.setSpacing(5)
        self.hBoxLayout.addWidget(self.helpBtn)
        self.hBoxLayout.addWidget(self.titleLabel)
        self.hBoxLayout.addWidget(self.btn_fovarite, 0, Qt.AlignRight)

        self.clicked.connect(self.on_clicked)
        
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()
    
    def setObjectName(self, name: str) -> None:
        self.ob_name = name
        return super().setObjectName(self.ob_name)
    def getObjectname(self) -> str:
        return super().objectName()
    def emit_infor_add_to_favorite(self,_bool):
        self.sig_add_remove_favorite.emit((_bool,self._type_indicator,self.title))
    def on_clicked(self):
        self.sig_add_indicator_to_chart.emit((self._type_indicator,self.title))
    def enterEvent(self, event):
        self.btn_fovarite.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()
        super().leaveEvent(event)



class Interval_Item(CardWidget):
    """ App card """
    def __init__(self,_name, title, _type, parent=None):
        super().__init__(parent)
        self.setObjectName(_name)
        self.splitToolButton:IntervalButton = parent
        self.title:str = title
        self.setContentsMargins(0,0,0,0)
        self.setClickEnabled(True)
        self.titleLabel = BodyLabel(title, self)
        self.btn_fovarite = Favorite_Button(FIF.HEART, self.splitToolButton)
        self.hBoxLayout = QHBoxLayout(self)
        self.setFixedHeight(35)
 
        #self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.hBoxLayout.setContentsMargins(10, 5, 5, 5)
        self.hBoxLayout.setSpacing(5)
    
        self.hBoxLayout.addWidget(self.titleLabel)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.btn_fovarite, 0, Qt.AlignRight)
        self.btn_fovarite.setFixedSize(20, 20)
        self.btn_fovarite.clicked.connect(self.onbtn_fovariteClicked)
        self.clicked.connect(self.on_clicked)
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()

    def setObjectName(self, name: str) -> None:
        self.ob_name = name
        return super().setObjectName(self.ob_name)
    def getObjectname(self) -> str:
        return self.ob_name
    def get_title(self):
        if self.title == "1 minute":
            return "1m"
        elif self.title == "3 minutes":
            return "3m"
        elif self.title == "5 minutes":
            return "5m"
        elif self.title == "15 minutes":
            return "15m"
        elif self.title == "30 minutes":
            return "30m"
        elif self.title == "1 hour":
            return "1h"
        elif self.title == "2 hours":
            return "2h"
        elif self.title == "4 hours":
            return "4h"
        elif self.title == "6 hours":
            return "6h"
        elif self.title == "12 hours":
            return "12h"
        elif self.title == "1 day":
            return "1d"
        elif self.title == "3 days":
            return "3d"
        elif self.title == "1 week":
            return "1w"
        return "none"
             
    def onbtn_fovariteClicked(self):
        self.splitToolButton.add_remove_to_favorites(self.get_title())
    def on_clicked(self):
        self.splitToolButton.change_item(self.get_title())
    
    def enterEvent(self, event):
        self.btn_fovarite.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()
        super().leaveEvent(event)

class Candle_Item(CardWidget):
    """ App card """
    def __init__(self, icon, title, _type, parent=None):
        super().__init__(parent)
        self.splitToolButton:Candle_Button = parent
        self.setObjectName(title)
        self.icon = icon
        self.setContentsMargins(2,2,2,2)
        self.setClickEnabled(True)
        self.iconWidget = IconWidget(self.icon,self)
        self.titleLabel = BodyLabel(title, self)
        self.btn_fovarite = Favorite_Button(FIF.HEART, self.splitToolButton)
        self.hBoxLayout = QHBoxLayout(self)
        self.setFixedHeight(35)
        self.iconWidget.setFixedSize(30, 30)
        #self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.hBoxLayout.setContentsMargins(10, 5, 5, 5)
        self.hBoxLayout.setSpacing(5)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.hBoxLayout.addWidget(self.titleLabel)

        self.hBoxLayout.addStretch(1)

        self.hBoxLayout.addWidget(self.btn_fovarite, 0, Qt.AlignRight)

        self.btn_fovarite.setFixedSize(20, 20)
        self.btn_fovarite.clicked.connect(self.onbtn_fovariteClicked)
        self.clicked.connect(self.on_clicked)
        
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()

    def setObjectName(self, name: str) -> None:
        self.ob_name = name
        return super().setObjectName(self.ob_name)
    def getObjectname(self) -> str:
        return self.ob_name
    def onbtn_fovariteClicked(self):
        self.splitToolButton.add_remove_to_favorites(self.icon)
    def on_clicked(self):
        self.splitToolButton.change_item(self.icon)
    
    def enterEvent(self, event):
        self.btn_fovarite.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        if self.btn_fovarite.isChecked():
            self.btn_fovarite.show()
        else:
            self.btn_fovarite.hide()
        super().leaveEvent(event)