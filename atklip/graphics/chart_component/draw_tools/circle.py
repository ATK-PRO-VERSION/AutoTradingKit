# import sys
# from numpy.array_api import atan2
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Signal,Qt,QPointF
from PySide6.QtGui import QPainter
# from numpy.array_api import atan2
from atklip.graphics.pyqtgraph import ROI
import numpy as np
# from atklip.graphics.pyqtgraph import *
import numpy as np

from atklip.app_utils.functions import mkBrush, mkPen
import numpy as np

from atklip.graphics.pyqtgraph.Point import Point
from atklip.graphics.pyqtgraph.Qt import QtGui
from atklip.graphics.pyqtgraph.graphicsItems.ROI import Handle
from .elip import Ellipse

class Circle(Ellipse):
    r"""
    Circular ROI subclass. Behaves exactly as EllipseROI, but may only be scaled
    proportionally to maintain its aspect ratio.
    
    ============== =============================================================
    **Arguments**
    pos            (length-2 sequence) The position of the ROI's origin.
    size           (length-2 sequence) The size of the ROI's bounding rectangle.
    \**args        All extra keyword arguments are passed to ROI()
    ============== =============================================================
    
    """
    def __init__(self, pos, size=None, radius=None,drawtool=None, **args):
        if size is None:
            if radius is None:
                raise TypeError("Must provide either size or radius.")
            size = (radius*2, radius*2)
        Ellipse.__init__(self, pos, size,drawtool, aspectLocked=True, **args)
        
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
    
    def addHandle(self, info, index=None):
        ## If a Handle was not supplied, create it now
        if 'item' not in info or info['item'] is None:
            h = Handle(self.handleSize, typ=info['type'], pen=self.handlePen,
                       hoverPen=self.handleHoverPen, parent=self, antialias=self._antialias)
            info['item'] = h
        else:
            h = info['item']
            if info['pos'] is None:
                info['pos'] = h.pos()
        h.setPos(info['pos'] * self.state['size'])

        ## connect the handle to this ROI
        #iid = len(self.handles)
        h.connectROI(self)
        if index is None:
            self.handles.append(info)
        else:
            self.handles.insert(index, info)
        
        h.setZValue(self.zValue()+1)
        self.stateChanged()
        return h
    
    def addScaleHandle(self, pos, center, axes=None, item=None, name=None, lockAspect=False, index=None):
        """
        Add a new scale handle to the ROI. Dragging a scale handle allows the
        user to change the height and/or width of the ROI.
        
        =================== ====================================================
        **Arguments**
        pos                 (length-2 sequence) The position of the handle 
                            relative to the shape of the ROI. A value of (0,0)
                            indicates the origin, whereas (1, 1) indicates the
                            upper-right corner, regardless of the ROI's size.
        center              (length-2 sequence) The center point around which 
                            scaling takes place. If the center point has the
                            same x or y value as the handle position, then 
                            scaling will be disabled for that axis.
        item                The Handle instance to add. If None, a new handle
                            will be created.
        name                The name of this handle (optional). Handles are 
                            identified by name when calling 
                            getLocalHandlePositions and getSceneHandlePositions.
        =================== ====================================================
        """
        pos = Point(pos)
        center = Point(center)
        info = {'name': name, 'type': 's', 'center': center, 'pos': pos, 'item': item, 'lockAspect': lockAspect}
        if pos.x() == center.x():
            info['xoff'] = True
        if pos.y() == center.y():
            info['yoff'] = True
        return self.addHandle(info, index=index)
    
    def _addHandles(self):
        self.addScaleHandle([0.5*2.**-0.5 + 0.5, 0.5*2.**-0.5 + 0.5], [0.5, 0.5])
     
