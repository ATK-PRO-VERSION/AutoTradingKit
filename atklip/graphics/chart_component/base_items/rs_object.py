from pyqtgraph import *
from pyqtgraph import functions as fn
from typing import Tuple, List, Dict
import numpy as np
from numpy import ndarray
from PySide6.QtGui import QPainter, QPainterPath, QKeyEvent, QColor, QTransform,QFont
from PySide6.QtCore import Qt
from pyqtgraph.Point import Point

class RSObject(ROI):
    def __init__(self, pos, size=..., angle=0, invertible=False, maxBounds=None, snapSize=1, scaleSnap=False, translateSnap=False, rotateSnap=False, parent=None, pen=None, hoverPen=None, handlePen=None, handleHoverPen=None, movable=False, rotatable=True, resizable=True, removable=True, aspectLocked=False,type_rs=None):
        super().__init__(pos, size, angle, invertible, maxBounds, snapSize, scaleSnap, translateSnap, rotateSnap, parent, pen, hoverPen, handlePen, handleHoverPen, movable, rotatable, resizable, removable, aspectLocked)
        self.pen_color = pen
        if pen is None:
            self.pen_color = 'white'
        self.type_rs = type_rs
        self.setPen(self.pen_color)
        self.setBrush(self.pen_color)
        self.pass_up = False
        self.pass_down = False
        self.id = None
        self.pos_ = pos
        self.size_ = size
        self.touch_count = 1
        
    def setPen(self, *args, **kwargs):
        self.pen = fn.mkPen(*args, **kwargs)
        self.currentPen = self.pen
        self.update()

    def setBrush(self, *args, **kwargs):
        self.brush = fn.mkBrush(*args, **kwargs)
        self.update()

    def paint(self, p, opt, widget):
        # Note: don't use self.boundingRect here, because subclasses may need to redefine it.
        r = QtCore.QRectF(0, 0, self.state['size'][0], self.state['size'][1]).normalized()
        
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        p.setBrush(self.brush)
        p.translate(r.left(), r.top())
        p.scale(r.width(), r.height())
        p.drawRect(0, 0, 1, 1)
        
        # Set up the font for drawing the text
        font = QFont("Arial", 9, QFont.Bold)
        p.setFont(font)
        
        p.setPen(fn.mkPen("white"))

        text = f"{self.pos()[1]}-{self.pos()[1] + self.size()[1]}"
        # Calculate the text rect and center it in the rectangle
        text_rect = p.boundingRect(QtCore.QRectF(self.pos()[0], self.pos()[1], self.state['size'][0], self.state['size'][1]), Qt.AlignCenter, text)
        # Draw the text
        p.drawText(QtCore.QRectF(self.pos()[0], self.pos()[1], self.state['size'][0], self.state['size'][1]), Qt.AlignCenter, text)
        
    def size(self):
        """Return the size (w,h) of the ROI."""
        return self.getState()['size']
        
    def pos(self):

        return self.getState()['pos']

    def setPos(self, pos, y=None, update=True, finish=True):
 
        if update not in (True, False):
            raise TypeError("update argument must be bool")
        
        if y is None:
            pos = Point(pos)
        else:
            # avoid ambiguity where update is provided as a positional argument
            if isinstance(y, bool):
                raise TypeError("Positional arguments to setPos() must be numerical.")
            pos = Point(pos, y)

        self.state['pos'] = pos
        QtWidgets.QGraphicsItem.setPos(self, pos)
        if update:
            self.stateChanged(finish=finish)
        
    def setSize(self, size, center=None, centerLocal=None, snap=False, update=True, finish=True):
 
        if update not in (True, False):
            raise TypeError("update argument must be bool")
        size = Point(size)
        if snap:
            size[0] = round(size[0] / self.scaleSnapSize) * self.scaleSnapSize
            size[1] = round(size[1] / self.scaleSnapSize) * self.scaleSnapSize

        if centerLocal is not None:
            oldSize = Point(self.state['size'])
            oldSize[0] = 1 if oldSize[0] == 0 else oldSize[0]
            oldSize[1] = 1 if oldSize[1] == 0 else oldSize[1]
            center = Point(centerLocal) / oldSize

        if center is not None:
            center = Point(center)
            c = self.mapToParent(Point(center) * self.state['size'])
            c1 = self.mapToParent(Point(center) * size)
            newPos = self.state['pos'] + c - c1
            self.setPos(newPos, update=False, finish=False)
        
        self.prepareGeometryChange()
        self.state['size'] = size
        if update:
            self.stateChanged(finish=finish)

