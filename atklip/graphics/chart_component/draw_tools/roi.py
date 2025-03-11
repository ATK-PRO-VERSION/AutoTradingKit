from math import atan2, cos, sin

import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import Signal, QPointF, Qt, QCoreApplication, QPoint
from PySide6.QtGui import QPainter, QPainterPath, QTransform
from PySide6.QtWidgets import QMenu
from atklip.app_utils.functions import mkBrush, mkPen
from atklip.graphics.pyqtgraph import functions as fn, LineSegmentROI, ROI, UIGraphicsItem, GraphicsObject
from atklip.graphics.pyqtgraph.Point import Point
from atklip.graphics.pyqtgraph.graphicsItems.ROI import Handle

DEFAULTS_FIBO = [1.0, 0.786, 0.618, 0.5, 0.382, 0.236, 0.0]
DEFAULTS_COLOR = [(120,123,134,200),(242,54,69,200),(255,152,0,200),(76,175,80,200),(8,153,129,200),(0,188,212,200),(120,123,134,200),(41, 98, 255,200),(242, 54, 69, 200),(156,39,176,200),(233, 30, 99,200),(206,147,216,200),(159,168,218,200),(255,204,128,200),
                        (229,115,115,200),(244,142,177,200),(66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200), (66, 135, 245,200)]
LEFT_FAR_TIMESTAMP = 1562990041
RIGHT_FAR_TIMESTAMP = 1783728000
translate = QCoreApplication.translate


class BaseHandle(Handle, UIGraphicsItem):
    """
    Handle represents a single user-interactable point attached to an ROI. They
    are usually created by a call to one of the ROI.add___Handle() methods.
    
    Handles are represented as a square, diamond, or circle, and are drawn with 
    fixed pixel size regardless of the scaling of the view they are displayed in.
    
    Handles may be dragged to change the position, size, orientation, or other
    properties of the ROI they are attached to.
    """
    types = {   ## defines number of sides, start angle for each handle type
        't': (4, np.pi/4),
        'f': (4, np.pi/4), # hinh vuong
        's': (4, 0),       # hinh thoi
        'r': (12, 0),      # hinh tron
        'sr': (12, 0),
        'rf': (12, 0),
    }

    sigClicked = Signal(object, object)   # self, event
    sigRemoveRequested = Signal(object)   # self
    
    def __init__(self, radius, typ="r", pen=(200, 200, 220),
                 hoverPen=(255, 255, 0), parent=None, deletable=False, draggable=True):
        self.rois = []
        self.radius = radius
        self.typ = typ
        self.pen = fn.mkPen(pen)
        self.brush = fn.mkBrush("#363a45")
        self.currentBrush = self.brush
        self.hoverPen = fn.mkPen(hoverPen)
        self.hoverBrush = fn.mkBrush("#363a45")
        self.currentPen = self.pen
        self.pen.setWidth(0)
        self.pen.setCosmetic(True)
        self.isMoving = False
        self.sides, self.startAng = self.types["r"]
        self.buildPath()
        self._shape = None
        self.menu = self.buildMenu()
        self.draggable = draggable
        self.horing = False
        
        UIGraphicsItem.__init__(self, parent=parent)
        self.drawtool = parent
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.deletable = deletable
        if deletable:
            self.setAcceptedMouseButtons(Qt.MouseButton.RightButton)        
        self.setZValue(11)

    def change_size_handle(self, size):
        self.radius = size
        self.buildPath()
        self.update()
        self._updateView()
        self.viewTransformChanged()
            
    def connectROI(self, roi):
        ### roi is the "parent" roi, i is the index of the handle in roi.handles
        self.rois.append(roi)
        
    def disconnectROI(self, roi):
        self.rois.remove(roi)
            
    def setDeletable(self, b):
        self.deletable = b
        if b:
            self.setAcceptedMouseButtons(self.acceptedMouseButtons() | Qt.MouseButton.RightButton)
        else:
            self.setAcceptedMouseButtons(self.acceptedMouseButtons() & ~Qt.MouseButton.RightButton)

    def removeClicked(self):
        self.sigRemoveRequested.emit(self)

    def hoverEvent(self, ev):
        hover = False
        
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            hover = False
            self.setCursor(Qt.CursorShape.CrossCursor)
        
        if not ev.isExit():
            if ev.acceptDrags(Qt.MouseButton.LeftButton):
                hover=True
            for btn in [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton]:
                if (self.acceptedMouseButtons() & btn) and ev.acceptClicks(btn):
                    hover=True
                    
        if hover:
            self.currentPen = self.hoverPen
            self.currentBrush = self.hoverBrush
            self.show()
        else:
            self.currentPen = self.pen
            self.currentBrush = self.brush
            # self.hide()

        self.update()

    def mouseClickEvent(self, ev):
        ## right-click cancels drag
        if ev.button() == Qt.MouseButton.RightButton and self.isMoving:
            self.isMoving = False  ## prevents any further motion
            self.movePoint(self.startPos, finish=True)
            ev.accept()
        elif self.acceptedMouseButtons() & ev.button():
            ev.accept()
            if ev.button() == Qt.MouseButton.RightButton and self.deletable:
                self.raiseContextMenu(ev)
            self.sigClicked.emit(self, ev)
        else:
            ev.ignore()
                
    def buildMenu(self):
        menu = QMenu()
        menu.setTitle(translate("ROI", "Handle"))
        self.removeAction = menu.addAction(translate("ROI", "Remove handle"), self.removeClicked) 
        return menu
        
    def getMenu(self):
        return self.menu

    def raiseContextMenu(self, ev):
        menu = self.scene().addParentContextMenus(self, self.getMenu(), ev)
        
        ## Make sure it is still ok to remove this handle
        removeAllowed = all(r.checkRemoveHandle(self) for r in self.rois)
        self.removeAction.setEnabled(removeAllowed)
        pos = ev.screenPos()
        menu.popup(QPoint(int(pos.x()), int(pos.y())))    

    def mouseDragEvent(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        # if not self.draggable:
        #     return
        ev.accept()
        
        ## Inform ROIs that a drag is happening 
        ##  note: the ROI is informed that the handle has moved using ROI.movePoint
        ##  this is for other (more nefarious) purposes.
        #for r in self.roi:
            #r[0].pointDragEvent(r[1], ev)
            
        if ev.isFinish():
            if self.isMoving:
                for r in self.rois:
                    r.stateChangeFinished()
            self.isMoving = False
            self.currentPen = self.pen
            self.currentBrush = self.brush
            self.update()
        elif ev.isStart():
            for r in self.rois:
                r.handleMoveStarted()
            self.isMoving = True
            self.startPos = self.scenePos()
            self.cursorOffset = self.scenePos() - ev.buttonDownScenePos()
            self.currentPen = self.hoverPen
            self.currentBrush = self.hoverBrush
            self.show()
            
        if self.isMoving:  ## note: isMoving may become False in mid-drag due to right-click.
            pos = ev.scenePos() + self.cursorOffset
            self.currentPen = self.hoverPen
            self.currentBrush = self.hoverBrush
            self.show()
            # if self.parentItem().chart.magnet_on:
            #     position = self.parentItem().chart.get_position_crosshair()
            #     pos = self.parentItem().chart.vb.mapViewToScene(QPointF(position[0],position[1]))
            self.movePoint(pos, ev.modifiers(), finish=False)

    def movePoint(self, pos, modifiers=None, finish=True):
        if modifiers is None:
            modifiers = Qt.KeyboardModifier.NoModifier
        for r in self.rois:
            if not r.checkPointMove(self, pos, modifiers):
                return
        #print "point moved; inform %d ROIs" % len(self.roi)
        # A handle can be used by multiple ROIs; tell each to update its handle position
        for r in self.rois:
            r.movePoint(self, pos, modifiers, finish=finish, coords='scene')
        
    def buildPath(self):
        size = self.radius
        self.path = QPainterPath()
        ang = self.startAng
        dt = 2 * np.pi / self.sides
        for i in range(0, self.sides+1):
            x = size * cos(ang)
            y = size * sin(ang)
            ang += dt
            if i == 0:
                self.path.moveTo(x, y)
            else:
                self.path.lineTo(x, y)            
    
    
    def paint(self, p, opt, widget):
        p.setRenderHints(p.RenderHint.Antialiasing, True)
        p.setPen(mkPen("#2962ff"))
        p.setBrush(mkBrush("#2962ff"))
        p.drawPath(self.shape())
    
            
    def shape(self):
        if self._shape is None:
            s = self.generateShape()
            if s is None:
                return self.path
            self._shape = s
              ## beware--this can cause the view to adjust, which would immediately invalidate the shape.
        return self._shape
    
    def boundingRect(self):
        s1 = self.shape()  # noqa: avoid problems with shape invalidation
        return self.shape().boundingRect()
            
    def generateShape(self):
        dt = self.deviceTransform()
        
        if dt is None:
            self._shape = self.path
            return None
        
        v = dt.map(QPointF(1, 0)) - dt.map(QPointF(0, 0))
        va = atan2(v.y(), v.x())
        
        dti = fn.invertQTransform(dt)
        devPos = dt.map(QPointF(0,0))
        tr = QTransform()
        tr.translate(devPos.x(), devPos.y())
        tr.rotateRadians(va)
        
        return dti.map(tr.map(self.path))
        
    def viewTransformChanged(self):
        GraphicsObject.viewTransformChanged(self)
        self._shape = None  ## invalidate shape, recompute later if requested.
        self.update()

class SmallROI(ROI):
    def __init__(self, *args, **kwargs):
        ROI.__init__(self, *args, **kwargs)
        self.handleSize = 0
        self.point_draggable = True

class MyLineNoHandleROI(SmallROI):
    "dùng cho horizontal roi"
    def __init__(self, positions=(None, None), pos=None, handles=(None,None), point_draggable=True,**args):
        if pos is None:
            pos = [0,0]
            
        SmallROI.__init__(self, pos, [1,1], **args)
        if len(positions) > 2:
            raise Exception("LineSegmentROI must be defined by exactly 2 positions. For more points, use PolyLineROI.")
        
        for i, p in enumerate(positions):
            self.addFreeHandle(p, item=handles[i])
            
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
        self.movePoint(self.getHandles()[0], p1, finish=False)
        self.movePoint(self.getHandles()[1], p2)
            
    def paint(self, p, *args):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        h1 = self.endpoints[0].pos()
        h2 = self.endpoints[1].pos()
        p.drawLine(h1, h2)
        
    def boundingRect(self):
        return self.shape().boundingRect()
    
    def shape(self):
        p = QPainterPath()
    
        h1 = self.endpoints[0].pos()
        h2 = self.endpoints[1].pos()
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

class SpecialROI(ROI):
    finish_changed = Signal(list)

    def __init__(self, *args, **kwargs):
        ROI.__init__(self, *args, **kwargs)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        self.setFlag(self.GraphicsItemFlag.ItemSendsGeometryChanges,False)
        self.handleSize = 5
        self.yoff = False
        self.xoff = False
        self.locked = False

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
        
    def movePoint(self, handle, pos, modifiers=None, finish=True, coords='parent'):
        ## called by Handles when they are moved. 
        ## pos is the new position of the handle in scene coords, as requested by the handle.
        if modifiers is None:
            modifiers = Qt.KeyboardModifier.NoModifier
        newState = self.stateCopy()
        index = self.indexOfHandle(handle)
        h = self.handles[index]
        p0 = self.mapToParent(h['pos'] * self.state['size'])
        p1 = Point(pos)

        # print("moving ROI", p1)
        
        if coords == 'parent':
            pass
        elif coords == 'scene':
            p1 = self.mapSceneToParent(p1)
        else:
            raise Exception("New point location must be given in either 'parent' or 'scene' coordinates.")

        ## Handles with a 'center' need to know their local position relative to the center point (lp0, lp1)
        if 'center' in h:
            c = h['center']
            cs = c * self.state['size']
            lp0 = self.mapFromParent(p0) - cs
            lp1 = self.mapFromParent(p1) - cs
        
        if h['type'] == 't':
            snap = True if (modifiers & Qt.KeyboardModifier.ControlModifier) else None
            self.translate(p1-p0, snap=snap, update=False)
        
        elif h['type'] == 'f':
            # print(888, self.xoff, self.yoff)
            if self.yoff and self.xoff:
                self.freeHandleMoved = False
            else:
                newPos = self.mapFromParent(p1)
                h['item'].setPos(newPos)
                h['pos'] = newPos
                self.freeHandleMoved = True
            
        elif h['type'] == 's':
            ## If a handle and its center have the same x or y value, we can't scale across that axis.
            if h['center'][0] == h['pos'][0] or self.xoff:
                lp1[0] = 0
            if h['center'][1] == h['pos'][1] or self.yoff:
                lp1[1] = 0
            
            ## snap 
            if self.scaleSnap or (modifiers & Qt.KeyboardModifier.ControlModifier):
                lp1[0] = round(lp1[0] / self.scaleSnapSize) * self.scaleSnapSize
                lp1[1] = round(lp1[1] / self.scaleSnapSize) * self.scaleSnapSize
                
            ## preserve aspect ratio (this can override snapping)
            if h['lockAspect'] or (modifiers & Qt.KeyboardModifier.AltModifier):
                #arv = Point(self.preMoveState['size']) - 
                lp1 = lp1.proj(lp0)
            
            ## determine scale factors and new size of ROI
            hs = h['pos'] - c
            if hs[0] == 0:
                hs[0] = 1
            if hs[1] == 0:
                hs[1] = 1
            newSize = lp1 / hs
            
            ## Perform some corrections and limit checks
            if newSize[0] == 0:
                newSize[0] = newState['size'][0]
            if newSize[1] == 0:
                newSize[1] = newState['size'][1]
            if not self.invertible:
                if newSize[0] < 0:
                    newSize[0] = newState['size'][0]
                if newSize[1] < 0:
                    newSize[1] = newState['size'][1]
            if self.aspectLocked:
                newSize[0] = newSize[1]
            
            ## Move ROI so the center point occupies the same scene location after the scale
            s0 = c * self.state['size']
            s1 = c * newSize
            cc = self.mapToParent(s0 - s1) - self.mapToParent(Point(0, 0))
            
            ## update state, do more boundary checks
            newState['size'] = newSize
            newState['pos'] = newState['pos'] + cc
            if self.maxBounds is not None:
                r = self.stateRect(newState)
                if not self.maxBounds.contains(r):
                    return
            
            self.setPos(newState['pos'], update=False)
            self.setSize(newState['size'], update=False)
        
        elif h['type'] in ['r', 'rf']:
            if h['type'] == 'rf':
                self.freeHandleMoved = True
            
            if not self.rotatable:
                return
            ## If the handle is directly over its center point, we can't compute an angle.
            try:
                if lp1.length() == 0 or lp0.length() == 0:
                    return
            except OverflowError:
                return
            
            ## determine new rotation angle, constrained if necessary
            ang = newState['angle'] - lp0.angle(lp1)
            if ang is None:  ## this should never happen..
                return
            if self.rotateSnap or (modifiers & Qt.KeyboardModifier.ControlModifier):
                ang = round(ang / self.rotateSnapAngle) * self.rotateSnapAngle
            
            ## create rotation transform
            tr = QTransform()
            tr.rotate(ang)
            
            ## move ROI so that center point remains stationary after rotate
            cc = self.mapToParent(cs) - (tr.map(cs) + self.state['pos'])
            newState['angle'] = ang
            newState['pos'] = newState['pos'] + cc
            
            ## check boundaries, update
            if self.maxBounds is not None:
                r = self.stateRect(newState)
                if not self.maxBounds.contains(r):
                    return
            self.setPos(newState['pos'], update=False)
            self.setAngle(ang, update=False)
            
            ## If this is a free-rotate handle, its distance from the center may change.
            
            if h['type'] == 'rf':
                h['item'].setPos(self.mapFromScene(p1))  ## changes ROI coordinates of handle
                h['pos'] = self.mapFromParent(p1)
                
        elif h['type'] == 'sr':
            try:
                if lp1.length() == 0 or lp0.length() == 0:
                    return
            except OverflowError:
                return
            
            ang = newState['angle'] - lp0.angle(lp1)
            if ang is None:
                return
            if self.rotateSnap or (modifiers & Qt.KeyboardModifier.ControlModifier):
                ang = round(ang / self.rotateSnapAngle) * self.rotateSnapAngle

            if self.aspectLocked or h['center'][0] != h['pos'][0]:
                newState['size'][0] = self.state['size'][0] * lp1.length() / lp0.length()
                if self.scaleSnap:  # use CTRL only for angular snap here.
                    newState['size'][0] = round(newState['size'][0] / self.snapSize) * self.snapSize

            if self.aspectLocked or h['center'][1] != h['pos'][1]:
                newState['size'][1] = self.state['size'][1] * lp1.length() / lp0.length()
                if self.scaleSnap:  # use CTRL only for angular snap here.
                    newState['size'][1] = round(newState['size'][1] / self.snapSize) * self.snapSize

            if newState['size'][0] == 0:
                newState['size'][0] = 1
            if newState['size'][1] == 0:
                newState['size'][1] = 1

            c1 = c * newState['size']
            tr = QTransform()
            tr.rotate(ang)
            
            cc = self.mapToParent(cs) - (tr.map(c1) + self.state['pos'])
            newState['angle'] = ang
            newState['pos'] = newState['pos'] + cc
            if self.maxBounds is not None:
                r = self.stateRect(newState)
                if not self.maxBounds.contains(r):
                    return
            
            self.setState(newState, update=False)
        
        self.stateChanged(finish=finish)

    def stateChangeFinished(self):
        self.sigRegionChangeFinished.emit(self)
        self.finish_changed.emit([self.state])
        
class _FiboLineSegment(LineSegmentROI):     # dung de ke line cheo
    # Used internally by PolyLineROI
    on_click = Signal(object)
    def __init__(self, *args, **kwds):
        self._parentHovering = False
        LineSegmentROI.__init__(self, *args, **kwds)
        self._parent = kwds["parent"]
        self.scaleModifier = Qt.KeyboardModifier.NoModifier


    def mouseDragEvent(self, ev):
        return self._parent.mouseDragEvent(ev, line=self)
    
    def setParentHover(self, hover):
        # set independently of own hover state
        if self._parentHovering != hover:
            self._parentHovering = hover
            self._updateHoverColor()
        
    def _makePen(self):
        if self.mouseHovering or self._parentHovering:
            return self.hoverPen
        else:
            return self.pen
        
    def hoverEvent(self, ev):
        # accept drags even though we discard them to prevent competition with parent ROI
        # (unless parent ROI is not movable)
        if self.parentItem().translatable:
            ev.acceptDrags(Qt.MouseButton.LeftButton)

        hover = False
        if not ev.isExit():
            if self.translatable and ev.acceptDrags(Qt.MouseButton.LeftButton):
                hover=True
                
            for btn in [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton]:
                if (self.acceptedMouseButtons() & btn) and ev.acceptClicks(btn):
                    hover=True
            if self.contextMenuEnabled():
                ev.acceptClicks(Qt.MouseButton.RightButton)
                
        if hover:
            # self.setMouseHover(True)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            ev.acceptClicks(Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
            ev.acceptClicks(Qt.MouseButton.RightButton)
            ev.acceptClicks(Qt.MouseButton.MiddleButton)
            self.sigHoverEvent.emit(self)
        else:
            # self.setMouseHover(False)
            self.setCursor(Qt.CursorShape.CrossCursor)

class _PolyLineSegment(LineSegmentROI):
    # Used internally by PolyLineROI
    def __init__(self, *args, **kwds):
        self._parentHovering = False
        LineSegmentROI.__init__(self, *args, **kwds)
        
    def setParentHover(self, hover):
        pass
        # set independently of own hover state
        # if self._parentHovering != hover:
        #     self._parentHovering = hover
        #     self._updateHoverColor()
        
    def _makePen(self):
        if self.mouseHovering or self._parentHovering:
            return self.hoverPen
        else:
            return self.pen
        
    def hoverEvent(self, ev):
        # accept drags even though we discard them to prevent competition with parent ROI
        # (unless parent ROI is not movable)
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            hover = False
            self.setCursor(Qt.CursorShape.CrossCursor)
        if self.parentItem().translatable:
            ev.acceptDrags(Qt.MouseButton.LeftButton)
        return LineSegmentROI.hoverEvent(self, ev)
    

class BasePolyLineROI(SpecialROI):
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


    def hoverEvent(self, ev: QtCore.QEvent):
        if ev.exit:
            self.setSelected(False)
        else:
            self.setSelected(True)
        hover = False
        if not ev.isExit():
            if self.translatable and ev.acceptDrags(QtCore.Qt.MouseButton.LeftButton):
                hover=True
                
            for btn in [QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.RightButton, QtCore.Qt.MouseButton.MiddleButton]:
                if (self.acceptedMouseButtons() & btn) and ev.acceptClicks(btn):
                    hover=True
            if self.contextMenuEnabled():
                ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
                
        if hover:
            self.setMouseHover(True)
            ev.acceptClicks(QtCore.Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
            ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
            ev.acceptClicks(QtCore.Qt.MouseButton.MiddleButton)
            self.sigHoverEvent.emit(self)
        else:
            self.setMouseHover(False)

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
        seg = _PolyLineSegment(handles=(h1, h2), pen=self.pen, hoverPen=self.hoverPen,
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



class CustomLineSegmentROI(SpecialROI):
    def __init__(self, positions=(None, None), pos=None, handles=(None,None), point_draggable=True,**args):
        if pos is None:
            pos = [0,0]
            
        SpecialROI.__init__(self, pos, [1,1], **args)
        if len(positions) > 2:
            raise Exception("LineSegmentROI must be defined by exactly 2 positions. For more points, use PolyLineROI.")
        
        for i, p in enumerate(positions):
            self.addFreeHandle(p, item=handles[i])

    def hoverEvent(self, ev):
        hover = False
        if not ev.isExit():
            if self.translatable and ev.acceptDrags(QtCore.Qt.MouseButton.LeftButton):
                hover=True
                
            for btn in [QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.RightButton, QtCore.Qt.MouseButton.MiddleButton]:
                if (self.acceptedMouseButtons() & btn) and ev.acceptClicks(btn):
                    hover=True
            if self.contextMenuEnabled():
                ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
                
        if hover:
            # self.setMouseHover(True)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            ev.acceptClicks(QtCore.Qt.MouseButton.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
            ev.acceptClicks(QtCore.Qt.MouseButton.RightButton)
            ev.acceptClicks(QtCore.Qt.MouseButton.MiddleButton)
            self.sigHoverEvent.emit(self)
        else:
            # self.setMouseHover(False)
            self.setCursor(Qt.CursorShape.CrossCursor)
            
    @property
    def endpoints(self):
        # must not be cached because self.handles may change.
        return [h['item'] for h in self.handles]
        
    def listPoints(self):
        return [p['item'].pos() for p in self.handles]

    def getState(self):
        state = SpecialROI.getState(self)
        state['points'] = [Point(h.pos()) for h in self.getHandles()]
        return state

    def saveState(self):
        state = SpecialROI.saveState(self)
        state['points'] = [tuple(h.pos()) for h in self.getHandles()]
        return state

    def setState(self, state):
        SpecialROI.setState(self, state)
        p1 = [state['points'][0][0]+state['pos'][0], state['points'][0][1]+state['pos'][1]]
        p2 = [state['points'][1][0]+state['pos'][0], state['points'][1][1]+state['pos'][1]]
        self.movePoint(self.getHandles()[0], p1, finish=False)
        self.movePoint(self.getHandles()[1], p2)
            
    def paint(self, p, *args):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        h1 = self.endpoints[0].pos()
        h2 = self.endpoints[1].pos()
        p.drawLine(h1, h2)
        
    def boundingRect(self):
        return self.shape().boundingRect()
    
    def shape(self):
        p = QPainterPath()
    
        h1 = self.endpoints[0].pos()
        h2 = self.endpoints[1].pos()
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

