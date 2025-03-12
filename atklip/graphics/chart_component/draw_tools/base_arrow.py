from math import hypot
from atklip.app_utils import functions as fn
from PySide6.QtCore import Qt,QPointF,Signal
from PySide6.QtGui import QTransform,QPainter
from PySide6.QtWidgets import QGraphicsPathItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool

__all__ = ['BaseArrowItem']

class BaseArrowItem(QGraphicsPathItem):
    on_click = Signal(object)
    """
    For displaying scale-invariant arrows.
    For arrows pointing to a location on a curve, see CurveArrow
    
    """
    def __init__(self, parent=None,drawtool=None, **opts):
        """
        Arrows can be initialized with any keyword arguments accepted by 
        the setStyle() method.
        """
        self.opts = {}
        QGraphicsPathItem.__init__(self, parent)

        if 'size' in opts:
            opts['headLen'] = opts['size']
        if 'width' in opts:
            opts['headWidth'] = opts['width']
        pos = opts.pop('pos', (0, 0))

        self.defaultOpts = {
            'pxMode': True,
            'angle': -150,   ## If the angle is 0, the arrow points left
            'headLen': 20,
            'headWidth': None,
            'tipAngle': 25,
            'baseAngle': 0,
            'tailLen': None,
            'tailWidth': 3,
            'pen': (200,200,200),
            'brush': (50,50,200),
        }
        self.defaultOpts.update(opts)
        
        self.moving = False
        self.yoff = False
        self.xoff = False
        self.locked = False
        self.cursorOffset = None
        self.startPosition = None
        self.drawtool:DrawTool = drawtool
        self.chart:Chart = self.drawtool.chart
        
        
        self.has: dict = {
            "x_axis_show":True,
            "name": "rectangle",
            "type": "drawtool",
            "id": id,
            "inputs":{
                    },
            "styles":{
                    'brush': opts["brush"],
                    "lock":True,
                    "setting": False,
                    "delete":True,}
        }
        
        self.setStyle(**self.defaultOpts)

        # for backward compatibility
        # self.setPos(*pos)
    
    
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
        
    def mouseDragEvent(self, ev):
        if not self.locked:
            if ev.button() == Qt.MouseButton.LeftButton:
                if ev.isStart():
                    self.moving = True
                    self.cursorOffset = self.pos() - self.mapToParent(ev.buttonDownPos())
                    self.startPosition = self.pos()
                ev.accept()

                if not self.moving:
                    return
                if self.chart.magnet_on:
                    pos_y = self.chart.hLine.getYPos()
                    self.setPos(QPointF((self.cursorOffset + self.mapToParent(ev.pos())).x(), pos_y))
                else:
                    self.setPos(self.cursorOffset + self.mapToParent(ev.pos()))

                if ev.isFinish():
                    self.moving = False            
            
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
        if _input == "brush":
            self.defaultOpts["brush"] = _style
            self.setStyle(**self.defaultOpts)
    
    def setStyle(self, **opts):
        """
        Changes the appearance of the arrow.
        All arguments are optional:
        
        ======================  =================================================
        **Keyword Arguments:**
        angle                   Orientation of the arrow in degrees. Default is
                                0; arrow pointing to the left.
        headLen                 Length of the arrow head, from tip to base.
                                default=20
        headWidth               Width of the arrow head at its base. If
                                headWidth is specified, it overrides tipAngle.
        tipAngle                Angle of the tip of the arrow in degrees. Smaller
                                values make a 'sharper' arrow. default=25
        baseAngle               Angle of the base of the arrow head. Default is
                                0, which means that the base of the arrow head
                                is perpendicular to the arrow tail.
        tailLen                 Length of the arrow tail, measured from the base
                                of the arrow head to the end of the tail. If
                                this value is None, no tail will be drawn.
                                default=None
        tailWidth               Width of the tail. default=3
        pen                     The pen used to draw the outline of the arrow.
        brush                   The brush used to fill the arrow.
        pxMode                  If True, then the arrow is drawn as a fixed size
                                regardless of the scale of its parents (including
                                the ViewBox zoom level). 
        ======================  =================================================
        """
        arrowOpts = ['headLen', 'tipAngle', 'baseAngle', 'tailLen', 'tailWidth', 'headWidth']
        allowedOpts = ['angle', 'pen', 'brush', 'pxMode'] + arrowOpts
        needUpdate = False
        for k,v in opts.items():
            if k not in allowedOpts:
                raise KeyError('Invalid arrow style option "%s"' % k)
            if self.opts.get(k) != v:
                needUpdate = True
            self.opts[k] = v

        if not needUpdate:
            return
        
        opt = dict([(k,self.opts[k]) for k in arrowOpts if k in self.opts])
        tr = QTransform()
        tr.rotate(self.opts['angle'])
        
        self.path = tr.map(fn.makeArrowPath(**opt))

        self.setPath(self.path)
        
        self.setPen(fn.mkPen(self.opts['pen']))
        self.setBrush(fn.mkBrush(self.opts['brush']))
        
        if self.opts['pxMode']:
            self.setFlags(self.flags() | self.GraphicsItemFlag.ItemIgnoresTransformations)
        else:
            self.setFlags(self.flags() & ~self.GraphicsItemFlag.ItemIgnoresTransformations)
    
    def paint(self, p, *args):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # p.drawRect(self.boundingRect())
        super().paint(p, *args)
        
        #p.setPen(fn.mkPen('r'))
        #p.setBrush(fn.mkBrush(None))
        

    def shape(self):
        #if not self.opts['pxMode']:
            #return QtWidgets.QGraphicsPathItem.shape(self)
        return self.path
    
    ## dataBounds and pixelPadding methods are provided to ensure ViewBox can
    ## properly auto-range 
    def dataBounds(self, ax, frac, orthoRange=None):
        pw = 0
        pen = self.pen()
        if not pen.isCosmetic():
            pw = pen.width() * 0.7072
        if self.opts['pxMode']:
            return [0,0]
        else:
            br = self.boundingRect()
            if ax == 0:
                return [br.left()-pw, br.right()+pw]
            else:
                return [br.top()-pw, br.bottom()+pw]
        
    def pixelPadding(self):
        pad = 0
        if self.opts['pxMode']:
            br = self.boundingRect()
            pad += hypot(br.width(), br.height())
        pen = self.pen()
        if pen.isCosmetic():
            pad += max(1, pen.width()) * 0.7072
        return pad
        
    def boundingRect(self):
        return self.path.boundingRect()
    
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        # else:
        ev.ignore()