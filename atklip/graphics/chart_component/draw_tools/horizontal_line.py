from atklip.graphics.pyqtgraph import InfiniteLine
from atklip.graphics.pyqtgraph import functions as fn
from PySide6 import QtCore
from PySide6.QtCore import Signal,Qt,QPointF


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool

class Horizontal_line(InfiniteLine):
    
    on_click = Signal(object)
    change_pen_signal = Signal(tuple)

    signal_visible = Signal(bool)
    signal_delete = Signal()

    
    def __init__(self, drawtool=None, id=None, pos=None, angle=90, pen=None, movable=False, bounds=None,
                 hoverPen=None, label=None, labelOpts=None, span=(0, 1), markers=None, 
                 name=None):
        super(Horizontal_line,self).__init__(pos, angle, pen, movable, bounds, hoverPen, label, labelOpts, span, markers, name)
        self.drawtool:DrawTool = drawtool
        self.chart:Chart = self.drawtool.chart  # plot mapchart
        self.vb = self.chart.vb
        
        self.id = id
        self.popup_setting_tool = None
        self.isSelected = False
        self.has = {
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
        self.change_pen_signal.connect(self.chart.yAxis.change_value)
        self.locked = False
        self.color = "#2962ff"
        self.width = 1
        self.style = Qt.SolidLine
        self.addMarker('o', size=6)
        self.change_pen_signal.emit(("#363a45",pos))
        self.signal_visible.connect(self.setVisible)
        self.signal_delete.connect(self.delete)

    def selectedHandler(self, is_selected):
        if is_selected:
            self.isSelected = True
            self.addMarker('o', size=6)
        else:
            self.isSelected = False
            self.clearMarkers()

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
        if _input == "pen" or _input == "width" or _input == "style":
            self.setPen(color=self.has["styles"]["pen"], width=self.has["styles"]["width"],style=self.has["styles"]["style"])


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.update()

    def get_pos_point(self):
        print(self.getYPos())
    
    def get_pen_color(self):
        return self.currentPen.color().name()
    
    def get_pen_style(self):
        return self.currentPen.style().name
    
    def delete(self):
        "xoa hien thi gia truc y"
        self.price_axis.kwargs["horizontal_ray"].remove(self.id)
        self.deleteLater()

    def setPen(self, *args, **kwargs):
        """Set the pen for drawing the line. Allowable arguments are any that are valid
        for :func:`mkPen <pyqtgraph.mkPen>`."""
        if "color" in kwargs.keys():
            self.color = kwargs["color"]
        if "width" in kwargs.keys():
            self.width = kwargs["width"]
        if "style" in kwargs.keys():
            self.style = kwargs["style"]
        
        self.pen = fn.mkPen(*args, **kwargs)
        if not self.mouseHovering:
            self.currentPen = self.pen
            self.update()

    def mouseClickEvent(self, ev):
        self.sigClicked.emit(self, ev)
        if self.moving and ev.button() == QtCore.Qt.MouseButton.RightButton:
            ev.accept()
            self.setPos(self.startPosition)
            self.moving = False
            self.sigDragged.emit(self)
            self.sigPositionChangeFinished.emit(self)
        elif ev.button() == Qt.MouseButton.LeftButton:
            
            self.on_click.emit(self)
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
        if self.movable and not self.locked and ev.button() == QtCore.Qt.MouseButton.LeftButton:
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
            self.sigDragged.emit(self)
            if ev.isFinish():
                self.moving = False
                self.sigPositionChangeFinished.emit(self)
        self.change_pen_signal.emit(("#363a45",float(self.getYPos())))

    def hoverEvent(self, ev):
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            hover = False
            self.setCursor(Qt.CursorShape.CrossCursor)
        
        if not self.isSelected:
            if (not ev.isExit()) and self.movable and ev.acceptDrags(QtCore.Qt.MouseButton.LeftButton):
                self.setMouseHover(True)
                self.addMarker('o', size=6)
            else:
                self.setMouseHover(False)
                self.clearMarkers()

    def setMouseHover(self, hover):
        ## Inform the item that the mouse is (not) hovering over it
        if self.mouseHovering == hover:
            return
        self.mouseHovering = hover
        if hover:
            # self.currentPen = self.hoverPen
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            # self.currentPen = self.pen
            self.setCursor(Qt.CursorShape.CrossCursor)
        self.update()
