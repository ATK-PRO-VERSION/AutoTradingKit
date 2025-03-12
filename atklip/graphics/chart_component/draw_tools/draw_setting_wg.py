from typing import TYPE_CHECKING

from atklip.gui.qfluentwidgets.components.container import HWIDGET,VWIDGET
from atklip.gui.components import ScrollInterface,TextButton,MovingWidget,PivotInterface
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.components.setting_element import PeriodEdit,MultiDevEdit,PriceEdit,ColorEdit,WidthEdit,StyleEdit,\
SourceEdit,TypeEdit,MaTypeEdit,MaIntervalEdit

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.sub_panel_indicator import ViewSubPanel

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget


class SettingButton(VWIDGET):
    def __init__(self,parent:QWidget=None):
        super(SettingButton, self).__init__(parent)
        self._parent = parent
        
        self._hwidget = HWIDGET(self)
        
        self.btn_ok = TextButton("OK",self,None)
        self.btn_ok.setFixedSize(80,35)
        self.btn_ok.clicked.connect(self._onGotoClicked)

        self.btn_cancel = TextButton("Cancel",self,None)
        self.btn_cancel.setFixedSize(80,35)
        self.btn_cancel.clicked.connect(self._onCancelClicked)
        
        self.btn_save = TextButton("Save",self,None)
        self.btn_save.setFixedSize(80,35)
        self.btn_save.clicked.connect(self._onGotoClicked)
        # self.setSpacing(5)
        # self.setContentsMargins(0,0,0,0)
        # self.addSpacer()
        self.addSeparator(_type = "HORIZONTAL",w=330,h=2)
        self._hwidget.addWidget(self.btn_save)
        self._hwidget.addWidget(self.btn_cancel)
        self._hwidget.addWidget(self.btn_ok)
        self._hwidget.setSpacing(5)
        self._hwidget.setContentsMargins(2,2,2,5)
        self.addWidget(self._hwidget)
        self.setFixedHeight(45)
        
    def _onGotoClicked(self):
        self.close()
    def _onCancelClicked(self):
        self.hide()


class BasicMenu(ScrollInterface):
    sig_add_tool = Signal(object)
    sig_remove_tool = Signal(object)
    
    def __init__(self,name:str,parent:QWidget=None,tool=None,chart=None):
        super(BasicMenu,self).__init__(parent)
        self.setObjectName(name)
        self._parent = parent
        self.tool = tool
        self.chart:Chart|ViewSubPanel = chart
        self.setSpacing(3)
        self.sig_add_tool.connect(self.add_Widget, Qt.ConnectionType.AutoConnection)
        self.sig_remove_tool.connect(self.remove_Widget,Qt.ConnectionType.AutoConnection)
        self.setup_setting_tool()
        self._parent.setFixedHeight(self.height())
        
    def name(self):
        return self.objectName()
    def setup_setting_tool(self):
        """_summary_
        {"capital":self.has["inputs"]["capital"],
                   "loss_capital":self.has["inputs"]["loss_capital"],
                    "proportion_closed":self.has["inputs"]["proportion_closed"],
                    "is_risk":self.has["inputs"]["is_risk"],
                    "risk_percentage":self.has["inputs"]["risk_percentage"],
                    "leverage":self.has["inputs"]["leverage"],
                    "taker_fee":self.has["inputs"]["taker_fee"],
                    "maker_fee":self.has["inputs"]["maker_fee"],
                    }
        """
        _name = self.name()
        if _name == "input":
            _inputs = self.tool.get_inputs()
            for _input in list(_inputs.keys()):
                if "capital" in _input:
                    value = PriceEdit(self,self.tool, _input)
                    value.set_name(_input)
                    self.sig_add_tool.emit(value)
                
                elif "loss_capital" in _input:
                    value = PriceEdit(self,self.tool, _input)
                    value.set_name(_input)
                    self.sig_add_tool.emit(value)
                elif "proportion_closed" in _input:
                    value = PriceEdit(self,self.tool, _input)
                    value.set_name(_input)
                    self.sig_add_tool.emit(value)
                elif "risk_percentage" in _input:
                    value = PriceEdit(self,self.tool, _input)
                    value.set_name(_input)
                    self.sig_add_tool.emit(value)
                elif "leverage" in _input:
                    value = PriceEdit(self,self.tool, _input)
                    value.set_name(_input)
                    self.sig_add_tool.emit(value)
                elif "taker_fee" in _input:
                    period = PriceEdit(self._parent,self.tool,_input)
                    period.set_name(_input)
                    self.sig_add_tool.emit(period)
                elif "maker_fee" in _input:
                    period = PriceEdit(self._parent,self.tool,_input)
                    period.set_name(_input)
                    self.sig_add_tool.emit(period)
                elif "legs" in _input:
                    length = PeriodEdit(self,self.tool, _input)
                    length.set_name(_input)
                    self.sig_add_tool.emit(length)
           
        elif _name == "style":
            _inputs = self.tool.get_styles()
            for _input in list(_inputs.keys()):
                if "pen" in _input:
                    pen = ColorEdit(self,self.tool, _input)
                    pen.set_name(_input)
                    self.sig_add_tool.emit(pen)
                elif "brush" in _input:
                    brush = ColorEdit(self,self.tool, _input)
                    brush.set_name(_input)
                    self.sig_add_tool.emit(brush)
                    
                elif "width" in _input:
                    width = WidthEdit(self,self.tool, _input)
                    width.set_name(_input)
                    self.sig_add_tool.emit(width)

                elif "style" in _input:
                    style = StyleEdit(self,self.tool, _input)
                    style.set_name(_input)
                    self.sig_add_tool.emit(style)
    
    def add_Widget(self,widget):
        self.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)
        if self.height() < 250:
            _height = self.height() + widget.height()
            # self.view.setFixedHeight(_height)
            self.setFixedHeight(_height)
        # else:
        #     self.setFixedHeight(250)
    def remove_Widget(self,widget):
        self.removeWidget(widget)



class SettingWidget(PivotInterface):
    def __init__(self,parent:QWidget=None,tool=None,chart=None):
        super(SettingWidget, self).__init__(parent)
        self.w = 330
        self.setFixedWidth(self.w)
        self.tool = tool
        self.chart:Chart|ViewSubPanel = chart
        self.setup_setting_tool()
        
    def setup_setting_tool(self):
        _inputs = self.tool.get_inputs()
        _styles = self.tool.get_styles()
        
        if _inputs != {}:
            self.input_widget = BasicMenu("input",self,self.tool,self.chart)
            self.addSubInterface(self.input_widget, 'Inputs', self.tr('Inputs'))

        if _styles!= {}:
            self.style_widget = BasicMenu("style",self,self.tool,self.chart)
            self.addSubInterface(self.style_widget, 'Styles', self.tr('Styles'))
            if _inputs == {}:
                _height_style_widget = self.style_widget.height() 
                self.stackedWidget.setFixedHeight(_height_style_widget)
                self.stackedWidget.setCurrentWidget(self.style_widget)
                self.pivot.setCurrentItem(self.style_widget.objectName())
                self.setFixedHeight(self.stackedWidget.height()+self.pivot.height())
                qrouter.setDefaultRouteKey(self.stackedWidget, self.style_widget.objectName())
            else:
                _height_input_widget = self.input_widget.height() 
                self.stackedWidget.setFixedHeight(_height_input_widget)
                
                self.stackedWidget.setCurrentWidget(self.input_widget)
                self.pivot.setCurrentItem(self.input_widget.objectName())
                self.setFixedHeight(self.stackedWidget.height()+self.pivot.height())
                qrouter.setDefaultRouteKey(self.stackedWidget, self.input_widget.objectName())
                
        else:
            if _inputs != {}:
                _height_input_widget = self.input_widget.height() 
                self.setFixedHeight(_height_input_widget)
                self.stackedWidget.setCurrentWidget(self.input_widget)
                self.pivot.setCurrentItem(self.input_widget.objectName())
                self.setFixedHeight(self.stackedWidget.height()+self.pivot.height())
                qrouter.setDefaultRouteKey(self.stackedWidget, self.input_widget.objectName())
        

class DrawSettingMenu(MovingWidget):
    def __init__(self,tool,parent:QWidget=None,chart=None):
        super(DrawSettingMenu, self).__init__(parent,f"""Setting {tool.has["name"]}""")
        self.title.btn_close.clicked.connect(self.deleteLater,Qt.ConnectionType.AutoConnection)
        "change title"
        # tool.sig_change_tool_name.connect(self.change_title,Qt.ConnectionType.AutoConnection)
        
        self.chart:Chart|ViewSubPanel = chart
        
        self.chart.mouse_clicked_signal.connect(self.delete)
        menu =  SettingWidget(self,tool,self.chart)
        menu.sig_change_widget.connect(self.update_size,Qt.ConnectionType.AutoConnection)
        
        self.addWidget(menu)
        self.w = menu.width()
        
        self.btn_setting = SettingButton(self)
        self.addWidget(self.btn_setting)
        
        _height_widget = menu.stackedWidget.height() + menu.pivot.height()
        menu.sig_change_widget.emit(_height_widget)
        
        FluentStyleSheet.INDICATORMENU.apply(self)
    
    
    def delete(self,ev):
        try:
            ev_pos = ev.position()
        except:
            ev_pos = ev.pos()
        _rect = QRectF(self.x(),self.y(),self.width(),self.height())
        if not _rect.contains(QPoint(ev_pos.x(),ev_pos.y())):
            self.deleteLater()

    def deleteLater(self) -> None:
        return super().deleteLater()
    def update_size(self,height):
        _height = 0
        _height += self.title.height()
        _height +=  height
        _height += self.btn_setting.height()
        self.resize(self.w,_height)
        
    def change_title(self,name):
        title= f"Setting {name}"
        self.title.title.setText(title)



