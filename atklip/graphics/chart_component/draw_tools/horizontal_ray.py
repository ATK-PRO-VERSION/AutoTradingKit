
from PySide6 import QtCore
from PySide6.QtCore import QObject, Signal, Qt, QPointF
from PySide6.QtGui import QPainter, QPainterPath, QColor
from atklip.graphics.pyqtgraph import functions as fn, Point, ROI

from .roi import MyLineNoHandleROI, CustomLineSegmentROI

#from components.chart import TradingChart

draw_line_color = '#2962ff'


class HorizontalRayNoHandle(MyLineNoHandleROI):
    """ Use for drawing history base """
    on_click = Signal(object)
    drag_signal = Signal()
    signal_visible = Signal(bool)
    signal_delete = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    
    def __init__(self, positions=None, pen=("#eaeaea"), parent=None):
        super().__init__(positions=positions,pen=pen, movable=False, resizable=False)
        self.chart = parent  # plot mapchart
        # self.on_click.connect(self.chart.main.show_popup_setting_tool)
        self.id = None
        self.isSelected = False
        
        self.dragMode = None
        
        self.startState = None
        self.snapModifier = Qt.KeyboardModifier.ControlModifier
        self.translateModifier = Qt.KeyboardModifier.NoModifier
        self.rotateModifier = Qt.KeyboardModifier.AltModifier
        self.scaleModifier = Qt.KeyboardModifier.ShiftModifier
        self.rotateSpeed = 0.5
        self.scaleSpeed = 1.01
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.deleteLater)

    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            self.setSelected(True)
            self.change_size_handle(3)
        else:
            self.isSelected = False
            self.setSelected(False)
            self.change_size_handle(0)

    def change_size_handle(self, size):
        for handle in self.endpoints:
            handle.change_size_handle(size)

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.update()

    def cancelHandle(self):
        for handle in self.endpoints:
            handle.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def setPen(self, *args, **kwargs):
        """
        Set the pen to use when drawing the ROI shape.
        For arguments, see :func:`mkPen <pyqtgraph.mkPen>`.
        """
        self.pen = fn.mkPen(*args, **kwargs)
        self.currentPen = self.pen
        self.update()
    
    
    def translate(self, *args, **kargs):
        """
        Move the ROI to a new position.
        Accepts either (x, y, snap) or ([x,y], snap) as arguments
        If the ROI is bounded and the move would exceed boundaries, then the ROI
        is moved to the nearest acceptable position instead.
        
        *snap* can be:
        
        =============== ==========================================================================
        None (default)  use self.translateSnap and self.snapSize to determine whether/how to snap
        False           do not snap
        Point(w,h)      snap to rectangular grid with spacing (w,h)
        True            snap using self.snapSize (and ignoring self.translateSnap)
        =============== ==========================================================================
           
        Also accepts *update* and *finish* arguments (see setPos() for a description of these).
        """

        if len(args) == 1:
            pt = args[0]
        else:
            pt = args
            
        newState = self.stateCopy()
        newState['pos'] = newState['pos'] + pt
        
        snap = kargs.get('snap', None)
        if snap is None:
            snap = self.translateSnap
        if snap is not False:
            newState['pos'] = self.getSnapPosition(newState['pos'], snap=snap)
        
        if self.maxBounds is not None:
            r = self.stateRect(newState)
            d = Point(0,0)
            if self.maxBounds.left() > r.left():
                d[0] = self.maxBounds.left() - r.left()
            elif self.maxBounds.right() < r.right():
                d[0] = self.maxBounds.right() - r.right()
            if self.maxBounds.top() > r.top():
                d[1] = self.maxBounds.top() - r.top()
            elif self.maxBounds.bottom() < r.bottom():
                d[1] = self.maxBounds.bottom() - r.bottom()
            newState['pos'] += d
        
        update = kargs.get('update', True)
        finish = kargs.get('finish', True)
        
        #print(newState['pos'])
        
        self.setPos(newState['pos'], update=update, finish=finish)

    def mouseDragEvent(self, ev):
        
        print(self.dragMode)
        
        if ev.isStart():
            if ev.button() == Qt.MouseButton.LeftButton:
                self.setSelected(True)
                mods = ev.modifiers() & ~self.snapModifier
                if self.translatable and mods == self.translateModifier:
                    self.dragMode = 'translate'
                elif self.rotatable and mods == self.rotateModifier:
                    self.dragMode = 'rotate'
                elif self.resizable and mods == self.scaleModifier:
                    self.dragMode = 'scale'
                else:
                    self.dragMode = None
                
                if self.dragMode is not None:
                    self._moveStarted()
                    self.startPos = self.mapToParent(ev.buttonDownPos())
                    self.startState = self.saveState()
                    self.cursorOffset = self.pos() - self.startPos
                    ev.accept()
                else:
                    ev.ignore()
            else:
                self.dragMode = None
                ev.ignore()


        if ev.isFinish() and self.dragMode is not None:
            self._moveFinished()
            return

        # roi.isMoving becomes False if the move was cancelled by right-click
        if not self.isMoving or self.dragMode is None:
            return

        snap = True if (ev.modifiers() & self.snapModifier) else None
        pos = self.mapToParent(ev.pos())
        
        print(self.dragMode, pos, snap)
        
        if self.dragMode == 'translate':
            newPos = pos + self.cursorOffset
            self.translate(newPos - self.pos(), snap=snap, finish=False)
        elif self.dragMode == 'rotate':
            diff = self.rotateSpeed * (ev.scenePos() - ev.buttonDownScenePos()).x()
            angle = self.startState['angle'] - diff
            self.setAngle(angle, centerLocal=ev.buttonDownPos(), snap=snap, finish=False)
        elif self.dragMode == 'scale':
            diff = self.scaleSpeed ** -(ev.scenePos() - ev.buttonDownScenePos()).y()
            self.setSize(Point(self.startState['size']) * diff, centerLocal=ev.buttonDownPos(), snap=snap, finish=False)
        

    def mouseClickEvent(self, ev):
        # if ev.button() == Qt.MouseButton.RightButton and self.isMoving:
        #     ev.accept()
        #     self.cancelMove()
        # if ev.button() == Qt.MouseButton.RightButton and self.contextMenuEnabled():
        #     self.raiseContextMenu(ev)
        #     ev.accept()
        # elif self.acceptedMouseButtons() & ev.button():
        #     ev.accept()
        #     self.sigClicked.emit(self, ev)
        
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        # else:
        ev.ignore()
             
    # def mouseEnterEvent(self, ev):
    #     ev.accept()
    #     print("zooo day__________________",ev)
    #     if ev.button() == Qt.MouseButton.LeftButton:
    #         self.on_click.emit(self)
            

    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
        
    def listPoints(self):
        return [p['item'].pos() for p in self.handles]

    def getState(self):
        state = ROI.getState(self)
        state['points'] = [Point(h.pos()) for h in self.getHandles()]
        return state

    def saveState(self):
        state = ROI.saveState(self)
        state['points'] = [tuple(h.pos()) for h in self.getHandles()]
        return state

    def setState(self, state):
        ROI.setState(self, state)
        p1 = [state['points'][0][0]+state['pos'][0], state['points'][0][1]+state['pos'][1]]
        p2 = [state['points'][1][0]+state['pos'][0], state['points'][1][1]+state['pos'][1]]
        
        # print(self.getHandles(), p1, p1)
        
        self.movePoint(self.getHandles()[0], p1, finish=False)
        self.movePoint(self.getHandles()[1], p2)
            
    
    # def paintEvent(self, event):
    #     
    #     self.prepareGeometryChange()
        self.informViewBoundsChanged()
    
    def paint(self, p, *args):
        
        x_range = self.chart.getAxis('bottom').range
        left_xrange = x_range[1]
        
        
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        h1 = self.endpoints[0].pos()
        #h2 = self.endpoints[1].pos()
        h2 = Point(left_xrange, h1.y())
        #print(h1, h2)
        
        p.drawLine(h1, h2)
        
        #self.prepareGeometryChange()
        self.informViewBoundsChanged()
        
    def boundingRect(self):
        return self.shape().boundingRect()
    
    def shape(self):
        
        x_range = self.chart.getAxis('bottom').range
        left_xrange = x_range[1]
        
        p = QPainterPath()
    
        h1 = self.endpoints[0].pos()
        
        h2 = Point(left_xrange, h1.y())
        
        #h2 = self.endpoints[1].pos()
        dh = h2-h1
        if dh.length() == 0:
            return p
        pxv = self.pixelVectors(dh)[1]
        if pxv is None:
            return p
            
        pxv *= 4
        
        p.moveTo(h1+pxv)
        p.lineTo(h2+pxv)
        p.lineTo(h2-pxv)
        p.lineTo(h1-pxv)
        p.lineTo(h1+pxv)
      
        return p
    
    def getArrayRegion(self, data, img, axes=(0,1), order=1, returnMappedCoords=False, **kwds):
        """
        Use the position of this ROI relative to an imageItem to pull a slice 
        from an array.
        
        Since this pulls 1D data from a 2D coordinate system, the return value 
        will have ndim = data.ndim-1
        
        See :meth:`~pyqtgraph.ROI.getArrayRegion` for a description of the
        arguments.
        """
        imgPts = [self.mapToItem(img, h.pos()) for h in self.endpoints]

        d = Point(imgPts[1] - imgPts[0])
        o = Point(imgPts[0])
        rgn = fn.affineSlice(data, shape=(int(d.length()),), vectors=[Point(d.norm())], origin=o, axes=axes, order=order, returnCoords=returnMappedCoords, **kwds)

        return rgn
    
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool

class Horizontal_ray(CustomLineSegmentROI):
    
    on_click = Signal(object)
    drag_signal = Signal()

    signal_visible = Signal(bool)
    signal_delete = Signal()

    
    def __init__(self, positions=None, pen=("#eaeaea"), drawtool=None):
        super().__init__(positions=positions,pen=pen, movable=False, resizable=False)
        
        self.drawtool:DrawTool = drawtool
        self.chart:Chart = self.drawtool.chart  # plot mapchart
        self.vb = self.chart.vb
        self.price_axis = self.chart.getAxis('right')
        self.bottom_axis = self.chart.getAxis('bottom')
        self.isSelected = False
        self.has: dict = {
            "y_axis_show":True,
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
        self.id = None
        
        self.dragMode = None
        self.locked = False
        self.startState = None
        self.snapModifier = Qt.KeyboardModifier.ControlModifier
        self.translateModifier = Qt.KeyboardModifier.NoModifier
        self.rotateModifier = Qt.KeyboardModifier.AltModifier
        self.scaleModifier = Qt.KeyboardModifier.ShiftModifier
        self.rotateSpeed = 0.5
        self.scaleSpeed = 1.01
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

    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name
    
    def get_pos_point(self):
        return self.listPoints()[0]
    
    def get_pen_color(self):
        return self.currentPen.color().name()
    
    def get_pen_style(self):
        return self.currentPen.style().name
    
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

    def cancelHandle(self):
        for handle in self.endpoints:
            handle.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def setPen(self, *args, **kwargs):
        """
        Set the pen to use when drawing the ROI shape.
        For arguments, see :func:`mkPen <pyqtgraph.mkPen>`.
        """
        self.pen = fn.mkPen(*args, **kwargs)
        self.currentPen = self.pen
        self.update()

    def translate(self, *args, **kargs):
        """
        Move the ROI to a new position.
        Accepts either (x, y, snap) or ([x,y], snap) as arguments
        If the ROI is bounded and the move would exceed boundaries, then the ROI
        is moved to the nearest acceptable position instead.
        
        *snap* can be:
        
        =============== ==========================================================================
        None (default)  use self.translateSnap and self.snapSize to determine whether/how to snap
        False           do not snap
        Point(w,h)      snap to rectangular grid with spacing (w,h)
        True            snap using self.snapSize (and ignoring self.translateSnap)
        =============== ==========================================================================
           
        Also accepts *update* and *finish* arguments (see setPos() for a description of these).
        """

        if len(args) == 1:
            pt = args[0]
        else:
            pt = args
            
        newState = self.stateCopy()
        newState['pos'] = newState['pos'] + pt
        
        snap = kargs.get('snap', None)
        if snap is None:
            snap = self.translateSnap
        if snap is not False:
            newState['pos'] = self.getSnapPosition(newState['pos'], snap=snap)
        
        if self.maxBounds is not None:
            r = self.stateRect(newState)
            d = Point(0,0)
            if self.maxBounds.left() > r.left():
                d[0] = self.maxBounds.left() - r.left()
            elif self.maxBounds.right() < r.right():
                d[0] = self.maxBounds.right() - r.right()
            if self.maxBounds.top() > r.top():
                d[1] = self.maxBounds.top() - r.top()
            elif self.maxBounds.bottom() < r.bottom():
                d[1] = self.maxBounds.bottom() - r.bottom()
            newState['pos'] += d
        
        update = kargs.get('update', True)
        finish = kargs.get('finish', True)
        
        #print(newState['pos'])
        
        self.setPos(newState['pos'], update=update, finish=finish)

    def mouseDragEvent(self, ev, axis=None):

        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.vb.mouseDragEvent(ev, axis)
        if not self.locked:
            ev.accept()
            if ev.button() == Qt.MouseButton.LeftButton:
                # self.setSelected(True)
                self._moveStarted()
                self.startPos = ev.buttonDownPos()
                self.startState = self.saveState()
                if ev.isStart():
                    self.cursorOffset = self.get_pos_point() - self.startPos

                newPosX = (ev.pos() + self.mapToView(self.cursorOffset)).x()
                newPosY = ev.pos().y()

                self.movePoint(self.getHandles()[0], QPointF(newPosX, newPosY), finish=False)

            if ev.isFinish():
                self._moveFinished()
                return

        elif self.locked:
            ev.ignore()
        
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        # else:
        ev.ignore()

    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
        
    def listPoints(self):
        return [p['item'].pos() for p in self.handles]

    def getState(self):
        state = ROI.getState(self)
        state['points'] = [Point(h.pos()) for h in self.getHandles()]
        return state

    def saveState(self):
        state = ROI.saveState(self)
        state['points'] = [tuple(h.pos()) for h in self.getHandles()]
        return state

    def setState(self, state):
        ROI.setState(self, state)
        p1 = [state['points'][0][0]+state['pos'][0], state['points'][0][1]+state['pos'][1]]
        p2 = [state['points'][1][0]+state['pos'][0], state['points'][1][1]+state['pos'][1]]
        
        # print(self.getHandles(), p1, p1)
        
        self.movePoint(self.getHandles()[0], p1, finish=False)
        self.movePoint(self.getHandles()[1], p2)
            
    
    # def paintEvent(self, event):
    #     
    #     self.prepareGeometryChange()
        self.informViewBoundsChanged()
    
    def paint(self, p, *args):
        
        x_range = self.bottom_axis.range
        left_xrange = x_range[1]
        
        
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        h1 = self.endpoints[0].pos()
        #h2 = self.endpoints[1].pos()
        h2 = Point(left_xrange, h1.y())
        #print(h1, h2)
        
        p.drawLine(h1, h2)
        
        #self.prepareGeometryChange()
        self.informViewBoundsChanged()
        
    def boundingRect(self):
        return self.shape().boundingRect()
    
    def shape(self):
        
        x_range = self.bottom_axis.range
        left_xrange = x_range[1]
        
        p = QPainterPath()
    
        h1 = self.endpoints[0].pos()
        
        h2 = Point(left_xrange, h1.y())
        
        #h2 = self.endpoints[1].pos()
        dh = h2-h1
        if dh.length() == 0:
            return p
        pxv = self.pixelVectors(dh)[1]
        if pxv is None:
            return p
            
        pxv *= 4
        
        p.moveTo(h1+pxv)
        p.lineTo(h2+pxv)
        p.lineTo(h2-pxv)
        p.lineTo(h1-pxv)
        p.lineTo(h1+pxv)
      
        return p
    
    def getArrayRegion(self, data, img, axes=(0,1), order=1, returnMappedCoords=False, **kwds):
        """
        Use the position of this ROI relative to an imageItem to pull a slice 
        from an array.
        
        Since this pulls 1D data from a 2D coordinate system, the return value 
        will have ndim = data.ndim-1
        
        See :meth:`~pyqtgraph.ROI.getArrayRegion` for a description of the
        arguments.
        """
        imgPts = [self.mapToItem(img, h.pos()) for h in self.endpoints]

        d = Point(imgPts[1] - imgPts[0])
        o = Point(imgPts[0])
        rgn = fn.affineSlice(data, shape=(int(d.length()),), vectors=[Point(d.norm())], origin=o, axes=axes, order=order, returnCoords=returnMappedCoords, **kwds)

        return rgn
    
