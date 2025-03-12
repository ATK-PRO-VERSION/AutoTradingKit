# import sys
# from numpy.array_api import atan2
from atklip.graphics.pyqtgraph import ROI
from PySide6.QtGui import QPainter,QPicture
from PySide6.QtCore import Signal, Qt,QRectF,QPointF

from atklip.app_utils.functions import mkBrush, mkColor, mkPen
from .roi import BaseHandle
from atklip.graphics.pyqtgraph.graphicsItems.ROI import Handle

class posHandle(Handle):
    def __init__(self, radius, typ=None, pen=(200, 200, 220),
                 hoverPen=(255, 255, 0), parent=None, deletable=False, antialias=True):
        super().__init__(radius, typ, pen,
                 hoverPen, parent, deletable, antialias)
    
    def paint(self, p, opt, widget):
        p.setRenderHints(p.RenderHint.Antialiasing, True)
        p.setPen(mkPen("#2962ff"))
        p.setBrush(mkBrush("#2962ff"))
        p.drawPath(self.shape())

class BaseRect(ROI):
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    def __init__(self, pos, size, centered=False, sideScalers=False,is_short=False,is_long=False, **args):
        ROI.__init__(self, pos, size, **args)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.setFlag(self.GraphicsItemFlag.ItemSendsGeometryChanges,False)
        self.has: dict = {
            "styles":{
                    'pen': None,
                    'brush': mkBrush((43, 106, 255, 40)),
                    'width': 1}
        }
        self.brush = self.has["styles"]['brush']
        self.is_short:bool = is_short
        self.is_long:bool = is_long
        self.handleSize = 5
        self.yoff = False
        self.xoff =False
        self.locked = False
        self.h1 = None
        self.h0 = None
        self.is_size_change = False
        self.picture:QPicture =QPicture()
    
    def addHandle(self, info, index=None):
        ## If a Handle was not supplied, create it now
        if 'item' not in info or info['item'] is None:
            h = posHandle(self.handleSize, typ="r", pen=self.handlePen,
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
    
    def hoverEvent(self, ev):
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            if not self.locked:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)
    
    def set_lock(self,btn):
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
        
    def setBrush(self,brush):
        self.has["styles"]['brush'] = brush
    
    def boundingRect(self):
        if self.handles:
            h0 = self.handles[0]['item'].pos()
            h1 = self.handles[1]['item'].pos()
            
            if not self.h1:
                
                self.h1 = h1 
                self.h0 = h0
                self.picture = QPicture()
                painter = QPainter(self.picture)
                
                r = QRectF(0, 0, self.state['size'][0], self.state['size'][1])#.normalized()
                painter.setRenderHint(
                    QPainter.RenderHint.Antialiasing,
                    self._antialias
                )
                painter.setPen(mkPen(self.has["styles"]['pen']))
                painter.setBrush(self.has["styles"]["brush"])
                painter.translate(r.left(), r.top())
                painter.scale(r.width(), r.height())
                painter.drawRect(0, 0, 1, 1)
                if self.is_long:
                    painter.setPen(mkPen("red",width=1))
                    painter.drawLine(QPointF(0,0), QPointF(1,0))
                if self.is_short:
                    painter.setPen(mkPen("green",width=1))
                    painter.drawLine(QPointF(0,0), QPointF(1,0))
                self.is_size_change = True
                painter.end()

            elif self.h1 == h1 and self.h0 == h0:
                self.is_size_change = False
            else:
                self.picture = QPicture()
                painter = QPainter(self.picture)
                self.h1 = h1 
                self.h0 = h0
                r = QRectF(0, 0, self.state['size'][0], self.state['size'][1])#.normalized()
                painter.setRenderHint(
                    QPainter.RenderHint.Antialiasing,
                    self._antialias
                )
                painter.setPen(mkPen(self.has["styles"]['pen']))
                painter.setBrush(self.has["styles"]["brush"])
                painter.translate(r.left(), r.top())
                painter.scale(r.width(), r.height())
                painter.drawRect(0, 0, 1, 1)
                if self.is_long:
                    painter.setPen(mkPen("red",width=1))
                    painter.drawLine(QPointF(0,0), QPointF(1,0))
                if self.is_short:
                    painter.setPen(mkPen("green",width=1))
                    painter.drawLine(QPointF(0,0), QPointF(1,0))
                self.is_size_change = True
                painter.end()
        return QRectF(0, 0, self.state['size'][0], self.state['size'][1]) #.normalized()
    
    def paint(self, p: QPainter, *args):
        self.picture.play(p)
    
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # if not self.boundingRect().contains(ev.pos()): 
            self.on_click.emit(self)
            self.finished = True
            self.setSelected(True)
            ev.accept()
        ev.ignore()
        super().mouseClickEvent(ev)
    
    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # if not self.boundingRect().contains(ev.pos()): 
            # self.on_click.emit(self)
            self.finished = True
            ev.accept()
        ev.ignore()        
        super().mouseReleaseEvent()