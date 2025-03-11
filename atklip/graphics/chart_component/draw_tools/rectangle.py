from PySide6 import QtCore, QtGui
from PySide6.QtCore import Signal, QObject, Qt,QPointF,QRectF
from PySide6.QtGui import QColor,QPainter,QPicture
from PySide6.QtWidgets import QGraphicsItem

from atklip.graphics.pyqtgraph.Point import Point
from .roi import BaseHandle, SpecialROI, _FiboLineSegment
from atklip.app_utils import mkBrush,mkColor,mkPen

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool
 
class Rectangle(SpecialROI):
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()

    def __init__(self, pos, size=..., angle=0,id=None, invertible=False, maxBounds=None, \
        snapSize=1, scaleSnap=False, translateSnap=False, rotateSnap=False, parent=None, \
            pen=None, hoverPen=None, handlePen=None, handleHoverPen=None, movable=True, \
                rotatable=True, resizable=True, removable=False, aspectLocked=False,drawtool=None):
        super().__init__(pos, size, angle, invertible, maxBounds, snapSize, scaleSnap, \
            translateSnap, rotateSnap, parent, pen, hoverPen, handlePen, handleHoverPen,\
                movable, rotatable, resizable, removable, aspectLocked)
        
        self.drawtool:DrawTool= drawtool
        self.chart:Chart = self.drawtool.chart
        self.name = None
        self.isSelected = False
        self.id = id
        self.reverse = False
        
        self.has = {
            "x_axis_show":True,
            "name": "rectangle",
            "type": "drawtool",
            "id": id,
            "inputs":{
                    },
            "styles":{
                    'pen': pen,
                    'brush': (43, 106, 255, 40),
                    'width': 1,
                    'style': Qt.PenStyle.SolidLine,
                    "lock":True,
                    "setting": False,
                    "delete":True,}
        }
        self.addScaleHandle([0, 0], [1, 1])
        
        self.addScaleHandle([1, 0.5], [0, 0.5])
        self.addScaleHandle([0, 0.5], [1, 0.5])

        ## handles scaling vertically from opposite edge
        self.addScaleHandle([0.5, 0], [0.5, 1])
        self.addScaleHandle([0.5, 1], [0.5, 0])
        ## handles scaling both vertically and horizontally
        self.addScaleHandle([0, 1], [1, 0])
        self.addScaleHandle([1, 0], [0, 1])
        self.addScaleHandle([1, 1], [0, 0])

        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)

        self.lastMousePos = pos
        self.finished = False
        self.h1 = None
        self.h0 = None
        self.last_point = None
        self.picture:QPicture =QPicture()


    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            self.setSelected(True)
            self.change_size_handle(3)
        else:
            self.isSelected = False
            self.setSelected(False)
            self.change_size_handle(4)
       
    def hoverEvent(self, ev: QtCore.QEvent):
        hover = False
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            if not self.locked:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            if not self.isMoving:
                hover = False
                self.setCursor(Qt.CursorShape.CrossCursor)
                
        if not self.isSelected:
            if hover:
                self.setSelected(True)
                ev.acceptClicks(QtCore.Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
                ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
                ev.acceptClicks(QtCore.Qt.MouseButton.MiddleButton)
                self.sigHoverEvent.emit(self)
            else:
                self.setSelected(False)

    def addHandle(self, info, index=None):
        ## If a Handle was not supplied, create it now
        if 'item' not in info or info['item'] is None:
            h = BaseHandle(self.handleSize, typ=info['type'], pen=self.handlePen,
                       hoverPen=self.handleHoverPen, parent=self)
            info['item'] = h
            # info["yoff"] = True
        else:
            h = info['item']
            # info["yoff"] = True
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

    def setPoint(self,pos_x, pos_y):
        if not self.finished:
            if self.drawtool.chart.magnet_on:
                pos_x, pos_y = self.drawtool.get_position_crosshair()
            self.last_point = (pos_x, pos_y)
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
        self.h1 = None
        self.h0 = None
        self.update()


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.update()

    def get_pen_color(self):
        return self.currentPen.color().name()
    
    def get_pen_style(self):
        return self.currentPen.style().name

    def get_pos_point(self):
        pos = self.state["pos"]
        size = self.state["size"]
        if pos.x() < pos.x() + size[0]:
            first_point = [pos.x(), pos.y()]
            second_point = [pos.x() + size[0], pos.y() + size[1]]
        else:
            second_point = [pos.x(), pos.y()]
            first_point = [pos.x() + size[0], pos.y() + size[1]]
        return first_point, second_point
    
    def delete(self):
        "xoa hien thi gia truc y"
        self.price_axis.kwargs["horizontal_ray"].remove(self.id)
        self.deleteLater()


    
    
    
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
        self.change_size_handle(2)

    def unlocked_handle(self):
        self.yoff = False
        self.xoff =False
        self.locked = False
        self.change_size_handle(4)
    
    def change_size_handle(self, size):
        for handle in self.endpoints:
            handle.change_size_handle(size)

    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]

    def boundingRect(self) -> QRectF:
        if self.handles:
            h0 = self.handles[0]['item'].pos()
            h1 = self.handles[-1]['item'].pos()
            if not self.h1:
                self.h1 = h1 
                self.h0 = h0
                self.picture = QPicture()
                painter = QPainter(self.picture)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                painter.setPen(mkPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"]))
                painter.drawRect(QRectF(h1,h0))
                painter.setBrush(mkBrush(self.has["styles"]["brush"]))
                painter.fillRect(QRectF(h1,h0),mkColor(self.has["styles"]["brush"]))
                painter.end()

            elif self.h1 == h1 and self.h0 == h0:
                pass
            else:
                self.h1 = h1 
                self.h0 = h0
                self.picture = QPicture()
                painter = QPainter(self.picture)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                painter.setPen(mkPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"]))
                painter.drawRect(QRectF(h1,h0))
                painter.setBrush(mkBrush(self.has["styles"]["brush"]))
                painter.fillRect(QRectF(h1,h0),mkColor(self.has["styles"]["brush"]))
                painter.end()
        return QRectF(self.picture.boundingRect())
    
    def paint(self, p: QPainter, *args):
        self.picture.play(p)

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
    
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # if not self.boundingRect().contains(ev.pos()): 
            if self.last_point:
                self.on_click.emit(self)
                self.finished = True
                self.drawtool.drawing_object =None
                ev.accept()
        ev.ignore()
        super().mouseClickEvent(ev)

        
       