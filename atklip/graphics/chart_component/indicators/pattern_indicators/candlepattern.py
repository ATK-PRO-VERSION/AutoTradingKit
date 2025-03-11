import time
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal, Qt,QRectF
from PySide6.QtGui import QPainter,QPicture
import pandas as pd

from atklip.graphics.pyqtgraph.Point import Point
from atklip.graphics.pyqtgraph.graphicsItems.TextItem import TextItem
# from atklip.graphics.chart_component.graph_items.CustomTextItem import TextItem

from atklip.graphics.pyqtgraph import GraphicsObject


from atklip.controls import IndicatorType,AllCandlePattern

from atklip.appmanager import FastWorker
from atklip.app_utils import *

if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart


class CandlePattern(GraphicsObject):
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart) -> None:
        GraphicsObject.__init__(self)
        # super().__init__()
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsToShape, True)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        
        self.chart:Chart = chart
        self.has = {
            "name": f"BB 20 2",
            "y_axis_show":False,
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "indicator_type":IndicatorType.CANDLE_PATTERN,
                    "show":False},

            "styles":{
                    }
                    }
        self.id = self.chart.objmanager.add(self)
       
        self.list_patterns:dict = {}
     
        self.picture: QPicture = QPicture()
                
        self.INDICATOR  = AllCandlePattern(self.has["inputs"]["source"])
        
        self.chart.sig_update_source.connect(self.change_source,Qt.ConnectionType.AutoConnection)   
        self.signal_delete.connect(self.delete)
    
    @property
    def is_all_updated(self):
        is_updated = self.INDICATOR.is_current_update 
        return is_updated
    @property
    def id(self):
        return self.chart_id
    
    @id.setter
    def id(self,_chart_id):
        self.chart_id = _chart_id
        
    def disconnect_signals(self):
        try:
            self.INDICATOR.sig_reset_all.disconnect(self.reset_threadpool_asyncworker)
            self.INDICATOR.sig_update_candle.disconnect(self.setdata_worker)
            self.INDICATOR.sig_add_candle.disconnect(self.add_worker)
            self.INDICATOR.signal_delete.disconnect(self.replace_source)
            self.INDICATOR.sig_add_historic.disconnect(self.add_historic_worker)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self.INDICATOR.sig_reset_all.connect(self.reset_threadpool_asyncworker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_update_candle.connect(self.setdata_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_candle.connect(self.add_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.sig_add_historic.connect(self.add_historic_worker,Qt.ConnectionType.AutoConnection)
        self.INDICATOR.signal_delete.connect(self.replace_source,Qt.ConnectionType.AutoConnection)
    
    def fisrt_gen_data(self):
        self.connect_signals()
        self.INDICATOR.started_worker()
       
    def delete(self):
        self.INDICATOR.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        df= self.INDICATOR.get_data()
        setdata.emit(df)
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"ALL CDL PATTERNS"
        self.sig_change_indicator_name.emit(self.has["name"])
    
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
    def reset_threadpool_asyncworker(self):
        self.reset_indicator()
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
      
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"]}
        return inputs
    
    def get_styles(self):
        styles =  {
                    }
        return styles
    
    def update_inputs(self,_input,_source):
        is_update = False
        if _input == "source":
            if self.chart.sources[_source] != self.has["inputs"][_input]:
                self.has["inputs"]["source"] = self.chart.sources[_source]
                self.has["inputs"]["source_name"] = self.chart.sources[_source].source_name
                self.INDICATOR.change_input(self.has["inputs"]["source"])

    def update_styles(self, _input):
        _style = self.has["styles"][_input]

    
    def get_xaxis_param(self):
        return None,"#363a45"


    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    
    def set_Data(self,df:pd.DataFrame):
        if self.list_patterns:
            for obj in self.list_patterns.values():
                if self.scene() is not None:
                    self.scene().removeItem(obj["cdl_pattern"])
                    # self.scene().removeItem(obj["entry"])
                    if hasattr(obj["cdl_pattern"], "deleteLater"):
                        obj["cdl_pattern"].deleteLater()
                    # if hasattr(obj["entry"], "deleteLater"):
                    #     obj["entry"].deleteLater()
                    # 
        self.list_patterns.clear()   
        "CDL_DOJISTAR  CDL_EVENINGDOJISTAR  CDL_ENGULFING  CDL_EVENINGSTAR  CDL_MORNINGDOJISTAR  CDL_MORNINGSTAR  CDL_SHOOTINGSTAR  CDL_HARAMI  CDL_HARAMICROSS  CDL_KICKING  CDL_KICKINGBYLENGTH"
        # print(df)

        for i in range(len(df)):
            index, text = None,None
            row = df.iloc[i]

            if row['bearish_engulfing'] == True:
                index = row['index']
                text = 'bearish_engulfing'
            elif row['three_outside_down'] == True:
                index = row['index']
                text = 'three_outsidedown'
            elif row['evening_doji_star'] == True:
                index = row['index']
                text = 'evening_dojistar'
            elif row['bearish_harami'] == True:
                index = row['index']
                text = 'bearish_harami'
            elif row['three_inside_down'] == True:
                index = row['index']
                text = 'three_insidedown'
            elif row['three_black_crows'] == True:
                index = row['index']
                text = 'three_blackcrows'
            elif row['evenning_star'] == True:
                index = row['index']
                text = 'evenning_star'

            
  
            if index and text:
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                    obj = TextItem("",color="green")
                    obj.setParentItem(self)
                    obj.setAnchor((0.5,1))
                    txt = text.split("_")
                    txt1,txt2 = txt[0],txt[1]
                    html = f"""<div style="text-align: center">
                <span style="color: red; font-size: {10}pt;">{txt1}</span><br><span style="color: red; font-size: {10}pt;">{txt2}</span>"""
                    obj.setHtml(html)
                    obj.setPos(Point(index, ohlc.high))
                    obj.hide()
                    self.list_patterns[index] = {"cdl_pattern":obj}

            index, text = None,None
           
            if row['bullish_engulfing'] == True:
                index = row['index']
                text = 'bullish_engulfing'
            elif row['three_outside_up'] == True:
                index = row['index']
                text = 'three_outsideup'
            elif row['bullish_harami'] == True:
                index = row['index']
                text = 'bullish_harami'
            elif row['three_inside_up'] == True:
                index = row['index']
                text = 'three_insideup'
            elif row['piercing_line'] == True:
                index = row['index']
                text = 'piercing_line'
            elif row['three_white_soldiers'] == True:
                index = row['index']
                text = 'three_whitesoldiers'
            elif row['morning_doji_star'] == True:
                index = row['index']
                text = 'morning_dojistar'

                
            if index and text:
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                    # obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self.chart.drawtool)
                    obj = TextItem("",color="green")
                    obj.setParentItem(self)

                    txt = text.split("_")
                    txt1,txt2 = txt[0],txt[1]
                    html = f"""<div style="text-align: center">
                <span style="color: green; font-size: {10}pt;">{txt1}</span><br><span style="color: green; font-size: {10}pt;">{txt2}</span>"""
                    obj.setHtml(html)
                    
                    obj.setAnchor((0.5,0))
                    
                    r = obj.textItem.boundingRect()
                    tl = obj.textItem.mapToParent(r.topLeft())
                    br = obj.textItem.mapToParent(r.bottomRight())
                    offset = (br - tl) * obj.anchor

                    _y = ohlc.low-offset.y()/2

                    obj.setPos(Point(index,_y))
                    self.list_patterns[index] = {"cdl_pattern":obj}
                    
                    obj.hide()
                    

    def add_historic_Data(self,df):
        for i in range(len(df)):
            index, text = None,None
            row = df.iloc[i]
           
            if row['bearish_engulfing'] == True:
                index = row['index']
                text = 'bearish_engulfing'
            elif row['three_outside_down'] == True:
                index = row['index']
                text = 'three_outsidedown'
            elif row['evening_doji_star'] == True:
                index = row['index']
                text = 'evening_dojistar'
            elif row['bearish_harami'] == True:
                index = row['index']
                text = 'bearish_harami'
            elif row['three_inside_down'] == True:
                index = row['index']
                text = 'three_insidedown'
            elif row['three_black_crows'] == True:
                index = row['index']
                text = 'three_blackcrows'
            elif row['evenning_star'] == True:
                index = row['index']
                text = 'evenning_star'

            
            if index and text:
                if self.list_patterns.get(index):
                    continue
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                    obj = TextItem("",color="green")
                    obj.setParentItem(self)
                    obj.setAnchor((0.5,1))
                    txt = text.split("_")
                    txt1,txt2 = txt[0],txt[1]
                    html = f"""<div style="text-align: center">
                <span style="color: red; font-size: {10}pt;">{txt1}</span><br><span style="color: red; font-size: {10}pt;">{txt2}</span>"""
                    obj.setHtml(html)
                    obj.setPos(Point(index, ohlc.high))
                    obj.hide()
                    self.list_patterns[index] = {"cdl_pattern":obj}

            index, text = None,None

            if row['bullish_engulfing'] == True:
                index = row['index']
                text = 'bullish_engulfing'
            elif row['three_outside_up'] == True:
                index = row['index']
                text = 'three_outsideup'
            elif row['bullish_harami'] == True:
                index = row['index']
                text = 'bullish_harami'
            elif row['three_inside_up'] == True:
                index = row['index']
                text = 'three_insideup'
            elif row['piercing_line'] == True:
                index = row['index']
                text = 'piercing_line'
            elif row['three_white_soldiers'] == True:
                index = row['index']
                text = 'three_whitesoldiers'
            elif row['morning_doji_star'] == True:
                index = row['index']
                text = 'morning_dojistar'

                
            if index and text:
                if self.list_patterns.get(index):
                    continue
                ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
                if ohlc:
                    # obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self.chart.drawtool)
                    obj = TextItem("",color="green")
                    obj.setParentItem(self)

                    txt = text.split("_")
                    txt1,txt2 = txt[0],txt[1]
                    html = f"""<div style="text-align: center">
                <span style="color: green; font-size: {10}pt;">{txt1}</span><br><span style="color: green; font-size: {10}pt;">{txt2}</span>"""
                    obj.setHtml(html)
                    
                    obj.setAnchor((0.5,0))
                    
                    r = obj.textItem.boundingRect()
                    tl = obj.textItem.mapToParent(r.topLeft())
                    br = obj.textItem.mapToParent(r.bottomRight())
                    offset = (br - tl) * obj.anchor

                    _y = ohlc.low-offset.y()/2

                    obj.setPos(Point(index,_y))
                    self.list_patterns[index] = {"cdl_pattern":obj}
                    
                    obj.hide()

        
    def update_Data(self,df):
        index, text = None,None
        row = df.iloc[0]
        index = row['index']
        if self.list_patterns.get(index):
            return

        if row['bearish_engulfing'] == True:
            index = row['index']
            text = 'bearish_engulfing'
        elif row['three_outside_down'] == True:
            index = row['index']
            text = 'three_outsidedown'
        elif row['evening_doji_star'] == True:
            index = row['index']
            text = 'evening_dojistar'
        elif row['bearish_harami'] == True:
            index = row['index']
            text = 'bearish_harami'
        elif row['three_inside_down'] == True:
            index = row['index']
            text = 'three_insidedown'
        elif row['three_black_crows'] == True:
            index = row['index']
            text = 'three_blackcrows'
        elif row['evenning_star'] == True:
            index = row['index']
            text = 'evenning_star'

        
        if index and text:
            if self.list_patterns.get(index):
                return
            ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
            if ohlc:
                obj = TextItem("",color="green")
                obj.setParentItem(self)
                obj.setAnchor((0.5,1))
                txt = text.split("_")
                txt1,txt2 = txt[0],txt[1]
                html = f"""<div style="text-align: center">
            <span style="color: red; font-size: {10}pt;">{txt1}</span><br><span style="color: red; font-size: {10}pt;">{txt2}</span>"""
                obj.setHtml(html)
                obj.setPos(Point(index, ohlc.high))
                self.list_patterns[index] = {"cdl_pattern":obj}

        index, text = None,None

        if row['bullish_engulfing'] == True:
            index = row['index']
            text = 'bullish_engulfing'
        elif row['three_outside_up'] == True:
            index = row['index']
            text = 'three_outsideup'
        elif row['bullish_harami'] == True:
            index = row['index']
            text = 'bullish_harami'
        elif row['three_inside_up'] == True:
            index = row['index']
            text = 'three_insideup'
        elif row['piercing_line'] == True:
            index = row['index']
            text = 'piercing_line'
        elif row['three_white_soldiers'] == True:
            index = row['index']
            text = 'three_whitesoldiers'
        elif row['morning_doji_star'] == True:
            index = row['index']
            text = 'morning_dojistar'

            
        if index and text:
            if self.list_patterns.get(index):
                return
            ohlc =  self.chart.jp_candle.map_index_ohlcv.get(index)
            if ohlc:
                # obj = TextBoxROI(size=5,symbol="o",pen="green",brush = "green", drawtool=self.chart.drawtool)
                obj = TextItem("",color="green")
                obj.setParentItem(self)

                txt = text.split("_")
                txt1,txt2 = txt[0],txt[1]
                html = f"""<div style="text-align: center">
            <span style="color: green; font-size: {10}pt;">{txt1}</span><br><span style="color: green; font-size: {10}pt;">{txt2}</span>"""
                obj.setHtml(html)
                
                obj.setAnchor((0.5,0))
                
                r = obj.textItem.boundingRect()
                tl = obj.textItem.mapToParent(r.topLeft())
                br = obj.textItem.mapToParent(r.bottomRight())
                offset = (br - tl) * obj.anchor

                _y = ohlc.low-offset.y()/2

                obj.setPos(Point(index,_y))
                self.list_patterns[index] = {"cdl_pattern":obj}
                
    
    def setdata_worker(self):
        self.worker = None
        self.worker = FastWorker(self.update_data)
        self.worker.signals.setdata.connect(self.update_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()    
        
    def add_historic_worker(self,_len):
        self.worker = None
        self.worker = FastWorker(self.load_historic_data,_len)
        self.worker.signals.setdata.connect(self.add_historic_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start() 
    def add_worker(self):
        self.worker = None
        self.worker = FastWorker(self.add_data)
        self.worker.signals.setdata.connect(self.update_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()
    
    def load_historic_data(self,_len,setdata):
        data = self.INDICATOR.get_data(stop=_len)
        setdata.emit(data)  
    def add_data(self,setdata):
        data = self.INDICATOR.get_data(start=-2)
        setdata.emit(data)   
    
    def update_data(self,setdata):
        data = self.INDICATOR.get_data(start=-2)
        setdata.emit(data)

       
    def boundingRect(self) -> QRectF:
        if self.list_patterns:
            x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
            for _x in list(self.list_patterns.keys()):
                obj = self.list_patterns.get(_x)
                if obj:
                    if x_left < _x < x_right:
                        obj["cdl_pattern"].show()
                    else:
                        obj["cdl_pattern"].hide()

        return self.picture.boundingRect()
    
    def paint(self, p:QPainter, *args):
        self.picture.play(p)
    
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return _value,"#363a45"
    
    
    def get_last_point(self):
        return None,None
    
    def get_min_max(self):
        try:
            return None,None
        except Exception as e:
            pass
        time.sleep(0.1)
        return None,None

    def on_click_event(self):
        #print("zooo day__________________")
        pass

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.on_click.emit(self)
        super().mousePressEvent(ev)

    def setObjectName(self, name):
        self.name = name

    def objectName(self):
        return self.name
    
