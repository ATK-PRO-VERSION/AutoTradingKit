from typing import TYPE_CHECKING

from atklip.gui.qfluentwidgets.components.container import HWIDGET,VWIDGET
from atklip.gui.components import ScrollInterface,TextButton,MovingWidget,PivotInterface
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.components.setting_element import PeriodEdit,MultiDevEdit,PriceEdit,ColorEdit,WidthEdit,StyleEdit,\
SourceEdit,TypeEdit,MaTypeEdit,MaIntervalEdit,BandTypeEdit,CheckBoxEdit

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
    sig_add_indicator = Signal(object)
    sig_remove_indicator = Signal(object)
    
    def __init__(self,name:str,parent:QWidget=None,indicator=None,chart=None):
        super(BasicMenu,self).__init__(parent)
        self.setObjectName(name)
        self._parent = parent
        self.indicator = indicator
        self.chart:Chart|ViewSubPanel = chart
        self.setSpacing(3)
        self.sig_add_indicator.connect(self.add_Widget, Qt.ConnectionType.AutoConnection)
        self.sig_remove_indicator.connect(self.remove_Widget,Qt.ConnectionType.AutoConnection)
        self.setup_setting_indicator()
        # self.setMaximumHeight(200)
        # self._parent.setFixedHeight(self.height())
    
    def name(self):
        return self.objectName()
    def setup_setting_indicator(self):
        _name = self.name()
        _y_axis_show = self.indicator.has["y_axis_show"]
        if _name == "input":
            _inputs = self.indicator.get_inputs()
            for _input in list(_inputs.keys()):
                if _input == "source":
                    source = SourceEdit(self,self.indicator, _input,self.chart.sources)
                    source.set_name(_input)
                    self.sig_add_indicator.emit(source)
                    continue
                elif _input == "type":
                    if isinstance(_input,str):
                        type_indicator = TypeEdit(self,self.indicator, _input)
                        type_indicator.set_name(_input)
                        self.sig_add_indicator.emit(type_indicator)
                    continue
                
                elif _input == "band_type":
                    if isinstance(_input,str):
                        type_indicator = BandTypeEdit(self,self.indicator, _input)
                        type_indicator.set_name(_input)
                        self.sig_add_indicator.emit(type_indicator)
                    continue
                
                elif _input == "wicks":
                    if isinstance(_input,str):
                        type_indicator = CheckBoxEdit(self,self.indicator, _input)
                        type_indicator.set_name(_input)
                        self.sig_add_indicator.emit(type_indicator)
                    continue
                
                elif  "window" in _input or "period" in _input or "length" in _input or "legs" in _input or "smooth" in _input:
                    period = PeriodEdit(self,self.indicator, _input)
                    period.set_name(_input)
                    self.sig_add_indicator.emit(period)
                    continue
                elif "mamode" in _input or "macd_type" in _input:
                    mamode = MaTypeEdit(self,self.indicator, _input)
                    mamode.set_name(_input)
                    self.sig_add_indicator.emit(mamode)
                    continue
                elif "interval" in _input:
                    interval = MaIntervalEdit(self,self.indicator, _input)
                    interval.set_name(_input)
                    self.sig_add_indicator.emit(interval)
                    continue
                
                elif "price" in _input or "scalar" in _input or "value" in _input or "std" in _input or "mul" in _input:
                    price = PriceEdit(self,self.indicator, _input)
                    price.set_name(_input)
                    self.sig_add_indicator.emit(price)
                    continue
                elif "show" in _input:
                    pass
                elif "indicator_type" in _input:
                    pass
                else:
                    continue
                    period = MultiDevEdit(self._parent,self.indicator,_input)
                    period.set_name(_input)
                    self.sig_add_indicator.emit(period)
                    continue
        elif _name == "style":
            _inputs = self.indicator.get_styles()
            for _input in list(_inputs.keys()):
                if "pen" in _input:
                    pen = ColorEdit(self,self.indicator, _input)
                    pen.set_name(_input)
                    self.sig_add_indicator.emit(pen)
                elif "brush" in _input:
                    brush = ColorEdit(self,self.indicator, _input)
                    brush.set_name(_input)
                    self.sig_add_indicator.emit(brush)
                    
                elif "width" in _input:
                    width = WidthEdit(self,self.indicator, _input)
                    width.set_name(_input)
                    self.sig_add_indicator.emit(width)

                elif "style" in _input:
                    style = StyleEdit(self,self.indicator, _input)
                    style.set_name(_input)
                    self.sig_add_indicator.emit(style)
            
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
    def __init__(self,parent:QWidget=None,indicator=None,chart=None):
        super(SettingWidget, self).__init__(parent)
        self.setFixedWidth(330)
        
        self.indicator = indicator
        self.chart:Chart|ViewSubPanel = chart
        self.setup_setting_indicator()
        
    def setup_setting_indicator(self):
        _inputs = self.indicator.get_inputs()
        _styles = self.indicator.get_styles()
        
        if _inputs != {}:
            self.input_widget = BasicMenu("input",self,self.indicator,self.chart)
            self.addSubInterface(self.input_widget, 'Inputs', self.tr('Inputs'))

        if _styles!= {}:
            self.style_widget = BasicMenu("style",self,self.indicator,self.chart)
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

class IndicatorSettingMenu(MovingWidget):
    def __init__(self,indicator,parent:QWidget=None,chart=None):
        super(IndicatorSettingMenu, self).__init__(parent,f"Setting {indicator.has["name"]}")
        self.title.btn_close.clicked.connect(self.deleteLater,Qt.ConnectionType.AutoConnection)
        "change title"
        indicator.sig_change_indicator_name.connect(self.change_title,Qt.ConnectionType.AutoConnection)
        
        self.chart:Chart|ViewSubPanel = chart
        
        self.chart.mouse_clicked_signal.connect(self.delete)
        menu =  SettingWidget(self,indicator,self.chart)
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



