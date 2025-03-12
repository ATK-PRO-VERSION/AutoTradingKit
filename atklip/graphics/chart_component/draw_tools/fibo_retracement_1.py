from PySide6 import QtCore, QtGui
from PySide6.QtCore import Signal, QObject, Qt,QPointF,QRectF
from PySide6.QtGui import QColor,QPainter,QPicture
from PySide6.QtWidgets import QGraphicsItem

from atklip.graphics.pyqtgraph.Point import Point
from .roi import BaseHandle, SpecialROI, _FiboLineSegment
from atklip.app_utils import mkBrush,mkColor,mkPen
from .model_draw_tool import Line
from typing import TYPE_CHECKING, List
from .base_textitem import BaseTextItem
from atklip.graphics.pyqtgraph import TextItem
from atklip.app_utils.calculate import cal_line_price_fibo

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool
 
class FiboROI(SpecialROI):
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
                
        self.price_precision = f".{self.chart._precision}f"
        
        self.name = None
        self.isSelected = False
        self.id = id
        self.reverse = False
        
        self.has: dict = {
            "x_axis_show":True,
            "name": "rectangle",
            "type": "drawtool",
            "id": id,
            
            "inputs":{
                "data":{
                        -0.146: Line("-0.146",[],None,TextItem("",color=(255, 51, 69, 255), anchor=(1, 0)),(255, 51, 69, 255),QColor(255, 51, 69, 60),True),
                        0: Line("0",[],None,TextItem("",color=(255,152,0,255), anchor=(1, 0)),(255,152,0,255),QColor(255,152,0,60),True),
                        0.236: Line("0.236",[],None,TextItem("",color=(242,54,69,255), anchor=(1, 0)),(242,54,69,255),QColor(242,54,69,60),True),
                        0.382: Line("0.382",[],None,TextItem("",color=(120,123,134,255), anchor=(1, 0)),(120,123,134,255),QColor(120,123,134,60),True),
                        0.5: Line("0.5",[],None,TextItem("",color=(229,115,115,255), anchor=(1, 0)),(229,115,115,255),QColor(229,115,115,60),True),
                        0.618: Line("0.618",[],None,TextItem("",color=(244,142,177,255), anchor=(1, 0)),(244,142,177,255),QColor(244,142,177,60),True),
                        0.786: Line("0.786",[],None,TextItem("", color=(66, 135, 245, 255),anchor=(1, 0)),(66, 135, 245,255),QColor(66, 135, 245,60),True),
                        1.0: Line("1",[],None,TextItem("", color=(180, 0, 0, 255),anchor=(1, 0)),(180, 0, 0, 255),QColor(180, 0, 0, 60),True),
                        1.146: Line("1.146",[],None,TextItem("",color=(255, 51, 69, 255), anchor=(1, 0)),(255, 51, 69, 255),QColor(255, 51, 69, 60),True),
                        }
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
        
        self.addScaleHandle([1, 1], [0, 0])

        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)

        self.lastMousePos = pos
        self.finished = False
        self.h1 = None
        self.h0 = None
        self.last_point = None
        self.picture:QPicture =QPicture()
        
        self.sigRegionChangeStarted.connect(self.drag_change)
        for level in list(self.has["inputs"]["data"].keys()):
            line:Line = self.has["inputs"]["data"][level]
            line.item.setParentItem(self)
            # line.item.setAnchor((1, level))


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
            if self.reverse:
                self.movePoint(-1, QPointF(pos_x, pos_y))
            else:
                self.movePoint(0, QPointF(pos_x, pos_y))
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
                # painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                self.update_text(painter)
                painter.end()

            elif self.h1 == h1 and self.h0 == h0:
                pass
            else:
                self.h1 = h1 
                self.h0 = h0
                self.picture = QPicture()
                painter = QPainter(self.picture)
                # painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                self.update_text(painter)
                painter.end()
            return QRectF(self.picture.boundingRect())
        
        return QRectF(0,0,0,0)
    
    def drag_change(self,obj):
        diff = self.h1 - self.h0
        keys = list(self.has["inputs"]["data"].keys())
        keys.sort()
        for i in range(len(keys)):
            level = keys[i]
            line:Line = self.has["inputs"]["data"][level]
            if line.show:
                textItem:TextItem = line.item
                color = line.color
                brush = line.brush
                pointy = QPointF(self.h1.x(), self.h1.y() - diff.y()*level)
                pointx = QPointF(self.h0.x(), self.h1.y() - diff.y()*level)
                line.pos = [pointx,pointy]
                point = self.mapToParent(pointx)
                price_level =  f"{point.y():{self.price_precision}}"
                text = f"{line.text} ({price_level}) "
                textItem.setText(text)
                
                r = textItem.textItem.boundingRect()
                tl = textItem.textItem.mapToParent(r.topLeft())
                br = textItem.textItem.mapToParent(r.bottomRight())
                offset = (br - tl)
                _y = pointy.y() + offset.y()
                textItem.setPos(Point(pointy.x(),_y))
    
    def update_text(self,painter: QPainter=None):
        diff = self.h1 - self.h0
        keys = list(self.has["inputs"]["data"].keys())
        keys.sort()
        for i in range(len(keys)):
            level = keys[i]
            line:Line = self.has["inputs"]["data"][level]
            if line.show:
                textItem:TextItem = line.item
                color = line.color
                brush = line.brush
                pointy = QPointF(self.h1.x(), self.h1.y() - diff.y()*level)
                pointx = QPointF(self.h0.x(), self.h1.y() - diff.y()*level)
                line.pos = [pointx,pointy]
                point = self.mapToParent(pointx)
                price_level =  f"{point.y():{self.price_precision}}"
                text = f"{line.text} ({price_level}) "
                textItem.setText(text)
                
                r = textItem.textItem.boundingRect()
                tl = textItem.textItem.mapToParent(r.topLeft())
                br = textItem.textItem.mapToParent(r.bottomRight())
                offset = (br - tl)
                
                _y = pointy.y() + offset.y()
                
                textItem.setPos(Point(pointy.x(),_y))
                
                if painter:
                    painter.setPen(mkPen(color=color, width=self.has["styles"]["width"],style=self.has["styles"]["style"]))
                    painter.drawLine(pointx, pointy)
                    
                    if i > 0:
                        pre_level = keys[i-1]
                        pre_item = self.has["inputs"]["data"][pre_level].pos
                        cr_pos = line.pos
                        top_left = pre_item[0]
                        bottom_right = cr_pos[1]
                        painter.setBrush(mkBrush(brush))
                        painter.fillRect(QRectF(top_left,bottom_right),mkColor(brush))
        
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

        
       