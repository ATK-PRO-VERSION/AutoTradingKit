
from atklip.gui.qfluentwidgets.components import SearchLineEdit
from atklip.gui.qfluentwidgets.components.container import VWIDGET,HWIDGET
from atklip.gui.qfluentwidgets import FluentIcon as FIF
from atklip.gui.components import ICON_TEXT_BUTTON,Indicator_Item,MovingWidget
from atklip.gui.qfluentwidgets.common import FluentStyleSheet
from atklip.appmanager.setting import AppConfig
from atklip.controls import IndicatorType

from PySide6.QtWidgets import QStackedWidget,QWidget
from PySide6.QtCore import Signal,Qt

class RightMenu(VWIDGET):
    def __init__(self,parent:QWidget=None):
        super(RightMenu, self).__init__(parent,"Right Menu")
        self._parent:MainMenu = parent
        self.favorites = ICON_TEXT_BUTTON(self._parent,"Favorites",FIF.FAVORITE)
        self.favorites.exchange_icon.setFixedSize(20,20)
        self.basics = ICON_TEXT_BUTTON(self._parent,"Basic Indicators",FIF.INDICATOR)
        self.subs = ICON_TEXT_BUTTON(self._parent,"Sub Indicators",FIF.INDICATOR)
        self.profiles = ICON_TEXT_BUTTON(self._parent,"Profiles",FIF.BAR_PATTERN)
        self.patterns = ICON_TEXT_BUTTON(self._parent,"Paterns",FIF.CANDLE)
        self.candles = ICON_TEXT_BUTTON(self._parent,"Candle Idicators",FIF.CANDLE)
        self.subview = ICON_TEXT_BUTTON(self._parent,"Sub View Idicators",FIF.CANDLE)
        self.advands = ICON_TEXT_BUTTON(self._parent,"Advand Idicators",FIF.ANHCHORED_VOLUME)
        self.strategy = ICON_TEXT_BUTTON(self._parent,"Strategies",FIF.STRATEGY)
        self.addWidget(self.favorites)
        self.addWidget(self.basics)
        self.addWidget(self.subs)
        self.addWidget(self.profiles)
        self.addWidget(self.patterns)
        self.addWidget(self.candles)
        self.addWidget(self.subview)
        self.addWidget(self.advands)
        self.addWidget(self.strategy)
        self.addSpacer()
    def get_indicator_menu(self,name):
        menu = self.findChild(ICON_TEXT_BUTTON,name)
        return menu


from atklip.gui.top_bar.indicator.indicator_table import BasicMenu

dict_indicators = {
    "Favorites": [IndicatorType.EMA],
    "Basic Indicators": [IndicatorType.FWMA ,
                        # IndicatorType.ALMA ,
                        IndicatorType.DEMA ,
                        IndicatorType.EMA ,
                        IndicatorType.HMA ,
                        IndicatorType.LINREG ,
                        IndicatorType.MIDPOINT,
                        IndicatorType.PWMA,
                        IndicatorType.RMA ,
                        IndicatorType.SINWMA ,
                        IndicatorType.SMA ,
                        # IndicatorType.SMMA ,
                        IndicatorType.SWMA ,
                        IndicatorType.T3 ,
                        IndicatorType.TEMA ,
                        IndicatorType.TRIMA ,
                        # IndicatorType.VIDYA ,
                        IndicatorType.WMA ,
                        IndicatorType.SSF ,
                        IndicatorType.ZLMA,
                        ],
    "Advand Idicators": [
                        # IndicatorType.ATKPRO,
                        IndicatorType.UTBOT,
                        IndicatorType.SMC,
                        # IndicatorType.UTBOT_WITH_BBAND,
                        IndicatorType.TRENDWITHSL,
                        IndicatorType.SuperTrend,
                        IndicatorType.ATRSuperTrend,
                        # IndicatorType.BUY_SELL_WITH_ETM_ST,
                        
                        IndicatorType.ZIGZAG,
                        IndicatorType.BB,
                        IndicatorType.KeltnerChannels,
                        IndicatorType.DonchianChannels,
                        
                        # IndicatorType.StdDev,
                        # IndicatorType.ParabolicSAR,
                        # IndicatorType.PivotsHL,
                        # IndicatorType.McGinleyDynamic,
                        # IndicatorType.KAMA,
                        # IndicatorType.ChandeKrollStop,
                        # IndicatorType.VWAP,IndicatorType.VWMA,
                        # IndicatorType.T3,
                        ],
    
    "Sub Indicators":[IndicatorType.VOLUME,
                    IndicatorType.MACD,
                    IndicatorType.RSI,
                    IndicatorType.MOM,
                    IndicatorType.RVGI,
                    IndicatorType.EMATrendMetter,
                    IndicatorType.ROC,
                    IndicatorType.SQEEZE,
                    # IndicatorType.TTM,
                    IndicatorType.TSI, 
                    IndicatorType.VOLUMEWITHMA,
                    IndicatorType.VTX,
                    IndicatorType.UO,
                    IndicatorType.StochRSI,
                    IndicatorType.TRIX,
                    IndicatorType.STC,
                    IndicatorType.Stoch,
                    
                    # IndicatorType.SOBV,
                    # IndicatorType.SFX,
                    # IndicatorType.IBS,
                    # IndicatorType.MassIndex,
                    # IndicatorType.OBV,
                    # IndicatorType.MeanDev,
                    # IndicatorType.KVO,
                    # IndicatorType.KST,
                    # IndicatorType.Ichimoku,
                    # IndicatorType.ForceIndex,
                    # IndicatorType.EMV,
                    # IndicatorType.DPO,
                    # IndicatorType.CoppockCurve,
                    # IndicatorType.CHOP,
                    # IndicatorType.ChaikinOsc,
                    IndicatorType.CCI,
                    # IndicatorType.BOP,
                    # IndicatorType.ATR,
                    # IndicatorType.Aroon,
                    # IndicatorType.AO,
                    # IndicatorType.ADX,
                    # IndicatorType.AccuDist,
                    ],
    
    "Paterns": [
                        IndicatorType.CANDLE_PATTERN,
                        IndicatorType.CUSTOM_CANDLE_PATTERN,
                        # IndicatorType.CHART_PATTERN
                        ],
    "Profiles":[IndicatorType.VWAP],
    "Candle Idicators":[
                        IndicatorType.JAPAN_CANDLE, 
                        IndicatorType.HEIKINASHI_CANDLE, 
                        IndicatorType.SMOOTH_JAPAN_CANDLE, 
                        IndicatorType.SMOOTH_HEIKINASHI_CANDLE, 
                        IndicatorType.N_SMOOTH_HEIKIN, 
                        IndicatorType.N_SMOOTH_JP],
    
    "Sub View Idicators": [IndicatorType.SUB_CHART],
    "Strategies": [IndicatorType.ATKBOT_SUPERTREND_SSCANDLE, 
                   IndicatorType.ATKBOT_SUPERTREND, 
                   IndicatorType.ATKBOT_CCI],  
}

class ListIndicatorMenu(QStackedWidget):
    sig_add_remove_favorite = Signal(tuple)
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None):
        super(ListIndicatorMenu,self).__init__(parent)
        self.sig_add_indicator_to_chart =sig_add_indicator_to_chart
        
        for _name, _list_indicator in dict_indicators.items():
        
            _wg = BasicMenu(self,
                            sig_add_indicator_to_chart = self.sig_add_indicator_to_chart,
                            sig_add_remove_favorite= self.sig_add_remove_favorite,
                            list_indicators=_list_indicator,
                            _type_indicator=_name)
        
            self.addWidget(_wg)
        #self.setSpacing(0)
        self.setContentsMargins(0,0,0,0)

        self.sig_add_remove_favorite.connect(self.add_remove_favorite_item,Qt.ConnectionType.AutoConnection)

    
    def add_remove_favorite_item(self,item_data):
        target_wg = item_data[1][4]
        sender_wg = item_data[0]
        new_data = item_data[1]
        favorite_menu =  self.get_exchange_menu("Favorites")
        indicator_menu =  self.get_exchange_menu(target_wg)
        indicator_menu.add_remove_favorite_item(sender_wg,new_data)
        favorite_menu.add_remove_favorite_item(sender_wg,new_data)
    
    
    def add_to_favorite(self,indicator,_type_indicator):
        "overwrite for favorite menu only"
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")
        if _type_indicator not in list(self.dict_favorites.keys()):
            self.dict_favorites[_type_indicator] = [indicator.name]
            self.FavoritesMenu.sig_add_indicator.emit((_type_indicator,indicator))
        else:
            if indicator.name not in self.dict_favorites[_type_indicator]:
                self.dict_favorites[_type_indicator].append(indicator.name)
                self.FavoritesMenu.sig_add_indicator.emit((_type_indicator,indicator))
        AppConfig.sig_set_single_data.emit((f"topbar.indicator.favorite.{_type_indicator}",self.dict_favorites[_type_indicator]))
        
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")

    def remove_from_favorite(self,indicator,_type_indicator):
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")
        if _type_indicator not in list(self.dict_favorites.keys()):
            return
        if indicator.name not in self.dict_favorites[_type_indicator]:
            return
        
        self.dict_favorites[_type_indicator].remove(indicator.name)
        menu = self.findChild(BasicMenu,_type_indicator)

        if isinstance(menu,BasicMenu):
            _item = menu.find_item(indicator.name)
            if isinstance(_item,Indicator_Item):
                _item.btn_fovarite.reject_from_favorite()
        _item = self.FavoritesMenu.find_item(indicator.name)
        if _item != None:
                self.FavoritesMenu.sig_remove_indicator.emit(_item)

        AppConfig.sig_set_single_data.emit((f"topbar.indicator.favorite.{_type_indicator}",self.dict_favorites[_type_indicator]))
        self.dict_favorites = AppConfig.get_config_value(f"topbar.indicator.favorite")

    def get_exchange_menu(self,exchange_name:str)->'BasicMenu':
        return self.findChild(BasicMenu,exchange_name)
    
    def setCurrentWidget(self, widget):
        return super().setCurrentWidget(widget)

    def changePage(self,exchange_name):
        _wg = self.get_exchange_menu(exchange_name)
        if isinstance(_wg,BasicMenu):
            self.setCurrentWidget(_wg)
    def filter_table(self,keyword:str=""):
        _wg:BasicMenu = self.currentWidget()
        if isinstance(_wg,BasicMenu):
            _wg.filter_table(keyword)
    

class MainMenu(HWIDGET):
    def __init__(self,parent:QWidget=None,sig_add_indicator_to_chart=None):
        super(MainMenu,self).__init__(parent)
        self.ListIndicatorMenu = ListIndicatorMenu(self,sig_add_indicator_to_chart)
        self.rightmenu = RightMenu(self.ListIndicatorMenu)
        self.addWidget(self.rightmenu)
        self.addSeparator(_type = "VERTICAL",w=2,h=self.parent().height())
        self.addWidget(self.ListIndicatorMenu)
        self.setSpacing(0)
        self.setContentsMargins(0,0,0,0)

        
class IndicatorMenu(MovingWidget):
    def __init__(self,sig_remove_menu,sig_add_indicator_to_chart,parent:QWidget=None):
        super(IndicatorMenu, self).__init__(parent,"Indicators, Metrics & Strategies")
        self.title.btn_close.clicked.connect(sig_remove_menu,Qt.ConnectionType.AutoConnection)
        #self.setFixedWidth(700)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(600,500)
        #self.setSpacing(5)
        self.search_box = SearchLineEdit(self)
        self.search_box.setFixedHeight(35)
        
        #self.addSeparator(_type = "HORIZONTAL",w=self.width(),h=2)
        self.addWidget(self.search_box)
        #self.addSeparator(_type = "HORIZONTAL",w=self.width(),h=2)
        self.main_menu = MainMenu(self,sig_add_indicator_to_chart)
        self.addWidget(self.main_menu)
        
        self.search_box.textChanged.connect(self.main_menu.ListIndicatorMenu.filter_table)
        
        FluentStyleSheet.INDICATORMENU.apply(self)



