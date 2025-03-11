# type: ignore
from atklip.graphics.pyqtgraph import PlotItem 
from .axisitem import *
from .viewbox import PlotViewBox
from PySide6.QtWidgets import QGraphicsItem

class ViewPlotItem(PlotItem):
   
    def __init__(self, context, type_chart="trading",parent=None):
        self._context = context
        self.view_box = PlotViewBox(type_chart=type_chart, plotwidget=context)
        super().__init__(parent=parent,viewBox=self.view_box, axisItems={"right":CustomPriceAxisItem(context=self._context,vb=self.view_box, parent=parent ,
                                                                        showValues=True,orientation="right", axisPen="#5b626f", textPen="#5b626f"),
                                                                         "bottom":CustomDateAxisItem(orientation='bottom',context=self._context,vb=self.view_box,
                                                                       showValues=True, axisPen="#5b626f", textPen="#5b626f",**{Axis.TICK_FORMAT: Axis.DATETIME})})
        self.setClipToView(True) 
        self.setDownsampling(auto=True, mode='subsample') #
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsToShape, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemAcceptsInputMethod, False)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape,True)
        self.hideAxis("left")
        self.showAxis("right")
        self.hideButtons()
        # self.showGrid(True,True,1)
