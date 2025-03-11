from dataclasses import dataclass
import traceback,asyncio,time
import winloop
from typing import Dict, TYPE_CHECKING
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

from atklip.appmanager import FastStartThread,AppLogger,ThreadPoolExecutor_global,SimpleWorker
from atklip.appmanager.object.unique_object_id import objmanager, UniqueManager

from atklip.graphics.chart_component.indicator_panel import IndicatorPanel
from atklip.graphics.chart_component.base_items.replay_cut import ReplayObject

from atklip.controls.exchangemanager import ExchangeManager
from atklip.appmanager.setting import AppConfig

from psygnal import Signal

if TYPE_CHECKING:
    from .viewchart import Chart

@dataclass
class ExchangeModel():
    interval:str
    japan_cdl : JAPAN_CANDLE
    heikin_cdl: HEIKINASHI
    client_exchange:object
    ws_exchange:object
    worker:object
    worker_reload:asyncio.Task
    list_indicator:list
    is_active:bool
    precision: float
    quanty_precision: float
    

class INTERVALS():
    sig_change_symbol = Signal(str)
    sig_change_exchange = Signal(str)
    def __init__(self,chart:object):
        self.chart:Chart = chart
        self.exchange_name = self.chart.exchange_name
        self.symbol = self.chart.symbol
        
        self.intervals = ["1m","3m","5m","15m","30m","1h","2h","4h","6h","12h","1D","3D","1w"] #

        self._init_async_winloop()
        
        self.map_intervals_indicator:Dict[str,ExchangeModel] = {}
        self.Exchange_Manager = ExchangeManager()
        for interval in self.intervals:
            jp_cdl = JAPAN_CANDLE(self.chart)
            heikin_cdl = HEIKINASHI(self.chart,jp_cdl)
            self.map_intervals_indicator[interval] = ExchangeModel(interval,jp_cdl,heikin_cdl,None,None,None,None,[],False,2,3)
        
        self.keys = AppConfig.get_config_value(f"app.keys")

        if self.keys == None:
            api = ""
            secretkey = ""
            if "binance" in self.exchange_name:
                api = ""
                secretkey = ""
            AppConfig.sig_set_single_data.emit((f"app.keys",{self.exchange_name:{"apikey":api,"secretkey":secretkey}}))
            self.keys = AppConfig.get_config_value(f"app.keys")
            
        self.apikey = self.keys[self.exchange_name]["apikey"]
        self.secretkey = self.keys[self.exchange_name]["secretkey"]
        
        self.sig_change_symbol.connect(self.change_symbol)
        self.sig_change_exchange.connect(self.change_exchange)
    
    def get_jp_heikin_cdls_for_indicator(self,interval:str="1m",indicator: object=None):
        Exchangedata:ExchangeModel = self.map_intervals_indicator.get(interval,None)
        if not Exchangedata:
            Exchangedata = self.map_intervals_indicator[interval] = ExchangeModel(interval,jp_cdl,heikin_cdl,None,None,None,None,[],False,2,3)
        if Exchangedata.is_active:
            return Exchangedata.japan_cdl, Exchangedata.heikin_cdl
        
        Exchangedata.list_indicator.append(indicator)
        
        
        
        self.set_up_exchange(ExchangeModel=Exchangedata)
        
    
    def _init_async_winloop(self) -> asyncio.AbstractEventLoop: # type: ignore
        winloop.install()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
    
    def update_exchange_status(self,interval:str="1m"):
        data:ExchangeModel = self.map_intervals_indicator[interval]
        list_indicator = data.list_indicator
        if list_indicator:
            return
        worker:FastStartThread = data.worker
        worker.stop_thread()
        worker = None
        data.is_active = False
        asyncio.run(self.Exchange_Manager.remove_exchange(self.exchange_name,self.chart.id,self.symbol,interval))
        data.client_exchange = None
        data.ws_exchange = None
        data.worker_reload.cancel()
        data.list_indicator = []
        
    def check_active_exchange(self,interval:str):
        data:ExchangeModel = self.map_intervals_indicator[interval]
        is_active = data.is_active
        return is_active
    
    def set_up_exchange(self,ExchangeModel:ExchangeModel):
        interval:str = ExchangeModel.interval
        asyncio.run(self.Exchange_Manager.remove_exchange(self.exchange_name,self.chart.id,self.symbol,interval))
        ExchangeModel.client_exchange, ExchangeModel.ws_exchange = None,None
        ExchangeModel.client_exchange, ExchangeModel.ws_exchange = self.Exchange_Manager.add_exchange(self.exchange_name,self.chart.id,self.symbol,interval,self.apikey,self.secretkey)
        ExchangeModel.is_active = True
        
    async def reload_market(self,ExchangeModel:ExchangeModel):
        interval:str = ExchangeModel.interval
        ExchangeModel.worker_reload = asyncio.create_task(self.Exchange_Manager.reload_markets(self.exchange_name,self.chart.id,self.symbol,interval))
    
    def add_indicator_to_map(self,interval:str,indicator: object):
        self.map_intervals_indicator[interval].append(indicator) 
    
    def remove_indicator_from_map(self,interval:str,indicator: object):
        _indicators = self.map_intervals_indicator.get(interval,[])
        if _indicators:
            for _indicator in _indicators:
                if _indicator == indicator:
                    _indicators.remove(_indicator)
                    break
        self.map_intervals_indicator[interval] = _indicators
    
    def change_symbol(self,symbol:str):
        pass
    def change_exchange(self,exchange:str):
        pass
    
    def setup_interval(self,interval:str="1m"):
        pass
    
    def set_market_by_symbol(self,ExchangeModel:ExchangeModel):
        crypto_ex = ExchangeModel.client_exchange
        market = crypto_ex.market(self.symbol)
        ExchangeModel.precision = convert_precision(market['precision']['price'])
        ExchangeModel.quanty_precision = convert_precision(market['precision']['amount'])
        
    
    def set_precision(self,precision,quanty_precision):
        ExchangeModel.precision = precision
        self.quanty_precision= quanty_precision
    
    def check_all_indicator_updated(self,ExchangeModel:ExchangeModel):
        if ExchangeModel.list_indicator:
            for indicator in ExchangeModel.list_indicator:
                if not indicator.is_all_updated():
                        return False
        return True
    
    async def watch_ohlcv(self,ExchangeModel:ExchangeModel):
        crypto_ex = ExchangeModel.client_exchange
        interval = ExchangeModel.interval
        
        if not ExchangeModel.worker_reload:
            await self.reload_market(ExchangeModel)
        elif isinstance(ExchangeModel.worker_reload,asyncio.Task):
            ExchangeModel.worker_reload.cancel()
            await self.reload_market(ExchangeModel)
        
        data = [] 
        data = crypto_ex.fetch_ohlcv(self.symbol,interval,limit=1500) 
        if len(data) == 0:
            raise BadSymbol(f"{self.exchange_name} data not received")
        
        self.set_market_by_symbol(ExchangeModel)
        
        ExchangeModel.japan_cdl.fisrt_gen_data(data,ExchangeModel.precision)
        ExchangeModel.japan_cdl.source_name = f"jp {self.symbol} {interval}"
        # self.chart.update_sources(ExchangeModel.japan_cdl)
        ExchangeModel.heikin_cdl.source_name = f"heikin {self.symbol} {interval}"
        # self.chart.update_sources(ExchangeModel.heikin_cdl)
        ExchangeModel.heikin_cdl.fisrt_gen_data(ExchangeModel.precision)
        
        await self.loop_watch_ohlcv(ExchangeModel)
    
    
    async def loop_watch_ohlcv(self,ExchangeModel:ExchangeModel):
        interval = ExchangeModel.interval
        while True:
            client_socket = ExchangeModel.client_exchange
            ws_socket = ExchangeModel.ws_exchange

            if client_socket != None and ws_socket != None:
                try:
                    if "watchOHLCV" in list(ws_socket.has.keys()):
                        if _ohlcv == []:
                            _ohlcv = client_socket.fetch_ohlcv(self.symbol,interval,limit=2)
                            ohlcv = _ohlcv
                            if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                                _ohlcv[-1] = ohlcv[-1]
                            else:
                                _ohlcv = client_socket.fetch_ohlcv(self.symbol,interval,limit=2)
                            
                        else:
                            ohlcv = await ws_socket.watch_ohlcv(self.symbol,interval,limit=2)
                            if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                                _ohlcv[-1] = ohlcv[-1]
                            else:
                                _ohlcv = client_socket.fetch_ohlcv(self.symbol,interval,limit=2)
                                # _ohlcv.append(ohlcv[-1])
                                # _ohlcv = _ohlcv[-2:]
                    elif "fetchOHLCV" in list(client_socket.has.keys()):
                        _ohlcv = client_socket.fetch_ohlcv(self.symbol,interval,limit=2)
                    else:
                        await asyncio.sleep(0.3)
                        continue
                except Exception as ex:
                    print(ex)
                    await asyncio.sleep(0.3)
                    continue
                
                if len(_ohlcv) >= 2:
                    pre_ohlcv = OHLCV(_ohlcv[-2][1],
                                      _ohlcv[-2][2],
                                      _ohlcv[-2][3],
                                      _ohlcv[-2][4], 
                                      round((_ohlcv[-2][2]+_ohlcv[-2][3])/2,ExchangeModel.precision) , 
                                      round((_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/3,ExchangeModel.precision), 
                                      round((_ohlcv[-2][1]+_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/4,ExchangeModel.precision),_ohlcv[-2][5],_ohlcv[-2][0]/1000,0)
                    last_ohlcv = OHLCV(_ohlcv[-1][1],
                                       _ohlcv[-1][2],
                                       _ohlcv[-1][3],
                                       _ohlcv[-1][4], 
                                       round((_ohlcv[-1][2]+_ohlcv[-1][3])/2,ExchangeModel.precision) , 
                                       round((_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/3,ExchangeModel.precision), 
                                       round((_ohlcv[-1][1]+_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/4,ExchangeModel.precision),_ohlcv[-1][5],_ohlcv[-1][0]/1000,0)
                    
                    _is_add_candle = ExchangeModel.japan_cdl.update([pre_ohlcv,last_ohlcv])
                    ExchangeModel.heikin_cdl.update(ExchangeModel.japan_cdl.candles[-2:],_is_add_candle)
                    
                    is_updated =  self.check_all_indicator_updated(ExchangeModel)
                    while not is_updated:
                        print("all updated",is_updated)
                        is_updated =  self.check_all_indicator_updated(ExchangeModel)
                        time.sleep(0.3)
                        if is_updated:
                            print("all updated",is_updated)
                            break
            await asyncio.sleep(self.chart.time_delay)
