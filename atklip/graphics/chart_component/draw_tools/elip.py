# import sys
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Signal,Qt,QPointF
from PySide6.QtGui import QPainter
# from numpy.array_api import atan2
from atklip.graphics.pyqtgraph import ROI
import numpy as np
# from atklip.graphics.pyqtgraph import *
import numpy as np

from atklip.app_utils.functions import mkBrush, mkPen
from .roi import SpecialROI
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool

class Ellipse(ROI):
    r"""
    Elliptical ROI subclass with one scale handle and one rotation handle.


    ============== =============================================================
    **Arguments**
    pos            (length-2 sequence) The position of the ROI's origin.
    size           (length-2 sequence) The size of the ROI's bounding rectangle.
    \**args        All extra keyword arguments are passed to ROI()
    ============== =============================================================
    
    """
    on_click = Signal(object)
    def __init__(self, pos, size,drawtool, **args):
        self.path = None
        ROI.__init__(self, pos, size, **args)
        
        self.drawtool:DrawTool= drawtool
        self.chart:Chart = self.drawtool.chart
        self.name = None
        self.isSelected = False
        self.finished = False
        self.reverse = False
        
        self.has: dict = {
            "x_axis_show":True,
            "name": "rectangle",
            "type": "drawtool",
            "id": "id",
            "inputs":{
                    },
            "styles":{
                    'pen': "#2962ff",
                    'brush': (43, 106, 255, 40),
                    'width': 1,
                    'style': Qt.PenStyle.SolidLine,
                    "lock":True,
                    "setting": False,
                    "delete":True,}
        }
        
        self.sigRegionChanged.connect(self._clearPath)
        self._addHandles()
        self.yoff = False
        self.xoff = False
        self.locked = False
        
        # self.setFlags(self.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations
        #                | self.GraphicsItemFlag.ItemIsMovable)
    
    def mouseDragEvent(self, ev, axis=None, line=None):
        self.setSelected(True)
        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.drawtool.chart.vb.mouseDragEvent(ev, axis)
        if not self.locked:
            # r_out = self.boundingRect().adjusted(-4,-4,4,4)
            # r_in = self.boundingRect().adjusted(4,4,-4,-4)
            # if r_out.contains(ev.pos()) and not r_in.contains(ev.pos()):
            self._moveStarted()
            return super().mouseDragEvent(ev)
            
        elif self.locked:
            ev.ignore()
        ev.ignore()
    def set_lock(self,btn):
        print(btn,btn.isChecked())
        if btn.isChecked():
            self.locked_handle()
        else:
            self.unlocked_handle()
    def locked_handle(self):
        self.yoff = True
        self.xoff = True
        self.locked = True

    def unlocked_handle(self):
        self.yoff = False
        self.xoff =False
        self.locked = False
    
    def hoverEvent(self, ev: QtCore.QEvent):
        hover = False
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            if not self.locked:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            hover = False
            self.setCursor(Qt.CursorShape.CrossCursor)
    def setPoint(self,pos_x, pos_y):
        if not self.finished:
            if self.drawtool.chart.magnet_on:
                pos_x, pos_y = self.drawtool.get_position_crosshair()
            # self.state['size'] = [pos_x-self.state['pos'][0], pos_y-self.state['pos'][1]]
            # if self.reverse:
            #     self.movePoint(0, QPointF(pos_x, pos_y))
            # else:
            self.movePoint(-1, QPointF(pos_x, pos_y))
            self.stateChanged()
    
    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name

    def get_inputs(self):
        inputs =  {}
        return inputs
    
    def get_styles(self):
        styles =  {"pen":self.has["styles"]["pen"],
                    "brush":self.has["styles"]["brush"],
                    "width":self.has["styles"]["width"],
                    "style":self.has["styles"]["style"],
                    
                    "lock":self.has["styles"]["lock"],
                    "delete":self.has["styles"]["delete"],
                    "setting":self.has["styles"]["setting"],}
        return styles
    
    def update_inputs(self,_input,_source):
        is_update = False
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        self.update()
        # if _input == "pen" or _input == "width" or _input == "style":
        #     self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"])
        # elif _input == "pen":
        #     pass
    
    def _addHandles(self):
        self.addRotateHandle([1.0, 0.5], [0.5, 0.5])
        self.addScaleHandle([0.5*2.**-0.5 + 0.5, 0.5*2.**-0.5 + 0.5], [0.5, 0.5])
            
    def _clearPath(self):
        self.path = None
        
    def paint(self, p:QPainter, opt, widget):
        r = self.boundingRect()
        if r.width() == 0 or r.height() == 0:
            return
        p.setRenderHint(
            QtGui.QPainter.RenderHint.Antialiasing,
            self._antialias
        )
        p.setPen(mkPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"]))
        p.setBrush(mkBrush(self.has["styles"]["brush"]))
        p.scale(r.width(), r.height())## workaround for GL bug
        r = QtCore.QRectF(r.x()/r.width(), r.y()/r.height(), 1,1)
        p.drawEllipse(r)
    
        
    def getArrayRegion(self, arr, img=None, axes=(0, 1), returnMappedCoords=False, **kwds):
        """
        Return the result of :meth:`~pyqtgraph.ROI.getArrayRegion` masked by the
        elliptical shape of the ROI. Regions outside the ellipse are set to 0.

        See :meth:`~pyqtgraph.ROI.getArrayRegion` for a description of the
        arguments.

        Note: ``returnMappedCoords`` is not yet supported for this ROI type.
        """
        # Note: we could use the same method as used by PolyLineROI, but this
        # implementation produces a nicer mask.
        if returnMappedCoords:
           arr, mappedCoords = ROI.getArrayRegion(self, arr, img, axes,
                                                  returnMappedCoords, **kwds)
        else:
           arr = ROI.getArrayRegion(self, arr, img, axes,
                                    returnMappedCoords, **kwds)
        if arr is None or arr.shape[axes[0]] == 0 or arr.shape[axes[1]] == 0:
            if returnMappedCoords:
                return arr, mappedCoords
            else:
                return arr
        w = arr.shape[axes[0]]
        h = arr.shape[axes[1]]

        ## generate an ellipsoidal mask
        mask = np.fromfunction(lambda x,y: np.hypot(((x+0.5)/(w/2.)-1), ((y+0.5)/(h/2.)-1)) < 1, (w, h))
        
        # reshape to match array axes
        if axes[0] > axes[1]:
            mask = mask.T
        shape = [(n if i in axes else 1) for i,n in enumerate(arr.shape)]
        mask = mask.reshape(shape)
        
        if returnMappedCoords:
            return arr * mask, mappedCoords
        else:
            return arr * mask
    
    def shape(self):
        if self.path is None:
            path = QtGui.QPainterPath()
            
            # Note: Qt has a bug where very small ellipses (radius <0.001) do
            # not correctly intersect with mouse position (upper-left and 
            # lower-right quadrants are not clickable).
            #path.addEllipse(self.boundingRect())
            
            # Workaround: manually draw the path.
            br = self.boundingRect()
            center = br.center()
            r1 = br.width() / 2.
            r2 = br.height() / 2.
            theta = np.linspace(0, 2 * np.pi, 24)
            x = center.x() + r1 * np.cos(theta)
            y = center.y() + r2 * np.sin(theta)
            path.moveTo(x[0], y[0])
            for i in range(1, len(x)):
                path.lineTo(x[i], y[i])
            self.path = path
        return self.path

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # if not self.boundingRect().contains(ev.pos()): 
            self.on_click.emit(self)
            self.finished = True
            self.drawtool.drawing_object =None
            ev.accept()
        ev.ignore()
        super().mouseClickEvent(ev)