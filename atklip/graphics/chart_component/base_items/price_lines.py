from typing import Tuple, TYPE_CHECKING
import numpy as np
from atklip.graphics.pyqtgraph import InfiniteLine,mkColor,mkPen
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsItem

from atklip.controls import OHLCV
from atklip.controls import IndicatorType

class PriceLine(InfiniteLine):
    """Line plot"""
    def __init__(self,angle=0,color="#a0a0a0",width=1,dash=None,style= Qt.DotLine,movable=False,precision=3) -> None:
        labelOpts={'position': 0.98}
        if dash == None:
            pen = mkPen(color=color,width=width,style= style)
        else:
            pen=mkPen(color,width=width,style= style,dash=dash)
        super().__init__(angle=angle,labelOpts=labelOpts, movable=movable, pen=pen)
        self.precision = precision
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsToShape, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemAcceptsInputMethod, False)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def get_yaxis_param(self):
        _value = self.getYPos()
        # if self.precision != None:
        _value = round(_value,self.precision)
        if self.angle == 90:
            _value = None
        return _value,"#363a45"
    
    def get_xaxis_param(self):
        _value = self.getXPos()
        if self.angle == 0:
            _value = None
        return _value,"#363a45"

    def update_data(self,lastcandle):
        # print(type(lastcandle))
        
        if isinstance(lastcandle,list):
            lastcandle:OHLCV=lastcandle[-1]
        _open = lastcandle.open
        _close = lastcandle.close
                
        colorline = '#089981' if _close >= _open else '#f23645'
        self.pen.setColor(mkColor(colorline))
        self.setPos(_close)
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
            
    def update_price_line_indicator(self,lastcandle:list[OHLCV]|float):
        
        colorline = "white"
        if isinstance(lastcandle, list):
            colorline = '#089981' if lastcandle[-1].close >= lastcandle[-1].open else '#f23645'
            self.pen.setColor(mkColor(colorline))
            self.setPos(lastcandle[-1].close)

        elif isinstance(lastcandle, tuple):
            _type,point = lastcandle[0], lastcandle[1]
            
            try:
                self.pen.setColor(mkColor(colorline))
                self.setPos(point)
            except:
                if _type == IndicatorType.MACD:
                    self.pen.setColor(mkColor(colorline))
                    self.setPos(point)
    
                elif _type == IndicatorType.RSI:
                    self.pen.setColor(mkColor(colorline))
                    self.setPos(point)
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
