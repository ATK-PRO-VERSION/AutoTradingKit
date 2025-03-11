
import datetime
import time
import traceback
from typing import Optional, Any, List, TYPE_CHECKING

from numpy import ceil, log10
import pytz
from PySide6.QtCore import Signal, QObject, QRunnable, Qt, QRectF, Slot
from PySide6.QtGui import QPicture, QPainter, QFont, QBrush, QCursor, QPen
from PySide6.QtWidgets import QGraphicsItem
from atklip.graphics.pyqtgraph import AxisItem, mkBrush, debug, mkPen, getConfigOption,Point, functions as fn

from atklip.app_utils import *

if TYPE_CHECKING:
    from .viewchart import Chart

class Axis:
    TICK_FORMAT = "Tick_Format"  # "Tick format"
    DATETIME = "DateTime"
    TIME = "Time"
    CATEGORY = "Category"
    CATEGORIES = "Categories"
    DURATION = "Duration"
    DURATION_FORMAT = "Duration_Format"
    # Duration format options
    DF_SHORT = "short"
    DF_LONG = "long"


class CustomDateAxisItem(AxisItem):

    def __init__(self, orientation,context=None, pen=None, textPen=None, axisPen=None, linkView=None, parent=None, maxTickLength=-5,
                 showValues=True, vb=None, **kwargs) -> None:
        self.tick_position_indexes: Optional[List] = None
        super().__init__(orientation, pen=pen, textPen=textPen, linkView=linkView, parent=parent,
                         maxTickLength=maxTickLength, showValues=showValues, **kwargs)
        
        self.style['tickTextOffset'] = [1, 1]
        # self.style['textFillLimits'] = [ 
        #                                 # (0, 0.8),  
        #                                 (2, 0.8),   
        #                                 (4, 0.6),    
        #                                 ]
        self.style['maxTickLevel'] = 2
        self.style['maxTextLevel'] = 2
        
        self.setFixedHeight(25)
        self.setContentsMargins(1,1,1,1)
        
        self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.setTickFont("Segoe UI")
        self.context:Chart = context
        self.vb = vb
        self.last_color,self.last_price = "#eaeaea", 00000
        self.dict_objects = {}
        
        # Fixing pyqtgraph bug, not setting textPen properly
        if textPen is None:
            self.setTextPen()
        else:
            self.setTextPen(textPen)
        # Set axisPen
        if axisPen is None:
            self.setAxisPen()
        else:
            self.setAxisPen(axisPen)
        # Tick format
        self.tick_format = kwargs.get(Axis.TICK_FORMAT, None)
        self.categories = kwargs.get(Axis.CATEGORIES, [])
        self.df_short = kwargs.get(Axis.DURATION_FORMAT, Axis.DF_SHORT) == Axis.DF_SHORT
        if self.tick_format == Axis.CATEGORY:
            # Override ticks spacing and set spacing 1 with step 1
            self.setTickSpacing(3, 1)

        self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        

        self.last_value = None
        
    def axisPen(self) -> QPen:
        """Get axis pen"""
        if self._axisPen is None:
            return mkPen(getConfigOption('foreground'))
        return mkPen(self._axisPen)

    def setAxisPen(self, *args: Any, **kwargs: Any) -> None:
        """
        Set axis pen used for drawing axis line.
        If no arguments are given, the default foreground color will be used.
        """
        self.picture = None
        if args or kwargs:
            self._axisPen = mkPen(*args, **kwargs)
        else:
            self._axisPen = mkPen(getConfigOption('foreground'))
        self._updateLabel()
    
    def get_times_via_indexs(self,index):
        #value =  self.context.jp_candle.candles[0].time + (index-self.context.jp_candle.candles[0].index)*(self.context.jp_candle.candles[1].time-self.context.jp_candle.candles[0].time)
        ohlc = self.context.jp_candle.map_index_ohlcv.get(index)
        if ohlc:
            value = ohlc.time
            return value
        return None

    def tickStrings(self, indexs: list, scale: float, spacing: float) -> list:
        """Convert ticks into final strings"""
        values = indexs
        tick_strings = indexs
        try:
            vls = []
            for index in indexs:
                value = self.get_times_via_indexs(index)
                if value:
                    vls.append(value)
            values = vls
            
            # if self.context.jp_candle.candles != []:
            #     try:
            #         vls = []
            #         for index in indexs:
            #             value = self.get_times_via_indexs(index)
            #             if value:
            #                 vls.append(value)
            #         # values = [self.get_times_via_indexs(index) for index in indexs if self.get_times_via_indexs(index)]
            #         values = vls
            #     except Exception as e:
            #         pass

            if self.tick_format == Axis.DATETIME:
                # timezone_offset = -time.timezone // 3600
                tz = datetime.datetime.now().astimezone().tzinfo
                # tick_strings = [datetime.datetime.fromtimestamp(value, tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S") for value in values]
                tick_strings = [datetime.datetime.fromtimestamp(value,tz=tz).strftime("%Y-%m-%d %H:%M:%S") for value in values]
            elif self.tick_format == Axis.TIME:
                # timezone_offset = -time.timezone // 3600
                # tick_strings = [datetime.datetime.fromtimestamp(value, tz=pytz.utc).strftime("%H:%M:%S") for value in values]
                tz = datetime.datetime.now().astimezone().tzinfo
                tick_strings = [datetime.datetime.fromtimestamp(value,tz=tz).strftime("%H:%M:%S") for value in values]
            else:
                tick_strings = super().tickStrings(values, scale, spacing)
        except Exception as e:
            tick_strings = super().tickStrings(values, scale, spacing)
        return tick_strings

    def drawPicture(self, p,  axisSpec, tickSpecs, textSpecs, ):
        #profiler = debug.Profiler()

        p.setRenderHint(p.RenderHint.Antialiasing, False)
        p.setRenderHint(p.RenderHint.TextAntialiasing, True)

        ## draw long line along axis
        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)
        # p.translate(0.5,0)  ## resolves some damn pixel ambiguity

        ## draw ticks
        for pen, p1, p2 in tickSpecs:
            p.setPen(pen)
            p.drawLine(p1, p2)
        #profiler('draw ticks')

        # Draw all text
        if self.style['tickFont'] is not None:
            p.setFont(self.style['tickFont'])
        p.setPen(self.textPen())
        bounding = self.boundingRect().toAlignedRect()
        p.setClipRect(bounding)

        for rect, flags, text in textSpecs:
            # print(rect)
            p.drawText(rect, int(flags), text)

        # self.drawvalue(p ,axisSpec, tickSpecs, textSpecs,color="#363a45",value=self.last_value)
        #profiler('draw text')
        self.draw_xcross_hair(p, color="#363a45",price=self.last_value)
        
        if self.dict_objects != {}:
            for item in list(self.dict_objects.keys()):
                if self.dict_objects[item] == True:
                    if hasattr(item, 'get_xaxis_param'):
                        price,color = item.get_xaxis_param()
                        if price != None:
                            self.draw_object_value(p,price,color=color)
        
        #self.draw_vertical_line(p)

    def draw_value(self,painter, rect,color, text):
        # Set up the pen for drawing the rectangle
        pen = QPen(Qt.white, 0.1, Qt.SolidLine)
        painter.setPen(pen)

        # Set up the brush for filling the rectangle
        brush = QBrush(mkBrush(color))
        painter.setBrush(brush)

        # Draw the rectangle
        painter.drawRect(rect)

        # Set up the font for drawing the text
        font = QFont('Segoe UI', 10, QFont.DemiBold)
        painter.setFont(font)

        # Calculate the text rect and center it in the rectangle
        text_rect = painter.boundingRect(rect, Qt.AlignCenter, text)

        # Draw the text
        painter.drawText(text_rect, Qt.AlignCenter, text)

    def draw_xcross_hair(self, p, color, price):
        if price != None:
            #print(price)
            try:
                bounds = self.mapRectFromParent(self.geometry())
                x,y,w,h = bounds.x(), bounds.y(),bounds.width(), bounds.height()
                range1, range2 = self.range[0], self.range[1]
                position = (price-range1)*(w-x)/(range2-range1)
                # print(245, l_price, self.vb.price_line_color)
                price_rect = QRectF(position-58,2,116,22)
                tz = datetime.datetime.now().astimezone().tzinfo
                tick_strings = datetime.datetime.fromtimestamp(self.get_times_via_indexs(price), tz=tz).strftime("%Y-%m-%d %H:%M:%S")
                self.draw_value(p,price_rect,color,str(tick_strings))
            except Exception as e:
                # traceback.print_exc(e)
                pass
        else:
            pass

    # k nen dung cho xasix
    def drawvalue(self, p ,axisSpec, tickSpecs, textSpecs,**kwargs):
        color = kwargs['color']
        price = kwargs['value']
        self.last_value = price  
        
        #profiler = debug.Profiler()
        p.setRenderHint(p.RenderHint.Antialiasing, False)
        p.setRenderHint(p.RenderHint.TextAntialiasing, True)

        ## draw long line along axis
        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)
        # p.translate(0.5,0)  ## resolves some damn pixel ambiguity

        ## draw ticks
        #print("len(tickSpecs), len(textSpecs)",len(tickSpecs), len(textSpecs))
        
        for pen, p1, p2 in tickSpecs:
            p.setPen(pen)
            p.drawLine(p1, p2)
        #profiler('draw ticks')
        # Draw all text
        if self.style['tickFont'] is not None:
            p.setFont(self.style['tickFont'])
        p.setPen(self.textPen())
        bounding = self.boundingRect().toAlignedRect()
        p.setClipRect(bounding)


        for rect, flags, text in textSpecs:
            p.drawText(rect, int(flags), text)
        
        if kwargs['value'] != None:
            try:
                bounds = self.mapRectFromParent(self.geometry())
                x,y,w,h = bounds.x(), bounds.y(),bounds.width(), bounds.height()
                range1, range2 = self.range[0], self.range[1]
                #step = (w-x)/(range2-range1)
                
                
                #print('x,y,w,h,range1, range2, step', x,y,w,h, range1, range2, step)
                
                #l_price = self.vb.price_line.getPos()[1]
                # print(242, global_var.last_price[global_var.symbol], self.vb.price_line.getPos())
                position = (price-range1)*(w-x)/(range2-range1)
                # print(245, l_price, self.vb.price_line_color)
                price_rect = QRectF(position-58,2,116,22)
                #self.draw_lastprice(p,price_rect,global_var.last_color,str(global_var.last_price[global_var.symbol]))
                tz = datetime.datetime.now().astimezone().tzinfo
                tick_strings = datetime.datetime.fromtimestamp(price, tz=tz).strftime("%Y-%m-%d %H:%M:%S")
                
                
                self.draw_value(p,price_rect,color,str(tick_strings))
                
            except Exception as e:
                # traceback.print_exc()
                pass
        else:
            if self.context.lastMousePositon != None:
                try:
                    bounds = self.mapRectFromParent(self.geometry())
                    x,y,w,h = bounds.x(), bounds.y(),bounds.width(), bounds.height()
                    range1, range2 = self.range[0], self.range[1]
                    #step = (w-x)/(range2-range1)
                    #l_price = self.vb.price_line.getPos()[1]
                    # print(242, global_var.last_price[global_var.symbol], self.vb.price_line.getPos())
                    position = (price-range1)*(w-x)/(range2-range1)
                    # print(245, l_price, self.vb.price_line_color)
                    price_rect = QRectF(position-58,2,116,22)
                    #self.draw_lastprice(p,price_rect,global_var.last_color,str(global_var.last_price[global_var.symbol]))
                    tz = datetime.datetime.now().astimezone().tzinfo
                    tick_strings = datetime.datetime.fromtimestamp(price, tz=tz).strftime("%Y-%m-%d %H:%M:%S")

                    self.draw_value(p,price_rect,color,str(tick_strings))
                    
                except Exception as e:
                    # traceback.print_exc()
                    pass
        #profiler('draw text')
    
    def change_value(self, args):
        #print(args, type(args))
        
        if len(args) == 1:
            color,price =args[0][0], args[0][1]
        else:
            color,price = args[0], args[1]
        self.last_value =  price
        #profiler = debug.Profiler()
        try:
            picture = QPicture()
            painter = QPainter(picture)
            if self.style["tickFont"]:
                painter.setFont(self.style["tickFont"])
            specs = self.generateDrawSpecs(painter)
            #profiler('generate specs')
            if specs is not None:
                self.drawPicture(painter, *specs, )
                # self.drawvalue(painter, *specs,color="#363a45",value=price)
                #profiler('draw picture')
        finally:
            
            painter.setRenderHint(painter.RenderHint.Antialiasing, True)  
            painter.setRenderHint(painter.RenderHint.TextAntialiasing, True)
            
            self.picture = picture
            self.picture.play(painter)
            painter.end()
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()

    def draw_vertical_line(self,p):
        #print("đa vao day")
        if "vertical_line" in self.kwargs.keys():
            if self.kwargs["vertical_line"] != []:
                for id in self.kwargs["vertical_line"]:
                    try:
                        line = self.context.ObjectManager.get(id)
                        if line is None:
                            self.kwargs["vertical_line"].remove(id)
                            continue
                        price = round(line.getXPos(),1)
                        color = "#2962ff"
                        bounds = self.mapRectFromParent(self.geometry())
                        x,y,w,h = bounds.x(), bounds.y(),bounds.width(), bounds.height()
                        range1, range2 = self.range[0], self.range[1]
                        step = (w-x)/(range2-range1)
                        position = (price-range1)*step 
                        price_rect = QRectF(position-58,y,116,22)
                        tz = datetime.datetime.now().astimezone().tzinfo
                        tick_strings = datetime.datetime.fromtimestamp(price, tz=tz).strftime("%Y-%m-%d %H:%M:%S")

                        self.draw_value(p,price_rect,color,str(tick_strings))
                        
                    except Exception as e:
                        # traceback.print_exc()
                        pass
    
    def wheelEvent(self, event):
        
        #print("vao daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        
        lv = self.linkedView()
        if lv is None:
            return
        # Did the event occur inside the linked ViewBox (and not over the axis iteself)?
        if not lv.sceneBoundingRect().contains(event.scenePos()):
            event.ignore()
            return
        if self.sceneBoundingRect().contains(event.scenePos()):
            # pass event to linked viewbox with appropriate single axis zoom parameter
            #print(self.orientation)
            if self.orientation in ['left', 'right']:
                lv.wheelEvent(event, axis=1)
            else:
                lv.wheelEvent(event, axis=0)
        event.accept()

    def mouseDragEvent(self, event):
        #print("drag la vao day......")
        self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        lv = self.linkedView()   # Link den ViewBox
        if lv is None:
            return
        #print(lv)
        
        # Did the mouse down event occur inside the linked ViewBox (and not the axis)?
        # if not lv.sceneBoundingRect().contains(event.buttonDownScenePos()):
        #     event.ignore()
        #     return
        # tr = self.vb.targetRect()
        # x0 = tr.left()
        # x1 = tr.right()
        # dif = event.screenPos() - event.lastScreenPos()
        # print(326, x1-x0, dif)
            
        if self.orientation in ['left', 'right']:
            return lv.mouseDragEvent(event, axis=1)
        else:
            # if x1 - x0 >= 1440 and dif.x() > 0:
            #     "giới hạn 1440 candle trên viewchart"
            #     return
            return lv.mouseDragEvent(event, axis=0)
    

class CustomPriceAxisItem(AxisItem):
    update_basement_feature_signal = Signal()
    
    def __init__(self, orientation, context=None,pen=None, textPen=None, tickPen=None, linkView=None, parent=None, maxTickLength=-5, showValues=True, vb=None, **args):
        
        super().__init__(orientation,
            pen=pen,
            textPen=textPen,
            tickPen = tickPen,
            linkView=linkView,
            parent=parent,
            maxTickLength=maxTickLength,
            showValues=showValues,
            **args,)
        
        # super().__init__(orientation, pen, textPen, tickPen, linkView, parent, maxTickLength, showValues, text, units, unitPrefix, **args)
        self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.setTickFont("Segoe UI")
        self.setContentsMargins(1,1,1,1)
        self.vb = vb
        self.context = context
        self._precision = f".{self.context._precision}f"
                
        self.cross_color,self.cross_price = "#eaeaea", None

        self.dict_objects = {}
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
    def generateDrawSpecs(self, p):
        """
        Calls tickValues() and tickStrings() to determine where and how ticks should
        be drawn, then generates from this a set of drawing commands to be
        interpreted by drawPicture().
        """
        #profiler = debug.Profiler()
        if self.style['tickFont'] is not None:
            p.setFont(self.style['tickFont'])
        bounds = self.mapRectFromParent(self.geometry())

        linkedView = self.linkedView()
        if linkedView is None or self.grid is False:
            tickBounds = bounds
        else:
            tickBounds = linkedView.mapRectToItem(self, linkedView.boundingRect())

        left_offset = -1.0
        right_offset = 1.0
        top_offset = -1.0
        bottom_offset = 1.0
        if self.orientation == 'left':
            span = (bounds.topRight() + Point(left_offset, top_offset),
                    bounds.bottomRight() + Point(left_offset, bottom_offset))
            tickStart = tickBounds.right()
            tickStop = bounds.right()
            tickDir = -1
            axis = 0
        elif self.orientation == 'right':
            span = (bounds.topLeft() + Point(right_offset, top_offset),
                    bounds.bottomLeft() + Point(right_offset, bottom_offset))
            tickStart = tickBounds.left()
            tickStop = bounds.left()
            tickDir = 1
            axis = 0
        elif self.orientation == 'top':
            span = (bounds.bottomLeft() + Point(left_offset, top_offset),
                    bounds.bottomRight() + Point(right_offset, top_offset))
            tickStart = tickBounds.bottom()
            tickStop = bounds.bottom()
            tickDir = -1
            axis = 1
        elif self.orientation == 'bottom':
            span = (bounds.topLeft() + Point(left_offset, bottom_offset),
                    bounds.topRight() + Point(right_offset, bottom_offset))
            tickStart = tickBounds.top()
            tickStop = bounds.top()
            tickDir = 1
            axis = 1
        else:
            raise ValueError("self.orientation must be in ('left', 'right', 'top', 'bottom')")
        #print tickStart, tickStop, span

        ## determine size of this item in pixels
        points = list(map(self.mapToDevice, span))
        if None in points:
            return
        lengthInPixels = Point(points[1] - points[0]).length()
        if lengthInPixels == 0:
            return

        # Determine major / minor / subminor axis ticks
        if self._tickLevels is None:
            tickLevels = self.tickValues(self.range[0], self.range[1], lengthInPixels)
            tickStrings = None
        else:
            ## parse self.tickLevels into the formats returned by tickLevels() and tickStrings()
            tickLevels = []
            tickStrings = []
            for level in self._tickLevels:
                values = []
                strings = []
                tickLevels.append((None, values))
                tickStrings.append(strings)
                for val, strn in level:
                    values.append(val)
                    strings.append(strn)

        ## determine mapping between tick values and local coordinates
        dif = self.range[1] - self.range[0]
        if dif == 0:
            xScale = 1
            offset = 0
        else:
            if axis == 0:
                xScale = -bounds.height() / dif
                offset = self.range[0] * xScale - bounds.height()
            else:
                xScale = bounds.width() / dif
                offset = self.range[0] * xScale

        xRange = [x * xScale - offset for x in self.range]
        xMin = min(xRange)
        xMax = max(xRange)

        #profiler('init')

        tickPositions = [] # remembers positions of previously drawn ticks

        ## compute coordinates to draw ticks
        ## draw three different intervals, long ticks first
        tickSpecs = []
        for i in range(len(tickLevels)):
            tickPositions.append([])
            ticks = tickLevels[i][1]

            ## length of tick
            tickLength = self.style['tickLength'] / ((i*0.5)+1.0)
                
            lineAlpha = self.style["tickAlpha"]
            if lineAlpha is None:
                lineAlpha = 255 / (i+1)
                if self.grid is not False:
                    lineAlpha *= self.grid/255. * fn.clip_scalar((0.05  * lengthInPixels / (len(ticks)+1)), 0., 1.)
            elif isinstance(lineAlpha, float):
                lineAlpha *= 255
                lineAlpha = max(0, int(round(lineAlpha)))
                lineAlpha = min(255, int(round(lineAlpha)))
            elif isinstance(lineAlpha, int):
                if (lineAlpha > 255) or (lineAlpha < 0):
                    raise ValueError("lineAlpha should be [0..255]")
            else:
                raise TypeError("Line Alpha should be of type None, float or int")
            tickPen = self.tickPen()
            if tickPen.brush().style() == QtCore.Qt.BrushStyle.SolidPattern: # only adjust simple color pens
                tickPen = QtGui.QPen(tickPen) # copy to a new QPen
                color = QtGui.QColor(tickPen.color()) # copy to a new QColor
                color.setAlpha(int(lineAlpha)) # adjust opacity                
                tickPen.setColor(color)

            for v in ticks:
                ## determine actual position to draw this tick
                x = (v * xScale) - offset
                if x < xMin or x > xMax:  ## last check to make sure no out-of-bounds ticks are drawn
                    tickPositions[i].append(None)
                    continue
                tickPositions[i].append(x)

                p1 = [x, x]
                p2 = [x, x]
                p1[axis] = tickStart
                p2[axis] = tickStop
                if self.grid is False:
                    p2[axis] += tickLength*tickDir
                tickSpecs.append((tickPen, Point(p1), Point(p2)))
        #profiler('compute ticks')


        if self.style['stopAxisAtTick'][0] is True:
            minTickPosition = min(map(min, tickPositions))
            if axis == 0:
                stop = max(span[0].y(), minTickPosition)
                span[0].setY(stop)
            else:
                stop = max(span[0].x(), minTickPosition)
                span[0].setX(stop)
        if self.style['stopAxisAtTick'][1] is True:
            maxTickPosition = max(map(max, tickPositions))
            if axis == 0:
                stop = min(span[1].y(), maxTickPosition)
                span[1].setY(stop)
            else:
                stop = min(span[1].x(), maxTickPosition)
                span[1].setX(stop)
        axisSpec = (self.pen(), span[0], span[1])


        textOffset = self.style['tickTextOffset'][axis]  ## spacing between axis and text
        #if self.style['autoExpandTextSpace'] is True:
            #textWidth = self.textWidth
            #textHeight = self.textHeight
        #else:
            #textWidth = self.style['tickTextWidth'] ## space allocated for horizontal text
            #textHeight = self.style['tickTextHeight'] ## space allocated for horizontal text

        textSize2 = 0
        lastTextSize2 = 0
        textRects = []
        textSpecs = []  ## list of draw

        # If values are hidden, return early
        if not self.style['showValues']:
            return (axisSpec, tickSpecs, textSpecs)

        for i in range(min(len(tickLevels), self.style['maxTextLevel']+1)):
            ## Get the list of strings to display for this level
            if tickStrings is None:
                spacing, values = tickLevels[i]
                strings = self.tickStrings(values, self.autoSIPrefixScale * self.scale, spacing)
            else:
                strings = tickStrings[i]

            if len(strings) == 0:
                continue

            ## ignore strings belonging to ticks that were previously ignored
            for j in range(len(strings)):
                if tickPositions[i][j] is None:
                    strings[j] = None

            ## Measure density of text; decide whether to draw this level
            rects = []
            for s in strings:
                if s is None:
                    rects.append(None)
                else:
                    
                    br = p.boundingRect(QtCore.QRectF(0, 0, 100, 100), QtCore.Qt.AlignmentFlag.AlignCenter, s)
                    ## boundingRect is usually just a bit too large
                    ## (but this probably depends on per-font metrics?)
                    br.setHeight(br.height() * 0.8)

                    rects.append(br)
                    textRects.append(rects[-1])

            if len(textRects) > 0:
                ## measure all text, make sure there's enough room
                if axis == 0:
                    textSize = np.sum([r.height() for r in textRects])
                    textSize2 = np.max([r.width() for r in textRects])
                else:
                    textSize = np.sum([r.width() for r in textRects])
                    textSize2 = np.max([r.height() for r in textRects])
            else:
                textSize = 0
                textSize2 = 0

            if i > 0:  ## always draw top level
                ## If the strings are too crowded, stop drawing text now.
                ## We use three different crowding limits based on the number
                ## of texts drawn so far.
                textFillRatio = float(textSize) / lengthInPixels
                finished = False
                for nTexts, limit in self.style['textFillLimits']:
                    if len(textSpecs) >= nTexts and textFillRatio >= limit:
                        finished = True
                        break
                if finished:
                    break
            
            lastTextSize2 = textSize2

            #spacing, values = tickLevels[best]
            #strings = self.tickStrings(values, self.scale, spacing)
            # Determine exactly where tick text should be drawn
            for j in range(len(strings)):
                vstr = strings[j]
                if vstr is None: ## this tick was ignored because it is out of bounds
                    continue
                x = tickPositions[i][j]
                #textRect = p.boundingRect(QtCore.QRectF(0, 0, 100, 100), QtCore.Qt.AlignmentFlag.AlignCenter, vstr)
                textRect = rects[j]
                height = textRect.height()
                width = textRect.width()
                #self.textHeight = height
                offset = max(0,self.style['tickLength']) + textOffset

                rect = QtCore.QRectF()
                if self.orientation == 'left':
                    alignFlags = QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter
                    rect = QtCore.QRectF(tickStop-offset-width, x-(height/2), width, height)
                elif self.orientation == 'right':
                    alignFlags = QtCore.Qt.AlignmentFlag.AlignVCenter|QtCore.Qt.AlignmentFlag.AlignVCenter
                    rect = QtCore.QRectF(tickStop+2*offset, x-(height/2), width, height)
                elif self.orientation == 'top':
                    alignFlags = QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignBottom
                    rect = QtCore.QRectF(x-width/2., tickStop-offset-height, width, height)
                elif self.orientation == 'bottom':
                    alignFlags = QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignTop
                    rect = QtCore.QRectF(x-width/2., tickStop+offset, width, height)

                textFlags = alignFlags | QtCore.Qt.TextFlag.TextDontClip    
                #p.setPen(self.pen())
                #p.drawText(rect, textFlags, vstr)

                br = self.boundingRect()
                if not br.contains(rect):
                    continue

                textSpecs.append((rect, textFlags, vstr))
        #profiler('compute text')

        ## update max text size if needed.
        self._updateMaxTextSize(lastTextSize2)

        return (axisSpec, tickSpecs, textSpecs)
    def tickStrings(self, values, scale, spacing):
        """Return the strings that should be placed next to ticks. This method is called
        when redrawing the axis and is a good method to override in subclasses.
        The method is called with a list of tick values, a scaling factor (see below), and the
        spacing between ticks (this is required since, in some instances, there may be only
        one tick and thus no other way to determine the tick spacing)

        The scale argument is used when the axis label is displaying units which may have an SI scaling prefix.
        When determining the text to display, use value*scale to correctly account for this prefix.
        For example, if the axis label's units are set to 'V', then a tick value of 0.001 might
        be accompanied by a scale value of 1000. This indicates that the label is displaying 'mV', and
        thus the tick should display 0.001 * 1000 = 1.
        """
        if self.logMode:
            return self.logTickStrings(values, scale, spacing)

        places = max(0, ceil(-log10(spacing*scale)))
        strings = []
        for v in values:
            vs = v * scale
            if abs(vs) < .0000001 or abs(vs) >= 100:
                vstr = "%g" % vs
            else:
                vstr = ("%%0.%df" % places) % vs
            if "e" in vstr:
                vstr = self.convert2float(vstr)
            strings.append(vstr)
        return strings
    def convert2float(self,number:str):
        new_number = number
        if 'e-' in number:
            if number.startswith("-"):
                number = number.split("-")
                value = number[1].strip("e")
                notional = number[2]
                new_number = "-0."
                for i in range(int(notional)-1):
                    new_number+="0"
                new_number+=f"{value}"
            
            elif number.startswith("+"):
                number = number[1:]
                number = number.split("-")
                value = number[0].strip("e")
                notional = number[1]
                new_number = "0."
                for i in range(int(notional)-1):
                    new_number+="0"
                new_number+=f"{value}"
            else:
                number = number.split("-")
                value = number[0].strip("e")
                notional = number[1]
                new_number = "0."
                for i in range(int(notional)-1):
                    new_number+="0"
                new_number+=f"{value}"
        elif 'e+' in number:
            
            if number.startswith("+"):
                number = number.split("+")
                value = number[1].strip("e")
                notional = number[2]
                new_number = f"{value}"
                for i in range(int(notional)-1):
                    new_number+="0"
            elif number.startswith("-"):
                number = number[1:]
                number = number.split("+")
                value = number[0].strip("e")
                notional = number[1]
                new_number = f"{value}"
                for i in range(int(notional)-1):
                    new_number+="0"
            else:
                number = number.split("+")
                value = number[0].strip("e")
                notional = number[1]
                new_number = f"{value}"
                for i in range(int(notional)-1):
                    new_number+="0"
        return new_number
    
    def draw_value(self,painter, rect,color, text):
        # Set up the pen for drawing the rectangle
        if "e" in text:
            text = self.convert2float(text)
        
        
        text = f"{float(text):{self._precision}}"
        

        pen = QPen(Qt.white, 0.1, Qt.SolidLine)
        painter.setPen(pen)

        # Set up the brush for filling the rectangle
        brush = QBrush(mkBrush(color))
        painter.setBrush(brush)

        # Draw the rectangle
        painter.drawRect(rect)

        # Set up the font for drawing the text
        font = QFont("Segoe UI", 10, QFont.DemiBold)
        painter.setFont(font)

        # Calculate the text rect and center it in the rectangle
        #text_rect = painter.boundingRect(rect, Qt.AlignCenter, text)

        # Draw the text
        painter.drawText(rect, Qt.AlignCenter, text)
    
    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        # super().drawPicture(p, axisSpec, tickSpecs, textSpecs)
        self._precision = f".{self.context.get_precision()}f"
        p.setRenderHint(p.RenderHint.Antialiasing, False)
        p.setRenderHint(p.RenderHint.TextAntialiasing, True)
        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)
        for pen, p1, p2 in tickSpecs:
            p.setPen(pen)
            p.drawLine(p1, p2)
        #profiler('draw ticks')
        # Draw all text
        if self.style['tickFont'] is not None:
            p.setFont(self.style['tickFont'])
        p.setPen(self.textPen())
        bounding = self.boundingRect().toAlignedRect()
        p.setClipRect(bounding)

        for rect, flags, text in textSpecs:
            if "e" in text:
                text = self.convert2float(text)
            # print(self._precision)
            text = f"{float(text):{self._precision}}"
            p.drawText(rect, int(flags), text)
        
        self.paint_crosshair(p)

        if self.dict_objects != {}:
            for item in list(self.dict_objects.keys()):
                if self.dict_objects[item] == True:
                    if hasattr(item, 'get_yaxis_param'):
                        price,color = item.get_yaxis_param()
                        if price != None:
                            
                            self.draw_object_value(p,price,color=color)
    def paint_crosshair(self,p):
        """draw cross hair"""
        color = self.cross_color
        price = self.cross_price
        if price != None:
            try:
                bounds = self.mapRectFromParent(self.geometry())
                x,y,w,h = bounds.x(), bounds.y(),bounds.width(), bounds.height()
                range1, range2 = self.range[0], self.range[1]
                step = (h-y)/(range2-range1)
                position = (range2-price)*step 
                price_rect = QRectF(x,position-11,w,22)
                self.draw_value(p,price_rect,color,str(price))
            except Exception as e:
                # traceback.print_exc(e)
                pass
        else:
            pass
            # if self.context.lastMousePositon != None:
            #     try:
            #         bounds = self.mapRectFromParent(self.geometry())
            #         x,y,w,h = bounds.x(), bounds.y(),bounds.width(), bounds.height()
            #         range1, range2 = self.range[0], self.range[1]
            #         step = (h-y)/(range2-range1)
            #         position = (range2-self.context.lastMousePositon.y())*step 
            #         price_rect = QRectF(x,position-9,w,18)
            #         "xem lai cho update value tren truc y"
            #         #self.draw_value(p,price_rect,color,str(self.vb.round_price_trading_rules(self.vb.symbol, self.context.lastMousePositon.y())))
            #     except Exception as e:
            #         traceback.print_exc()
            #         pass
        # #profiler('draw text')
    # k dung` cai nay`
    def draw_object_value(self,p,price,color="#2962ff"):
        bounds = self.mapRectFromParent(self.geometry())
        x,y,w,h = bounds.x(), bounds.y(),bounds.width(), bounds.height()
        range1, range2 = self.range[0], self.range[1]
        step = (h-y)/(range2-range1)
        #print(range2,price)
        position = (range2-price)*step 
        price_rect = QRectF(x,position-11,w,22)
        self.draw_value(p,price_rect,color,str(price))
                
    def paint(self, p, opt, widget):
        #profiler = debug.Profiler()
        if self.picture is None:
            try:
                picture = QPicture()
                painter = QPainter(picture)
                if self.style["tickFont"]:
                    painter.setFont(self.style["tickFont"])
                specs = self.generateDrawSpecs(painter)
                #profiler('generate specs')
                if specs is not None:
                    self.drawPicture(painter, *specs)
                    #profiler('draw picture')
            finally:
                painter.end()
            self.picture = picture
        p.setRenderHint(p.RenderHint.Antialiasing, True)   ## Sometimes we get a segfault here ???
        p.setRenderHint(p.RenderHint.TextAntialiasing, True)
        self.picture.play(p)
    @Slot()
    def change_view(self):
        
        #profiler = debug.Profiler()
        try:
            picture = QPicture()
            painter = QPainter(picture)
            if self.style["tickFont"]:
                painter.setFont(self.style["tickFont"])
            specs = self.generateDrawSpecs(painter)
            #profiler('generate specs')
            if specs is not None:
                self.drawPicture(painter, *specs) # ,color="#363a45",price=None
                #profiler('draw picture')
        finally:
            painter.setRenderHint(painter.RenderHint.Antialiasing, True)  
            painter.setRenderHint(painter.RenderHint.TextAntialiasing, True)
            self.picture = picture
            self.picture.play(painter)
            painter.end()
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
    
    def change_value(self, args):
        
        if len(args) == 1:
            # if args[0][1] != None:
            self.cross_color,self.cross_price =args[0][0], args[0][1]
        else:
            # if args[1] != None:
            self.cross_color,self.cross_price = args[0], args[1]
        #profiler = debug.Profiler()
        try:
            picture = QPicture()
            painter = QPainter(picture)
            if self.style["tickFont"]:
                painter.setFont(self.style["tickFont"])
            specs = self.generateDrawSpecs(painter)
            #profiler('generate specs')
            if specs is not None:
                self.drawPicture(painter, *specs) # color="#363a45",price=price
                #profiler('draw picture')
        finally:
            painter.setRenderHint(painter.RenderHint.Antialiasing, True)  
            painter.setRenderHint(painter.RenderHint.TextAntialiasing, True)
            self.picture = picture
            self.picture.play(painter)
            painter.end()
        
        self.prepareGeometryChange()
        self.informViewBoundsChanged()

    def wheelEvent(self, event):
        #print("wheelEvent drag la vao day......")
        lv = self.linkedView()
        if lv is None:
            return
        try:
            ev_pos = event.position()
        except:
            ev_pos = event.pos()

        """Check if mouse move on viewbox"""
        if lv.sceneBoundingRect().contains(ev_pos):
            #print("wheelEvent drag la vao day......", ev_pos)
            # event.ignore()
            # return
        # Did the event occur inside the linked ViewBox (and not over the axis iteself)?
        # if lv.sceneBoundingRect().contains(event.scenePos()):
        #     event.ignore()
        #     return
            # pass event to linked viewbox with appropriate single axis zoom parameter
            #print(self.orientation)
            if self.orientation in ['left', 'right']:
                lv.wheelEvent(event, axis=1)
            else:
                lv.wheelEvent(event, axis=0)
        self.update_basement_feature_signal.emit()
        event.accept()

    def mouseDragEvent(self, event):
        #print("mouseDragEvent drag la vao day......")
        self.update_basement_feature_signal.emit()
        self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        lv = self.linkedView()   # Link den ViewBox
        
        if lv is None:
            return
        # Did the mouse down event occur inside the linked ViewBox (and not the axis)?
        if lv.sceneBoundingRect().contains(event.buttonDownScenePos()):
            event.ignore()
            return
        # otherwise pass event to linked viewbox with appropriate single axis parameter
        if self.orientation in ['left', 'right']:
            return lv.mouseDragEvent(event, axis=1)
        else:
            return lv.mouseDragEvent(event, axis=0)
