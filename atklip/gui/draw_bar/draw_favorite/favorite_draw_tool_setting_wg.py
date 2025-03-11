from typing import TYPE_CHECKING

from atklip.gui.components import MovingParentWG
from atklip.gui.qfluentwidgets.common import *

from PySide6.QtWidgets import QWidget

from atklip.gui.components import Tradingview_Button
from atklip.gui import FluentIcon as FIF
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.qfluentwidgets.components.widgets.button import TransparentDropDownPushButton
from atklip.gui.qfluentwidgets.components.widgets.command_bar import CommandBarView
from atklip.gui.qfluentwidgets.components.widgets.menu import CheckableMenu, MenuIndicatorType
from atklip.appmanager.setting import AppConfig
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

from PySide6.QtWidgets import QWidget

class FavoriteSettingMenu(CommandBarView):
    def __init__(self, parent:QWidget=None, sig_add_to_favorite=None,sig_draw_object_name=None):
        super().__init__(parent)
        self._parent = parent
        self.sig_add_to_favorite = sig_add_to_favorite
        self.sig_draw_object_name = sig_draw_object_name
        self.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.bar.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.hBoxLayout.setSpacing(0)
        self.bar.setSpacing(0)
                       
        self.moving_btn = MovingParentWG(self._parent,self)
        self.moving_btn.setFixedSize(35,35)
        self.hBoxLayout.insertWidget(0,self.moving_btn,0)
        
        self.sig_add_to_favorite.connect(self.add_favorite_btn)
      
        self.map_btn_drawtool_name:dict={}
        self.map_drawtool_btn:dict={}
        self.list_favorites:List=[]
        self.load_favorite_tools()
        self.resizeToSuitableWidth(self.moving_btn)
    
    def add_favorite_btn(self,infor):
        title,icon,tool_name,is_add = infor[0],infor[1],infor[2],infor[3]
        if is_add:
            btn = Tradingview_Button(icon,self)
            btn.clicked.connect(self.sent_draw_sig_to_chart)
            self.addWidget(btn)
            tool_infor = {"tool":title,"name":tool_name,"icon":icon.name}
            self.map_btn_drawtool_name[btn] = tool_infor
            self.map_drawtool_btn[title] = btn
        else:
            btn = self.map_drawtool_btn.get(title)
            if btn:
                del self.map_btn_drawtool_name[btn]
                del self.map_drawtool_btn[title]
                self.removeWidget(btn)
                btn.deleteLater()
        self.resizeToSuitableWidth(self.moving_btn)
    
    def load_favorite_tools(self):
        self.list_favorites = AppConfig.get_config_value(f"drawbar.favorite")
        if self.list_favorites == None:
            AppConfig.sig_set_single_data.emit((f"drawbar.favorite",[]))
            self.list_favorites = AppConfig.get_config_value(f"drawbar.favorite")
            return
        if self.list_favorites != []:
            for tool_infor in self.list_favorites:
                title,icon,tool_name = tool_infor["tool"],tool_infor["icon"],tool_infor["name"]
                btn_icon =  FIF.__getitem__(icon)
                self.add_favorite_btn((title,btn_icon,tool_name,True))
    
    def sent_draw_sig_to_chart(self):
        btn = self.sender()
        self.uncheck_btns(btn)
        map_btn_drawtool_name:dict = self.map_btn_drawtool_name[btn]
        tool,tool_name = map_btn_drawtool_name["tool"],map_btn_drawtool_name["name"]
        self.sig_draw_object_name.emit((tool,True,tool_name))
    
    def uncheck_btns(self,cr_btn=None):
        if cr_btn:
            for btn in self.bar._widgets:
                if btn != cr_btn:
                    btn.setChecked(False)
                    btn.set_icon_color()
        else:
            for btn in self.bar._widgets:
                btn.setChecked(False)
                btn.set_icon_color()
    
    def delete(self,ev):
        try:
            ev_pos = ev.position()
        except:
            ev_pos = ev.pos()
        _rect = QRectF(self.x(),self.y(),self.width(),self.height())
        if not _rect.contains(QPoint(ev_pos.x(),ev_pos.y())):
            self.deleteLater()
    
    def resizeToSuitableWidth(self,moving_btn):
        self.bar.resizeToSuitableWidth()
        self.setFixedWidth(self.suitableWidth()+moving_btn.width())
    
    
    def createCheckableMenu(self, pos=None):
        createTimeAction = Action(FIF.CALENDAR, self.tr('Create Date'), checkable=True)
        shootTimeAction = Action(FIF.CAMERA, self.tr('Shooting Date'), checkable=True)
        modifiedTimeAction = Action(FIF.EDIT, self.tr('Modified time'), checkable=True)
        nameAction = Action(FIF.FONT, self.tr('Name'), checkable=True)

        ascendAction =  Action(FIF.UP, self.tr('Ascending'), checkable=True)
        descendAction =  Action(FIF.DOWN, self.tr('Descending'), checkable=True)
        
        
        menu = CheckableMenu(parent=self, indicatorType=MenuIndicatorType.RADIO)

        menu.addActions([
            createTimeAction, shootTimeAction,
            modifiedTimeAction, nameAction
        ])
        menu.addSeparator()
        menu.addActions([ascendAction, descendAction])

        if pos is not None:
            menu.exec(pos, ani=True)

        return menu



