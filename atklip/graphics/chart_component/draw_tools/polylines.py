from typing import List
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter,QPicture
from PySide6.QtWidgets import QGraphicsItem
from pyqtgraph import TextItem, Point, ArrowItem, mkPen,mkBrush

from atklip.app_utils.functions import mkColor

draw_line_color = '#2962ff'
epoch_period = 1e30

from .roi import BaseHandle, SpecialROI, _FiboLineSegment
from atklip.app_utils import covert_time_to_sec,percent_caculator,divide_with_remainder


def _draw_line_segment_text(interval,precision,pos0, pos1):
    sec_per_interval = covert_time_to_sec(interval)
    diff = pos1 - pos0
    fsecs = int(abs(diff.x())) #*epoch_period)
    secs = fsecs*sec_per_interval
    
    _min, _sec = divide_with_remainder(secs, 60)
    
    _hour, __min = divide_with_remainder(_min, 60)
    
    _day, __hour = divide_with_remainder(_hour, 24)
    
    if _day == 0:
        _text = '%0.2i:%0.2i' % (_hour, __min)
    else:
        _text = '%id %0.2i:%0.2i' % (_day, __hour, __min)
    
    # ysc = polyline.vb.yscale
    if diff.y() >= 0:
        percent = percent_caculator(pos0.y(), pos1.y())
    else:
        percent = -percent_caculator(pos0.y(), pos1.y())
    return round(diff.y(),precision), percent,fsecs,_text #f'{diff.y()} ({percent}%) \n{fsecs} bars {ts}'

"""
    The yaxis parameter can be one of [False, 'linear', 'log'].'''
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool

class RangePolyLine(SpecialROI):     # for date price range
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    
    def __init__(self, pos, size=..., angle=0, invertible=True, maxBounds=None, snapSize=1, scaleSnap=False, translateSnap=False, rotateSnap=False, parent=None, pen=None, hoverPen=None, handlePen=None, handleHoverPen=None, movable=True, rotatable=True, resizable=True, removable=False, aspectLocked=False, drawtool=None):
        super().__init__(pos, size, angle, invertible, maxBounds, snapSize, scaleSnap, translateSnap, rotateSnap, parent, pen, hoverPen, handlePen, handleHoverPen, movable, rotatable, resizable, removable, aspectLocked)
    
        self.drawtool:DrawTool = drawtool
        self.chart:Chart = self.drawtool.chart
        self.interval = self.chart.interval
        self.precision = self.chart._precision
        
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
        self.handles:List[dict] = []
        
        self.texts = []
        self.arrows = []
        self.finished = False
        self.doubleclick = False
        self.segments = []
        self.isSelected = False
        self.name="Ruler..."
        
        
        self.v_arrow = ArrowItem(angle=90, tipAngle=30, baseAngle=20, headLen=10, tailWidth=1, pen=None, brush=draw_line_color)
        self.h_arrow = ArrowItem(angle=180, tipAngle=30, baseAngle=20, headLen=10, tailWidth=1, pen=None, brush=draw_line_color)
        self.textitem = TextItem("",color=draw_line_color)
        self.v_arrow.setParentItem(self)
        self.h_arrow.setParentItem(self)
        self.textitem.setParentItem(self)
        
        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([1, 1], [0, 0])

        self.h1 = None
        self.h0 = None
        self.last_point = None
        self.picture:QPicture =QPicture()
        try:
            self.addSegment(self.handles[0]['item'], self.handles[1]['item'])
        except:
            import traceback
            traceback.print_exc()

    
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
        self.h1 = None
        self.h0 = None
        self.update()
        # if _input == "pen" or _input == "width" or _input == "style":
        #     self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"])

    
    
    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
    
    def addSegment(self, h1, h2, index=None):
        seg = _FiboLineSegment(handles=(h1, h2), pen=mkPen(color="#9598a1",width= 1,style= Qt.DashLine), hoverPen=self.hoverPen,
                               parent=self, movable=False)
        if index is None:
            self.segments.append(seg)
        else:
            self.segments.insert(index, seg)
        seg.sigClicked.connect(self.segmentClicked)
        seg.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        seg.setZValue(self.zValue()+1)
        # for h in seg.handles:
            # h['item'].setDeletable(True)
            # h['item'].setAcceptedMouseButtons(h['item'].acceptedMouseButtons() | Qt.MouseButton.LeftButton) ## have these handles take left clicks too, so that handles cannot be added on top of other handles
    
    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            # self.setSelected(True)
            self.change_size_handle(3)
        else:
            self.isSelected = False
            # self.setSelected(False)
            self.change_size_handle(4)

    def setSelected(self, s):
        QGraphicsItem.setSelected(self, s)
        #print "select", self, s
        if s:
            [h['item'].show() for h in self.handles]
            [h.show() for h in self.segments]

        else:
            [h['item'].hide() for h in self.handles]
            [h.hide() for h in self.segments]
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
    def hoverEvent(self, ev):
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
                ev.acceptClicks(Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
                ev.acceptClicks(Qt.MouseButton.RightButton)
                ev.acceptClicks(Qt.MouseButton.MiddleButton)
                self.sigHoverEvent.emit(self)
            else:
                self.setSelected(False)
    
    def mouseDragEvent(self, ev, axis=None, line=None):
        self.setSelected(True)
        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.chart.vb.mouseDragEvent(ev, axis)

        if not self.locked and line:
            return super().mouseDragEvent(ev)
        elif self.locked and line:
            ev.ignore()
        ev.ignore()
    
    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.finished = True
        ev.ignore()
    

    def setObjectName(self, name):
        self.name = name

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            if self.last_point:
                ev.accept()
                self.on_click.emit(self)
                self.finished = True
                self.drawtool.drawing_object =None
        ev.ignore()
        super().mouseClickEvent(ev)
    
    def objectName(self):
        return self.name
    
    
    def setPoint(self,pos_x, pos_y):
        if not self.finished:
            if self.drawtool.chart.magnet_on:
                pos_x, pos_y = self.drawtool.get_position_crosshair()
            self.last_point =(pos_x, pos_y)
            self.movePoint(-1, QPointF(pos_x, pos_y))
            self.stateChanged()
    
    def update_text(self):
        h0 = self.handles[0]['item'].pos()
        h1 = self.handles[1]['item'].pos()

        diff = h1 - h0
        # point0 = self.mapFromParent(Point(h0))
        # point1 = self.mapFromParent(Point(h1))
        point0 = self.mapToParent(Point(h0))
        point1 = self.mapToParent(Point(h1))
        
        diff_y, percent,fsecs,ts = _draw_line_segment_text(self.chart.interval,self.chart._precision,point0, point1)
        
        if diff.y() < 0:
            # print("<0")
            self.textitem.setAnchor((0.5,0))
        else:
            self.textitem.setAnchor((0.5,1))
        
        html=f"""<div style="text-align: center"><span style="color: #d1d4dc; font-size: 10pt;">{diff_y} ({percent}%)</span><br><span style="color: #d1d4dc; font-size: 10pt;">{fsecs} bars, {ts}</span></div>"""
        
        self.textitem.setHtml(html)
        
        r = self.textitem.textItem.boundingRect()
        tl = self.textitem.textItem.mapToParent(r.topLeft())
        br = self.textitem.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.textitem.anchor
        
        _pointf = Point(h1.x() - diff.x()/2, h1.y())
        _x = _pointf.x() #+r.width()/2
        
        if diff.y() < 0:
            _y = _pointf.y()-offset.y()/2
        else:
            _y = _pointf.y() + offset.y()/2
        self.textitem.setPos(Point(_x,_y))


    def update_arrows(self):
        h0 = self.handles[0]['item'].pos()
        h1 = self.handles[1]['item'].pos()
        diff = h1 - h0
        _width = abs(diff.x()) 
        _height = abs(diff.y()) #- self.v_arrow.opts["headLen"]
        if diff.y() < 0:
            # print(63, "di xuong")
            self.v_arrow.setStyle(angle=-90)
        else:
            self.v_arrow.setStyle(angle=90)
        if diff.x() > 0:
            # sang phai
            self.h_arrow.setStyle(angle=180)
        else:
            self.h_arrow.setStyle(angle=0)
            # print(66, "di len")
        self.h_arrow.setPos(h1.x(), h1.y() - diff.y() /2)
        self.v_arrow.setPos(h1.x() - diff.x() /2, h1.y())

    def segmentClicked(self, segment, ev=None, pos=None): ## pos should be in this item's coordinate system
        if ev is not None:
            pos = segment.mapToParent(ev.pos())
        elif pos is None:
            raise Exception("Either an event or a position must be given.")
        # h2 = segment.handles[1]['item']
        print(598, pos, self)
        if not self.finished and self.last_point:
            self.finished = True
            self.drawtool.drawing_object =None
            self.on_click.emit(self)

    
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
        # h.mousePressEvent = self.mousePressEvent
        # h.mouseClickEvent = self.mouseClickEvent_Handle
        h.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        return h
    def mouseDoubleClickEvent(self, event) -> None:
        self.drawtool.drawing_object =None
        self.finished = True
        self.doubleclick = True
        self.update()
    
    def mouseClickEvent_Handle(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            if self.last_point != None and (not self.doubleclick):
                self.drawtool.drawing_object =None
                self.finished = True
                self.doubleclick = True
                self.update()
    
    def boundingRect(self) -> QRectF:
        if self.handles:
            h0 = self.handles[0]['item'].pos()
            h1 = self.handles[1]['item'].pos()
            if not self.h1:
                self.h1 = h1 
                self.h0 = h0
                self.picture = QPicture()
                painter = QPainter(self.picture)
                diff = h1 - h0
                painter.setPen(mkPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"]))
                painter.drawLine(QPointF(h1.x(), h1.y() - diff.y() /2), QPointF(h0.x(), h1.y() - diff.y() /2))
                painter.drawLine(QPointF(h1.x() - diff.x() /2, h1.y()), QPointF(h1.x() - diff.x() /2, h0.y()))
                painter.setBrush(mkBrush(self.has["styles"]["brush"]))
                painter.fillRect(QRectF(h1,h0),mkColor(self.has["styles"]["brush"]))
                self.update_arrows()
                self.update_text()
                painter.end()
            elif self.h1 == h1 and self.h0 == h0:
                pass
            else:
                self.picture = QPicture()
                painter = QPainter(self.picture)
                self.h1 = h1 
                self.h0 = h0
                diff = h1 - h0
                painter.setPen(mkPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"]))
                painter.drawLine(QPointF(h1.x(), h1.y() - diff.y() /2), QPointF(h0.x(), h1.y() - diff.y() /2))
                painter.drawLine(QPointF(h1.x() - diff.x() /2, h1.y()), QPointF(h1.x() - diff.x() /2, h0.y()))
                painter.setBrush(mkBrush(self.has["styles"]["brush"]))
                painter.fillRect(QRectF(h1,h0),mkColor(self.has["styles"]["brush"]))
                self.update_arrows()
                self.update_text()
                painter.end()
        return QRectF(self.picture.boundingRect())
    def paint(self, p: QPainter, *args):
            self.picture.play(p)

