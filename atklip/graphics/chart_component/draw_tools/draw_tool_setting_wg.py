from typing import TYPE_CHECKING

from atklip.gui.components import MovingParentWG
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.components.setting_element import ColorEditDrawTool,WidthEditDrawTool,StyleEditDrawTool
from atklip.gui.qfluentwidgets.components.widgets.tool_tip import ToolTipFilter,ToolTipPosition

from PySide6.QtWidgets import QWidget

from atklip.gui.qfluentwidgets.common import FluentIcon as FIF
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.qfluentwidgets.components.widgets.command_bar import CommandBarView
from atklip.gui.qfluentwidgets.components.widgets.menu import CheckableMenu, MenuIndicatorType
from atklip.gui.components import Tradingview_Button,Lock_Unlock_Button

from .draw_setting_wg import DrawSettingMenu
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

from PySide6.QtCore import Signal,QSize
from PySide6.QtWidgets import QWidget


class PopUpSettingMenu(CommandBarView):
    sig_mouse_move = Signal(tuple)
    def __init__(self, parent:QWidget=None, tool=None):
        super().__init__(parent)
        self.chart:Chart = parent
        self.chart.sig_remove_all_draw_obj.connect(self.deleteLater)
        self.tool = tool
        self.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.bar.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.hBoxLayout.setSpacing(0)
        self.bar.setSpacing(0)
                       
        self.moving_btn = MovingParentWG(self.chart,self)
        self.moving_btn.setFixedSize(30,30)
        self.hBoxLayout.insertWidget(0,self.moving_btn,0)
        
        self._menu = None
        
        styles = self.tool.get_styles()
                
        if styles:
            for _input in list(styles.keys()):
                    if "pen" in _input:
                        pen = ColorEditDrawTool(self,self.tool, _input)
                        pen.setToolTip("Change pen color")
                        self.add_btn(pen)
                    elif "brush" in _input:
                        brush = ColorEditDrawTool(self,self.tool, _input)
                        brush.setToolTip("Change brush color")
                        self.add_btn(brush)
                        
                    elif "width" in _input:
                        width = WidthEditDrawTool(self,self.tool, _input)
                        width.setToolTip("Change width line")
                        self.add_btn(width)

                    elif "style" in _input:
                        style = StyleEditDrawTool(self,self.tool, _input)
                        style.setToolTip("Change style line")
                        self.add_btn(style)
                    
                    elif "lock" in _input:
                        if styles[_input] == True:
                            lock = Lock_Unlock_Button(FIF.UNLOCK,self)
                            lock.setChecked(self.tool.locked)
                            lock.set_icon_color()
                            lock.setToolTip("Lock object")
                            lock.setFixedSize(30,30)
                            lock.installEventFilter(ToolTipFilter(lock, 3000, ToolTipPosition.TOP))
                            lock.clicked.connect(self.lock_tool)
                            self.add_btn(lock)
                    
                    elif "setting" in _input:
                        if styles[_input] == True:
                            setting = Tradingview_Button(FIF.SETTING,self)
                            setting.setFixedSize(30,30)
                            setting.setIconSize(QSize(30,30))
                            setting.setToolTip("Open setting object")
                            setting.installEventFilter(ToolTipFilter(setting, 3000, ToolTipPosition.TOP))
                            setting.clicked.connect(self.open_tool_setting_menu)
                            self.add_btn(setting)
                        
                    elif "delete" in _input:
                        if styles[_input] == True:
                            delete = Tradingview_Button(FIF.CYCLEBIN,self)
                            delete.setFixedSize(30,30)
                            delete.setIconSize(QSize(30,30))
                            delete.setToolTip("Delete object")
                            delete.installEventFilter(ToolTipFilter(delete, 3000, ToolTipPosition.TOP))
                            delete.clicked.connect(self.delete_tool)
                            self.add_btn(delete)

        self.resizeToSuitableWidth(self.moving_btn)
    
    def open_tool_setting_menu(self):
        if self._menu is None:
            self._menu = DrawSettingMenu(self.tool,self.chart.mainwindow,self.chart)
            _x = self.chart.width()
            _y = self.chart.height()
            x = (_x-self._menu.width())/2
            y = (_y-self._menu.height())/3
            self._menu.move(QPoint(x, y))
            self._menu.show()
        else:
            try:
                self._menu.deleteLater()
                self._menu = None
            except RuntimeError:
                self._menu = DrawSettingMenu(self.tool,self.chart.mainwindow,self.chart)
                _x = self.chart.width()
                _y = self.chart.height()
                x = (_x-self._menu.width())/2
                y = (_y-self._menu.height())/3
                self._menu.move(QPoint(x, y))
                self._menu.show()
        # self.chart.prepareGeometryChange()
        
    
    def lock_tool(self):
        btn = self.sender()
        self.tool.set_lock(btn)
    
    def delete_tool(self):
        self.chart.remove_item(self.tool)
        self.deleteLater()
    
    def add_btn(self,btn):
        self.addWidget(btn)
        self.resizeToSuitableWidth(self.moving_btn)
    
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



