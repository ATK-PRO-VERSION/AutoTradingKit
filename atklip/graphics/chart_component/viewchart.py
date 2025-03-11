import traceback,asyncio,time
from typing import Dict
from PySide6 import QtCore
from PySide6.QtCore import Qt, QEvent, QCoreApplication, QKeyCombination, QThreadPool,QObject
from PySide6.QtGui import QKeyEvent,QImage
from atklip.app_utils.syncer import sync
from atklip.graphics.chart_component.base_items import CandleStick

from atklip.graphics.chart_component import ViewPlotWidget
from atklip.exchanges import CryptoExchange,CryptoExchange_WS
from ccxt.base.errors import *
# from ccxt.base.errors import BadSymbol
from atklip.controls import IndicatorType,OHLCV
from atklip.controls.candle import HEIKINASHI, SMOOTH_CANDLE,JAPAN_CANDLE, N_SMOOTH_CANDLE

from atklip.graphics.chart_component.draw_tools import *

from .unique_object_id import ObjManager

from atklip.app_utils import *

from atklip.appmanager import FastStartThread,AppLogger,SimpleWorker

from atklip.appmanager.object.unique_object_id import objmanager, UniqueManager

from atklip.graphics.chart_component.indicator_panel import IndicatorPanel
from atklip.graphics.chart_component.base_items.replay_cut import ReplayObject

from atklip.controls.exchangemanager import ExchangeManager
from atklip.appmanager.setting import AppConfig

from atklip.graphics.chart_component.indicators import *

class Chart(ViewPlotWidget):
    def __init__(self, parent=None,apikey:str="", secretkey:str="",exchange_name:str="binanceusdm",
                 symbol:str="BTCUSDT",interval:str="1m"):
        super(Chart,self).__init__(parent=parent)
        self._parent = parent
        
        self.objmanager:UniqueManager = objmanager
        self.id = self.objmanager.add(self)
        
        self.sig_reload_indicator_panel.connect(self._parent.reload_pre_indicator,Qt.ConnectionType.AutoConnection)
        self.apikey = apikey
        self.secretkey = secretkey
                
        self.exchange_name,self.symbol, self.interval =exchange_name, symbol,interval
        
        self.vb.symbol, self.vb.interval = self.symbol, self.interval
        
        self.ExchangeManager = ExchangeManager()
        
            
        self.apikey, self.secretkey = self.get_api_secret_key(self.exchange_name)
        
        self.worker = None
        self.worker_reload:asyncio.Task = None
        self.worker_auto_load_old_data = None
        
        self.sources: Dict[str:object] = {}
        
        self.is_load_historic = False
        self.time_delay = 0.5
        self.replay_speed = 1
        self.replay_data:list = []
        self.replay_pos_i:int = 0
                
        # self.f()
        self.crypto_ex = None
        self.crypto_ex_ws = None
        self.set_up_exchange()
        
        self.vb.load_old_data.connect(self.auto_load_old_data)
        self.sig_add_indicator_panel.connect(self.setup_indicator,Qt.ConnectionType.AutoConnection)
        self.first_run.connect(self.set_data_dataconnect,Qt.ConnectionType.AutoConnection)
        self.mouse_clicked_on_chart.connect(self.started_replay_mode)
        self.fast_reset_worker()
    
    def get_api_secret_key(self,exchange_name)-> tuple:
        keys = AppConfig.get_config_value(f"app.keys")
        if keys == None:
            api = ""
            secretkey = ""
            if "binance" in exchange_name:
                api = ""
                secretkey = ""
            AppConfig.sig_set_single_data.emit((f"app.keys.{exchange_name}",{"apikey":api,"secretkey":secretkey}))
            keys = AppConfig.get_config_value(f"app.keys")
        api_secret_keys = keys.get(exchange_name,None)
        if api_secret_keys is None:
            api = ""
            secretkey = ""
            if "binance" in exchange_name:
                api = ""
                secretkey = ""
            AppConfig.sig_set_single_data.emit((f"app.keys.{exchange_name}",{"apikey":api,"secretkey":secretkey}))
            keys = AppConfig.get_config_value(f"app.keys")
        apikey, secretkey= keys[exchange_name]["apikey"],keys[exchange_name]["secretkey"]
        return apikey, secretkey
        
    async def reload_market(self):
        self.worker_reload:asyncio.Task = asyncio.create_task(self.ExchangeManager.reload_markets(self.exchange_name,self.id,self.symbol,self.interval))
        
    @property
    def id(self):
        return self.chart_id
    
    @id.setter
    def id(self,_chart_id):
        self.chart_id = _chart_id
    
    @property
    def time_delay(self):
        return self._time_delay
    @time_delay.setter
    def time_delay(self,value):
        self._time_delay = value
    
    def change_mode(self):
        sender = self.sender()
        if self.is_trading:
            self.is_trading = False
            self.time_delay = 0.5
        else:
            self.is_trading = True
            self.time_delay = 0.01
            
    def set_replay_speed(self,text):
        if text == "0.5x ":
            self.replay_speed = 0.5
        elif text == "1x ":
            self.replay_speed = 1
        elif text == "2x ":
            self.replay_speed = 2
        elif text == "3x ":
            self.replay_speed = 3
        elif text == "5x ":
            self.replay_speed = 5
        elif text == "7x ":
            self.replay_speed = 7
        elif text == "10x ":
            self.replay_speed = 10
        elif text == "15x ":
            self.replay_speed = 15
    
    def set_replay_mode(self):
        btn = self.sender()     
        btn_name = btn.objectName()   
        if btn_name == "btn_replay":
            self.is_running_replay = False
            self.replay_data:list = []
            self.replay_pos_i:int = 0
            if btn.isChecked():
                self.replay_obj = ReplayObject(self)
                self.add_item(self.replay_obj)
                self.replay_mode = True
                self.drawtool.drawing_object = self.replay_obj
                # cursor = QtGui.QCursor(QImage(""))
                # self.setCursor(cursor)
            else:
                self.sig_show_process.emit(True)
                if isinstance(self.replay_obj,ReplayObject):
                    self.drawtool.drawing_object = None
                    self.remove_item(self.replay_obj)
                    self.replay_obj = None
                self.replay_mode = False
                self.set_up_exchange()
                self.fast_reset_worker()
        elif btn_name == "btn_seclect_bar":
            self.is_running_replay = False
            if btn.isChecked():
                self.replay_obj = ReplayObject(self)
                self.add_item(self.replay_obj)
                # self.replay_mode = True
                self.drawtool.drawing_object = self.replay_obj
            else:
                if isinstance(self.replay_obj,ReplayObject):
                    self.drawtool.drawing_object = None
                    self.remove_item(self.replay_obj)
                    self.replay_obj = None
                # self.replay_mode = False
        elif btn_name == "btn_close_playbar":
            self.is_running_replay = False
            self.replay_data:list = []
            self.replay_pos_i:int = 0
            self.sig_show_process.emit(True)
            if isinstance(self.replay_obj,ReplayObject):
                self.drawtool.drawing_object = None
                self.remove_item(self.replay_obj)
                self.replay_obj = None
            self.replay_mode = False
            self.set_up_exchange()
            self.fast_reset_worker()
    
    def started_replay_mode(self,event:QEvent):
        if isinstance(self.replay_obj,ReplayObject):
            index,posy = self.get_position_crosshair()
            # self.set_up_exchange()
            self.on_replay_reset_worker(index)

    def on_replay_reset_worker(self,index,is_goto: bool=False):
        if is_goto:
            self.is_goto_date = True
        self.replay_data:list = []
        self.replay_pos_i:int = 0
        self.sig_show_process.emit(True)
        if self.worker != None:
            if isinstance(self.worker,FastStartThread):
                self.worker.stop_thread()
        
        self.worker = FastStartThread(self.on_replay_mode_reset_exchange,index,is_goto)
        self.worker.start_thread()
    
    async def on_replay_mode_reset_exchange(self,index:int|float,is_goto: bool=False):
        data = [] 
        if is_goto:
            _cr_time = index
            
        else:
            ohlcv = self.jp_candle.map_index_ohlcv.get(index)
            if ohlcv:
                _cr_time = int(ohlcv.time)
            else:
                return
        
        # print(is_goto,_cr_time)
        
        data = self.crypto_ex.fetch_ohlcv(self.symbol,self.interval,limit=1500, params={"until":_cr_time*1000})
        
        if len(data) == 0:
            raise BadSymbol(f"{self.exchange_name} data not received")
        self.set_market_by_symbol(self.crypto_ex)
        self.jp_candle.fisrt_gen_data(data,self._precision)
        self.jp_candle.source_name = f"jp {self.symbol} {self.interval}"
        self.update_sources(self.jp_candle)
        
        self.heikinashi.source_name = f"heikin {self.symbol} {self.interval}"
        self.update_sources(self.heikinashi)
        self.heikinashi.fisrt_gen_data(self._precision)
        
        if isinstance(self.replay_obj,ReplayObject):
                self.drawtool.drawing_object = None
                self.remove_item(self.replay_obj)
                self.replay_obj = None
        self.auto_xrange()
        self.sig_show_process.emit(False)

    def worker_replay_loop_start(self):
        btn = self.sender()
        self.is_running_replay = btn.isChecked()
        if self.is_running_replay:
            if self.worker != None:
                if isinstance(self.worker,FastStartThread):
                    self.worker.stop_thread()
                self.worker = None
            
            self.worker = FastStartThread(self.replay_loop_start)
            self.worker.start_thread()
    

    def replay_forward_update(self):
        if not self.replay_data:
            ohlcv = self.jp_candle.candles[-1]
            _cr_time = int(ohlcv.time)
            _ohlcv = self.crypto_ex.fetch_ohlcv(self.symbol,self.interval,since=_cr_time*1000,limit=1500)
            self.replay_data = _ohlcv
            self.replay_pos_i = 0
        elif len(self.replay_data) == self.replay_pos_i+1:
            ohlcv = self.jp_candle.candles[-1]
            _cr_time = int(ohlcv.time)
            _ohlcv = self.crypto_ex.fetch_ohlcv(self.symbol,self.interval,since=_cr_time*1000,limit=1500)
            self.replay_data = _ohlcv
            self.replay_pos_i = 0
        
        pre_ohlcv = OHLCV(self.replay_data[self.replay_pos_i-1][1],self.replay_data[self.replay_pos_i-1][2],
                            self.replay_data[self.replay_pos_i-1][3],self.replay_data[self.replay_pos_i-1][4], 
                            round((self.replay_data[self.replay_pos_i-1][2]+self.replay_data[self.replay_pos_i-1][3])/2,self._precision) , 
                            round((self.replay_data[self.replay_pos_i-1][2]+self.replay_data[self.replay_pos_i-1][3]+self.replay_data[self.replay_pos_i-1][4])/3,self._precision), 
                            round((self.replay_data[self.replay_pos_i-1][1]+self.replay_data[self.replay_pos_i-1][2]+self.replay_data[self.replay_pos_i-1][3]+self.replay_data[self.replay_pos_i-1][4])/4,self._precision),
                            self.replay_data[self.replay_pos_i-1][5],self.replay_data[self.replay_pos_i-1][0]/1000,0)
        last_ohlcv = OHLCV(self.replay_data[self.replay_pos_i][1],
                            self.replay_data[self.replay_pos_i][2],
                            self.replay_data[self.replay_pos_i][3],
                            self.replay_data[self.replay_pos_i][4], 
                            round((self.replay_data[self.replay_pos_i][2]+self.replay_data[self.replay_pos_i][3])/2,self._precision) , 
                            round((self.replay_data[self.replay_pos_i][2]+self.replay_data[self.replay_pos_i][3]+self.replay_data[self.replay_pos_i][4])/3,self._precision), 
                            round((self.replay_data[self.replay_pos_i][1]+self.replay_data[self.replay_pos_i][2]+self.replay_data[self.replay_pos_i][3]+self.replay_data[self.replay_pos_i][4])/4,self._precision),self.replay_data[self.replay_pos_i][5],self.replay_data[self.replay_pos_i][0]/1000,0)
        
        _is_add_candle = self.jp_candle.update([pre_ohlcv,last_ohlcv])
        self.heikinashi.update(self.jp_candle.candles[-2:],_is_add_candle)   
        self.replay_pos_i += 1
        
        is_updated =  self.check_all_indicator_updated()
        while not is_updated:
            # print("all updated",is_updated)
            is_updated =  self.check_all_indicator_updated()
            time.sleep(0.1)
            if self.replay_mode or not self.exchange_name:
                self.trading_mode = False
                break
            if is_updated:
                break
                     
    
    async def replay_loop_start(self):
        _ohlcv = []
        while self.is_running_replay:    
            try:
                if not self.replay_data:
                    ohlcv = self.jp_candle.candles[-1]
                    _cr_time = int(ohlcv.time)
                    _ohlcv = self.crypto_ex.fetch_ohlcv(self.symbol,self.interval,since=_cr_time*1000,limit=1500)
                    self.replay_data = _ohlcv
                    self.replay_pos_i = 0
                elif len(self.replay_data) == self.replay_pos_i+1:
                    ohlcv = self.jp_candle.candles[-1]
                    _cr_time = int(ohlcv.time)
                    _ohlcv = self.crypto_ex.fetch_ohlcv(self.symbol,self.interval,since=_cr_time*1000,limit=1500)
                    self.replay_data = _ohlcv
                    self.replay_pos_i = 0
            except Exception as ex:
                print(ex)
                
            if len(self.replay_data)>1:
                autorange = 0
                for i in range(self.replay_pos_i,len(self.replay_data)):
                    autorange += 1
                    if autorange == 15:
                        self.auto_xrange()
                        autorange = 0
                    if self.is_running_replay:
                        if i == 0:
                            pre_ohlcv = self.jp_candle.candles[-1]
                        else:
                            pre_ohlcv = OHLCV(self.replay_data[self.replay_pos_i-1][1],self.replay_data[self.replay_pos_i-1][2],
                                                self.replay_data[self.replay_pos_i-1][3],self.replay_data[self.replay_pos_i-1][4], 
                                                round((self.replay_data[self.replay_pos_i-1][2]+self.replay_data[self.replay_pos_i-1][3])/2,self._precision) , 
                                                round((self.replay_data[self.replay_pos_i-1][2]+self.replay_data[self.replay_pos_i-1][3]+self.replay_data[self.replay_pos_i-1][4])/3,self._precision), 
                                                round((self.replay_data[self.replay_pos_i-1][1]+self.replay_data[self.replay_pos_i-1][2]+self.replay_data[self.replay_pos_i-1][3]+self.replay_data[self.replay_pos_i-1][4])/4,self._precision),
                                                self.replay_data[self.replay_pos_i-1][5],self.replay_data[self.replay_pos_i-1][0]/1000,0)
                        last_ohlcv = OHLCV(self.replay_data[self.replay_pos_i][1],
                                            self.replay_data[self.replay_pos_i][2],
                                            self.replay_data[self.replay_pos_i][3],
                                            self.replay_data[self.replay_pos_i][4], 
                                            round((self.replay_data[self.replay_pos_i][2]+self.replay_data[self.replay_pos_i][3])/2,self._precision) , 
                                            round((self.replay_data[self.replay_pos_i][2]+self.replay_data[self.replay_pos_i][3]+self.replay_data[self.replay_pos_i][4])/3,self._precision), 
                                            round((self.replay_data[self.replay_pos_i][1]+self.replay_data[self.replay_pos_i][2]+self.replay_data[self.replay_pos_i][3]+self.replay_data[self.replay_pos_i][4])/4,self._precision),self.replay_data[self.replay_pos_i][5],self.replay_data[self.replay_pos_i][0]/1000,0)
                        
                        
                        
                        _is_add_candle = self.jp_candle.update([pre_ohlcv,last_ohlcv])
                        self.heikinashi.update(self.jp_candle.candles[-2:],_is_add_candle)   
                        self.replay_pos_i = i
                        
                        last_point = self.jp_candle.candles[-1]
                        
                        if self.atkobj:
                            self.atkobj.move_entry(last_point.index,last_point.high,last_point.low)
                        
                        is_updated =  self.check_all_indicator_updated()
                        while not is_updated:
                            # print("all updated",is_updated)
                            is_updated =  self.check_all_indicator_updated()
                            await asyncio.sleep(0.1)
                            if self.replay_mode or not self.exchange_name:
                                self.trading_mode = False
                                break
                            if is_updated:
                                break   
                    else:
                        break
                    try:
                        await asyncio.sleep(1/self.replay_speed)
                    except:
                        pass
            else:
                break
                    
    def auto_load_old_data(self):
        "load historic data when wheel or drag viewbox"
        if isinstance(self.worker_auto_load_old_data,SimpleWorker):
            if not self.is_load_historic:
                self.worker_auto_load_old_data = None
        if not self.is_load_historic:
            x_range = self.getAxis('bottom').range
            left_xrange = x_range[0]
            right_xrange = x_range[1]
            if self.jp_candle.candles:
                first_candlestick_index = self.jp_candle.candles[0].index        
                if left_xrange < first_candlestick_index + 1500:
                    self.is_load_historic = True
                    self.worker_auto_load_old_data = SimpleWorker(fn=self.check_signal_load_old_data)
                    self.worker_auto_load_old_data.start_thread()
        
    def check_signal_load_old_data(self):
        if self.jp_candle.candles != []:
            _cr_time = self.jp_candle.candles[0].time
            data = self.crypto_ex.fetch_ohlcv(self.symbol,self.interval, params={"until":_cr_time*1000},limit=1500)
            self.jp_candle.load_historic_data(data,self._precision)
            self.heikinashi.load_historic_data(len(data))
        self.is_load_historic = False

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
    
    def delete_all_draw_obj(self):
        # if self.drawtools != []:
        while self.drawtools:
            tool = self.drawtools.pop()
            # for tool in self.drawtools:
            self.remove_item(tool)
        self.sig_remove_all_draw_obj.emit()
            
                
    def remove_source(self,source:HEIKINASHI|SMOOTH_CANDLE|JAPAN_CANDLE|N_SMOOTH_CANDLE):
        if source.source_name in list(self.sources.keys()):
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
    
    def set_up_exchange(self):
        self.ExchangeManager.clear()
        self.crypto_ex_ws,self.crypto_ex = None,None
        self.crypto_ex, self.crypto_ex_ws = self.ExchangeManager.add_exchange(self.exchange_name,self.id,self.symbol,self.interval,self.apikey,self.secretkey)
    
    def on_reset_exchange(self,args):
        """("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path)"""
        
        asyncio.run(self.ExchangeManager.remove_exchange(self.exchange_name,self.id,self.symbol,self.interval))
        
        _type, symbol, exchange_name = args[0],args[1],args[2]
        self.exchange_name = exchange_name
        self.symbol = symbol
        
        self.apikey, self.secretkey = self.get_api_secret_key(self.exchange_name)
        
        self.sig_show_process.emit(True)
        
        self.set_up_exchange()
        
        self.sig_change_tab_infor.emit((self.symbol,self.interval))

        self.fast_reset_worker()
    
    def on_change_inteval(self,args):
        """
        ("change_interval",interval)
        """
        asyncio.run(self.ExchangeManager.remove_exchange(self.exchange_name,self.id,self.symbol,self.interval))
        _type, interval = args[0],args[1]
        
        self.sig_show_process.emit(True)
        self.interval = interval
        
        self.set_up_exchange()
        
        self.sig_change_tab_infor.emit((self.symbol,self.interval))

        self.fast_reset_worker()
    
    def fast_reset_worker(self):
        self.is_goto_date = False
        self.is_running_replay = False
        self.replay_data:list = []
        self.replay_pos_i:int = 0
        self.replay_mode = False
        if self.worker != None:
            if isinstance(self.worker,FastStartThread):
                self.worker.stop_thread()
            self.worker = None
        
        self.worker = FastStartThread(self.reset_exchange)
        self.worker.start_thread()

    async def reset_exchange(self):
        data = [] 
        if not self.worker_reload:
            await self.reload_market()
        elif isinstance(self.worker_reload,asyncio.Task):
            self.worker_reload.cancel()
            await self.reload_market()
        # print("-------------reset_exchange------------",self.crypto_ex,self.symbol,self.interval)
        data = self.crypto_ex.fetch_ohlcv(self.symbol,self.interval,limit=1500) 
        if len(data) == 0:
            raise BadSymbol(f"{self.exchange_name} data not received")
        self.set_market_by_symbol(self.crypto_ex)
        self.jp_candle.fisrt_gen_data(data,self._precision)
        self.jp_candle.source_name = f"jp {self.symbol} {self.interval}"
        self.update_sources(self.jp_candle)
        
        self.heikinashi.source_name = f"heikin {self.symbol} {self.interval}"
        self.update_sources(self.heikinashi)
        self.heikinashi.fisrt_gen_data(self._precision)
        print("===========reset_exchange============ OK",self.crypto_ex,self.symbol,self.interval)
        self.auto_xrange()
        await self.loop_watch_ohlcv(self.symbol,self.interval,self.exchange_name)
    
    def check_all_indicator_updated(self):
        if self.indicators:
            for indicator in self.indicators:
                # print(indicator.is_all_updated())
                if not indicator.is_all_updated:
                    # print("false--------",indicator)
                    return False
        return True
    
    async def loop_watch_ohlcv(self,symbol,interval,exchange_name):
        self.trading_mode = True
        self.sig_show_process.emit(False)
        firt_run = False
        _ohlcv = []
        n = 0
        while True:
            client_socket = self.ExchangeManager.get_client_exchange(exchange_name,self.id,symbol,interval)
            ws_socket = self.ExchangeManager.get_ws_exchange(exchange_name,self.id,symbol,interval)
            
            if self.replay_mode or self.is_goto_date:
                print("close because of replay mode ON")
                if isinstance(self.worker_reload,asyncio.Task):
                    self.worker_reload.cancel()
                    self.worker_reload = None
                break
            
            if not client_socket and not ws_socket:
                break
            if not (self.symbol == symbol and self.interval == interval and self.exchange_name == exchange_name):
                break
            if client_socket != None and ws_socket != None:
                try:
                    if "watchOHLCV" in list(ws_socket.has.keys()):
                        if _ohlcv == []:
                            _ohlcv = client_socket.fetch_ohlcv(symbol,interval,limit=2)
                            ohlcv = _ohlcv
                            if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                                _ohlcv[-1] = ohlcv[-1]
                            else:
                                _ohlcv = client_socket.fetch_ohlcv(symbol,interval,limit=2)
                            
                        else:
                            ohlcv = await ws_socket.watch_ohlcv(symbol,interval,limit=2)
                            if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                                _ohlcv[-1] = ohlcv[-1]
                            else:
                                _ohlcv = client_socket.fetch_ohlcv(symbol,interval,limit=2)
                                # _ohlcv.append(ohlcv[-1])
                                # _ohlcv = _ohlcv[-2:]
                    elif "fetchOHLCV" in list(client_socket.has.keys()):
                        _ohlcv = client_socket.fetch_ohlcv(symbol,interval,limit=2)
                    else:
                        await asyncio.sleep(0.3)
                        continue
                except Exception as ex:
                    print(ex)
                    await asyncio.sleep(0.3)
                    continue
                
                if len(_ohlcv) >= 2 and (self.symbol == symbol and self.interval == interval and self.exchange_name == exchange_name):
                    pre_ohlcv = OHLCV(_ohlcv[-2][1],
                                      _ohlcv[-2][2],
                                      _ohlcv[-2][3],
                                      _ohlcv[-2][4], 
                                      round((_ohlcv[-2][2]+_ohlcv[-2][3])/2,self._precision) , 
                                      round((_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/3,self._precision), 
                                      round((_ohlcv[-2][1]+_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/4,self._precision),_ohlcv[-2][5],_ohlcv[-2][0]/1000,0)
                    last_ohlcv = OHLCV(_ohlcv[-1][1],
                                       _ohlcv[-1][2],
                                       _ohlcv[-1][3],
                                       _ohlcv[-1][4], 
                                       round((_ohlcv[-1][2]+_ohlcv[-1][3])/2,self._precision) , 
                                       round((_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/3,self._precision), 
                                       round((_ohlcv[-1][1]+_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/4,self._precision),_ohlcv[-1][5],_ohlcv[-1][0]/1000,0)
                    
                    _is_add_candle = self.jp_candle.update([pre_ohlcv,last_ohlcv])
                    self.heikinashi.update(self.jp_candle.candles[-2:],_is_add_candle)
                    
                    is_updated =  self.check_all_indicator_updated()
                    while not is_updated:
                        # print("all updated",is_updated)
                        is_updated =  self.check_all_indicator_updated()
                        await asyncio.sleep(0.1)
                        if self.replay_mode or not self.exchange_name:
                            self.trading_mode = False
                            break
                        if is_updated:
                            break
                    
                    if _is_add_candle:
                        last_point = self.jp_candle.candles[-1]
                        if self.atkobj:
                            self.atkobj.move_entry(last_point.index,last_point.high,last_point.low)
                        if self.is_trading:
                            n+=1
                            if n == 15:
                                self.roll_till_now()
                                n = 0 
                    if not firt_run:
                        if self.candle_object == None:
                            self.first_run.emit()
                        firt_run = True   
            else:
                break
            await asyncio.sleep(self.time_delay)

        try:
            AppLogger.writer("INFO",f"{__name__} - {symbol}-{interval} have closed")
            print(f"turn-off {symbol}-{interval}")
        except Exception as e:
            print("turn-off with error!!!")
        
    async def close(self):
        if isinstance(self.worker_reload,asyncio.Task):
            self.worker_reload.cancel()
            self.worker_reload = None
        self.ExchangeManager.clear()
        self.crypto_ex_ws,self.crypto_ex = None,None
        self.exchange_name = None
        self.id = None
        self.is_running_replay = False

    def set_market_by_symbol(self,exchange):
        market = exchange.market(self.symbol)
        _precision = convert_precision(market['precision']['price'])
        quanty_precision = convert_precision(market['precision']['amount'])
        self.set_precision(_precision,quanty_precision)
        # print("self._precision", self._precision)

    def get_candle(self,_type:str="japan"):
        candle = CandleStick(self,_type)
        return candle
    
    def setup_indicator(self,indicator_data):
        
        _group_indicator = indicator_data[0][0]
        _indicator_type = indicator_data[0][1]
        self.mainwindow = indicator_data[1]
        indicator = None
        # print("view chart", _group_indicator,_indicator_type)
        if _group_indicator == "Basic Indicators":
            indicator = BasicMA(self,indicator_type=_indicator_type,length=30,_type="close",pen="#ffaa00")

        elif _group_indicator == "Candle Idicators":
            _type = _indicator_type.value
            candle:CandleStick = self.get_candle(_type)
            panel = IndicatorPanel(self.mainwindow,self, candle)
            # self.container_indicator_wg.sig_add_panel.emit(panel)
            self.container_indicator_wg.add_indicator_panel(panel)
            #self.sig_add_item.emit(candle)
            self.add_item(candle)
            # candle.first_setup_candle()
            if isinstance(candle.source,JAPAN_CANDLE): 
                candle.source.sig_add_candle.emit(candle.source.candles[-2:])
                ohlcv = candle.source.candles[-1]
                data = [ohlcv.open,ohlcv.high,ohlcv.low,ohlcv.close]
                self.sig_show_candle_infor.emit(data)
                self.auto_xrange()
                self.sig_show_process.emit(False)
            if not isinstance(candle.source,JAPAN_CANDLE):
                self.indicators.append(candle) 
            else:
                self.candle_object = candle

        elif _group_indicator == "Advand Idicators":
            #________BASIC INDICATORS__________
            if _indicator_type==IndicatorType.BB:
                indicator = BasicBB(self)
   
            elif _indicator_type==IndicatorType.DonchianChannels:
                indicator = BasicDonchianChannels(self)
            
            elif _indicator_type==IndicatorType.KeltnerChannels:
                indicator = KeltnerChannels(self)

            elif _indicator_type==IndicatorType.ZIGZAG:
                indicator = BasicZIGZAG(self)
            
            elif _indicator_type==IndicatorType.VWMA:
                indicator = BASE_VWMA(self)
                
                
            #________Custom INDICATORS_________
            elif _indicator_type==IndicatorType.ATKPRO:
                indicator = ATKBOT(self)
            
            elif _indicator_type==IndicatorType.UTBOT:
                indicator = UTBOT(self)
            
            elif _indicator_type==IndicatorType.UTBOT_WITH_BBAND:
                indicator = UTBOT_WITH_BBAND(self)
            
            elif _indicator_type==IndicatorType.BUY_SELL_WITH_ETM_ST:
                indicator = EMA_SUPER_TREND_BOT(self)
            
            elif _indicator_type==IndicatorType.TRENDWITHSL:
                indicator = TrendStopLoss(self)
            
            elif _indicator_type==IndicatorType.SuperTrend:
                indicator = BasicSuperTrend(self)
            
            elif _indicator_type==IndicatorType.ATRSuperTrend:
                indicator = ATRSuperTrend(self)
            
            elif _indicator_type==IndicatorType.SMC:
                indicator = SMC(self)
        #________Candle Pattern________
        elif _group_indicator == "Paterns":
            if _indicator_type==IndicatorType.CANDLE_PATTERN:
                indicator = CandlePattern(self)
            elif _indicator_type==IndicatorType.CUSTOM_CANDLE_PATTERN:
                indicator = CustomCandlePattern(self)
                
        if indicator:
            self.indicators.append(indicator) 
            self.add_item(indicator)
            panel = IndicatorPanel(self.mainwindow,self, indicator)
            self.container_indicator_wg.add_indicator_panel(panel)
            indicator.fisrt_gen_data()

    def set_data_dataconnect(self):
        if self.indicators == []:
            "load data when starting app"
            self.sig_reload_indicator_panel.emit()
            self._add_crosshair()
        else:  
            "change interval/symbol data when starting app"
            self.jp_candle.sig_add_candle.emit(self.jp_candle.candles[-2:])
            self.auto_xrange()
        self.sig_show_process.emit(False)

    def mousePressEvent(self, ev):
        # print(self.drawtool.draw_object_name)
        if self.mouse_on_vb and ev.button() & Qt.MouseButton.LeftButton:
            if self.drawtool.draw_object_name ==  "draw_trenlines":
                self.drawtool.draw_trenlines(ev)
            elif self.drawtool.draw_object_name ==  "draw_horizontal_line":
                self.drawtool.draw_horizontal_line(ev)
            elif self.drawtool.draw_object_name ==  "draw_horizontal_ray":
                self.drawtool.draw_horizontal_ray(ev)
            elif self.drawtool.draw_object_name ==  "draw_verticallines":
                self.drawtool.draw_verticallines(ev)
                
                
            elif self.drawtool.draw_object_name ==  "draw_fib_retracement":
                self.drawtool.draw_fibo(ev)
            elif self.drawtool.draw_object_name ==  "draw_fib_retracement_2":
                self.drawtool.draw_fibo_2(ev)
            elif self.drawtool.draw_object_name ==  "draw_risk_reward_ratio":
                self.drawtool.draw_risk_reward_ratio(ev)
            
            
            elif self.drawtool.draw_object_name ==  "draw_long_position":
                self.drawtool.draw_long_position(ev)  
            elif self.drawtool.draw_object_name ==  "draw_short_position":
                self.drawtool.draw_short_position(ev)      
            
            elif self.drawtool.draw_object_name ==  "draw_rectangle":
                self.drawtool.draw_rectangle(ev)
            elif self.drawtool.draw_object_name ==  "draw_rotate_rectangle":
                self.drawtool.draw_rotate_rectangle(ev)
            elif self.drawtool.draw_object_name ==  "draw_path":
                self.drawtool.draw_path(ev)
            elif self.drawtool.draw_object_name ==  "draw_circle":
                self.drawtool.draw_circle(ev)
            elif self.drawtool.draw_object_name ==  "draw_elipse":
                self.drawtool.draw_ellipse(ev)
                   
            elif self.drawtool.draw_object_name ==  "draw_up_arrow":
                self.drawtool.draw_up_arrow(ev)
            elif self.drawtool.draw_object_name ==  "draw_down_arrow":
                self.drawtool.draw_down_arrow(ev)
            elif self.drawtool.draw_object_name ==  "draw_arrow":
                self.drawtool.draw_arrow(ev)
                   
                
            elif self.drawtool.draw_object_name ==  "draw_text":
                self.drawtool.draw_text(ev)   
            elif self.drawtool.draw_object_name ==  "draw_note":
                self.drawtool.draw_text(ev)    
            
            elif self.drawtool.draw_object_name == "draw_date_price_range":
                self.drawtool.draw_date_price_range(ev)
            elif self.drawtool.draw_object_name == "draw_date_range":
                self.drawtool.draw_date_price_range(ev)
            elif self.drawtool.draw_object_name == "draw_price_range":
                self.drawtool.draw_date_price_range(ev)
                    
        super().mousePressEvent(ev)

    def get_position_crosshair(self):
        return self.vLine.getXPos(), self.hLine.getYPos()
    
    def roll_till_now(self):
        vr = self.viewRect()
        height = vr.height()
        y1 = self.jp_candle.candles[-1].close + height / 2
        y0 = y1 - height
        self.setYRange(y1, y0, padding=0.2)
        x1 = self.jp_candle.candles[-1].index
        self.setXRange(x1, x1-200, padding=0.5)
        self.auto_xrange()

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
    
    