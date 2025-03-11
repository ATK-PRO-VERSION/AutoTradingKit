from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPainterPath
from atklip.graphics.pyqtgraph import PolyLineROI, TextItem, Point, ArrowItem, mkPen

draw_line_color = '#fca326'
epoch_period = 1e30


from ..draw_tools.roi import SpecialROI, _FiboLineSegment

class BasePolyLine(SpecialROI):
    r"""
    Container class for multiple connected LineSegmentROIs.

    This class allows the user to draw paths of multiple line segments.

    ============== =============================================================
    **Arguments**
    positions      (list of length-2 sequences) The list of points in the path.
                   Note that, unlike the handle positions specified in other
                   ROIs, these positions must be expressed in the normal
                   coordinate system of the ROI, rather than (0 to 1) relative
                   to the size of the ROI.
    closed         (bool) if True, an extra LineSegmentROI is added connecting 
                   the beginning and end points.
    \**args        All extra keyword arguments are passed to ROI()
    ============== =============================================================
    
    """
    def __init__(self, positions, closed=False, pos=None, **args):
        
        if pos is None:
            pos = [0,0]
            
        self.closed = closed
        self.segments = []
        SpecialROI.__init__(self, pos, size=[1,1], **args)
        
        self.setPoints(positions)

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
        for h in seg.handles:
            h['item'].setDeletable(True)
            h['item'].setAcceptedMouseButtons(h['item'].acceptedMouseButtons() | Qt.MouseButton.LeftButton) ## have these handles take left clicks too, so that handles cannot be added on top of other handles
        
    def setMouseHover(self, hover):
        ## Inform all the ROI's segments that the mouse is(not) hovering over it
        SpecialROI.setMouseHover(self, hover)
        for s in self.segments:
            s.setParentHover(hover)
          
    def addHandle(self, info, index=None):
        h = SpecialROI.addHandle(self, info, index=index)
        h.sigRemoveRequested.connect(self.removeHandle)
        self.stateChanged(finish=True)
        return h
        
    def segmentClicked(self, segment, ev=None, pos=None): ## pos should be in this item's coordinate system
        if ev is not None:
            pos = segment.mapToParent(ev.pos())
        elif pos is None:
            raise Exception("Either an event or a position must be given.")
        h2 = segment.handles[1]['item']
        
        i = self.segments.index(segment)
        h3 = self.addFreeHandle(pos, index=self.indexOfHandle(h2))
        self.addSegment(h3, h2, index=i+1)
        segment.replaceHandle(h2, h3)
        
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
        self.scene().removeItem(seg)
        
    def checkRemoveHandle(self, h):
        ## called when a handle is about to display its context menu
        if self.closed:
            return len(self.handles) > 3
        else:
            return len(self.handles) > 2
        
    def paint(self, p, *args):
        pass
    
    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        p = QPainterPath()
        if len(self.handles) == 0:
            return p
        p.moveTo(self.handles[0]['item'].pos())
        for i in range(len(self.handles)):
            p.lineTo(self.handles[i]['item'].pos())
        p.lineTo(self.handles[0]['item'].pos())
        return p

    def getArrayRegion(self, *args, **kwds):
        return self._getArrayRegionForArbitraryShape(*args, **kwds)

    def setPen(self, *args, **kwds):
        SpecialROI.setPen(self, *args, **kwds)
        for seg in self.segments:
            seg.setPen(*args, **kwds)

class RangePolyLine(BasePolyLine):     # for date price range
    on_click = Signal(object)

    signal_visible = Signal(bool)
    signal_delete = Signal()
    def __init__(self, vb, chart, *args, **kwargs):
        self.vb = vb # init before parent constructor
        self.chart = chart
        self.texts = []
        self.arrows = []
        self.finished = False
        self.name="Ruler..."
        super().__init__(*args, **kwargs)
        # self.on_click.connect(self.chart.show_popup_setting_tool)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.finished = True
        ev.ignore()

    def setPoint(self, data):
        if not self.finished and data[0]=="drawed_date_price_range":
            pos = self.mapSceneToParent(QPointF(data[1], data[2]))
            print("setLastPoint", pos, data, )
            h0 = self.handles[0]['item'].pos()
            h1 = self.handles[1]['item'].pos()
            print(h0, h1)
            self.movePoint(-1, pos)
            self.stateChanged()

    def setObjectName(self, name):
        self.name = name

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # widget = self.childAt(ev.position().toPoint())
            # print(191, ev.pos().toPoint())
            self.on_click.emit(self)
        ev.ignore()

    def objectName(self):
        return self.name
        
    def addSegment(self, h1, h2, index=None):
        super().addSegment(h1, h2, index)
        text = TextItem(color=draw_line_color)
        text.setZValue(50)
        text.segment = self.segments[-1 if index is None else index]

        # super().addSegment(h1, h2)
        # super().addSegment(h1, h2)
        for seg in self.segments:
            seg.hide()
        self.v_arrow = ArrowItem(angle=90, tipAngle=30, baseAngle=20, headLen=10, tailWidth=1, pen=None, brush=draw_line_color)
        self.h_arrow = ArrowItem(angle=180, tipAngle=30, baseAngle=20, headLen=10, tailWidth=1, pen=None, brush=draw_line_color)
        self.h_arrow.setZValue(50)
        self.v_arrow.setZValue(50)
        self.arrows.append(self.h_arrow)
        self.arrows.append(self.v_arrow)
        self.update_arrows()
        self.v_arrow.show()
        self.h_arrow.show()
        self.vb.addItem(self.h_arrow, ignoreBounds=True)
        self.vb.addItem(self.v_arrow, ignoreBounds=True)
        if index is None:
            self.texts.append(text)
        else:
            self.texts.insert(index, text)
        self.update_text(text)
        self.vb.addItem(text, ignoreBounds=True)

    def removeSegment(self, seg):
        super().removeSegment(seg)
        for text in list(self.texts):
            if text.segment == seg:
                self.vb.removeItem(text)
                self.texts.remove(text)

    def update_text(self, text):
        h0 = text.segment.handles[0]['item']
        h1 = text.segment.handles[1]['item']
        # self.segments
        diff = h1.pos() - h0.pos()
        if diff.y() < 0:
            text.setAnchor((0.5,0))
        else:
            text.setAnchor((0.5,1))
        text.setPos(h1.pos())
        text.setText(_draw_line_segment_text(self, text.segment, h0.pos(), h1.pos()))

    def update_texts(self):
        for text in self.texts:
            self.update_text(text)

    def update_arrows(self):
        h0 = self.handles[0]['item']
        h1 = self.handles[1]['item']
        diff = h1.pos() - h0.pos()
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
        self.h_arrow.setPos(h1.pos().x(), h1.pos().y() - diff.y() /2)
        self.v_arrow.setPos(h1.pos().x() - diff.x() /2, h1.pos().y())

    def movePoint(self, handle, pos, modifiers=Qt.KeyboardModifier, finish=True, coords='parent'):
        super().movePoint(handle, pos, modifiers, finish, coords)
        self.update_texts()
        self.update_arrows()

    def segmentClicked(self, segment, ev=None, pos=None):
        # pos = segment.mapToParent(ev.pos())
        # pos = _clamp_point(self.vb.parent(), pos)
        # super().segmentClicked(segment, pos=pos)
        # self.update_texts()
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        return

    def addHandle(self, info, index=None):
        handle = super().addHandle(info, index)
        # handle.movePoint = partial(_roihandle_move_snap, self.vb, handle.movePoint)
        return handle
    
    def paint(self, p: QPainter, *args):
        # p.setRenderHint(QPainter.Antialiasing)
        # p.drawRect(0, 0 , self.pixelWidth(), self.pixelHeight())
        # p.drawLine(QPointF(0,1), QPointF(1,1))
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        if self.handles:
            h0 = self.handles[0]['item'].pos()
            h1 = self.handles[1]['item'].pos()
            diff = h1 - h0
            p.drawLine(QPointF(h1.x(), h1.y() - diff.y() /2), QPointF(h0.x(), h1.y() - diff.y() /2))
            p.drawLine(QPointF(h1.x() - diff.x() /2, h1.y()), QPointF(h1.x() - diff.x() /2, h0.y()))

            p.setPen(QColor(252, 163, 38, 40))
            p.setBrush(QColor(252, 163, 38, 40))
            # p.drawRect(QRectF(h0, h1))
            p.fillRect(QRectF(h1,h0), QColor(252, 163, 38, 40))


class FinPolyLine(PolyLineROI):     # for ruler
    def __init__(self, vb, *args, **kwargs):
        self.vb = vb # init before parent constructor
        self.texts = []
        self.arrows = []
        self.name="Ruler..."
        super().__init__(*args, **kwargs)

    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name
        
    def addSegment(self, h1, h2, index=None):
        super().addSegment(h1, h2, index)
        text = TextItem(color=draw_line_color)
        text.setZValue(50)
        text.segment = self.segments[-1 if index is None else index]

        # super().addSegment(h1, h2)
        # super().addSegment(h1, h2)
        for seg in self.segments:
            seg.hide()
        self.v_arrow = ArrowItem(angle=90, tipAngle=30, baseAngle=20, headLen=10, tailWidth=1, pen=None, brush=draw_line_color)
        self.h_arrow = ArrowItem(angle=180, tipAngle=30, baseAngle=20, headLen=10, tailWidth=1, pen=None, brush=draw_line_color)
        self.h_arrow.setZValue(50)
        self.v_arrow.setZValue(50)
        self.arrows.append(self.h_arrow)
        self.arrows.append(self.v_arrow)
        self.update_arrows()
        self.v_arrow.show()
        self.h_arrow.show()
        self.vb.addItem(self.h_arrow, ignoreBounds=True)
        self.vb.addItem(self.v_arrow, ignoreBounds=True)
        if index is None:
            self.texts.append(text)
        else:
            self.texts.insert(index, text)
        self.update_text(text)
        self.vb.addItem(text, ignoreBounds=True)

    def removeSegment(self, seg):
        super().removeSegment(seg)
        for text in list(self.texts):
            if text.segment == seg:
                self.vb.removeItem(text)
                self.texts.remove(text)

    def update_text(self, text):
        h0 = text.segment.handles[0]['item']
        h1 = text.segment.handles[1]['item']
        # self.segments
        diff = h1.pos() - h0.pos()
        if diff.y() < 0:
            text.setAnchor((0.5,0))
        else:
            text.setAnchor((0.5,1))
        text.setPos(h1.pos())
        text.setText(_draw_line_segment_text(self, text.segment, h0.pos(), h1.pos()))

    def update_texts(self):
        for text in self.texts:
            self.update_text(text)

    def update_arrows(self):
        h0 = self.handles[0]['item']
        h1 = self.handles[1]['item']
        diff = h1.pos() - h0.pos()
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
        self.h_arrow.setPos(h1.pos().x(), h1.pos().y() - diff.y() /2)
        self.v_arrow.setPos(h1.pos().x() - diff.x() /2, h1.pos().y())

    def movePoint(self, handle, pos, modifiers=Qt.KeyboardModifier, finish=True, coords='parent'):
        super().movePoint(handle, pos, modifiers, finish, coords)
        self.update_texts()
        self.update_arrows()

    def segmentClicked(self, segment, ev=None, pos=None):
        # pos = segment.mapToParent(ev.pos())
        # pos = _clamp_point(self.vb.parent(), pos)
        # super().segmentClicked(segment, pos=pos)
        # self.update_texts()
        return

    def addHandle(self, info, index=None):
        handle = super().addHandle(info, index)
        # handle.movePoint = partial(_roihandle_move_snap, self.vb, handle.movePoint)
        return handle
    
    def paint(self, p: QPainter, *args):
        # p.setRenderHint(QPainter.Antialiasing)
        # p.drawRect(0, 0 , self.pixelWidth(), self.pixelHeight())
        # p.drawLine(QPointF(0,1), QPointF(1,1))
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        if self.handles:
            h0 = self.handles[0]['item'].pos()
            h1 = self.handles[1]['item'].pos()
            diff = h1 - h0
            p.drawLine(QPointF(h1.x(), h1.y() - diff.y() /2), QPointF(h0.x(), h1.y() - diff.y() /2))
            p.drawLine(QPointF(h1.x() - diff.x() /2, h1.y()), QPointF(h1.x() - diff.x() /2, h0.y()))

            p.setPen(QColor(252, 163, 38, 40))
            p.setBrush(QColor(252, 163, 38, 40))
            # p.drawRect(QRectF(h0, h1))
            p.fillRect(QRectF(h1,h0), QColor(252, 163, 38, 40))

class MouseDragHandler(object):
    """Implements default mouse drag behavior for ROI (not for ROI handles).
    """
    def __init__(self, roi):
        self.roi = roi
        self.dragMode = None
        self.startState = None
        self.snapModifier = Qt.KeyboardModifier.ControlModifier
        self.translateModifier = Qt.KeyboardModifier.NoModifier
        self.rotateModifier = Qt.KeyboardModifier.AltModifier
        self.scaleModifier = Qt.KeyboardModifier.ShiftModifier
        self.rotateSpeed = 0.5
        self.scaleSpeed = 1.01

    def mouseDragEvent(self, ev):
        roi = self.roi

        if ev.isStart():
            if ev.button() == Qt.MouseButton.LeftButton:
                roi.setSelected(True)
                mods = ev.modifiers() & ~self.snapModifier
                if roi.translatable and mods == self.translateModifier:
                    self.dragMode = 'translate'
                elif roi.rotatable and mods == self.rotateModifier:
                    self.dragMode = 'rotate'
                elif roi.resizable and mods == self.scaleModifier:
                    self.dragMode = 'scale'
                else:
                    self.dragMode = None
                
                if self.dragMode is not None:
                    roi._moveStarted()
                    self.startPos = roi.mapToParent(ev.buttonDownPos())
                    print(164, self.startPos)
                    self.startState = roi.saveState()
                    self.cursorOffset = roi.pos() - self.startPos
                    ev.accept()
                else:
                    ev.ignore()
            else:
                self.dragMode = None
                ev.ignore()


        if ev.isFinish() and self.dragMode is not None:
            roi._moveFinished()
            return

        # roi.isMoving becomes False if the move was cancelled by right-click
        if not roi.isMoving or self.dragMode is None:
            return

        snap = True if (ev.modifiers() & self.snapModifier) else None
        pos = roi.mapToParent(ev.pos())
        if self.dragMode == 'translate':
            newPos = pos + self.cursorOffset
            roi.translate(newPos - roi.pos(), snap=snap, finish=False)
        elif self.dragMode == 'rotate':
            diff = self.rotateSpeed * (ev.scenePos() - ev.buttonDownScenePos()).x()
            angle = self.startState['angle'] - diff
            roi.setAngle(angle, centerLocal=ev.buttonDownPos(), snap=snap, finish=False)
        elif self.dragMode == 'scale':
            diff = self.scaleSpeed ** -(ev.scenePos() - ev.buttonDownScenePos()).y()
            roi.setSize(Point(self.startState['size']) * diff, centerLocal=ev.buttonDownPos(), snap=snap, finish=False)


def _draw_line_segment_text(polyline, segment, pos0, pos1):
    diff = pos1 - pos0
    fsecs = abs(diff.x()) #*epoch_period)
    secs = int(fsecs)
    mins = secs//60
    hours = mins//60
    mins = mins%60
    secs = secs%60
    if hours==0 and mins==0 and secs < 60: # and   < 1:
        msecs = int((fsecs-int(fsecs))*1000)
        ts = '%0.2i:%0.2i.%0.3i' % (mins, secs, msecs)
    elif hours==0 and mins < 60 and epoch_period < 60:
        ts = '%0.2i:%0.2i:%0.2i' % (hours, mins, secs)
    elif hours < 24:
        ts = '%0.2i:%0.2i' % (hours, mins)
    else:
        days = hours // 24
        hours %= 24
        ts = '%id %0.2i:%0.2i' % (days, hours, mins)
        if ts.endswith(' 00:00'):
            ts = ts.partition(' ')[0]
    # ysc = polyline.vb.yscale
    if 1: # polyline.vb.y_positive:
        # y0,y1 = ysc.xform(pos0.y()), ysc.xform(pos1.y())
        y0,y1 = pos0.y(), pos1.y()
        if y0:
            gain = y1 / y0 - 1
            if gain > 10:
                value = 'x%i' % gain
            else:
                value = '%+.2f %%' % (100 * gain)
        elif not y1:
            value = '0'
        else:
            value = '+∞' if y1>0 else '-∞'
    else:
        dy = diff.y() # ysc.xform(diff.y())
        if dy and (abs(dy) >= 1e4 or abs(dy) <= 1e-2):
            value = '%+3.3g' % dy
        else:
            value = '%+2.2f' % dy
    extra = _draw_line_extra_text(polyline, segment, pos0, pos1)
    # print(180, value, extra, ts)
    return '%s %s (%s)' % (value, extra, ts)


def _draw_line_extra_text(polyline, segment, pos0, pos1):
    '''Shows the proportions of this line height compared to the previous segment.'''
    prev_text = None
    for text in polyline.texts:
        if prev_text is not None and text.segment == segment:
            h0 = prev_text.segment.handles[0]['item']
            h1 = prev_text.segment.handles[1]['item']
            prev_change = h1.pos().y() - h0.pos().y()
            this_change = pos1.y() - pos0.y()
            if abs(prev_change) <= 1e-14:
                break
            change_part = abs(this_change / prev_change)
            # print(196, change_part)
            return ' = 1:%.2f ' % change_part
        prev_text = text
    return ''


"""
    The yaxis parameter can be one of [False, 'linear', 'log'].'''
"""