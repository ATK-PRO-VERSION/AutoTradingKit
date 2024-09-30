
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict

from .models import *
from .ta_indicators import *
from .ta_indicators import IndicatorType
  
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[:str:List[WebSocket]] = {}

    def get_sockets(self):
        return list(self.active_connections.keys())
    
    def get_socket_by_name(self,socket_infor):
        id_exchange = socket_infor.get("id_exchange")
        symbol:str=socket_infor.get("symbol")
        interval:str=socket_infor.get("interval")
        ma_type:IndicatorType=socket_infor.get("ma_type")
        ma_leng:int=socket_infor.get("ma_leng")
        n_smooth:int=socket_infor.get("n_smooth")
        name:str=socket_infor.get("name")
        source:str=socket_infor.get("source")
        precicion:float=socket_infor.get("precicion") 
        socket_name = f"{id_exchange}-{symbol}-{interval}"
        return  self.active_connections.get(socket_name)

    
    async def connect(self, socket_infor,websocket: WebSocket):
        id_exchange = socket_infor.get("id_exchange")
        symbol:str=socket_infor.get("symbol")
        interval:str=socket_infor.get("interval")
        ma_type:IndicatorType=socket_infor.get("ma_type")
        ma_leng:int=socket_infor.get("ma_leng")
        n_smooth:int=socket_infor.get("n_smooth")
        name:str=socket_infor.get("name")
        source:str=socket_infor.get("source")
        precicion:float=socket_infor.get("precicion") 
        socket_name = f"{id_exchange}-{symbol}-{interval}"
        if self.socket_is_active(websocket):
            await self.disconnect(socket_infor,websocket)
        self.active_connections[socket_name]=websocket

    async def disconnect(self,socket_infor, websocket: WebSocket):
        print(f"{websocket} is closed")
        id_exchange = socket_infor.get("id_exchange")
        symbol:str=socket_infor.get("symbol")
        interval:str=socket_infor.get("interval")
        ma_type:IndicatorType=socket_infor.get("ma_type")
        ma_leng:int=socket_infor.get("ma_leng")
        n_smooth:int=socket_infor.get("n_smooth")
        name:str=socket_infor.get("name")
        source:str=socket_infor.get("source")
        precicion:float=socket_infor.get("precicion") 
        socket_name = f"{id_exchange}-{symbol}-{interval}"
        del self.active_connections[socket_name]
        try:
            await websocket.close()
        except:
            pass
    
    def socket_is_active(self,websocket: WebSocket):
        if websocket in self.active_connections.values():
            return True
        return False

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
            
    async def send_heartbeat(self, websocket: WebSocket):
        while True:
            try:
                await asyncio.sleep(30)
                await websocket.send_text("heartbeat")
            except WebSocketDisconnect:
                break
