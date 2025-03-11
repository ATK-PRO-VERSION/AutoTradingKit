
from PySide6.QtCore import Signal, Qt,QRectF,QPointF,QEvent,QPoint
from PySide6.QtGui import QPainter,QPicture
from atklip.app_utils.functions import mkBrush, mkPen
from atklip.graphics.pyqtgraph.Point import Point
from atklip.graphics.pyqtgraph.graphicsItems.TextItem import TextItem
from atklip.app_utils import percent_caculator, calculate_pl_with_fees,calculate_recommended_capital_base_on_risk,calculate_recommended_capital_base_on_loss_capital

from .base_rectangle import BaseRect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart
    from atklip.graphics.chart_component.draw_tools.drawtools import DrawTool


class Longposition(BaseRect):
    
    def __init__(self, pos, size, centered=False, sideScalers=False,drawtool=None,is_short=False,is_long=False, **args):
        super().__init__(pos, size, centered, sideScalers,is_short,is_long, **args)

        self.drawtool:DrawTool = drawtool
        self.chart:Chart = self.drawtool.chart
        self.has = {
            "y_axis_show":False,
            "name": "Long Position",
            "type": "longposition",
            "id": id,
            "inputs":{
                "capital": 1000,
                "proportion_closed":1,
                "is_risk":True,
                "risk_percentage":1,
                "loss_capital":100,
                "leverage":10, #5
                "taker_fee":0.05, #0.05
                "maker_fee":0.02, #0.02
                "order_type":"market"
                    },
            "styles":{
                    'pen': None,
                    'brush': mkBrush((43, 106, 255, 40)),
                    'above_brush': mkBrush((0, 180, 90, 60)),
                    'under_brush': mkBrush((180, 0, 0, 60)),
                    "lock":True,
                    "setting": True,
                    "delete":True,}
        }
        
        self.center_handle = self.addScaleHandle([1, 0], [0, 0], lockAspect=True)
        # self.addTranslateHandle([0, 0], [1, 0])
        self.up_handle = self.addScaleHandle([0, 1], [0, 0], lockAspect=True)
        
        self.under_part = BaseRect([0,-self.size().y()], size,is_long=True)
        self.under_part.setParentItem(self)

        self.under_part.mouseDragEvent = self.mouseDragEvent
        self.under_part.mouseClickEvent = self.mouseClickEvent
        self.under_part.mouseReleaseEvent = self.mouseReleaseEvent
        self.under_part.hoverEvent = self.hoverEvent
        
        self.under_part.addScaleHandle([1, 0], [0, 0], lockAspect=True,item=self.center_handle)
        self.under_handle=self.under_part.addScaleHandle([0, 0], [0, 1], lockAspect=True)
        
        
        self.textitem_up = TextItem("",color="#FFF")
        self.textitem_up.setParentItem(self)
        self.textitem_up.setAnchor((0.5,1))
        self.textitem_center = TextItem("",color="#7876")
        self.textitem_center.setParentItem(self)
        self.textitem_center.setAnchor((0.5,1))
        self.textitem_under = TextItem("",color="#0468")
        self.textitem_under.setParentItem(self.under_part)
        self.textitem_under.setAnchor((0.5,0))
        
        
        self.setbrushs()
    
    def set_seclected(self,ev):
        try:
            ev_pos = ev.position()
        except:
            ev_pos = ev.pos()
        
        
    def update_text(self):
        h0 = self.handles[0]['item'].pos()
        h1 = self.handles[1]['item'].pos()
        diff = h1 - h0

        h0_under_part = self.under_part.handles[0]['item'].pos()
        h1_under_part = self.under_part.handles[1]['item'].pos()
        diff_under_part = h1_under_part - h0_under_part

        point0_ = self.mapToParent(Point(h0))
        point1_ = self.mapToParent(Point(h1))
        point0_under_part_ = self.mapToParent(self.under_part.mapToParent(Point(h0_under_part)))
        # point1_under_part_ = self.mapToParent(self.under_part.mapToParent(Point(h1_under_part)))
        
        exit_price = point1_.y()
        stop_loss_price = point0_under_part_.y()
        entry_price = point0_.y()
                
        if exit_price == entry_price or stop_loss_price == entry_price:
            return
        profit_percent = percent_caculator(entry_price,exit_price)
        stoploss_percent = percent_caculator(entry_price,stop_loss_price)
        RR = 0
        if stoploss_percent != 0:
            RR = profit_percent/stoploss_percent
            
        
        
        if self.has["inputs"]["is_risk"]:
            recom_capital = calculate_recommended_capital_base_on_risk(entry_price=entry_price,stop_loss_price=stop_loss_price,
                                            total_capital=self.has["inputs"]["capital"],
                                            risk_percentage=self.has["inputs"]["risk_percentage"],
                                            leverage=self.has["inputs"]["leverage"],
                                            taker_fee=self.has["inputs"]["taker_fee"],
                                            maker_fee=self.has["inputs"]["maker_fee"],
                                            order_type=self.has["inputs"]["order_type"],
                                            )
        else:
            recom_capital = calculate_recommended_capital_base_on_loss_capital(entry_price=entry_price,stop_loss_price=stop_loss_price,
                                          loss_capital=self.has["inputs"]["loss_capital"],
                                          leverage=self.has["inputs"]["leverage"],
                                          taker_fee=self.has["inputs"]["taker_fee"],
                                          maker_fee=self.has["inputs"]["maker_fee"],
                                          order_type=self.has["inputs"]["order_type"],
                                          )
                
        stoploss = calculate_pl_with_fees(entry_price=entry_price,exit_price=stop_loss_price,
                                          capital=recom_capital,
                                          proportion_closed=self.has["inputs"]["proportion_closed"],
                                          leverage=self.has["inputs"]["leverage"],
                                          taker_fee=self.has["inputs"]["taker_fee"],
                                          maker_fee=self.has["inputs"]["maker_fee"],
                                          order_type=self.has["inputs"]["order_type"],
                                          is_stop_loss=True
                                          )
        
        profit = calculate_pl_with_fees(entry_price=entry_price,exit_price=exit_price,
                                          capital=recom_capital,
                                          proportion_closed=self.has["inputs"]["proportion_closed"],
                                          leverage=self.has["inputs"]["leverage"],
                                          taker_fee=self.has["inputs"]["taker_fee"],
                                          maker_fee=self.has["inputs"]["maker_fee"],
                                          order_type=self.has["inputs"]["order_type"],
                                          is_stop_loss=False
                                          )
        
        profit = profit
        stoploss = stoploss
        
        profit_amount = profit
        stoploss_amount = stoploss
        
        recom_quanty = recom_capital/entry_price
        
        qty_precision = f".{self.chart.quanty_precision}f"
        price_precision = f".{self.chart._precision}f"
        
        html_up = f"""
                <div style="text-align: center; border-radius: 5px solid #d1d4dc;">
                    <span style="color: #d1d4dc; font-size: 10pt;">Target {exit_price:{price_precision}} ({profit_percent:.2f}%), Amount {profit_amount:.2f}$</span>
                </div>
                """
        
        html_center = f"""
                <div style="text-align: center; border-radius: 5px solid #d1d4dc;">
                    <span style="color: #d1d4dc; font-size: 10pt;">Entry {entry_price:{price_precision}}, Qty {recom_quanty:{qty_precision}}</span>
                    <br>
                    <span style="color: #d1d4dc; font-size: 10pt;">R/R Ratio {RR:.2f}, Recom Capital {recom_capital:.2f}$</span>
                </div>
                """
                
        html_under = f"""
                <div style="text-align: center; border-radius: 5px solid #d1d4dc;">
                    <span style="color: #d1d4dc; font-size: 10pt;">Stop {stop_loss_price:{price_precision}} ({stoploss_percent:.2f}%), Amount -{stoploss_amount:.2f}$</span>
                </div>
                """
        
        
        # up_text= f"Target {exit_price:{price_precision}} ({profit_percent:.2f}%), Amount {profit_amount:.2f}$"
        # center_text= f"Entry {entry_price:{price_precision}}, Qty {recom_quanty:{qty_precision}}\nR/R Ratio {RR:.2f}, Recom Capital {recom_capital:.2f}$"
        # under_text= f"Stop {stop_loss_price:{price_precision}} ({stoploss_percent:.2f}%), Amount -{stoploss_amount:.2f}$"
        
        self.textitem_up.setHtml(html_up)
        self.textitem_center.setHtml(html_center)
        self.textitem_under.setHtml(html_under)
        
        
        # self.textitem_up.setText(up_text)
        # self.textitem_center.setText(center_text)
        # self.textitem_under.setText(under_text)

        r = self.textitem_up.textItem.boundingRect()
        tl = self.textitem_up.textItem.mapToParent(r.topLeft())
        br = self.textitem_up.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.textitem_up.anchor
        
        _pointf = Point(h1.x() - diff.x()/2, h1.y())
        _x = _pointf.x() #+r.width()/2
        _y = _pointf.y() + offset.y()/2
        self.textitem_up.setPos(Point(_x,_y))
        
        r = self.textitem_center.textItem.boundingRect()
        tl = self.textitem_center.textItem.mapToParent(r.topLeft())
        br = self.textitem_center.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.textitem_center.anchor
        
        _pointf = Point(h1.x() - diff.x()/2, h0.y())
        _x = _pointf.x() #+r.width()/2
        _y = _pointf.y() + offset.y()/8
        self.textitem_center.setPos(Point(_x,_y))
             
        r = self.textitem_under.textItem.boundingRect()
        tl = self.textitem_under.textItem.mapToParent(r.topLeft())
        br = self.textitem_under.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.textitem_under.anchor
        _pointf = Point(h1_under_part.x() - diff_under_part.x()/2, h1_under_part.y())
        _x = _pointf.x() #+r.width()/2
        _y = _pointf.y() - offset.y()/2
        self.textitem_under.setPos(Point(_x,_y))
        

    def setbrushs(self):
        self.setBrush(self.has["styles"]["above_brush"])
        self.under_part.setBrush(self.has["styles"]["under_brush"])
        self.under_part.update()
        self.update()
    
    def get_inputs(self):
        inputs =  {"capital":self.has["inputs"]["capital"],
                   "loss_capital":self.has["inputs"]["loss_capital"],
                    "proportion_closed":self.has["inputs"]["proportion_closed"],
                    "is_risk":self.has["inputs"]["is_risk"],
                    "risk_percentage":self.has["inputs"]["risk_percentage"],
                    "leverage":self.has["inputs"]["leverage"],
                    "taker_fee":self.has["inputs"]["taker_fee"],
                    "maker_fee":self.has["inputs"]["maker_fee"],
                    }
        return inputs
    
    def get_styles(self):
        styles =  {"above_brush":self.has["styles"]["above_brush"],
                    "under_brush":self.has["styles"]["under_brush"],
                    "lock":self.has["styles"]["lock"],
                    "delete":self.has["styles"]["delete"],
                    "setting":self.has["styles"]["setting"],}
        return styles
    
    def update_inputs(self,_input=None,_source=None):
        # _input = self.has["inputs"][_input]
        self.update()
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
        self.setbrushs() 

    def hoverEvent(self, ev: QEvent):
        hover = False
        if not ev.exit: # and not self.boundingRect().contains(ev.pos()):
            hover = True
            if not self.locked:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.textitem_up.setVisible(True)
            self.textitem_center.setVisible(True)
            self.textitem_under.setVisible(True)
            handles = self.handles + self.under_part.handles
            for handle in handles:
                handle['item'].setVisible(True)
        else:
            hover = False
            self.setCursor(Qt.CursorShape.CrossCursor)
            # self.textitem_up.setVisible(False)
            # self.textitem_center.setVisible(False)
            # self.textitem_under.setVisible(False)
            handles = self.handles + self.under_part.handles
            for handle in handles:
                handle['item'].setVisible(False)
    
    def mouseClickEvent(self, ev):
        super().mouseClickEvent(ev)   
    
    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent()

    def boundingRect(self):
        if self.handles:
            h0 = self.handles[0]['item'].pos()
            h1 = self.handles[-1]['item'].pos()
            
            if not self.h1:
                self.h1 = h1 
                self.h0 = h0
                self.picture = QPicture()
                painter = QPainter(self.picture)
                
                r = QRectF(0, 0, self.state['size'][0], self.state['size'][1])#.normalized()
                painter.setRenderHint(
                    QPainter.RenderHint.Antialiasing,
                    self._antialias
                )
                painter.setPen(mkPen(self.has["styles"]['pen']))
                painter.setBrush(self.has["styles"]["brush"])
                painter.translate(r.left(), r.top())
                painter.scale(r.width(), r.height())
                painter.drawRect(0, 0, 1, 1)
                if self.is_long:
                    painter.setPen(mkPen("red",width=1))
                    painter.drawLine(QPointF(0,0), QPointF(1,0))
                if self.is_short:
                    painter.setPen(mkPen("green",width=1))
                    painter.drawLine(QPointF(0,0), QPointF(1,0))
                painter.setPen(mkPen("green",width=1))
                painter.drawLine(QPointF(0,1), QPointF(1,1))
                painter.end()
                self.update_text()

            elif self.h1 == h1 and self.h0 == h0:
                if self.under_part.is_size_change:
                    self.update_text()
            else:
                self.picture = QPicture()
                painter = QPainter(self.picture)
                self.h1 = h1 
                self.h0 = h0
                
                r = QRectF(0, 0, self.state['size'][0], self.state['size'][1])#.normalized()
                painter.setRenderHint(
                    QPainter.RenderHint.Antialiasing,
                    self._antialias
                )
                painter.setPen(mkPen(self.has["styles"]['pen']))
                painter.setBrush(self.has["styles"]["brush"])
                painter.translate(r.left(), r.top())
                painter.scale(r.width(), r.height())
                painter.drawRect(0, 0, 1, 1)
                if self.is_long:
                    painter.setPen(mkPen("red",width=1))
                    painter.drawLine(QPointF(0,0), QPointF(1,0))
                if self.is_short:
                    painter.setPen(mkPen("green",width=1))
                    painter.drawLine(QPointF(0,0), QPointF(1,0))
                painter.setPen(mkPen("green",width=1))
                painter.drawLine(QPointF(0,1), QPointF(1,1))
                painter.end()
                self.update_text()
        return QRectF(0, -self.under_part.state['size'][1], self.state['size'][0], self.state['size'][1]+self.under_part.state['size'][1])#.normalized()
    
    def paint(self, p: QPainter, *args):
        self.picture.play(p)
    
        
    def mouseDragEvent(self, ev, axis=None):
        if ev.button == Qt.KeyboardModifier.ShiftModifier:
            return self.chart.vb.mouseDragEvent(ev, axis)
        if not self.locked:
            return super().mouseDragEvent(ev)
        elif self.locked:
            ev.ignore()
        ev.ignore()