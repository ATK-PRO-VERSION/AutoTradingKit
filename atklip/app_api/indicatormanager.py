
from typing import Any, Dict, List
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from atklip.app_utils.calculate import convert_precision
from ..controls.models import *
from .ta_indicators import *
from .ta_indicators import IndicatorType
from .socketmanager import ConnectionManager
from .socketmanager import ConnectionManager
from .exchangemanager import ExchangeManager

class IndicatorManager:
    def __init__(self) -> None:
        self.map_candle:Dict[str:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE] = {}
        self.map_indicator:Dict[str:Any] = {}
        self.map_candle_indicator:Dict[JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE:Any] = {}
        self.map_candle_smooth_candle :Dict[JAPAN_CANDLE|HEIKINASHI:SMOOTH_CANDLE|N_SMOOTH_CANDLE]= {}
        self.mnsocket:ConnectionManager = ConnectionManager()
        self.mnexchange:ExchangeManager= ExchangeManager()

    def send_msg(self,data, websocket:WebSocket):    
        asyncio.run(websocket.send_text(json.dumps(data)))

    def reset_candle(self,client_exchange,old_candle_infor,new_candle_infor):
        
        new_chart_id:str=new_candle_infor.get("chart_id")
        new_symbol:str=new_candle_infor.get("symbol")
        new_interval:str=new_candle_infor.get("interval")
        new_id_exchange:str = new_candle_infor.get("id_exchange")
        
        data = client_exchange.fetch_ohlcv(new_symbol,new_interval,limit=1500) 
        market = client_exchange.market(new_symbol)
        _precision = convert_precision(market['precision']['price'])
        
        old_candle_infor["name"] = "japancandle"
        jp_candle:JAPAN_CANDLE
        jp_candle, old_jp_candle_source_name = self.get_candle(old_candle_infor)
        jp_candle.set_candle_infor(new_id_exchange,new_symbol,new_interval)
        jp_candle.fisrt_gen_data(data,_precision)
        jp_name = f"{new_chart_id}-{new_id_exchange}-japancandle-{new_symbol}-{new_interval}"
        old_jp_name:str = jp_candle.source_name
        if old_jp_name in list(self.map_candle.keys()):
            self.map_candle[jp_name] = self.map_candle.pop(old_jp_name)
        else:
            self.map_candle[jp_name] = jp_candle
        jp_candle.source_name = jp_name
        
        
        old_candle_infor["name"] = "heikinashi"
        heikin_candle: HEIKINASHI
        heikin_candle, old_heikin_candle_source_name = self.get_candle(old_candle_infor)
        heikin_candle.update_source(jp_candle)
        heikin_candle.set_candle_infor(new_id_exchange,new_symbol,new_interval)
        heikin_candle.fisrt_gen_data()
        heikin_name = f"{new_chart_id}-{new_id_exchange}-heikinashi-{new_symbol}-{new_interval}"
        old_heikin_name:str = heikin_candle.source_name
        if old_heikin_name in list(self.map_candle.keys()):
            self.map_candle[heikin_name] = self.map_candle.pop(old_heikin_name)
        else:
            self.map_candle[heikin_name] = heikin_candle
        heikin_candle.source_name = heikin_name

        list_smooth_of_heikin:List[SMOOTH_CANDLE|N_SMOOTH_CANDLE] = self.get_list_smooth_of_candle(heikin_candle)
        list_smooth_of_japan:List[SMOOTH_CANDLE|N_SMOOTH_CANDLE] = self.get_list_smooth_of_candle(jp_candle)
        
        list_smooths:List[SMOOTH_CANDLE|N_SMOOTH_CANDLE] = list_smooth_of_heikin+list_smooth_of_japan
        if list_smooths != []:
            for sm_candle in list_smooths:
                old_source_name:str = sm_candle.source_name
                new_source_name:str = ""
                if old_source_name.__contains__("supersmoothcandle"):
                    new_source_name = f"{new_chart_id}-{sm_candle.canlde_id}-{new_id_exchange}-{sm_candle.source}-supersmoothcandle-{new_symbol}-{new_interval}-{sm_candle.ma_type}-{sm_candle.ma_leng}-{sm_candle.n}"
                elif old_source_name.__contains__("smoothcandle"):
                    new_source_name = f"{new_chart_id}-{sm_candle.canlde_id}-{new_id_exchange}-{sm_candle.source}-smoothcandle-{new_symbol}-{new_interval}-{sm_candle.ma_type}-{sm_candle.ma_leng}"

                if new_source_name != "":
                    if old_source_name in list(self.map_candle.keys()):
                        self.map_candle[new_source_name] = self.map_candle.pop(old_source_name)
                    else:
                        self.map_candle[new_source_name] = sm_candle
                    sm_candle.source_name = new_source_name

        "change indicator infor"
        all_new_change_markets = list_smooths+[jp_candle,heikin_candle]
        for candle in all_new_change_markets:
            list_indicators = self.get_list_indicator_of_candle(candle)
            if list_indicators != []:
                for indicator in list_indicators:
                    indicator.source_name = candle.source_name
        
        return jp_candle, heikin_candle,new_symbol,new_interval, _precision
        

    def setup_market(self,crypto_ex,candle_infor:dict):
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:str=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        try:
            data = crypto_ex.fetch_ohlcv(symbol,interval,limit=1500) 
        except:
            return None,None,None,None,None
        # print(data)
        market = crypto_ex.market(symbol)
        _precision = convert_precision(market['precision']['price'])
        
        candle_infor["name"] = "japancandle"
        
        jp_candle:JAPAN_CANDLE = self.add_candle(candle_infor)
        jp_candle.fisrt_gen_data(data,_precision)
        
        candle_infor["name"] = "heikinashi"
        
        heikin_candle:HEIKINASHI = self.add_candle(candle_infor)
        heikin_candle.fisrt_gen_data()
        return jp_candle,heikin_candle,symbol,interval,_precision
    
    def re_connect_market(self,crypto_ex,candle_infor:dict):
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:str=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        
        data = crypto_ex.fetch_ohlcv(symbol,interval,limit=50) 
        # print(data)
        market = crypto_ex.market(symbol)
        _precision = convert_precision(market['precision']['price'])
        
        candle_infor["name"] = "japancandle"
        jp_candle:JAPAN_CANDLE
        jp_candle,jp_name = self.get_candle(candle_infor) 
        if jp_candle == None:
            return None,None,None,None,None
        candle_infor["name"] = "heikinashi"
        heikin_candle:HEIKINASHI
        heikin_candle,heikin_name = self.get_candle(candle_infor)
        
        if heikin_candle == None:
            return None,None,None,None,None
        for i in range(len(data)):
            if i > 1:
                _ohlcv = data[i-1:i+1]
                pre_ohlcv = OHLCV(_ohlcv[-2][1],_ohlcv[-2][2],_ohlcv[-2][3],_ohlcv[-2][4], round((_ohlcv[-2][2]+_ohlcv[-2][3])/2,_precision) , round((_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/3,_precision), round((_ohlcv[-2][1]+_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/4,_precision),_ohlcv[-2][5],_ohlcv[-2][0]/1000,0)
                last_ohlcv = OHLCV(_ohlcv[-1][1],_ohlcv[-1][2],_ohlcv[-1][3],_ohlcv[-1][4], round((_ohlcv[-1][2]+_ohlcv[-1][3])/2,_precision) , round((_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/3,_precision), round((_ohlcv[-1][1]+_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/4,_precision),_ohlcv[-1][5],_ohlcv[-1][0]/1000,0)
                _is_add_candle = jp_candle.update([pre_ohlcv,last_ohlcv])
                heikin_candle.update(jp_candle.candles[-2:],_is_add_candle)
        return jp_candle,heikin_candle,symbol,interval,_precision
    
    def load_historic_data(self,candle_infor: dict)->dict:
        chart_id = candle_infor.get("chart_id")
        id_exchange = candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        precision:float=candle_infor.get("precision") 

        candle:SMOOTH_CANDLE|N_SMOOTH_CANDLE|JAPAN_CANDLE|HEIKINASHI = None
        jp_name = f"{chart_id}-{id_exchange}-japancandle-{symbol}-{interval}"
        heikin_name = f"{chart_id}-{id_exchange}-heikinashi-{symbol}-{interval}"
        
        jp_candle:JAPAN_CANDLE = self.map_candle.get(jp_name) 
        heikin_candle:HEIKINASHI = self.map_candle.get(heikin_name) 
        
        list_indicators:list = []
        output:dict = {}
        if jp_candle == None or heikin_candle == None:
            return output
        
        if jp_candle.candles != []:
            _cr_time = jp_candle.candles[0].time
            
            crypto_ex = self.mnexchange.map_chart_exchange[chart_id].get(f"client-{id_exchange}")
            if crypto_ex != None:
                data = crypto_ex.fetch_ohlcv(symbol,interval,limit=1500, params={"until":_cr_time*1000})
                _len = len(data)
                jp_candle.load_historic_data(data,precision)
                heikin_candle.load_historic_data(len(data))
                list_smooth_heikin = self.get_list_smooth_of_candle(heikin_candle)
                list_smooth_jp = self.get_list_smooth_of_candle(jp_candle)
                
                list_smooth_candles = list_smooth_heikin+list_smooth_jp
                list_candles = list_smooth_candles+[jp_candle,heikin_candle]
                for candle in list_candles:
                    list_indicators += self.get_list_indicator_of_candle(candle)   
                    if candle in list_smooth_candles:
                        # output.update({candle.source_name: "Done"})
                        while True:
                            if candle.is_histocric_load == True:
                                # output.update({candle.source_name: candle.get_index_data(stop=_len)})
                                output.update({candle.source_name: "Done"})
                                break
                    else:
                        # output.update({candle.source_name: candle.get_index_data(stop=_len)})
                        output.update({candle.source_name: "Done"})
                    
                if list_indicators != []:
                    for indicator in list_indicators:
                        # output.update({indicator.indicator_name: "Done"})
                        while True:
                            if indicator.is_histocric_load == True:
                                # output.update({indicator.indicator_name: indicator.get_data(stop=_len)})
                                output.update({indicator.indicator_name: "Done"})
                                indicator.is_histocric_load = False
                                break
        
        return output
    
    def reset_data(self,candle_infor: dict)->dict:
        chart_id = candle_infor.get("chart_id")
        id_exchange = candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        precision:float=candle_infor.get("precision") 

        candle:SMOOTH_CANDLE|N_SMOOTH_CANDLE|JAPAN_CANDLE|HEIKINASHI = None
        jp_name = f"{chart_id}-{id_exchange}-japancandle-{symbol}-{interval}"
        heikin_name = f"{chart_id}-{id_exchange}-heikinashi-{symbol}-{interval}"
        
        jp_candle:JAPAN_CANDLE = self.map_candle.get(jp_name) 
        heikin_candle:HEIKINASHI = self.map_candle.get(heikin_name) 
        
        list_indicators:list = []
        output:dict = {}
        if jp_candle == None or heikin_candle == None:
            return output
        
        if jp_candle.candles != []:            
            crypto_ex = self.mnexchange.map_chart_exchange[chart_id].get(f"client-{id_exchange}")
            if crypto_ex != None:
                data = crypto_ex.fetch_ohlcv(symbol,interval,limit=1500)
                
                jp_candle.fisrt_gen_data(data,precision)
                heikin_candle.fisrt_gen_data()
                list_smooth_heikin = self.get_list_smooth_of_candle(heikin_candle)
                list_smooth_jp = self.get_list_smooth_of_candle(jp_candle)
                
                list_smooth_candles = list_smooth_heikin+list_smooth_jp
                list_candles = list_smooth_candles+[jp_candle,heikin_candle]
                for candle in list_candles:
                    list_indicators += self.get_list_indicator_of_candle(candle)   
                    if candle in list_smooth_candles:
                        # output.update({candle.source_name: "Done"})
                        while True:
                            if candle.is_current_update == True:
                                # output.update({candle.source_name: candle.get_index_data(stop=_len)})
                                output.update({candle.source_name: "Done"})
                                candle.is_current_update = False
                                break
                    else:
                        # output.update({candle.source_name: candle.get_index_data(stop=_len)})
                        output.update({candle.source_name: "Done"})
                    
                if list_indicators != []:
                    for indicator in list_indicators:
                        # output.update({indicator.indicator_name: "Done"})
                        while True:
                            if indicator.is_current_update == True:
                                # output.update({indicator.indicator_name: indicator.get_data(stop=_len)})
                                output.update({indicator.indicator_name: "Done"})
                                indicator.is_current_update = False
                                break
        
        return output
    
    
    def goto_date(self,candle_infor: dict)->dict:
        chart_id = candle_infor.get("chart_id")
        id_exchange = candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        precision:float=candle_infor.get("precision") 
        gototime:int=candle_infor.get("gototime") 

        candle:SMOOTH_CANDLE|N_SMOOTH_CANDLE|JAPAN_CANDLE|HEIKINASHI = None
        jp_name = f"{chart_id}-{id_exchange}-japancandle-{symbol}-{interval}"
        heikin_name = f"{chart_id}-{id_exchange}-heikinashi-{symbol}-{interval}"
        
        jp_candle:JAPAN_CANDLE = self.map_candle.get(jp_name) 
        heikin_candle:HEIKINASHI = self.map_candle.get(heikin_name) 
        
        list_indicators:list = []
        output:dict = {}
        if jp_candle == None or heikin_candle == None:
            return output
        
        if jp_candle.candles != []:            
            crypto_ex = self.mnexchange.map_chart_exchange[chart_id].get(f"client-{id_exchange}")
            if crypto_ex != None:
                
                data = crypto_ex.fetch_ohlcv(symbol,interval,limit=1500, params={"until":gototime})
                
                jp_candle.fisrt_gen_data(data,precision)
                heikin_candle.fisrt_gen_data()
                list_smooth_heikin = self.get_list_smooth_of_candle(heikin_candle)
                list_smooth_jp = self.get_list_smooth_of_candle(jp_candle)
                
                list_smooth_candles = list_smooth_heikin+list_smooth_jp
                list_candles = list_smooth_candles+[jp_candle,heikin_candle]
                for candle in list_candles:
                    list_indicators += self.get_list_indicator_of_candle(candle)   
                    if candle in list_smooth_candles:
                        # output.update({candle.source_name: "Done"})
                        while True:
                            if candle.is_current_update == True:
                                # output.update({candle.source_name: candle.get_index_data(stop=_len)})
                                output.update({candle.source_name: "Done"})
                                candle.is_current_update = False
                                break
                    else:
                        # output.update({candle.source_name: candle.get_index_data(stop=_len)})
                        output.update({candle.source_name: "Done"})
                    
                if list_indicators != []:
                    for indicator in list_indicators:
                        # output.update({indicator.indicator_name: "Done"})
                        while True:
                            if indicator.is_current_update == True:
                                # output.update({indicator.indicator_name: indicator.get_data(stop=_len)})
                                output.update({indicator.indicator_name: "Done"})
                                indicator.is_current_update = False
                                break
        
        return output
    
    
    
    async def loop_watch_ohlcv(self,websocket:WebSocket,crypto_ex_ws,client_exchange,jp_candle:JAPAN_CANDLE,heikin_candle:HEIKINASHI,id_exchange,symbol,interval,_precision):
        _ohlcv = []
        while True:
            if not self.mnsocket.socket_is_active(websocket):
                try:
                    ws_market = await crypto_ex_ws.close()
                    client_market = client_exchange.close()
                except:
                    pass
                break
            try:
                if "watchOHLCV" in list(crypto_ex_ws.has.keys()):
                    if _ohlcv == []:
                        _ohlcv = client_exchange.fetch_ohlcv(symbol,interval,limit=2)
                    else:
                        try:
                            ohlcv = await crypto_ex_ws.watch_ohlcv(symbol,interval,limit=2)
                            if _ohlcv[-1][0]/1000 == ohlcv[-1][0]/1000:
                                _ohlcv[-1] = ohlcv[-1]
                            else:
                                _ohlcv.append(ohlcv[-1])
                                _ohlcv = _ohlcv[-2:]
                        except Exception as e:
                            print(f"Error {e}")
                            _ohlcv = client_exchange.fetch_ohlcv(symbol,interval,limit=2)
                            ws_market = await crypto_ex_ws.load_markets(True)
                            client_market = client_exchange.load_markets(True)
                elif "fetchOHLCV" in list(crypto_ex_ws.has.keys()):
                    _ohlcv = client_exchange.fetch_ohlcv(symbol,interval,limit=2)
                else:
                    await asyncio.sleep(0.3)

                _is_add_candle = False
                if len(_ohlcv) >= 2:
                    pre_ohlcv = OHLCV(_ohlcv[-2][1],_ohlcv[-2][2],_ohlcv[-2][3],_ohlcv[-2][4], round((_ohlcv[-2][2]+_ohlcv[-2][3])/2,_precision) , round((_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/3,_precision), round((_ohlcv[-2][1]+_ohlcv[-2][2]+_ohlcv[-2][3]+_ohlcv[-2][4])/4,_precision),_ohlcv[-2][5],_ohlcv[-2][0]/1000,0)
                    last_ohlcv = OHLCV(_ohlcv[-1][1],_ohlcv[-1][2],_ohlcv[-1][3],_ohlcv[-1][4], round((_ohlcv[-1][2]+_ohlcv[-1][3])/2,_precision) , round((_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/3,_precision), round((_ohlcv[-1][1]+_ohlcv[-1][2]+_ohlcv[-1][3]+_ohlcv[-1][4])/4,_precision),_ohlcv[-1][5],_ohlcv[-1][0]/1000,0)
                    _is_add_candle = jp_candle.update([pre_ohlcv,last_ohlcv])
                    heikin_candle.update(jp_candle.candles[-2:],_is_add_candle)
                    # data = {"is_added_candle": False,"lastcandle":""}
                    candle_data = {}
                    if _is_add_candle != None:
                        candle_data.update({jp_candle.source_name: jp_candle.get_index_data(start=-2)})
                        candle_data.update({heikin_candle.source_name: heikin_candle.get_index_data(start=-2)})
                        
                        list_indicators = []
                        
                        list_indicators += self.get_list_indicator_of_candle(jp_candle)
                        list_indicators += self.get_list_indicator_of_candle(heikin_candle)
                        
                        list_smooth_of_heikin:List[SMOOTH_CANDLE|N_SMOOTH_CANDLE] = self.get_list_smooth_of_candle(heikin_candle)
                        list_smooth_of_japan:List[SMOOTH_CANDLE|N_SMOOTH_CANDLE] = self.get_list_smooth_of_candle(jp_candle)
                        
                        list_smooths:List[SMOOTH_CANDLE|N_SMOOTH_CANDLE] = list_smooth_of_heikin+list_smooth_of_japan
                        

                        if list_smooths != []:
                            for smooth_candle in list_smooths:
                                while True:
                                    if smooth_candle.is_current_update == True:
                                        candle_data.update({smooth_candle.source_name: smooth_candle.get_index_data(start=-2)})
                                        list_indicators += self.get_list_indicator_of_candle(smooth_candle)
                                        smooth_candle.is_current_update = False
                                        break
                                
                        if list_indicators != []:
                            for indicator in list_indicators:
                                while True:
                                    if indicator.is_current_update == True:
                                        candle_data.update({indicator.indicator_name: indicator.get_data(start=-2,stop=0)})
                                        indicator.is_current_update = False
                                        break
                                    
                        data = {"is_added_candle": _is_add_candle,
                                "data_on_chart": candle_data}
                        try:
                            await websocket.send_text(json.dumps(data))
                        except (RuntimeError, WebSocketDisconnect):
                            print ("Error, websocket disconnect in loop_watch_ohlcv")
                            break
            except Exception as e:
                    print("error", "lỗi kết nối với exchange", e)
                    ws_market = await crypto_ex_ws.load_markets(True)
                    client_market = client_exchange.load_markets(True)

    
    def add_indicator(self,ta_infor: dict,source_name: str=""):
        """_summary_
        Args:
            ta_param: indicator.indicator_name = ta_param
            source_name: candle.source_name
        Returns:
            _type_: _description_
        """
        ta_name:str=ta_infor.get("ta_name")
        if source_name == "":
            source_name:str=ta_infor.get("source_name")

        obj_id:str=ta_infor.get("obj_id") 
        indicator = None
        ta_param = ""
        dict_ta_params = {}
        _candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE = self.map_candle.get(source_name)
        if _candles == None:
            return None
        if ta_name == "zigzag":
            legs:str = ta_infor.get("legs")
            deviation:str = ta_infor.get("deviation")
            ta_param = f"{obj_id}-{ta_name}-{legs}-{deviation}"
            
            indicator = ZIGZAG(_candles= _candles,
                    dict_ta_params=ta_infor)
            indicator.started_worker()
        
        elif ta_name == "macd":
            source:str = ta_infor.get("source") 
            slow_period:int = ta_infor.get("slow_period") 
            fast_period:int = ta_infor.get("fast_period") 
            signal_period:int = ta_infor.get("signal_period") 
            ma_type: str = ta_infor.get("ma_type")
            ta_param = f"{obj_id}-{ta_name}-{source}-{ma_type}-{slow_period}-{fast_period}-{signal_period}"
            
            indicator = MACD(_candles= _candles,
                    dict_ta_params=ta_infor)
            indicator.started_worker()
            
        elif ta_name == "ma":
            ma_type:str = ta_infor.get("ma_type")
            source:str = ta_infor.get("source")
            length:int= ta_infor.get("length")
            ta_param = f"{obj_id}-{ta_name}-{source}-{ma_type}-{length}"
            
            indicator = MA(_candles= _candles,
                    dict_ta_params=ta_infor)
            indicator.started_worker()
        
        elif ta_name == "bbands":
            ma_type:PD_MAType = ta_infor["ma_type"]
            source:str = ta_infor["source"]
            length:int = ta_infor["length"]
            std_dev_mult:float = ta_infor["std_dev_mult"]
            
            ta_param = f"{obj_id}-{ta_name}-{source}-{ma_type}-{length}-{std_dev_mult}"
            
            indicator = BBANDS(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
        
        elif ta_name == "donchain":
            lower_length:int = ta_infor["lower_length"]
            upper_length:int = ta_infor["upper_length"]
            ta_param = f"{obj_id}-{ta_name}-{lower_length}-{upper_length}"
            
            indicator = DONCHIAN(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
            
        elif ta_name == "roc":
            source:str = ta_infor["source"]      
            length:int = ta_infor["length"]
            ta_param = f"{obj_id}-{ta_name}-{source}-{length}"
            
            indicator = ROC(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
        
        elif ta_name == "rsi":
            source:str = ta_infor["source"]      
            length:int = ta_infor["length"]
            ma_type:str = ta_infor["ma_type"]
            ta_param = f"{obj_id}-{ta_name}-{source}-{ma_type}-{length}"
            
            indicator = RSI(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
            
        elif ta_name == "stc":
            source:str = ta_infor["source"]              
            tclength:int= ta_infor["tclength"]
            fast:int = ta_infor["fast"]
            slow:int = ta_infor["slow"]
            ma_type:str = ta_infor["ma_type"]
            
            ta_param = f"{obj_id}-{ta_name}-{source}-{ma_type}-{tclength}-{fast}-{slow}"
            
            indicator = STC(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
            
        elif ta_name == "stoch":
            smooth_k_period:int = ta_infor["smooth_k_period"]
            k_period:int = ta_infor["k_period"]
            d_period:int = ta_infor["d_period"]
            ma_type:str = ta_infor["ma_type"]
            
            ta_param = f"{obj_id}-{ta_name}-{ma_type}-{smooth_k_period}-{k_period}-{d_period}"
            
            indicator = STOCH(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
            
        elif ta_name == "stochrsi":
            rsi_period :int = ta_infor["rsi_period"]
            period:int = ta_infor["period"]
            k_period:int = ta_infor["k_period"]
            d_period:int = ta_infor["d_period"]
            source:str = ta_infor["source"]
            ma_type:str = ta_infor["ma_type"]
            
            ta_param = f"{obj_id}-{ta_name}-{source}-{ma_type}-{rsi_period}-{period}-{k_period}-{d_period}"
            
            indicator = STOCHRSI(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
            
        elif ta_name == "vortex":
            period :int=ta_infor["period"]
            drift :int=ta_infor["drift"]
            ta_param = f"{obj_id}-{ta_name}-{period}-{drift}"
            
            indicator = VORTEX(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
            
        elif ta_name == "trix":
            length_period :int = ta_infor["length_period"]
            signal_period:int = ta_infor["signal_period"]
            source:str = ta_infor["source"]
            ma_type:str = ta_infor["ma_type"]
            
            ta_param = f"{obj_id}-{ta_name}-{source}-{ma_type}-{signal_period}-{length_period}"
            
            indicator = TRIX(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
            
        elif ta_name == "tsi":
            fast_period :int = ta_infor["fast_period"]
            slow_period :int = ta_infor["slow_period"]
            signal_period:int = ta_infor["signal_period"]
            source:str = ta_infor["source"]
            ma_type:str = ta_infor["ma_type"]
            
            ta_param = f"{obj_id}-{ta_name}-{source}-{ma_type}-{signal_period}-{slow_period}-{fast_period}"
            
            indicator = TSI(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
            
        elif ta_name == "uo":
            fast_period :int=ta_infor["fast_period"]
            medium_period :int=ta_infor["medium_period"]
            slow_period :int=ta_infor["slow_period"]
            fast_w_value :float=ta_infor["fast_w_value"]
            medium_w_value :float=ta_infor["medium_w_value"]
            slow_w_value :float=ta_infor["slow_w_value"]
            drift  :int=ta_infor.get("drift",1)
            offset :int=ta_infor.get("offset",0)
        
            ta_param = f"{obj_id}-{ta_name}-{fast_period}-{medium_period}-{slow_period}-{fast_w_value}-{medium_w_value}-{slow_w_value}"
            
            indicator = UO(_candles= _candles,
                                dict_ta_params=ta_infor)
            indicator.started_worker()
        
        
        if indicator != None:
            indicator.indicator_name = ta_param
            indicator.source_name = source_name
            
            old_indicator = self.map_indicator.get(obj_id,None)
            if old_indicator != None:
                del self.map_indicator[obj_id]
            self.map_indicator[obj_id] = indicator
            
            list_indicator = self.map_candle_indicator.get(_candles,[])
            if list_indicator == []:
                self.map_candle_indicator[_candles] = [indicator]
            else:
                self.map_candle_indicator[_candles].append(indicator)
        
        return indicator
    
    def delete_indicator(self,ta_infor):
        obj_id:str=ta_infor.get("obj_id") 
        indicator = self.map_indicator.get(obj_id,None)
        if indicator == None:
            return {"detail": f"{ta_infor} is not exist"}
        del self.map_indicator[obj_id]
        source_name:str=indicator.source_name
        candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE = self.map_candle.get(source_name)
        list_indicator = self.map_candle_indicator.get(candles,[])
        if list_indicator != []:
            if indicator in list_indicator:
                list_indicator.remove(indicator) 
        self.map_candle_indicator[candles] = list_indicator
        indicator = None
        return {"detail": f"{ta_infor} had been deleted"}

    def get_all_indicator_on_chart(self,jp_candle:JAPAN_CANDLE,heikin_candle:HEIKINASHI):
        list_indicators = []          
        list_indicators += self.get_list_indicator_of_candle(jp_candle)
        list_indicators += self.get_list_indicator_of_candle(heikin_candle)
        list_smooth_of_heikin:List[SMOOTH_CANDLE|N_SMOOTH_CANDLE] = self.get_list_smooth_of_candle(heikin_candle)
        list_smooth_of_japan:List[SMOOTH_CANDLE|N_SMOOTH_CANDLE] = self.get_list_smooth_of_candle(jp_candle)
        list_smooths:List[SMOOTH_CANDLE|N_SMOOTH_CANDLE] = list_smooth_of_heikin+list_smooth_of_japan
        if list_smooths != []:
            for smooth_candle in list_smooths:
                list_indicators += self.get_list_indicator_of_candle(smooth_candle)
        
        return list_indicators
    
    def get_indicator(self,ta_infor: dict):
        """_summary_
        Args:
            ta_param: indicator.indicator_name = ta_param
            source_name: candle.source_name
        Returns:
            _type_: _description_
        """
        obj_id:str=ta_infor.get("obj_id") 
        return self.map_indicator.get(obj_id,None)
    
    def get_ta_data(self,ta_infor: dict):
        indicator = self.get_indicator(ta_infor)
        if indicator != None:
            return indicator.get_data()

    def change_input_indicator(self,new_ta_infor: dict):
        """_summary_
        Args:
            ta_param: indicator.indicator_name = ta_param
            source_name: candle.source_name
        Returns:
            _type_: _description_
        """
        
        indicator = self.get_indicator(new_ta_infor)
        if indicator == None:
            return {}
        
        source_name:str=new_ta_infor.get("source_name")
        _candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE = self.map_candle.get(source_name)
        
        if _candles == None:
            return {}
        try:
            old_source_name:str=indicator.source_name
            
            "change inputs"
            if source_name == old_source_name:
                indicator.change_input(dict_ta_params=new_ta_infor)
                return indicator.get_data()
            "change source"
            old_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE = self.map_candle.get(old_source_name)
            indicator.source_name = source_name
            list_old_indicator = self.map_candle_indicator.get(old_candles,[])
            if indicator in list_old_indicator:
                    self.map_candle_indicator[old_candles].remove(indicator)
            
            indicator.change_input(candles=_candles,dict_ta_params={})
            
            list_indicator = self.map_candle_indicator.get(_candles,[])
            if list_indicator == []:
                self.map_candle_indicator[_candles] = [indicator]
            else:
                if indicator in list_indicator:
                    pass
                else:
                    self.map_candle_indicator[_candles].append(indicator)
            while True:
                if indicator.is_current_update:
                    return indicator.get_data()
        except:
            return {}
        
    
    def add_candle(self,candle_infor: dict)->SMOOTH_CANDLE|N_SMOOTH_CANDLE|JAPAN_CANDLE|HEIKINASHI:
        chart_id = candle_infor.get("chart_id")
        canlde_id:float=candle_infor.get("canlde_id") 
        id_exchange = candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:str=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        precision:float=candle_infor.get("precision") 
        source_name = ""
        candle:SMOOTH_CANDLE|N_SMOOTH_CANDLE|JAPAN_CANDLE|HEIKINASHI = None
        jp_name = f"{chart_id}-{id_exchange}-japancandle-{symbol}-{interval}"
        heikin_name = f"{chart_id}-{id_exchange}-heikinashi-{symbol}-{interval}"
        _candles:JAPAN_CANDLE|HEIKINASHI = None
        if name == "smoothcandle":
            source_name = f"{chart_id}-{canlde_id}-{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}-{ma_leng}"
            if source == "japan":
                _candles = self.map_candle[jp_name]
                candle = self.map_candle[source_name] = SMOOTH_CANDLE(_candles,candle_infor)
            else:
                _candles = self.map_candle[heikin_name]
                candle = self.map_candle[source_name] = SMOOTH_CANDLE(_candles,candle_infor)
            list_candle = self.map_candle_smooth_candle.get(_candles,[])
            if list_candle == []:
                self.map_candle_smooth_candle[_candles] = [candle]
            else:
                self.map_candle_smooth_candle[_candles].append(candle)
        elif name == "japancandle":
            source_name = jp_name
            candle = self.map_candle[source_name] = JAPAN_CANDLE()
        elif name == "supersmoothcandle":
            source_name = f"{chart_id}-{canlde_id}-{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}-{ma_leng}-{n_smooth}"
            if source == "japan":
                _candles = self.map_candle[jp_name]
                candle = self.map_candle[source_name] = N_SMOOTH_CANDLE(_candles,candle_infor)
            else:
                _candles = self.map_candle[heikin_name]
                candle = self.map_candle[source_name] = N_SMOOTH_CANDLE(_candles,candle_infor)
            list_candle = self.map_candle_smooth_candle.get(_candles,[])
            if list_candle == []:
                self.map_candle_smooth_candle[_candles] = [candle]
            else:
                self.map_candle_smooth_candle[_candles].append(candle)
        elif name == "heikinashi":
            source_name = heikin_name
            candle = self.map_candle[source_name] = HEIKINASHI(precision,self.map_candle[jp_name])
        
        if candle != None:
            candle.source_name = source_name
        return candle
    
    def get_candle(self,candle_infor:dict):
        """_summary_
            get candle by its infor
        Args:
            candle_infor (dict): _description_

        Returns:
            JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE: _description_
        """
        chart_id = candle_infor.get("chart_id")
        canlde_id:float=candle_infor.get("canlde_id") 
        id_exchange = candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:str=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        source_name = ""
        if name == "smoothcandle":
            source_name = f"{chart_id}-{canlde_id}-{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}-{ma_leng}"
            return self.map_candle.get(source_name), source_name
        elif name == "japancandle":
            source_name = f"{chart_id}-{id_exchange}-{name}-{symbol}-{interval}"
            return self.map_candle.get(source_name) ,source_name
        elif name == "supersmoothcandle":
            source_name = f"{chart_id}-{canlde_id}-{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}-{ma_leng}-{n_smooth}"
            return self.map_candle.get(source_name),source_name
        elif name == "heikinashi":
            source_name = f"{chart_id}-{id_exchange}-{name}-{symbol}-{interval}"
            return self.map_candle.get(source_name),source_name
        return None,source_name
    
    
    def delete_smooth_candle(self,candle_infor):
        chart_id = candle_infor.get("chart_id")
        canlde_id:float=candle_infor.get("canlde_id") 
        id_exchange = candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:str=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        source_name = ""

        jp_name = f"{chart_id}-{id_exchange}-japancandle-{symbol}-{interval}"
        heikin_name = f"{chart_id}-{id_exchange}-heikinashi-{symbol}-{interval}"
        _candles:JAPAN_CANDLE|HEIKINASHI = None
        if source == "japan":
            _candles = self.map_candle[jp_name]
        else:
            _candles = self.map_candle[heikin_name]
        if name == "smoothcandle":
            source_name = f"{chart_id}-{canlde_id}-{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}-{ma_leng}"
        elif name == "supersmoothcandle":
            source_name = f"{chart_id}-{canlde_id}-{id_exchange}-{source}-{name}-{symbol}-{interval}-{ma_type}-{ma_leng}-{n_smooth}"
        else:
            return {"detail": f"{candle_infor} is not exist","data":{}}
        
        smth_candle = self.map_candle.get(source_name,None) 
        output = {}
        if smth_candle != None:
            list_old_indicator:list = self.map_candle_indicator.get(smth_candle,[])
            if list_old_indicator != []:
                for indicator in list_old_indicator:
                        indicator.change_input(candles=_candles,dict_ta_params={})
                        while True:
                            if indicator.is_current_update:
                                output.update({indicator.indicator_name: indicator.get_data()})
            del self.map_candle_indicator[smth_candle]
            del self.map_candle[source_name]
            smth_candle = None
            return {"detail": f"{candle_infor} had been deleted","data":output}
        return {"detail": f"{candle_infor} is not exist","data":output}
        
    def get_list_indicator_of_candle(self,candle:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        """_summary_
            get list indicators, which has source_candle is candle
        Args:
            candle (JAPAN_CANDLE | HEIKINASHI | SMOOTH_CANDLE | N_SMOOTH_CANDLE): _description_

        Returns:
            _type_: list
        """
        return self.map_candle_indicator.get(candle,[])
    
    def get_list_smooth_of_candle(self,candle:JAPAN_CANDLE|HEIKINASHI):
        """_summary_
            get list smooth candles, which had been generated by candle
        Args:
            candle (JAPAN_CANDLE | HEIKINASHI): _description_
        Returns:
            _type_: list
        """
        return self.map_candle_smooth_candle.get(candle,[])
    
    
    def get_all_candles_on_chart(self)-> dict:
        list_indicators = list(self.map_indicator.values())
        output = []
        if list_indicators != []:
            for indicator in list_indicators:
                output.append(indicator.indicator_name)
        return {"indicators":output}
    
    def get_all_candles_on_chart(self,candle_infor)-> dict:
        """_summary_
            get all candles are on the same chart
        Args:
            candle_infor (_type_): _description_

        Returns:
            dict: dict
        """
        chart_id = candle_infor.get("chart_id")

        output = {}
        
        for candle_id in list(self.map_candle.keys()):
            if chart_id in candle_id and "heikinashi" in candle_id:
                s_smooth = output.get("heikinashi",None)
                if s_smooth == None:
                    output["heikinashi"] = [self.map_candle[candle_id].source_name]
                else:
                    output["heikinashi"].append(self.map_candle[candle_id].source_name)   
                
            elif chart_id in candle_id and "japancandle" in candle_id:
                s_smooth = output.get("japancandle",None)
                if s_smooth == None:
                    output["japancandle"] = [self.map_candle[candle_id].source_name]
                else:
                    output["japancandle"].append(self.map_candle[candle_id].source_name) 
            
            elif chart_id in candle_id and "-smoothcandle-" in candle_id:
                smooth = output.get("smoothcandle",None)
                if smooth == None:
                    output["smoothcandle"] = [self.map_candle[candle_id].source_name]
                else:
                    output["smoothcandle"].append(self.map_candle[candle_id].source_name)
            elif chart_id in candle_id and "supersmoothcandle" in candle_id:
                s_smooth = output.get("supersmoothcandle",None)
                if s_smooth == None:
                    output["supersmoothcandle"] = [self.map_candle[candle_id].source_name]
                else:
                    output["supersmoothcandle"].append(self.map_candle[candle_id].source_name)     
        return output

