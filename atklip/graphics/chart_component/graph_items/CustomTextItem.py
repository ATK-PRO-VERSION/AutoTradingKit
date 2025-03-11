"""
Real-time quotes charting components
"""
from PySide6 import QtCore, QtGui,QtWidgets
from PySide6.QtGui import QPainter,QPicture

from atklip.app_utils.functions import mkBrush
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

from math import atan2, degrees

from atklip.graphics.pyqtgraph import GraphicsObject,Point,functions as fn

__all__ = ['TextItem']

class TextItem(GraphicsObject):
    """
    GraphicsItem displaying unscaled text (the text will always appear normal even inside a scaled ViewBox). 
    """
    def __init__(self,chart=None, text='', color=(200,200,200), html=None, anchor=(0,0),
                 border=None, fill=None, angle=0, rotateAxis=None, ensureInBounds=False):
        """
        ================  =================================================================================
        **Arguments:**
        *text*            The text to display
        *color*           The color of the text (any format accepted by pg.mkColor)
        *html*            If specified, this overrides both *text* and *color*
        *anchor*          A QPointF or (x,y) sequence indicating what region of the text box will
                          be anchored to the item's position. A value of (0,0) sets the upper-left corner
                          of the text box to be at the position specified by setPos(), while a value of (1,1)
                          sets the lower-right corner.
        *border*          A pen to use when drawing the border
        *fill*            A brush to use when filling within the border
        *angle*           Angle in degrees to rotate text. Default is 0; text will be displayed upright.
        *rotateAxis*      If None, then a text angle of 0 always points along the +x axis of the scene.
                          If a QPointF or (x,y) sequence is given, then it represents a vector direction
                          in the parent's coordinate system that the 0-degree line will be aligned to. This
                          Allows text to follow both the position and orientation of its parent while still
                          discarding any scale and shear factors.
        *ensureInBounds*  Ensures that the entire TextItem will be visible when using autorange, but may
                          produce runaway scaling in certain circumstances (See issue #2642). Setting to 
                          "True" retains legacy behavior.
        ================  =================================================================================


        The effects of the `rotateAxis` and `angle` arguments are added independently. So for example:

          * rotateAxis=None, angle=0 -> normal horizontal text
          * rotateAxis=None, angle=90 -> normal vertical text
          * rotateAxis=(1, 0), angle=0 -> text aligned with x axis of its parent
          * rotateAxis=(0, 1), angle=0 -> text aligned with y axis of its parent
          * rotateAxis=(1, 0), angle=90 -> text orthogonal to x axis of its parent
        """
                     
        self.anchor = Point(anchor)
        self.rotateAxis = None if rotateAxis is None else Point(rotateAxis)
        #self.angle = 0
        GraphicsObject.__init__(self)
        
        self.chart:Chart = chart
        self.picture = QPicture()
        self.x,self.y = None,None
        
        self.textItem = QtWidgets.QGraphicsTextItem()
        self.textItem.setParentItem(self)
        self._lastTransform = None
        self._lastScene = None

        # Note: The following is pretty scuffed; ideally there would likely be 
        # some inheritance changes, But this is the least-intrusive thing that 
        # works for now
        if ensureInBounds:
            self.dataBounds = None
        
        self._bounds = QtCore.QRectF()
        if html is None:
            self.setColor(color)
            self.setText(text)
        else:
            self.setHtml(html)
        self.fill = fn.mkBrush(fill)
        self.border = fn.mkPen(border)
        self.setAngle(angle)

    def setText(self, text, color=None):
        """
        Set the text of this item. 
        
        This method sets the plain text of the item; see also setHtml().
        """
        if color is not None:
            self.setColor(color)
        self.setPlainText(text)

    def setPlainText(self, text):
        """
        Set the plain text to be rendered by this item. 
        
        See QtWidgets.QGraphicsTextItem.setPlainText().
        """
        if text != self.toPlainText():
            self.textItem.setPlainText(text)
            self.updateTextPos()

    def toPlainText(self):
        return self.textItem.toPlainText()
        
    def setHtml(self, html):
        """
        Set the HTML code to be rendered by this item. 
        
        See QtWidgets.QGraphicsTextItem.setHtml().
        """
        if self.toHtml() != html:
            self.textItem.setHtml(html)
            self.updateTextPos()
        
    def toHtml(self):
        return self.textItem.toHtml()
        
    def setTextWidth(self, *args):
        """
        Set the width of the text.
        
        If the text requires more space than the width limit, then it will be
        wrapped into multiple lines.
        
        See QtWidgets.QGraphicsTextItem.setTextWidth().
        """
        self.textItem.setTextWidth(*args)
        self.updateTextPos()
        
    def setFont(self, *args):
        """
        Set the font for this text. 
        
        See QtWidgets.QGraphicsTextItem.setFont().
        """
        self.textItem.setFont(*args)
        self.updateTextPos()
        
    def setAngle(self, angle):
        """
        Set the angle of the text in degrees.

        This sets the rotation angle of the text as a whole, measured
        counter-clockwise from the x axis of the parent. Note that this rotation
        angle does not depend on horizontal/vertical scaling of the parent.
        """
        self.angle = angle
        self.updateTransform(force=True)

    def setAnchor(self, anchor):
        self.anchor = Point(anchor)
        self.updateTextPos()

    def setColor(self, color):
        """
        Set the color for this text.
        
        See QtWidgets.QGraphicsItem.setDefaultTextColor().
        """
        self.color = fn.mkColor(color)
        self.textItem.setDefaultTextColor(self.color)
        
    def updateTextPos(self):
        # update text position to obey anchor
        r = self.textItem.boundingRect()
        tl = self.textItem.mapToParent(r.topLeft())
        br = self.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.anchor
        self.textItem.setPos(-offset)

    def dataBounds(self, ax, frac=1.0, orthoRange=None):
        """
        Returns only the anchor point for when calulating view ranges.
        
        Sacrifices some visual polish for fixing issue #2642.
        """
        if orthoRange:
            range_min, range_max = orthoRange[0], orthoRange[1]
            if not range_min <= self.anchor[ax] <= range_max:
                return [None, None]

        return [self.anchor[ax], self.anchor[ax]]
        
    def boundingRect(self):
        return self.textItem.mapRectToParent(self.textItem.boundingRect())

    def viewTransformChanged(self):
        # called whenever view transform has changed.
        # Do this here to avoid double-updates when view changes.
        self.updateTransform()
    
    def setPos(self,point):
        self.x,self.y = point.x(),point.y()
        super().setPos(point)
    
    def paint(self, p, *args):
        x_left,x_right = self.chart.xAxis.range[0],self.chart.xAxis.range[1]
        if self.x:
            if x_left < self.x < x_right:
                self.show()
                p = QPainter(self.picture)
                
                s = self.scene()
                ls = self._lastScene
                if s is not ls:
                    if ls is not None:
                        ls.sigPrepareForPaint.disconnect(self.updateTransform)
                    self._lastScene = s
                    if s is not None:
                        s.sigPrepareForPaint.connect(self.updateTransform)
                    self.updateTransform()
                    p.setTransform(self.sceneTransform())
                
                if self.border.style() != QtCore.Qt.PenStyle.NoPen or self.fill.style() != QtCore.Qt.BrushStyle.NoBrush:
                    p.setPen(self.border)
                    p.setBrush(self.fill)
                    p.setRenderHint(p.RenderHint.Antialiasing, True)
                    p.drawPolygon(self.textItem.mapToParent(self.textItem.boundingRect()))
            else:
                self.hide()
        
    def setVisible(self, v):
        GraphicsObject.setVisible(self, v)
        if v:
            self.updateTransform()
    
    def updateTransform(self, force=False):
        if not self.isVisible():
            return

        # update transform such that this item has the correct orientation
        # and scaling relative to the scene, but inherits its position from its
        # parent.
        # This is similar to setting ItemIgnoresTransformations = True, but 
        # does not break mouse interaction and collision detection.
        p = self.parentItem()
        if p is None:
            pt = QtGui.QTransform()
        else:
            pt = p.sceneTransform()
        
        if not force and pt == self._lastTransform:
            return

        t = fn.invertQTransform(pt)
        # reset translation
        t.setMatrix(t.m11(), t.m12(), t.m13(), t.m21(), t.m22(), t.m23(), 0, 0, t.m33())
        
        # apply rotation
        angle = -self.angle
        if self.rotateAxis is not None:
            d = pt.map(self.rotateAxis) - pt.map(Point(0, 0))
            a = degrees(atan2(d.y(), d.x()))
            angle += a
        t.rotate(angle)  
        self.setTransform(t)
        self._lastTransform = pt
        self.updateTextPos()



# TODO: test this out as our help menu
class CenteredTextItem(QtWidgets.QGraphicsTextItem):
    def __init__(
        self,
        chart,
        text='',
        parent=None,
        pos=(0, 0),
        pen=None,
        brush=None,
        valign=QtCore.Qt.AlignBottom,
        opacity=0.1,
    ):
        super().__init__(text, parent)
        self.chart:Chart = chart
        self.pen = pen
        self.brush = mkBrush(brush)
        self.opacity = opacity
        self.valign = valign
        self.text_flags = QtCore.Qt.AlignCenter
        self.setPos(*pos)
        self.setFlag(self.GraphicsItemFlag.ItemIgnoresTransformations)
        
        self.has = {
            "x_axis_show":True,
            "name": "rectangle",
            "type": "drawtool",
            "id": id,
            "inputs":{
                    },
            "styles":{
                    'brush': pen,
                    "lock":True,
                    "setting": False,
                    "delete":True,}
        }
        
        self.picture = QPicture()
        self.x,self.y = None,None
        self.setdata()

    def setPos(self,x,y):
        self.x,self.y = x,y
        super().setPos(x,y)
    
    def boundingRect(self):  # noqa
        r = super().boundingRect()
        if self.valign == QtCore.Qt.AlignTop:
            return QtCore.QRectF(-r.width() / 2, -37, r.width(), r.height())
        elif self.valign == QtCore.Qt.AlignBottom:
            return QtCore.QRectF(-r.width() / 2, 15, r.width(), r.height())

    def paint(self, p, option, widget):
        # x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
        # if self.x:
        #     if x_left < self.x < x_right:
        self.picture.play(p)
    
    def setdata(self):
        p = QPainter(self.picture)
        
        p.setRenderHint(QPainter.Antialiasing, False)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        p.setPen(self.pen)
        # if self.brush.style() != QtCore.Qt.NoBrush:
        #     p.setOpacity(self.opacity)
        #     p.fillRect(self.boundingRect(), self.brush)
        #     p.setOpacity(1)
        p.setFont(QtGui.QFont("Arial", 10))
        p.drawText(self.boundingRect(), self.text_flags, self.toPlainText())