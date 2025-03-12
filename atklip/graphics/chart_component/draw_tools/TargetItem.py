import string
from math import atan2
from PySide6 import QtGui,QtCore
from PySide6.QtCore import Signal,Qt,QRectF
from PySide6.QtGui import QColor,QPicture,QBrush

from atklip.graphics.pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject
from atklip.graphics.pyqtgraph import TextItem,UIGraphicsItem,ViewBox,Point,functions as fn
from atklip.graphics.pyqtgraph.graphicsItems.ScatterPlotItem import Symbols


__all__ = ['TargetItem', 'TargetLabel']


class TargetItem(UIGraphicsItem):
    """Draws a draggable target symbol (circle plus crosshair).

    The size of TargetItem will remain fixed on screen even as the view is zoomed.
    Includes an optional text label.
    """

    sigPositionChanged = QtCore.Signal(object)
    sigPositionChangeFinished = QtCore.Signal(object)

    def __init__(
        self,
        pos=None,
        size=10,
        symbol="crosshair",
        pen=None,
        hoverPen=None,
        brush=None,
        hoverBrush=None,
        movable=True,
        label=None,
        labelOpts=None,
    ):
        r"""
        Parameters
        ----------
        pos : list, tuple, QPointF, QPoint, Optional
            Initial position of the symbol.  Default is (0, 0)
        size : int
            Size of the symbol in pixels.  Default is 10.
        pen : QPen, tuple, list or str
            Pen to use when drawing line. Can be any arguments that are valid
            for :func:`~pyqtgraph.mkPen`. Default pen is transparent yellow.
        brush : QBrush, tuple, list, or str
            Defines the brush that fill the symbol. Can be any arguments that
            is valid for :func:`~pyqtgraph.mkBrush`. Default is transparent
            blue.
        movable : bool
            If True, the symbol can be dragged to a new position by the user.
        hoverPen : QPen, tuple, list, or str
            Pen to use when drawing symbol when hovering over it. Can be any
            arguments that are valid for :func:`~pyqtgraph.mkPen`. Default pen
            is red.
        hoverBrush : QBrush, tuple, list or str
            Brush to use to fill the symbol when hovering over it. Can be any
            arguments that is valid for :func:`~pyqtgraph.mkBrush`. Default is
            transparent blue.
        symbol : QPainterPath or str
            QPainterPath to use for drawing the target, should be centered at
            ``(0, 0)`` with ``max(width, height) == 1.0``.  Alternatively a string
            which can be any symbol accepted by
            :func:`~pyqtgraph.ScatterPlotItem.setSymbol`
        label : bool, str or callable, optional
            Text to be displayed in a label attached to the symbol, or None to
            show no label (default is None). May optionally include formatting
            strings to display the symbol value, or a callable that accepts x
            and y as inputs.  If True, the label is ``x = {: >.3n}\ny = {: >.3n}``
            False or None will result in no text being displayed
        labelOpts : dict
            A dict of keyword arguments to use when constructing the text
            label. See :class:`TargetLabel` and :class:`~pyqtgraph.TextItem`
        """
        super().__init__()
        self.movable = movable
        self.moving = False
        self._label = None
        self.mouseHovering = False

        if pen is None:
            pen = (255, 255, 0)
        self.setPen(pen)

        if hoverPen is None:
            hoverPen = (255, 0, 255)
        self.setHoverPen(hoverPen)

        if brush is None:
            brush = (0, 0, 255, 50)
        self.setBrush(brush)

        if hoverBrush is None:
            hoverBrush = (0, 255, 255, 100)
        self.setHoverBrush(hoverBrush)

        self.currentPen = self.pen
        self.currentBrush = self.brush

        self._shape = None

        self._pos = Point(0, 0)
        if pos is None:
            pos = Point(0, 0)
        self.setPos(pos)

        if isinstance(symbol, str):
            try:
                self._path = Symbols[symbol]
            except KeyError:
                raise KeyError("symbol name found in available Symbols")
        elif isinstance(symbol, QtGui.QPainterPath):
            self._path = symbol
        else:
            raise TypeError("Unknown type provided as symbol")

        self.scale = size
        self.setPath(self._path)
        self.setLabel(label, labelOpts)

    def setPos(self, *args):
        """Method to set the position to ``(x, y)`` within the plot view

        Parameters
        ----------
        args : tuple or list or QtCore.QPointF or QtCore.QPoint or Point or float
            Two float values or a container that specifies ``(x, y)`` position where the
            TargetItem should be placed

        Raises
        ------
        TypeError
            If args cannot be used to instantiate a Point
        """
        try:
            newPos = Point(*args)
        except TypeError:
            raise
        except Exception:
            raise TypeError(f"Could not make Point from arguments: {args!r}")

        if self._pos != newPos:
            self._pos = newPos
            super().setPos(self._pos)
            self.sigPositionChanged.emit(self)

    def setBrush(self, *args, **kwargs):
        """Set the brush that fills the symbol. Allowable arguments are any that
        are valid for :func:`~pyqtgraph.mkBrush`.
        """
        self.brush = fn.mkBrush(*args, **kwargs)
        if not self.mouseHovering:
            self.currentBrush = self.brush
            self.update()

    def setHoverBrush(self, *args, **kwargs):
        """Set the brush that fills the symbol when hovering over it. Allowable
        arguments are any that are valid for :func:`~pyqtgraph.mkBrush`.
        """
        self.hoverBrush = fn.mkBrush(*args, **kwargs)
        if self.mouseHovering:
            self.currentBrush = self.hoverBrush
            self.update()

    def setPen(self, *args, **kwargs):
        """Set the pen for drawing the symbol. Allowable arguments are any that
        are valid for :func:`~pyqtgraph.mkPen`."""
        self.pen = fn.mkPen(*args, **kwargs)
        if not self.mouseHovering:
            self.currentPen = self.pen
            self.update()

    def setHoverPen(self, *args, **kwargs):
        """Set the pen for drawing the symbol when hovering over it. Allowable
        arguments are any that are valid for
        :func:`~pyqtgraph.mkPen`."""
        self.hoverPen = fn.mkPen(*args, **kwargs)
        if self.mouseHovering:
            self.currentPen = self.hoverPen
            self.update()

    def boundingRect(self):
        return self.shape().boundingRect()

    def paint(self, p, *_):
        p.setPen(self.currentPen)
        p.setBrush(self.currentBrush)
        p.drawPath(self.shape())

    def setPath(self, path):
        if path != self._path:
            self._path = path
            self._shape = None
        return None

    def shape(self):
        if self._shape is None:
            s = self.generateShape()
            if s is None:
                return self._path
            self._shape = s

            # beware--this can cause the view to adjust
            # which would immediately invalidate the shape.
            self.prepareGeometryChange()
        return self._shape

    def generateShape(self):
        dt = self.deviceTransform()
        if dt is None:
            self._shape = self._path
            return None
        v = dt.map(QtCore.QPointF(1, 0)) - dt.map(QtCore.QPointF(0, 0))
        dti = fn.invertQTransform(dt)
        devPos = dt.map(QtCore.QPointF(0, 0))
        tr = QtGui.QTransform()
        tr.translate(devPos.x(), devPos.y())
        va = atan2(v.y(), v.x())
        tr.rotateRadians(va)
        tr.scale(self.scale, self.scale)
        return dti.map(tr.map(self._path))

    def mouseDragEvent(self, ev):
        if not self.movable or ev.button() != QtCore.Qt.MouseButton.LeftButton:
            return
        ev.accept()
        if ev.isStart():
            self.symbolOffset = self.pos() - self.mapToView(ev.buttonDownPos())
            self.moving = True

        if not self.moving:
            return
        self.setPos(self.symbolOffset + self.mapToView(ev.pos()))

        if ev.isFinish():
            self.moving = False
            self.sigPositionChangeFinished.emit(self)

    def mouseClickEvent(self, ev):
        if self.moving and ev.button() == QtCore.Qt.MouseButton.RightButton:
            ev.accept()
            self.moving = False
            self.sigPositionChanged.emit(self)
            self.sigPositionChangeFinished.emit(self)

    def setMouseHover(self, hover):
        # Inform the item that the mouse is(not) hovering over it
        if self.mouseHovering is hover:
            return
        self.mouseHovering = hover
        if hover:
            self.currentBrush = self.hoverBrush
            self.currentPen = self.hoverPen
        else:
            self.currentBrush = self.brush
            self.currentPen = self.pen
        self.update()

    def hoverEvent(self, ev):
        if self.movable and (not ev.isExit()) and ev.acceptDrags(QtCore.Qt.MouseButton.LeftButton):
            self.setMouseHover(True)
        else:
            self.setMouseHover(False)

    def viewTransformChanged(self):
        GraphicsObject.viewTransformChanged(self)
        self._shape = None  # invalidate shape, recompute later if requested.
        self.update()

    def pos(self):
        """Provides the current position of the TargetItem

        Returns
        -------
        Point
            pg.Point of the current position of the TargetItem
        """
        return self._pos

    def label(self):
        """Provides the TargetLabel if it exists

        Returns
        -------
        TargetLabel or None
            If a TargetLabel exists for this TargetItem, return that, otherwise
            return None
        """
        return self._label

    def setLabel(self, text=None, labelOpts=None):
        """Method to call to enable or disable the TargetLabel for displaying text

        Parameters
        ----------
        text : Callable or str, optional
            Details how to format the text, by default None
            If None, do not show any text next to the TargetItem
            If Callable, then the label will display the result of ``text(x, y)``
            If a fromatted string, then the output of ``text.format(x, y)`` will be
            displayed
            If a non-formatted string, then the text label will display ``text``, by
            default None
        labelOpts : dict, optional
            These arguments are passed on to :class:`~pyqtgraph.TextItem`
        """
        if not text:
            if self._label is not None and self._label.scene() is not None:
                # remove the label if it's already added
                self._label.scene().removeItem(self._label)
            self._label = None
        else:
            # provide default text if text is True
            if text is True:
                # convert to default value or empty string
                text = "x = {: .3n}\ny = {: .3n}"

            labelOpts = {} if labelOpts is None else labelOpts
            if self._label is not None:
                self._label.scene().removeItem(self._label)
            self._label = TargetLabel(self, text=text, **labelOpts)


class TargetLabel(TextItem):
    """A TextItem that attaches itself to a TargetItem.

    This class extends TextItem with the following features :
      * Automatically positions adjacent to the symbol at a fixed position.
      * Automatically reformats text when the symbol location has changed.

    Parameters
    ----------
    target : TargetItem
        The TargetItem to which this label will be attached to.
    text : str or callable, Optional
        Governs the text displayed, can be a fixed string or a format string
        that accepts the x, and y position of the target item; or be a callable
        method that accepts a tuple (x, y) and returns a string to be displayed.
        If None, an empty string is used.  Default is None
    offset : tuple or list or QPointF or QPoint
        Position to set the anchor of the TargetLabel away from the center of
        the target in pixels, by default it is (20, 0).
    anchor : tuple or list or QPointF or QPoint
        Position to rotate the TargetLabel about, and position to set the
        offset value to see :class:`~pyqtgraph.TextItem` for more information.
    kwargs : dict 
        kwargs contains arguments that are passed onto
        :class:`~pyqtgraph.TextItem` constructor, excluding text parameter
    """

    def __init__(
        self,
        target,
        text="",
        offset=(20, 0),
        anchor=(0, 0.5),
        **kwargs,
    ):
        if isinstance(offset, Point):
            self.offset = offset
        elif isinstance(offset, (tuple, list)):
            self.offset = Point(*offset)
        elif isinstance(offset, (QtCore.QPoint, QtCore.QPointF)):
            self.offset = Point(offset.x(), offset.y())
        else:
            raise TypeError("Offset parameter is the wrong data type")

        super().__init__(anchor=anchor, **kwargs)
        self.setParentItem(target)
        self.target = target
        self.setFormat(text)

        self.target.sigPositionChanged.connect(self.valueChanged)
        self.valueChanged()

    def format(self):
        return self._format

    def hoverEvent(self, ev):
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            hover = False
            self.setCursor(Qt.CursorShape.CrossCursor)
    
    def setFormat(self, text):
        """Method to set how the TargetLabel should display the text.  This
        method should be called from TargetItem.setLabel directly.

        Parameters
        ----------
        text : Callable or str
            Details how to format the text.
            If Callable, then the label will display the result of ``text(x, y)``
            If a fromatted string, then the output of ``text.format(x, y)`` will be
            displayed
            If a non-formatted string, then the text label will display ``text``
        """
        if not callable(text):
            parsed = list(string.Formatter().parse(text))
            if parsed and parsed[0][1] is not None:
                self.setProperty("formattableText", True)
            else:
                self.setText(text)
                self.setProperty("formattableText", False)
        else:
            self.setProperty("formattableText", False)
        self._format = text
        self.valueChanged()

    def valueChanged(self):
        x, y = self.target.pos()
        if self.property("formattableText"):
            self.setText(self._format.format(float(x), float(y)))
        elif callable(self._format):
            self.setText(self._format(x, y))

    def viewTransformChanged(self):
        viewbox = self.getViewBox()
        if isinstance(viewbox, ViewBox):
            viewPixelSize = viewbox.viewPixelSize()
            scaledOffset = QtCore.QPointF(
                self.offset.x() * viewPixelSize[0], self.offset.y() * viewPixelSize[1]
            )
            self.setPos(scaledOffset)
        return super().viewTransformChanged()

    def mouseClickEvent(self, ev):
        return self.parentItem().mouseClickEvent(ev)

    def mouseDragEvent(self, ev):
        targetItem = self.parentItem()
        if not targetItem.movable or ev.button() != QtCore.Qt.MouseButton.LeftButton:
            return
        ev.accept()
        if ev.isStart():
            targetItem.symbolOffset = targetItem.pos() - self.mapToView(
                ev.buttonDownPos()
            )
            targetItem.moving = True

        if not targetItem.moving:
            return
        targetItem.setPos(targetItem.symbolOffset + self.mapToView(ev.pos()))

        if ev.isFinish():
            targetItem.moving = False
            targetItem.sigPositionChangeFinished.emit(self)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool



class TextBoxROI(UIGraphicsItem):
    """Draws a draggable target symbol (circle plus crosshair).

    The size of TargetItem will remain fixed on screen even as the view is zoomed.
    Includes an optional text label.
    """
    on_click = Signal(object)
    draw_rec = Signal()

    signal_change_font_size = Signal(int)
    sigPositionChanged = QtCore.Signal(object)
    sigPositionChangeFinished = QtCore.Signal(object)
    
    def __init__(
        self,
        pos=None, size=10,id=None, symbol= "o", 
        pen=None, hoverPen=None, brush=None, 
        hoverBrush=None, movable=True, label=None, 
        labelOpts=None,drawtool=None
    ):
        r"""
        Parameters
        ----------
        pos : list, tuple, QPointF, QPoint, Optional
            Initial position of the symbol.  Default is (0, 0)
        size : int
            Size of the symbol in pixels.  Default is 10.
        pen : QPen, tuple, list or str
            Pen to use when drawing line. Can be any arguments that are valid
            for :func:`~pyqtgraph.mkPen`. Default pen is transparent yellow.
        brush : QBrush, tuple, list, or str
            Defines the brush that fill the symbol. Can be any arguments that
            is valid for :func:`~pyqtgraph.mkBrush`. Default is transparent
            blue.
        movable : bool
            If True, the symbol can be dragged to a new position by the user.
        hoverPen : QPen, tuple, list, or str
            Pen to use when drawing symbol when hovering over it. Can be any
            arguments that are valid for :func:`~pyqtgraph.mkPen`. Default pen
            is red.
        hoverBrush : QBrush, tuple, list or str
            Brush to use to fill the symbol when hovering over it. Can be any
            arguments that is valid for :func:`~pyqtgraph.mkBrush`. Default is
            transparent blue.
        symbol : QPainterPath or str
            QPainterPath to use for drawing the target, should be centered at
            ``(0, 0)`` with ``max(width, height) == 1.0``.  Alternatively a string
            which can be any symbol accepted by
            :func:`~pyqtgraph.ScatterPlotItem.setSymbol`
        label : bool, str or callable, optional
            Text to be displayed in a label attached to the symbol, or None to
            show no label (default is None). May optionally include formatting
            strings to display the symbol value, or a callable that accepts x
            and y as inputs.  If True, the label is ``x = {: >.3n}\ny = {: >.3n}``
            False or None will result in no text being displayed
        labelOpts : dict
            A dict of keyword arguments to use when constructing the text
            label. See :class:`TargetLabel` and :class:`~pyqtgraph.TextItem`
        """
        super().__init__()
        self.movable = movable
        self.moving = False
        self._label = None
        self.mouseHovering = False

        if pen is None:
            pen = (255, 255, 0)
        self.setPen(pen)

        if hoverPen is None:
            hoverPen = (255, 0, 255)
        self.setHoverPen(hoverPen)

        if brush is None:
            brush = (0, 0, 255, 50)
        self.setBrush(brush)

        if hoverBrush is None:
            hoverBrush = (0, 255, 255, 100)
        self.setHoverBrush(hoverBrush)

        self.currentPen = self.pen
        self.currentBrush = self.brush

        self._shape = None

        self._pos = Point(0, 0)
        # if pos is None:
        #     pos = Point(0, 0)
        # self.setPos(pos)

        # if isinstance(symbol, str):
        #     try:
        #         self._path = Symbols[symbol]
        #     except KeyError:
        #         raise KeyError("symbol name found in available Symbols")
        # elif isinstance(symbol, QtGui.QPainterPath):
        #     self._path = symbol
        # else:
        #     raise TypeError("Unknown type provided as symbol")

        self.scale = size
        # self.setPath(self._path)
        # self.setLabel(label, labelOpts)
        
        self.id = id
        self.locked = False
        self.drawtool:DrawTool = drawtool
        self.chart:Chart= self.drawtool.chart
        self.is_selected = False
        # self.on_click.connect(self.chart.show_popup_setting_tool)
        # self.on_click.connect(self.get_pos_point)
        self.picture:QPicture = QPicture()
        self.signal_change_font_size.connect(self.change_font_size)
        self.color =  "#F4511E"
        self.font_size = 10
        self.name = ''
        self.setLabel("Text",
                        {
                            "anchor": QtCore.QPointF(0.5, 0.5),
                            "offset": QtCore.QPointF(0, 30),
                            "color": self.color,
                        }
                        )
        
        self.update_html(self.color, self.font_size)
        self.setBrush(QColor("#1ec2f4"))
        
        self.has: dict = {
            "x_axis_show":False,
            "name": "rectangle",
            "type": "drawtool",
            "id": id,
            "inputs":{
                    },
            "styles":{
                    "lock":True,
                    "setting": False,
                    "delete":True,}
                    }
        
    def get_styles(self):
        styles =  {"lock":self.has["styles"]["lock"],
                    "delete":self.has["styles"]["delete"],
                    "setting":self.has["styles"]["setting"],}
        return styles

    def setPos(self, *args):
        """Method to set the position to ``(x, y)`` within the plot view

        Parameters
        ----------
        args : tuple or list or QtCore.QPointF or QtCore.QPoint or Point or float
            Two float values or a container that specifies ``(x, y)`` position where the
            TargetItem should be placed

        Raises
        ------
        TypeError
            If args cannot be used to instantiate a Point
        """
        try:
            newPos = Point(*args)
        except TypeError:
            raise
        except Exception:
            raise TypeError(f"Could not make Point from arguments: {args!r}")

        if self._pos != newPos:
            self._pos = newPos
            super().setPos(self._pos)
            self.sigPositionChanged.emit(self)

    def setBrush(self, *args, **kwargs):
        """Set the brush that fills the symbol. Allowable arguments are any that
        are valid for :func:`~pyqtgraph.mkBrush`.
        """
        self.brush = fn.mkBrush(*args, **kwargs)
        if not self.mouseHovering:
            self.currentBrush = self.brush
            self.update()

    def setHoverBrush(self, *args, **kwargs):
        """Set the brush that fills the symbol when hovering over it. Allowable
        arguments are any that are valid for :func:`~pyqtgraph.mkBrush`.
        """
        self.hoverBrush = fn.mkBrush(*args, **kwargs)
        if self.mouseHovering:
            self.currentBrush = self.hoverBrush
            self.update()

    def setPen(self, *args, **kwargs):
        """Set the pen for drawing the symbol. Allowable arguments are any that
        are valid for :func:`~pyqtgraph.mkPen`."""
        self.pen = fn.mkPen(*args, **kwargs)
        if not self.mouseHovering:
            self.currentPen = self.pen
            self.update()

    def setHoverPen(self, *args, **kwargs):
        """Set the pen for drawing the symbol when hovering over it. Allowable
        arguments are any that are valid for
        :func:`~pyqtgraph.mkPen`."""
        self.hoverPen = fn.mkPen(*args, **kwargs)
        if self.mouseHovering:
            self.currentPen = self.hoverPen
            self.update()

    def boundingRect(self):
        if self._label:
            return self._label.boundingRect()
        return QRectF(0,0,0,0)
        
        # return self.shape().boundingRect()

    def paint(self, p, *_):
        self.picture.play(p)
        # p.setPen(self.currentPen)
        # p.setBrush(self.currentBrush)
        # p.drawPath(self.shape())

    def setPath(self, path):
        if path != self._path:
            self._path = path
            self._shape = None
        return None

    def shape(self):
        return
        if self._shape is None:
            s = self.generateShape()
            if s is None:
                return self._path
            self._shape = s

            # beware--this can cause the view to adjust
            # which would immediately invalidate the shape.
            self.prepareGeometryChange()
        return self._shape

    def generateShape(self):
        dt = self.deviceTransform()
        if dt is None:
            self._shape = self._path
            return None
        v = dt.map(QtCore.QPointF(1, 0)) - dt.map(QtCore.QPointF(0, 0))
        dti = fn.invertQTransform(dt)
        devPos = dt.map(QtCore.QPointF(0, 0))
        tr = QtGui.QTransform()
        tr.translate(devPos.x(), devPos.y())
        va = atan2(v.y(), v.x())
        tr.rotateRadians(va)
        tr.scale(self.scale, self.scale)
        return dti.map(tr.map(self._path))

    def mouseDragEvent(self, ev):
        if not self.movable or ev.button() != QtCore.Qt.MouseButton.LeftButton:
            return
        ev.accept()
        if ev.isStart():
            self.symbolOffset = self.pos() - self.mapToView(ev.buttonDownPos())
            self.moving = True

        if not self.moving:
            return
        self.setPos(self.symbolOffset + self.mapToView(ev.pos()))

        if ev.isFinish():
            self.moving = False
            self.sigPositionChangeFinished.emit(self)

    def mouseClickEvent(self, ev):
        if self.moving and ev.button() == QtCore.Qt.MouseButton.RightButton:
            ev.accept()
            self.moving = False
            self.sigPositionChanged.emit(self)
            self.sigPositionChangeFinished.emit(self)

    def setMouseHover(self, hover):
        # Inform the item that the mouse is(not) hovering over it
        if self.mouseHovering is hover:
            return
        self.mouseHovering = hover
        if hover:
            self.currentBrush = self.hoverBrush
            self.currentPen = self.hoverPen
        else:
            self.currentBrush = self.brush
            self.currentPen = self.pen
        self.update()

    def hoverEvent(self, ev):
        if self.movable and (not ev.isExit()) and ev.acceptDrags(QtCore.Qt.MouseButton.LeftButton):
            self.setMouseHover(True)
        else:
            self.setMouseHover(False)

    def viewTransformChanged(self):
        GraphicsObject.viewTransformChanged(self)
        self._shape = None  # invalidate shape, recompute later if requested.
        self.update()

    def pos(self):
        """Provides the current position of the TargetItem

        Returns
        -------
        Point
            pg.Point of the current position of the TargetItem
        """
        return self._pos

    def label(self):
        """Provides the TargetLabel if it exists

        Returns
        -------
        TargetLabel or None
            If a TargetLabel exists for this TargetItem, return that, otherwise
            return None
        """
        return self._label

    def setLabel(self, text=None, labelOpts=None):
        """Method to call to enable or disable the TargetLabel for displaying text

        Parameters
        ----------
        text : Callable or str, optional
            Details how to format the text, by default None
            If None, do not show any text next to the TargetItem
            If Callable, then the label will display the result of ``text(x, y)``
            If a fromatted string, then the output of ``text.format(x, y)`` will be
            displayed
            If a non-formatted string, then the text label will display ``text``, by
            default None
        labelOpts : dict, optional
            These arguments are passed on to :class:`~pyqtgraph.TextItem`
        """
        
        if self._label:
            self.update_html(self.color,self.font_size, text)
            return
        
        if not text:
            if self._label is not None and self._label.scene() is not None:
                # remove the label if it's already added
                self._label.scene().removeItem(self._label)
            self._label = None
        else:
            # provide default text if text is True
            if text is True:
                # convert to default value or empty string
                text = "x = {: .3n}\ny = {: .3n}"

            labelOpts = {} if labelOpts is None else labelOpts
            if self._label is not None:
                self._label.scene().removeItem(self._label)
            self._label = TargetLabel(self, text=text, **labelOpts)

    
    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            # self.setSelected(True)
            # self.change_size_handle(3)
        else:
            self.isSelected = False
            # self.setSelected(False)
            # self.change_size_handle(4)

    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name

    def update_text_item(self, main_chart, setting_menu):
        updated_text = setting_menu.plain_textedit.toPlainText()
        self.update_html(text=updated_text)
        self.draw_rec.emit()
    
    def update_html(self, color="#F4511E",font_size=14, text="Text"):
        self.color =  color
        self.font_size = font_size
        self.html = f"""<div style="text-align: center">
    <span style="color: {color}; font-size: {font_size}pt;">{text}</span>"""
        self.label().setHtml(self.html)

    def getText(self):
        return self.label().toPlainText()
    
    def get_pos_point(self):
        return self.pos()
    def set_lock(self,btn):
        print(btn,btn.isChecked())
        if btn.isChecked():
            self.locked_handle()
        else:
            self.unlocked_handle()
            
    def locked_handle(self):
        self.movable = False
        self.locked = True
        

    def unlocked_handle(self):
        self.movable = True
        self.locked = False

    def change_color(self, color):
        r, g, b = color[0], color[1], color[2]
        self.color = QColor(r, g, b).name()
        text = self.getText()
        self.update_html(color=self.color, text=text)

    def change_font_size(self, size):
        text = self.getText()
        self.update_html(color=self.color, text=text, font_size=size)


    def mouseDoubleClickEvent(self, event) -> None:
        # print(325, "mouseDoubleClickEvent", event)
        return super().mouseDoubleClickEvent(event)
    
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            # widget = self.childAt(ev.position().toPoint())
            # print(191, ev.pos().toPoint())
            self.on_click.emit(self)
        # print(647, self.pos(), self.state)
        ev.ignore()
        #return super().mouseClickEvent(event)
    
from PySide6.QtGui import QTransform,QPainter

class ArrowItem(UIGraphicsItem):
    """Draws a draggable target symbol (circle plus crosshair).

    The size of TargetItem will remain fixed on screen even as the view is zoomed.
    Includes an optional text label.
    """
    on_click = Signal(object)
    sigPositionChanged = QtCore.Signal(object)
    sigPositionChangeFinished = QtCore.Signal(object)

    def __init__(
        self,
        drawtool=None,
        size=10,
        symbol="arrow_up",
        angle:int=90,
        pen=None,
        hoverPen=None,
        brush=None,
        hoverBrush=None,
        movable=True,
        label=None,
        labelOpts=None,
    ):
        r"""
        Parameters
        ----------
        pos : list, tuple, QPointF, QPoint, Optional
            Initial position of the symbol.  Default is (0, 0)
        size : int
            Size of the symbol in pixels.  Default is 10.
        pen : QPen, tuple, list or str
            Pen to use when drawing line. Can be any arguments that are valid
            for :func:`~pyqtgraph.mkPen`. Default pen is transparent yellow.
        brush : QBrush, tuple, list, or str
            Defines the brush that fill the symbol. Can be any arguments that
            is valid for :func:`~pyqtgraph.mkBrush`. Default is transparent
            blue.
        movable : bool
            If True, the symbol can be dragged to a new position by the user.
        hoverPen : QPen, tuple, list, or str
            Pen to use when drawing symbol when hovering over it. Can be any
            arguments that are valid for :func:`~pyqtgraph.mkPen`. Default pen
            is red.
        hoverBrush : QBrush, tuple, list or str
            Brush to use to fill the symbol when hovering over it. Can be any
            arguments that is valid for :func:`~pyqtgraph.mkBrush`. Default is
            transparent blue.
        symbol : QPainterPath or str
            QPainterPath to use for drawing the target, should be centered at
            ``(0, 0)`` with ``max(width, height) == 1.0``.  Alternatively a string
            which can be any symbol accepted by
            :func:`~pyqtgraph.ScatterPlotItem.setSymbol`
        label : bool, str or callable, optional
            Text to be displayed in a label attached to the symbol, or None to
            show no label (default is None). May optionally include formatting
            strings to display the symbol value, or a callable that accepts x
            and y as inputs.  If True, the label is ``x = {: >.3n}\ny = {: >.3n}``
            False or None will result in no text being displayed
        labelOpts : dict
            A dict of keyword arguments to use when constructing the text
            label. See :class:`TargetLabel` and :class:`~pyqtgraph.TextItem`
        """
        super().__init__()
        
        self.drawtool:DrawTool = drawtool
        self.chart:Chart = self.drawtool.chart
        
        
        self.movable = movable
        self.moving = False
        self._label = None
        self.mouseHovering = False
        
        
        self.moving = False
        self.yoff = False
        self.xoff = False
        self.locked = False
        self.cursorOffset = None
        self.startPosition = None

        if pen is None:
            pen = (255, 255, 0)
        self.setPen(pen)

        if hoverPen is None:
            hoverPen = (255, 0, 255)
        self.setHoverPen(hoverPen)

        if brush is None:
            brush = (0, 0, 255, 50)
        self.setBrush(brush)

        if hoverBrush is None:
            hoverBrush = (0, 255, 255, 100)
        self.setHoverBrush(hoverBrush)

        self.currentPen = self.pen
        self.currentBrush = self.brush

        self._shape = None

        self._pos:Point = None
        
        self.has: dict = {
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
        
        ops = {'headLen': 10, 'tipAngle': 60, 'baseAngle': 0, 'tailLen': 10, 'tailWidth': 5, 'headWidth': None}
        
        tr = QTransform()
        tr.rotate(angle)
        self._path = tr.map(fn.makeArrowPath(**ops))
        self.scale = 1
        self.setPath(self._path)
        
        # self.setFlags(self.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
        # self.setLabel(label, labelOpts)

    def setPos(self, *args):
        """Method to set the position to ``(x, y)`` within the plot view

        Parameters
        ----------
        args : tuple or list or QtCore.QPointF or QtCore.QPoint or Point or float
            Two float values or a container that specifies ``(x, y)`` position where the
            TargetItem should be placed

        Raises
        ------
        TypeError
            If args cannot be used to instantiate a Point
        """
        try:
            newPos = Point(*args)
        except TypeError:
            raise
        except Exception:
            raise TypeError(f"Could not make Point from arguments: {args!r}")

        if self._pos != newPos:
            self._pos = newPos
            super().setPos(self._pos)
            self.sigPositionChanged.emit(self)

    def setBrush(self, *args, **kwargs):
        """Set the brush that fills the symbol. Allowable arguments are any that
        are valid for :func:`~pyqtgraph.mkBrush`.
        """
        self.brush = fn.mkBrush(*args, **kwargs)
        if not self.mouseHovering:
            self.currentBrush = self.brush
            self.update()

    def setHoverBrush(self, *args, **kwargs):
        """Set the brush that fills the symbol when hovering over it. Allowable
        arguments are any that are valid for :func:`~pyqtgraph.mkBrush`.
        """
        self.hoverBrush = fn.mkBrush(*args, **kwargs)
        if self.mouseHovering:
            self.currentBrush = self.hoverBrush
            self.update()

    def setPen(self, *args, **kwargs):
        """Set the pen for drawing the symbol. Allowable arguments are any that
        are valid for :func:`~pyqtgraph.mkPen`."""
        self.pen = fn.mkPen(*args, **kwargs)
        if not self.mouseHovering:
            self.currentPen = self.pen
            self.update()

    def setHoverPen(self, *args, **kwargs):
        """Set the pen for drawing the symbol when hovering over it. Allowable
        arguments are any that are valid for
        :func:`~pyqtgraph.mkPen`."""
        self.hoverPen = fn.mkPen(*args, **kwargs)
        if self.mouseHovering:
            self.currentPen = self.hoverPen
            self.update()

    def boundingRect(self):
        return self.shape().boundingRect()

    def paint(self, p:QPainter, *_):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        p.setBrush(self.currentBrush)
        p.drawPath(self.shape())

    def setPath(self, path):
        if path != self._path:
            self._path = path
            self._shape = None
        return None

    def shape(self):
        if self._shape is None:
            s = self.generateShape()
            if s is None:
                return self._path
            self._shape = s
            self.prepareGeometryChange()
        return self._shape

    def generateShape(self):
        dt = self.deviceTransform()
        if dt is None:
            self._shape = self._path
            return None
        v = dt.map(QtCore.QPointF(1, 0)) - dt.map(QtCore.QPointF(0, 0))
        dti = fn.invertQTransform(dt)
        devPos = dt.map(QtCore.QPointF(0, 0))
        tr = QtGui.QTransform()
        tr.translate(devPos.x(), devPos.y())
        va = atan2(v.y(), v.x())
        tr.rotateRadians(va)
        tr.scale(self.scale, self.scale)
        return dti.map(tr.map(self._path))

    def mouseDragEvent(self, ev):
        if not self.locked:
            if not self.movable or ev.button() != QtCore.Qt.MouseButton.LeftButton:
                return
            ev.accept()
            if ev.isStart():
                self.symbolOffset = self.pos() - self.mapToView(ev.buttonDownPos())
                self.moving = True

            if not self.moving:
                return
            self.setPos(self.symbolOffset + self.mapToView(ev.pos()))

            if ev.isFinish():
                self.moving = False
                self.sigPositionChangeFinished.emit(self)

    def viewTransformChanged(self):
        GraphicsObject.viewTransformChanged(self)
        self._shape = None  # invalidate shape, recompute later if requested.
        self.update()

    def pos(self):
        """Provides the current position of the TargetItem

        Returns
        -------
        Point
            pg.Point of the current position of the TargetItem
        """
        return self._pos

            
    def hoverEvent(self, ev):
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            hover = False
            self.setCursor(Qt.CursorShape.CrossCursor)
    
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

    def unlocked_handle(self):
        self.yoff = False
        self.xoff =False
        self.locked = False          
            
    def setObjectName(self,name):
        """Set the object name of the item."""
        self._objectName = name
    
    def objectName(self):
        return self._objectName
    
    def get_inputs(self):
        inputs =  {}
        return inputs
    
    def get_styles(self):
        styles =  {"brush":self.has["styles"]["brush"],
                    "lock":self.has["styles"]["lock"],
                    "delete":self.has["styles"]["delete"],
                    "setting":self.has["styles"]["setting"],}
        return styles
    
    def update_inputs(self,_input,_source):
        is_update = False
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        if _input == "brush" or _input == "pen":
            if isinstance(_style,QBrush):
                self.brush = _style
                self.currentBrush = self.brush
                color = _style.color()
                self.currentPen = self.pen = fn.mkPen(color)
            else:
                self.brush = fn.mkBrush(_style)
                self.currentBrush = self.brush
                self.currentPen = self.pen = fn.mkPen(_style)
            self.update()
            
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        # else:
        ev.ignore()