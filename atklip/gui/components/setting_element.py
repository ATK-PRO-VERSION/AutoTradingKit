from typing import List,TYPE_CHECKING

from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import QWidget

from atklip.gui.qfluentwidgets.components.widgets.tool_tip import ToolTipFilter,ToolTipPosition
from .combobox_value_ui import Ui_combobox_value as ComboboxValue
from .single_value_ui import Ui_single_value as SingleValue
from .double_value_ui import Ui_double_value as DoubleValue
from .edit_value_ui import Ui_text_value as TextValue
from .color_value_ui import Ui_color_value as ColorValue
from .checkbox_value_ui import Ui_Form as CheckBoxValue

from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF
from atklip.gui.components._pushbutton import Color_Picker_Button
from atklip.gui.qfluentwidgets.components.widgets import ComboBox
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE
from atklip.controls.ma_type import PD_MAType
from atklip.app_utils import mkPen, mkBrush

"Inputs setting"
class ComboboxEdit(QWidget,ComboboxValue):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(ComboboxEdit,self).__init__(parent)
        self._parent = parent
        self.indicator = indicator
        self._input = _input
        self.setupUi(self)
        self.setFixedHeight(35)
        
    def set_name(self,name):
        self.tittle.setText(name)
    def set_value(self,value):
        self.value.setText(str(value))
    def set_values(self,list_item: List[str]):
        self.addItems(list_item)
    def addItems(self, texts):
        for text in texts:
            if isinstance(text,str):
                self.value.addItem(text)
            elif isinstance(text,tuple):
                self.value.addItem(text[0],text[1])
    def get_index(self):
        return self.value.currentIndex()
    def set_index(self,index):
        self.value.setCurrentIndex(index)
    def set_current_text(self,text):
        self.value.setCurrentText(text)
    def get_current_text(self):
        return self.value.currentText()

class SourceEdit(ComboboxEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None,sources=None):
        super(SourceEdit,self).__init__(parent,indicator, _input)
        
        _sources = list(sources.keys())
        if isinstance(indicator, JAPAN_CANDLE) or isinstance(indicator, HEIKINASHI) or isinstance(indicator, SMOOTH_CANDLE):
            source_name = self.indicator.has["name"]
            index = _sources.index(source_name)
            _sources[0], _sources[index] = _sources[index], _sources[0]
        else:
            inputs = self.indicator.get_inputs()
            if "source" in list(inputs.keys()):
                source = inputs["source"]
                source_name =  source.source_name
                index = _sources.index(source_name)
                _sources[0], _sources[index] = _sources[index], _sources[0]
            
        self.set_values(_sources)
        self.value.currentTextChanged.connect(self.change_source)
        self.setFixedHeight(35)
   
    def change_source(self,_source):
        # self.indicator.has["inputs"][self._input] = self.sources[_source]
        self.indicator.update_inputs(self._input,_source)
        
class TypeEdit(ComboboxEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(TypeEdit,self).__init__(parent,indicator, _input)
        
        list_types = ["open","high","low","close","hl2","hlc3","ohlc4","volume"]
        _inputs = self.indicator.get_inputs()
        _type = _inputs.get("type")
        if _type != None:
            # if _type in list_types:
            list_types.remove(_type)
            list_types.insert(0,_type)
        self.set_values(list_types)
        self.value.currentTextChanged.connect(self.change_type)
        self.setFixedHeight(35)
    def change_type(self,_type):
        """ "open","high","low","close","hl2","hlc3","ohlc4 """
        self.indicator.update_inputs(self._input,_type)


class BandTypeEdit(ComboboxEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(BandTypeEdit,self).__init__(parent,indicator, _input)
        
        list_types = ["Bollinger Bands","Keltner Channel","Donchian Channel"]
        _inputs = self.indicator.get_inputs()
        _type = _inputs.get("band_type")
        if _type != None:
            # if _type in list_types:
            list_types.remove(_type)
            list_types.insert(0,_type)
        self.set_values(list_types)
        self.value.currentTextChanged.connect(self.change_type)
        self.setFixedHeight(35)
    def change_type(self,_type):
        self.indicator.update_inputs(self._input,_type)


class MaTypeEdit(ComboboxEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(MaTypeEdit,self).__init__(parent,indicator, _input)
        
        list_types = ["mamode","macd_type","rsi_ma_type","supertrend_atr_mamode","atr_mamode"]
        
        _inputs = self.indicator.get_inputs()
        
        _type = _inputs.get(_input) 
        _type_name = _type.name
        
        
        self._dict_values = {"SSF":PD_MAType.SSF,
                            "WMA":PD_MAType.WMA,
                            "VIDYA":PD_MAType.VIDYA,
                            "TRIMA":PD_MAType.TRIMA,
                            "TEMA":PD_MAType.TEMA,
                            "T3":PD_MAType.T3,
                            "SWMA":PD_MAType.SWMA,
                            "SMA":PD_MAType.SMA,
                            "SMMA":PD_MAType.SMMA,
                            "SINWMA":PD_MAType.SINWMA,
                            "RMA":PD_MAType.RMA,
                            "PWMA":PD_MAType.PWMA,
                            "MIDPOINT":PD_MAType.MIDPOINT,
                            "LINREG":PD_MAType.LINREG,
                            "HMA":PD_MAType.HMA,
                            "EMA":PD_MAType.EMA,
                            "DEMA":PD_MAType.DEMA,
                            "ZLMA":PD_MAType.ZLMA,
                            "FWMA":PD_MAType.FWMA}
        _ma_type =  PD_MAType.__getitem__(_type_name)
        
        list_types = list(self._dict_values.keys())
        
        list_values = list(self._dict_values.values())
        
        if _ma_type in list_values:
            # if _type_name in list_types:
            list_types.remove(_type_name)
            list_types.insert(0,_type_name)
        self.set_values(list_types)
        self.value.currentTextChanged.connect(self.change_ma_type)
        self.setFixedHeight(35)
    def change_ma_type(self,text):
        self.indicator.update_inputs(self._input,self._dict_values[text])

class MaIntervalEdit(ComboboxEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(MaIntervalEdit,self).__init__(parent,indicator, _input)
        
        list_values = ["1m","3m","5m",
                        "15m","30m","1h",
                        "2h","4h","6h"]
        _inputs = self.indicator.get_inputs()
        interval = _inputs.get("interval")
        # if interval in list_values:
        list_values.remove(interval)
        list_values.insert(0,interval)
        self.set_values(list_values)
        self.value.currentTextChanged.connect(self.change_ma_type)
        self.setFixedHeight(35)
    def change_ma_type(self,text):
        self.indicator.update_inputs(self._input,text)
        
class IntEdit(QWidget,SingleValue):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(IntEdit,self).__init__(parent)
        self._parent = parent
        self.indicator = indicator
        self._input = _input
        self.setupUi(self)
        self.value.setRange(1,1000)
        self.value.setSingleStep(1)
        self.setFixedHeight(35)
    def set_name(self,name):
        self.tittle.setText(name)

    def get_value(self):
        return self.value.value()
    def set_value(self,value:int):
        self.value.setValue(value)


class PeriodEdit(IntEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(PeriodEdit,self).__init__(parent,indicator, _input)
        
        self.setFixedHeight(35)
        _inputs = self.indicator.get_inputs()
        
        _list_inputs = ["base_ema_length","ema_length_1","ema_length_2","ema_length_3",
                        "legs","length","period","ma_period","period_lower","swma_length",
                        "period_upper","k_period","atr_utbot_length","atr_length",
                        "channel_length",
                        "d_period","rsi_period","fast_period","medium_period","slow_period",
                        "ma_smooth_period","n_period","m_period",
                        "signal_period","length_period","n_smooth_period",
                        "smooth_k_period","atr_long_period","ema_long_period",
                        "atr_short_period","ema_short_period","bb_length",
                        "kc_length","mom_length","mom_smooth",
                        "supertrend_length","supertrend_atr_length"]
        
        # if _input in _list_inputs:
        _value = _inputs.get(_input)
        if _value != None:
            self.set_value(_value)
        self.value.valueChanged.connect(self.change_period)
         
    def change_period(self,period):
        """ "open","high","low","close" """
        if period <= 0:
            period = 1
            self.set_value(period)
        self.indicator.update_inputs(self._input,period)


class FloatEdit(QWidget,DoubleValue):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(FloatEdit,self).__init__(parent)
        self.setupUi(self)
        self.value.setDecimals(3)
        self.value.setMinimum(0.000)
        self.value.setSingleStep(0.001)
        self._parent = parent
        self.indicator = indicator
        self._input = _input
        self.value.setRange(-1000000000,1000000000)
        # self.value.setSingleStep(0.1)
        self.setFixedHeight(35)
        self.value.setFixedWidth(150)
    def set_name(self,name):
        self.tittle.setText(name)

    def get_value(self):
        return self.value.value()
    def set_value(self,value:float):
        self.value.setValue(value)


class MultiDevEdit(FloatEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(MultiDevEdit,self).__init__(parent,indicator, _input)
        
        self.setFixedHeight(35)
        _inputs = self.indicator.get_inputs()

        list_vls = ["std_dev_mult","price_low","deviation","supertrend_multiplier"]
        # if _input in list_vls:
        _value = _inputs.get(_input)
        if _value != None:
            self.set_value(_value)
        self.value.valueChanged.connect(self.change_price)

    def change_price(self,price):
        """ "open","high","low","close" """
        self.indicator.has["inputs"][self._input] = price
        self.indicator.update_inputs(self._input,price)


class PriceEdit(FloatEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(PriceEdit,self).__init__(parent,indicator, _input)
        
        self.setFixedHeight(35)
        _inputs = self.indicator.get_inputs()
        
        _ls_inputs = ["price_high","price_low","fast_w_value","medium_w_value","min_price_low","c_mul","mult",
                      "slow_w_value","key_value_long","key_value_short","max_price_high","key_value",
                      "capital","loss_capital","proportion_closed","risk_percentage","kc_scalar","atr_multiplier",
                      "leverage","taker_fee","rsi_price_high","rsi_price_low","bb_std","supertrend_multiplier",
                      "maker_fee","atr_multiplier"]
        
        # if _input in _ls_inputs:
        _value = _inputs.get(_input)
        if _value != None:
            self.set_value(_value)
        self.value.valueChanged.connect(self.change_price)
        

    def change_price(self,price):
        """ "open","high","low","close" """
        self.indicator.has["inputs"][self._input] = price
        self.indicator.update_inputs(self._input,price)

     
class TextEdit(QWidget,TextValue):
    def __init__(self,parent:QWidget=None):
        super(TextEdit,self).__init__(parent)
        self._parent = parent
        self.setupUi(self)
        self.setFixedHeight(35)
    def set_name(self,name):
        self.tittle.setText(name)

    def get_value(self):
        return self.value.text()
    def set_value(self,value:int):
        self.value.setText(value)


class BoolEdit(QWidget,SingleValue):
    def __init__(self,parent:QWidget=None):
        super(BoolEdit,self).__init__(parent)
        self._parent = parent
        self.setupUi(self)
        self.setFixedHeight(35)


"styles setting"
class ColorEdit(QWidget,ColorValue):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(ColorEdit,self).__init__(parent)
        self.setupUi(self)
        self._parent = parent
        self.indicator = indicator
        self._input = _input
        self.setFixedHeight(35)
        self.load_color()
        self.value.colorChanged.connect(self.change_color)
        
    def set_name(self,name):
        self.tittle.setText(name)
    def change_color(self,color):
        if "brush" in self._input:
            color = mkBrush(color)
        self.indicator.has["styles"][self._input] = color
        #print(self._input,color,self.indicator.has["styles"])
        self.indicator.update_styles(self._input)
    def load_color(self):
        _color = self.indicator.has["styles"].get(self._input)
        if isinstance(_color,QBrush):
            _color = _color.color()
        self.value.setColor(_color)

class StyleEdit(ComboboxEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(StyleEdit,self).__init__(parent,indicator, _input)
        
        self.set_values([("SolidLine",FIF.LINE),("DashLine",FIF.DASH_LINE),("DotLine",FIF.DOT_LINE)])
        self.load_style()
        self.value.currentTextChanged.connect(self.change_style)
        self.setFixedHeight(35)

    def change_style(self,text):
        if text == "SolidLine":
            self.indicator.has["styles"][self._input] = Qt.PenStyle.SolidLine
        elif text == "DashLine":
            self.indicator.has["styles"][self._input] = Qt.PenStyle.DashLine
        elif text == "DotLine":
            self.indicator.has["styles"][self._input] = Qt.PenStyle.DotLine
        self.indicator.update_styles(self._input)
    def load_style(self):
        _value = self.indicator.has["styles"].get(self._input)
        if _value == Qt.PenStyle.SolidLine:
            self.value.setCurrentIndex(0)
        elif _value == Qt.PenStyle.DashLine:
            self.value.setCurrentIndex(1)
        elif _value == Qt.PenStyle.DotLine:
            self.value.setCurrentIndex(2)

    
class WidthEdit(ComboboxEdit):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(WidthEdit,self).__init__(parent,indicator, _input)
        self.set_values([("1px ",FIF.ONE_PIX),("2px ",FIF.TWO_PIX),("3px ",FIF.THREE_PIX),("4px ",FIF.FOUR_PIX)])
        self.load_value()
        self.value.currentTextChanged.connect(self.change_width)
        self.setFixedHeight(35)
    def change_width(self,text):
        if text == "1px ":
            self.indicator.has["styles"][self._input] = 1
        elif text == "2px ":
            self.indicator.has["styles"][self._input] = 2
        elif text == "3px ":
            self.indicator.has["styles"][self._input] = 3
        elif text == "4px ":
            self.indicator.has["styles"][self._input] = 4
        self.indicator.update_styles(self._input)
    def load_value(self):
        _value = self.indicator.has["styles"].get(self._input)
        if _value == 1:
            self.value.setCurrentIndex(0)
        elif _value == 2:
            self.value.setCurrentIndex(1)
        elif _value == 3:
            self.value.setCurrentIndex(2)
        elif _value == 4:
            self.value.setCurrentIndex(3)


"styles setting"
class ColorEditDrawTool(Color_Picker_Button):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(ColorEditDrawTool,self).__init__(parent=parent,enableAlpha = True)
        self.indicator = indicator
        self._input = _input
        self._parent = parent
        self.indicator = indicator
        self._input = _input
        self.setFixedSize(30,30)
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.TOP))
        self.load_color()
        self.colorChanged.connect(self.change_color)

    def change_color(self,color):
        if "brush" in self._input:
            color = mkBrush(color)
        self.indicator.has["styles"][self._input] = color
        #print(self._input,color,self.indicator.has["styles"])
        self.indicator.update_styles(self._input)
    def load_color(self):
        _color = self.indicator.has["styles"].get(self._input)
        if isinstance(_color,QBrush):
            _color = _color.color()
        self.setColor(_color)

class StyleEditDrawTool(ComboBox):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(StyleEditDrawTool,self).__init__(parent)
        self.indicator = indicator
        self._input = _input
        
        self.set_values([("SolidLine",FIF.LINE),("DashLine",FIF.DASH_LINE),("DotLine",FIF.DOT_LINE)])
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.TOP))
        self.load_style()
        self.currentTextChanged.connect(self.change_style)
        self.setFixedSize(100,30)

    def set_value(self,value):
        self.setText(str(value))
    def set_values(self,list_item: List[str]):
        self.addItems(list_item)
    def addItems(self, texts):
        for text in texts:
            if isinstance(text,str):
                self.addItem(text)
            elif isinstance(text,tuple):
                self.addItem(text[0],text[1])
    
    def change_style(self,text):
        if text == "SolidLine":
            self.indicator.has["styles"][self._input] = Qt.PenStyle.SolidLine
        elif text == "DashLine":
            self.indicator.has["styles"][self._input] = Qt.PenStyle.DashLine
        elif text == "DotLine":
            self.indicator.has["styles"][self._input] = Qt.PenStyle.DotLine
        self.indicator.update_styles(self._input)
    def load_style(self):
        _value = self.indicator.has["styles"].get(self._input)
        if _value == Qt.PenStyle.SolidLine:
            self.setCurrentIndex(0)
        elif _value == Qt.PenStyle.DashLine:
            self.setCurrentIndex(1)
        elif _value == Qt.PenStyle.DotLine:
            self.setCurrentIndex(2)

    
class WidthEditDrawTool(ComboBox):
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(WidthEditDrawTool,self).__init__(parent)
        self.indicator = indicator
        self._input = _input
        self.set_values([("1px ",FIF.ONE_PIX),("2px ",FIF.TWO_PIX),("3px ",FIF.THREE_PIX),("4px ",FIF.FOUR_PIX)])
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.TOP))
        self.load_value()
        self.currentTextChanged.connect(self.change_width)
        self.setFixedSize(60,30)
    
    
    def set_value(self,value):
        self.setText(str(value))
    def set_values(self,list_item: List[str]):
        self.addItems(list_item)
    def addItems(self, texts):
        for text in texts:
            if isinstance(text,str):
                self.addItem(text)
            elif isinstance(text,tuple):
                self.addItem(text[0],text[1])
    
    def change_width(self,text):
        if text == "1px ":
            self.indicator.has["styles"][self._input] = 1
        elif text == "2px ":
            self.indicator.has["styles"][self._input] = 2
        elif text == "3px ":
            self.indicator.has["styles"][self._input] = 3
        elif text == "4px ":
            self.indicator.has["styles"][self._input] = 4
        self.indicator.update_styles(self._input)
    def load_value(self):
        _value = self.indicator.has["styles"].get(self._input)
        if _value == 1:
            self.setCurrentIndex(0)
        elif _value == 2:
            self.setCurrentIndex(1)
        elif _value == 3:
            self.setCurrentIndex(2)
        elif _value == 4:
            self.setCurrentIndex(3)


"styles setting"
class CheckBoxEdit(QWidget,CheckBoxValue):
    from PySide6.QtCore import Qt
    def __init__(self,parent:QWidget=None,indicator=None, _input=None):
        super(CheckBoxEdit,self).__init__(parent)
        self.setupUi(self)
        self._parent = parent
        self.indicator = indicator
        self._input = _input
        self.setFixedHeight(35)
        self.load_state()
        self.value.stateChanged.connect(self.change_value)
        
    def set_name(self,name):
        self.tittle.setText(name)
    def change_value(self,value):
        print(value)
        # self.indicator.update_styles(self._input)
    def load_state(self):
        _inputs = self.indicator.get_inputs()
        is_checked = _inputs.get(self._input,False)
        if is_checked:
            self.value.setCheckState(Qt.CheckState.Checked)