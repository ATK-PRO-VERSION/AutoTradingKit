

import time
from typing import List,TYPE_CHECKING

from PySide6.QtCore import Signal, QObject,Qt,QRectF,QPointF,QLineF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPicture,QTextItem,QFont
import pandas as pd

from atklip.graphics.chart_component.base_items.plotdataitem import PlotDataItem

from atklip.controls import PD_MAType,IndicatorType
from atklip.controls.models import SMCModel
from atklip.graphics.chart_component.draw_tools.base_arrow import BaseArrowItem
from atklip.graphics.chart_component.draw_tools.entry import Entry

from atklip.appmanager import FastWorker
from atklip.app_utils import *
from atklip.controls.candle.n_time_smooth_candle import N_SMOOTH_CANDLE
from atklip.controls.smc.smc import SMC as S_M_C

from atklip.graphics.pyqtgraph import GraphicsObject, TextItem
if TYPE_CHECKING:
    from atklip.graphics.chart_component.viewchart import Chart

class SMC(GraphicsObject):
    on_click = Signal(object)
    signal_visible = Signal(bool)
    signal_delete = Signal()
    sig_change_yaxis_range = Signal()
    signal_change_color = Signal(str)
    signal_change_width = Signal(int)
    signal_change_type = Signal(str)
    sig_change_indicator_name = Signal(str)
    def __init__(self,chart) -> None:
        # super().__init__()
        GraphicsObject.__init__(self)
        # self.setFlag(self.GraphicsItemFlag.ItemHasNoContents)
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption,True)
        
        self.chart:Chart = chart
        self.has: dict = {
            "name": "SMC Ver_1.0",
            "y_axis_show":False,
            
            "inputs":{
                    "source":self.chart.jp_candle,
                    "source_name": self.chart.jp_candle.source_name,
                    "window":500,
                    "time_frame":"4h",
                    "swing_length":5,
                    "session":"London",
                    "indicator_type":IndicatorType.SMC,
                    "show":False},

            "styles":{
                    }
                    }
        
        self.id = self.chart.objmanager.add(self)

        self.data:dict = {}

        self.list_text:dict = {
            "fvgs":{},
            "bos":{},
            "choch":{},
            "ob":{},
            "liquidity":{}
        }
        self.is_add = False
        self.list_pos:dict = {}
        self.picture: QPicture = QPicture()

        self.INDICATOR  = S_M_C(self.has["inputs"]["source"], self.model.__dict__)
                
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

    @property
    def model(self):
        return SMCModel(self.id,"SMC",self.has["inputs"]["source"].source_name,
                        self.has["inputs"]["window"],
                        self.has["inputs"]["swing_length"],
                        self.has["inputs"]["time_frame"],
                        self.has["inputs"]["session"]
                        )
    
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
        print("deleted--------------------------")
        self.disconnect_signals()
        self.INDICATOR.disconnect()
        self.INDICATOR.deleteLater()
        self.chart.sig_remove_item.emit(self)
    
    def reset_indicator(self):
        self.worker = None
        self.worker = FastWorker(self.regen_indicator)
        self.worker.signals.setdata.connect(self.set_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()

    def regen_indicator(self,setdata):
        
        data:dict= self.INDICATOR.get_data()
        setdata.emit(data)
        self.sig_change_yaxis_range.emit()
        self.has["name"] = f"""SMC {self.has['inputs']['window']}"""
        self.sig_change_indicator_name.emit(self.has["name"])
        
    def replace_source(self):
        self.update_inputs( "source",self.chart.jp_candle.source_name)
        
    def reset_threadpool_asyncworker(self):
        self.reset_indicator()
        
    def change_source(self,source):   
        if self.has["inputs"]["source_name"] == source.source_name:
            self.update_inputs("source",source.source_name)
      
    def get_inputs(self):
        inputs =  {"source":self.has["inputs"]["source"],
                    "window":self.has["inputs"]["window"],
                    "time_frame":self.has["inputs"]["time_frame"],
                    "swing_length":self.has["inputs"]["swing_length"],
                    "session":self.has["inputs"]["session"]
                    }
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
        elif _source != self.has["inputs"][_input]:
                self.has["inputs"][_input] = _source
                is_update = True
        
        if is_update:
            self.has["name"] = "SMC"
            self.sig_change_indicator_name.emit(self.has["name"])
            self.INDICATOR.change_input(dict_ta_params=self.model.__dict__)
    
    def update_styles(self, _input):
        _style = self.has["styles"][_input]
    
    def get_xaxis_param(self):
        return None,"#363a45"

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
     
    def set_Data(self,data):
        all_text = self.list_text.copy()
        for _key,list_texts in all_text.items():
            # print(_key,list_texts)
            list_text = list_texts.copy()
            for key,ti in list_text.items():
                ti.setParentItem(None)
                del self.list_text[_key][key]
                if self.scene() is not None:
                    self.scene().removeItem(ti)
                    if hasattr(ti, "deleteLater"):
                        ti.deleteLater()


        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        # p.setPen(self.outline_pen)
        if data:
            fvgs:dict = data.get("FVG")
            if fvgs:
                for key,fvg in fvgs.items():
                    self.draw_fvg(p,fvg)
                list_text = self.list_text["fvgs"].copy()
                for key,ti in list_text.items():
                    if key not in fvgs.keys():
                        ti.setParentItem(None)
                        del self.list_text["fvgs"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()

            bos:dict = data.get("BOS")
            if bos:
                for key,bo in bos.items():
                    self.draw_bos(p,bo)
                
                list_text = self.list_text["bos"].copy()
                for key,ti in list_text.items():
                    if key not in bos.keys():
                        ti.setParentItem(None)
                        del self.list_text["bos"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
            choch:dict = data.get("CHOCH")
            if choch:
                for key,cho in choch.items():
                    self.draw_choch(p,cho)
                list_text = self.list_text["choch"].copy()
                for key,ti in list_text.items():
                    if key not in choch.keys():
                        ti.setParentItem(None)
                        del self.list_text["choch"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
            ob:dict = data.get("OB")
            if ob:
                for key,cho in ob.items():
                    self.draw_ob(p,cho)
                list_text = self.list_text["ob"].copy()
                for key,ti in list_text.items():
                    if key not in ob.keys():
                        ti.setParentItem(None)
                        del self.list_text["ob"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
            liquidity:dict = data.get("Liquidity")
            if liquidity:
                for key,cho in liquidity.items():
                    self.draw_liquidity(p,cho)
                list_text = self.list_text["liquidity"].copy()
                for key,ti in list_text.items():
                    if key not in liquidity.keys():
                        ti.setParentItem(None)
                        del self.list_text["liquidity"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
            
        p.end()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.INDICATOR.is_current_update = True

    def add_historic_Data(self,data):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        # p.setPen(self.outline_pen)
        if data:
            fvgs:dict = data.get("FVG")
            if fvgs:
                for key,fvg in fvgs.items():
                    self.draw_fvg(p,fvg)
                list_text = self.list_text["fvgs"].copy()
                for key,ti in list_text.items():
                    if key not in fvgs.keys():
                        ti.setParentItem(None)
                        del self.list_text["fvgs"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
                    
            bos:dict = data.get("BOS")
            if bos:
                for key,bo in bos.items():
                    self.draw_bos(p,bo)
                
                list_text = self.list_text["bos"].copy()
                for key,ti in list_text.items():
                    if key not in bos.keys():
                        ti.setParentItem(None)
                        del self.list_text["bos"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
            choch:dict = data.get("CHOCH")
            if choch:
                for key,cho in choch.items():
                    self.draw_choch(p,cho)
                list_text = self.list_text["choch"].copy()
                for key,ti in list_text.items():
                    if key not in choch.keys():
                        ti.setParentItem(None)
                        del self.list_text["choch"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
            ob:dict = data.get("OB")
            if ob:
                for key,cho in ob.items():
                    self.draw_ob(p,cho)
                list_text = self.list_text["ob"].copy()
                for key,ti in list_text.items():
                    if key not in ob.keys():
                        ti.setParentItem(None)
                        del self.list_text["ob"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
            liquidity:dict = data.get("Liquidity")
            if liquidity:
                for key,cho in liquidity.items():
                    self.draw_liquidity(p,cho)
                list_text = self.list_text["liquidity"].copy()
                for key,ti in list_text.items():
                    if key not in liquidity.keys():
                        ti.setParentItem(None)
                        del self.list_text["liquidity"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
        p.end()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.INDICATOR.is_current_update = True
    
    def update_Data(self,data):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        # p.setPen(self.outline_pen)
        if data:
            fvgs:dict = data.get("FVG")
            if fvgs:
                for key,fvg in fvgs.items():
                    self.draw_fvg(p,fvg)
                list_text = self.list_text["fvgs"].copy()
                for key,ti in list_text.items():
                    if key not in fvgs.keys():
                        ti.setParentItem(None)
                        del self.list_text["fvgs"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
                    
            bos:dict = data.get("BOS")
            if bos:
                list_text = self.list_text["bos"].copy()
                for key,ti in list_text.items():
                    if key not in bos.keys():
                        ti.setParentItem(None)
                        del self.list_text["bos"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
                for key,bo in bos.items():
                    self.draw_bos(p,bo)
                
            choch:dict = data.get("CHOCH")
            if choch:
                list_text = self.list_text["choch"].copy()
                for key,ti in list_text.items():
                    if key not in choch.keys():
                        ti.setParentItem(None)
                        del self.list_text["choch"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
                for key,cho in choch.items():
                    self.draw_choch(p,cho)
            ob:dict = data.get("OB")
            if ob:
                list_text = self.list_text["ob"].copy()
                for key,ti in list_text.items():
                    if key not in ob.keys():
                        ti.setParentItem(None)
                        del self.list_text["ob"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()
                for key,cho in ob.items():
                    self.draw_ob(p,cho)
                self.is_add = False
            liquidity:dict = data.get("Liquidity")
            if liquidity:
                for key,cho in liquidity.items():
                    self.draw_liquidity(p,cho)
                list_text = self.list_text["liquidity"].copy()
                for key,ti in list_text.items():
                    if key not in liquidity.keys():
                        ti.setParentItem(None)
                        del self.list_text["liquidity"][key]
                        if self.scene() is not None:
                            self.scene().removeItem(ti)
                            if hasattr(ti, "deleteLater"):
                                ti.deleteLater()


        p.end()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.INDICATOR.is_current_update = True
        
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
        self.is_add = True
        self.worker = None
        self.worker = FastWorker(self.add_data)
        self.worker.signals.setdata.connect(self.update_Data,Qt.ConnectionType.AutoConnection)
        self.worker.start()    
    
    def load_historic_data(self,_len,setdata):
        data:dict= self.INDICATOR.get_data()
        setdata.emit(data)
        
    def add_data(self,setdata):
        data:dict= self.INDICATOR.get_data()
        setdata.emit(data)
    
    def update_data(self,setdata):
        data:dict= self.INDICATOR.get_data()
        setdata.emit(data)


    def boundingRect(self) -> QRectF:
        x_left,x_right = int(self.chart.xAxis.range[0]),int(self.chart.xAxis.range[1])
        start_index = self.chart.jp_candle.candles[0].index
        stop_index = self.chart.jp_candle.candles[-1].index
        if x_left > start_index:
            self._start = x_left+2
        else:
            self._start = start_index+2
            
        if x_right < stop_index:
            self._stop = x_right
        else:
            self._stop = stop_index
        h_low,h_high = self.chart.yAxis.range[0],self.chart.yAxis.range[1]
        rect = QRectF(self._start,h_low,self._stop-self._start,h_high-h_low)
        return rect#     

    def draw_liquidity(self,p:QPainter,liquidity:dict):
        # {'x': 1514755467, 'x1': np.int64(1514755490), 'liquidity': np.float32(-1.0), 'mid_x': 1514755478, 'mid_y': np.float32(85863.75)}
        # print(liquidity)
        try:
            _x = liquidity["x"]
            _x1 = liquidity["x1"]
            _liquidity = liquidity["liquidity"]
            _mid_x = liquidity["mid_x"]
            _mid_y = liquidity["mid_y"]
            if _liquidity < 0:
                p.setPen(mkPen(color="red",width=2))
                # p.setBrush(mkBrush("red"))
            else:
                p.setPen(mkPen(color="green",width=2))
                # p.setBrush(mkBrush("green"))
            p.setOpacity(0.6)
            line = QLineF(QPointF(_x, _mid_y), QPointF(_x1, _mid_y))
            p.drawLine(line)

            ti = self.list_text["liquidity"].get(_x)
            if not ti:
                html = f"""
                    <div style="text-align: center; border-radius: 5px solid #d1d4dc;">
                        <span style="color: #d1d4dc; font-size: 8pt;">Liquidity</span>
                    </div>
                    """
                text = TextItem("", anchor=(0.5, 0.5))
                text.setHtml(html)
                text.setParentItem(self)
                r = text.boundingRect()
                r = text.boundingRect()
                if _liquidity < 0:
                    text.setPos(_mid_x, _mid_y-r.height()/2)
                else:
                    text.setPos(_mid_x, _mid_y+r.height()/2)
                self.list_text["liquidity"][_x] = text
        except Exception as e:
            print(e)
            print(liquidity)

    def draw_choch(self,p:QPainter,choch:dict):
        # return
        try:
            _x = choch["x"]
            _x1 = choch["x1"]
            _choch = choch["choch"]
            _mid_x = choch["mid_x"]
            _mid_y = choch["mid_y"]
            if _choch > 0:
                p.setPen(mkPen(color="red",width=2))
                # p.setBrush(mkBrush("red"))
            else:
                p.setPen(mkPen(color="green",width=2))
                # p.setBrush(mkBrush("green"))
            p.setOpacity(0.6)
            line = QLineF(QPointF(_x, _mid_y), QPointF(_x1, _mid_y))
            p.drawLine(line)

            ti = self.list_text["choch"].get(_x)
            if not ti:
                html = f"""
                    <div style="text-align: center; border-radius: 5px solid #d1d4dc;">
                        <span style="color: #d1d4dc; font-size: 8pt;">CHOCH</span>
                    </div>
                    """

                text = TextItem("", anchor=(0.5, 0.5))
                text.setHtml(html)
                text.setParentItem(self)
                r = text.boundingRect()
                if _choch < 0:
                    text.setPos(_mid_x, _mid_y-r.height()/2)
                else:
                    text.setPos(_mid_x, _mid_y+r.height()/2)
                self.list_text["choch"][_x] = text

        except Exception as e:
            print(e)
            print(choch)

    def draw_bos(self,p:QPainter,bo:dict):
        # return
        try:
            _x = bo["x"]
            _x1 = bo["x1"]
            _bos = bo["bos"]
            _mid_x = bo["mid_x"]
            _mid_y = bo["mid_y"]
            if _bos > 0:
                p.setPen(mkPen(color="red",width=2))
                # p.setBrush(mkBrush("red"))
            else:
                p.setPen(mkPen(color="green",width=2))
                # p.setBrush(mkBrush("green"))
            p.setOpacity(0.6)
            line = QLineF(QPointF(_x, _mid_y), QPointF(_x1, _mid_y))
            p.drawLine(line)

            ti = self.list_text["bos"].get(_x)
            if not ti:
                html = f"""
                    <div style="text-align: center; border-radius: 5px solid #d1d4dc;">
                        <span style="color: #d1d4dc; font-size: 8pt;">BOS</span>
                    </div>
                    """
                text = TextItem("", anchor=(0.5, 0.5))
                text.setHtml(html)
                text.setParentItem(self)
                text.setPos(_mid_x, _mid_y)
                r = text.boundingRect()
                if _bos < 0:
                    text.setPos(_mid_x, _mid_y-r.height()/2)
                else:
                    text.setPos(_mid_x, _mid_y+r.height()/2)
                self.list_text["bos"][_x] = text

        except Exception as e:
            print(e)
            print(bo)

    def draw_ob(self,p:QPainter,ob:dict):
        # return
        try:
            _x = ob["x"]
            _x1 = ob["x1"]
            _ob = ob["ob"]
            _top = ob["top"]
            _bottom = ob["bottom"]
            _mid_x = ob["mid_x"]
            _mid_y = ob["mid_y"]
            if _ob > 0:
                p.setPen(Qt.NoPen)
                p.setBrush(mkBrush("green"))
            else:
                p.setPen(Qt.NoPen)
                p.setBrush(mkBrush("red"))
            p.setOpacity(0.4)
            if _top > _bottom:
                rect = QRectF(_x, _top, _x1-_x, _bottom-_top) 
            else:
                 rect = QRectF(_x, _top, _x1-_x, _top-_bottom)
            p.drawRect(rect)

            ti = self.list_text["ob"].get(_x)
            if not ti:
                html = f"""
                    <div style="text-align: center; border-radius: 5px solid #d1d4dc;">
                        <span style="color: #d1d4dc; font-size: 8pt;">OB</span>
                    </div>
                    """
                text = TextItem("", anchor=(0.5, 0.5))
                text.setHtml(html)
                text.setParentItem(self)
                # r = text.boundingRect()
                text.setPos(_mid_x, _mid_y-abs(_bottom-_top)/2)
                self.list_text["ob"][_x] = text
            else:
                if self.is_add:
                    ti.setPos(_mid_x, _mid_y-abs(_bottom-_top)/2)

        except Exception as e:
            print(e)
            print(ob)


    def draw_fvg(self,p:QPainter,fvg:dict):
        # return
        # print(fvg)
        try:
            _x = fvg["x"]
            _x1 = fvg["x1"]
            _top = fvg["top"]
            _fvg = fvg["fvg"]
            _bottom = fvg["bottom"]
            _mid_x = fvg["mid_x"]
            _mid_y = fvg["mid_y"]
            if _fvg > 0:
                p.setPen(Qt.NoPen)
                p.setBrush(mkBrush("orange"))
            else:
                p.setPen(Qt.NoPen)
                p.setBrush(mkBrush("orange"))
            p.setOpacity(0.4)
            if _top > _bottom:
                rect = QRectF(_x, _top, _x1-_x, _bottom-_top) 
            else:
                 rect = QRectF(_x, _top, _x1-_x, _top-_bottom)
            p.drawRect(rect)
            ti = self.list_text["fvgs"].get(_x)
            if not ti:
                html = f"""
                    <div style="text-align: center; border-radius: 5px solid #d1d4dc;">
                        <span style="color: #d1d4dc; font-size: 8pt;">FVG</span>
                    </div>
                    """
                text = TextItem("", anchor=(0.5, 0.5))
                text.setHtml(html)
                text.setParentItem(self)
                r = text.boundingRect()
                if _fvg < 0:
                    text.setPos(_mid_x, _mid_y)
                else:
                    text.setPos(_mid_x, _mid_y)
                self.list_text["fvgs"][_x] = text
        except Exception as e:
            print(e)
            print(fvg)


    def paint(self, p: QtGui.QPainter, *args) -> None:
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self) -> QtCore.QRect:
        return QtCore.QRectF(self.picture.boundingRect())
    
    def get_yaxis_param(self):
        _value = None
        try:
            _time,_value = self.get_last_point()
        except:
            pass
        return None,None
    
    def get_last_point(self):
        return None,None
    
    def get_min_max(self):
        return None,None
        try:
            _min, _max = np.nanmin(self.lowline.yData), np.nanmax(self.highline.yData)
            # if y_data.__len__() > 0:
            #     _min = y_data.min()
            #     _max = y_data.max()
            return _min,_max
        except Exception as e:
            pass
        time.sleep(0.1)
        self.get_min_max()
        return _min,_max

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
    