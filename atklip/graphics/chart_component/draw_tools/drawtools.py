from PySide6.QtCore import QObject,QEvent
from typing import TYPE_CHECKING

from atklip.app_utils import *

from .roi import FiboSpecialROI, DEFAULTS_COLOR, DEFAULTS_FIBO,\
TextBoxROI, SpecialROI, CustomLineSegmentROI
from .horizontal_line import Horizontal_line
from .horizontal_ray import Horizontal_ray, HorizontalRayNoHandle
from .brush_path import PathROI
from .brush_rectangle import RectangleROI
from .fibo_retracement_1 import FiboROI
from .fibo_retracement_2 import FiboROI2
from .trend_lines import TrendlinesROI
from .vertical_line import Vertical_line
from .polylines import RangePolyLine

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

class DrawTool(QObject):
    def __init__(self, chart=None):
        super().__init__(chart)
        self.chart :Chart= chart
        self.num_fibo = 0
        self.num_fibo2 = 0
        self.num_trendline = 0
        self.num_vertical_line = 0
        self.num_dateprice_range = 0
        self.num_horizontal_line = 0
        self.num_horizontal_ray = 0
        self.num_path = 0
        self.num_rectangle = 0
        self.num_textbox = 0
        self.drawing_object = None
        self.draw_object_name = None
    
    def get_position_crosshair(self):
        return self.chart.vLine.getXPos(), self.chart.hLine.getYPos()
    
    def get_position_mouse_on_chart(self, ev: QEvent):
        if self.chart.magnet_on:
            pos_x, pos_y = self.get_position_crosshair()
        else:
            ev_pos = ev.position()
            pos_x = self.chart.vb.mapSceneToView(ev_pos).x()
            pos_y = self.chart.vb.mapSceneToView(ev_pos).y()
        return pos_x, pos_y
    
    def draw_trenlines(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        line = TrendlinesROI(positions=[[pos_x, pos_y],[pos_x, pos_y]], pen=("#2962ff"),drawtool=self)
        self.chart.addItem(line)
        self.num_trendline += 1
        module_name = "Trend Line " + str(self.num_trendline)
        line.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(line)
        self.drawing_object = line
        self.draw_object_name = "drawed_trenlines"

    def draw_verticallines(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        line = Vertical_line(pos=pos_x, movable=True,angle=90,pen=mkPen("#2962ff"), chart=self.chart)
        self.chart.addItem(line)
        self.num_vertical_line += 1
        module_name = "Vertital Line " + str(self.num_vertical_line)
        line.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(line)
        self.draw_object_name = None

    def draw_horizontal_line(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj = Horizontal_line(parent=self.chart,pos=pos_y, movable=True,angle=0,pen=mkPen("#2962ff"), chart=self.chart)
        self.chart.addItem(obj)
        self.num_horizontal_line += 1
        module_name = "Horizontal Line " + str(self.num_horizontal_line)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = None
    
    def draw_horizontal_ray(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj = Horizontal_ray(positions=[[pos_x, pos_y]], pen=("#2962ff"), chart=self.chart)
        self.chart.addItem(obj)
        self.num_horizontal_ray += 1
        module_name = "Horizontal Ray " + str(self.num_horizontal_ray)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = None

    def draw_fibo(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        r3a =FiboROI([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen=mkPen("green",width=1), fibo_level=self.custom_fibonacci_levels, color_rect=self.custom_colors_rect, color_line=self.custom_colors_lines, color_borders=self.custom_colors_borders,parent=self.chart.vb, main=self.chart)
    
        self.chart.addItem(r3a)
        self.num_fibo += 1
        module_name = "Fibo Retracement(I) " + str(self.num_fibo)
        r3a.setObjectName(module_name)
        self.drawing_object = r3a
        uid_obj = self.chart.objmanager.add(r3a)
        self.draw_object_name = "drawed_fibo_retracement"

    def draw_fibo_2(self, ev: QEvent):
        if not self._main_window.permission_fibo_advance:
            self.draw_object_name = None
            return
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        r3a_ =FiboROI2([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen=mkPen("green",width=1), 
                          parent=self.chart.vb, main=self.chart)

        self.chart.addItem(r3a_)
        self.num_fibo2 += 1
        module_name = "Fibo Retracement(II) " + str(self.num_fibo2)
        r3a_.setObjectName(module_name)
        self.drawing_object = r3a_
        uid_obj = self.chart.objmanager.add(r3a_)
        self.draw_object_name = "drawed_fibo_retracement_2"

    def draw_path(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        Path =PathROI(positions=[(pos_x, pos_y), (pos_x, pos_y)], pen=mkPen("#2962ff"),  chart=self.chart)
        self.chart.addItem(Path)
        self.num_path += 1
        module_name = "Path " + str(self.num_path)
        Path.setObjectName(module_name)
        self.drawing_object = Path
        uid_obj = self.chart.objmanager.add(Path)
        self.draw_object_name = "drawed_path"

    def draw_rectangle(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        Rectangle =RectangleROI([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen=mkPen("#2962ff",width=1),parent=self.chart.vb, main=self.chart)
        self.chart.addItem(Rectangle)
        self.num_rectangle += 1
        module_name = "Rectangle " + str(self.num_rectangle)
        Rectangle.setObjectName(module_name)
        self.drawing_object = Rectangle
        uid_obj = self.chart.objmanager.add(Rectangle)
        self.draw_object_name = "drawed_rectangle"

    def draw_text(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        TextBox = TextBoxROI(size=5,symbol="o",pen="green",brush = "green",parent=self.chart.vb, main=self.chart)
        TextBox.setPos(pos_x, pos_y)
        self.chart.addItem(TextBox)
        self.num_textbox += 1
        module_name = "TextBox " + str(self.num_textbox)
        TextBox.setObjectName(module_name)
        self.draw_object_name = None
        uid_obj = self.chart.objmanager.add(TextBox)

    def draw_date_price_range(self, ev):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        Date_price_range = RangePolyLine(self.chart.vb, self, [0, 0], closed=False, pen=mkPen('#fca326'), movable=True)
        Date_price_range.setPos(pos_x, pos_y)
        self.chart.addItem(Date_price_range)
        self.num_dateprice_range += 1
        module_name = "DatePrice Range " + str(self.num_dateprice_range)
        Date_price_range.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(Date_price_range)
        self.draw_object_name = "drawed_date_price_range"