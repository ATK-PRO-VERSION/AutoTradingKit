
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.components import Favorite_Draw_Button
from atklip.gui import FluentIcon as FIF
from atklip.appmanager.setting import AppConfig
from atklip.gui.qfluentwidgets.common import *
from .favorite_draw_tool_setting_wg import FavoriteSettingMenu
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainlayout import MainWidget
    from atklip.graphics.chart_component.viewchart import Chart

class FAVORITE(QFrame):
    def __init__(self,parent:QWidget=None,sig_add_to_favorite=None,sig_draw_object_name=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent:MainWidget = parent
        self.sig_add_to_favorite = sig_add_to_favorite
        self.sig_draw_object_name = sig_draw_object_name
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(50,40)
        self._QLayout = QHBoxLayout(self)
        self._QLayout.setSpacing(0)
        self._QLayout.setContentsMargins(0, 0, 0, 0)
        self._QLayout.setAlignment(Qt.AlignLeft)

        self.splitToolButton = Favorite_Draw_Button(FIF.FAVORITE,self)
        
        self.splitToolButton.clicked.connect(self.add_remove_favorite_wg)

        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
    def add_remove_favorite_wg(self):
        if self.splitToolButton.isChecked():
            AppConfig.sig_set_single_data.emit((f"drawbar.favorite_draw_btn",True))
            _x = self.parent.chartbox_splitter.chart.width()
            _y = self.parent.chartbox_splitter.chart.height()
            menu = FavoriteSettingMenu(self.parent.chartbox_splitter.chart,self.sig_add_to_favorite,self.sig_draw_object_name)
            self.parent.chartbox_splitter.chart.sig_reset_drawbar_favorite_btn.connect(menu.uncheck_btns)
            self.splitToolButton.clicked.connect(menu.deleteLater)
            x,y = self.parent.chartbox_splitter.chart.x()+(_x-menu.width()), self.parent.chartbox_splitter.chart.y()+2
            menu.move(QPoint(x, y))
            menu.show()
        else:
            AppConfig.sig_set_single_data.emit((f"drawbar.favorite_draw_btn",False))

    def set_current_tool(self,tool_infor):
        tool,icon = tool_infor[0],tool_infor[1]
        self.current_tool = tool
        self.splitToolButton.change_item(icon)
        self.set_enable()
        self.sig_add_to_favorite.emit((self.current_tool.title,self.is_enabled,"draw_trenlines"))
        
    def set_enable(self):
        if self.splitToolButton.isChecked():
            self.is_enabled = True
        else:
            self.is_enabled = False
    
    def enterEvent(self, event):
        super().enterEvent(event)
    def leaveEvent(self, event):
        super().leaveEvent(event)
