import aiohttp
import asyncio
import json

import requests
from atklip.app_api.var import *
from atklip.app_utils.syncer import sync
from .urls import ApiURL
from .var import *

class API():
    def __init__(self):
        self.map_chart_exchange:dict = {}
        self.urls = ApiURL()
        self.timeout = aiohttp.ClientTimeout(total=60)

    def check_server_is_alive(self):
        payload = {}
        headers = {}
        try:
            with requests.request("GET", self.urls.url_test, headers=headers, data=payload) as response:
                if response.status_code == 200:
                    return True
                else:
                    return True
        except Exception as e:
            return False
        
    @sync
    async def get_active_indicator(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.urls.url_get_active_indicator) as response:
                    data = await response.json(encoding="utf-8")
                    return data
            except Exception as e:
                print(e)
                return {}
            await session.close()
        return {}
        
    
    @sync
    async def get_candle_data(self,candle_infor,start:int=0,stop:int=0):
        chart_id = candle_infor.get("chart_id")
        canlde_id = candle_infor.get("canlde_id")
        id_exchange = candle_infor.get("id_exchange")
        symbol = candle_infor.get("symbol")
        interval = candle_infor.get("interval")
        ma_type = candle_infor.get("ma_type")
        ma_leng = candle_infor.get("ma_leng")
        name = candle_infor.get("name")
        source = candle_infor.get("source")
        payload = {
            "chart_id": f"{chart_id}",
            "canlde_id": f"{canlde_id}",
            "id_exchange": f"{id_exchange}",
            "symbol": f"{symbol}",
            "interval": f"{interval}",
            "ma_type": f"{ma_type}",
            "ma_leng": f"{ma_leng}",
            "name": f"{name}",
            "source": f"{source}",
            "precision": 3
        }
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_get_candle_data(start,stop), json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def get_volume_data(self,candle_infor,start:int=0,stop:int=0):
        chart_id = candle_infor.get("chart_id")
        canlde_id = candle_infor.get("canlde_id")
        id_exchange = candle_infor.get("id_exchange")
        symbol = candle_infor.get("symbol")
        interval = candle_infor.get("interval")
        ma_type = candle_infor.get("ma_type")
        ma_leng = candle_infor.get("ma_leng")
        name = candle_infor.get("name")
        source = candle_infor.get("source")
        payload = {
            "chart_id": f"{chart_id}",
            "canlde_id": f"{canlde_id}",
            "id_exchange": f"{id_exchange}",
            "symbol": f"{symbol}",
            "interval": f"{interval}",
            "ma_type": f"{ma_type}",
            "ma_leng": f"{ma_leng}",
            "name": f"{name}",
            "source": f"{source}",
            "precision": 3
        }
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_get_volume_data(start,stop), json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def get_list_candle(self,chart_id,start:int=0,stop:int=0):
        """_summary_
        Args:
            chart_id (_type_): _description_
            start (int, optional): _description_. Defaults to 0.
            stop (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: {
                    "candles": {
                        "japancandle": [
                            "this_is_my_fastapi-binanceusdm-japancandle-ETHUSDT-1m"
                        ],
                        "heikinashi": [
                            "this_is_my_fastapi-binanceusdm-heikinashi-ETHUSDT-1m"
                        ],
                        "smoothcandle": [
                            "this_is_my_fastapi-smooth_exam-binanceusdm-japan-smoothcandle-ETHUSDT-1m-ema-10"
                        ]
                    }
                }
        """
        payload = {
            "chart_id": f"{chart_id}"
        }
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_get_volume_data(start,stop), json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}

    @sync
    async def add_smooth_candle(self,candle_infor:dict):
        payload = candle_infor
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_add_smooth_candle, json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def change_input_smooth_candle(self,candle_infor:dict):
        # old_candle_infor = candle_infor["old"]
        # new_candle_infor = candle_infor["new"]
        # payload = {"old":{"chart_id": old_candle_infor.get("chart_id"),
        #                 "canlde_id":old_candle_infor.get("canlde_id"),
        #                 "id_exchange":old_candle_infor.get("id_exchange"),
        #                 "symbol":old_candle_infor.get("symbol"),
        #                 "interval":old_candle_infor.get("interval"),
        #                 "ma_type":old_candle_infor.get("ma_type"),
        #                 "ma_leng":old_candle_infor.get("ma_leng"),
        #                 "name":old_candle_infor.get("name"),
        #                 "source":old_candle_infor.get("source"),
        #                 "precision":old_candle_infor.get("precision")}
        #                 ,
        #             "new":{"chart_id": new_candle_infor.get("chart_id"),
        #                 "canlde_id":new_candle_infor.get("canlde_id"),
        #                 "id_exchange":new_candle_infor.get("id_exchange"),
        #                 "symbol":new_candle_infor.get("symbol"),
        #                 "interval":new_candle_infor.get("interval"),
        #                 "ma_type":new_candle_infor.get("ma_type"),
        #                 "ma_leng":new_candle_infor.get("ma_leng"),
        #                 "name":new_candle_infor.get("name"),
        #                 "source":new_candle_infor.get("source"),
        #                 "precision":new_candle_infor.get("precision")}
        #                 }
        payload = candle_infor
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_delete_smooth_candle, json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    
    @sync
    async def delete_smooth_candle(self,candle_infor:dict):
        # chart_id = candle_infor.get("chart_id")
        # canlde_id = candle_infor.get("canlde_id")
        # id_exchange = candle_infor.get("id_exchange")
        # symbol = candle_infor.get("symbol")
        # interval = candle_infor.get("interval")
        # ma_type = candle_infor.get("ma_type")
        # ma_leng = candle_infor.get("ma_leng")
        # n_smooth = candle_infor.get("n_smooth")
        # name = candle_infor.get("name")
        # source = candle_infor.get("source")
        payload = candle_infor
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_delete_smooth_candle, json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def add_indicator(self,indicator_infor:dict):
        """_summary_

        Args:
            indicator_infor (dict): {"list_ta":
                                    [
                                    {"obj_id":"rewrwerwererwerewrewrerwerfd",
                                    "ta_name":"zigzag",
                                    "source_name":"this_is_my_fastapi-binanceusdm-japancandle-ETHUSDT-1m",
                                    "legs":3,
                                    "deviation":1},
                                    ]}

        Returns:
            _type_: _description_
        """
        payload = {"list_ta":
                        [indicator_infor,
                        ]}
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_add_indicator, json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def get_indicator_data(self,indicator_infor:dict,start:int=0,stop:int=0):
        """_summary_

        Args:
            indicator_infor (dict): {"obj_id":"rewrwerwererwerewrewrerwerfd"}

        Returns:
            _type_: _description_
        """
        payload = indicator_infor
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_get_indicator_data(start,stop), json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def change_input_indicator(self,indicator_infor:dict):
        """_summary_

        Args:
            indicator_infor (dict): {"obj_id":"fdsfdfdsf",
                                "ta_name":"macd",
                                "source_name":"this_is_my_fastapi-smooth_exam-binanceusdm-japan-smoothcandle-BTCUSDT-1m-ema-10",
                                "source":"close",
                                "fast_period":15,
                                "slow_period":30,
                                "signal_period":12,
                                "ma_type":"ema"}
        Returns:
            _type_: _description_
        """
        payload = indicator_infor
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_change_indicator_input, json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def delete_indicator(self,indicator_infor:dict):
        """_summary_

        Args:
            indicator_infor (dict): {"list_indicators":
                                    [
                                    {"obj_id":"rewrwerwererwerewrewrerwerfd"},
                                    ]}

        Returns:
            _type_: _description_
        """
        payload = {"list_indicators":[indicator_infor]}
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_delete_indicator, json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def load_historic_data(self,candle_infor:dict):
        """_summary_

        Args:
            candle_infor (dict): {"chart_id": "this_is_my_fastapi",
                                "id_exchange":"binanceusdm",
                                "symbol":"ETHUSDT",
                                "interval":"1m"}
        Returns:
            _type_: _description_
        """
        
        payload = candle_infor
        headers = {
            'Content-Type': 'application/json'
            }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_load_historic, json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def reset_chart(self,candle_infor:dict):
        """_summary_

        Args:
            candle_infor (dict): {"chart_id": "this_is_my_fastapi",
                                    "id_exchange":"binanceusdm",
                                    "symbol":"ETHUSDT",
                                    "interval":"1m",
                                    "precision":3}
        Returns:
            _type_: _description_
        """
        
        payload = candle_infor
        headers = {
            'Content-Type': 'application/json'
            }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_reset_chart, json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def goto_date(self,candle_infor:dict):
        """_summary_

        Args:
            candle_infor (dict): {"chart_id": "this_is_my_fastapi",
                                "id_exchange":"binanceusdm",
                                "symbol":"ETHUSDT",
                                "interval":"1m",
                                "precision":3,
                                "gototime":1244324234234}
            gototime: (ms) timestamp
        Returns:
            _type_: _description_
        """
        
        payload = candle_infor
        headers = {
            'Content-Type': 'application/json'
            }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls.url_goto_date, json=payload, headers=headers) as response:
                try:
                    data = await response.json(encoding="utf-8")
                    return data
                except Exception as e:
                    print(e)
                    return {}
            await session.close()
        return {}
    
    @sync
    async def re_connect_to_market(self,chart_id,id_exchange,symbol,interval,emit_data):
        if not self.check_server_is_alive():
            print("Server was died")
            return
        print("Start re-connect")
        message = {"chart_id": f"{chart_id}",
                    "id_exchange":f"{id_exchange}",
                    "symbol":f"{symbol}",
                    "interval":f"{interval}"}
        self.map_chart_exchange[chart_id]=f"{id_exchange}-{symbol}-{interval}"
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.urls.ws_reconnect_market) as websocket:
                await websocket.send_json(message)
                print(f"Sent: {message}")
                async for msg in websocket:
                    if self.map_chart_exchange[chart_id] != f"{id_exchange}-{symbol}-{interval}":
                        break
                    if not self.check_server_is_alive():
                        print("Server was died")
                        break
                    try:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            response = msg.data
                            if response != "heartbeat":
                                try:
                                    output = json.loads(response)
                                    print(output)
                                except json.JSONDecodeError:
                                    print("Invalid JSON response from server.", response)
                            else:
                                await websocket.send_str("pong")
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print("Error occurred.")
                            break
                    except (RuntimeError,aiohttp.ClientConnectionError,aiohttp.ServerConnectionError,\
                            aiohttp.ServerTimeoutError):
                        await self.re_connect_to_market(chart_id,id_exchange,symbol,interval,emit_data)
                        break

    @sync
    async def connect_to_market(self,chart_infor:dict,emit_data):
        """_summary_

        Args:
            change_infor (dict): _description_
            emit_data (_type_): _description_
        """
        chart_id = chart_infor.get("chart_id")
        id_exchange = chart_infor.get("id_exchange")
        symbol = chart_infor.get("symbol")
        interval = chart_infor.get("interval")
        
        message = {"chart_id": f"{chart_id}",
                    "id_exchange":f"{id_exchange}",
                    "symbol":f"{symbol}",
                    "interval":f"{interval}"}
        
        self.map_chart_exchange[chart_id]=f"{id_exchange}-{symbol}-{interval}"
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.urls.ws_setup_market) as websocket:
                await websocket.send_json(message)
                print(f"Sent: {message}")

                async for msg in websocket:
                    if self.map_chart_exchange[chart_id] != f"{id_exchange}-{symbol}-{interval}":
                        break
                    if not self.check_server_is_alive():
                        print("Server was died")
                        break
                    try:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            response = msg.data
                            if response != "heartbeat":
                                try:
                                    output = json.loads(response)
                                    emit_data.emit(output)
                                    # print(output)
                                except json.JSONDecodeError:
                                    print("Invalid JSON response from server.", response)
                            else:
                                await websocket.send_str("pong")
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print("Error occurred.")
                            break
                    except (RuntimeError,aiohttp.ClientConnectionError,aiohttp.ServerConnectionError,\
                            aiohttp.ServerTimeoutError):
                        await self.re_connect_to_market(chart_id,id_exchange,symbol,interval,emit_data)
                        break
    
    @sync
    async def change_market(self,change_infor:dict,emit_data):
        chart_id = change_infor.get("chart_id")
        old_id_exchange = change_infor.get("old_id_exchange")
        old_symbol = change_infor.get("old_symbol")
        old_interval = change_infor.get("old_interval")
        new_id_exchange = change_infor.get("new_id_exchange")
        new_symbol = change_infor.get("new_symbol")
        new_interval = change_infor.get("new_interval")
        
        message = {"old":{"chart_id": f"{chart_id}",
                        "obj_id":"maincandle",
                        "id_exchange":f"{old_id_exchange}",
                        "symbol":f"{old_symbol}",
                        "interval":f"{old_interval}"},
                    "new":{"chart_id": f"{chart_id}",
                        "obj_id":"maincandle",
                        "id_exchange":f"{new_id_exchange}",
                        "symbol":f"{new_symbol}",
                        "interval":f"{new_interval}"}}
        
        self.map_chart_exchange[chart_id]=f"{new_id_exchange}-{new_symbol}-{new_interval}"
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.urls.ws_change_market) as websocket:
                await websocket.send_json(message)
                print(f"Sent: {message}")
                async for msg in websocket:
                    if self.map_chart_exchange[chart_id] != f"{new_id_exchange}-{new_symbol}-{new_interval}":
                        break
                    if not self.check_server_is_alive():
                        print("Server was died")
                        break
                    try:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            response = msg.data
                            if response != "heartbeat":
                                try:
                                    output = json.loads(response)
                                    print(output)
                                except json.JSONDecodeError:
                                    print("Invalid JSON response from server.", response)
                            else:
                                await websocket.send_str("pong")
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print("Error occurred.")
                            break
                    except (RuntimeError,aiohttp.ClientConnectionError,aiohttp.ServerConnectionError,\
                            aiohttp.ServerTimeoutError):
                        await self.re_connect_to_market(chart_id,new_id_exchange,new_symbol,new_interval,emit_data)
                        break

global api
api = API()