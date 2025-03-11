

from .exchange_ui import Ui_cr_exchange
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.qfluentwidgets.common import EchangeIcon as EI
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt,QSize

from atklip.appmanager.setting import AppConfig

class CR_EXCHANGE(QWidget,Ui_cr_exchange):
    """
    CR_EXCHANGE
    """
    def __init__(self,sig_change_symbol, parent: QWidget=None,icon:EI=EI.BINANCE_ICON,exchange:str='Binance',mode:str='FUTURES'):
        super().__init__(parent)
        self.setupUi(self)
        # icon_path = icon.path() #:/qfluentwidgets/images/exchange/Binance.png
        #self.exchange_icon.setImage(icon_path)
        # self.exchange_icon.set_pixmap_icon(icon_path)
        self.exchange.setStyleSheet("QLabel {color:#d1d4dc;}")
        self.mode.setStyleSheet("QLabel {color:#d1d4dc;}")
        sig_change_symbol.connect(self.setexchange,Qt.ConnectionType.AutoConnection)
        self.load_pre_config()
        FluentStyleSheet.TRANSCARD.apply(self)
    
    def load_pre_config(self):
        curent_tab = AppConfig.get_config_value("profiles.current_tab")
        if curent_tab == None:
            AppConfig.sig_set_single_data.emit(("profiles.current_tab", {"exchangeID":"binanceusdm","symbol":"BTC/USDT"}))
            curent_tab = AppConfig.get_config_value("profiles.current_tab")
        current_ex = curent_tab["exchangeID"]
        current_symbol = curent_tab["symbol"]
        icon_path, ex_name,ex_mode = get_exchange_icon(current_ex)
        self.exchange_icon.set_pixmap_icon(icon_path)
        self.exchange.setText(ex_name)
        self.mode.setText(ex_mode)
        # return icon_path, ex_name,ex_mode
    def setexchange(self,args)->None:
        """("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path,_mode)"""
        # print(args)
        # symbol_name = args[1]
        exchange_name = args[3]
        icon =  args[5] #QPixmap(icon)
        _mode = args[6]
        #_icon = QPixmap(icon)
        self.exchange_icon.set_pixmap_icon(icon)
        self.exchange.setText(exchange_name)
        self.mode.setText(_mode)
