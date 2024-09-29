import traceback,asyncio,time
from typing import Dict
from PySide6 import QtCore
from PySide6.QtCore import Qt, Signal, QCoreApplication, QKeyCombination, QThreadPool,QObject
from PySide6.QtGui import QKeyEvent

from atklip.graphics.chart_component.base_items import CandleStick
from atklip.graphics.chart_component.indicators import BasicMA,BasicBB,BasicDonchianChannels,BasicZIGZAG
from atklip.graphics.chart_component import ViewPlotWidget
from atklip.exchanges import CryptoExchange,CryptoExchange_WS
from ccxt.base.errors import *
# from ccxt.base.errors import BadSymbol
from atklip.controls import IndicatorType,OHLCV
from atklip.controls.candle import HEIKINASHI, SMOOTH_CANDLE,JAPAN_CANDLE, N_SMOOTH_CANDLE

from atklip.graphics.chart_component.draw_tools import *

from .unique_object_id import ObjManager

from atklip.app_utils import *

from atklip.appmanager import FastStartThread,AppLogger,ThreadPoolExecutor_global,SimpleWorker


from atklip.graphics.chart_component.indicator_panel import IndicatorPanel

class Chart(ViewPlotWidget):
    def __init__(self, parent=None,apikey:str="", secretkey:str="",exchange_name:str="binanceusdm",
                 symbol:str="BTCUSDT",interval:str="1m"):
        super(Chart,self).__init__(parent=parent)
        self._parent = parent
        self.sig_reload_indicator_panel.connect(self._parent.reload_pre_indicator,Qt.ConnectionType.AutoConnection)
        self.apikey = apikey
        self.secretkey = secretkey
        
        
        self.exchange_name,self.symbol, self.interval =exchange_name, symbol,interval
        
        self.vb.symbol, self.vb.interval = self.symbol, self.interval
        
        if "binance" in self.exchange_name:
            self.apikey = "zhBF9X2mhD7rY6fpFU243biBtE4ySGpXTBPdYYOExyx27G5CrU6cCEditBhO7ek4"
            self.secretkey = "6rIYDN1xBaxxGyuLslYGMxlHFtjgzhVh6nV4zO8IKaspdF1H3tC5MKXMgxA1rHDA"
        else:
            self.apikey = ""
            self.secretkey = ""
        
        self.sig_reset_exchange = False
        self.is_reseting =  False
        self.worker = None
        self.worker_auto_load_old_data = None
        
        self.vb.load_old_data.connect(self.auto_load_old_data)
        
        self.sources: Dict[str:QObject] = {}
        self.indicators:Dict[str:QObject] = {}
        self.drawtools:Dict[str:QObject] = {}
        self.objmanager:ObjManager = ObjManager()
        self.exchanges = {}
        self.is_load_historic = False
        self.time_delay = 5
                
        self.crypto_ex = CryptoExchange().setupEchange(apikey=self.apikey, secretkey=self.secretkey,exchange_name=self.exchange_name)
        self.crypto_ex_ws = CryptoExchange_WS().setupEchange(apikey=self.apikey, secretkey=self.secretkey,exchange_name=self.exchange_name)
        
        self.sig_add_indicator_panel.connect(self.setup_indicator,Qt.ConnectionType.AutoConnection)

        self.first_run.connect(self.set_data_dataconnect,Qt.ConnectionType.AutoConnection)
        self.fast_reset_worker(apikey=self.apikey,secretkey=self.secretkey,exchange_name=self.exchange_name,symbol=self.symbol,interval=self.interval)
    
    def _init_async_loop(self) -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

    @property
    def time_delay(self):
        return self._time_delay
    @time_delay.setter
    def time_delay(self,value):
        self._time_delay = value
    
    def change_mode(self):
        sender = self.sender()
        print(sender)
        if self.is_living:
            self.is_living = False
            self.time_delay = 5
        else:
            self.is_living = True
            self.time_delay = 0.3
    
    def auto_load_old_data(self):
        "load historic data when wheel or drag viewbox"
        if isinstance(self.worker_auto_load_old_data,SimpleWorker):
            if not self.is_load_historic:
                self.worker_auto_load_old_data = None
        if not self.is_load_historic:
            x_range = self.getAxis('bottom').range
            left_xrange = x_range[0]
            right_xrange = x_range[1]
            first_candlestick_index = self.jp_candle.candles[0].index        
            if left_xrange < first_candlestick_index + 1500:
                self.is_load_historic = True
                self.worker_auto_load_old_data = SimpleWorker(fn=self.check_signal_load_old_data)
                self.worker_auto_load_old_data.start_thread()
        
    def check_signal_load_old_data(self):
        if self.jp_candle.candles != []:
            _cr_time = self.jp_candle.candles[0].time
            data = self.crypto_ex.fetch_ohlcv(self.symbol,self.interval,limit=1500, params={"until":_cr_time*1000})
            self.jp_candle.load_historic_data(data,self._precision)
            self.heikinashi.load_historic_data(len(data))
        self.is_load_historic = False

    def add_to_exchanges(self,new_echange:dict):
        """new_echange = {"id":"symbol_interval","exchange":Exchange,}"""
        if self.exchanges != {}:
            if new_echange["id"] in list(self.exchanges.keys()):
                old_ex =  self.exchanges[new_echange["id"]]
                if new_echange["exchange"] == old_ex:
                    return
                del self.exchanges[new_echange["id"]]
            self.exchanges[new_echange["id"]] = new_echange["exchange"]
            return
        self.exchanges[new_echange["id"]] = new_echange["exchange"]
        
    async def remove_from_exchanges(self,_id):
        if _id in list(self.exchanges.keys()):
                old_ex =  self.exchanges[_id]
                del self.exchanges[_id]
                print("old_Ex", old_ex)
    
    def update_sources(self,source:HEIKINASHI|SMOOTH_CANDLE|JAPAN_CANDLE|N_SMOOTH_CANDLE):
        _key = f"{self.symbol} {self.interval}"
        while True:
            for key,value in list(self.sources.items()):
                if not key.__contains__(_key):
                    del self.sources[key] 
                if value == source:
                    if key in list(self.sources.keys()):
                        del self.sources[key]
            else:
                break
        self.sources[source.source_name] = source
    
    def remove_source(self,source:HEIKINASHI|SMOOTH_CANDLE|JAPAN_CANDLE|N_SMOOTH_CANDLE):
        if source.source_name in list(self.sources.keys()):
            # self.sig_remove_source.emit(source.source_name)
            del self.sources[source.source_name]
            # if not isinstance(source,JAPAN_CANDLE):
            #     source.deleteLater()
    
    def get_source(self,_source_name) ->HEIKINASHI|SMOOTH_CANDLE|JAPAN_CANDLE|N_SMOOTH_CANDLE:
        return self.sources[_source_name]
    
    def generate_source(self,interval):
        "Tạo source cùng symbol khác interval để phục vụ logic nếu cần"
        self.generate_source_worker(exchange_name=self.exchange_name,symbol=self.symbol,interval=interval)
    def generate_source_worker(self,exchange_name:str="binanceusdm",symbol:str="",interval:str=""):
        pass

    def on_reset_exchange(self,args):
        self.sig_show_process.emit(True)
        self.sig_reset_exchange = True
        """("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path)"""

        cr_id = f"{self.symbol}_{self.interval}"
        asyncio.run(self.remove_from_exchanges(cr_id)) 
        _type, symbol, exchange_name = args[0],args[1],args[2]
        
        if exchange_name != self.exchange_name:
            self.exchange_name = exchange_name
            self.crypto_ex = CryptoExchange().setupEchange(apikey=self.apikey, secretkey=self.secretkey,exchange_name=self.exchange_name)

        try:
            asyncio.run(self.crypto_ex_ws.close()) 
            self.crypto_ex_ws = None
            self.crypto_ex = None
        except:
            pass
        self.crypto_ex_ws = CryptoExchange_WS().setupEchange(apikey=self.apikey, secretkey=self.secretkey,exchange_name=self.exchange_name)
        
        self.symbol = symbol
        self.is_reseting =  False
        self.sig_change_tab_infor.emit((self.symbol,self.interval))

        self.fast_reset_worker(exchange_name=exchange_name,symbol=symbol,interval=self.interval)
    
    def on_change_inteval(self,args):
        """
        ("change_interval",interval)
        """
        self.sig_show_process.emit(True)
        
        cr_id = f"{self.symbol}_{self.interval}"
        asyncio.run(self.remove_from_exchanges(cr_id)) 
        
        self.sig_reset_exchange = True
        _type, interval = args[0],args[1]
        self.interval = interval
        self.is_reseting =  False
        
        try:
            asyncio.run(self.crypto_ex_ws.close()) 
            self.crypto_ex_ws = None
            self.crypto_ex = None
        except:
            pass
        
        self.crypto_ex_ws = CryptoExchange_WS().setupEchange(apikey=self.apikey, secretkey=self.secretkey,exchange_name=self.exchange_name)

        self.sig_change_tab_infor.emit((self.symbol,self.interval))

        self.fast_reset_worker(exchange_name=self.exchange_name,symbol=self.symbol,interval=interval)
    
    
    def fast_reset_worker(self,apikey:str="",secretkey:str="",exchange_name:str="binanceusdm",symbol:str="",interval:str=""):
        if self.worker != None:
            if isinstance(self.worker,FastStartThread):
                self.worker.stop_thread()
        self.worker = None
        self.worker = FastStartThread(self.reset_exchange, apikey,secretkey,exchange_name,symbol,interval)
        self.worker.start_thread()

    async def reset_exchange(self,apikey:str="",secretkey:str="",exchange_name:str="binanceusdm",symbol:str="",interval:str=""):
        if apikey != "":
            self.apikey = apikey
        if secretkey != "":
            self.secretkey = secretkey
        
        new_echange = {"id":f"{symbol}_{interval}","exchange":self.crypto_ex_ws}
        self.add_to_exchanges(new_echange)
        # exchange.streaming['keepAlive'] = 10000 
        # exchange.streaming['maxPingPongMisses'] = 1
        data = [] 
        if not self.crypto_ex:
            self.crypto_ex = CryptoExchange().setupEchange(apikey=self.apikey, secretkey=self.secretkey,exchange_name=self.exchange_name)      
        self.crypto_ex.load_markets()
        await self.crypto_ex_ws.load_markets()
        data = await self.crypto_ex_ws.fetch_ohlcv(symbol,interval,limit=1500) 
        if len(data) == 0:
            raise BadSymbol(f"{self.exchange_name} data not received")
        self.set_market_by_symbol(self.crypto_ex)
        self.jp_candle.fisrt_gen_data(data,self._precision)
        self.jp_candle.source_name = f"jp {self.symbol} {self.interval}"
        self.update_sources(self.jp_candle)
        
        self.heikinashi.source_name = f"heikin {self.symbol} {self.interval}"
        self.update_sources(self.heikinashi)
        self.heikinashi.fisrt_gen_data()
        
        await self.loop_watch_ohlcv(symbol,interval)
        
    async def loop_watch_ohlcv(self,symbol,interval):
        print("start loop__________")
        firt_run = False
        _ohlcv = []
        while self.crypto_ex_ws in list(self.exchanges.values()):
            if self.exchanges == {}:
                break
            if not (self.symbol == symbol and self.interval == interval and self.crypto_ex.id == self.exchange_name):
                AppLogger.writer("INFO",f"{__name__} - {self.crypto_ex.id}-{symbol}-{interval} have changed to {self.exchange_name}-{self.symbol}-{self.interval}")
                break
            if self.crypto_ex != None:
                if (self.symbol == symbol and self.interval == interval and self.crypto_ex.id == self.exchange_name):
                    try:
                        if "watchOHLCV" in list(self.crypto_ex_ws.has.keys()):
                            if _ohlcv == []:
                                _ohlcv = self.crypto_ex.fetch_ohlcv(symbol,interval,limit=2)
                            else:
                                ohlcv = await self.crypto_ex_ws.watch_ohlcv(symbol,interval,limit=2)
                                if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                                    _ohlcv[-1] = ohlcv[-1]
                                else:
                                    _ohlcv.append(ohlcv[-1])
                                    _ohlcv = _ohlcv[-2:]
                        elif "fetchOHLCV" in list(self.crypto_ex.has.keys()):
                            _ohlcv = self.crypto_ex.fetch_ohlcv(symbol,interval,limit=2)
                        else:
                            await asyncio.sleep(0.3)
                            continue
                    except Exception as ex:
                        print(ex)
                        await asyncio.sleep(0.3)
                        continue
                    
                    if len(_ohlcv) >= 2 and (self.symbol == symbol and self.interval == interval and self.crypto_ex.id == self.exchange_name):
                        pre_ohlcv = OHLCV(_ohlcv[-2][1],_ohlcv[-2][2],_ohlcv[-2][3],_ohlcv[-2][4], round((_ohlcv[-2][2]+_ohlcv[-2][3])/2,self._precision) , round((_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/3,self._precision), round((_ohlcv[-2][1]+_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/4,self._precision),_ohlcv[-2][5],_ohlcv[-2][0]/1000,0)
                        last_ohlcv = OHLCV(_ohlcv[-1][1],_ohlcv[-1][2],_ohlcv[-1][3],_ohlcv[-1][4], round((_ohlcv[-1][2]+_ohlcv[-1][3])/2,self._precision) , round((_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/3,self._precision), round((_ohlcv[-1][1]+_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/4,self._precision),_ohlcv[-1][5],_ohlcv[-1][0]/1000,0)
                        _is_add_candle = self.jp_candle.update([pre_ohlcv,last_ohlcv])
                        
                        self.heikinashi.update(self.jp_candle.candles[-2:],_is_add_candle)
      
                        if firt_run == False:
                            self.first_run.emit()
                            firt_run = True
                else:
                    if self.crypto_ex != None:
                        AppLogger.writer("warning",f"{__name__} - {self.crypto_ex.id}-{symbol}-{interval} have changed to {self.exchange_name}-{self.symbol}-{self.interval}")
                    break
            else:
                break
            try:
                await asyncio.sleep(self.time_delay)
            except:
                pass
        if self.crypto_ex != None:
            AppLogger.writer("INFO",f"{__name__} - {symbol}-{interval} have closed")
        try:
            # await exchange.close()
            AppLogger.writer("INFO",f"{__name__} - {self.crypto_ex.id}-{symbol}-{interval} have closed")
            print(f"turn-off {self.crypto_ex.id}-{symbol}-{interval}")
        except Exception as e:
            print("turn-off with error!!!")
        
 
    async def close(self):
        if self.crypto_ex_ws != None:
            await self.crypto_ex_ws.close()
        self.exchanges.clear()
        if self.worker != None:
            if isinstance(self.worker,FastStartThread):
                self.worker.stop_thread()
        ThreadPoolExecutor_global.shutdown()

    def set_market_by_symbol(self,exchange):
        """
        - Binance
        {'id': 'BTCUSDT', 'lowercaseId': 'btcusdt', 'symbol': 'BTC/USDT:USDT', 'base': 'BTC', 'quote': 'USDT', 
        'settle': 'USDT', 'baseId': 'BTC', 'quoteId': 'USDT', 'settleId': 'USDT', 'type': 'swap', 'spot': False, 
        'margin': False, 'swap': True, 'future': False, 'option': False, 'active': True, 'contract': True, 
        'linear': True, 'inverse': False, 'taker': 0.0004, 'maker': 0.0002, 'contractSize': 1.0, 'expiry': None, 
        'expiryDatetime': None, 'strike': None, 'optionType': None, 'precision': {'amount': 3, 'price': 1, 'base': 8, 
        'quote': 8}, 'limits': {'leverage': {'min': None, 'max': None}, 'amount': {'min': 0.001, 'max': 1000.0}, 
        'price': {'min': 556.8, 'max': 4529764.0}, 'cost': {'min': 100.0, 'max': None}, 
        'market': {'min': 0.001, 'max': 120.0}}, 'info': {'symbol': 'BTCUSDT', 'pair': 'BTCUSDT', 
        'contractType': 'PERPETUAL', 'deliveryDate': '4133404800000', 'onboardDate': '1569398400000', 
        'status': 'TRADING', 'maintMarginPercent': '2.5000', 'requiredMarginPercent': '5.0000', 'baseAsset': 'BTC', 
        'quoteAsset': 'USDT', 'marginAsset': 'USDT', 
        'pricePrecision': '2', 'quantityPrecision': '3', 'baseAssetPrecision': '8', 'quotePrecision': '8', 
        'underlyingType': 'COIN', 'underlyingSubType': ['PoW'], 'settlePlan': '0', 'triggerProtect': '0.0500', 
        'liquidationFee': '0.012500', 'marketTakeBound': '0.05', 'maxMoveOrderLimit': '10000', 
        'filters': [{'tickSize': '0.10', 'maxPrice': '4529764', 'filterType': 'PRICE_FILTER', 'minPrice': '556.80'}, 
        {'minQty': '0.001', 'stepSize': '0.001', 'filterType': 'LOT_SIZE', 'maxQty': '1000'}, 
        {'minQty': '0.001', 'filterType': 'MARKET_LOT_SIZE', 'maxQty': '120', 'stepSize': '0.001'}, 
        {'filterType': 'MAX_NUM_ORDERS', 'limit': '200'}, {'limit': '10', 'filterType': 'MAX_NUM_ALGO_ORDERS'}, 
        {'notional': '100', 'filterType': 'MIN_NOTIONAL'}, 
        {'multiplierDecimal': '4', 'multiplierUp': '1.0500', 'multiplierDown': '0.9500', 'filterType': 'PERCENT_PRICE'}], 
        'orderTypes': ['LIMIT', 'MARKET', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET'], 
        'timeInForce': ['GTC', 'IOC', 'FOK', 'GTX', 'GTD']}, 'created': 1569398400000}
        """
        market = exchange.market(self.symbol)
        #print(market)
        _precision = convert_precicion(market['precision']['price'])
        self.set_precision(_precision)
        #print("self._precision", self._precision)

    def get_candle(self,_type:str="japan"):
        candle = CandleStick(self,_type)
        return candle
    
    def setup_indicator(self,indicator_data):
        _group_indicator = indicator_data[0][0]
        _indicator_type = indicator_data[0][1]
        mainwindow = indicator_data[1]
        # print("view chart", _group_indicator,_indicator_type)
        if _group_indicator == "Basic Indicator":
            indicator = BasicMA(self,indicator_type=_indicator_type,length=30,_type="close",pen="#ffaa00")
            panel = IndicatorPanel(mainwindow,self, indicator)
            self.container_indicator_wg.add_indicator_panel(panel)
            self.add_item(indicator)
            indicator.fisrt_gen_data()

        elif _group_indicator == "Candle Indicator":
            candle:CandleStick = self.get_candle(_indicator_type)
            panel = IndicatorPanel(mainwindow,self, candle)
            # self.container_indicator_wg.sig_add_panel.emit(panel)
            self.container_indicator_wg.add_indicator_panel(panel)
            #self.sig_add_item.emit(candle)
            self.add_item(candle)
            candle.first_setup_candle()
            if isinstance(candle.source,JAPAN_CANDLE): 
                self.auto_xrange()
            candle.source.sig_add_candle.emit(candle.source.candles[-2:])

        elif _group_indicator == "Advance Indicator":
            
            if _indicator_type==IndicatorType.BB:
                indicator = BasicBB(self)
                panel = IndicatorPanel(mainwindow,self, indicator)
                self.container_indicator_wg.add_indicator_panel(panel)
                self.add_item(indicator)
                indicator.fisrt_gen_data()
                
            elif _indicator_type==IndicatorType.DonchianChannels:
                indicator = BasicDonchianChannels(self)
                panel = IndicatorPanel(mainwindow,self, indicator)
                self.container_indicator_wg.add_indicator_panel(panel)
                self.add_item(indicator)
                indicator.fisrt_gen_data()
            elif _indicator_type==IndicatorType.ZIGZAG:
                indicator = BasicZIGZAG(self)
                panel = IndicatorPanel(mainwindow,self, indicator)
                self.container_indicator_wg.add_indicator_panel(panel)
                self.add_item(indicator)
                indicator.fisrt_gen_data()
                
    def set_data_dataconnect(self):
        if self.list_candle_indicators == []:
            "load data when starting app"
            self.sig_reload_indicator_panel.emit()
        else:  
            "change interval/symbol data when starting app"
            self.jp_candle.sig_add_candle.emit(self.jp_candle.candles[-2:])
            self.auto_xrange()
        self.sig_show_process.emit(False)
        self.is_reseting =  False
        self.sig_reset_exchange = False

    def mousePressEvent(self, ev):
        # print(self.drawtool.draw_object_name)
        if self.mouse_on_vb and ev.button() & Qt.MouseButton.LeftButton:
            if self.drawtool.draw_object_name ==  "draw_trenlines":
                self.drawtool.draw_trenlines(ev)
            elif self.drawtool.draw_object_name ==  "draw_horizontal_line":
                self.drawtool.draw_horizontal_line(ev)
            elif self.drawtool.draw_object_name ==  "draw_horizontal_ray":
                self.drawtool.draw_horizontal_ray(ev)
            elif self.drawtool.draw_object_name ==  "draw_fibo_retracement":
                self.drawtool.draw_fibo(ev)
            elif self.drawtool.draw_object_name ==  "draw_fibo_2":
                self.drawtool.draw_fibo_2(ev)
            elif self.drawtool.draw_object_name ==  "draw_rectangle":
                self.drawtool.draw_rectangle(ev)
            elif self.drawtool.draw_object_name ==  "draw_text":
                self.drawtool.draw_text(ev)
            elif self.drawtool.draw_object_name ==  "draw_path":
                self.drawtool.draw_path(ev)
            elif self.drawtool.draw_object_name == "draw_date_price_range":
                self.drawtool.draw_date_price_range(ev)
            elif self.drawtool.draw_object_name ==  "draw_verticallines":
                self.drawtool.draw_verticallines(ev)
            else:
                pass
                # if self.drawtool.draw_object_name in ["drawed_trenlines", "drawed_fibo_retracement", "drawed_fibo_retracement_2", "drawed_rectangle", "drawed_date_price_range"]:
                #     self.drawtool.draw_object_name =None
                #     self.drawtool.drawing_object.finished = True
                #     self.drawtool.drawing_object.on_click.emit(self.drawtool.drawing_object)
                #     self.drawtool.drawing_object = None
                
        super().mousePressEvent(ev)

    def get_position_crosshair(self):
        return self.vLine.getXPos(), self.hLine.getYPos()
    
    def roll_till_now(self,):
        vr = self.viewRect()
        height = vr.height()
        # close_price = datasrc.df.columns[2]
        y1 = self.last_close_price + height / 2
        y0 = y1 - height
        self.setYRange(y1, y0, padding=0.2)
        x1 = self.timedata[-1]
        x0 = x1 - 400*covert_time_to_sec(self.interval)
        ##print(752, "Rolling", x1, x0, self.timedata[-400])
        self.setXRange(x1, x0, padding=0.5)

    def keyPressEvent(self, ev: QKeyEvent):
        if ev.key() == Qt.Key.Key_Delete:
            pass

        elif ev.modifiers() == Qt.KeyboardModifier.AltModifier:
            #print("Enter Ctrl V",ev.keyCombination(), ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_V))
            if ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_T):
                self.drawtool.draw_object_name = "draw_trenlines"
            elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_H):
                self.drawtool.draw_object_name =  "draw_horizontal_line"
            elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_J):
                self.drawtool.draw_object_name =  "draw_horizontal_ray"
            elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_F):
                self.drawtool.draw_object_name =  "draw_fibo_retracement"
            elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_V):
                self.drawtool.draw_object_name =  "draw_verticallines"
            # elif ev.keyCombination() == QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_J):
            #     self.drawtool.draw_object_name ==  "draw_horizontal_ray"

        return super().keyPressEvent(ev)       
    

    