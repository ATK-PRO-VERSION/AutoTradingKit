import asyncio
import traceback
import re
import requests

from atklip.gui.qfluentwidgets.components.widgets import SearchLineEdit
from atklip.gui.qfluentwidgets.components.container import HWIDGET
from atklip.gui.qfluentwidgets import EchangeIcon as EI,FluentStyleSheet
from atklip.gui.components import ScrollInterface,ICON_TEXT_BUTTON_SYMBOL,Symbol_Item,MovingWidget

from PySide6.QtWidgets import QStackedWidget,QAbstractScrollArea, QWidget,QApplication
from PySide6.QtCore import QEvent, Signal,QCoreApplication
from PySide6.QtGui import Qt

from atklip.exchanges import list_exchanges, CryptoExchange, _exchanges
from atklip.appmanager.worker import RequestAsyncWorker,ThreadingAsyncWorker
from atklip.gui.components import LoadingProgress
from atklip.gui.qfluentwidgets.common.icon import *
from atklip.appmanager import AppConfig, AppLogger
from atklip.app_utils import *
from .symbol_table import BaseMenu

class RightMenu(ScrollInterface):
    def __init__(self,parent:QWidget=None):
        super(RightMenu,self).__init__(parent)
        self.setObjectName("ExChanges Menu")
        self._parent:ListSymbolMenuByExchange = parent
        self.setFixedHeight(600)

        self.FAVORITE = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.FAVORITE,self._parent,"Favorite Markets",EI.FAVORITE)
        self.addWidget(self.FAVORITE)

        self.BINANCE_SPOT = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BINANCE_SPOT,self._parent,"Binance",EI.BINANCE_ICON)
        self.addWidget(self.BINANCE_SPOT)
        self.BINANCE_PERPETUAL_FUTURES = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BINANCE_PERPETUAL_FUTURES,self._parent,"Binance Perpetual",EI.BINANCE_TEXT)
        self.addWidget(self.BINANCE_PERPETUAL_FUTURES)
        # self.BINANCE_COIN_FUTURES = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BINANCE_COIN_FUTURES,self._parent,"Binance Coin",EI.BINANCE_TEXT)
        # self.addWidget(self.BINANCE_COIN_FUTURES)
        # self.BITVAVO = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BITVAVO,self._parent,"BitVAVO",EI.BITVAVO)
        # self.addWidget(self.BITVAVO)
        self.BYBIT = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BYBIT,self._parent,"ByBit",EI.BYBIT)
        self.addWidget(self.BYBIT)
        
        self.MEXC = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.MEXC,self._parent,"Mexc",EI.MEXC)
        self.addWidget(self.MEXC)
        self.KUCOIN_FUTURES = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.KUCOIN_FUTURES,self._parent,"Kucoin Futures",EI.KUCOIN_FUTURES)
        self.addWidget(self.KUCOIN_FUTURES)
        self.KUCOIN_SPOT = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.KUCOIN_SPOT,self._parent,"Kucoin Spot",EI.KUCOIN)
        self.addWidget(self.KUCOIN_SPOT)
        
        # self.DERIBIT = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.DERIBIT,self._parent,"DeriBit",EI.DERIBIT)
        # self.addWidget(self.DERIBIT)
        # self.HITBTC = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.HITBTC,self._parent,"HitBTC",EI.HITBTC)
        # self.addWidget(self.HITBTC)
        self.HUOBI = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.HUOBI,self._parent,"HuoBi",EI.HUOBI)
        self.addWidget(self.HUOBI)
        self.OKEX = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.OKEX,self._parent,"OKX",EI.OKEX)
        self.addWidget(self.OKEX)
        self.COINBASE_EXCHANGE = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.COINBASE_EXCHANGE,self._parent,"Coinbase Exchange",EI.COINBASE_PRO)
        self.addWidget(self.COINBASE_EXCHANGE)
        
        self.COINBASE = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.COINBASE,self._parent,"Coinbase Advanced",EI.COINBASE_PRO)
        self.addWidget(self.COINBASE)
        
        # self.BINGX = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BINGX,self._parent,"BingX",EI.BINGX)
        # self.addWidget(self.BINGX)
        # self.BITFINEX2 = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BITFINEX2,self._parent,"Bitfinex",EI.BITFINEX2)
        # self.addWidget(self.BITFINEX2)
        self.BITGET = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BITGET,self._parent,"Bitget",EI.BITGET)
        self.addWidget(self.BITGET)
        self.BITMART = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BITMART,self._parent,"BitMart",EI.BITMART)
        self.addWidget(self.BITMART)
        self.BITMEX = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.BITMEX,self._parent,"BitMex",EI.BITMEX)
        self.addWidget(self.BITMEX)
        
        self.KRAKEN_SPOT = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.KRAKEN_SPOT,self._parent,"Kraken Spot",EI.KRAKEN_SPOT)
        self.addWidget(self.KRAKEN_SPOT)
        # self.KRAKEN_FUTURES = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.KRAKEN_FUTURES,self._parent,"Kraken Futures",EI.KRAKEN_FUTURES)
        # self.addWidget(self.KRAKEN_FUTURES)
        # self.COINEX = ICON_TEXT_BUTTON_SYMBOL(list_exchanges.COINEX,self._parent,"CoinEX",EI.COINEX)
        # self.addWidget(self.COINEX)
        #self.addSpacer()

class ListSymbolMenuByExchange(QStackedWidget):
    sig_add_remove_favorite = Signal(tuple)
    sig_add_basemenu = Signal(object)
    def __init__(self,sig_change_symbol,parent:QWidget=None):
        super(ListSymbolMenuByExchange,self).__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self._list_menu:List[BaseMenu] = []
        self.sig_add_basemenu.connect(self.addWidget,Qt.ConnectionType.AutoConnection)

        for exchange in list(_exchanges.values()):
            # if exchange != "favorite":
            menu = BaseMenu(self.sig_add_remove_favorite,sig_change_symbol,self,exchange)
            self._list_menu.append(menu)
            self.sig_add_basemenu.emit(menu)

        #self.setSpacing(0)
        self.changePage("favorite")
        self.sig_add_remove_favorite.connect(self.add_remove_favorite_item,Qt.ConnectionType.AutoConnection)
    
    def add_remove_favorite_item(self,item_data):
        target_exchange_id = item_data[1][5]
        exchange_id = item_data[0]
        new_data = item_data[1]
        favorite_menu =  self.get_exchange_menu("favorite")
        exchange_menu =  self.get_exchange_menu(target_exchange_id)
        exchange_menu.add_remove_favorite_item(exchange_id,new_data)
        favorite_menu.add_remove_favorite_item(exchange_id,new_data)

    def get_exchange_menu(self,exchange_name:str)->'BaseMenu':
        return self.findChild(BaseMenu,exchange_name)
    
    def setCurrentWidget(self, widget):
        return super().setCurrentWidget(widget)
    # def setCurrentIndex(self, index, popOut=False):
    #     return super().setCurrentIndex(index, popOut)
    def changePage(self,exchange_name):
        _wg = self.get_exchange_menu(exchange_name)
        if isinstance(_wg,BaseMenu):
            self.setCurrentWidget(_wg)
            # _wg.switch_page()

    def filter_table(self,keyword:str=""):
        _wg:BaseMenu = self.currentWidget()
        if isinstance(_wg,BaseMenu):
            _wg.filter_table(keyword)
    
class MainMenu(HWIDGET):
    def __init__(self,sig_change_symbol,parent:QWidget=None):
        super(MainMenu,self).__init__(parent)
        self.ListSymbols = ListSymbolMenuByExchange(sig_change_symbol,self)
        self.rightmenu = RightMenu(self.ListSymbols)
        self.rightmenu.setFixedWidth(250)
        self.addWidget(self.rightmenu)
        self.addSeparator(_type = "VERTICAL",w=2,h=self.parent().height())
        self.addWidget(self.ListSymbols)
        
        # for menu in self.ListSymbols._list_menu:
        #     # if menu.exchange_id == "favorite":
        #     menu.load_favorite()

class SymbolSearchMenu(MovingWidget):
    def __init__(self,sig_remove_menu,sig_change_symbol,parent:QWidget=None):
        super(SymbolSearchMenu, self).__init__(parent,"Search Symbol")
        self.title.btn_close.clicked.connect(sig_remove_menu,Qt.ConnectionType.AutoConnection)
        self.setFixedSize(600,600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        #self.setFixedWidth(700)
        #self.setSpacing(2)
        self.search_box = SearchLineEdit(self)
        self.search_box.setFixedHeight(35)
        self.addWidget(self.search_box)
        self.main_menu = MainMenu(sig_change_symbol,self)
        
        self.search_box.textChanged.connect(self.main_menu.ListSymbols.filter_table)
        
        self.addWidget(self.main_menu)
        sig_change_symbol.connect(self.remove_menu)
        FluentStyleSheet.INDICATORMENU.apply(self)
    def remove_menu(self,data):
        self.title.btn_close.clicked.emit()