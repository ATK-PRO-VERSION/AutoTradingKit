
from typing import Any, Dict
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from atklip.app_utils.calculate import convert_precicion
from .models import *
from .ta_indicators import *
from .ta_indicators import IndicatorType
from .socketmanager import ConnectionManager


class IndicatorManager:
    def __init__(self,managersocket) -> None:
        self.map_candle:Dict[str:Any] = {}
        self.map_indicator:Dict[str:Any] = {}
        self.map_candle_indicator: Dict[str:list] = {}
        self.managersocket:ConnectionManager = managersocket

    def send_msg(self,data, websocket:WebSocket):    
        asyncio.run(websocket.send_text(json.dumps(data)))

    def reset_candle(self,client_exchange,old_candle_infor,new_candle_infor):
        new_symbol:str=new_candle_infor.get("symbol")
        new_interval:str=new_candle_infor.get("interval")
        new_id_exchange:str = new_candle_infor.get("id_exchange")
        
        data = client_exchange.fetch_ohlcv(new_symbol,new_interval,limit=1500) 
        market = client_exchange.market(new_symbol)
        _precision = convert_precicion(market['precision']['price'])
        
        old_candle_infor["name"] = "japancandle"
        jp_candle:JAPAN_CANDLE = self.get_candle(old_candle_infor)
        jp_name = f"{new_id_exchange}-japancandle-{new_symbol}-{new_interval}"
        self.map_candle[jp_name] = jp_candle
        jp_candle.source_name = jp_name
        jp_candle.fisrt_gen_data(data,_precision)
        jp_candle.sig_reset_source.emit(jp_candle.source_name)
        
        old_candle_infor["name"] = "heikinashi"
        heikin_candle:HEIKINASHI = self.get_candle(old_candle_infor)
        heikin_name = f"{new_id_exchange}-heikinashi-{new_symbol}-{new_interval}"
        
        self.map_candle[heikin_name] = heikin_candle
        heikin_candle.source_name = heikin_name
        heikin_candle.update_source(jp_candle)
        heikin_candle.fisrt_gen_data()
        heikin_candle.sig_reset_source.emit(heikin_candle.source_name)

        return jp_candle, heikin_candle,new_symbol,new_interval, _precision
        

    def create_exchange(self,crypto_ex,candle_infor:dict):
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:IndicatorType=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        
        data = crypto_ex.fetch_ohlcv(symbol,interval,limit=1500) 
        # print(data)
        market = crypto_ex.market(symbol)
        _precision = convert_precicion(market['precision']['price'])
        
        candle_infor["name"] = "japancandle"
        
        jp_candle:JAPAN_CANDLE = self.add_candle(candle_infor)
        jp_candle.fisrt_gen_data(data,_precision)
        
        candle_infor["name"] = "heikinashi"
        
        heikin_candle:HEIKINASHI = self.add_candle(candle_infor)
        heikin_candle.fisrt_gen_data()
        return jp_candle,heikin_candle,symbol,interval,_precision


    def add_new_candle(self,candle_infor:dict,pre_active_candles:dict):
        if pre_active_candles["smoothcandle"] == True:
            candle_infor["name"] = "smoothcandle"
            smoothcandle:SMOOTH_CANDLE = self.add_candle(candle_infor)
            smoothcandle.fisrt_gen_data()
        
        if pre_active_candles["supersmoothcandle"] == True:
            candle_infor["name"] = "supersmoothcandle"
            supersmoothcandle:N_SMOOTH_CANDLE = self.add_candle(candle_infor)
            supersmoothcandle.fisrt_gen_data()
        

    async def loop_watch_ohlcv(self,websocket:WebSocket,crypto_ex_ws,jp_candle:JAPAN_CANDLE,heikin_candle:HEIKINASHI,symbol,interval,_precision):
        _ohlcv = []
        while self.managersocket.socket_is_active(websocket):
            if "watchOHLCV" in list(crypto_ex_ws.has.keys()):
                if _ohlcv == []:
                    _ohlcv = await crypto_ex_ws.fetch_ohlcv(symbol,interval,limit=2)
                else:
                    ohlcv = await crypto_ex_ws.watch_ohlcv(symbol,interval,limit=2)
                    if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                        _ohlcv[-1] = ohlcv[-1]
                    else:
                        _ohlcv.append(ohlcv[-1])
                        _ohlcv = _ohlcv[-2:]
            elif "fetchOHLCV" in list(crypto_ex_ws.has.keys()):
                _ohlcv = await crypto_ex_ws.fetch_ohlcv(symbol,interval,limit=2)
            else:
                await asyncio.sleep(0.3)

            _is_add_candle = False
            if len(_ohlcv) >= 2:
                pre_ohlcv = OHLCV(_ohlcv[-2][1],_ohlcv[-2][2],_ohlcv[-2][3],_ohlcv[-2][4], round((_ohlcv[-2][2]+_ohlcv[-2][3])/2,_precision) , round((_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/3,_precision), round((_ohlcv[-2][1]+_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/4,_precision),_ohlcv[-2][5],_ohlcv[-2][0]/1000,0)
                last_ohlcv = OHLCV(_ohlcv[-1][1],_ohlcv[-1][2],_ohlcv[-1][3],_ohlcv[-1][4], round((_ohlcv[-1][2]+_ohlcv[-1][3])/2,_precision) , round((_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/3,_precision), round((_ohlcv[-1][1]+_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/4,_precision),_ohlcv[-1][5],_ohlcv[-1][0]/1000,0)
                _is_add_candle = jp_candle.update([pre_ohlcv,last_ohlcv])
                heikin_candle.update(jp_candle.candles[-2:],_is_add_candle)
                # data = {"is_added_candle": False,"lastcandle":""}
                if _is_add_candle != None:
                    data = {"is_added_candle": _is_add_candle,
                            "lastcandle": jp_candle.candles[-1].__dict__}
                    try:
                        await websocket.send_text(json.dumps(data))
                    except (RuntimeError, WebSocketDisconnect):
                        break

    
    def add_indicator(self,ta_infor: dict):
        """_summary_
        Args:
            ta_param: indicator.indicator_name = ta_param
            source_name: candle.source_name
        Returns:
            _type_: _description_
        """
        # id_exchange = ta_infor.get("id_exchange")
        # symbol:str=ta_infor.get("symbol")
        # interval:str=ta_infor.get("interval")
        ta_name:str=ta_infor.get("ta_name")
        source_name:str=ta_infor.get("source_name")
        precicion:float=ta_infor.get("precicion") 
        indicator = None
        ta_id = ""
        ta_param = ""
        dict_ta_params = {}
        if ta_name == "zigzag":
            legs:str = ta_infor.get("legs")
            deviation:str = ta_infor.get("deviation")
            ta_param = f"{ta_name}-{legs}-{deviation}"
            dict_ta_params = {"name":ta_name,"legs":legs,"deviation":deviation}
            ta_id = f"{source_name}-{ta_param}"
            indicator = ZIGZAG(parent= None,
                    _candles= self.map_candle[source_name],
                    dict_ta_params=dict_ta_params)
            indicator.started_worker()
        list_indicator = self.map_candle_indicator.get(source_name,[])
        if list_indicator == []:
            self.map_candle_indicator[source_name] = [dict_ta_params]
        else:
            self.map_candle_indicator[source_name].append(dict_ta_params)
        
        indicator.indicator_name = ta_param
        indicator.dict_ta_params = dict_ta_params
        
        old_indicator = self.map_indicator.get(ta_id,None)
        if old_indicator != None:
            old_indicator.deleteLater()
        self.map_indicator[ta_id] = indicator
        return indicator
    
    def get_indicator(self,ta_infor: dict):
        """_summary_
        Args:
            ta_param: indicator.indicator_name = ta_param
            source_name: candle.source_name
        Returns:
            _type_: _description_
        """
        source_name:str=ta_infor.get("source_name")
        ta_param:str = ta_infor.get("ta_param")
        ta_id = f"{source_name}-{ta_param}"
        return self.map_indicator.get(ta_id,None)
    
    def get_ta_data(self,ta_infor: dict):
        indicator = self.get_indicator(ta_infor)
        if indicator != None:
            return indicator.get_data()

    def add_candle(self,candle_infor: dict)->JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE:
        id_exchange = candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:IndicatorType=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        precicion:float=candle_infor.get("precicion") 
        source_name = ""
        candle = None
        jp_name = f"{id_exchange}-japancandle-{symbol}-{interval}"
        heikin_name = f"{id_exchange}-heikinashi-{symbol}-{interval}"
        if name == "smoothcandle":
            source_name = f"{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}"
            if source == "japan":
                candle = self.map_candle[source_name] = SMOOTH_CANDLE(precicion,
                                                                    self.map_candle[jp_name],
                                                                    ma_type,
                                                                    ma_leng)
            else:
                candle = self.map_candle[source_name] = SMOOTH_CANDLE(precicion,
                                                                    self.map_candle[heikin_name],
                                                                    ma_type,
                                                                    ma_leng)
        elif name == "japancandle":
            source_name = f"{id_exchange}-{name}-{symbol}-{interval}"
            candle = self.map_candle[source_name] = JAPAN_CANDLE()
        elif name == "supersmoothcandle":
            source_name = f"{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}-{ma_leng}-{n_smooth}"
            if source == "japan":
                candle = self.map_candle[source_name] = N_SMOOTH_CANDLE(precicion,
                                                                        self.map_candle[jp_name],
                                                                        n_smooth,
                                                                        ma_type,
                                                                        ma_leng)
            else:
                candle = self.map_candle[source_name] = N_SMOOTH_CANDLE(precicion,
                                                                        self.map_candle[heikin_name],
                                                                        ma_type,
                                                                        ma_leng)
        elif name == "heikinashi":
            source_name = f"{id_exchange}-{name}-{symbol}-{interval}"
            candle = self.map_candle[source_name] = HEIKINASHI(precicion,self.map_candle[jp_name])
        if candle != None:
            candle.source_name = source_name
        return candle
    
    def get_list_indicator_of_candle(self,source_name):
        return self.map_candle_indicator.get(source_name,[])
    
    def clear_old_map_candle_indicator(self,old_source_name):
        list_indicator_param = self.get_list_indicator_of_candle(old_source_name)
        if list_indicator_param != []:
            del self.map_candle_indicator[old_source_name]
    
    def change_indicator_when_change_candle(self,old_source_name,new_source_name):
        list_indicator_param = self.get_list_indicator_of_candle(old_source_name)
        self.clear_old_map_candle_indicator(old_source_name)
        if list_indicator_param != []:
            for ta_param in list_indicator_param:
                old_ta_id = f"{old_source_name}-{ta_param}"
                new_ta_id = f"{new_source_name}-{ta_param}"
                indicator = self.map_indicator.get(old_ta_id,None)
                if indicator != None:
                    del self.map_indicator[old_ta_id]
                    indicator.indicator_name = new_ta_id
                    self.map_indicator[new_ta_id] = indicator
                    list_new_indicator_param = self.get_list_indicator_of_candle(new_source_name)
                    if list_new_indicator_param == []:
                        self.map_candle_indicator[new_source_name] = [ta_param]
                

    def get_list_indicator(self):
        return list(self.map_indicator.keys())
    
    def get_list_candles(self,candle_infor)-> list[dict]:
        id_exchange = candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:IndicatorType=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        
        japancandle_id = f"{id_exchange}-japancandle-{symbol}-{interval}"
        heikinashi_id = f"{id_exchange}-heikinashi-{symbol}-{interval}"
        output = []
        for candle_id in list(self.map_candle.keys()):
            if heikinashi_id == candle_id:
                output.append({self.map_candle[candle_id]:"heikinashi"}) 
            elif japancandle_id == candle_id:
                output.append({self.map_candle[candle_id]:"japancandle"}) 
            elif id_exchange in candle_id and "smoothcandle" in candle_id and f"{symbol}-{interval}" in candle_id:
                output.append({self.map_candle[candle_id]:"smoothcandle"}) 
            elif id_exchange in candle_id and "supersmoothcandle" in candle_id and f"{symbol}-{interval}" in candle_id:
                output.append({self.map_candle[candle_id]:"supersmoothcandle"})
        return output
    
    def delete_old_indicator(self,old_candle_infor):
        list_old_indicator = self.get_list_indicator_of_candle(old_candle_infor['source_name'])
    

    def get_candle(self,candle_infor:dict)->JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE:
        id_exchange = candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:IndicatorType=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        if name == "smoothcandle":
            return self.map_candle.get(f"{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}")
        elif name == "japancandle":
            return self.map_candle.get(f"{id_exchange}-{name}-{symbol}-{interval}") 
        elif name == "supersmoothcandle":
            return self.map_candle.get(f"{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}-{ma_leng}-{n_smooth}")
        elif name == "heikinashi":
            return self.map_candle.get(f"{id_exchange}-{name}-{symbol}-{interval}")
        return None
    
    def remove_indicator(self,indicator):
        if indicator.name in self.map_indicator:
            del self.map_indicator[indicator.name]
    
    def remove_candle(self,indicator):
        if indicator.name in self.map_indicator:
            del self.map_indicator[indicator.name]
    