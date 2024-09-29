import asyncio
import json
import time
import websockets
import requests

from atklip.controls.ma_type import IndicatorType
from .var import *
class API():
    def __init__(self):
        pass
        
    def check_server_is_alive(self):
        test_url = f"ws://{host}:{port}/candle/test" 
        try:
            response = requests.get(test_url)
            if response.status_code == 200:
                return True
            else:
                return True
        except requests.exceptions.ConnectionError:
            return False
        
    def get_candle_data(self):
        pass
    
    async def connect_to_websocket(self,candle_infor):
        candle_infor = {"id_exchange":"binanceusdm",
                "symbol":"BTCUSDT",
                "interval":"1m",
                "ma_type":"",
                "ma_leng":3,
                "n_smooth":3,
                "name":"japancandle",
                "source":"japan",
                "precicion":3}
        
        id_exchange:str=candle_infor.get("id_exchange")
        symbol:str=candle_infor.get("symbol")
        interval:str=candle_infor.get("interval")
        ma_type:IndicatorType=candle_infor.get("ma_type")
        ma_leng:int=candle_infor.get("ma_leng")
        n_smooth:int=candle_infor.get("n_smooth")
        name:str=candle_infor.get("name")
        source:str=candle_infor.get("source")
        precicion:str=candle_infor.get("precicion") 
        
        uri = f"ws://{host}:{port}/candle/{id_exchange}"  
        websocket = await websockets.connect(uri)
        while not websocket.open:
            time.sleep(1)
            continue
        
        if websocket.closed:
            websocket = await websockets.connect(uri)
        await websocket.send(json.dumps(candle_infor))
        # Nhận phản hồi từ server
        response = await websocket.recv()
        print(f"Received: {response}")
