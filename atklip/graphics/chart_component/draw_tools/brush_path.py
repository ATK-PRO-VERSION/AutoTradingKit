from PySide6 import QtCore, QtGui
from PySide6.QtCore import Signal, QObject, Qt
from atklip.graphics.pyqtgraph.Point import Point

from .roi import BaseHandle, SpecialROI,BasePolyLineROI, _PolyLineSegment

translate = QtCore.QCoreApplication.translate



class PathROI(BasePolyLineROI):
    on_click = Signal(object)
    on_Doubleclick = Signal(QObject)
    draw_rec = Signal()
    signal_visible = Signal(bool)
    signal_delete = Signal()


    def __init__(self, positions, closed=False,id=None, pos=None,drawtool=None, pen=None):
        super().__init__(positions, closed, pos)

        self.setPen(pen)
        
        self.uid = None
        self.id = id
        
        self.has: dict = {
            "x_axis_show":True,
            "name": "rectangle",
            "type": "drawtool",
            "id": id,
            "inputs":{
                    },
            "styles":{
                    'pen': pen,
                    'width': 1,
                    'style': Qt.PenStyle.SolidLine,
                    "lock":True,
                    "setting": False,
                    "delete":True,}
        }
        
        self.drawtool=drawtool
        self.chart = self.drawtool.chart
        self.isSelected = False
        self.last_point = None
        self.finished = False
        self.doubleclick = False
        self.yoff = False
        self.xoff =False
        self.locked = False
        
        self._arrow_height = 5
        self._arrow_width = 4

        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)


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
            # self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            hover = False
            # self.setCursor(Qt.CursorShape.CrossCursor)
                
        if not self.isSelected:
            if hover:
                self.setSelected(True)
                ev.acceptClicks(QtCore.Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
                ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
                ev.acceptClicks(QtCore.Qt.MouseButton.MiddleButton)
                self.sigHoverEvent.emit(self)
            else:
                self.setSelected(False)

    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name
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

    def get_pos_point(self):
        res = []
        list_point = self.listPoints()
        for point in list_point:
            res.append((point.x(), point.y()))
        return res

    def get_pen_color(self):
        return self.currentPen.color().name()
    
    def get_pen_style(self):
        return self.currentPen.style().name

    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
    
    def listPoints(self):
        return [p['item'].pos() for p in self.handles]

    def setMouseHover(self, hover):
        ## Inform the ROI that the mouse is(not) hovering over it
        if self.mouseHovering == hover:
            return
        self.mouseHovering = hover
        self._updateHoverColor()
        
    def _updateHoverColor(self):
        pass
    def _makePen(self):
        # Generate the pen color for this ROI based on its current state.
        if self.mouseHovering:
            return self.hoverPen
        else:
            return self.pen

    def setPen(self, *args, **kwds):
        SpecialROI.setPen(self, *args, **kwds)
        for seg in self.segments:
            seg.setPen(*args, **kwds)

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
        if _input == "pen" or _input == "width" or _input == "style":
            self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"])


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.update()
    
    def delete(self):
        "xoa hien thi gia truc y"
        self.deleteLater()

    def mouseDragEvent(self, ev, axis=None, line=None):
        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.chart.vb.mouseDragEvent(ev, axis)
        if not self.locked:
            return super().mouseDragEvent(ev)
        elif self.locked:
            ev.ignore()
        ev.ignore()

    def mouseDoubleClickEvent(self, event) -> None:
        self.drawtool.drawing_object =None
        self.finished = True
        self.doubleclick = True
        lasthandle = self.handles[-1]['item']
        self.removeHandle(lasthandle)
        # self.addArrowAtEnd()
        self.update()
    
    def mouseClickEvent_Handle(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            if self.last_point != None and (not self.doubleclick):
                self.addPoint(self.last_point)
            elif self.last_point != None and self.doubleclick:
                self.on_click.emit(self)
    
    def addFreeHandle(self, pos=None, axes=None, item=None, name=None, index=None):
        """
        Add a new free handle to the ROI. Dragging free handles has no effect
        on the position or shape of the ROI. 
        
        =================== ====================================================
        **Arguments**
        pos                 (length-2 sequence) The position of the handle 
                            relative to the shape of the ROI. A value of (0,0)
                            indicates the origin, whereas (1, 1) indicates the
                            upper-right corner, regardless of the ROI's size.
        item                The Handle instance to add. If None, a new handle
                            will be created.
        name                The name of this handle (optional). Handles are 
                            identified by name when calling 
                            getLocalHandlePositions and getSceneHandlePositions.
        =================== ====================================================
        """
        if pos is not None:
            pos = Point(pos)
        return self.addHandle({'name': name, 'type': 'f', 'pos': pos, 'item': item}, index=index)

    def setPoint(self, pos_x, pos_y):
        if not self.finished:
            if self.chart.magnet_on:
                pos_x, pos_y = self.drawtool.get_position_crosshair()
            point = Point(pos_x, pos_y)
            pos = self.chart.vb.mapViewToScene(point)
            self.last_point = point
            lasthandle = self.handles[-1]['item']
            lasthandle.movePoint(pos)
            self.stateChanged()

    def addSegment(self, h1, h2, index=None):
        seg = _PolyLineSegment(handles=(h1, h2), pen=self.pen, hoverPen=self.hoverPen,
                               parent=self, movable=False)
        if index is None:
            self.segments.append(seg)
        else:
            self.segments.insert(index, seg)
        seg.mouseDragEvent = self.mouseDragEvent
        seg.sigClicked.connect(self.segmentClicked)
        seg.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        seg.setZValue(self.zValue()+1)
        for h in seg.handles:
            h['item'].setDeletable(True)
            h['item'].setAcceptedMouseButtons(h['item'].acceptedMouseButtons() | QtCore.Qt.MouseButton.LeftButton) ## have these handles take left clicks too, so that handles cannot be added on top of other handles
        
    def addPoint(self, point):
        self.addFreeHandle(point)
        self.addSegment(self.handles[-2]['item'], self.handles[-1]['item'])
        self.stateChanged(finish=True)
        self.update()

    def setPoints(self, points, closed=None):
        """
        Set the complete sequence of points displayed by this ROI.
        ============= =========================================================
        **Arguments**
        points        List of (x,y) tuples specifying handle locations to set.
        closed        If bool, then this will set whether the ROI is closed 
                      (the last point is connected to the first point). If
                      None, then the closed mode is left unchanged.
        ============= =========================================================
        """
        if closed is not None:
            self.closed = closed
        self.clearPoints()
        for p in points:
            self.addFreeHandle(p)
        start = -1 if self.closed else 0
        for i in range(start, len(self.handles)-1):
            self.addSegment(self.handles[i]['item'], self.handles[i+1]['item'])
        
    def clearPoints(self):
        """
        Remove all handles and segments.
        """
        while len(self.handles) > 0:
            self.removeHandle(self.handles[0]['item'])
    
    def getState(self):
        state = SpecialROI.getState(self)
        state['closed'] = self.closed
        state['points'] = [Point(h.pos()) for h in self.getHandles()]
        return state

    def saveState(self):
        state = SpecialROI.saveState(self)
        state['closed'] = self.closed
        state['points'] = [tuple(h.pos()) for h in self.getHandles()]
        return state

    def setState(self, state):
        SpecialROI.setState(self, state)
        self.setPoints(state['points'], closed=state['closed'])
        
    def setMouseHover(self, hover):
        ## Inform all the ROI's segments that the mouse is(not) hovering over it
        SpecialROI.setMouseHover(self, hover)
        for s in self.segments:
            s.setParentHover(hover)
          

    def addHandle(self, info, index=None):
        h = SpecialROI.addHandle(self, info, index=index)
        h.sigRemoveRequested.connect(self.removeHandle)
        self.stateChanged(finish=True)
        h.mouseClickEvent = self.mouseClickEvent_Handle
        h.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.update()
        return h
        
    def segmentClicked(self, segment, ev=None, pos=None): ## pos should be in this item's coordinate system
        self.on_click.emit(self)
        
    def indexOfHandle(self, handle):
        """
        Return the index of *handle* in the list of this ROI's handles.
        """
        if isinstance(handle, BaseHandle):
            index = [i for i, info in enumerate(self.handles) if info['item'] is handle]    
            if len(index) == 0:
                raise Exception("Cannot return handle index; not attached to this ROI")
            return index[0]
        else:
            return handle
        
    def removeHandle(self, handle, updateSegments=True):
        SpecialROI.removeHandle(self, handle)
        handle.sigRemoveRequested.disconnect(self.removeHandle)
        
        if not updateSegments:
            return
        segments = handle.rois[:]
        
        if len(segments) == 1:
            self.removeSegment(segments[0])
        elif len(segments) > 1:
            handles = [h['item'] for h in segments[1].handles]
            handles.remove(handle)
            segments[0].replaceHandle(handle, handles[0])
            self.removeSegment(segments[1])
        self.stateChanged(finish=True)

    def removeSegment(self, seg):
        for handle in seg.handles[:]:
            seg.removeHandle(handle['item'])
        self.segments.remove(seg)
        seg.sigClicked.disconnect(self.segmentClicked)
        if self.scene():
            self.scene().removeItem(seg)

    def checkRemoveHandle(self, h):
        ## called when a handle is about to display its context menu
        if self.closed:
            return len(self.handles) > 3
        else:
            return len(self.handles) > 2
    
       
    def paint(self, painter: QtGui.QPainter, option, widget=None):
        pass
      
    
    # def boundingRect(self):
    #     pass
        # return self.shape().boundingRect()

    def shape(self):
        p = QtGui.QPainterPath()
        if len(self.handles) == 0:
            return p
        p.moveTo(self.handles[0]['item'].pos())
        for i in range(len(self.handles)):
            p.lineTo(self.handles[i]['item'].pos())
        p.lineTo(self.handles[0]['item'].pos())
        return p

    def getArrayRegion(self, *args, **kwds):
        return self._getArrayRegionForArbitraryShape(*args, **kwds)
    
    def addArrowAtEnd(self):
        if len(self.handles) >= 2:
            # Get the last two handles
            handle1 = self.handles[-2]['item']
            handle2 = self.handles[-1]['item']
            
            # Calculate the direction of the arrow
            direction = handle2.pos() - handle1.pos()
            direction /= Point(direction).length()
            
            # Calculate the arrowhead points
            arrowhead_length = 10  # You can adjust this value
            p1 = handle2.pos()
            p2 = p1 - direction.rotate(30) * arrowhead_length
            p3 = p1 - direction.rotate(-30) * arrowhead_length
            
            # Add arrowhead handles
            arrowhead_handle1 = self.addFreeHandle(p1)
            arrowhead_handle2 = self.addFreeHandle(p2)
            arrowhead_handle3 = self.addFreeHandle(p3)
            
            # Add a segment for the arrowhead
            self.addSegment(arrowhead_handle1, arrowhead_handle2)
            self.addSegment(arrowhead_handle2, arrowhead_handle3)







