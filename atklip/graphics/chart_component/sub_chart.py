import asyncio
from functools import lru_cache
from typing import Union, Optional, Any, List, TYPE_CHECKING
import time
from PySide6 import QtGui
from PySide6.QtCore import Signal,QPointF,Qt,QEvent,QThreadPool,QCoreApplication
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter

import numpy as np
from atklip.app_utils.calculate import convert_precision, round_
from atklip.graphics.pyqtgraph import mkPen, PlotWidget
from atklip.appmanager import FastWorker
from atklip.graphics.chart_component.base_items import CandleStick, PriceLine
from atklip.graphics.chart_component.indicators import *
from .plotitem import ViewPlotItem
from .proxy_signal import Signal_Proxy
from atklip.controls import *

from atklip.graphics.chart_component.indicator_panel import SubIndicatorContainer
from atklip.graphics.chart_component.indicator_panel import IndicatorPanel
from .globarvar import global_signal
from atklip.appmanager import FastStartThread,AppLogger
from atklip.exchanges import CryptoExchange
from ccxt.base.errors import *

if TYPE_CHECKING:
    from .viewchart import Chart
    from .viewbox import PlotViewBox
    from .axisitem import CustomDateAxisItem, CustomPriceAxisItem

class Crosshair:
    """Keyword arguments related to Crosshair used in LivePlotWidget"""

    ENABLED = "Crosshair_Enabled"  # Toggle crosshair: bool
    LINE_PEN = "Crosshair_Line_Pen"  # Pen to draw crosshair: QPen
    TEXT_KWARGS = "Text_Kwargs"  # Kwargs for crosshair markers: dict
    X_AXIS = "Crosshair_x_axis"  # Pick axis [default bottom] format and source for x ticks displayed in crosshair: str
    Y_AXIS = "Crosshair_y_axis"  # Pick axis [default left] format and source for y ticks displayed in crosshair: str


class SubChart(PlotWidget):
    crosshair_y_value_change = Signal(tuple)
    crosshair_x_value_change = Signal(tuple)
    mousepossiton_signal = Signal(tuple)
    sig_add_item = Signal(object)
    sig_remove_item = Signal(object)
    sig_add_indicator_panel = Signal(tuple)
    sig_delete_sub_panel = Signal(object)
    first_run = Signal()
    sig_update_y_axis = Signal()
    sig_show_candle_infor = Signal(list)
    sig_reload_indicator_panel = Signal()
    sig_update_source = Signal(object)
    sig_remove_source = Signal(str)

    def __init__(self,chart, parent:None,indicator_name:None,mainwindow:None,background: str = "#161616",) -> None: #str = "#f0f0f0"
        kwargs = {Crosshair.ENABLED: True,
          Crosshair.LINE_PEN: mkPen(color="#eaeaea", width=0.5,style=Qt.DashLine),
          Crosshair.TEXT_KWARGS: {"color": "#eaeaea"}} 

        self.PlotItem = ViewPlotItem(context=self, type_chart="trading")    
        # self.sigSceneMouseMoved.
        self.manual_range = False
        self.magnet_on = False
        self.mouse_on_vb = False

        super().__init__(parent=parent,background=background, plotItem= self.PlotItem,**kwargs)
        self.crosshair_enabled = kwargs.get(Crosshair.ENABLED, False)
        
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)
        self._parent = parent
        self._parent.destroyed.connect(lambda :asyncio.run(self.close()))
        self.indicator_name,self.mainwindow = indicator_name,mainwindow
        # self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)

        self.list_candle_indicators = []

        self.Chart: Chart = chart
        
        self.exchange_name, self.symbol, self.interval =self.Chart.exchange_name, self.Chart.symbol,self.Chart.interval
        self.apikey,self.secretkey = self.Chart.apikey, self.Chart.secretkey
        
        self._precision = self.Chart.get_precision()
        
        self.jp_candle = JAPAN_CANDLE()
        
        self.container_indicator_wg = SubIndicatorContainer(self)

        #print("self.crosshair_enabled", self.crosshair_enabled)
        self.crosshair_items: List = []

        self.crosshair_x_axis = kwargs.get(Crosshair.X_AXIS, "bottom")
        self.crosshair_y_axis = kwargs.get(Crosshair.Y_AXIS, "left")
        
        self.ev_pos = None
        self.last_color = None
        self.last_close_price = None
        self.nearest_value = None
        
        # self.grid = GridItem(textPen="#1111")
        # self.addItem(self.grid)
        
        if self.crosshair_enabled:
            self._add_crosshair(kwargs.get(Crosshair.LINE_PEN, None),
                                kwargs.get(Crosshair.TEXT_KWARGS, {}))
        self.disableAutoRange()

        """Modified _______________________________________ """

        self.yAxis: CustomPriceAxisItem = self.getAxis('right')
        self.xAxis:CustomDateAxisItem = self.getAxis('bottom')
        self.yAxis.setWidth(60)
        self.xAxis.hide()
        
        self.timedata, self.data = [], []
        self.vb:PlotViewBox = self.getViewBox()

        self.lastMousePositon = None
        #self.ObjectManager = UniqueObjectManager()

        self.indicator = None
        self.is_mouse_click = False
        self.threadpool = QThreadPool(self)
        self.threadpool.setMaxThreadCount(1)
        
        self.sources = {}
        self.exchanges = {}
        self.dockLabel = None
        
        self.indicator_data = ()
        self.panel:IndicatorPanel = None
        
        self.sig_add_item.connect(self.add_item,Qt.ConnectionType.QueuedConnection)
        self.sig_remove_item.connect(self.remove_item,Qt.ConnectionType.QueuedConnection)

        self.sig_add_indicator_panel.connect(self.setup_indicator,Qt.ConnectionType.QueuedConnection)
        
        Signal_Proxy(self.sig_update_y_axis,self.yAxis.change_view)
        Signal_Proxy(self.crosshair_y_value_change,slot=self.yAxis.change_value,connect_type = Qt.ConnectionType.AutoConnection)
        
        self.Chart.crosshair_x_value_change.connect(slot=self.xAxis.change_value,type=Qt.ConnectionType.AutoConnection)

        global_signal.sig_show_hide_cross.connect(self.show_hide_cross,Qt.ConnectionType.AutoConnection)
        
        self.first_run.connect(self.set_data_dataconnect,Qt.ConnectionType.AutoConnection)
        self.fast_reset_worker(apikey=self.apikey,secretkey=self.secretkey,exchange_name=self.exchange_name,symbol=self.symbol,interval=self.interval)
    
    def set_data_dataconnect(self):
        self.setup_indicator((self.indicator_name,self.mainwindow))
        self.jp_candle.sig_add_candle.emit(self.jp_candle.candles[-2:])

    def add_to_exchanges(self,new_echange):
        """new_echange = {"id":"symbol_interval","exchange":Exchange,}"""
        if self.exchanges != {}:
            _list_values = list(self.exchanges.items())
            for key,echange in _list_values:
                if key == new_echange["id"]:
                    self.exchanges[new_echange["id"]] = new_echange["exchange"]
                    return
        self.exchanges[new_echange["id"]] = new_echange["exchange"]
    
    async def remove_from_exchanges(self,_id,exchange):
        print(_id,exchange)
        del self.exchanges[_id]
        if exchange.exchange != None:
            await exchange.exchange.close()
        exchange.deleteLater()
        exchange = None
    
    def get_exchange(self):
        return f"{self.symbol}_{self.interval}",self.exchanges.get(f"{self.symbol}_{self.interval}")
    
    def update_sources(self,source:HEIKINASHI|SMOOTH_CANDLE|JAPAN_CANDLE|N_SMOOTH_CANDLE):
        _list_values = list(self.sources.items())
        for key,value in _list_values:
            if value == source:
                del self.sources[key] 
        self.sources[source.source_name] = source
    
    def remove_source(self,source:HEIKINASHI|SMOOTH_CANDLE|JAPAN_CANDLE|N_SMOOTH_CANDLE):
        if source.source_name in list(self.sources.keys()):
            self.sig_remove_source.emit(source.source_name)
            del self.sources[source.source_name]
            # if not isinstance(source,JAPAN_CANDLE):
            #     source.deleteLater()
    
    def on_reset_exchange(self,args):
        self.sig_reset_exchange = True
        """("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path)"""
        #print("viwchart",args)
        _id,exchange = self.get_exchange()
        if exchange != None:
            print(exchange)
            asyncio.run(self.remove_from_exchanges(_id,exchange)) 
        
        _type, symbol, exchange_name = args[0],args[1],args[2]
        if exchange_name == self.exchange_name:
            print("same exchange")
        self.symbol = symbol
        self.exchange_name = exchange_name
        self.is_reseting =  False
        self.fast_reset_worker(exchange_name=exchange_name,symbol=symbol,interval=self.interval)
    
    def on_change_inteval(self,interval):
        """
        ("change_interval",interval)
        """
        _id,exchange = self.get_exchange()
        if exchange != None:
            # print(exchange)
            asyncio.run(self.remove_from_exchanges(_id,exchange)) 
        
        self.sig_reset_exchange = True
        self.interval = interval
        self.is_reseting =  False
        self.fast_reset_worker(exchange_name=self.exchange_name,symbol=self.symbol,interval=interval)
    
    
    def fast_reset_worker(self,apikey:str="",secretkey:str="",exchange_name:str="binanceusdm",symbol:str="",interval:str=""):
        crypto_ex = CryptoExchange(self)
        new_echange = {"id":f"{symbol}_{interval}","exchange":crypto_ex,}
        self.add_to_exchanges(new_echange)
        if self.worker != None:
            if isinstance(self.worker,FastStartThread):
                self.worker.stop_thread()
        self.worker = None
        self.worker = FastStartThread(crypto_ex,self.reset_exchange, apikey,secretkey,crypto_ex,exchange_name,symbol,interval)
        self.worker.start_thread()
        #self.threadpool.start(worker)
    
    async def reset_exchange(self,apikey:str="",secretkey:str="",crypto_ex: CryptoExchange=None,exchange_name:str="binanceusdm",symbol:str="",interval:str=""):
        if apikey != "":
            self.apikey = apikey
        if secretkey != "":
            self.secretkey = secretkey
        
        exchange = crypto_ex.setupEchange(apikey=self.apikey, secretkey=self.secretkey,exchange_name=exchange_name)
        # exchange.streaming['keepAlive'] = 10000 
        # exchange.streaming['maxPingPongMisses'] = 1
        data = []
        if exchange != None:
            data = await exchange.fetch_ohlcv(symbol,interval,limit=1500) 
        else:
             raise BadSymbol(f"{self.exchange_name} {symbol}/{interval} does not support fetch_ohlcv")
        if len(data) == 0:
            raise BadSymbol(f"{self.exchange_name} data not received")
        self.set_market_by_symbol(exchange)
        self.jp_candle.fisrt_gen_data(data,self._precision)
        self.jp_candle.source_name = f"jp {self.symbol} {self.interval}"
        self.update_sources(self.jp_candle)
        await self.loop_watch_ohlcv(crypto_ex,exchange,symbol,interval)
    
    def set_precision(self,precision):
        self._precision = precision
    
    def get_precision(self):
        return self._precision
    
    def set_market_by_symbol(self,exchange):
        market = exchange.market(self.symbol)
        #print(market)
        _precision = convert_precision(market['precision']['price'])
        self.set_precision(_precision)
        #print("self._precision", self._precision)
    
    async def loop_watch_ohlcv(self,crypto_ex,exchange,symbol,interval):
        firt_run = False
        _ohlcv = []
        while crypto_ex in list(self.exchanges.values()):
            if not (self.symbol == symbol and self.interval == interval and exchange.id == self.exchange_name):
                AppLogger.writer("INFO",f"{__name__} - {exchange.id}-{symbol}-{interval} have changed to {self.exchange_name}-{self.symbol}-{self.interval}")
                break
            if exchange != None:
                if (self.symbol == symbol and self.interval == interval and exchange.id == self.exchange_name):
                    try:
                        if "watchOHLCV" in list(exchange.has.keys()):
                            if _ohlcv == []:
                                _ohlcv = await exchange.fetch_ohlcv(symbol,interval,limit=2)
                                # _ohlcv[-1] = ohlcv[-1]
                            else:
                                ohlcv = await exchange.watch_ohlcv(symbol,interval,limit=2)
                                if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                                    _ohlcv[-1] = ohlcv[-1]
                                else:
                                    _ohlcv.append(ohlcv[-1])
                                    _ohlcv = _ohlcv[-2:]
                                    #_ohlcv = await exchange.fetch_ohlcv(symbol,interval,limit=2)    
                        elif "fetchOHLCV" in list(exchange.has.keys()):
                            _ohlcv = await exchange.fetch_ohlcv(symbol,interval,limit=2)
                        else:
                            time.sleep(1)
                            continue
                    except Exception as ex:
                        time.sleep(1)
                        continue
                    if len(_ohlcv) >= 2 and (self.symbol == symbol and self.interval == interval and exchange.id == self.exchange_name):
                        pre_ohlcv = OHLCV(_ohlcv[-2][1],_ohlcv[-2][2],_ohlcv[-2][3],_ohlcv[-2][4], round((_ohlcv[-2][2]+_ohlcv[-2][3])/2,self._precision) , round((_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/3,self._precision), round((_ohlcv[-2][1]+_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/4,self._precision),_ohlcv[-2][5],_ohlcv[-2][0]/1000,0)
                        last_ohlcv = OHLCV(_ohlcv[-1][1],_ohlcv[-1][2],_ohlcv[-1][3],_ohlcv[-1][4], round((_ohlcv[-1][2]+_ohlcv[-1][3])/2,self._precision) , round((_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/3,self._precision), round((_ohlcv[-1][1]+_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/4,self._precision),_ohlcv[-1][5],_ohlcv[-1][0]/1000,0)
                        new_update = self.jp_candle.update([pre_ohlcv,last_ohlcv])
                        if firt_run == False:
                            self.first_run.emit()
                            #QCoreApplication.processEvents()
                            firt_run = True
                else:
                    if exchange != None:
                        AppLogger.writer("warning",f"{__name__} - {exchange.id}-{symbol}-{interval} have changed to {self.exchange_name}-{self.symbol}-{self.interval}")
                    break
            else:
                break
        if exchange != None:
            AppLogger.writer("INFO",f"{__name__}-{symbol}-{interval} have closed")
        try:
            await exchange.close()
        except Exception as e:
            pass
    async def close(self):
        if self.worker != None:
            if isinstance(self.worker,FastStartThread):
                self.worker.stop_thread()
        while list(self.exchanges.keys()) != []:
            for key,value in list(self.exchanges.items()):
                print(key,value)
                del self.exchanges[key]
                if value.exchange != None:
                    await value.exchange.close()
                value.exchange = None
                value.deleteLater()
    def setup_indicator(self,indicator_data):
        self.indicator_data = indicator_data
        _group_indicator = indicator_data[0][0]
        mainwindow = indicator_data[1]
        self.indicator_type =_indicator_type = indicator_data[0][1]
        self._precision = self.Chart.get_precision()
        "add price line"
        if _indicator_type == IndicatorType.SUB_CHART:
            if not isinstance(self.indicator,CandleStick):
                self.indicator = CandleStick(self,IndicatorType.SUB_CHART)
                self.indicator.has["inputs"]["interval"] = self.Chart.interval
                self.panel = IndicatorPanel(mainwindow,self, self.indicator)
                if not self.dockLabel:
                    self.panel.btn_more.clicked.connect(self.dockLabel.floatDock)
                self.container_indicator_wg.add_indicator_panel(self.panel)
                self.add_item(self.indicator)
                self.indicator.first_setup_market()
            else:
                self.indicator.change_interval()
        self.auto_xrange()
        
    def setdockLabel(self,docklabel):
        "để float kết nối more btn với float dock"
        self.dockLabel = docklabel
        if self.panel != None:
            self.panel.btn_more.clicked.connect(docklabel.floatDock)
        
    async def reset_panel(self):
        while True:
            if len(self.jp_candle.candles) > 0:
                break
            #await asyncio.sleep(0.1)
    def add_item(self,args):
        if isinstance(args,tuple):
            item = args[0]
        else:
            item = args
        self.list_candle_indicators.append(item)
        self.addItem(item) 
        self.yAxis.dict_objects.update({item:item.has["y_axis_show"]})

    def remove_item(self,args):
        if isinstance(args,tuple):
            item = args[0]
        else:
            item = args
        self.list_candle_indicators.remove(item)
        del self.yAxis.dict_objects[item]
        self.removeItem(item) 
        item.deleteLater()
        self.sig_delete_sub_panel.emit(self)
        #self.deleteLater()
        
    def slot_proxy_sigMouseMoved(self, pos):
        "de xem sau can lam gi khong"
        pass

    def get_last_pos_of_indicator(self,setdata):
        if self.indicator != None:
            if self.indicator.has["inputs"]["indicator_type"] != IndicatorType.VOLUME:
                if self.indicator._INDICATOR != None:
                    if len(self.indicator._INDICATOR.output_values) > 0:
                        _min, _max = self.indicator.get_min_max()
                        if _min != None:
                            setdata.emit((_min, _max))
                            return 
                    else:
                        time.sleep(0.5)
                        self.get_last_pos_of_indicator(setdata)
            else:
                _min, _max = self.indicator.get_min_max()
                if _min != None:
                    setdata.emit((_min, _max))
                    return
            time.sleep(0.5)
            self.get_last_pos_of_indicator(setdata)
    def auto_xrange(self):
        _min,_max =  self.Chart.yAxis.range[0], self.Chart.yAxis.range[1]   # lastpoint[0], lastpoint[1]
        x_min,x_max =  self.Chart.xAxis.range[0], self.Chart.xAxis.range[1] 
        # x_left,x_right = self.Chart.xAxis.range[0],self.Chart.xAxis.range[1]
        self.setXRange(x_min,x_max)
        self.setYRange(_max,_min)
        #self.setYRange(_max + (_max-_min)*0.1, _min - (_max-_min)*0.1, padding=0.05)

    def show_hide_cross(self, value):
        _isshow, self.nearest_value = value[0],value[1]
        if _isshow:
            if self.nearest_value != None:
                if not self.vLine.isVisible():
                    self.vLine.show() 
                self.vLine.setPos(self.nearest_value)     
        else:
            self.hLine.hide()
            self.vLine.hide()
            self.crosshair_x_value_change.emit(("#363a45",None))
            self.crosshair_y_value_change.emit(("#363a45",None))
        # self.vb.viewTransformChanged()
        # self.vb.informViewBoundsChanged()
    # Override addItem method
    def addItem(self, *args: Any, **kwargs: Any) -> None:
        if hasattr(args[0], "_vl_kwargs") and args[0]._vl_kwargs is not None:
            self.plotItem.addItem(args[0]._vl_kwargs["line"], ignoreBounds=True)
            self.plotItem.addItem(args[0]._vl_kwargs["text"], ignoreBounds=True)
        if hasattr(args[0], "_hl_kwargs") and args[0]._hl_kwargs is not None:
            self.plotItem.addItem(args[0]._hl_kwargs["line"], ignoreBounds=True)
            self.plotItem.addItem(args[0]._hl_kwargs["text"], ignoreBounds=True)
        if hasattr(args[0], "update_leading_line"):
            setattr(args[0], "x_format", self.x_format)
            setattr(args[0], "y_format", self.y_format)
        self.plotItem.addItem(*args)
        args[0].plot_widget = self
    
    def removeItem(self, *args):
        return self.plotItem.removeItem(*args)

    def _update_crosshair_position(self, pos) -> None:
        """Update position of crosshair based on mouse position"""
        self._precision = self.Chart.get_precision()
        nearest_value_yaxis = pos.y()
        h_value = round(nearest_value_yaxis,self._precision)
        if self.mouse_on_vb:
            if not self.hLine.isVisible():
                self.hLine.show()
            self.hLine.setPos(h_value)
            self.crosshair_y_value_change.emit(("#363a45",h_value))
        else:
            self.vLine.hide()
            self.hLine.hide()
        
    def _add_crosshair(self, crosshair_pen: QtGui.QPen, crosshair_text_kwargs: dict) -> None:
        self._precision = self.Chart.get_precision()
        """Add crosshair into plot"""
        self.vLine = PriceLine(angle=90, movable=False,precision=self._precision,dash=[5, 5])
        self.hLine = PriceLine(angle=0, movable=False,precision=self._precision,dash=[5, 5])
        self.crosshair_items = [self.hLine, self.vLine]
        for item in self.crosshair_items:
            item.setZValue(999)
            self.addItem(item)
        self.hide_crosshair()
    def x_format(self, value: Union[int, float]) -> str:
        """X tick format"""
        try:
            # Get crosshair X str format from bottom tick axis format
            return self.getPlotItem().axes[self.crosshair_x_axis]["item"].tickStrings((value,), 0, 1)[0]
        except Exception:
            return str(round(value, 4))
    def y_format(self, value: Union[int, float]) -> str:
        """Y tick format"""
        try:
            # Get crosshair Y str format from left tick axis format
            return self.getPlotItem().axes[self.crosshair_y_axis]["item"].tickStrings((value,), 0, 1)[0]
        except Exception:
            return str(round(value, 4))

    def leaveEvent(self, ev: QEvent) -> None:
        """Mouse left PlotWidget"""
        global_signal.sig_show_hide_cross.emit((False,self.nearest_value))
        self.crosshair_x_value_change.emit(("#363a45",None))
        self.crosshair_y_value_change.emit(("#363a45",None))

        if self.crosshair_enabled:
            self.hide_crosshair()
        super().leaveEvent(ev)

    def enterEvent(self, ev: QEvent) -> None:
        """Mouse enter PlotWidget"""
        self._parent.sig_show_hide_cross.emit((True,self.nearest_value))
        if self.crosshair_enabled:
            self.show_crosshair()
        super().enterEvent(ev)
    # @lru_cache()
    def find_nearest_value(self,closest_index):
        # closest_index = round_(x)
        # last_index = self.jp_candle.last_data().index
        # if last_index < closest_index:
        #     closest_index = last_index
        sub_ohlcv = self.jp_candle.dict_index_ohlcv.get(closest_index)
        _time = sub_ohlcv.time
        main_ohlcv = self.Chart.jp_candle.dict_time_ohlcv.get(_time)

        return sub_ohlcv, main_ohlcv 
    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        self.is_mouse_click =  True

    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        self.is_mouse_click = False
    def mouseMoveEvent(self, ev: QEvent) -> None:
        if not self.is_mouse_click:
            self._precision = self.get_precision()
            """Mouse moved in PlotWidget"""
            try:
                self.ev_pos = ev.position()
            except:
                self.ev_pos = ev.pos()
            self.lastMousePositon = self.plotItem.vb.mapSceneToView(self.ev_pos)
            if self.crosshair_enabled and self.sceneBoundingRect().contains(self.ev_pos):
                self.mouse_on_vb = True
                try:
                    closest_index = round_(self.lastMousePositon.x())
                    last_index = self.jp_candle.last_data().index
                    if last_index < closest_index:
                        closest_index = last_index
                    sub_ohlcv, main_ohlcv = self.find_nearest_value(closest_index)
                    
                    self._update_crosshair_position(self.lastMousePositon)
                    if main_ohlcv is not None:
                        self._parent.sig_show_hide_cross.emit((True,main_ohlcv.index))
                        ##QCoreApplication.processEvents()
                    data = [sub_ohlcv.open,sub_ohlcv.high,sub_ohlcv.low,sub_ohlcv.close]
                    self.Chart.sig_show_candle_infor.emit(data)
                    self.show_hide_cross((True,sub_ohlcv.index))

                except:
                    pass
            elif not self.sceneBoundingRect().contains(self.ev_pos):
                self.mouse_on_vb = False
            
        super().mouseMoveEvent(ev)

    def emit_mouse_position(self, lastpos):
        pass

    def hide_crosshair(self) -> None:
        """Hide crosshair items"""
        self.hLine.setVisible(False)
        
    def show_crosshair(self) -> None:
        """Show crosshair items"""
        for item in self.crosshair_items:
            #if item.isVisible() is False:
            item.setVisible(True)