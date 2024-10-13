from typing import TYPE_CHECKING

from atklip.gui.qfluentwidgets.common import FluentIcon as FIF, CryptoIcon as CI
from atklip.gui.qfluentwidgets.components import VerticalSeparator

from atklip.gui.top_bar.candle import *
from atklip.gui.top_bar.interval import *
from atklip.gui.top_bar.symbol import *
from atklip.gui.top_bar.indicator import *
from atklip.gui.top_bar.replay import *
from atklip.gui.top_bar.mode import *
from atklip.gui.top_bar.layouts_saving import *
from atklip.gui.top_bar.goto import *
from atklip.gui.top_bar.profile import *
from atklip.gui.top_bar.exchange import *
if TYPE_CHECKING:
    from views.mainlayout import MainWidget

from .topbar_ui import  Ui_Frame as TopFrame

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame,QSizePolicy

class TopBar(QFrame,TopFrame):
    sig_change_symbol = Signal(tuple)
    sig_change_inteval = Signal(tuple)
    sig_goto_date = Signal(tuple)
    sig_add_indicator_to_chart = Signal(tuple)
    sig_change_market_type = Signal(str)
    sig_replay =  Signal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent:MainWidget = self.parent()
        self.setupUi(self)
        self.setFixedHeight(40)
        self.profile = AvatarButton(self)
        self.gotodate = GotoButton(self._parent)
        self.exchange = CR_EXCHANGE(self.sig_change_symbol,self._parent)
        self.symbol = SymbolButton(self.sig_change_symbol,CI.BTC,"BTCUSDT",self._parent)
        self.interval = IntervalButton(self._parent,self.sig_change_inteval)
        # self.candle = CANDLES(self.sig_change_market_type,self._parent)
        self.indicator = IndicatorButton(self.sig_add_indicator_to_chart,self._parent)
        
        self.replay = ReplayButton(self.sig_replay,FIF.REPLAY,"Replay",self._parent)
        
        self.mode = ModeButton("Off Trading",self._parent)
        
        self.LayoutButton = LayoutButton(self._parent)

        self.left_layout.addWidget(self.profile)
        self.left_layout.addWidget(VerticalSeparator(self))
        self.left_layout.addWidget(self.exchange)
        self.left_layout.addWidget(VerticalSeparator(self))
        self.left_layout.addWidget(self.symbol)
        self.left_layout.addWidget(VerticalSeparator(self))
        self.left_layout.addWidget(self.interval)
        self.left_layout.addWidget(VerticalSeparator(self))
        #self.left_layout.addWidget(self.candle)
        #self.left_layout.addWidget(VerticalSeparator(self))
        self.left_layout.addWidget(self.indicator)
        self.left_layout.addWidget(VerticalSeparator(self))
        self.left_layout.addWidget(self.gotodate)
        self.left_layout.addWidget(self.replay)
        self.left_layout.addWidget(self.mode)
        self.right_layout.addWidget(self.LayoutButton)
        
        self.setContentsMargins(0,0,0,0)
        
        self.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)

    def setup_indicator_menu(self):
        self.indicator.setup_menu()
    def setup_symbol_menu(self):
        self.symbol.setup_menu()

