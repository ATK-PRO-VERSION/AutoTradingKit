from typing import TYPE_CHECKING

from atklip.gui.qfluentwidgets.common import isDarkTheme
from atklip.gui.qfluentwidgets.components import VWIDGET
from .candle_infor_panel import CandlePanel

from .indicator_panel_wg import IndicatorPanel
from atklip.graphics.chart_component.proxy_signal import Signal_Proxy
if TYPE_CHECKING:
    from atklip.graphics.chart_component.plotwidget import ViewPlotWidget
from PySide6.QtCore import Signal,Qt

class IndicatorContainer(VWIDGET):
    sig_add_panel = Signal(object)
    sig_remove_panel = Signal(object)
    def __init__(self, parent):
        super().__init__(parent)
        self._parent:ViewPlotWidget = parent
        self.list_indicator_panel = []
        self.setStyleSheet("""background-color: transparent; """)
        self.CandlePanel = CandlePanel(self)
        self.resize(320,0)
        
        self.sig_add_panel.connect(self.add_indicator_panel,Qt.ConnectionType.AutoConnection)
        self.sig_remove_panel.connect(self.remove_indicator_panel,Qt.ConnectionType.AutoConnection)

        # self.sig_add_panel.emit(self.CandlePanel)
        self.add_indicator_panel(self.CandlePanel)

    def add_indicator_panel(self,panel:IndicatorPanel):
        self.list_indicator_panel.append(panel)
        "chua xong"
        self.addWidget(panel)
        _heigh = self._heigh()
        self.resize(320,_heigh)
        self.update()
        self._parent.prepareGeometryChange()
    
    def _heigh(self):
        _leng = len(self.list_indicator_panel)
        _heigh = 0
        for panel in self.list_indicator_panel:
            _heigh+=panel.height()
        return _heigh + (_leng-1)*5

    def add_candle_panel(self,panel:IndicatorPanel):
        self.list_indicator_panel.append(panel)
        "chua xong"
        self.addWidget(panel)
        _heigh = self._heigh()
        self.resize(320,_heigh)
        self.update()
        self._parent.prepareGeometryChange()
    
    def remove_indicator_panel(self,panel):
        "chua xong"
        self.list_indicator_panel.remove(panel)
        self.deleteWidget(panel)
        _heigh = self._heigh()
        self.resize(320,_heigh)
        self.update()
        self._parent.prepareGeometryChange()

    def get_candle_infor(self, tuple_price):
        #print(tuple_price) 
        "[64039.7, 64060.0, 64014.1, 64037.7]"
        # tuple_price = data[0][data[1]]
        if tuple_price[0] <= tuple_price[3]:
            color = '#089981'
        else:
            color = '#f23645'
            
        _precision = f".{self._parent._precision}f"
        style = f"color:{color};"
        color_theme = "#d1d4dc" if isDarkTheme else "black"
        style_0 = f"color:{color_theme};"
        # [open, close, min, max]
        html = f"<span style=\"{style_0}\">O </span><span style=\"{style}\">{tuple_price[0]:{_precision}}</span> <span style=\"{style_0}\">H </span><span style=\"{style}\">{tuple_price[1]:{_precision}}</span> <span style=\"{style_0}\">L </span><span style=\"{style}\">{tuple_price[2]:{_precision}}</span> <span style=\"{style_0}\">C </span><span style=\"{style}\">{tuple_price[3]:{_precision}}</span>"
        self.CandlePanel.candle_info.setHtml(html)
        # self._parent.prepareGeometryChange()

class SubIndicatorContainer(VWIDGET):
    sig_add_panel = Signal(object)
    sig_remove_panel = Signal(object)
    def __init__(self, parent):
        super().__init__(parent)
        self._parent:ViewPlotWidget = parent
        self.list_indicator_panel = []
        self.setStyleSheet("""background-color: transparent; """)
        self.resize(320,0)

        self.sig_add_panel.connect(self.add_indicator_panel,Qt.ConnectionType.AutoConnection)
        self.sig_remove_panel.connect(self.remove_indicator_panel,Qt.ConnectionType.AutoConnection)

    def add_indicator_panel(self,panel:IndicatorPanel):
        self.list_indicator_panel.append(panel)
        "chua xong"
        self.addWidget(panel)
        _heigh = self._heigh()
        self.resize(320,_heigh)
        self.update()
        self._parent.prepareGeometryChange()
    
    def _heigh(self):
        _leng = len(self.list_indicator_panel)
        _heigh = 0
        for panel in self.list_indicator_panel:
            _heigh+=panel.height()
        return _heigh + (_leng-1)*5

    def add_candle_panel(self,panel:IndicatorPanel):
        self.list_indicator_panel.append(panel)
        "chua xong"
        self.addWidget(panel)
        _heigh = self._heigh()
        self.resize(320,_heigh)
        self.update()
        self._parent.prepareGeometryChange()
    
    def remove_indicator_panel(self,panel):
        "chua xong"
        self.list_indicator_panel.remove(panel)
        self.deleteWidget(panel)
        _heigh = self._heigh()
        self.resize(320,_heigh)
        self.update()
        self._parent.prepareGeometryChange()

    def get_candle_infor(self, tuple_price):
        #print(tuple_price) 
        "[64039.7, 64060.0, 64014.1, 64037.7]"
        if tuple_price[0] <= tuple_price[3]:
            color = '#089981'
        else:
            color = '#f23645'
        style = f"color:{color};"
        color_theme = "#d1d4dc" if isDarkTheme else "black"
        style_0 = f"color:{color_theme};"
        # [open, close, min, max]
        html = f"<span style=\"{style_0}\">O </span><span style=\"{style}\">{tuple_price[0]}</span> <span style=\"{style_0}\">H </span><span style=\"{style}\">{tuple_price[1]}</span> <span style=\"{style_0}\">L </span><span style=\"{style}\">{tuple_price[2]}</span> <span style=\"{style_0}\">C </span><span style=\"{style}\">{tuple_price[3]}</span>"
        self.CandlePanel.candle_info.setHtml(html)
        self._parent.prepareGeometryChange()