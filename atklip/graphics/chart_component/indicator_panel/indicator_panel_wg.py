

from typing import TYPE_CHECKING,Any

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QPoint

from atklip.gui.qfluentwidgets.common import isDarkTheme, FluentIcon as FIF,Theme
from . indicator_panel_ui import Ui_Form as indicator_panel
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel

from atklip.graphics.chart_component.globarvar import global_signal

from atklip.graphics.chart_component.indicators.indicator_setting_wg import IndicatorSettingMenu

from atklip.controls.candle import JAPAN_CANDLE

"import all indicators"
from atklip.graphics.chart_component.indicators import * 
from atklip.graphics.chart_component.base_items.candlestick import CandleStick

style_sheet = """QWidget:hover {
	border: solid;
    border-width: 0.5px;
    border-radius: 5px;
    border-color: #474747;
}

QWidget:!hover {
	border: solid;
    border-width: 0.5px;
    border-radius: 5px;
    border-color: transparent;
}

QPushButton {
    background-color:transparent;
	border: solid;
    border-width: 0px;
    border-radius: 5px;
    border-color: transparent;

}

QPushButton:hover {
    /* "bg_two" */
   background-color: #444551;
	border: solid;
    border-width: 0px;
    border-radius: 5px;
    border-color: transparent;
}

QPushButton:!hover {
    /* "bg_two" */
   background-color: transparent;
	border: solid;
    border-width: 0px;
    border-radius: 5px;
    border-color: transparent;
}

QPushButton:pressed {
    background-color : #141622;
	border: solid;
    border-width: 0px;
    border-radius: 5px;
    border-color: transparent;
}

QLabel {
    background-color:transparent;
    color: #eaeaea;
    font: 10pt "Segoe UI";
	border: none;
}

QLabel:hover{
    background-color:transparent;
	color: #eaeaea;
    font: 12px;
    font-family: Time Newroman;
	border: none;
}

QLabel:!hover{
    background-color:transparent;
	color: #eaeaea;
    font: 12px;
    font-family: Time Newroman;
	border: none;
}
""".encode("utf-8").decode("utf-8")
class IndicatorPanel(QWidget):
    def __init__(self, parent:QWidget=None, chart=None, indicator:Any=None):
        super().__init__(parent)

        self.chart:Chart|ViewSubPanel = chart
        self._parent = parent

        self.indicator = indicator
        
        self.indicator.sig_change_indicator_name.connect(self.set_name)

        self._name = self.indicator.has["name"]
        self._menu = None

        self.indicator_panel = indicator_panel()
        self.indicator_panel.setupUi(self)
        self.setStyleSheet(style_sheet)


        self.lb_indicator_name = self.indicator_panel.name
        self.btn_setting = self.indicator_panel.btn_indicator_setting
        self.btn_show_hide = self.indicator_panel.showhide
        self.btn_more = self.indicator_panel.btn_more_option

        self.btn_close = self.indicator_panel.btn_indicator_close
        self.btn_close.clicked.connect(self._on_deleted_indicator)
        
        self.btn_show_hide.clicked.connect(self._on_hide_show)
        self.btn_setting.clicked.connect(self.show_menu)
        
        self.set_name(self._name)
        
    def set_name(self, name):
        self.lb_indicator_name.setText(name)
    
    
    def _on_deleted_indicator(self):
        self.chart.container_indicator_wg.remove_indicator_panel(self)

        if isinstance(self.indicator,CandleStick):
            # self.chart.remove_source(self.indicator.has["inputs"]["source"])
            if not isinstance(self.indicator.source, JAPAN_CANDLE):
                self.indicator.signal_delete.emit()
        # print(self.indicator)
        self.chart.sig_remove_item.emit(self.indicator)

    def _on_hide_show(self):
        if self.indicator.isVisible():
            self.indicator.hide()
            icon_path = FIF.EYE_CLOSE.path(Theme.DARK) if isDarkTheme() else FIF.EYE_CLOSE.path(Theme.LIGHT) 
            self.btn_show_hide.setIcon(QIcon(icon_path))
            self.chart.yAxis.dict_objects.update({self.indicator:False})
        else:
            self.indicator.show()
            icon_path = FIF.EYE_OPEN.path(Theme.DARK) if isDarkTheme() else FIF.EYE_OPEN.path(Theme.LIGHT) 
            self.btn_show_hide.setIcon(QIcon(icon_path))
            if not isinstance(self.indicator,BasicMA):
                self.chart.yAxis.dict_objects.update({self.indicator:True})
        # self.chart.prepareGeometryChange()
    
    def show_menu(self)->None:
        if self._menu is None:
            self._menu = IndicatorSettingMenu(self.indicator,self._parent,self.chart)
            _x = self._parent.width()
            _y = self._parent.height()
            x = (_x-self._menu.width())/2
            y = (_y-self._menu.height())/3
            self._menu.move(QPoint(x, y))
            self._menu.show()
        else:
            try:
                self._menu.deleteLater()
                self._menu = None
            except RuntimeError:
                self._menu = IndicatorSettingMenu(self.indicator,self._parent,self.chart)
                _x = self._parent.width()
                _y = self._parent.height()
                x = (_x-self._menu.width())/2
                y = (_y-self._menu.height())/3
                self._menu.move(QPoint(x, y))
                self._menu.show()
        # self.chart.prepareGeometryChange()
    
    def enterEvent(self, ev):
        global_signal.sig_show_hide_cross.emit((False,None))
        self.btn_setting.show()
        self.btn_show_hide.show()
        self.btn_more.show()
        self.btn_close.show()
        super().enterEvent(ev)
        
    def leaveEvent(self, ev):
        self.btn_setting.hide()
        self.btn_show_hide.hide()
        self.btn_more.hide()
        self.btn_close.hide()
        super().leaveEvent(ev)