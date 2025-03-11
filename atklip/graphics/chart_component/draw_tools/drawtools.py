from PySide6.QtCore import QObject,QEvent,QPoint
from typing import TYPE_CHECKING

from atklip.app_utils import *

from .TargetItem import TextBoxROI
from .horizontal_line import Horizontal_line
from .horizontal_ray import Horizontal_ray
from .brush_path import PathROI
from .rectangle import Rectangle
from .rotate_rectangle import RotateRectangle
from .fibo_retracement_1 import FiboROI
from .fibo_retracement_2 import FiboROI2
from .risk_reward_ratio import RickRewardRatio
from .trend_lines import TrendlinesROI
from .vertical_line import Vertical_line
from .polylines import RangePolyLine
from .base_arrow import BaseArrowItem
from .elip import Ellipse
from .circle import Circle
from .long_possiton import Longposition
from .short_possiton import Shortposition
from atklip.graphics.chart_component.graph_items.CustomTextItem import CenteredTextItem
from atklip.graphics.chart_component.draw_tools.TargetItem import ArrowItem


from .draw_tool_setting_wg import PopUpSettingMenu

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

class DrawTool(QObject):
    def __init__(self, chart=None):
        super().__init__(chart)
        self.chart :Chart= chart
        
        self.custom_fibonacci_levels = None
        self.custom_colors_rect = None
        self.custom_colors_lines = None
        self.custom_colors_borders = None
        self.fibo_reverse = False
        
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
        
        
    def show_popup_menu(self,obj):
        "obj: draw object"
        menu = PopUpSettingMenu(self.chart,obj)
        # menu.setParent(self.chart)
        self.chart.mouse_clicked_signal.connect(menu.delete)
        boundingRect = obj.mapRectToScene(obj.boundingRect())  
        x,y = boundingRect.x()+(boundingRect.width()-menu.width())/2, boundingRect.y()-menu.height()*3
        
        if x < 0:
            x= 5
        elif x > self.chart.width()-menu.width():
            x = self.chart.width() - menu.width()-5
        if y < 0:
            y = 5
        elif y > self.chart.height():
            y = self.chart.height() - menu.height()
        menu.move(QPoint(x, y))
        menu.show()
        # menu.flyout.exec(pos,FlyoutAnimationType.NONE)
        # menu.flyout.make(menu, pos, self.chart, FlyoutAnimationType.NONE)
    
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
        obj = TrendlinesROI(positions=[[pos_x, pos_y],[pos_x, pos_y]], pen="#2962ff",drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_trendline += 1
        module_name = "Trend Line " + str(self.num_trendline)
        obj.setObjectName(module_name)
        self.draw_object_name = "drawed_trenlines"
        
        obj.on_click.connect(self.show_popup_menu)
        
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)

    def draw_verticallines(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        obj = Vertical_line(pos=pos_x, movable=True,angle=90,pen="#2962ff", drawtool=self)
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_vertical_line += 1
        module_name = "Vertital Line " + str(self.num_vertical_line)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = None
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    

    def draw_horizontal_line(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj = Horizontal_line(pos=pos_y, movable=True,angle=0,pen="#2962ff", drawtool=self)
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_horizontal_line += 1
        module_name = "Horizontal Line " + str(self.num_horizontal_line)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = None
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    def draw_horizontal_ray(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        obj = Horizontal_ray(positions=[[pos_x, pos_y]], pen="#2962ff", drawtool=self)
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_horizontal_ray += 1
        module_name = "Horizontal Ray " + str(self.num_horizontal_ray)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = None
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)

    def draw_fibo(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj =FiboROI([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=True, removable=True, pen="#2962ff",parent=self.chart.vb, drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_rectangle += 1
        module_name = "Fibo Retracement(I) " + str(self.num_fibo)
        obj.setObjectName(module_name)
        
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_fibo_retracement"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)

    def draw_long_position(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        yrange = self.chart.yAxis.range
        xrange = self.chart.xAxis.range
        
        deltax = (xrange[1]-xrange[0])/6
        deltay = (yrange[1]-yrange[0])/6
        
        obj =Longposition(pos=[pos_x, pos_y], size=[deltax, deltay], drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_fibo += 1
        module_name = "Longposition " + str(self.num_fibo)
        obj.setObjectName(module_name)
        
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_long_position"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    def draw_short_position(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        yrange = self.chart.yAxis.range
        xrange = self.chart.xAxis.range
        
        deltax = (xrange[1]-xrange[0])/6
        deltay = (yrange[1]-yrange[0])/6
        
        obj =Shortposition(pos=[pos_x, pos_y], size=[deltax, deltay], drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_fibo += 1
        module_name = "Shortposition " + str(self.num_fibo)
        obj.setObjectName(module_name)
        
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_short_position"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    
    def draw_risk_reward_ratio(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        obj =RickRewardRatio([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=self.chart.vb, drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_fibo += 1
        module_name = "Risk Reward Ratio " + str(self.num_fibo)
        obj.setObjectName(module_name)
        
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_risk_reward_ratio"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    
    def draw_fibo_2(self, ev: QEvent):
        # pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        pos_x, pos_y = self.get_position_crosshair()
        # obj =FiboROI2([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen=mkPen("green",width=1), 
        #                   parent=self.chart.vb, drawtool=self)
        obj =FiboROI2([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=True, removable=True, pen="#2962ff",parent=self.chart.vb, drawtool=self)
        self.drawing_object = obj

        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_fibo2 += 1
        module_name = "Fibo Retracement(II) " + str(self.num_fibo2)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_fibo_retracement_2"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)

    def draw_path(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj =PathROI(positions=[(pos_x, pos_y), (pos_x, pos_y)], pen="#2962ff", drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_path += 1
        module_name = "Path " + str(self.num_path)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_path"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)

    def draw_rectangle(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj =Rectangle([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=self.chart.vb, drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_rectangle += 1
        module_name = "Rectangle " + str(self.num_rectangle)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_rectangle"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    def draw_rotate_rectangle(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj =RotateRectangle([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff",parent=self.chart.vb, drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_rectangle += 1
        module_name = "Rotate_rectangle " + str(self.num_rectangle)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_rotate_rectangle"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    def draw_ellipse(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj =Ellipse([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff", drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_rectangle += 1
        module_name = "Ellipse " + str(self.num_rectangle)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_ellipse"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    def draw_circle(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj =Circle([pos_x, pos_y], [0, 0],invertible=True,movable=True, resizable=False, removable=True, pen="#2962ff", drawtool=self)
        self.drawing_object = obj
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_rectangle += 1
        module_name = "Circle " + str(self.num_rectangle)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_circle"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    def draw_text(self, ev: QEvent):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self)

        obj.setPos((pos_x, pos_y))
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_textbox += 1
        module_name = "TextBox " + str(self.num_textbox)
        obj.setObjectName(module_name)
        self.draw_object_name = None
        uid_obj = self.chart.objmanager.add(obj)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
        obj.on_click.connect(self.show_popup_menu)
        
    # def draw_text(self, ev: QEvent):
    #     pos_x, pos_y = self.get_position_mouse_on_chart(ev)
    #     obj = CenteredTextItem(text = 'text',
    #                            chart = self.chart,
    #                             parent=self.chart.vb,
    #                             pen="green",brush = "green")
        
    #     obj.setPos(pos_x, pos_y)
    #     self.chart.add_item(obj)
    #     self.chart.drawtools.append(obj)
    #     self.num_textbox += 1
    #     module_name = "TextBox " + str(self.num_textbox)
    #     obj.setObjectName(module_name)
    #     self.draw_object_name = None
    #     uid_obj = self.chart.objmanager.add(obj)
    #     self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    #     # obj.on_click.connect(self.show_popup_menu)
    
    def draw_date_price_range(self, ev):
        pos_x, pos_y = self.get_position_mouse_on_chart(ev)
        obj = RangePolyLine([pos_x, pos_y], [0, 0], pen='#2962ff', movable=True,drawtool=self)
        self.drawing_object = obj
        # obj.setPos(pos_x, pos_y)
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_dateprice_range += 1
        module_name = "DatePrice Range " + str(self.num_dateprice_range)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_date_price_range"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    def draw_up_arrow(self, ev):
        pos_x, pos_y = self.get_position_crosshair()
        obj = ArrowItem(drawtool=self,angle=90,pen="green",brush = "green")
        obj.setPos(pos_x, pos_y)
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_dateprice_range += 1
        module_name = "ArrowItem " + str(self.num_dateprice_range)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_draw_up_arrow"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    def draw_down_arrow(self, ev):
        pos_x, pos_y = self.get_position_crosshair()
        obj = ArrowItem(drawtool=self,angle=270,pen="red",brush = "red")
        obj.setPos(pos_x, pos_y)
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_dateprice_range += 1
        module_name = "ArrowItem " + str(self.num_dateprice_range)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_draw_down_arrow"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)
    
    def draw_arrow(self, ev):
        pos_x, pos_y = self.get_position_crosshair()
        
        obj = ArrowItem(drawtool=self,angle=180,pen="pink",brush = "pink")
        
        obj.setPos(pos_x, pos_y)
        self.chart.add_item(obj)
        self.chart.drawtools.append(obj)
        self.num_dateprice_range += 1
        module_name = "ArrowItem " + str(self.num_dateprice_range)
        obj.setObjectName(module_name)
        uid_obj = self.chart.objmanager.add(obj)
        self.draw_object_name = "drawed_draw_down_arrow"
        obj.on_click.connect(self.show_popup_menu)
        self.chart.sig_reset_drawbar_favorite_btn.emit(obj)